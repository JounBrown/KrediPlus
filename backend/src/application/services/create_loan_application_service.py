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
            created_at=datetime.now()
        )
        
        # Validate business rules
        if not loan_application.validate_application_data():
            raise ValueError("Los datos de la solicitud no son válidos")
        
        # Check if there's already an application for this cedula (optional business rule)
        existing_applications = await self._loan_application_repository.get_by_cedula(
            loan_application.cedula
        )
        
        if existing_applications:
            # You can implement business rules here if needed
            # For now, we'll allow multiple applications per cedula
            pass
        
        # Save to repository
        try:
            created_application = await self._loan_application_repository.create(loan_application)
            
            # Convert to response DTO
            return LoanApplicationResponse(
                id=created_application.id,
                name=created_application.name,
                cedula=created_application.cedula,
                convenio=created_application.convenio,
                telefono=created_application.telefono,
                fecha_nacimiento=created_application.fecha_nacimiento,
                created_at=created_application.created_at
            )
            
        except Exception as e:
            raise Exception(f"Error al crear la solicitud: {str(e)}")
    
