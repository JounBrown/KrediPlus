from typing import List, Optional
from fastapi import UploadFile
from src.domain.entities.client_document import ClientDocument, DocumentType
from src.domain.ports.client_document_repository import ClientDocumentRepositoryPort
from src.domain.ports.storage_port import StoragePort
from src.application.dtos.client_document_dtos import (
    CreateClientDocumentRequest,
    UpdateClientDocumentRequest,
    ClientDocumentResponse
)


class ClientDocumentService:
    """Service for client document operations"""
    
    def __init__(self, document_repository: ClientDocumentRepositoryPort, storage_service: StoragePort):
        self._document_repository = document_repository
        self._storage_service = storage_service
    
    async def upload_document(
        self,
        file: UploadFile,
        document_type: str,
        client_id: int,
        credit_id: Optional[int] = None
    ) -> dict:
        """
        Upload a document file and save record to database
        
        Args:
            file: The uploaded file
            document_type: Type of document (must be valid enum value)
            client_id: ID of the client
            credit_id: Optional ID of the credit
            
        Returns:
            Dictionary with upload result
            
        Raises:
            ValueError: If validation fails
            Exception: If upload or database operation fails
        """
        try:
            # Validate document type
            try:
                doc_type = DocumentType(document_type)
            except ValueError:
                valid_types = [dt.value for dt in DocumentType]
                raise ValueError(f"Invalid document_type. Must be one of: {valid_types}")
            
            # Validate file
            if not file.filename:
                raise ValueError("File must have a filename")
            
            # Generate unique filename
            unique_filename = self._storage_service.generate_unique_filename(
                document_type, file.filename
            )
            
            # Build storage path
            storage_path = self._storage_service.build_storage_path(client_id, unique_filename)
            
            # Read file content
            file_content = await file.read()
            
            if not file_content:
                raise ValueError("File is empty")
            
            # Upload to Supabase Storage
            try:
                await self._storage_service.upload_file(file_content, storage_path)
            except Exception as e:
                raise Exception(f"Error al subir el archivo a Supabase Storage: {str(e)}")
            
            # Create document entity
            document = ClientDocument(
                file_name=file.filename,
                storage_path=storage_path,
                document_type=doc_type,
                client_id=client_id,
                credit_id=credit_id
            )
            
            # Validate document
            if not document.validate():
                # If database insertion fails, try to clean up uploaded file
                await self._storage_service.delete_file(storage_path)
                raise ValueError("Invalid document data")
            
            # Save to database
            try:
                created_document = await self._document_repository.create(document)
            except Exception as e:
                # If database insertion fails, try to clean up uploaded file
                await self._storage_service.delete_file(storage_path)
                raise Exception(f"Error saving document to database: {str(e)}")
            
            # Generate URL for the uploaded file
            try:
                file_url = self._storage_service.get_public_url(storage_path)
            except Exception:
                # If public URL fails, create signed URL as fallback
                file_url = self._storage_service.create_signed_url(storage_path, expires_in=86400)  # 24 hours
            
            return {
                "status": "success",
                "message": "Archivo subido exitosamente",
                "path": storage_path,
                "document_id": created_document.id,
                "file_url": file_url
            }
            
        except ValueError as e:
            raise e
        except Exception as e:
            raise Exception(f"Unexpected error during file upload: {str(e)}")
    
    async def get_client_documents(self, client_id: int) -> List[ClientDocumentResponse]:
        """Get all documents for a client"""
        try:
            documents = await self._document_repository.get_by_client_id(client_id)
            
            result = []
            for doc in documents:
                # Generate URL for each document
                try:
                    file_url = self._storage_service.get_public_url(doc.storage_path)
                except Exception:
                    # If public URL fails, create signed URL as fallback
                    file_url = self._storage_service.create_signed_url(doc.storage_path, expires_in=86400)  # 24 hours
                
                result.append(ClientDocumentResponse(
                    id=doc.id,
                    file_name=doc.file_name,
                    storage_path=doc.storage_path,
                    document_type=doc.document_type.value,
                    client_id=doc.client_id,
                    credit_id=doc.credit_id,
                    created_at=doc.created_at.isoformat(),
                    file_url=file_url
                ))
            
            return result
            
        except Exception as e:
            raise Exception(f"Error getting client documents: {str(e)}")
    
    async def get_credit_documents(self, credit_id: int) -> List[ClientDocumentResponse]:
        """Get all documents for a credit"""
        try:
            documents = await self._document_repository.get_by_credit_id(credit_id)
            
            result = []
            for doc in documents:
                # Generate URL for each document
                try:
                    file_url = self._storage_service.get_public_url(doc.storage_path)
                except Exception:
                    # If public URL fails, create signed URL as fallback
                    file_url = self._storage_service.create_signed_url(doc.storage_path, expires_in=86400)  # 24 hours
                
                result.append(ClientDocumentResponse(
                    id=doc.id,
                    file_name=doc.file_name,
                    storage_path=doc.storage_path,
                    document_type=doc.document_type.value,
                    client_id=doc.client_id,
                    credit_id=doc.credit_id,
                    created_at=doc.created_at.isoformat(),
                    file_url=file_url
                ))
            
            return result
            
        except Exception as e:
            raise Exception(f"Error getting credit documents: {str(e)}")
    
    async def delete_document(self, document_id: int) -> dict:
        """Delete a document and its file from storage"""
        try:
            # Get document first
            document = await self._document_repository.get_by_id(document_id)
            if not document:
                raise ValueError(f"Document with ID {document_id} not found")
            
            # Delete from database
            success = await self._document_repository.delete(document_id)
            if not success:
                raise Exception("Failed to delete document from database")
            
            # Delete from storage (don't fail if this doesn't work)
            await self._storage_service.delete_file(document.storage_path)
            
            return {
                "status": "success",
                "message": f"Document {document_id} deleted successfully"
            }
            
        except ValueError as e:
            raise e
        except Exception as e:
            raise Exception(f"Error deleting document: {str(e)}")
    
    async def delete_client_document(self, client_id: int, document_id: int) -> dict:
        """Delete a document that belongs to a specific client"""
        try:
            # Get document first
            document = await self._document_repository.get_by_id(document_id)
            if not document:
                raise ValueError(f"Document with ID {document_id} not found")
            
            # Validate that document belongs to the specified client
            if document.client_id != client_id:
                raise ValueError(f"Document {document_id} does not belong to client {client_id}")
            
            # Delete from database
            success = await self._document_repository.delete(document_id)
            if not success:
                raise Exception("Failed to delete document from database")
            
            # Delete from storage (don't fail if this doesn't work)
            await self._storage_service.delete_file(document.storage_path)
            
            return {
                "status": "success",
                "message": f"Document {document_id} deleted successfully from client {client_id}"
            }
            
        except ValueError as e:
            raise e
        except Exception as e:
            raise Exception(f"Error deleting client document: {str(e)}")
    
    async def delete_credit_document(self, credit_id: int, document_id: int) -> dict:
        """Delete a document that belongs to a specific credit"""
        try:
            # Get document first
            document = await self._document_repository.get_by_id(document_id)
            if not document:
                raise ValueError(f"Document with ID {document_id} not found")
            
            # Validate that document belongs to the specified credit
            if document.credit_id != credit_id:
                raise ValueError(f"Document {document_id} does not belong to credit {credit_id}")
            
            # Delete from database
            success = await self._document_repository.delete(document_id)
            if not success:
                raise Exception("Failed to delete document from database")
            
            # Delete from storage (don't fail if this doesn't work)
            await self._storage_service.delete_file(document.storage_path)
            
            return {
                "status": "success",
                "message": f"Document {document_id} deleted successfully from credit {credit_id}"
            }
            
        except ValueError as e:
            raise e
        except Exception as e:
            raise Exception(f"Error deleting credit document: {str(e)}")

    async def get_document_download_url(self, document_id: int, expires_in: int = 3600) -> str:
        """Get a signed URL for downloading a document"""
        try:
            document = await self._document_repository.get_by_id(document_id)
            if not document:
                raise ValueError(f"Document with ID {document_id} not found")
            
            # Create signed URL
            signed_url = self._storage_service.create_signed_url(
                document.storage_path, expires_in
            )
            
            return signed_url
            
        except ValueError as e:
            raise e
        except Exception as e:
            raise Exception(f"Error creating download URL: {str(e)}")