from abc import ABC, abstractmethod
from typing import List


class EmbeddingPort(ABC):
    """
    Port for embedding generation operations.
    
    This interface allows decoupling from specific embedding providers (OpenAI, Cohere, etc.)
    To change provider, implement this interface with a new adapter.
    """
    
    @abstractmethod
    async def generate_embedding(self, text: str) -> List[float]:
        """
        Generate an embedding vector for the given text.
        
        Args:
            text: The text to generate an embedding for
            
        Returns:
            List of floats representing the embedding vector (1536 dimensions for OpenAI)
            
        Raises:
            Exception: If embedding generation fails
        """
        pass
    
    @abstractmethod
    async def generate_embeddings_batch(self, texts: List[str]) -> List[List[float]]:
        """
        Generate embedding vectors for multiple texts in batch.
        
        Args:
            texts: List of texts to generate embeddings for
            
        Returns:
            List of embedding vectors, one for each input text
            
        Raises:
            Exception: If embedding generation fails
        """
        pass
