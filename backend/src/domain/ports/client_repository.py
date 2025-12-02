from abc import ABC, abstractmethod
from typing import List, Optional
from src.domain.entities.client import Client


class ClientRepositoryPort(ABC):
    """Port for Client repository operations"""
    
    @abstractmethod
    async def create(self, client: Client) -> Client:
        """Create a new client"""
        pass
    
    @abstractmethod
    async def get_by_id(self, client_id: int) -> Optional[Client]:
        """Get client by ID"""
        pass
    
    @abstractmethod
    async def get_by_cedula(self, cedula: str) -> Optional[Client]:
        """Get client by cedula"""
        pass
    
    @abstractmethod
    async def get_by_email(self, email: str) -> Optional[Client]:
        """Get client by email"""
        pass
    
    @abstractmethod
    async def get_all(self, skip: int = 0, limit: int = 100) -> List[Client]:
        """Get all clients with pagination"""
        pass
    
    @abstractmethod
    async def search_by_name(self, name: str, skip: int = 0, limit: int = 100) -> List[Client]:
        """Search clients by name"""
        pass
    
    @abstractmethod
    async def search_by_cedula(self, cedula: str) -> List[Client]:
        """Search clients by cedula (partial match)"""
        pass
    
    @abstractmethod
    async def update(self, client: Client) -> Client:
        """Update client"""
        pass
    
    @abstractmethod
    async def delete(self, client_id: int) -> bool:
        """Delete client (soft delete recommended)"""
        pass
    
    @abstractmethod
    async def exists_by_cedula(self, cedula: str) -> bool:
        """Check if client exists by cedula"""
        pass
    
    @abstractmethod
    async def exists_by_email(self, email: str) -> bool:
        """Check if client exists by email"""
        pass
    
    @abstractmethod
    async def count_total(self) -> int:
        """Get total count of clients"""
        pass