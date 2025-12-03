from datetime import datetime
from typing import Optional
from src.domain.entities.loan_application import LoanApplication
from src.domain.ports.loan_application_repository import LoanApplicationRepositoryPort
from src.application.dtos.loan_application_dtos import (
    CreateLoanApplicationRequest, 
    LoanApplicationResponse
)


class CreateLoanApplicationService:
    """Service for creating new loan applications"""
    
    def __init__(self, loan_application_repository: LoanApplicationRepositoryPort):
        self._loan_application_repository = loan_application_repository
    
    async def execute(self, request: CreateLoanApplicationRequest) -> LoanApplicationResponse:
        """
        Create a new loan application
        
        Args:
            request: CreateLoanApplicationRequest with application data
            
        Returns:
            LoanApplicationResponse with created application data
            
        Raises:
            ValueError: If validation fails
            Exception: If creation fails
        """
        
        # Create domain entity
        loan_application = LoanApplication(
            id=None,
            name=request.name.strip(),
            cedula=request.cedula.strip(),
            convenio=request.convenio.strip() if request.convenio else None,
            telefono=request.telefono.strip(),
            fecha_nacimiento=request.fecha_nacimiento,
            monto_solicitado=request.monto_solicitado,
            plazo=request.plazo,
            estado="nueva",  # Default status
            created_at=datetime.now()
        )
        
        # Validate business rules
        if not loan_application.validate_application_data():
            raise ValueError("Los datos de la solicitud no son válidos")
        
        # Check if there's already a pending application for this cedula
        existing_applications = await self._loan_application_repository.get_by_cedula(
            loan_application.cedula
        )
        
        # Check for pending applications (nueva or en_proceso)
        pending_applications = [
            app for app in existing_applications 
            if app.estado in ["nueva", "en_proceso"]
        ]
        
        if pending_applications:
            raise ValueError(
                "Ya existe una solicitud pendiente para esta cédula. "
                "Complete el proceso actual antes de crear una nueva solicitud."
            )
        
        # Save to repository
        try:
            created_application = await self._loan_application_repository.create(loan_application)
            
            # Calculate estimated monthly payment for response
            estimated_payment = self._calculate_estimated_payment(
                created_application.monto_solicitado,
                created_application.plazo
            )
            
            # Convert to response DTO
            return LoanApplicationResponse(
                id=created_application.id,
                name=created_application.name,
                cedula=created_application.cedula,
                convenio=created_application.convenio,
                telefono=created_application.telefono,
                fecha_nacimiento=created_application.fecha_nacimiento,
                monto_solicitado=created_application.monto_solicitado,
                plazo=created_application.plazo,
                estado=created_application.estado,
                created_at=created_application.created_at,
                estimated_monthly_payment=estimated_payment
            )
            
        except Exception as e:
            raise Exception(f"Error al crear la solicitud: {str(e)}")
    
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