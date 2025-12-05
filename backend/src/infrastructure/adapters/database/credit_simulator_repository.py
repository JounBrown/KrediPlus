from typing import Optional
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func

from src.domain.entities.credit_simulator import CreditSimulator
from src.domain.ports.credit_simulator_repository import CreditSimulatorRepositoryPort
from .models import CreditSimulatorModel


class SupabaseCreditSimulatorRepository(CreditSimulatorRepositoryPort):
    """Supabase implementation of CreditSimulatorRepositoryPort using SQLAlchemy"""
    
    def __init__(self, db_session: AsyncSession):
        self.db = db_session
    
    def _model_to_entity(self, model: CreditSimulatorModel) -> CreditSimulator:
        """Convert database model to domain entity"""
        return CreditSimulator(
            id=model.id,
            tasa_interes_mensual=model.tasa_interes_mensual,
            monto_minimo=model.monto_minimo,
            monto_maximo=model.monto_maximo,
            plazos_disponibles=model.plazos_disponibles,
            created_at=model.created_at
        )
    
    def _entity_to_model(self, entity: CreditSimulator) -> CreditSimulatorModel:
        """Convert domain entity to database model"""
        return CreditSimulatorModel(
            id=entity.id,
            tasa_interes_mensual=entity.tasa_interes_mensual,
            monto_minimo=entity.monto_minimo,
            monto_maximo=entity.monto_maximo,
            plazos_disponibles=entity.plazos_disponibles,
            created_at=entity.created_at or datetime.now()
        )
    
    async def create(self, simulator: CreditSimulator) -> CreditSimulator:
        """Create a new simulator configuration"""
        try:
            model = self._entity_to_model(simulator)
            model.id = None  # Ensure new record
            
            self.db.add(model)
            await self.db.flush()
            await self.db.refresh(model)
            
            return self._model_to_entity(model)
            
        except Exception as e:
            raise Exception(f"Error creating simulator config: {str(e)}")
    
    async def get_active_config(self) -> Optional[CreditSimulator]:
        """Get the most recent (active) simulator configuration"""
        try:
            stmt = select(CreditSimulatorModel).order_by(
                CreditSimulatorModel.created_at.desc()
            ).limit(1)
            
            result = await self.db.execute(stmt)
            model = result.scalar_one_or_none()
            
            if model:
                return self._model_to_entity(model)
            return None
            
        except Exception as e:
            raise Exception(f"Error getting active config: {str(e)}")
    
    async def update(self, simulator: CreditSimulator) -> CreditSimulator:
        """Update simulator configuration"""
        try:
            stmt = select(CreditSimulatorModel).where(CreditSimulatorModel.id == simulator.id)
            result = await self.db.execute(stmt)
            model = result.scalar_one_or_none()
            
            if not model:
                raise Exception(f"Simulator config with ID {simulator.id} not found")
            
            # Update fields
            model.tasa_interes_mensual = simulator.tasa_interes_mensual
            model.monto_minimo = simulator.monto_minimo
            model.monto_maximo = simulator.monto_maximo
            model.plazos_disponibles = simulator.plazos_disponibles
            
            await self.db.flush()
            await self.db.refresh(model)
            
            return self._model_to_entity(model)
            
        except Exception as e:
            raise Exception(f"Error updating simulator config: {str(e)}")
    
    async def get_by_id(self, config_id: int) -> Optional[CreditSimulator]:
        """Get simulator configuration by ID"""
        try:
            stmt = select(CreditSimulatorModel).where(CreditSimulatorModel.id == config_id)
            result = await self.db.execute(stmt)
            model = result.scalar_one_or_none()
            
            if model:
                return self._model_to_entity(model)
            return None
            
        except Exception as e:
            raise Exception(f"Error getting simulator config by ID: {str(e)}")
    
    async def get_all(self) -> list[CreditSimulator]:
        """Get all simulator configurations"""
        try:
            stmt = select(CreditSimulatorModel).order_by(CreditSimulatorModel.id)
            result = await self.db.execute(stmt)
            models = result.scalars().all()
            
            return [self._model_to_entity(model) for model in models]
            
        except Exception as e:
            raise Exception(f"Error getting all simulator configs: {str(e)}")