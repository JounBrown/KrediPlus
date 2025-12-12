from typing import List, Optional
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func

from src.domain.entities.context_document import ContextDocument, ProcessingStatus
from src.domain.ports.context_document_repository import ContextDocumentRepositoryPort
from .models import ContextDocumentModel


class SupabaseContextDocumentRepository(ContextDocumentRepositoryPort):
    """Supabase implementation of ContextDocumentRepositoryPort using SQLAlchemy"""
    
    def __init__(self, db_session: AsyncSession):
        self.db = db_session
    
    def _status_to_db(self, status: ProcessingStatus) -> str:
        """Convert domain ProcessingStatus to database string value"""
        return status.value  # Returns 'pending', 'processing', etc.
    
    def _db_to_status(self, db_val: str) -> ProcessingStatus:
        """Convert database string value to domain ProcessingStatus"""
        return ProcessingStatus(db_val)
    
    def _model_to_entity(self, model: ContextDocumentModel) -> ContextDocument:
        """Convert database model to domain entity"""
        return ContextDocument(
            id=model.id,
            filename=model.filename,
            storage_url=model.storage_url,
            processing_status=self._db_to_status(model.processing_status),
            created_at=model.created_at
        )
    
    def _entity_to_model(self, entity: ContextDocument) -> ContextDocumentModel:
        """Convert domain entity to database model"""
        return ContextDocumentModel(
            id=entity.id,
            filename=entity.filename,
            storage_url=entity.storage_url,
            processing_status=self._status_to_db(entity.processing_status),
            created_at=entity.created_at or datetime.now()
        )
    
    async def create(self, document: ContextDocument) -> ContextDocument:
        """Create a new context document"""
        try:
            model = self._entity_to_model(document)
            model.id = None  # Ensure new record
            
            self.db.add(model)
            await self.db.flush()
            await self.db.refresh(model)
            await self.db.commit()
            
            return self._model_to_entity(model)
            
        except Exception as e:
            await self.db.rollback()
            raise Exception(f"Error creating context document: {str(e)}")
    
    async def get_by_id(self, document_id: int) -> Optional[ContextDocument]:
        """Get a context document by its ID"""
        try:
            stmt = select(ContextDocumentModel).where(ContextDocumentModel.id == document_id)
            result = await self.db.execute(stmt)
            model = result.scalar_one_or_none()
            
            if model:
                return self._model_to_entity(model)
            return None
            
        except Exception as e:
            raise Exception(f"Error getting context document by ID: {str(e)}")
    
    async def get_all(self) -> List[ContextDocument]:
        """Get all context documents"""
        try:
            stmt = select(ContextDocumentModel).order_by(ContextDocumentModel.created_at.desc())
            result = await self.db.execute(stmt)
            models = result.scalars().all()
            
            return [self._model_to_entity(model) for model in models]
            
        except Exception as e:
            raise Exception(f"Error getting all context documents: {str(e)}")
    
    async def update_status(
        self, 
        document_id: int, 
        status: ProcessingStatus
    ) -> Optional[ContextDocument]:
        """Update the processing status of a document"""
        try:
            stmt = select(ContextDocumentModel).where(ContextDocumentModel.id == document_id)
            result = await self.db.execute(stmt)
            model = result.scalar_one_or_none()
            
            if not model:
                return None
            
            model.processing_status = self._status_to_db(status)
            
            await self.db.flush()
            await self.db.refresh(model)
            await self.db.commit()
            
            return self._model_to_entity(model)
            
        except Exception as e:
            await self.db.rollback()
            raise Exception(f"Error updating document status: {str(e)}")
    
    async def delete(self, document_id: int) -> bool:
        """Delete a context document by ID (cascades to chunks)"""
        try:
            stmt = select(ContextDocumentModel).where(ContextDocumentModel.id == document_id)
            result = await self.db.execute(stmt)
            model = result.scalar_one_or_none()
            
            if not model:
                return False
            
            await self.db.delete(model)
            await self.db.commit()
            
            return True
            
        except Exception as e:
            await self.db.rollback()
            raise Exception(f"Error deleting context document: {str(e)}")
    
    async def get_by_status(self, status: ProcessingStatus) -> List[ContextDocument]:
        """Get all documents with a specific processing status"""
        try:
            stmt = select(ContextDocumentModel).where(
                ContextDocumentModel.processing_status == self._status_to_db(status)
            ).order_by(ContextDocumentModel.created_at.desc())
            
            result = await self.db.execute(stmt)
            models = result.scalars().all()
            
            return [self._model_to_entity(model) for model in models]
            
        except Exception as e:
            raise Exception(f"Error getting documents by status: {str(e)}")
    
    async def count_chunks(self, document_id: int) -> int:
        """Count the number of chunks for a document"""
        try:
            from .models import ChunkModel
            stmt = select(func.count(ChunkModel.id)).where(ChunkModel.document_id == document_id)
            result = await self.db.execute(stmt)
            return result.scalar() or 0
            
        except Exception as e:
            raise Exception(f"Error counting chunks: {str(e)}")
