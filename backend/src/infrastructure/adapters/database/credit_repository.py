from typing import List, Optional
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func

from src.domain.entities.credit import Credit, CreditStatus
from src.domain.ports.credit_repository import CreditRepositoryPort
from .models import CreditModel, EstadoCreditoEnum


class SupabaseCreditRepository(CreditRepositoryPort):
    """Supabase implementation of CreditRepositoryPort using SQLAlchemy"""
    
    def __init__(self, db_session: AsyncSession):
        self.db = db_session
    
    def _model_to_entity(self, model: CreditModel) -> Credit:
        """Convert database model to domain entity"""
        # Convert database enum to string
        estado_str = model.estado.value if isinstance(model.estado, EstadoCreditoEnum) else model.estado
        
        return Credit(
            id=model.id,
            client_id=model.client_id,
            monto_aprobado=model.monto_aprobado,
            plazo_meses=model.plazo_meses,
            tasa_interes=model.tasa_interes,
            estado=estado_str,
            fecha_desembolso=model.fecha_desembolso,
            created_at=model.created_at
        )
    
    def _entity_to_model(self, entity: Credit) -> CreditModel:
        """Convert domain entity to database model"""
        # Convert string to database enum
        estado_enum = EstadoCreditoEnum(entity.estado)
        
        return CreditModel(
            id=entity.id,
            client_id=entity.client_id,
            monto_aprobado=entity.monto_aprobado,
            plazo_meses=entity.plazo_meses,
            tasa_interes=entity.tasa_interes,
            estado=estado_enum,
            fecha_desembolso=entity.fecha_desembolso,
            created_at=entity.created_at or datetime.now()
        )
    
    async def create(self, credit: Credit) -> Credit:
        """Create a new credit"""
        try:
            model = self._entity_to_model(credit)
            model.id = None  # Ensure new record
            
            self.db.add(model)
            await self.db.flush()
            await self.db.refresh(model)
            
            return self._model_to_entity(model)
            
        except Exception as e:
            raise Exception(f"Error creating credit: {str(e)}")
    
    async def get_by_id(self, credit_id: int) -> Optional[Credit]:
        """Get credit by ID"""
        try:
            stmt = select(CreditModel).where(CreditModel.id == credit_id)
            result = await self.db.execute(stmt)
            model = result.scalar_one_or_none()
            
            if model:
                return self._model_to_entity(model)
            return None
            
        except Exception as e:
            raise Exception(f"Error getting credit by ID: {str(e)}")
    
    async def get_by_client_id(self, client_id: int) -> List[Credit]:
        """Get all credits for a client"""
        try:
            stmt = select(CreditModel).where(
                CreditModel.client_id == client_id
            ).order_by(CreditModel.created_at.desc())
            
            result = await self.db.execute(stmt)
            models = result.scalars().all()
            
            return [self._model_to_entity(model) for model in models]
            
        except Exception as e:
            raise Exception(f"Error getting credits by client ID: {str(e)}")
    
    async def get_all(self, skip: int = 0, limit: int = 100) -> List[Credit]:
        """Get all credits with pagination"""
        try:
            stmt = select(CreditModel).order_by(
                CreditModel.created_at.desc()
            ).offset(skip).limit(limit)
            
            result = await self.db.execute(stmt)
            models = result.scalars().all()
            
            return [self._model_to_entity(model) for model in models]
            
        except Exception as e:
            raise Exception(f"Error getting all credits: {str(e)}")
    
    async def update(self, credit: Credit) -> Credit:
        """Update credit"""
        try:
            stmt = select(CreditModel).where(CreditModel.id == credit.id)
            result = await self.db.execute(stmt)
            model = result.scalar_one_or_none()
            
            if not model:
                raise Exception(f"Credit with ID {credit.id} not found")
            
            # Update fields
            model.monto_aprobado = credit.monto_aprobado
            model.plazo_meses = credit.plazo_meses
            model.tasa_interes = credit.tasa_interes
            model.estado = EstadoCreditoEnum(credit.estado)
            model.fecha_desembolso = credit.fecha_desembolso
            
            await self.db.flush()
            await self.db.refresh(model)
            
            return self._model_to_entity(model)
            
        except Exception as e:
            raise Exception(f"Error updating credit: {str(e)}")
    
    async def delete(self, credit_id: int) -> bool:
        """Delete credit"""
        try:
            stmt = select(CreditModel).where(CreditModel.id == credit_id)
            result = await self.db.execute(stmt)
            model = result.scalar_one_or_none()
            
            if not model:
                return False
            
            await self.db.delete(model)
            await self.db.flush()
            
            return True
            
        except Exception as e:
            raise Exception(f"Error deleting credit: {str(e)}")
    
    async def count_total(self) -> int:
        """Count total credits"""
        try:
            stmt = select(func.count(CreditModel.id))
            result = await self.db.execute(stmt)
            return result.scalar()
            
        except Exception as e:
            raise Exception(f"Error counting credits: {str(e)}")
    
    async def get_by_status(self, status: str, skip: int = 0, limit: int = 100) -> List[Credit]:
        """Get credits by status"""
        try:
            stmt = select(CreditModel).where(
                CreditModel.estado == status
            ).order_by(CreditModel.created_at.desc()).offset(skip).limit(limit)
            
            result = await self.db.execute(stmt)
            models = result.scalars().all()
            
            return [self._model_to_entity(model) for model in models]
            
        except Exception as e:
            raise Exception(f"Error getting credits by status: {str(e)}")
    
    async def get_active_credits(self, skip: int = 0, limit: int = 100) -> List[Credit]:
        """Get active credits"""
        try:
            active_statuses = [EstadoCreditoEnum.AL_DIA, EstadoCreditoEnum.DESEMBOLSADO]
            stmt = select(CreditModel).where(
                CreditModel.estado.in_(active_statuses)
            ).order_by(CreditModel.created_at.desc()).offset(skip).limit(limit)
            
            result = await self.db.execute(stmt)
            models = result.scalars().all()
            
            return [self._model_to_entity(model) for model in models]
            
        except Exception as e:
            raise Exception(f"Error getting active credits: {str(e)}")
    
    async def get_overdue_credits(self, skip: int = 0, limit: int = 100) -> List[Credit]:
        """Get overdue credits"""
        try:
            stmt = select(CreditModel).where(
                CreditModel.estado == EstadoCreditoEnum.EN_MORA
            ).order_by(CreditModel.created_at.desc()).offset(skip).limit(limit)
            
            result = await self.db.execute(stmt)
            models = result.scalars().all()
            
            return [self._model_to_entity(model) for model in models]
            
        except Exception as e:
            raise Exception(f"Error getting overdue credits: {str(e)}")
    
    async def get_credits_for_disbursement(self, skip: int = 0, limit: int = 100) -> List[Credit]:
        """Get approved credits ready for disbursement"""
        try:
            stmt = select(CreditModel).where(
                CreditModel.estado == EstadoCreditoEnum.APROBADO
            ).order_by(CreditModel.created_at.desc()).offset(skip).limit(limit)
            
            result = await self.db.execute(stmt)
            models = result.scalars().all()
            
            return [self._model_to_entity(model) for model in models]
            
        except Exception as e:
            raise Exception(f"Error getting credits for disbursement: {str(e)}")
    
    async def get_by_date_range(self, start_date, end_date, skip: int = 0, limit: int = 100) -> List[Credit]:
        """Get credits within date range"""
        try:
            stmt = select(CreditModel).where(
                CreditModel.created_at >= start_date,
                CreditModel.created_at <= end_date
            ).order_by(CreditModel.created_at.desc()).offset(skip).limit(limit)
            
            result = await self.db.execute(stmt)
            models = result.scalars().all()
            
            return [self._model_to_entity(model) for model in models]
            
        except Exception as e:
            raise Exception(f"Error getting credits by date range: {str(e)}")
    
    async def update_status(self, credit_id: int, new_status: str) -> bool:
        """Update credit status"""
        try:
            stmt = select(CreditModel).where(CreditModel.id == credit_id)
            result = await self.db.execute(stmt)
            model = result.scalar_one_or_none()
            
            if not model:
                return False
            
            model.estado = EstadoCreditoEnum(new_status)
            await self.db.flush()
            
            return True
            
        except Exception as e:
            raise Exception(f"Error updating credit status: {str(e)}")
    
    async def count_by_status(self, status: str) -> int:
        """Count credits by status"""
        try:
            stmt = select(func.count(CreditModel.id)).where(CreditModel.estado == status)
            result = await self.db.execute(stmt)
            return result.scalar()
            
        except Exception as e:
            raise Exception(f"Error counting credits by status: {str(e)}")
    
    async def get_portfolio_summary(self) -> dict:
        """Get credit portfolio summary"""
        try:
            # Count by status
            total_stmt = select(func.count(CreditModel.id))
            total_result = await self.db.execute(total_stmt)
            total_credits = total_result.scalar()
            
            # Sum amounts by status
            amount_stmt = select(func.sum(CreditModel.monto_aprobado))
            amount_result = await self.db.execute(amount_stmt)
            total_amount = amount_result.scalar() or 0
            
            return {
                "total_credits": total_credits,
                "total_amount": float(total_amount),
                "average_amount": float(total_amount / total_credits) if total_credits > 0 else 0
            }
            
        except Exception as e:
            raise Exception(f"Error getting portfolio summary: {str(e)}")
    
    async def calculate_total_disbursed(self) -> float:
        """Calculate total amount disbursed"""
        try:
            stmt = select(func.sum(CreditModel.monto_aprobado)).where(
                CreditModel.estado.in_([EstadoCreditoEnum.DESEMBOLSADO, EstadoCreditoEnum.PAGADO])
            )
            result = await self.db.execute(stmt)
            return float(result.scalar() or 0)
            
        except Exception as e:
            raise Exception(f"Error calculating total disbursed: {str(e)}")
    
    async def calculate_total_outstanding(self) -> float:
        """Calculate total outstanding amount"""
        try:
            stmt = select(func.sum(CreditModel.monto_aprobado)).where(
                CreditModel.estado == EstadoCreditoEnum.AL_DIA
            )
            result = await self.db.execute(stmt)
            return float(result.scalar() or 0)
            
        except Exception as e:
            raise Exception(f"Error calculating total outstanding: {str(e)}")