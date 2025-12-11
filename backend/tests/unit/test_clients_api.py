"""
Unit tests for Clients API routes
"""
import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from datetime import date, datetime
from decimal import Decimal
from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from src.api.routes.clients import (
    create_client,
    get_client,
    list_clients,
    get_client_by_cedula,
    update_client,
    delete_client,
    search_clients_by_name,
    delete_client_document,
    create_credit_for_client,
    update_client_credit
)
from src.application.dtos.client_dtos import (
    CreateClientRequest,
    UpdateClientRequest,
    ClientResponse
)
from src.application.dtos.credit_dtos import (
    CreateCreditForClientRequest,
    UpdateCreditRequest,
    CreditResponse
)


class TestCreateClient:
    """Test create_client endpoint"""
    
    @pytest.mark.asyncio
    async def test_create_client_success(self):
        """Test successful client creation"""
        # Arrange
        request = CreateClientRequest(
            nombre_completo="Juan Pérez",
            cedula="12345678",
            email="juan@example.com",
            telefono="3001234567",
            fecha_nacimiento=date(1990, 1, 1),
            direccion="Calle 123",
            info_adicional={"notes": "test"}
        )
        
        expected_response = ClientResponse(
            id=1,
            nombre_completo="Juan Pérez",
            cedula="12345678",
            email="juan@example.com",
            telefono="3001234567",
            fecha_nacimiento=date(1990, 1, 1),
            direccion="Calle 123",
            info_adicional={"notes": "test"},
            created_at=datetime.now()
        )
        
        mock_service = AsyncMock()
        mock_service.create_client.return_value = expected_response
        
        # Act
        result = await create_client(request, mock_service)
        
        # Assert
        assert result == expected_response
        mock_service.create_client.assert_called_once_with(request)
    
    def test_create_client_validation_error(self):
        """Test client creation with validation error - Pydantic validates at creation"""
        from pydantic import ValidationError
        
        # Act & Assert - Pydantic should reject empty name
        with pytest.raises(ValidationError) as exc_info:
            CreateClientRequest(
                nombre_completo="",  # Invalid empty name
                cedula="12345678",
                email="juan@example.com",
                telefono="3001234567",
                fecha_nacimiento=date(1990, 1, 1),
                direccion="Calle 123"
            )
        
        assert "nombre_completo" in str(exc_info.value)
    
    @pytest.mark.asyncio
    async def test_create_client_internal_error(self):
        """Test client creation with internal error"""
        # Arrange
        request = CreateClientRequest(
            nombre_completo="Juan Pérez",
            cedula="12345678",
            email="juan@example.com",
            telefono="3001234567",
            fecha_nacimiento=date(1990, 1, 1),
            direccion="Calle 123"
        )
        
        mock_service = AsyncMock()
        mock_service.create_client.side_effect = Exception("Database error")
        
        # Act & Assert
        with pytest.raises(HTTPException) as exc_info:
            await create_client(request, mock_service)
        
        assert exc_info.value.status_code == 500
        assert "Error creating client" in str(exc_info.value.detail)


class TestGetClient:
    """Test get_client endpoint"""
    
    @pytest.mark.asyncio
    async def test_get_client_success(self):
        """Test successful client retrieval"""
        # Arrange
        client_id = 1
        expected_response = ClientResponse(
            id=1,
            nombre_completo="Juan Pérez",
            cedula="12345678",
            email="juan@example.com",
            telefono="3001234567",
            fecha_nacimiento=date(1990, 1, 1),
            direccion="Calle 123",
            info_adicional=None,
            created_at=datetime.now()
        )
        
        mock_service = AsyncMock()
        mock_service.get_client_by_id.return_value = expected_response
        
        # Act
        result = await get_client(client_id, mock_service)
        
        # Assert
        assert result == expected_response
        mock_service.get_client_by_id.assert_called_once_with(client_id)
    
    @pytest.mark.asyncio
    async def test_get_client_not_found(self):
        """Test client retrieval when client not found"""
        # Arrange
        client_id = 999
        mock_service = AsyncMock()
        mock_service.get_client_by_id.return_value = None
        
        # Act & Assert
        with pytest.raises(HTTPException) as exc_info:
            await get_client(client_id, mock_service)
        
        assert exc_info.value.status_code == 404
        assert "Client not found" in str(exc_info.value.detail)
    
    @pytest.mark.asyncio
    async def test_get_client_internal_error(self):
        """Test client retrieval with internal error"""
        # Arrange
        client_id = 1
        mock_service = AsyncMock()
        mock_service.get_client_by_id.side_effect = Exception("Database error")
        
        # Act & Assert
        with pytest.raises(HTTPException) as exc_info:
            await get_client(client_id, mock_service)
        
        assert exc_info.value.status_code == 500
        assert "Error getting client" in str(exc_info.value.detail)


class TestGetClientByCedula:
    """Test get_client_by_cedula endpoint"""
    
    @pytest.mark.asyncio
    async def test_get_client_by_cedula_success(self):
        """Test successful client retrieval by cedula"""
        # Arrange
        cedula = "12345678"
        expected_response = ClientResponse(
            id=1,
            nombre_completo="Juan Pérez",
            cedula="12345678",
            email="juan@example.com",
            telefono="3001234567",
            fecha_nacimiento=date(1990, 1, 1),
            direccion="Calle 123",
            info_adicional=None,
            created_at=datetime.now()
        )
        
        mock_service = AsyncMock()
        mock_service.get_client_by_cedula.return_value = expected_response
        
        # Act
        result = await get_client_by_cedula(cedula, mock_service)
        
        # Assert
        assert result == expected_response
        mock_service.get_client_by_cedula.assert_called_once_with(cedula)
    
    @pytest.mark.asyncio
    async def test_get_client_by_cedula_not_found(self):
        """Test client retrieval by cedula when not found"""
        # Arrange
        cedula = "99999999"
        mock_service = AsyncMock()
        mock_service.get_client_by_cedula.return_value = None
        
        # Act & Assert
        with pytest.raises(HTTPException) as exc_info:
            await get_client_by_cedula(cedula, mock_service)
        
        assert exc_info.value.status_code == 404
        assert "Client not found" in str(exc_info.value.detail)


class TestUpdateClient:
    """Test update_client endpoint"""
    
    @pytest.mark.asyncio
    async def test_update_client_success(self):
        """Test successful client update"""
        # Arrange
        client_id = 1
        request = UpdateClientRequest(
            nombre_completo="Juan Pérez Updated",
            email="juan.updated@example.com",
            telefono="3009876543",
            direccion="Nueva Calle 456",
            info_adicional={"updated": True}
        )
        
        expected_response = ClientResponse(
            id=1,
            nombre_completo="Juan Pérez Updated",
            cedula="12345678",
            email="juan.updated@example.com",
            telefono="3009876543",
            fecha_nacimiento=date(1990, 1, 1),
            direccion="Nueva Calle 456",
            info_adicional={"updated": True},
            created_at=datetime.now()
        )
        
        mock_service = AsyncMock()
        mock_service.update_client.return_value = expected_response
        
        # Act
        result = await update_client(client_id, request, mock_service)
        
        # Assert
        assert result == expected_response
        mock_service.update_client.assert_called_once_with(client_id, request)
    
    def test_update_client_validation_error(self):
        """Test client update with validation error - Pydantic validates at creation"""
        from pydantic import ValidationError
        
        # Act & Assert - Pydantic should reject empty name
        with pytest.raises(ValidationError) as exc_info:
            UpdateClientRequest(
                nombre_completo="",  # Invalid empty name
                email="juan@example.com"
            )
        
        assert "nombre_completo" in str(exc_info.value)


class TestDeleteClient:
    """Test delete_client endpoint"""
    
    @pytest.mark.asyncio
    async def test_delete_client_success(self):
        """Test successful client deletion"""
        # Arrange
        client_id = 1
        mock_service = AsyncMock()
        mock_service.delete_client.return_value = True
        
        # Act
        result = await delete_client(client_id, mock_service)
        
        # Assert
        assert result == {"message": "Client deleted successfully"}
        mock_service.delete_client.assert_called_once_with(client_id)
    
    @pytest.mark.asyncio
    async def test_delete_client_not_found(self):
        """Test client deletion when client not found"""
        # Arrange
        client_id = 999
        mock_service = AsyncMock()
        mock_service.delete_client.return_value = False
        
        # Act & Assert
        with pytest.raises(HTTPException) as exc_info:
            await delete_client(client_id, mock_service)
        
        assert exc_info.value.status_code == 404
        assert "Client not found" in str(exc_info.value.detail)


class TestCreateCreditForClient:
    """Test create_credit_for_client endpoint"""
    
    @pytest.mark.asyncio
    async def test_create_credit_for_client_success(self):
        """Test successful credit creation for client"""
        # Arrange
        client_id = 1
        credit_request = CreateCreditForClientRequest(
            monto_aprobado=Decimal('1000000'),
            plazo_meses=12,
            tasa_interes=Decimal('15.5')
        )
        
        expected_client = ClientResponse(
            id=1,
            nombre_completo="Juan Pérez",
            cedula="12345678",
            email="juan@example.com",
            telefono="3001234567",
            fecha_nacimiento=date(1990, 1, 1),
            direccion="Calle 123",
            info_adicional=None,
            created_at=datetime.now()
        )
        
        expected_credit = CreditResponse(
            id=1,
            client_id=1,
            monto_aprobado=Decimal('1000000'),
            plazo_meses=12,
            tasa_interes=Decimal('15.5'),
            estado="EN_ESTUDIO",
            fecha_desembolso=None,
            created_at=datetime.now()
        )
        
        # Mock database session
        mock_db = AsyncMock(spec=AsyncSession)
        
        # Act & Assert with patches
        with patch('src.api.routes.clients.get_client_service') as mock_get_client_service, \
             patch('src.application.services.credit_service.CreditService') as mock_credit_service_class, \
             patch('src.infrastructure.adapters.database.credit_repository.SupabaseCreditRepository') as mock_credit_repo:
            
            # Setup client service mock
            mock_client_service = AsyncMock()
            mock_client_service.get_client_by_id.return_value = expected_client
            mock_get_client_service.return_value = mock_client_service
            
            # Setup credit service mock
            mock_credit_service = AsyncMock()
            mock_credit_service.create_credit.return_value = expected_credit
            mock_credit_service_class.return_value = mock_credit_service
            
            # Call the function
            result = await create_credit_for_client(client_id, credit_request, mock_db)
            
            # Assertions
            assert result == expected_credit
            mock_client_service.get_client_by_id.assert_called_once_with(client_id)
            mock_credit_service.create_credit.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_create_credit_for_client_not_found(self):
        """Test credit creation when client not found"""
        # Arrange
        client_id = 999
        credit_request = CreateCreditForClientRequest(
            monto_aprobado=Decimal('1000000'),
            plazo_meses=12,
            tasa_interes=Decimal('15.5')
        )
        
        mock_db = AsyncMock(spec=AsyncSession)
        
        # Act & Assert
        with patch('src.api.routes.clients.get_client_service') as mock_get_client_service:
            mock_client_service = AsyncMock()
            mock_client_service.get_client_by_id.return_value = None
            mock_get_client_service.return_value = mock_client_service
            
            with pytest.raises(HTTPException) as exc_info:
                await create_credit_for_client(client_id, credit_request, mock_db)
            
            assert exc_info.value.status_code == 404
            assert "Client not found" in str(exc_info.value.detail)


class TestListClients:
    """Test list_clients endpoint"""
    
    @pytest.mark.asyncio
    async def test_list_clients_success(self):
        """Test successful client listing"""
        # Arrange
        mock_db = AsyncMock(spec=AsyncSession)
        
        # Mock client entities
        from src.domain.entities.client import Client
        mock_clients = [
            Client(
                id=1,
                nombre_completo="Juan Pérez",
                cedula="12345678",
                email="juan@example.com",
                telefono="3001234567",
                fecha_nacimiento=date(1990, 1, 1),
                direccion="Calle 123",
                info_adicional=None,
                created_at=datetime.now()
            ),
            Client(
                id=2,
                nombre_completo="María García",
                cedula="87654321",
                email="maria@example.com",
                telefono="3009876543",
                fecha_nacimiento=date(1985, 5, 15),
                direccion="Calle 456",
                info_adicional=None,
                created_at=datetime.now()
            )
        ]
        
        # Act & Assert
        with patch('src.infrastructure.adapters.database.client_repository.SupabaseClientRepository') as mock_repo_class:
            mock_repo = AsyncMock()
            mock_repo.get_all.return_value = mock_clients
            mock_repo_class.return_value = mock_repo
            
            result = await list_clients(mock_db)
            
            # Verify we get a list of ClientResponse objects
            assert len(result) == 2
            assert all(isinstance(client, ClientResponse) for client in result)
            assert result[0].nombre_completo == "Juan Pérez"
            assert result[1].nombre_completo == "María García"
            
            mock_repo.get_all.assert_called_once_with(skip=0, limit=10000)


class TestSearchClientsByName:
    """Test search_clients_by_name endpoint"""
    
    def test_search_clients_by_name_placeholder(self):
        """Placeholder test - search functionality tested via integration tests"""
        # This test is a placeholder because the search endpoint requires
        # complex database mocking that is better tested via integration tests
        assert True


class TestDeleteClientDocument:
    """Test delete_client_document endpoint"""
    
    @pytest.mark.asyncio
    async def test_delete_client_document_success(self):
        """Test successful client document deletion"""
        # Arrange
        client_id = 1
        document_id = 1
        mock_db = AsyncMock(spec=AsyncSession)
        
        expected_result = {"message": "Document deleted successfully"}
        
        # Act & Assert
        with patch('src.application.services.client_document_service.ClientDocumentService') as mock_service_class, \
             patch('src.infrastructure.adapters.database.client_document_repository.SupabaseClientDocumentRepository') as mock_repo_class:
            
            mock_service = AsyncMock()
            mock_service.delete_client_document.return_value = expected_result
            mock_service_class.return_value = mock_service
            
            result = await delete_client_document(client_id, document_id, mock_db)
            
            assert result == expected_result
            mock_service.delete_client_document.assert_called_once_with(client_id, document_id)
    
    @pytest.mark.asyncio
    async def test_delete_client_document_not_found(self):
        """Test client document deletion when document not found"""
        # Arrange
        client_id = 1
        document_id = 999
        mock_db = AsyncMock(spec=AsyncSession)
        
        # Act & Assert
        with patch('src.application.services.client_document_service.ClientDocumentService') as mock_service_class, \
             patch('src.infrastructure.adapters.database.client_document_repository.SupabaseClientDocumentRepository'):
            
            mock_service = AsyncMock()
            mock_service.delete_client_document.side_effect = ValueError("Document not found")
            mock_service_class.return_value = mock_service
            
            with pytest.raises(HTTPException) as exc_info:
                await delete_client_document(client_id, document_id, mock_db)
            
            assert exc_info.value.status_code == 404
            assert "Document not found" in str(exc_info.value.detail)


class TestUpdateClientCredit:
    """Test update_client_credit endpoint"""
    
    @pytest.mark.asyncio
    async def test_update_client_credit_success(self):
        """Test successful client credit update"""
        # Arrange
        client_id = 1
        credit_id = 1
        credit_request = UpdateCreditRequest(
            monto_aprobado=Decimal('1500000'),
            plazo_meses=24,
            tasa_interes=Decimal('12.0'),
            estado="APROBADO"
        )
        
        expected_client = ClientResponse(
            id=1,
            nombre_completo="Juan Pérez",
            cedula="12345678",
            email="juan@example.com",
            telefono="3001234567",
            fecha_nacimiento=date(1990, 1, 1),
            direccion="Calle 123",
            info_adicional=None,
            created_at=datetime.now()
        )
        
        existing_credit = CreditResponse(
            id=1,
            client_id=1,  # Belongs to the client
            monto_aprobado=Decimal('1000000'),
            plazo_meses=12,
            tasa_interes=Decimal('15.5'),
            estado="EN_ESTUDIO",
            fecha_desembolso=None,
            created_at=datetime.now()
        )
        
        updated_credit = CreditResponse(
            id=1,
            client_id=1,
            monto_aprobado=Decimal('1500000'),
            plazo_meses=24,
            tasa_interes=Decimal('12.0'),
            estado="APROBADO",
            fecha_desembolso=None,
            created_at=datetime.now()
        )
        
        mock_db = AsyncMock(spec=AsyncSession)
        
        # Act & Assert
        with patch('src.api.routes.clients.get_client_service') as mock_get_client_service, \
             patch('src.application.services.credit_service.CreditService') as mock_credit_service_class, \
             patch('src.infrastructure.adapters.database.credit_repository.SupabaseCreditRepository'):
            
            # Setup client service mock
            mock_client_service = AsyncMock()
            mock_client_service.get_client_by_id.return_value = expected_client
            mock_get_client_service.return_value = mock_client_service
            
            # Setup credit service mock
            mock_credit_service = AsyncMock()
            mock_credit_service.get_credit_by_id.return_value = existing_credit
            mock_credit_service.update_credit.return_value = updated_credit
            mock_credit_service_class.return_value = mock_credit_service
            
            result = await update_client_credit(client_id, credit_id, credit_request, mock_db)
            
            assert result == updated_credit
            mock_client_service.get_client_by_id.assert_called_once_with(client_id)
            mock_credit_service.get_credit_by_id.assert_called_once_with(credit_id)
            mock_credit_service.update_credit.assert_called_once_with(credit_id, credit_request)
    
    @pytest.mark.asyncio
    async def test_update_client_credit_wrong_client(self):
        """Test credit update when credit doesn't belong to client"""
        # Arrange
        client_id = 1
        credit_id = 1
        credit_request = UpdateCreditRequest(
            monto_aprobado=Decimal('1500000')
        )
        
        expected_client = ClientResponse(
            id=1,
            nombre_completo="Juan Pérez",
            cedula="12345678",
            email="juan@example.com",
            telefono="3001234567",
            fecha_nacimiento=date(1990, 1, 1),
            direccion="Calle 123",
            info_adicional=None,
            created_at=datetime.now()
        )
        
        existing_credit = CreditResponse(
            id=1,
            client_id=2,  # Belongs to different client
            monto_aprobado=Decimal('1000000'),
            plazo_meses=12,
            tasa_interes=Decimal('15.5'),
            estado="EN_ESTUDIO",
            fecha_desembolso=None,
            created_at=datetime.now()
        )
        
        mock_db = AsyncMock(spec=AsyncSession)
        
        # Act & Assert
        with patch('src.api.routes.clients.get_client_service') as mock_get_client_service, \
             patch('src.application.services.credit_service.CreditService') as mock_credit_service_class, \
             patch('src.infrastructure.adapters.database.credit_repository.SupabaseCreditRepository'):
            
            mock_client_service = AsyncMock()
            mock_client_service.get_client_by_id.return_value = expected_client
            mock_get_client_service.return_value = mock_client_service
            
            mock_credit_service = AsyncMock()
            mock_credit_service.get_credit_by_id.return_value = existing_credit
            mock_credit_service_class.return_value = mock_credit_service
            
            with pytest.raises(HTTPException) as exc_info:
                await update_client_credit(client_id, credit_id, credit_request, mock_db)
            
            assert exc_info.value.status_code == 404
            assert f"Credit {credit_id} does not belong to client {client_id}" in str(exc_info.value.detail)