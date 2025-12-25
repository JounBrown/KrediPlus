from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession

from src.infrastructure.inbound.api.middleware.auth_middleware import get_current_user
from src.application.services.credit_service import CreditService
from src.application.dtos.credit_dtos import (
    CreateCreditRequest,
    UpdateCreditRequest,
    CreditResponse
)
from src.infrastructure.outbound.database.connection import get_db_session
from src.infrastructure.outbound.database.credit_repository import SupabaseCreditRepository

router = APIRouter(
    prefix="/credits",
    tags=["Credits"],
    dependencies=[Depends(get_current_user)]
)


def get_credit_service(db: AsyncSession = Depends(get_db_session)) -> CreditService:
    """Dependency to get CreditService"""
    repository = SupabaseCreditRepository(db)
    return CreditService(repository)


@router.post("/", response_model=CreditResponse)
async def create_credit(
    request: CreateCreditRequest,
    service: CreditService = Depends(get_credit_service)
):
    """
    Create a new credit
    
    - **client_id**: ID of the client
    - **monto_aprobado**: Approved amount (Decimal: 100,000 - 100,000,000)
    - **plazo_meses**: Term in months (1-120)
    - **tasa_interes**: Interest rate percentage (Decimal: 0-100)
    - **fecha_desembolso**: Optional disbursement date
    
    **Default status**: EN_ESTUDIO
    """
    try:
        return await service.create_credit(request)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error creating credit: {str(e)}")


@router.get("/{credit_id}", response_model=CreditResponse)
async def get_credit(
    credit_id: int,
    service: CreditService = Depends(get_credit_service)
):
    """Get a specific credit by ID"""
    try:
        credit = await service.get_credit_by_id(credit_id)
        if not credit:
            raise HTTPException(status_code=404, detail="Credit not found")
        return credit
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting credit: {str(e)}")


@router.get("/", response_model=list[CreditResponse])
async def list_credits(
    db: AsyncSession = Depends(get_db_session)
):
    """List all credits"""
    try:
        # Usar directamente el repositorio sin límites
        from src.infrastructure.outbound.database.models import CreditModel
        from sqlalchemy import select
        
        stmt = select(CreditModel).order_by(CreditModel.created_at.desc())
        result = await db.execute(stmt)
        models = result.scalars().all()
        
        # Convertir a DTOs
        repository = SupabaseCreditRepository(db)
        credits = [repository._model_to_entity(model) for model in models]
        
        credit_responses = []
        for credit in credits:
            credit_responses.append(
                CreditResponse(
                    id=credit.id,
                    client_id=credit.client_id,
                    monto_aprobado=credit.monto_aprobado,
                    plazo_meses=credit.plazo_meses,
                    tasa_interes=credit.tasa_interes,
                    estado=credit.estado,
                    fecha_desembolso=credit.fecha_desembolso,
                    created_at=credit.created_at
                )
            )
        
        return credit_responses
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error listing credits: {str(e)}")


@router.get("/by_client/{client_id}", response_model=list[CreditResponse])
async def get_credits_by_client(
    client_id: int,
    service: CreditService = Depends(get_credit_service)
):
    """
    Get all credits for a specific client
    
    - **client_id**: Client's ID number
    """
    try:
        return await service.get_credits_by_client(client_id)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting credits by client: {str(e)}")


@router.put("/{credit_id}", response_model=CreditResponse)
async def update_credit(
    credit_id: int,
    request: UpdateCreditRequest,
    service: CreditService = Depends(get_credit_service)
):
    """
    Update credit information
    
    - **monto_aprobado**: Approved amount (Decimal)
    - **plazo_meses**: Term in months
    - **tasa_interes**: Interest rate percentage (Decimal)
    - **estado**: Credit status (EN_ESTUDIO, APROBADO, RECHAZADO, DESEMBOLSADO, AL_DIA, EN_MORA, PAGADO)
    - **fecha_desembolso**: Disbursement date
    """
    try:
        return await service.update_credit(credit_id, request)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error updating credit: {str(e)}")


@router.delete("/{credit_id}")
async def delete_credit(
    credit_id: int,
    service: CreditService = Depends(get_credit_service)
):
    """
    Delete a credit
    
    **Warning**: This permanently deletes the credit from the database.
    """
    try:
        success = await service.delete_credit(credit_id)
        if not success:
            raise HTTPException(status_code=404, detail="Credit not found")
        
        return {"message": "Credit deleted successfully"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error deleting credit: {str(e)}")


@router.delete("/{credit_id}/documents/{document_id}")
async def delete_credit_document(
    credit_id: int,
    document_id: int,
    db: AsyncSession = Depends(get_db_session)
):
    """
    Delete a document that belongs to a specific credit
    
    - **credit_id:** ID of the credit
    - **document_id:** ID of the document to delete
    
    **Validation:**
    - Verifies that the document belongs to the specified credit
    - Returns 404 if document doesn't exist or doesn't belong to credit
    """
    try:
        from src.application.services.client_document_service import ClientDocumentService
        from src.infrastructure.outbound.database.client_document_repository import SupabaseClientDocumentRepository
        from src.infrastructure.outbound.supabase_storage_service import SupabaseStorageService
        
        # Create document service
        document_repository = SupabaseClientDocumentRepository(db)
        storage_service = SupabaseStorageService()
        document_service = ClientDocumentService(document_repository, storage_service)
        
        # Delete document with credit validation
        return await document_service.delete_credit_document(credit_id, document_id)
        
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))