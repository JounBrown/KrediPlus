"""
Unit tests for Client Service - Full Coverage
"""
import pytest
from unittest.mock import AsyncMock, MagicMock
from datetime import datetime, date

from src.application.services.client_service import ClientService
from src.domain.entities.client import Client
from src.application.dtos.client_dtos import (
    CreateClientRequest,
    UpdateClientRequest,
    SearchClientsRequest
)


class TestClientServiceFull:
    """Test ClientService functionality"""
    
    def setup_method(self):
        """Setup test fixtures"""
        self.mock_repository = MagicMock()
        self.service = ClientService(self.mock_repository)
        
        self.sample_client = Client(
            id=1,
            nombre_completo="Juan Pérez García",
            cedula="1234567890",
            email="juan@example.com",
            telefono="3001234567",
            fecha_nacimiento=date(1990, 5, 15),
            direccion="Calle 123 #45-67",
            info_adicional={"ocupacion": "Ingeniero"},
            created_at=datetime.now()
        )


class TestCreateClientFull(TestClientServiceFull):
    """Test create_client method - full coverage"""
    
    @pytest.mark.asyncio
    async def test_create_client_success(self):
        """Test successful client creation"""
        request = CreateClientRequest(
            nombre_completo="Juan Pérez García",
            cedula="1234567890",
            email="juan@example.com",
            telefono="3001234567",
            fecha_nacimiento=date(1990, 5, 15),
            direccion="Calle 123 #45-67",
            info_adicional={"ocupacion": "Ingeniero"}
        )
        
        self.mock_repository.get_by_cedula = AsyncMock(return_value=None)
        self.mock_repository.get_by_email = AsyncMock(return_value=None)
        self.mock_repository.create = AsyncMock(return_value=self.sample_client)
        
        result = await self.service.create_client(request)
        
        assert result is not None
        assert result.id == 1
        assert result.nombre_completo == "Juan Pérez García"
        assert result.email == "juan@example.com"
    
    @pytest.mark.asyncio
    async def test_create_client_duplicate_cedula(self):
        """Test creation fails with duplicate cedula"""
        request = CreateClientRequest(
            nombre_completo="Juan Pérez",
            cedula="1234567890",
            email="nuevo@example.com",
            telefono="3001234567",
            fecha_nacimiento=date(1990, 5, 15),
            direccion="Calle 123"
        )
        
        self.mock_repository.get_by_cedula = AsyncMock(return_value=self.sample_client)
        
        with pytest.raises(ValueError) as exc_info:
            await self.service.create_client(request)
        
        assert "Ya existe un cliente con cédula" in str(exc_info.value)
    
    @pytest.mark.asyncio
    async def test_create_client_duplicate_email(self):
        """Test creation fails with duplicate email"""
        request = CreateClientRequest(
            nombre_completo="Otro Cliente",
            cedula="9876543210",
            email="juan@example.com",
            telefono="3009876543",
            fecha_nacimiento=date(1985, 3, 20),
            direccion="Otra Calle 456"
        )
        
        self.mock_repository.get_by_cedula = AsyncMock(return_value=None)
        self.mock_repository.get_by_email = AsyncMock(return_value=self.sample_client)
        
        with pytest.raises(ValueError) as exc_info:
            await self.service.create_client(request)
        
        assert "Ya existe un cliente con email" in str(exc_info.value)
    
    @pytest.mark.asyncio
    async def test_create_client_repository_error(self):
        """Test creation with repository error"""
        request = CreateClientRequest(
            nombre_completo="Juan Pérez",
            cedula="1234567890",
            email="juan@example.com",
            telefono="3001234567",
            fecha_nacimiento=date(1990, 5, 15),
            direccion="Calle 123"
        )
        
        self.mock_repository.get_by_cedula = AsyncMock(return_value=None)
        self.mock_repository.get_by_email = AsyncMock(return_value=None)
        self.mock_repository.create = AsyncMock(side_effect=Exception("Database error"))
        
        with pytest.raises(Exception) as exc_info:
            await self.service.create_client(request)
        
        assert "Error al crear el cliente" in str(exc_info.value)


class TestGetClientFull(TestClientServiceFull):
    """Test get client methods"""
    
    @pytest.mark.asyncio
    async def test_get_client_by_id_success(self):
        """Test successful client retrieval by ID"""
        self.mock_repository.get_by_id = AsyncMock(return_value=self.sample_client)
        
        result = await self.service.get_client_by_id(1)
        
        assert result is not None
        assert result.id == 1
        assert result.nombre_completo == "Juan Pérez García"
    
    @pytest.mark.asyncio
    async def test_get_client_by_id_not_found(self):
        """Test retrieval when client not found"""
        self.mock_repository.get_by_id = AsyncMock(return_value=None)
        
        result = await self.service.get_client_by_id(999)
        
        assert result is None
    
    @pytest.mark.asyncio
    async def test_get_client_by_cedula_success(self):
        """Test successful client retrieval by cedula"""
        self.mock_repository.get_by_cedula = AsyncMock(return_value=self.sample_client)
        
        result = await self.service.get_client_by_cedula("1234567890")
        
        assert result is not None
        assert result.cedula == "1234567890"
    
    @pytest.mark.asyncio
    async def test_get_client_by_cedula_not_found(self):
        """Test retrieval when cedula not found"""
        self.mock_repository.get_by_cedula = AsyncMock(return_value=None)
        
        result = await self.service.get_client_by_cedula("0000000000")
        
        assert result is None


class TestUpdateClientFull(TestClientServiceFull):
    """Test update_client method - full coverage"""
    
    @pytest.mark.asyncio
    async def test_update_client_success(self):
        """Test successful client update"""
        request = UpdateClientRequest(
            nombre_completo="Juan Carlos Pérez",
            telefono="3009999999"
        )
        
        updated_client = Client(
            id=1,
            nombre_completo="Juan Carlos Pérez",
            cedula="1234567890",
            email="juan@example.com",
            telefono="3009999999",
            fecha_nacimiento=date(1990, 5, 15),
            direccion="Calle 123 #45-67",
            info_adicional={"ocupacion": "Ingeniero"},
            created_at=datetime.now()
        )
        
        self.mock_repository.get_by_id = AsyncMock(return_value=self.sample_client)
        self.mock_repository.update = AsyncMock(return_value=updated_client)
        
        result = await self.service.update_client(1, request)
        
        assert result.nombre_completo == "Juan Carlos Pérez"
        assert result.telefono == "3009999999"
    
    @pytest.mark.asyncio
    async def test_update_client_not_found(self):
        """Test update when client not found"""
        request = UpdateClientRequest(nombre_completo="Nuevo Nombre")
        
        self.mock_repository.get_by_id = AsyncMock(return_value=None)
        
        with pytest.raises(ValueError) as exc_info:
            await self.service.update_client(999, request)
        
        assert "no encontrado" in str(exc_info.value)
    
    @pytest.mark.asyncio
    async def test_update_client_email_duplicate(self):
        """Test update fails with duplicate email"""
        request = UpdateClientRequest(email="otro@example.com")
        
        other_client = Client(
            id=2,
            nombre_completo="Otro Cliente",
            cedula="9876543210",
            email="otro@example.com",
            telefono="3009876543",
            fecha_nacimiento=date(1985, 3, 20),
            direccion="Otra Calle",
            created_at=datetime.now()
        )
        
        self.mock_repository.get_by_id = AsyncMock(return_value=self.sample_client)
        self.mock_repository.get_by_email = AsyncMock(return_value=other_client)
        
        with pytest.raises(ValueError) as exc_info:
            await self.service.update_client(1, request)
        
        assert "Ya existe un cliente con email" in str(exc_info.value)
    
    @pytest.mark.asyncio
    async def test_update_client_same_email_allowed(self):
        """Test update with same email is allowed"""
        request = UpdateClientRequest(
            email="juan@example.com",
            telefono="3009999999"
        )
        
        updated_client = Client(
            id=1,
            nombre_completo="Juan Pérez García",
            cedula="1234567890",
            email="juan@example.com",
            telefono="3009999999",
            fecha_nacimiento=date(1990, 5, 15),
            direccion="Calle 123 #45-67",
            created_at=datetime.now()
        )
        
        self.mock_repository.get_by_id = AsyncMock(return_value=self.sample_client)
        self.mock_repository.update = AsyncMock(return_value=updated_client)
        
        result = await self.service.update_client(1, request)
        
        assert result.email == "juan@example.com"
    
    @pytest.mark.asyncio
    async def test_update_client_repository_error(self):
        """Test update with repository error"""
        request = UpdateClientRequest(nombre_completo="Nuevo Nombre")
        
        self.mock_repository.get_by_id = AsyncMock(return_value=self.sample_client)
        self.mock_repository.update = AsyncMock(side_effect=Exception("Database error"))
        
        with pytest.raises(Exception) as exc_info:
            await self.service.update_client(1, request)
        
        assert "Error al actualizar el cliente" in str(exc_info.value)


class TestSearchClientsFull(TestClientServiceFull):
    """Test search_clients method - full coverage"""
    
    @pytest.mark.asyncio
    async def test_search_clients_with_term(self):
        """Test search with search term"""
        request = SearchClientsRequest(search_term="Juan", skip=0, limit=10)
        
        self.mock_repository.search_by_name = AsyncMock(return_value=[self.sample_client])
        self.mock_repository.search_by_cedula = AsyncMock(return_value=[])
        
        result = await self.service.search_clients(request)
        
        assert result.total == 1
        assert len(result.clients) == 1
        assert result.clients[0].nombre_completo == "Juan Pérez García"
    
    @pytest.mark.asyncio
    async def test_search_clients_without_term(self):
        """Test search without search term (get all)"""
        request = SearchClientsRequest(skip=0, limit=10)
        
        self.mock_repository.get_all = AsyncMock(return_value=[self.sample_client])
        self.mock_repository.count_total = AsyncMock(return_value=1)
        
        result = await self.service.search_clients(request)
        
        assert result.total == 1
        assert len(result.clients) == 1
    
    @pytest.mark.asyncio
    async def test_search_clients_pagination(self):
        """Test search with pagination"""
        request = SearchClientsRequest(skip=20, limit=10)
        
        self.mock_repository.get_all = AsyncMock(return_value=[self.sample_client])
        self.mock_repository.count_total = AsyncMock(return_value=50)
        
        result = await self.service.search_clients(request)
        
        assert result.total == 50
        assert result.page == 3
        assert result.total_pages == 5
    
    @pytest.mark.asyncio
    async def test_search_clients_empty_result(self):
        """Test search with no results"""
        request = SearchClientsRequest(search_term="NoExiste", skip=0, limit=10)
        
        self.mock_repository.search_by_name = AsyncMock(return_value=[])
        self.mock_repository.search_by_cedula = AsyncMock(return_value=[])
        
        result = await self.service.search_clients(request)
        
        assert result.total == 0
        assert len(result.clients) == 0
    
    @pytest.mark.asyncio
    async def test_search_clients_repository_error(self):
        """Test search with repository error"""
        request = SearchClientsRequest(skip=0, limit=10)
        
        self.mock_repository.get_all = AsyncMock(side_effect=Exception("Database error"))
        
        with pytest.raises(Exception) as exc_info:
            await self.service.search_clients(request)
        
        assert "Error al buscar clientes" in str(exc_info.value)


class TestDeleteClientFull(TestClientServiceFull):
    """Test delete_client method - full coverage"""
    
    @pytest.mark.asyncio
    async def test_delete_client_success(self):
        """Test successful client deletion"""
        self.mock_repository.get_by_id = AsyncMock(return_value=self.sample_client)
        self.mock_repository.delete = AsyncMock(return_value=True)
        
        result = await self.service.delete_client(1)
        
        assert result is True
    
    @pytest.mark.asyncio
    async def test_delete_client_not_found(self):
        """Test deletion when client not found"""
        self.mock_repository.get_by_id = AsyncMock(return_value=None)
        
        result = await self.service.delete_client(999)
        
        assert result is False
    
    @pytest.mark.asyncio
    async def test_delete_client_repository_error(self):
        """Test deletion with repository error"""
        self.mock_repository.get_by_id = AsyncMock(return_value=self.sample_client)
        self.mock_repository.delete = AsyncMock(side_effect=Exception("Database error"))
        
        with pytest.raises(Exception) as exc_info:
            await self.service.delete_client(1)
        
        assert "Error al eliminar el cliente" in str(exc_info.value)


class TestGetAllClientsFull(TestClientServiceFull):
    """Test get_all_clients method"""
    
    @pytest.mark.asyncio
    async def test_get_all_clients_success(self):
        """Test get all clients"""
        self.mock_repository.get_all = AsyncMock(return_value=[self.sample_client])
        self.mock_repository.count_total = AsyncMock(return_value=1)
        
        result = await self.service.get_all_clients(skip=0, limit=20)
        
        assert result.total == 1
        assert len(result.clients) == 1
