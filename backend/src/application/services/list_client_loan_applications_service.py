import math
from typing import List, Optional
from src.domain.entities.loan_application import LoanApplication
from src.domain.ports.loan_application_repository import LoanApplicationRepositoryPort
from src.application.dtos.loan_application_dtos import (
    ListClientLoanApplicationsRequest,
    LoanApplicationResponse,
    LoanApplicationListResponse
)


class ListClientLoanApplicationsService:
    """Service for listing client loan applications"""
    
    def __init__(self, loan_application_repository: LoanApplicationRepositoryPort):
        self._loan_application_repository = loan_application_repository
    
    async def execute(self, request: ListClientLoanApplicationsRequest) -> LoanApplicationListResponse:
        """
        List loan applications for a specific client
        
        Args:
            request: ListClientLoanApplicationsRequest with search criteria
            
        Returns:
            LoanApplicationListResponse with paginated results
            
        Raises:
            ValueError: If validation fails
            Exception: If query fails
        """
        
        try:
            # Get applications by cedula
            all_applications = await self._loan_application_repository.get_by_cedula(request.cedula)
            
            # Sort by creation date (newest first)
            all_applications.sort(key=lambda x: x.created_at, reverse=True)
            
            # Apply pagination
            total = len(all_applications)
            start_index = request.skip
            end_index = start_index + request.limit
            paginated_applications = all_applications[start_index:end_index]
            
            # Convert to response DTOs
            application_responses = []
            for app in paginated_applications:
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
            
            # Calculate pagination info
            page = (request.skip // request.limit) + 1
            total_pages = math.ceil(total / request.limit) if total > 0 else 1
            
            return LoanApplicationListResponse(
                applications=application_responses,
                total=total,
                page=page,
                page_size=request.limit,
                total_pages=total_pages
            )
            
        except Exception as e:
            raise Exception(f"Error al consultar las solicitudes: {str(e)}")
    
    async def get_client_application_summary(self, cedula: str) -> dict:
        """
        Get summary of client's loan applications
        
        Args:
            cedula: Client's cedula
            
        Returns:
            Dictionary with application summary
        """
        
        try:
            applications = await self._loan_application_repository.get_by_cedula(cedula)
            
            if not applications:
                return {
                    "total_applications": 0,
                    "has_pending": False,
                    "has_approved": False,
                    "latest_status": None,
                    "total_requested": 0.0
                }
            
            # Calculate summary statistics
            total_applications = len(applications)
            
            # Get latest application
            latest_application = max(applications, key=lambda x: x.created_at)
            
            return {
                "total_applications": total_applications,
                "latest_application_date": latest_application.created_at,
                "applications_by_convenio": {}
            }
            
        except Exception as e:
            raise Exception(f"Error al obtener resumen de solicitudes: {str(e)}")
    
