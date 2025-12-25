from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query, Request
from sqlalchemy.ext.asyncio import AsyncSession

from src.application.services.client_service import ClientService
from src.application.dtos.client_dtos import (
    CreateClientRequest,
    UpdateClientRequest,
    ClientResponse,
    ClientListResponse,
    SearchClientsRequest
)
from src.application.dtos.credit_dtos import CreateCreditForClientRequest, CreditResponse, UpdateCreditRequest
from src.infrastructure.inbound.api.middleware.auth_middleware import get_current_user
from src.infrastructure.outbound.database.connection import get_db_session
from src.infrastructure.outbound.database.client_repository import SupabaseClientRepository

router = APIRouter(
    prefix="/clients",
    tags=["Clients"],
    dependencies=[Depends(get_current_user)]
)


def get_client_service(db: AsyncSession = Depends(get_db_session)) -> ClientService:
    """Dependency to get ClientService"""
    repository = SupabaseClientRepository(db)
    return ClientService(repository)


@router.post("/", response_model=ClientResponse)
async def create_client(
    request: CreateClientRequest,
    service: ClientService = Depends(get_client_service)
):
    """
    Create a new client
    
    - **nombre_completo**: Full name of the client
    - **cedula**: ID number (8-11 digits)
    - **email**: Email address
    - **telefono**: Phone number
    - **fecha_nacimiento**: Birth date
    - **direccion**: Address
    - **info_adicional**: Optional additional information (JSON)
    """
    try:
        return await service.create_client(request)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error creating client: {str(e)}")


@router.get("/{client_id}", response_model=ClientResponse)
async def get_client(
    client_id: int,
    service: ClientService = Depends(get_client_service)
):
    """Get a specific client by ID"""
    try:
        client = await service.get_client_by_id(client_id)
        if not client:
            raise HTTPException(status_code=404, detail="Client not found")
        return client
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting client: {str(e)}")


@router.get("/", response_model=list[ClientResponse])
async def list_clients(
    db: AsyncSession = Depends(get_db_session)
):
    """List all clients"""
    try:
        # Usar directamente el repositorio sin límites
        from src.infrastructure.outbound.database.client_repository import SupabaseClientRepository
        repository = SupabaseClientRepository(db)
        
        # Obtener todos los clientes sin límite
        clients = await repository.get_all(skip=0, limit=10000)  # Límite muy alto
        
        # Convertir a DTOs
        client_responses = []
        for client in clients:
            client_responses.append(
                ClientResponse(
                    id=client.id,
                    nombre_completo=client.nombre_completo,
                    cedula=client.cedula,
                    email=client.email,
                    telefono=client.telefono,
                    fecha_nacimiento=client.fecha_nacimiento,
                    direccion=client.direccion,
                    info_adicional=client.info_adicional,
                    created_at=client.created_at
                )
            )
        
        return client_responses
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error listing clients: {str(e)}")


@router.get("/by_cedula/{cedula}", response_model=ClientResponse)
async def get_client_by_cedula(
    cedula: str,
    service: ClientService = Depends(get_client_service)
):
    """Get client by cedula (ID number)"""
    try:
        client = await service.get_client_by_cedula(cedula)
        if not client:
            raise HTTPException(status_code=404, detail="Client not found")
        return client
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting client by cedula: {str(e)}")


@router.put("/{client_id}", response_model=ClientResponse)
async def update_client(
    client_id: int,
    request: UpdateClientRequest,
    service: ClientService = Depends(get_client_service)
):
    """
    Update client information
    
    - **nombre_completo**: Full name of the client
    - **email**: Email address
    - **telefono**: Phone number
    - **direccion**: Address
    - **info_adicional**: Optional additional information (JSON)
    """
    try:
        return await service.update_client(client_id, request)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error updating client: {str(e)}")


@router.delete("/{client_id}")
async def delete_client(
    client_id: int,
    service: ClientService = Depends(get_client_service)
):
    """
    Delete a client
    
    **Warning**: This permanently deletes the client from the database.
    """
    try:
        success = await service.delete_client(client_id)
        if not success:
            raise HTTPException(status_code=404, detail="Client not found")
        
        return {"message": "Client deleted successfully"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error deleting client: {str(e)}")


@router.get("/search/by_name", response_model=list[ClientResponse])
async def search_clients_by_name(
    name: str = Query(..., description="Name to search for"),
    db: AsyncSession = Depends(get_db_session)
):
    """
    Search clients by name
    
    - **name**: Name to search for (partial matches allowed)
    """
    try:
        # Buscar por nombre SIN LÍMITE - consulta directa
        from sqlalchemy import select
        from src.infrastructure.outbound.database.models import ClientModel
        from src.infrastructure.outbound.database.client_repository import SupabaseClientRepository
        
        repository = SupabaseClientRepository(db)
        search_pattern = f"%{name}%"
        
        stmt = select(ClientModel).where(
            ClientModel.nombre_completo.ilike(search_pattern)
        ).order_by(ClientModel.created_at.desc())  # SIN .limit() - TODAS las coincidencias
        
        result = await db.execute(stmt)
        models = result.scalars().all()
        
        # Convertir modelos a entidades
        clients = [repository._model_to_entity(model) for model in models]
        
        # Convertir a DTOs
        client_responses = []
        for client in clients:
            client_responses.append(
                ClientResponse(
                    id=client.id,
                    nombre_completo=client.nombre_completo,
                    cedula=client.cedula,
                    email=client.email,
                    telefono=client.telefono,
                    fecha_nacimiento=client.fecha_nacimiento,
                    direccion=client.direccion,
                    info_adicional=client.info_adicional,
                    created_at=client.created_at
                )
            )
        
        return client_responses
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error searching clients: {str(e)}")


@router.delete("/{client_id}/documents/{document_id}")
async def delete_client_document(
    client_id: int,
    document_id: int,
    db: AsyncSession = Depends(get_db_session)
):
    """
    Delete a document that belongs to a specific client
    
    - **client_id:** ID of the client
    - **document_id:** ID of the document to delete
    
    **Validation:**
    - Verifies that the document belongs to the specified client
    - Returns 404 if document doesn't exist or doesn't belong to client
    """
    try:
        from src.application.services.client_document_service import ClientDocumentService
        from src.infrastructure.outbound.database.client_document_repository import SupabaseClientDocumentRepository
        from src.infrastructure.outbound.supabase_storage_service import SupabaseStorageService
        
        # Create document service
        document_repository = SupabaseClientDocumentRepository(db)
        storage_service = SupabaseStorageService()
        document_service = ClientDocumentService(document_repository, storage_service)
        
        # Delete document with client validation
        return await document_service.delete_client_document(client_id, document_id)
        
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/{client_id}/credits", response_model=CreditResponse)
async def create_credit_for_client(
    client_id: int,
    credit_request: CreateCreditForClientRequest,
    db: AsyncSession = Depends(get_db_session)
):
    """
    Create a new credit for a specific client
    
    - **client_id:** ID of the client (from URL path)
    - **monto_aprobado**: Approved amount (Decimal: 100,000 - 100,000,000)
    - **plazo_meses**: Term in months (1-120)
    - **tasa_interes**: Interest rate percentage (Decimal: 0-100)
    - **fecha_desembolso**: Optional disbursement date
    
    **Validation:**
    - Verifies that the client exists before creating the credit
    - Default status: EN_ESTUDIO
    
    **RESTful Design:**
    - This endpoint follows the pattern: POST /clients/{client_id}/credits
    - The client_id is taken from the URL path, not the request body
    """
    try:
        from src.application.services.credit_service import CreditService
        from src.application.dtos.credit_dtos import CreateCreditRequest
        from src.infrastructure.outbound.database.credit_repository import SupabaseCreditRepository
        
        # First verify that client exists
        client_service = get_client_service(db)
        client = await client_service.get_client_by_id(client_id)
        if not client:
            raise HTTPException(status_code=404, detail="Client not found")
        
        # Create credit service
        credit_repository = SupabaseCreditRepository(db)
        credit_service = CreditService(credit_repository)
        
        # Convert to full CreateCreditRequest (adding client_id)
        full_request = CreateCreditRequest(
            client_id=client_id,
            monto_aprobado=credit_request.monto_aprobado,
            plazo_meses=credit_request.plazo_meses,
            tasa_interes=credit_request.tasa_interes,
            fecha_desembolso=credit_request.fecha_desembolso
        )
        
        # Create the credit
        return await credit_service.create_credit(full_request)
        
    except HTTPException:
        raise
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error creating credit for client: {str(e)}")


@router.put("/{client_id}/credits/{credit_id}", response_model=CreditResponse)
async def update_client_credit(
    client_id: int,
    credit_id: int,
    credit_request: UpdateCreditRequest,
    db: AsyncSession = Depends(get_db_session)
):
    """
    Update a credit that belongs to a specific client
    
    - **client_id:** ID of the client (from URL path)
    - **credit_id:** ID of the credit to update (from URL path)
    - **monto_aprobado**: Approved amount (Decimal: 100,000 - 100,000,000)
    - **plazo_meses**: Term in months (1-120)
    - **tasa_interes**: Interest rate percentage (Decimal: 0-100)
    - **estado**: Credit status (EN_ESTUDIO, APROBADO, RECHAZADO, etc.)
    - **fecha_desembolso**: Disbursement date
    
    **Validation:**
    - Verifies that the client exists
    - Verifies that the credit exists and belongs to the specified client
    - All fields are optional (partial updates allowed)
    
    **RESTful Design:**
    - This endpoint follows the pattern: PUT /clients/{client_id}/credits/{credit_id}
    - Both client_id and credit_id are taken from the URL path
    """
    try:
        from src.application.services.credit_service import CreditService
        from src.infrastructure.outbound.database.credit_repository import SupabaseCreditRepository
        
        # First verify that client exists
        client_service = get_client_service(db)
        client = await client_service.get_client_by_id(client_id)
        if not client:
            raise HTTPException(status_code=404, detail="Client not found")
        
        # Create credit service
        credit_repository = SupabaseCreditRepository(db)
        credit_service = CreditService(credit_repository)
        
        # Verify that credit exists and belongs to the client
        existing_credit = await credit_service.get_credit_by_id(credit_id)
        if not existing_credit:
            raise HTTPException(status_code=404, detail="Credit not found")
        
        if existing_credit.client_id != client_id:
            raise HTTPException(
                status_code=404, 
                detail=f"Credit {credit_id} does not belong to client {client_id}"
            )
        
        # Update the credit
        return await credit_service.update_credit(credit_id, credit_request)
        
    except HTTPException:
        raise
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error updating credit for client: {str(e)}")


