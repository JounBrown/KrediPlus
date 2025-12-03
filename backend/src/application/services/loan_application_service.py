from typing import List, Optional
from src.domain.ports.loan_application_repository import LoanApplicationRepositoryPort
from src.application.services.create_loan_application_service import CreateLoanApplicationService
from src.application.services.update_loan_application_status_service import UpdateLoanApplicationStatusService
from src.application.services.list_client_loan_applications_service import ListClientLoanApplicationsService
from src.application.dtos.loan_application_dtos import (
    CreateLoanApplicationRequest,
    UpdateLoanApplicationStatusRequest,
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
        self._update_status_service = UpdateLoanApplicationStatusService(loan_application_repository)
        self._list_client_service = ListClientLoanApplicationsService(loan_application_repository)
    
    # Create operations
    async def create_application(self, request: CreateLoanApplicationRequest) -> LoanApplicationResponse:
        """Create a new loan application"""
        return await self._create_service.execute(request)
    
    # Status update operations
    async def update_application_status(self, request: UpdateLoanApplicationStatusRequest) -> LoanApplicationResponse:
        """Update loan application status"""
        return await self._update_status_service.execute(request)
    
    async def approve_application(self, application_id: int) -> LoanApplicationResponse:
        """Approve a loan application"""
        return await self._update_status_service.approve_application(application_id)
    
    async def reject_application(self, application_id: int, notes: Optional[str] = None) -> LoanApplicationResponse:
        """Reject a loan application"""
        return await self._update_status_service.reject_application(application_id, notes)
    
    async def cancel_application(self, application_id: int, notes: Optional[str] = None) -> LoanApplicationResponse:
        """Cancel a loan application"""
        return await self._update_status_service.cancel_application(application_id, notes)
    
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
            monto_solicitado=application.monto_solicitado,
            plazo=application.plazo,
            estado=application.estado,
            created_at=application.created_at
        )
    
    async def list_client_applications(self, request: ListClientLoanApplicationsRequest) -> LoanApplicationListResponse:
        """List loan applications for a specific client"""
        return await self._list_client_service.execute(request)
    
    async def get_client_application_summary(self, cedula: str) -> dict:
        """Get summary of client's loan applications"""
        return await self._list_client_service.get_client_application_summary(cedula)
    
    async def get_pending_applications_for_client(self, cedula: str) -> List[LoanApplicationResponse]:
        """Get pending applications for a client"""
        return await self._list_client_service.get_pending_applications_for_client(cedula)
    
    # Admin operations
    async def list_all_applications(self, status_filter: Optional[str] = None, 
                                  skip: int = 0, limit: int = 20) -> LoanApplicationListResponse:
        """List all applications with optional status filter"""
        try:
            if status_filter:
                applications = await self._loan_application_repository.get_by_status(
                    status_filter, skip, limit
                )
                total = await self._loan_application_repository.count_by_status(status_filter)
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
                        monto_solicitado=app.monto_solicitado,
                        plazo=app.plazo,
                        estado=app.estado,
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
                nueva=stats.get('nueva', 0),
                en_proceso=stats.get('en_proceso', 0),
                aprobada=stats.get('aprobada', 0),
                rechazada=stats.get('rechazada', 0),
                cancelada=stats.get('cancelada', 0),
                total_amount_requested=stats.get('total_amount', 0.0),
                average_amount=stats.get('average_amount', 0.0),
                average_term=stats.get('average_term', 0.0)
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
                        monto_solicitado=app.monto_solicitado,
                        plazo=app.plazo,
                        estado=app.estado,
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