from typing import Optional, List
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from src.domain.entities.client_document import ClientDocument, DocumentType
from src.domain.ports.client_document_repository import ClientDocumentRepositoryPort
from .models import ClientDocumentModel, DocumentTypeEnum


class SupabaseClientDocumentRepository(ClientDocumentRepositoryPort):
    """Supabase implementation of ClientDocumentRepositoryPort using SQLAlchemy"""
    
    def __init__(self, db_session: AsyncSession):
        self.db = db_session
    
    def _model_to_entity(self, model: ClientDocumentModel) -> ClientDocument:
        """Convert database model to domain entity"""
        # Convert database enum to domain enum
        if isinstance(model.document_type, DocumentTypeEnum):
            document_type = DocumentType(model.document_type.value)
        else:
            # Fallback for string values
            document_type = DocumentType(model.document_type)
        
        return ClientDocument(
            id=model.id,
            file_name=model.file_name,
            storage_path=model.storage_path,
            document_type=document_type,
            client_id=model.client_id,
            credit_id=model.credit_id,
            created_at=model.created_at
        )
    
    def _entity_to_model(self, entity: ClientDocument) -> ClientDocumentModel:
        """Convert domain entity to database model"""
        # Convert domain enum to database enum
        db_enum = DocumentTypeEnum(entity.document_type.value)
        
        return ClientDocumentModel(
            id=entity.id,
            file_name=entity.file_name,
            storage_path=entity.storage_path,
            document_type=db_enum,
            client_id=entity.client_id,
            credit_id=entity.credit_id,
            created_at=entity.created_at or datetime.now()
        )
    
    async def create(self, document: ClientDocument) -> ClientDocument:
        """Create a new client document"""
        try:
            model = self._entity_to_model(document)
            model.id = None  # Ensure new record
            
            self.db.add(model)
            await self.db.flush()
            await self.db.refresh(model)
            
            return self._model_to_entity(model)
            
        except Exception as e:
            raise Exception(f"Error creating client document: {str(e)}")
    
    async def get_by_id(self, document_id: int) -> Optional[ClientDocument]:
        """Get client document by ID"""
        try:
            stmt = select(ClientDocumentModel).where(ClientDocumentModel.id == document_id)
            result = await self.db.execute(stmt)
            model = result.scalar_one_or_none()
            
            if model:
                return self._model_to_entity(model)
            return None
            
        except Exception as e:
            raise Exception(f"Error getting client document by ID: {str(e)}")
    
    async def get_by_client_id(self, client_id: int) -> List[ClientDocument]:
        """Get all documents for a specific client"""
        try:
            stmt = select(ClientDocumentModel).where(
                ClientDocumentModel.client_id == client_id
            ).order_by(ClientDocumentModel.created_at.desc())
            
            result = await self.db.execute(stmt)
            models = result.scalars().all()
            
            return [self._model_to_entity(model) for model in models]
            
        except Exception as e:
            raise Exception(f"Error getting documents by client ID: {str(e)}")
    
    async def get_by_credit_id(self, credit_id: int) -> List[ClientDocument]:
        """Get all documents for a specific credit"""
        try:
            stmt = select(ClientDocumentModel).where(
                ClientDocumentModel.credit_id == credit_id
            ).order_by(ClientDocumentModel.created_at.desc())
            
            result = await self.db.execute(stmt)
            models = result.scalars().all()
            
            return [self._model_to_entity(model) for model in models]
            
        except Exception as e:
            raise Exception(f"Error getting documents by credit ID: {str(e)}")
    
    async def update(self, document: ClientDocument) -> ClientDocument:
        """Update client document"""
        try:
            stmt = select(ClientDocumentModel).where(ClientDocumentModel.id == document.id)
            result = await self.db.execute(stmt)
            model = result.scalar_one_or_none()
            
            if not model:
                raise Exception(f"Client document with ID {document.id} not found")
            
            # Update fields
            model.file_name = document.file_name
            model.storage_path = document.storage_path
            model.document_type = DocumentTypeEnum(document.document_type.value)
            model.credit_id = document.credit_id
            
            await self.db.flush()
            await self.db.refresh(model)
            
            return self._model_to_entity(model)
            
        except Exception as e:
            raise Exception(f"Error updating client document: {str(e)}")
    
    async def delete(self, document_id: int) -> bool:
        """Delete a client document by ID"""
        try:
            stmt = select(ClientDocumentModel).where(ClientDocumentModel.id == document_id)
            result = await self.db.execute(stmt)
            model = result.scalar_one_or_none()
            
            if not model:
                return False  # Document not found
            
            await self.db.delete(model)
            await self.db.flush()
            
            return True
            
        except Exception as e:
            raise Exception(f"Error deleting client document: {str(e)}")
    
    async def get_all(self) -> List[ClientDocument]:
        """Get all client documents"""
        try:
            stmt = select(ClientDocumentModel).order_by(ClientDocumentModel.created_at.desc())
            result = await self.db.execute(stmt)
            models = result.scalars().all()
            
            return [self._model_to_entity(model) for model in models]
            
        except Exception as e:
            raise Exception(f"Error getting all client documents: {str(e)}")