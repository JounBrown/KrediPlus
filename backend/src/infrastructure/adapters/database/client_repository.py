from typing import List, Optional
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, or_

from src.domain.entities.client import Client
from src.domain.ports.client_repository import ClientRepositoryPort
from .models import ClientModel


class SupabaseClientRepository(ClientRepositoryPort):
    """Supabase implementation of ClientRepositoryPort using SQLAlchemy"""
    
    def __init__(self, db_session: AsyncSession):
        self.db = db_session
    
    def _model_to_entity(self, model: ClientModel) -> Client:
        """Convert database model to domain entity"""
        return Client(
            id=model.id,
            nombre_completo=model.nombre_completo,
            cedula=model.cedula,
            email=model.email,
            telefono=model.telefono,
            fecha_nacimiento=model.fecha_nacimiento,
            direccion=model.direccion,
            info_adicional=model.info_adicional,
            created_at=model.created_at
        )
    
    def _entity_to_model(self, entity: Client) -> ClientModel:
        """Convert domain entity to database model"""
        return ClientModel(
            id=entity.id,
            nombre_completo=entity.nombre_completo,
            cedula=entity.cedula,
            email=entity.email,
            telefono=entity.telefono,
            fecha_nacimiento=entity.fecha_nacimiento,
            direccion=entity.direccion,
            info_adicional=entity.info_adicional,
            created_at=entity.created_at or datetime.now()
        )
    
    async def create(self, client: Client) -> Client:
        """Create a new client"""
        try:
            model = self._entity_to_model(client)
            model.id = None  # Ensure new record
            
            self.db.add(model)
            await self.db.flush()
            await self.db.refresh(model)
            
            return self._model_to_entity(model)
            
        except Exception as e:
            await self.db.rollback()
            raise Exception(f"Error creating client: {str(e)}")
    
    async def get_by_id(self, client_id: int) -> Optional[Client]:
        """Get client by ID"""
        try:
            stmt = select(ClientModel).where(ClientModel.id == client_id)
            result = await self.db.execute(stmt)
            model = result.scalar_one_or_none()
            
            if model:
                return self._model_to_entity(model)
            return None
            
        except Exception as e:
            raise Exception(f"Error getting client by ID: {str(e)}")
    
    async def get_by_cedula(self, cedula: str) -> Optional[Client]:
        """Get client by cedula"""
        try:
            stmt = select(ClientModel).where(ClientModel.cedula == cedula)
            result = await self.db.execute(stmt)
            model = result.scalar_one_or_none()
            
            if model:
                return self._model_to_entity(model)
            return None
            
        except Exception as e:
            raise Exception(f"Error getting client by cedula: {str(e)}")
    
    async def get_by_email(self, email: str) -> Optional[Client]:
        """Get client by email"""
        try:
            stmt = select(ClientModel).where(ClientModel.email == email.lower())
            result = await self.db.execute(stmt)
            model = result.scalar_one_or_none()
            
            if model:
                return self._model_to_entity(model)
            return None
            
        except Exception as e:
            raise Exception(f"Error getting client by email: {str(e)}")
    
    async def get_all(self, skip: int = 0, limit: int = 100) -> List[Client]:
        """Get all clients with pagination"""
        try:
            stmt = select(ClientModel).order_by(
                ClientModel.created_at.desc()
            ).offset(skip).limit(limit)
            
            result = await self.db.execute(stmt)
            models = result.scalars().all()
            
            return [self._model_to_entity(model) for model in models]
            
        except Exception as e:
            raise Exception(f"Error getting all clients: {str(e)}")
    
    async def search_by_name(self, name: str, skip: int = 0, limit: int = 100) -> List[Client]:
        """Search clients by name"""
        try:
            search_pattern = f"%{name}%"
            stmt = select(ClientModel).where(
                ClientModel.nombre_completo.ilike(search_pattern)
            ).order_by(ClientModel.created_at.desc()).offset(skip).limit(limit)
            
            result = await self.db.execute(stmt)
            models = result.scalars().all()
            
            return [self._model_to_entity(model) for model in models]
            
        except Exception as e:
            raise Exception(f"Error searching clients by name: {str(e)}")
    
    async def search_by_cedula(self, cedula: str) -> List[Client]:
        """Search clients by cedula (partial match)"""
        try:
            search_pattern = f"%{cedula}%"
            stmt = select(ClientModel).where(
                ClientModel.cedula.ilike(search_pattern)
            ).order_by(ClientModel.created_at.desc())
            
            result = await self.db.execute(stmt)
            models = result.scalars().all()
            
            return [self._model_to_entity(model) for model in models]
            
        except Exception as e:
            raise Exception(f"Error searching clients by cedula: {str(e)}")
    
    async def update(self, client: Client) -> Client:
        """Update client"""
        try:
            stmt = select(ClientModel).where(ClientModel.id == client.id)
            result = await self.db.execute(stmt)
            model = result.scalar_one_or_none()
            
            if not model:
                raise ValueError(f"Client with ID {client.id} not found")
            
            # Update model with entity data
            model.nombre_completo = client.nombre_completo
            model.email = client.email
            model.telefono = client.telefono
            model.direccion = client.direccion
            model.info_adicional = client.info_adicional
            
            await self.db.flush()
            await self.db.refresh(model)
            
            return self._model_to_entity(model)
            
        except Exception as e:
            await self.db.rollback()
            raise Exception(f"Error updating client: {str(e)}")
    
    async def delete(self, client_id: int) -> bool:
        """Delete client"""
        try:
            stmt = select(ClientModel).where(ClientModel.id == client_id)
            result = await self.db.execute(stmt)
            model = result.scalar_one_or_none()
            
            if not model:
                return False
            
            await self.db.delete(model)
            await self.db.flush()
            
            return True
            
        except Exception as e:
            await self.db.rollback()
            raise Exception(f"Error deleting client: {str(e)}")
    
    async def exists_by_cedula(self, cedula: str) -> bool:
        """Check if client exists by cedula"""
        try:
            stmt = select(func.count(ClientModel.id)).where(ClientModel.cedula == cedula)
            result = await self.db.execute(stmt)
            count = result.scalar() or 0
            return count > 0
            
        except Exception as e:
            raise Exception(f"Error checking client existence by cedula: {str(e)}")
    
    async def exists_by_email(self, email: str) -> bool:
        """Check if client exists by email"""
        try:
            stmt = select(func.count(ClientModel.id)).where(ClientModel.email == email.lower())
            result = await self.db.execute(stmt)
            count = result.scalar() or 0
            return count > 0
            
        except Exception as e:
            raise Exception(f"Error checking client existence by email: {str(e)}")
    
    async def count_total(self) -> int:
        """Get total count of clients"""
        try:
            stmt = select(func.count(ClientModel.id))
            result = await self.db.execute(stmt)
            return result.scalar() or 0
            
        except Exception as e:
            raise Exception(f"Error counting total clients: {str(e)}")