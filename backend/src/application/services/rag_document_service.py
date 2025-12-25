from typing import List, Optional
from fastapi import UploadFile

from src.domain.entities.context_document import ContextDocument, ProcessingStatus
from src.domain.entities.chunk import Chunk
from src.domain.ports.context_document_repository import ContextDocumentRepositoryPort
from src.domain.ports.chunk_repository import ChunkRepositoryPort
from src.domain.ports.embedding_port import EmbeddingPort
from src.infrastructure.outbound.supabase_storage_service import SupabaseStorageService
from src.application.services.document_processors.factory import DocumentProcessorFactory
from src.application.services.text_chunking_service import TextChunkingService


class RAGDocumentService:
    """Service for managing RAG context documents"""
    
    def __init__(
        self,
        document_repository: ContextDocumentRepositoryPort,
        chunk_repository: ChunkRepositoryPort,
        embedding_port: EmbeddingPort
    ):
        self._document_repository = document_repository
        self._chunk_repository = chunk_repository
        self._embedding_port = embedding_port
        self._storage_service = SupabaseStorageService()
        self._processor_factory = DocumentProcessorFactory()
        self._chunking_service = TextChunkingService()
    
    async def upload_and_process(self, file: UploadFile) -> dict:
        """
        Upload a document and process it for RAG.
        
        Steps:
        1. Validate file format
        2. Upload to Supabase Storage
        3. Create document record
        4. Extract text from document
        5. Split into chunks
        6. Generate embeddings
        7. Store chunks with embeddings
        
        Args:
            file: Uploaded file
            
        Returns:
            Dict with upload result and document info
        """
        # Validate file format
        if not file.filename:
            raise ValueError("File must have a filename")
        
        if not self._processor_factory.is_supported(file.filename):
            supported = self._processor_factory.get_supported_extensions_string()
            raise ValueError(f"Unsupported file format. Supported formats: {supported}")
        
        # Read file content
        print(f"[RAG] Reading file: {file.filename}", flush=True)
        file_content = await file.read()
        if not file_content:
            raise ValueError("File is empty")
        print(f"[RAG] File size: {len(file_content)} bytes", flush=True)
        
        # Generate storage path with sanitized filename
        import uuid
        import re
        import unicodedata
        
        # Normalize unicode and remove accents
        normalized = unicodedata.normalize('NFKD', file.filename)
        ascii_filename = normalized.encode('ASCII', 'ignore').decode('ASCII')
        
        # Sanitize: keep only alphanumeric, dash, underscore, dot
        safe_filename = re.sub(r'[^\w\-_\.]', '_', ascii_filename)
        safe_filename = re.sub(r'_+', '_', safe_filename)  # Remove multiple underscores
        safe_filename = safe_filename.strip('_')  # Remove leading/trailing underscores
        
        unique_filename = f"rag_{uuid.uuid4()}_{safe_filename}"
        storage_path = f"rag_documents/{unique_filename}"
        
        # Upload to storage
        print(f"[RAG] Uploading to storage: {storage_path}", flush=True)
        try:
            await self._storage_service.upload_file(file_content, storage_path)
            print("[RAG] Upload complete", flush=True)
        except Exception as e:
            raise Exception(f"Error uploading file to storage: {str(e)}")
        
        # Create document record
        document = ContextDocument(
            filename=file.filename,
            storage_url=storage_path,
            processing_status=ProcessingStatus.PENDING
        )
        
        try:
            created_document = await self._document_repository.create(document)
        except Exception as e:
            # Cleanup storage on failure
            await self._storage_service.delete_file(storage_path)
            raise Exception(f"Error creating document record: {str(e)}")
        
        # Process document asynchronously (in background ideally, but sync for now)
        try:
            await self._process_document(created_document.id, file_content, file.filename)
        except Exception as e:
            # Mark as failed but don't delete - admin can retry
            await self._document_repository.update_status(
                created_document.id, 
                ProcessingStatus.FAILED
            )
            raise Exception(f"Error processing document: {str(e)}")
        
        return {
            "status": "success",
            "message": "Document uploaded and processed successfully",
            "document_id": created_document.id,
            "filename": file.filename,
            "processing_status": ProcessingStatus.COMPLETED.value
        }
    
    async def _process_document(
        self, 
        document_id: int, 
        content: bytes, 
        filename: str
    ) -> None:
        """Process a document: extract text, chunk, embed, store"""
        # Update status to processing
        print(f"[RAG] Processing document {document_id}", flush=True)
        await self._document_repository.update_status(document_id, ProcessingStatus.PROCESSING)
        
        # Get processor for file type
        processor = self._processor_factory.get_processor(filename)
        if not processor:
            raise ValueError(f"No processor found for file: {filename}")
        
        # Extract text
        print("[RAG] Extracting text...", flush=True)
        extracted_texts = await processor.extract_text(content, filename)
        if not extracted_texts:
            raise ValueError("No text could be extracted from document")
        print(f"[RAG] Extracted {len(extracted_texts)} text sections", flush=True)
        
        # Combine all extracted text
        full_text = "\n\n".join([et.text for et in extracted_texts])
        print(f"[RAG] Total text length: {len(full_text)} chars", flush=True)
        
        # Get base metadata from first extraction
        base_metadata = extracted_texts[0].metadata if extracted_texts else {}
        
        # Split into chunks
        print("[RAG] Chunking text...", flush=True)
        text_chunks = self._chunking_service.chunk_text(full_text, base_metadata)
        
        if not text_chunks:
            raise ValueError("No chunks could be created from document")
        print(f"[RAG] Created {len(text_chunks)} chunks", flush=True)
        
        # Generate embeddings for all chunks
        print("[RAG] Generating embeddings (OpenAI API)...", flush=True)
        chunk_texts = [tc["text"] for tc in text_chunks]
        embeddings = await self._embedding_port.generate_embeddings_batch(chunk_texts)
        print(f"[RAG] Generated {len(embeddings)} embeddings", flush=True)
        
        # Create chunk entities and store
        chunks_to_create = []
        for i, (tc, embedding) in enumerate(zip(text_chunks, embeddings)):
            chunk = Chunk(
                content=tc["text"],
                metadata=tc["metadata"],
                documento_id=document_id,
                embedding=embedding
            )
            chunks_to_create.append(chunk)
        
        # Store chunks
        print("[RAG] Storing chunks in database...", flush=True)
        await self._chunk_repository.create_batch(chunks_to_create)
        print("[RAG] Chunks stored successfully", flush=True)
        
        # Update status to completed
        await self._document_repository.update_status(document_id, ProcessingStatus.COMPLETED)
        print("[RAG] Document processing complete!", flush=True)
    
    async def list_documents(self) -> List[dict]:
        """List all RAG documents with their status and chunk count"""
        documents = await self._document_repository.get_all()
        
        result = []
        for doc in documents:
            chunk_count = await self._document_repository.count_chunks(doc.id)
            result.append({
                "id": doc.id,
                "filename": doc.filename,
                "storage_url": doc.storage_url,
                "processing_status": doc.processing_status.value,
                "created_at": doc.created_at.isoformat() if doc.created_at else None,
                "chunks_count": chunk_count
            })
        
        return result
    
    async def get_document(self, document_id: int) -> Optional[dict]:
        """Get a specific document by ID"""
        doc = await self._document_repository.get_by_id(document_id)
        if not doc:
            return None
        
        chunk_count = await self._document_repository.count_chunks(doc.id)
        
        return {
            "id": doc.id,
            "filename": doc.filename,
            "storage_url": doc.storage_url,
            "processing_status": doc.processing_status.value,
            "created_at": doc.created_at.isoformat() if doc.created_at else None,
            "chunks_count": chunk_count
        }
    
    async def delete_document(self, document_id: int) -> dict:
        """Delete a document and all its chunks"""
        doc = await self._document_repository.get_by_id(document_id)
        if not doc:
            raise ValueError(f"Document with ID {document_id} not found")
        
        # Delete from storage
        try:
            await self._storage_service.delete_file(doc.storage_url)
        except Exception:
            pass  # Continue even if storage delete fails
        
        # Delete document (cascades to chunks)
        success = await self._document_repository.delete(document_id)
        
        if not success:
            raise Exception("Failed to delete document")
        
        return {
            "status": "success",
            "message": f"Document {document_id} deleted successfully"
        }
