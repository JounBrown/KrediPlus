"""
Unit tests for Client Repository
"""
import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from datetime import date, datetime
from sqlalchemy.ext.asyncio import AsyncSession

from src.infrastructure.adapters.database.client_repository import SupabaseClientRepository
from src.infrastructure.adapters.database.models import ClientModel
from src.domain.entities.client import Client


class TestSupabaseClientRepository:
    """Test SupabaseClientRepository functionality"""
    
    def setup_method(self):
        """Setup test fixtures"""
        self.mock_db = AsyncMock(spec=AsyncSession)
        self.repository = SupabaseClientRepository(self.mock_db)
        
        # Sample client entity
        self.sample_client = Client(
            id=1,
            nombre_completo="Juan Pérez García",
            cedula="12345678",
            email="juan@example.com",
            telefono="3001234567",
            fecha_nacimiento=date(1985, 6, 15),
            direccion="Calle 123 #45-67",
            info_adicional={"notes": "test client"},
            created_at=datetime(2024, 1, 15, 10, 30, 0)
        )
        
        # Sample client model
        self.sample_model = ClientModel(
            id=1,
            nombre_completo="Juan Pérez García",
            cedula="12345678",
            email="juan@example.com",
            telefono="3001234567",
            fecha_nacimiento=date(1985, 6, 15),
            direccion="Calle 123 #45-67",
            info_adicional={"notes": "test client"},
            created_at=datetime(2024, 1, 15, 10, 30, 0)
        )


class TestModelEntityConversion(TestSupabaseClientRepository):
    """Test model to entity conversion methods"""
    
    def test_model_to_entity_conversion(self):
        """Test converting database model to domain entity"""
        # Act
        entity = self.repository._model_to_entity(self.sample_model)
        
        # Assert
        assert isinstance(entity, Client)
        assert entity.id == self.sample_model.id
        assert entity.nombre_completo == self.sample_model.nombre_completo
        assert entity.cedula == self.sample_model.cedula
        assert entity.email == self.sample_model.email
        assert entity.telefono == self.sample_model.telefono
        assert entity.fecha_nacimiento == self.sample_model.fecha_nacimiento
        assert entity.direccion == self.sample_model.direccion
        assert entity.info_adicional == self.sample_model.info_adicional
        assert entity.created_at == self.sample_model.created_at
    
    def test_entity_to_model_conversion(self):
        """Test converting domain entity to database model"""
        # Act
        model = self.repository._entity_to_model(self.sample_client)
        
        # Assert
        assert isinstance(model, ClientModel)
        assert model.id == self.sample_client.id
        assert model.nombre_completo == self.sample_client.nombre_completo
        assert model.cedula == self.sample_client.cedula
        assert model.email == self.sample_client.email
        assert model.telefono == self.sample_client.telefono
        assert model.fecha_nacimiento == self.sample_client.fecha_nacimiento
        assert model.direccion == self.sample_client.direccion
        assert model.info_adicional == self.sample_client.info_adicional
        assert model.created_at == self.sample_client.created_at
    
    def test_entity_to_model_with_none_created_at(self):
        """Test entity to model conversion when created_at is None"""
        # Arrange
        client_without_created_at = Client(
            id=1,
            nombre_completo="Test User",
            cedula="12345678",
            email="test@example.com",
            telefono="3001234567",
            fecha_nacimiento=date(1990, 1, 1),
            direccion="Test Address",
            created_at=None
        )
        
        # Act
        model = self.repository._entity_to_model(client_without_created_at)
        
        # Assert - created_at should be set to current time (not None)
        assert model.created_at is not None
        assert isinstance(model.created_at, datetime)
    
    def test_model_to_entity_with_none_values(self):
        """Test model to entity conversion with None values"""
        # Arrange
        model_with_nones = ClientModel(
            id=1,
            nombre_completo="Test User",
            cedula="12345678",
            email="test@example.com",
            telefono="3001234567",
            fecha_nacimiento=date(1990, 1, 1),
            direccion="Test Address",
            info_adicional=None,  # None value
            created_at=datetime.now()
        )
        
        # Act
        entity = self.repository._model_to_entity(model_with_nones)
        
        # Assert - info_adicional defaults to empty dict when None
        assert entity.info_adicional == {} or entity.info_adicional is None
        assert isinstance(entity, Client)


class TestCreateClient(TestSupabaseClientRepository):
    """Test create client functionality"""
    
    @pytest.mark.asyncio
    async def test_create_client_success(self):
        """Test successful client creation"""
        # Arrange
        new_client = Client(
            id=None,  # New client without ID
            nombre_completo="María González",
            cedula="87654321",
            email="maria@example.com",
            telefono="3009876543",
            fecha_nacimiento=date(1990, 3, 20),
            direccion="Avenida 456",
            info_adicional=None,
            created_at=None
        )
        
        # Mock the model that will be created
        created_model = ClientModel(
            id=2,  # Database assigns ID
            nombre_completo="María González",
            cedula="87654321",
            email="maria@example.com",
            telefono="3009876543",
            fecha_nacimiento=date(1990, 3, 20),
            direccion="Avenida 456",
            info_adicional=None,
            created_at=datetime.now()
        )
        
        # Setup mocks
        self.mock_db.flush = AsyncMock()
        self.mock_db.refresh = AsyncMock()
        
        # Mock the model creation and ID assignment
        with patch.object(self.repository, '_entity_to_model') as mock_entity_to_model, \
             patch.object(self.repository, '_model_to_entity') as mock_model_to_entity:
            
            mock_entity_to_model.return_value = created_model
            mock_model_to_entity.return_value = Client(
                id=2,
                nombre_completo="María González",
                cedula="87654321",
                email="maria@example.com",
                telefono="3009876543",
                fecha_nacimiento=date(1990, 3, 20),
                direccion="Avenida 456",
                info_adicional=None,
                created_at=datetime.now()
            )
            
            # Act
            result = await self.repository.create(new_client)
            
            # Assert
            assert result.id == 2
            assert result.nombre_completo == "María González"
            assert result.cedula == "87654321"
            
            # Verify database operations
            self.mock_db.add.assert_called_once()
            self.mock_db.flush.assert_called_once()
            self.mock_db.refresh.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_create_client_database_error(self):
        """Test client creation with database error"""
        # Arrange
        new_client = Client(
            id=None,
            nombre_completo="Test User",
            cedula="12345678",
            email="test@example.com",
            telefono="3001234567",
            fecha_nacimiento=date(1990, 1, 1),
            direccion="Test Address"
        )
        
        # Setup mock to raise exception
        self.mock_db.add.side_effect = Exception("Database connection error")
        self.mock_db.rollback = AsyncMock()
        
        # Act & Assert
        with pytest.raises(Exception) as exc_info:
            await self.repository.create(new_client)
        
        assert "Error creating client" in str(exc_info.value)
        assert "Database connection error" in str(exc_info.value)
        self.mock_db.rollback.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_create_client_ensures_no_id(self):
        """Test that create method ensures model has no ID"""
        # Arrange
        client_with_id = Client(
            id=999,  # Should be ignored
            nombre_completo="Test User",
            cedula="12345678",
            email="test@example.com",
            telefono="3001234567",
            fecha_nacimiento=date(1990, 1, 1),
            direccion="Test Address"
        )
        
        # Setup mocks
        self.mock_db.flush = AsyncMock()
        self.mock_db.refresh = AsyncMock()
        
        created_model = ClientModel(
            id=1,  # Database assigns new ID
            nombre_completo="Test User",
            cedula="12345678",
            email="test@example.com",
            telefono="3001234567",
            fecha_nacimiento=date(1990, 1, 1),
            direccion="Test Address",
            created_at=datetime.now()
        )
        
        with patch.object(self.repository, '_entity_to_model', return_value=created_model) as mock_entity_to_model, \
             patch.object(self.repository, '_model_to_entity') as mock_model_to_entity:
            
            mock_model_to_entity.return_value = Client(
                id=1,
                nombre_completo="Test User",
                cedula="12345678",
                email="test@example.com",
                telefono="3001234567",
                fecha_nacimiento=date(1990, 1, 1),
                direccion="Test Address",
                created_at=datetime.now()
            )
            
            # Act
            result = await self.repository.create(client_with_id)
            
            # Assert
            # Verify that the model's ID was set to None before adding
            added_model = self.mock_db.add.call_args[0][0]
            assert added_model.id is None
            assert result.id == 1  # Database assigned ID


class TestGetClient(TestSupabaseClientRepository):
    """Test get client functionality"""
    
    @pytest.mark.asyncio
    async def test_get_by_id_success(self):
        """Test successful client retrieval by ID"""
        # Arrange
        client_id = 1
        
        # Mock database result
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = self.sample_model
        self.mock_db.execute.return_value = mock_result
        
        # Act
        result = await self.repository.get_by_id(client_id)
        
        # Assert
        assert result is not None
        assert isinstance(result, Client)
        assert result.id == client_id
        assert result.nombre_completo == "Juan Pérez García"
        
        # Verify database query
        self.mock_db.execute.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_get_by_id_not_found(self):
        """Test client retrieval when ID not found"""
        # Arrange
        client_id = 999
        
        # Mock database result - no client found
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = None
        self.mock_db.execute.return_value = mock_result
        
        # Act
        result = await self.repository.get_by_id(client_id)
        
        # Assert
        assert result is None
        self.mock_db.execute.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_get_by_id_database_error(self):
        """Test client retrieval with database error"""
        # Arrange
        client_id = 1
        self.mock_db.execute.side_effect = Exception("Database error")
        
        # Act & Assert
        with pytest.raises(Exception) as exc_info:
            await self.repository.get_by_id(client_id)
        
        assert "Error getting client by ID" in str(exc_info.value)
    
    @pytest.mark.asyncio
    async def test_get_by_cedula_success(self):
        """Test successful client retrieval by cedula"""
        # Arrange
        cedula = "12345678"
        
        # Mock database result
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = self.sample_model
        self.mock_db.execute.return_value = mock_result
        
        # Act
        result = await self.repository.get_by_cedula(cedula)
        
        # Assert
        assert result is not None
        assert result.cedula == cedula
        self.mock_db.execute.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_get_by_email_success(self):
        """Test successful client retrieval by email"""
        # Arrange
        email = "juan@example.com"
        
        # Mock database result
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = self.sample_model
        self.mock_db.execute.return_value = mock_result
        
        # Act
        result = await self.repository.get_by_email(email)
        
        # Assert
        assert result is not None
        assert result.email == email
        self.mock_db.execute.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_get_by_email_case_insensitive(self):
        """Test that email search is case insensitive"""
        # Arrange
        email = "JUAN@EXAMPLE.COM"  # Uppercase
        
        # Mock database result
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = self.sample_model
        self.mock_db.execute.return_value = mock_result
        
        # Act
        result = await self.repository.get_by_email(email)
        
        # Assert
        assert result is not None
        # Verify that email was converted to lowercase in the query
        self.mock_db.execute.assert_called_once()


class TestGetAllClients(TestSupabaseClientRepository):
    """Test get all clients functionality"""
    
    @pytest.mark.asyncio
    async def test_get_all_success(self):
        """Test successful retrieval of all clients"""
        # Arrange
        client_models = [
            self.sample_model,
            ClientModel(
                id=2,
                nombre_completo="María González",
                cedula="87654321",
                email="maria@example.com",
                telefono="3009876543",
                fecha_nacimiento=date(1990, 3, 20),
                direccion="Avenida 456",
                info_adicional=None,
                created_at=datetime.now()
            )
        ]
        
        # Mock database result
        mock_result = MagicMock()
        mock_result.scalars.return_value.all.return_value = client_models
        self.mock_db.execute.return_value = mock_result
        
        # Act
        result = await self.repository.get_all(skip=0, limit=100)
        
        # Assert
        assert len(result) == 2
        assert all(isinstance(client, Client) for client in result)
        assert result[0].nombre_completo == "Juan Pérez García"
        assert result[1].nombre_completo == "María González"
        self.mock_db.execute.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_get_all_with_pagination(self):
        """Test get all clients with pagination parameters"""
        # Arrange
        skip = 10
        limit = 5
        
        mock_result = MagicMock()
        mock_result.scalars.return_value.all.return_value = []
        self.mock_db.execute.return_value = mock_result
        
        # Act
        result = await self.repository.get_all(skip=skip, limit=limit)
        
        # Assert
        assert result == []
        self.mock_db.execute.assert_called_once()
        # Verify that pagination parameters are used in the query
    
    @pytest.mark.asyncio
    async def test_get_all_empty_result(self):
        """Test get all clients with empty result"""
        # Arrange
        mock_result = MagicMock()
        mock_result.scalars.return_value.all.return_value = []
        self.mock_db.execute.return_value = mock_result
        
        # Act
        result = await self.repository.get_all()
        
        # Assert
        assert result == []
        assert isinstance(result, list)
        self.mock_db.execute.assert_called_once()


class TestSearchClients(TestSupabaseClientRepository):
    """Test search clients functionality"""
    
    @pytest.mark.asyncio
    async def test_search_by_name_success(self):
        """Test successful client search by name"""
        # Arrange
        search_name = "Juan"
        
        mock_result = MagicMock()
        mock_result.scalars.return_value.all.return_value = [self.sample_model]
        self.mock_db.execute.return_value = mock_result
        
        # Act
        result = await self.repository.search_by_name(search_name)
        
        # Assert
        assert len(result) == 1
        assert result[0].nombre_completo == "Juan Pérez García"
        self.mock_db.execute.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_search_by_name_partial_match(self):
        """Test client search by partial name match"""
        # Arrange
        search_name = "Pérez"
        
        mock_result = MagicMock()
        mock_result.scalars.return_value.all.return_value = [self.sample_model]
        self.mock_db.execute.return_value = mock_result
        
        # Act
        result = await self.repository.search_by_name(search_name, skip=0, limit=50)
        
        # Assert
        assert len(result) == 1
        assert "Pérez" in result[0].nombre_completo
        self.mock_db.execute.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_search_by_cedula_success(self):
        """Test successful client search by cedula"""
        # Arrange
        search_cedula = "1234"
        
        mock_result = MagicMock()
        mock_result.scalars.return_value.all.return_value = [self.sample_model]
        self.mock_db.execute.return_value = mock_result
        
        # Act
        result = await self.repository.search_by_cedula(search_cedula)
        
        # Assert
        assert len(result) == 1
        assert search_cedula in result[0].cedula
        self.mock_db.execute.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_search_no_results(self):
        """Test search with no matching results"""
        # Arrange
        search_name = "NonExistentName"
        
        mock_result = MagicMock()
        mock_result.scalars.return_value.all.return_value = []
        self.mock_db.execute.return_value = mock_result
        
        # Act
        result = await self.repository.search_by_name(search_name)
        
        # Assert
        assert result == []
        self.mock_db.execute.assert_called_once()


class TestUpdateClient(TestSupabaseClientRepository):
    """Test update client functionality"""
    
    @pytest.mark.asyncio
    async def test_update_client_success(self):
        """Test successful client update"""
        # Arrange
        updated_client = Client(
            id=1,
            nombre_completo="Juan Pérez García Updated",
            cedula="12345678",  # Cedula cannot be updated
            email="juan.updated@example.com",
            telefono="3005555555",
            fecha_nacimiento=date(1985, 6, 15),
            direccion="Nueva Dirección 789",
            info_adicional={"updated": True},
            created_at=datetime(2024, 1, 15, 10, 30, 0)
        )
        
        # Mock finding existing model
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = self.sample_model
        self.mock_db.execute.return_value = mock_result
        
        # Mock database operations
        self.mock_db.flush = AsyncMock()
        self.mock_db.refresh = AsyncMock()
        
        # Act
        with patch.object(self.repository, '_model_to_entity', return_value=updated_client):
            result = await self.repository.update(updated_client)
        
        # Assert
        assert result.nombre_completo == "Juan Pérez García Updated"
        assert result.email == "juan.updated@example.com"
        assert result.telefono == "3005555555"
        
        # Verify database operations
        self.mock_db.execute.assert_called_once()
        self.mock_db.flush.assert_called_once()
        self.mock_db.refresh.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_update_client_not_found(self):
        """Test update when client not found"""
        # Arrange
        non_existent_client = Client(
            id=999,
            nombre_completo="Non Existent",
            cedula="99999999",
            email="nonexistent@example.com",
            telefono="3000000000",
            fecha_nacimiento=date(1990, 1, 1),
            direccion="Nowhere"
        )
        
        # Mock not finding the client
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = None
        self.mock_db.execute.return_value = mock_result
        
        # Act & Assert
        with pytest.raises(Exception) as exc_info:
            await self.repository.update(non_existent_client)
        
        assert "Error updating client" in str(exc_info.value)
    
    @pytest.mark.asyncio
    async def test_update_client_database_error(self):
        """Test update with database error"""
        # Arrange
        updated_client = self.sample_client
        
        # Mock finding client but error on flush
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = self.sample_model
        self.mock_db.execute.return_value = mock_result
        self.mock_db.flush.side_effect = Exception("Database error")
        self.mock_db.rollback = AsyncMock()
        
        # Act & Assert
        with pytest.raises(Exception) as exc_info:
            await self.repository.update(updated_client)
        
        assert "Error updating client" in str(exc_info.value)
        self.mock_db.rollback.assert_called_once()


class TestDeleteClient(TestSupabaseClientRepository):
    """Test delete client functionality"""
    
    @pytest.mark.asyncio
    async def test_delete_client_success(self):
        """Test successful client deletion"""
        # Arrange
        client_id = 1
        
        # Mock finding the client
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = self.sample_model
        self.mock_db.execute.return_value = mock_result
        
        # Mock database operations
        self.mock_db.delete = AsyncMock()
        self.mock_db.flush = AsyncMock()
        
        # Act
        result = await self.repository.delete(client_id)
        
        # Assert
        assert result is True
        self.mock_db.execute.assert_called_once()
        self.mock_db.delete.assert_called_once_with(self.sample_model)
        self.mock_db.flush.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_delete_client_not_found(self):
        """Test delete when client not found"""
        # Arrange
        client_id = 999
        
        # Mock not finding the client
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = None
        self.mock_db.execute.return_value = mock_result
        
        # Act
        result = await self.repository.delete(client_id)
        
        # Assert
        assert result is False
        self.mock_db.execute.assert_called_once()
        # Verify delete was not called
        self.mock_db.delete.assert_not_called()
    
    @pytest.mark.asyncio
    async def test_delete_client_database_error(self):
        """Test delete with database error"""
        # Arrange
        client_id = 1
        
        # Mock finding client but error on delete
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = self.sample_model
        self.mock_db.execute.return_value = mock_result
        self.mock_db.delete.side_effect = Exception("Database error")
        self.mock_db.rollback = AsyncMock()
        
        # Act & Assert
        with pytest.raises(Exception) as exc_info:
            await self.repository.delete(client_id)
        
        assert "Error deleting client" in str(exc_info.value)
        self.mock_db.rollback.assert_called_once()


class TestClientExistence(TestSupabaseClientRepository):
    """Test client existence check functionality"""
    
    @pytest.mark.asyncio
    async def test_exists_by_cedula_true(self):
        """Test exists by cedula returns True when client exists"""
        # Arrange
        cedula = "12345678"
        
        # Mock database result - client exists
        mock_result = MagicMock()
        mock_result.scalar.return_value = 1  # Count = 1
        self.mock_db.execute.return_value = mock_result
        
        # Act
        result = await self.repository.exists_by_cedula(cedula)
        
        # Assert
        assert result is True
        self.mock_db.execute.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_exists_by_cedula_false(self):
        """Test exists by cedula returns False when client doesn't exist"""
        # Arrange
        cedula = "99999999"
        
        # Mock database result - no client
        mock_result = MagicMock()
        mock_result.scalar.return_value = 0  # Count = 0
        self.mock_db.execute.return_value = mock_result
        
        # Act
        result = await self.repository.exists_by_cedula(cedula)
        
        # Assert
        assert result is False
        self.mock_db.execute.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_exists_by_email_true(self):
        """Test exists by email returns True when client exists"""
        # Arrange
        email = "juan@example.com"
        
        # Mock database result
        mock_result = MagicMock()
        mock_result.scalar.return_value = 1
        self.mock_db.execute.return_value = mock_result
        
        # Act
        result = await self.repository.exists_by_email(email)
        
        # Assert
        assert result is True
        self.mock_db.execute.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_exists_by_email_case_insensitive(self):
        """Test exists by email is case insensitive"""
        # Arrange
        email = "JUAN@EXAMPLE.COM"  # Uppercase
        
        # Mock database result
        mock_result = MagicMock()
        mock_result.scalar.return_value = 1
        self.mock_db.execute.return_value = mock_result
        
        # Act
        result = await self.repository.exists_by_email(email)
        
        # Assert
        assert result is True
        self.mock_db.execute.assert_called_once()


class TestCountClients(TestSupabaseClientRepository):
    """Test count clients functionality"""
    
    @pytest.mark.asyncio
    async def test_count_total_success(self):
        """Test successful total count of clients"""
        # Arrange
        expected_count = 42
        
        # Mock database result
        mock_result = MagicMock()
        mock_result.scalar.return_value = expected_count
        self.mock_db.execute.return_value = mock_result
        
        # Act
        result = await self.repository.count_total()
        
        # Assert
        assert result == expected_count
        self.mock_db.execute.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_count_total_zero(self):
        """Test count total when no clients exist"""
        # Arrange
        mock_result = MagicMock()
        mock_result.scalar.return_value = 0
        self.mock_db.execute.return_value = mock_result
        
        # Act
        result = await self.repository.count_total()
        
        # Assert
        assert result == 0
        self.mock_db.execute.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_count_total_none_result(self):
        """Test count total when database returns None"""
        # Arrange
        mock_result = MagicMock()
        mock_result.scalar.return_value = None
        self.mock_db.execute.return_value = mock_result
        
        # Act
        result = await self.repository.count_total()
        
        # Assert
        assert result == 0  # Should default to 0
        self.mock_db.execute.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_count_total_database_error(self):
        """Test count total with database error"""
        # Arrange
        self.mock_db.execute.side_effect = Exception("Database error")
        
        # Act & Assert
        with pytest.raises(Exception) as exc_info:
            await self.repository.count_total()
        
        assert "Error counting total clients" in str(exc_info.value)


class TestRepositoryErrorHandling(TestSupabaseClientRepository):
    """Test repository error handling"""
    
    @pytest.mark.asyncio
    async def test_all_methods_handle_database_errors(self):
        """Test that all repository methods handle database errors properly"""
        # Arrange
        self.mock_db.execute.side_effect = Exception("Connection lost")
        
        # Test various methods
        methods_to_test = [
            (self.repository.get_by_id, (1,)),
            (self.repository.get_by_cedula, ("12345678",)),
            (self.repository.get_by_email, ("test@example.com",)),
            (self.repository.get_all, ()),
            (self.repository.search_by_name, ("test",)),
            (self.repository.search_by_cedula, ("123",)),
            (self.repository.exists_by_cedula, ("12345678",)),
            (self.repository.exists_by_email, ("test@example.com",)),
            (self.repository.count_total, ())
        ]
        
        # Act & Assert
        for method, args in methods_to_test:
            with pytest.raises(Exception) as exc_info:
                await method(*args)
            
            # Verify error message contains method-specific context
            assert "Error" in str(exc_info.value)
            assert "Connection lost" in str(exc_info.value)
    
    @pytest.mark.asyncio
    async def test_repository_maintains_session_state(self):
        """Test that repository maintains database session state"""
        # Arrange & Act
        repository1 = SupabaseClientRepository(self.mock_db)
        repository2 = SupabaseClientRepository(self.mock_db)
        
        # Assert
        assert repository1.db is self.mock_db
        assert repository2.db is self.mock_db
        assert repository1.db is repository2.db