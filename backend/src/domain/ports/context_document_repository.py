from abc import ABC, abstractmethod
from typing import List, Optional
from src.domain.entities.context_document import ContextDocument, ProcessingStatus


class ContextDocumentRepositoryPort(ABC):
    """Port for ContextDocument repository operations"""
    
    @abstractmethod
    async def create(self, document: ContextDocument) -> ContextDocument:
        """
        Create a new context document.
        
        Args:
            document: ContextDocument entity to create
            
        Returns:
            Created document with ID
        """
        pass
    
    @abstractmethod
    async def get_by_id(self, document_id: int) -> Optional[ContextDocument]:
        """
        Get a context document by its ID.
        
        Args:
            document_id: ID of the document
            
        Returns:
            ContextDocument if found, None otherwise
        """
        pass
    
    @abstractmethod
    async def get_all(self) -> List[ContextDocument]:
        """
        Get all context documents.
        
        Returns:
            List of all context documents
        """
        pass
    
    @abstractmethod
    async def update_status(
        self, 
        document_id: int, 
        status: ProcessingStatus
    ) -> Optional[ContextDocument]:
        """
        Update the processing status of a document.
        
        Args:
            document_id: ID of the document
            status: New processing status
            
        Returns:
            Updated document if found, None otherwise
        """
        pass
    
    @abstractmethod
    async def delete(self, document_id: int) -> bool:
        """
        Delete a context document by ID.
        
        Note: This should cascade delete associated chunks.
        
        Args:
            document_id: ID of the document to delete
            
        Returns:
            True if deletion was successful
        """
        pass
    
    @abstractmethod
    async def get_by_status(self, status: ProcessingStatus) -> List[ContextDocument]:
        """
        Get all documents with a specific processing status.
        
        Args:
            status: Processing status to filter by
            
        Returns:
            List of documents with the specified status
        """
        pass
    
    @abstractmethod
    async def count_chunks(self, document_id: int) -> int:
        """
        Count the number of chunks for a document.
        
        Args:
            document_id: ID of the document
            
        Returns:
            Number of chunks associated with the document
        """
        pass
