from typing import List, Optional
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete, text

from src.domain.entities.chunk import Chunk
from src.domain.ports.chunk_repository import ChunkRepositoryPort
from .models import ChunkModel


class SupabaseChunkRepository(ChunkRepositoryPort):
    """Supabase implementation of ChunkRepositoryPort using SQLAlchemy and pgvector"""
    
    def __init__(self, db_session: AsyncSession):
        self.db = db_session
    
    def _model_to_entity(self, model: ChunkModel) -> Chunk:
        """Convert database model to domain entity"""
        return Chunk(
            id=model.id,
            content=model.content,
            metadata=model.chunk_metadata,  # Use chunk_metadata (SQLAlchemy reserved 'metadata')
            documento_id=model.document_id,
            embedding=[],  # Embedding loaded separately if needed
            created_at=model.created_at
        )
    
    async def create(self, chunk: Chunk) -> Chunk:
        """Create a new chunk with embedding using raw SQL for pgvector support"""
        import json
        try:
            # Use raw SQL to insert with vector type
            embedding_str = f"[{','.join(map(str, chunk.embedding))}]" if chunk.embedding else None
            metadata_json = json.dumps(chunk.metadata) if chunk.metadata else None
            created_at = chunk.created_at or datetime.now()
            
            # Use CAST instead of :: for asyncpg compatibility
            query = text("""
                INSERT INTO "Chunk" (content, metadata, document_id, embedding, created_at)
                VALUES (
                    :content, 
                    CAST(:metadata AS json), 
                    :document_id, 
                    CAST(:embedding AS vector), 
                    :created_at
                )
                RETURNING id, created_at
            """)
            
            result = await self.db.execute(query, {
                "content": chunk.content,
                "metadata": metadata_json,
                "document_id": chunk.documento_id,
                "embedding": embedding_str,
                "created_at": created_at
            })
            
            row = result.fetchone()
            chunk.id = row.id
            chunk.created_at = row.created_at
            
            await self.db.commit()
            return chunk
            
        except Exception as e:
            await self.db.rollback()
            raise Exception(f"Error creating chunk: {str(e)}")
    
    async def create_batch(self, chunks: List[Chunk]) -> List[Chunk]:
        """Create multiple chunks in batch"""
        created_chunks = []
        try:
            for chunk in chunks:
                created_chunk = await self.create(chunk)
                created_chunks.append(created_chunk)
            return created_chunks
        except Exception as e:
            await self.db.rollback()
            raise Exception(f"Error creating chunks batch: {str(e)}")
    
    async def get_by_id(self, chunk_id: int) -> Optional[Chunk]:
        """Get a chunk by its ID"""
        try:
            stmt = select(ChunkModel).where(ChunkModel.id == chunk_id)
            result = await self.db.execute(stmt)
            model = result.scalar_one_or_none()
            
            if model:
                return self._model_to_entity(model)
            return None
            
        except Exception as e:
            raise Exception(f"Error getting chunk by ID: {str(e)}")
    
    async def get_by_document_id(self, documento_id: int) -> List[Chunk]:
        """Get all chunks for a specific document"""
        try:
            stmt = select(ChunkModel).where(
                ChunkModel.document_id == documento_id
            ).order_by(ChunkModel.id)
            
            result = await self.db.execute(stmt)
            models = result.scalars().all()
            
            return [self._model_to_entity(model) for model in models]
            
        except Exception as e:
            raise Exception(f"Error getting chunks by document ID: {str(e)}")
    
    async def search_similar(
        self, 
        query_embedding: List[float], 
        match_threshold: float = 0.7,
        match_count: int = 5
    ) -> List[dict]:
        """
        Search for similar chunks using the match_documents function in Supabase.
        Uses cosine similarity via pgvector.
        """
        try:
            embedding_str = f"[{','.join(map(str, query_embedding))}]"
            
            # Use the match_documents function defined in Supabase
            query = text("""
                SELECT * FROM match_documents(
                    CAST(:query_embedding AS vector(1536)),
                    :match_threshold,
                    :match_count
                )
            """)
            
            result = await self.db.execute(query, {
                "query_embedding": embedding_str,
                "match_threshold": match_threshold,
                "match_count": match_count
            })
            
            rows = result.fetchall()
            
            return [
                {
                    "id": row.id,
                    "content": row.content,
                    "metadata": row.metadata,
                    "document_id": row.document_id,
                    "similarity": row.similarity
                }
                for row in rows
            ]
            
        except Exception as e:
            raise Exception(f"Error searching similar chunks: {str(e)}")
    
    async def delete_by_document_id(self, documento_id: int) -> bool:
        """Delete all chunks for a specific document"""
        try:
            stmt = delete(ChunkModel).where(ChunkModel.document_id == documento_id)
            await self.db.execute(stmt)
            await self.db.commit()
            return True
            
        except Exception as e:
            await self.db.rollback()
            raise Exception(f"Error deleting chunks by document ID: {str(e)}")
