from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession

from src.application.services.client_service import ClientService
from src.application.dtos.client_dtos import (
    CreateClientRequest,
    UpdateClientRequest,
    ClientResponse,
    ClientListResponse,
    SearchClientsRequest
)
from src.infrastructure.adapters.database.connection import get_db_session
from src.infrastructure.adapters.database.client_repository import SupabaseClientRepository

router = APIRouter(prefix="/clients", tags=["Clients"])


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
        from src.infrastructure.adapters.database.client_repository import SupabaseClientRepository
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
        from src.infrastructure.adapters.database.models import ClientModel
        from src.infrastructure.adapters.database.client_repository import SupabaseClientRepository
        
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
    # TODO: Add authentication dependency here
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
        from src.infrastructure.adapters.database.client_document_repository import SupabaseClientDocumentRepository
        
        # Create document service
        document_repository = SupabaseClientDocumentRepository(db)
        document_service = ClientDocumentService(document_repository)
        
        # Delete document with client validation
        return await document_service.delete_client_document(client_id, document_id)
        
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


