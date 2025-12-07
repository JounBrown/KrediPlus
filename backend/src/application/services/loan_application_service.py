from typing import List, Optional
from src.domain.ports.loan_application_repository import LoanApplicationRepositoryPort
from src.application.services.create_loan_application_service import CreateLoanApplicationService

from src.application.services.list_client_loan_applications_service import ListClientLoanApplicationsService
from src.application.dtos.loan_application_dtos import (
    CreateLoanApplicationRequest,
    UpdateLoanApplicationRequest,
    ListClientLoanApplicationsRequest,
    LoanApplicationResponse,
    LoanApplicationListResponse,
    LoanApplicationStatsResponse
)


class LoanApplicationService:
    """
    Main service for loan application operations
    Coordinates all loan application use cases
    """
    
    def __init__(self, loan_application_repository: LoanApplicationRepositoryPort):
        self._loan_application_repository = loan_application_repository
        
        # Initialize use case services
        self._create_service = CreateLoanApplicationService(loan_application_repository)
        self._list_client_service = ListClientLoanApplicationsService(loan_application_repository)
    
    # Create operations
    async def create_application(self, request: CreateLoanApplicationRequest) -> LoanApplicationResponse:
        """Create a new loan application"""
        return await self._create_service.execute(request)
    
    # Update operations
    async def update_application(self, application_id: int, request: UpdateLoanApplicationRequest) -> LoanApplicationResponse:
        """Update loan application"""
        try:
            # Get existing application
            application = await self._loan_application_repository.get_by_id(application_id)
            if not application:
                raise Exception(f"Solicitud con ID {application_id} no encontrada")
            
            # Update fields if provided
            if request.name is not None:
                application.name = request.name
            if request.convenio is not None:
                application.convenio = request.convenio
            if request.telefono is not None:
                application.telefono = request.telefono
            if request.fecha_nacimiento is not None:
                application.fecha_nacimiento = request.fecha_nacimiento
            
            # Save updated application
            updated_application = await self._loan_application_repository.update(application)
            
            return LoanApplicationResponse(
                id=updated_application.id,
                name=updated_application.name,
                cedula=updated_application.cedula,
                convenio=updated_application.convenio,
                telefono=updated_application.telefono,
                fecha_nacimiento=updated_application.fecha_nacimiento,
                created_at=updated_application.created_at
            )
            
        except Exception as e:
            raise Exception(f"Error al actualizar solicitud: {str(e)}")
    
    # Query operations
    async def get_application_by_id(self, application_id: int) -> Optional[LoanApplicationResponse]:
        """Get a specific loan application by ID"""
        application = await self._loan_application_repository.get_by_id(application_id)
        if not application:
            return None
        
        return LoanApplicationResponse(
            id=application.id,
            name=application.name,
            cedula=application.cedula,
            convenio=application.convenio,
            telefono=application.telefono,
            fecha_nacimiento=application.fecha_nacimiento,
            created_at=application.created_at
        )
    
    async def list_client_applications(self, request: ListClientLoanApplicationsRequest) -> LoanApplicationListResponse:
        """List loan applications for a specific client"""
        return await self._list_client_service.execute(request)
    
    async def get_client_application_summary(self, cedula: str) -> dict:
        """Get summary of client's loan applications"""
        return await self._list_client_service.get_client_application_summary(cedula)
    

    
    # Admin operations
    async def list_all_applications(self, convenio_filter: Optional[str] = None, 
                                  skip: int = 0, limit: int = 20) -> LoanApplicationListResponse:
        """List all applications with optional convenio filter"""
        try:
            if convenio_filter:
                applications = await self._loan_application_repository.get_by_convenio(
                    convenio_filter, skip, limit
                )
                total = await self._loan_application_repository.count_by_convenio(convenio_filter)
            else:
                applications = await self._loan_application_repository.get_all(skip, limit)
                total = await self._loan_application_repository.count_total()
            
            # Convert to response DTOs
            application_responses = []
            for app in applications:
                application_responses.append(
                    LoanApplicationResponse(
                        id=app.id,
                        name=app.name,
                        cedula=app.cedula,
                        convenio=app.convenio,
                        telefono=app.telefono,
                        fecha_nacimiento=app.fecha_nacimiento,
                        created_at=app.created_at
                    )
                )
            
            # Calculate pagination
            import math
            page = (skip // limit) + 1
            total_pages = math.ceil(total / limit) if total > 0 else 1
            
            return LoanApplicationListResponse(
                applications=application_responses,
                total=total,
                page=page,
                page_size=limit,
                total_pages=total_pages
            )
            
        except Exception as e:
            raise Exception(f"Error al listar solicitudes: {str(e)}")
    
    async def get_application_statistics(self) -> LoanApplicationStatsResponse:
        """Get application statistics"""
        try:
            stats = await self._loan_application_repository.get_statistics()
            
            return LoanApplicationStatsResponse(
                total_applications=stats.get('total', 0),
                applications_by_convenio=stats.get('by_convenio', {}),
                applications_by_month=stats.get('by_month', {})
            )
            
        except Exception as e:
            raise Exception(f"Error al obtener estadísticas: {str(e)}")
    
    async def search_applications_by_name(self, name: str, skip: int = 0, 
                                        limit: int = 20) -> LoanApplicationListResponse:
        """Search applications by applicant name"""
        try:
            applications = await self._loan_application_repository.search_by_name(name, skip, limit)
            
            # For simplicity, we'll count all matching results
            # In a real implementation, you might want a separate count method
            all_matching = await self._loan_application_repository.search_by_name(name, 0, 1000)
            total = len(all_matching)
            
            # Convert to response DTOs
            application_responses = []
            for app in applications:
                application_responses.append(
                    LoanApplicationResponse(
                        id=app.id,
                        name=app.name,
                        cedula=app.cedula,
                        convenio=app.convenio,
                        telefono=app.telefono,
                        fecha_nacimiento=app.fecha_nacimiento,
                        created_at=app.created_at
                    )
                )
            
            # Calculate pagination
            import math
            page = (skip // limit) + 1
            total_pages = math.ceil(total / limit) if total > 0 else 1
            
            return LoanApplicationListResponse(
                applications=application_responses,
                total=total,
                page=page,
                page_size=limit,
                total_pages=total_pages
            )
            
        except Exception as e:
            raise Exception(f"Error al buscar solicitudes: {str(e)}")