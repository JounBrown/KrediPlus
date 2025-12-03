from typing import Optional
from src.domain.entities.loan_application import LoanApplication, ApplicationStatus
from src.domain.ports.loan_application_repository import LoanApplicationRepositoryPort
from src.application.dtos.loan_application_dtos import (
    UpdateLoanApplicationStatusRequest,
    LoanApplicationResponse
)


class UpdateLoanApplicationStatusService:
    """Service for updating loan application status"""
    
    def __init__(self, loan_application_repository: LoanApplicationRepositoryPort):
        self._loan_application_repository = loan_application_repository
    
    async def execute(self, request: UpdateLoanApplicationStatusRequest) -> LoanApplicationResponse:
        """
        Update loan application status
        
        Args:
            request: UpdateLoanApplicationStatusRequest with status update data
            
        Returns:
            LoanApplicationResponse with updated application data
            
        Raises:
            ValueError: If validation fails or application not found
            Exception: If update fails
        """
        
        # Get existing application
        application = await self._loan_application_repository.get_by_id(request.application_id)
        if not application:
            raise ValueError(f"Solicitud con ID {request.application_id} no encontrada")
        
        # Validate status transition
        if not self._is_valid_status_transition(application.estado, request.new_status):
            raise ValueError(
                f"Transición de estado inválida: de '{application.estado}' a '{request.new_status}'"
            )
        
        # Update status using domain method
        if not application.update_status(request.new_status):
            raise ValueError(f"No se pudo actualizar el estado a '{request.new_status}'")
        
        # Save updated application
        try:
            updated_application = await self._loan_application_repository.update(application)
            
            # Convert to response DTO
            return LoanApplicationResponse(
                id=updated_application.id,
                name=updated_application.name,
                cedula=updated_application.cedula,
                convenio=updated_application.convenio,
                telefono=updated_application.telefono,
                fecha_nacimiento=updated_application.fecha_nacimiento,
                monto_solicitado=updated_application.monto_solicitado,
                plazo=updated_application.plazo,
                estado=updated_application.estado,
                created_at=updated_application.created_at
            )
            
        except Exception as e:
            raise Exception(f"Error al actualizar el estado de la solicitud: {str(e)}")
    
    def _is_valid_status_transition(self, current_status: str, new_status: str) -> bool:
        """
        Validate if status transition is allowed
        
        Args:
            current_status: Current application status
            new_status: Requested new status
            
        Returns:
            True if transition is valid, False otherwise
        """
        
        # Define valid transitions
        valid_transitions = {
            ApplicationStatus.NUEVA.value: [
                ApplicationStatus.EN_PROCESO.value,
                ApplicationStatus.APROBADA.value,
                ApplicationStatus.RECHAZADA.value,
                ApplicationStatus.CANCELADA.value
            ],
            ApplicationStatus.EN_PROCESO.value: [
                ApplicationStatus.APROBADA.value,
                ApplicationStatus.RECHAZADA.value,
                ApplicationStatus.CANCELADA.value,
                ApplicationStatus.NUEVA.value  # Allow going back to nueva for corrections
            ],
            ApplicationStatus.APROBADA.value: [
                ApplicationStatus.CANCELADA.value  # Only allow cancellation of approved applications
            ],
            ApplicationStatus.RECHAZADA.value: [
                ApplicationStatus.NUEVA.value,  # Allow reprocessing rejected applications
                ApplicationStatus.CANCELADA.value
            ],
            ApplicationStatus.CANCELADA.value: []  # No transitions from cancelled
        }
        
        # Check if transition is valid
        allowed_transitions = valid_transitions.get(current_status, [])
        return new_status in allowed_transitions
    
    async def approve_application(self, application_id: int) -> LoanApplicationResponse:
        """
        Convenience method to approve an application
        
        Args:
            application_id: ID of the application to approve
            
        Returns:
            LoanApplicationResponse with approved application data
        """
        request = UpdateLoanApplicationStatusRequest(
            application_id=application_id,
            new_status=ApplicationStatus.APROBADA.value
        )
        return await self.execute(request)
    
    async def reject_application(self, application_id: int, notes: Optional[str] = None) -> LoanApplicationResponse:
        """
        Convenience method to reject an application
        
        Args:
            application_id: ID of the application to reject
            notes: Optional rejection notes
            
        Returns:
            LoanApplicationResponse with rejected application data
        """
        request = UpdateLoanApplicationStatusRequest(
            application_id=application_id,
            new_status=ApplicationStatus.RECHAZADA.value,
            notes=notes
        )
        return await self.execute(request)
    
    async def cancel_application(self, application_id: int, notes: Optional[str] = None) -> LoanApplicationResponse:
        """
        Convenience method to cancel an application
        
        Args:
            application_id: ID of the application to cancel
            notes: Optional cancellation notes
            
        Returns:
            LoanApplicationResponse with cancelled application data
        """
        request = UpdateLoanApplicationStatusRequest(
            application_id=application_id,
            new_status=ApplicationStatus.CANCELADA.value,
            notes=notes
        )
        return await self.execute(request)