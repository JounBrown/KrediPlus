from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession

from src.api.middleware.auth_middleware import get_current_user
from src.application.services.loan_application_service import LoanApplicationService
from src.application.dtos.loan_application_dtos import (
    CreateLoanApplicationRequest,
    UpdateLoanApplicationRequest,
    ListClientLoanApplicationsRequest,
    LoanApplicationResponse,
    LoanApplicationListResponse,
    LoanApplicationStatsResponse
)
from src.infrastructure.adapters.database.connection import get_db_session
from src.domain.entities.user import User
from src.infrastructure.adapters.database.loan_application_repository import SupabaseLoanApplicationRepository

router = APIRouter(prefix="/loan_applications", tags=["Loan Applications"])


def get_loan_application_service(db: AsyncSession = Depends(get_db_session)) -> LoanApplicationService:
    """Dependency to get LoanApplicationService"""
    repository = SupabaseLoanApplicationRepository(db)
    return LoanApplicationService(repository)


@router.post("/", response_model=LoanApplicationResponse)
async def create_loan_application(
    request: CreateLoanApplicationRequest,
    service: LoanApplicationService = Depends(get_loan_application_service)
):
    """
    Create a new loan application
    
    - **name**: Full name of the applicant
    - **cedula**: ID number (8-11 digits)
    - **convenio**: Optional agreement/convention
    - **telefono**: Phone number
    - **fecha_nacimiento**: Birth date (must be 18+ years old)
    """
    try:
        return await service.create_application(request)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error creating application: {str(e)}")


@router.get("/{application_id}", response_model=LoanApplicationResponse)
async def get_loan_application(
    application_id: int,
    service: LoanApplicationService = Depends(get_loan_application_service),
    _: User = Depends(get_current_user)
):
    """Get a specific loan application by ID"""
    try:
        application = await service.get_application_by_id(application_id)
        if not application:
            raise HTTPException(status_code=404, detail="Application not found")
        return application
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting application: {str(e)}")


@router.get("/", response_model=list[LoanApplicationResponse])
async def list_loan_applications(
    service: LoanApplicationService = Depends(get_loan_application_service),
    _: User = Depends(get_current_user)
):
    """
    List all loan applications
    """
    try:
        result = await service.list_all_applications(convenio_filter=None, skip=0, limit=1000)
        return result.applications  # Solo devolver la lista, sin metadatos
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error listing applications: {str(e)}")


@router.get("/by_cedula/{cedula}", response_model=list[LoanApplicationResponse])
async def get_applications_by_cedula(
    cedula: str,
    service: LoanApplicationService = Depends(get_loan_application_service),
    _: User = Depends(get_current_user)
):
    """
    Get loan applications for a specific client by cedula
    
    - **cedula**: Client's ID number
    """
    try:
        request = ListClientLoanApplicationsRequest(
            cedula=cedula,
            skip=0,
            limit=100
        )
        result = await service.list_client_applications(request)
        return result.applications  # Solo devolver la lista, sin metadatos
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting applications by cedula: {str(e)}")





@router.put("/{application_id}", response_model=LoanApplicationResponse)
async def update_application(
    application_id: int,
    request: UpdateLoanApplicationRequest,
    service: LoanApplicationService = Depends(get_loan_application_service),
    _: User = Depends(get_current_user)
):
    """
    Update loan application
    
    - **name**: Full name of the applicant
    - **convenio**: Optional agreement/convention
    - **telefono**: Phone number
    - **fecha_nacimiento**: Birth date (must be 18+ years old)
    """
    try:
        return await service.update_application(application_id, request)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error updating application: {str(e)}")







@router.delete("/{application_id}")
async def delete_application(
    application_id: int,
    db: AsyncSession = Depends(get_db_session),
    _: User = Depends(get_current_user)
):
    """
    Delete a loan application
    
    **Warning**: This permanently deletes the application from the database.
    Consider using status updates instead for audit trail.
    """
    try:
        # Get the repository directly for delete operation
        repository = SupabaseLoanApplicationRepository(db)
        
        success = await repository.delete(application_id)
        if not success:
            raise HTTPException(status_code=404, detail="Application not found")
        
        return {"message": "Application deleted successfully"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error deleting application: {str(e)}")