from abc import ABC, abstractmethod
from typing import List, Optional
from src.domain.entities.chunk import Chunk


class ChunkRepositoryPort(ABC):
    """Port for Chunk repository operations"""
    
    @abstractmethod
    async def create(self, chunk: Chunk) -> Chunk:
        """
        Create a new chunk in the database.
        
        Args:
            chunk: Chunk entity to create
            
        Returns:
            Created chunk with ID
        """
        pass
    
    @abstractmethod
    async def create_batch(self, chunks: List[Chunk]) -> List[Chunk]:
        """
        Create multiple chunks in batch.
        
        Args:
            chunks: List of chunk entities to create
            
        Returns:
            List of created chunks with IDs
        """
        pass
    
    @abstractmethod
    async def get_by_id(self, chunk_id: int) -> Optional[Chunk]:
        """
        Get a chunk by its ID.
        
        Args:
            chunk_id: ID of the chunk
            
        Returns:
            Chunk if found, None otherwise
        """
        pass
    
    @abstractmethod
    async def get_by_document_id(self, documento_id: int) -> List[Chunk]:
        """
        Get all chunks for a specific document.
        
        Args:
            documento_id: ID of the context document
            
        Returns:
            List of chunks belonging to the document
        """
        pass
    
    @abstractmethod
    async def search_similar(
        self, 
        query_embedding: List[float], 
        match_threshold: float = 0.7,
        match_count: int = 5
    ) -> List[dict]:
        """
        Search for chunks similar to the query embedding.
        
        Uses vector similarity search (cosine distance).
        
        Args:
            query_embedding: Embedding vector of the query
            match_threshold: Minimum similarity threshold (0.0 - 1.0)
            match_count: Maximum number of results to return
            
        Returns:
            List of dicts with chunk data and similarity score
        """
        pass
    
    @abstractmethod
    async def delete_by_document_id(self, documento_id: int) -> bool:
        """
        Delete all chunks for a specific document.
        
        Args:
            documento_id: ID of the context document
            
        Returns:
            True if deletion was successful
        """
        pass
