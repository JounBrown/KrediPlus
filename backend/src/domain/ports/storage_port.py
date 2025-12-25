from abc import ABC, abstractmethod


class StoragePort(ABC):
    """Port for file storage operations"""
    
    @abstractmethod
    def generate_unique_filename(self, document_type: str, original_filename: str) -> str:
        """Generate a unique filename"""
        pass
    
    @abstractmethod
    def build_storage_path(self, client_id: int, filename: str) -> str:
        """Build the storage path for the file"""
        pass
    
    @abstractmethod
    async def upload_file(self, file_content: bytes, storage_path: str) -> bool:
        """Upload file to storage"""
        pass
    
    @abstractmethod
    async def delete_file(self, storage_path: str) -> bool:
        """Delete file from storage"""
        pass
    
    @abstractmethod
    def get_public_url(self, storage_path: str) -> str:
        """Get public URL for a file"""
        pass
    
    @abstractmethod
    def create_signed_url(self, storage_path: str, expires_in: int = 3600) -> str:
        """Create a signed URL for private file access"""
        pass
