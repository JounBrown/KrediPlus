from abc import ABC, abstractmethod
from typing import Optional, List
from src.domain.entities.client_document import ClientDocument


class ClientDocumentRepositoryPort(ABC):
    """Port for ClientDocument repository operations"""
    
    @abstractmethod
    async def create(self, document: ClientDocument) -> ClientDocument:
        """Create a new client document"""
        pass
    
    @abstractmethod
    async def get_by_id(self, document_id: int) -> Optional[ClientDocument]:
        """Get client document by ID"""
        pass
    
    @abstractmethod
    async def get_by_client_id(self, client_id: int) -> List[ClientDocument]:
        """Get all documents for a specific client"""
        pass
    
    @abstractmethod
    async def get_by_credit_id(self, credit_id: int) -> List[ClientDocument]:
        """Get all documents for a specific credit"""
        pass
    
    @abstractmethod
    async def update(self, document: ClientDocument) -> ClientDocument:
        """Update client document"""
        pass
    
    @abstractmethod
    async def delete(self, document_id: int) -> bool:
        """Delete a client document by ID"""
        pass
    
    @abstractmethod
    async def get_all(self) -> List[ClientDocument]:
        """Get all client documents"""
        pass