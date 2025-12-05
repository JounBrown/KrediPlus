import math
from typing import List, Optional
from src.domain.entities.client import Client
from src.domain.ports.client_repository import ClientRepositoryPort
from src.application.dtos.client_dtos import (
    CreateClientRequest,
    UpdateClientRequest,
    ClientResponse,
    ClientListResponse,
    SearchClientsRequest
)


class ClientService:
    """Service for client operations"""
    
    def __init__(self, client_repository: ClientRepositoryPort):
        self._client_repository = client_repository
    
    async def create_client(self, request: CreateClientRequest) -> ClientResponse:
        """Create a new client"""
        
        # Check if client already exists by cedula
        existing_client = await self._client_repository.get_by_cedula(request.cedula)
        if existing_client:
            raise ValueError(f"Ya existe un cliente con cédula {request.cedula}")
        
        # Check if email is already used
        existing_email = await self._client_repository.get_by_email(request.email)
        if existing_email:
            raise ValueError(f"Ya existe un cliente con email {request.email}")
        
        # Create domain entity
        client = Client(
            id=None,
            nombre_completo=request.nombre_completo.strip(),
            cedula=request.cedula.strip(),
            email=request.email.strip().lower(),
            telefono=request.telefono.strip(),
            fecha_nacimiento=request.fecha_nacimiento,
            direccion=request.direccion.strip(),
            info_adicional=request.info_adicional or {}
        )
        
        # Validate business rules
        if not client.validate():
            raise ValueError("Los datos del cliente no son válidos")
        
        # Save to repository
        try:
            created_client = await self._client_repository.create(client)
            
            return ClientResponse(
                id=created_client.id,
                nombre_completo=created_client.nombre_completo,
                cedula=created_client.cedula,
                email=created_client.email,
                telefono=created_client.telefono,
                fecha_nacimiento=created_client.fecha_nacimiento,
                direccion=created_client.direccion,
                info_adicional=created_client.info_adicional,
                created_at=created_client.created_at
            )
            
        except Exception as e:
            raise Exception(f"Error al crear el cliente: {str(e)}")
    
    async def get_client_by_id(self, client_id: int) -> Optional[ClientResponse]:
        """Get client by ID"""
        client = await self._client_repository.get_by_id(client_id)
        if not client:
            return None
        
        return ClientResponse(
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
    
    async def get_client_by_cedula(self, cedula: str) -> Optional[ClientResponse]:
        """Get client by cedula"""
        client = await self._client_repository.get_by_cedula(cedula)
        if not client:
            return None
        
        return ClientResponse(
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
    
    async def update_client(self, client_id: int, request: UpdateClientRequest) -> ClientResponse:
        """Update client information"""
        
        # Get existing client
        client = await self._client_repository.get_by_id(client_id)
        if not client:
            raise ValueError(f"Cliente con ID {client_id} no encontrado")
        
        # Check email uniqueness if changing email
        if request.email and request.email.lower() != client.email.lower():
            existing_email = await self._client_repository.get_by_email(request.email)
            if existing_email:
                raise ValueError(f"Ya existe un cliente con email {request.email}")
        
        # Update fields if provided
        if request.nombre_completo:
            client.nombre_completo = request.nombre_completo.strip()
        if request.email:
            client.email = request.email.strip().lower()
        if request.telefono:
            client.telefono = request.telefono.strip()
        if request.direccion:
            client.direccion = request.direccion.strip()
        if request.info_adicional is not None:
            client.info_adicional = request.info_adicional
        
        # Validate updated data
        if not client.validate():
            raise ValueError("Los datos actualizados del cliente no son válidos")
        
        try:
            updated_client = await self._client_repository.update(client)
            
            return ClientResponse(
                id=updated_client.id,
                nombre_completo=updated_client.nombre_completo,
                cedula=updated_client.cedula,
                email=updated_client.email,
                telefono=updated_client.telefono,
                fecha_nacimiento=updated_client.fecha_nacimiento,
                direccion=updated_client.direccion,
                info_adicional=updated_client.info_adicional,
                created_at=updated_client.created_at
            )
            
        except Exception as e:
            raise Exception(f"Error al actualizar el cliente: {str(e)}")
    
    async def search_clients(self, request: SearchClientsRequest) -> ClientListResponse:
        """Search clients by name or cedula"""
        try:
            if request.search_term:
                # Search by name or cedula
                clients_by_name = await self._client_repository.search_by_name(
                    request.search_term, request.skip, request.limit
                )
                clients_by_cedula = await self._client_repository.search_by_cedula(
                    request.search_term
                )
                
                # Combine results and remove duplicates
                all_clients = clients_by_name + [c for c in clients_by_cedula if c not in clients_by_name]
                
                # Apply pagination to combined results
                total = len(all_clients)
                paginated_clients = all_clients[request.skip:request.skip + request.limit]
            else:
                # Get all clients
                paginated_clients = await self._client_repository.get_all(request.skip, request.limit)
                total = await self._client_repository.count_total()
            
            # Convert to response DTOs
            client_responses = []
            for client in paginated_clients:
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
            
            # Calculate pagination
            page = (request.skip // request.limit) + 1
            total_pages = math.ceil(total / request.limit) if total > 0 else 1
            
            return ClientListResponse(
                clients=client_responses,
                total=total,
                page=page,
                page_size=request.limit,
                total_pages=total_pages
            )
            
        except Exception as e:
            raise Exception(f"Error al buscar clientes: {str(e)}")
    
    async def delete_client(self, client_id: int) -> bool:
        """Delete client"""
        try:
            # Check if client exists
            client = await self._client_repository.get_by_id(client_id)
            if not client:
                return False
            
            # TODO: Check if client has active loans/applications before deleting
            # This would require checking with LoanApplicationRepository
            
            return await self._client_repository.delete(client_id)
            
        except Exception as e:
            raise Exception(f"Error al eliminar el cliente: {str(e)}")
    
    async def get_all_clients(self, skip: int = 0, limit: int = 20) -> ClientListResponse:
        """Get all clients with pagination"""
        request = SearchClientsRequest(skip=skip, limit=limit)
        return await self.search_clients(request)