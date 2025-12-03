from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession

from src.application.services.loan_application_service import LoanApplicationService
from src.application.dtos.loan_application_dtos import (
    CreateLoanApplicationRequest,
    UpdateLoanApplicationStatusRequest,
    ListClientLoanApplicationsRequest,
    LoanApplicationResponse,
    LoanApplicationListResponse,
    LoanApplicationStatsResponse
)
from src.infrastructure.adapters.database.connection import get_db_session
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
    - **monto_solicitado**: Requested amount (100,000 - 50,000,000)
    - **plazo**: Term in months (6, 12, 18, 24, 36, 48, 60, 72)
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
    service: LoanApplicationService = Depends(get_loan_application_service)
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


@router.get("/", response_model=LoanApplicationListResponse)
async def list_loan_applications(
    status_filter: Optional[str] = Query(None, description="Filter by status"),
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(20, ge=1, le=100, description="Number of records to return"),
    service: LoanApplicationService = Depends(get_loan_application_service)
):
    """
    List all loan applications with optional filtering
    
    - **status_filter**: Filter by status (nueva, en_proceso, aprobada, rechazada, cancelada)
    - **skip**: Number of records to skip for pagination
    - **limit**: Number of records to return (max 100)
    """
    try:
        return await service.list_all_applications(status_filter, skip, limit)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error listing applications: {str(e)}")


@router.get("/by_cedula/{cedula}", response_model=LoanApplicationListResponse)
async def get_applications_by_cedula(
    cedula: str,
    status_filter: Optional[str] = Query(None, description="Filter by status"),
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(20, ge=1, le=100, description="Number of records to return"),
    service: LoanApplicationService = Depends(get_loan_application_service)
):
    """
    Get loan applications for a specific client by cedula
    
    - **cedula**: Client's ID number
    - **status_filter**: Optional status filter
    - **skip**: Number of records to skip for pagination
    - **limit**: Number of records to return (max 100)
    """
    try:
        request = ListClientLoanApplicationsRequest(
            cedula=cedula,
            status_filter=status_filter,
            skip=skip,
            limit=limit
        )
        return await service.list_client_applications(request)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting applications by cedula: {str(e)}")


@router.get("/by_cedula/{cedula}/summary")
async def get_client_application_summary(
    cedula: str,
    service: LoanApplicationService = Depends(get_loan_application_service)
):
    """
    Get summary of client's loan applications
    
    Returns statistics about the client's applications including:
    - Total number of applications
    - Whether they have pending applications
    - Whether they have approved applications
    - Latest application status
    - Total amount requested
    """
    try:
        return await service.get_client_application_summary(cedula)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting application summary: {str(e)}")


@router.get("/by_cedula/{cedula}/pending", response_model=list[LoanApplicationResponse])
async def get_pending_applications_by_cedula(
    cedula: str,
    service: LoanApplicationService = Depends(get_loan_application_service)
):
    """Get only pending applications (nueva, en_proceso) for a specific client"""
    try:
        return await service.get_pending_applications_for_client(cedula)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting pending applications: {str(e)}")


@router.put("/{application_id}/status", response_model=LoanApplicationResponse)
async def update_application_status(
    application_id: int,
    request: UpdateLoanApplicationStatusRequest,
    service: LoanApplicationService = Depends(get_loan_application_service)
):
    """
    Update loan application status
    
    - **new_status**: New status (nueva, en_proceso, aprobada, rechazada, cancelada)
    - **notes**: Optional notes about the status change
    """
    try:
        # Ensure the application_id matches
        request.application_id = application_id
        return await service.update_application_status(request)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error updating application status: {str(e)}")


@router.put("/{application_id}/approve", response_model=LoanApplicationResponse)
async def approve_application(
    application_id: int,
    service: LoanApplicationService = Depends(get_loan_application_service)
):
    """Approve a loan application"""
    try:
        return await service.approve_application(application_id)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error approving application: {str(e)}")


@router.put("/{application_id}/reject", response_model=LoanApplicationResponse)
async def reject_application(
    application_id: int,
    notes: Optional[str] = Query(None, description="Rejection notes"),
    service: LoanApplicationService = Depends(get_loan_application_service)
):
    """Reject a loan application"""
    try:
        return await service.reject_application(application_id, notes)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error rejecting application: {str(e)}")


@router.put("/{application_id}/cancel", response_model=LoanApplicationResponse)
async def cancel_application(
    application_id: int,
    notes: Optional[str] = Query(None, description="Cancellation notes"),
    service: LoanApplicationService = Depends(get_loan_application_service)
):
    """Cancel a loan application"""
    try:
        return await service.cancel_application(application_id, notes)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error cancelling application: {str(e)}")


@router.get("/search/by_name", response_model=LoanApplicationListResponse)
async def search_applications_by_name(
    name: str = Query(..., description="Name to search for"),
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(20, ge=1, le=100, description="Number of records to return"),
    service: LoanApplicationService = Depends(get_loan_application_service)
):
    """
    Search loan applications by applicant name
    
    - **name**: Name to search for (partial matches allowed)
    - **skip**: Number of records to skip for pagination
    - **limit**: Number of records to return (max 100)
    """
    try:
        return await service.search_applications_by_name(name, skip, limit)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error searching applications: {str(e)}")


@router.get("/statistics/summary", response_model=LoanApplicationStatsResponse)
async def get_application_statistics(
    service: LoanApplicationService = Depends(get_loan_application_service)
):
    """
    Get application statistics
    
    Returns comprehensive statistics including:
    - Total applications by status
    - Total amount requested
    - Average amount and term
    """
    try:
        return await service.get_application_statistics()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting statistics: {str(e)}")


@router.delete("/{application_id}")
async def delete_application(
    application_id: int,
    service: LoanApplicationService = Depends(get_loan_application_service)
):
    """
    Delete a loan application
    
    **Warning**: This permanently deletes the application from the database.
    Consider using status updates instead for audit trail.
    """
    try:
        # Get the repository directly for delete operation
        db_session = next(get_db_session())
        repository = SupabaseLoanApplicationRepository(db_session)
        
        success = await repository.delete(application_id)
        if not success:
            raise HTTPException(status_code=404, detail="Application not found")
        
        return {"message": "Application deleted successfully"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error deleting application: {str(e)}")