from fastapi import APIRouter, HTTPException, Depends, UploadFile, File
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List

from src.api.middleware.auth_middleware import get_current_user
from src.application.services.rag_document_service import RAGDocumentService
from src.application.dtos.rag_document_dtos import (
    ContextDocumentResponse,
    DocumentUploadResponse,
    DocumentDeleteResponse,
    ProcessingStatusDto
)
from src.infrastructure.adapters.database.connection import get_db_session
from src.infrastructure.adapters.database.context_document_repository import SupabaseContextDocumentRepository
from src.infrastructure.adapters.database.chunk_repository import SupabaseChunkRepository
from src.infrastructure.adapters.openai_adapter import OpenAIAdapter

router = APIRouter(
    prefix="/rag/documents",
    tags=["RAG Documents"],
    dependencies=[Depends(get_current_user)]  # Protected - requires authentication
)


def get_rag_document_service(db: AsyncSession = Depends(get_db_session)) -> RAGDocumentService:
    """Dependency to get RAGDocumentService"""
    document_repository = SupabaseContextDocumentRepository(db)
    chunk_repository = SupabaseChunkRepository(db)
    embedding_port = OpenAIAdapter()
    return RAGDocumentService(document_repository, chunk_repository, embedding_port)


@router.post("/", response_model=DocumentUploadResponse)
async def upload_document(
    file: UploadFile = File(..., description="Document file to upload (PDF, DOCX, DOC)"),
    service: RAGDocumentService = Depends(get_rag_document_service)
):
    """
    Upload and process a document for RAG.
    
    Supported formats: PDF, DOCX, DOC
    
    The document will be:
    1. Uploaded to storage
    2. Text extracted
    3. Split into chunks
    4. Embeddings generated
    5. Stored for vector search
    """
    try:
        result = await service.upload_and_process(file)
        return DocumentUploadResponse(
            status=result["status"],
            message=result["message"],
            document_id=result["document_id"],
            filename=result["filename"],
            processing_status=ProcessingStatusDto(result["processing_status"])
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/", response_model=List[ContextDocumentResponse])
async def list_documents(
    service: RAGDocumentService = Depends(get_rag_document_service)
):
    """
    List all RAG documents with their processing status and chunk count.
    """
    try:
        documents = await service.list_documents()
        return [
            ContextDocumentResponse(
                id=doc["id"],
                filename=doc["filename"],
                storage_url=doc["storage_url"],
                processing_status=ProcessingStatusDto(doc["processing_status"]),
                created_at=doc["created_at"],
                chunks_count=doc["chunks_count"]
            )
            for doc in documents
        ]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{document_id}", response_model=ContextDocumentResponse)
async def get_document(
    document_id: int,
    service: RAGDocumentService = Depends(get_rag_document_service)
):
    """
    Get a specific RAG document by ID.
    """
    try:
        doc = await service.get_document(document_id)
        if not doc:
            raise HTTPException(status_code=404, detail=f"Document {document_id} not found")
        
        return ContextDocumentResponse(
            id=doc["id"],
            filename=doc["filename"],
            storage_url=doc["storage_url"],
            processing_status=ProcessingStatusDto(doc["processing_status"]),
            created_at=doc["created_at"],
            chunks_count=doc["chunks_count"]
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/{document_id}", response_model=DocumentDeleteResponse)
async def delete_document(
    document_id: int,
    service: RAGDocumentService = Depends(get_rag_document_service)
):
    """
    Delete a RAG document and all its chunks.
    """
    try:
        result = await service.delete_document(document_id)
        return DocumentDeleteResponse(
            status=result["status"],
            message=result["message"]
        )
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
