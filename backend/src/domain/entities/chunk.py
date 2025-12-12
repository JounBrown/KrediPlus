from datetime import datetime
from typing import Optional, List, Dict, Any


class Chunk:
    """Chunk domain entity for RAG system - stores text fragments with embeddings"""
    
    def __init__(
        self,
        id: Optional[int] = None,
        content: str = "",
        metadata: Optional[Dict[str, Any]] = None,
        documento_id: int = 0,
        embedding: Optional[List[float]] = None,
        created_at: Optional[datetime] = None
    ):
        self.id = id
        self.content = content
        self.metadata = metadata or {}
        self.documento_id = documento_id  # FK to context_documents (Spanish name as in DB)
        self.embedding = embedding or []
        self.created_at = created_at or datetime.now()
    
    def validate(self) -> bool:
        """Validate chunk data"""
        if not self.content or not self.content.strip():
            return False
        
        if self.documento_id <= 0:
            return False
        
        return True
    
    def has_embedding(self) -> bool:
        """Check if chunk has an embedding vector"""
        return len(self.embedding) > 0
    
    def set_embedding(self, embedding: List[float]) -> None:
        """Set the embedding vector for this chunk"""
        self.embedding = embedding
    
    def add_metadata(self, key: str, value: Any) -> None:
        """Add metadata to the chunk"""
        self.metadata[key] = value
    
    def get_metadata(self, key: str, default: Any = None) -> Any:
        """Get metadata value by key"""
        return self.metadata.get(key, default)
