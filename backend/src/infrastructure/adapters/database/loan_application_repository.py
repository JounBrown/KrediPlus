from typing import List, Optional
from datetime import datetime, date
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_

from src.domain.entities.loan_application import LoanApplication
from src.domain.ports.loan_application_repository import LoanApplicationRepositoryPort
from .models import ApplicationModel


class SupabaseLoanApplicationRepository(LoanApplicationRepositoryPort):
    """Supabase implementation of LoanApplicationRepositoryPort using SQLAlchemy"""
    
    def __init__(self, db_session: AsyncSession):
        self.db = db_session
    
    def _model_to_entity(self, model: ApplicationModel) -> LoanApplication:
        """Convert database model to domain entity"""
        return LoanApplication(
            id=model.id,
            name=model.name,
            cedula=model.cedula,
            convenio=model.convenio,
            telefono=model.telefono,
            fecha_nacimiento=model.fecha_nacimiento,
            monto_solicitado=model.monto_solicitado,
            plazo=model.plazo,
            estado=model.estado,
            created_at=model.created_at
        )
    
    def _entity_to_model(self, entity: LoanApplication) -> ApplicationModel:
        """Convert domain entity to database model"""
        return ApplicationModel(
            id=entity.id,
            name=entity.name,
            cedula=entity.cedula,
            convenio=entity.convenio,
            telefono=entity.telefono,
            fecha_nacimiento=entity.fecha_nacimiento,
            monto_solicitado=entity.monto_solicitado,
            plazo=entity.plazo,
            estado=entity.estado,
            created_at=entity.created_at or datetime.now()
        )
    
    async def create(self, application: LoanApplication) -> LoanApplication:
        """Create a new loan application"""
        try:
            # Convert entity to model
            model = self._entity_to_model(application)
            model.id = None  # Ensure new record
            
            # Add to session and flush to get ID
            self.db.add(model)
            await self.db.flush()
            await self.db.refresh(model)
            
            # Convert back to entity with ID
            return self._model_to_entity(model)
            
        except Exception as e:
            raise Exception(f"Error creating loan application: {str(e)}")
    
    async def get_by_id(self, application_id: int) -> Optional[LoanApplication]:
        """Get application by ID"""
        try:
            stmt = select(ApplicationModel).where(ApplicationModel.id == application_id)
            result = await self.db.execute(stmt)
            model = result.scalar_one_or_none()
            
            if model:
                return self._model_to_entity(model)
            return None
            
        except Exception as e:
            raise Exception(f"Error getting application by ID: {str(e)}")
    
    async def get_by_cedula(self, cedula: str) -> List[LoanApplication]:
        """Get applications by cedula"""
        try:
            stmt = select(ApplicationModel).where(
                ApplicationModel.cedula == cedula
            ).order_by(ApplicationModel.created_at.desc())
            
            result = await self.db.execute(stmt)
            models = result.scalars().all()
            
            return [self._model_to_entity(model) for model in models]
            
        except Exception as e:
            raise Exception(f"Error getting applications by cedula: {str(e)}")
    
    async def get_all(self, skip: int = 0, limit: int = 100) -> List[LoanApplication]:
        """Get all applications with pagination"""
        try:
            stmt = select(ApplicationModel).order_by(
                ApplicationModel.created_at.desc()
            ).offset(skip).limit(limit)
            
            result = await self.db.execute(stmt)
            models = result.scalars().all()
            
            return [self._model_to_entity(model) for model in models]
            
        except Exception as e:
            raise Exception(f"Error getting all applications: {str(e)}")
    
    async def get_by_status(self, status: str, skip: int = 0, limit: int = 100) -> List[LoanApplication]:
        """Get applications by status"""
        try:
            stmt = select(ApplicationModel).where(
                ApplicationModel.estado == status
            ).order_by(ApplicationModel.created_at.desc()).offset(skip).limit(limit)
            
            result = await self.db.execute(stmt)
            models = result.scalars().all()
            
            return [self._model_to_entity(model) for model in models]
            
        except Exception as e:
            raise Exception(f"Error getting applications by status: {str(e)}")
    
    async def get_pending_applications(self, skip: int = 0, limit: int = 100) -> List[LoanApplication]:
        """Get applications that need processing (nueva, en_proceso)"""
        try:
            stmt = select(ApplicationModel).where(
                ApplicationModel.estado.in_(["nueva", "en_proceso"])
            ).order_by(ApplicationModel.created_at.desc()).offset(skip).limit(limit)
            
            result = await self.db.execute(stmt)
            models = result.scalars().all()
            
            return [self._model_to_entity(model) for model in models]
            
        except Exception as e:
            raise Exception(f"Error getting pending applications: {str(e)}")
    
    async def search_by_name(self, name: str, skip: int = 0, limit: int = 100) -> List[LoanApplication]:
        """Search applications by applicant name"""
        try:
            # Case-insensitive search using ILIKE
            search_pattern = f"%{name}%"
            stmt = select(ApplicationModel).where(
                ApplicationModel.name.ilike(search_pattern)
            ).order_by(ApplicationModel.created_at.desc()).offset(skip).limit(limit)
            
            result = await self.db.execute(stmt)
            models = result.scalars().all()
            
            return [self._model_to_entity(model) for model in models]
            
        except Exception as e:
            raise Exception(f"Error searching applications by name: {str(e)}")
    
    async def get_by_date_range(self, start_date: date, end_date: date, 
                               skip: int = 0, limit: int = 100) -> List[LoanApplication]:
        """Get applications within date range"""
        try:
            stmt = select(ApplicationModel).where(
                and_(
                    func.date(ApplicationModel.created_at) >= start_date,
                    func.date(ApplicationModel.created_at) <= end_date
                )
            ).order_by(ApplicationModel.created_at.desc()).offset(skip).limit(limit)
            
            result = await self.db.execute(stmt)
            models = result.scalars().all()
            
            return [self._model_to_entity(model) for model in models]
            
        except Exception as e:
            raise Exception(f"Error getting applications by date range: {str(e)}")
    
    async def update(self, application: LoanApplication) -> LoanApplication:
        """Update application"""
        try:
            # Get existing model
            stmt = select(ApplicationModel).where(ApplicationModel.id == application.id)
            result = await self.db.execute(stmt)
            model = result.scalar_one_or_none()
            
            if not model:
                raise ValueError(f"Application with ID {application.id} not found")
            
            # Update model with entity data
            model.name = application.name
            model.cedula = application.cedula
            model.convenio = application.convenio
            model.telefono = application.telefono
            model.fecha_nacimiento = application.fecha_nacimiento
            model.monto_solicitado = application.monto_solicitado
            model.plazo = application.plazo
            model.estado = application.estado
            
            # Flush changes and refresh
            await self.db.flush()
            await self.db.refresh(model)
            
            return self._model_to_entity(model)
            
        except Exception as e:
            await self.db.rollback()
            raise Exception(f"Error updating application: {str(e)}")
    
    async def delete(self, application_id: int) -> bool:
        """Delete application"""
        try:
            stmt = select(ApplicationModel).where(ApplicationModel.id == application_id)
            result = await self.db.execute(stmt)
            model = result.scalar_one_or_none()
            
            if not model:
                return False
            
            await self.db.delete(model)
            await self.db.flush()
            
            return True
            
        except Exception as e:
            await self.db.rollback()
            raise Exception(f"Error deleting application: {str(e)}")
    
    async def update_status(self, application_id: int, new_status: str) -> bool:
        """Update application status"""
        try:
            stmt = select(ApplicationModel).where(ApplicationModel.id == application_id)
            result = await self.db.execute(stmt)
            model = result.scalar_one_or_none()
            
            if not model:
                return False
            
            model.estado = new_status
            await self.db.flush()
            
            return True
            
        except Exception as e:
            await self.db.rollback()
            raise Exception(f"Error updating application status: {str(e)}")
    
    async def count_by_status(self, status: str) -> int:
        """Count applications by status"""
        try:
            stmt = select(func.count(ApplicationModel.id)).where(
                ApplicationModel.estado == status
            )
            result = await self.db.execute(stmt)
            return result.scalar() or 0
            
        except Exception as e:
            raise Exception(f"Error counting applications by status: {str(e)}")
    
    async def count_total(self) -> int:
        """Get total count of applications"""
        try:
            stmt = select(func.count(ApplicationModel.id))
            result = await self.db.execute(stmt)
            return result.scalar() or 0
            
        except Exception as e:
            raise Exception(f"Error counting total applications: {str(e)}")
    
    async def get_statistics(self) -> dict:
        """Get application statistics (counts by status, etc.)"""
        try:
            # Count by status
            status_counts = {}
            statuses = ["nueva", "en_proceso", "aprobada", "rechazada", "cancelada"]
            
            for status in statuses:
                count = await self.count_by_status(status)
                status_counts[status] = count
            
            # Total count
            total = await self.count_total()
            
            # Total amount requested
            stmt = select(func.sum(ApplicationModel.monto_solicitado))
            result = await self.db.execute(stmt)
            total_amount = result.scalar() or 0.0
            
            # Average amount
            stmt = select(func.avg(ApplicationModel.monto_solicitado))
            result = await self.db.execute(stmt)
            avg_amount = result.scalar() or 0.0
            
            # Average term
            stmt = select(func.avg(ApplicationModel.plazo))
            result = await self.db.execute(stmt)
            avg_term = result.scalar() or 0.0
            
            return {
                "total": total,
                **status_counts,
                "total_amount": float(total_amount),
                "average_amount": float(avg_amount),
                "average_term": float(avg_term)
            }
            
        except Exception as e:
            raise Exception(f"Error getting application statistics: {str(e)}")