import uuid
import os
from typing import Optional, Tuple
from supabase import create_client, Client
from src.config import SUPABASE_URL, SUPABASE_SERVICE_KEY
from src.domain.ports.storage_port import StoragePort


class SupabaseStorageService(StoragePort):
    """Service for handling file uploads to Supabase Storage"""
    
    def __init__(self):
        self.supabase: Client = create_client(SUPABASE_URL, SUPABASE_SERVICE_KEY)
        self.bucket_name = "krediplus_docs"
    
    def generate_unique_filename(self, document_type: str, original_filename: str) -> str:
        """
        Generate a unique filename using document type and UUID
        
        Args:
            document_type: Type of document (e.g., CEDULA_FRENTE)
            original_filename: Original filename with extension
            
        Returns:
            Unique filename in format: {document_type}_{uuid}.{extension}
        """
        # Extract file extension
        file_extension = ""
        if "." in original_filename:
            file_extension = original_filename.split(".")[-1].lower()
        
        # Generate UUID
        unique_id = str(uuid.uuid4())
        
        # Create unique filename
        if file_extension:
            return f"{document_type}_{unique_id}.{file_extension}"
        else:
            return f"{document_type}_{unique_id}"
    
    def build_storage_path(self, client_id: int, filename: str) -> str:
        """
        Build the storage path for the file
        
        Args:
            client_id: ID of the client
            filename: Unique filename
            
        Returns:
            Storage path in format: client_files/{client_id}/{filename}
        """
        return f"client_files/{client_id}/{filename}"
    
    async def upload_file(self, file_content: bytes, storage_path: str) -> bool:
        """
        Upload file to Supabase Storage
        
        Args:
            file_content: File content as bytes
            storage_path: Full storage path for the file
            
        Returns:
            True if upload successful, False otherwise
            
        Raises:
            Exception: If upload fails
        """
        try:
            # Upload file to Supabase Storage
            response = self.supabase.storage.from_(self.bucket_name).upload(
                path=storage_path,
                file=file_content,
                file_options={"content-type": "application/octet-stream"}
            )
            
            # Check if upload was successful
            if hasattr(response, 'error') and response.error:
                raise Exception(f"Supabase Storage error: {response.error}")
            
            return True
            
        except Exception as e:
            raise Exception(f"Error uploading file to Supabase Storage: {str(e)}")
    
    async def delete_file(self, storage_path: str) -> bool:
        """
        Delete file from Supabase Storage
        
        Args:
            storage_path: Full storage path of the file to delete
            
        Returns:
            True if deletion successful, False otherwise
        """
        try:
            response = self.supabase.storage.from_(self.bucket_name).remove([storage_path])
            
            if hasattr(response, 'error') and response.error:
                raise Exception(f"Supabase Storage error: {response.error}")
            
            return True
            
        except Exception as e:
            # Log error but don't raise - file might not exist
            print(f"Warning: Could not delete file from storage: {str(e)}")
            return False
    
    def get_public_url(self, storage_path: str) -> str:
        """
        Get public URL for a file (if bucket is public)
        
        Args:
            storage_path: Full storage path of the file
            
        Returns:
            Public URL of the file
        """
        try:
            response = self.supabase.storage.from_(self.bucket_name).get_public_url(storage_path)
            return response
        except Exception as e:
            raise Exception(f"Error getting public URL: {str(e)}")
    
    def create_signed_url(self, storage_path: str, expires_in: int = 3600) -> str:
        """
        Create a signed URL for private file access
        
        Args:
            storage_path: Full storage path of the file
            expires_in: URL expiration time in seconds (default: 1 hour)
            
        Returns:
            Signed URL for the file
        """
        try:
            response = self.supabase.storage.from_(self.bucket_name).create_signed_url(
                path=storage_path,
                expires_in=expires_in
            )
            
            if hasattr(response, 'error') and response.error:
                raise Exception(f"Supabase Storage error: {response.error}")
            
            return response.get('signedURL', '')
            
        except Exception as e:
            raise Exception(f"Error creating signed URL: {str(e)}")