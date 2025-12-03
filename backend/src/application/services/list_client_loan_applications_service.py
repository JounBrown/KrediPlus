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
            
            # Filter by status if specified
            if request.status_filter:
                all_applications = [
                    app for app in all_applications 
                    if app.estado == request.status_filter
                ]
            
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
                estimated_payment = self._calculate_estimated_payment(
                    app.monto_solicitado, 
                    app.plazo
                )
                
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
                        created_at=app.created_at,
                        estimated_monthly_payment=estimated_payment
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
            pending_statuses = ["nueva", "en_proceso"]
            has_pending = any(app.estado in pending_statuses for app in applications)
            has_approved = any(app.estado == "aprobada" for app in applications)
            total_requested = sum(app.monto_solicitado for app in applications)
            
            # Get latest application status
            latest_application = max(applications, key=lambda x: x.created_at)
            latest_status = latest_application.estado
            
            return {
                "total_applications": total_applications,
                "has_pending": has_pending,
                "has_approved": has_approved,
                "latest_status": latest_status,
                "total_requested": total_requested,
                "latest_application_date": latest_application.created_at
            }
            
        except Exception as e:
            raise Exception(f"Error al obtener resumen de solicitudes: {str(e)}")
    
    async def get_pending_applications_for_client(self, cedula: str) -> List[LoanApplicationResponse]:
        """
        Get only pending applications for a client
        
        Args:
            cedula: Client's cedula
            
        Returns:
            List of pending LoanApplicationResponse
        """
        
        request = ListClientLoanApplicationsRequest(
            cedula=cedula,
            status_filter="nueva",
            skip=0,
            limit=100
        )
        
        nueva_result = await self.execute(request)
        
        # Also get "en_proceso" applications
        request.status_filter = "en_proceso"
        en_proceso_result = await self.execute(request)
        
        # Combine and sort by creation date
        all_pending = nueva_result.applications + en_proceso_result.applications
        all_pending.sort(key=lambda x: x.created_at, reverse=True)
        
        return all_pending
    
    def _calculate_estimated_payment(self, amount: float, term: int, 
                                   estimated_rate: float = 2.5) -> float:
        """
        Calculate estimated monthly payment using a default interest rate
        
        Args:
            amount: Loan amount
            term: Loan term in months
            estimated_rate: Estimated monthly interest rate (default 2.5%)
            
        Returns:
            Estimated monthly payment
        """
        if estimated_rate <= 0:
            return amount / term
        
        monthly_rate = estimated_rate / 100
        payment = (amount * monthly_rate * (1 + monthly_rate) ** term) / \
                 ((1 + monthly_rate) ** term - 1)
        return round(payment, 2)