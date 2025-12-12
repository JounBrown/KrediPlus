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
    
    async def get_by_convenio(self, convenio: str, skip: int = 0, limit: int = 100) -> List[LoanApplication]:
        """Get applications by convenio"""
        try:
            stmt = select(ApplicationModel).where(
                ApplicationModel.convenio == convenio
            ).order_by(ApplicationModel.created_at.desc()).offset(skip).limit(limit)
            
            result = await self.db.execute(stmt)
            models = result.scalars().all()
            
            return [self._model_to_entity(model) for model in models]
            
        except Exception as e:
            raise Exception(f"Error getting applications by convenio: {str(e)}")
    
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
    
    async def count_by_convenio(self, convenio: str) -> int:
        """Count applications by convenio"""
        try:
            stmt = select(func.count(ApplicationModel.id)).where(
                ApplicationModel.convenio == convenio
            )
            result = await self.db.execute(stmt)
            return result.scalar() or 0
            
        except Exception as e:
            raise Exception(f"Error counting applications by convenio: {str(e)}")
    
    async def count_total(self) -> int:
        """Get total count of applications"""
        try:
            stmt = select(func.count(ApplicationModel.id))
            result = await self.db.execute(stmt)
            return result.scalar() or 0
            
        except Exception as e:
            raise Exception(f"Error counting total applications: {str(e)}")
    
    async def get_statistics(self) -> dict:
        """Get application statistics (counts by convenio, etc.)"""
        try:
            # Total count
            total = await self.count_total()
            
            # Count by convenio
            stmt = select(ApplicationModel.convenio, func.count(ApplicationModel.id)).group_by(ApplicationModel.convenio)
            result = await self.db.execute(stmt)
            convenio_counts = {row[0] or "Sin convenio": row[1] for row in result.fetchall()}
            
            # Count by month
            stmt = select(
                func.date_trunc('month', ApplicationModel.created_at).label('month'),
                func.count(ApplicationModel.id)
            ).group_by(func.date_trunc('month', ApplicationModel.created_at))
            result = await self.db.execute(stmt)
            month_counts = {str(row[0]): row[1] for row in result.fetchall()}
            
            return {
                "total": total,
                "by_convenio": convenio_counts,
                "by_month": month_counts
            }
            
        except Exception as e:
            raise Exception(f"Error getting application statistics: {str(e)}")