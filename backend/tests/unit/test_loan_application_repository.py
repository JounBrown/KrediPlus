"""
Unit tests for Loan Application Repository
"""
import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from datetime import date, datetime
from sqlalchemy.ext.asyncio import AsyncSession

from src.infrastructure.outbound.database.loan_application_repository import SupabaseLoanApplicationRepository
from src.infrastructure.outbound.database.models import ApplicationModel
from src.domain.entities.loan_application import LoanApplication


class TestSupabaseLoanApplicationRepository:
    """Test SupabaseLoanApplicationRepository functionality"""
    
    def setup_method(self):
        """Setup test fixtures"""
        self.mock_db = AsyncMock(spec=AsyncSession)
        self.repository = SupabaseLoanApplicationRepository(self.mock_db)
        
        self.sample_application = LoanApplication(
            id=1,
            name="Juan Pérez García",
            cedula="12345678",
            convenio="EMPRESA_ABC",
            telefono="3001234567",
            fecha_nacimiento=date(1985, 6, 15),
            created_at=datetime(2024, 1, 15, 10, 30, 0)
        )
        
        self.sample_model = ApplicationModel(
            id=1,
            name="Juan Pérez García",
            cedula="12345678",
            convenio="EMPRESA_ABC",
            telefono="3001234567",
            fecha_nacimiento=date(1985, 6, 15),
            created_at=datetime(2024, 1, 15, 10, 30, 0)
        )


class TestModelEntityConversion(TestSupabaseLoanApplicationRepository):
    """Test model to entity conversion methods"""
    
    def test_model_to_entity_conversion(self):
        """Test converting database model to domain entity"""
        entity = self.repository._model_to_entity(self.sample_model)
        
        assert isinstance(entity, LoanApplication)
        assert entity.id == self.sample_model.id
        assert entity.name == self.sample_model.name
        assert entity.cedula == self.sample_model.cedula
    
    def test_entity_to_model_conversion(self):
        """Test converting domain entity to database model"""
        model = self.repository._entity_to_model(self.sample_application)
        
        assert isinstance(model, ApplicationModel)
        assert model.id == self.sample_application.id
        assert model.name == self.sample_application.name


class TestCreateApplication(TestSupabaseLoanApplicationRepository):
    """Test create application functionality"""
    
    @pytest.mark.asyncio
    async def test_create_application_success(self):
        """Test successful application creation"""
        new_application = LoanApplication(
            id=None,
            name="María González",
            cedula="87654321",
            convenio="EMPRESA_XYZ",
            telefono="3009876543",
            fecha_nacimiento=date(1990, 3, 20),
            created_at=None
        )
        
        created_model = ApplicationModel(
            id=2,
            name="María González",
            cedula="87654321",
            convenio="EMPRESA_XYZ",
            telefono="3009876543",
            fecha_nacimiento=date(1990, 3, 20),
            created_at=datetime.now()
        )
        
        self.mock_db.flush = AsyncMock()
        self.mock_db.refresh = AsyncMock()
        
        with patch.object(self.repository, '_entity_to_model') as mock_entity_to_model, \
             patch.object(self.repository, '_model_to_entity') as mock_model_to_entity:
            
            mock_entity_to_model.return_value = created_model
            mock_model_to_entity.return_value = LoanApplication(
                id=2,
                name="María González",
                cedula="87654321",
                convenio="EMPRESA_XYZ",
                telefono="3009876543",
                fecha_nacimiento=date(1990, 3, 20),
                created_at=datetime.now()
            )
            
            result = await self.repository.create(new_application)
            
            assert result.id == 2
            assert result.name == "María González"
            self.mock_db.add.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_create_application_database_error(self):
        """Test application creation with database error"""
        new_application = LoanApplication(
            id=None,
            name="Test User",
            cedula="12345678",
            convenio=None,
            telefono="3001234567",
            fecha_nacimiento=date(1990, 1, 1)
        )
        
        self.mock_db.add.side_effect = Exception("Database error")
        
        with pytest.raises(Exception) as exc_info:
            await self.repository.create(new_application)
        
        assert "Error creating loan application" in str(exc_info.value)


class TestGetApplication(TestSupabaseLoanApplicationRepository):
    """Test get application functionality"""
    
    @pytest.mark.asyncio
    async def test_get_by_id_success(self):
        """Test successful application retrieval by ID"""
        application_id = 1
        
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = self.sample_model
        self.mock_db.execute.return_value = mock_result
        
        result = await self.repository.get_by_id(application_id)
        
        assert result is not None
        assert isinstance(result, LoanApplication)
        assert result.id == application_id
        self.mock_db.execute.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_get_by_id_not_found(self):
        """Test application retrieval when ID not found"""
        application_id = 999
        
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = None
        self.mock_db.execute.return_value = mock_result
        
        result = await self.repository.get_by_id(application_id)
        
        assert result is None
        self.mock_db.execute.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_get_by_cedula_success(self):
        """Test successful application retrieval by cedula"""
        cedula = "12345678"
        
        mock_result = MagicMock()
        mock_result.scalars.return_value.all.return_value = [self.sample_model]
        self.mock_db.execute.return_value = mock_result
        
        result = await self.repository.get_by_cedula(cedula)
        
        assert len(result) == 1
        assert result[0].cedula == cedula
        self.mock_db.execute.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_get_all_success(self):
        """Test successful retrieval of all applications"""
        mock_result = MagicMock()
        mock_result.scalars.return_value.all.return_value = [self.sample_model]
        self.mock_db.execute.return_value = mock_result
        
        result = await self.repository.get_all(skip=0, limit=100)
        
        assert len(result) == 1
        assert isinstance(result[0], LoanApplication)
        self.mock_db.execute.assert_called_once()


class TestUpdateApplication(TestSupabaseLoanApplicationRepository):
    """Test update application functionality"""
    
    @pytest.mark.asyncio
    async def test_update_application_success(self):
        """Test successful application update"""
        updated_application = LoanApplication(
            id=1,
            name="Juan Pérez García Updated",
            cedula="12345678",
            convenio="NEW_EMPRESA",
            telefono="3005555555",
            fecha_nacimiento=date(1985, 6, 15),
            created_at=datetime(2024, 1, 15, 10, 30, 0)
        )
        
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = self.sample_model
        self.mock_db.execute.return_value = mock_result
        
        self.mock_db.flush = AsyncMock()
        self.mock_db.refresh = AsyncMock()
        
        with patch.object(self.repository, '_model_to_entity', return_value=updated_application):
            result = await self.repository.update(updated_application)
        
        assert result.name == "Juan Pérez García Updated"
        self.mock_db.execute.assert_called_once()
        self.mock_db.flush.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_update_application_not_found(self):
        """Test update when application not found"""
        non_existent_application = LoanApplication(
            id=999,
            name="Non Existent",
            cedula="99999999",
            convenio=None,
            telefono="3000000000",
            fecha_nacimiento=date(1990, 1, 1)
        )
        
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = None
        self.mock_db.execute.return_value = mock_result
        
        with pytest.raises(Exception) as exc_info:
            await self.repository.update(non_existent_application)
        
        assert "Error updating application" in str(exc_info.value)


class TestDeleteApplication(TestSupabaseLoanApplicationRepository):
    """Test delete application functionality"""
    
    @pytest.mark.asyncio
    async def test_delete_application_success(self):
        """Test successful application deletion"""
        application_id = 1
        
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = self.sample_model
        self.mock_db.execute.return_value = mock_result
        
        self.mock_db.delete = AsyncMock()
        self.mock_db.flush = AsyncMock()
        
        result = await self.repository.delete(application_id)
        
        assert result is True
        self.mock_db.execute.assert_called_once()
        self.mock_db.delete.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_delete_application_not_found(self):
        """Test delete when application not found"""
        application_id = 999
        
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = None
        self.mock_db.execute.return_value = mock_result
        
        result = await self.repository.delete(application_id)
        
        assert result is False
        self.mock_db.execute.assert_called_once()


class TestApplicationCounting(TestSupabaseLoanApplicationRepository):
    """Test application counting functionality"""
    
    @pytest.mark.asyncio
    async def test_count_total_success(self):
        """Test successful total count of applications"""
        expected_count = 42
        
        mock_result = MagicMock()
        mock_result.scalar.return_value = expected_count
        self.mock_db.execute.return_value = mock_result
        
        result = await self.repository.count_total()
        
        assert result == expected_count
        self.mock_db.execute.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_count_by_convenio_success(self):
        """Test successful count by convenio"""
        convenio = "EMPRESA_ABC"
        expected_count = 15
        
        mock_result = MagicMock()
        mock_result.scalar.return_value = expected_count
        self.mock_db.execute.return_value = mock_result
        
        result = await self.repository.count_by_convenio(convenio)
        
        assert result == expected_count
        self.mock_db.execute.assert_called_once()


class TestApplicationStatistics(TestSupabaseLoanApplicationRepository):
    """Test application statistics functionality"""
    
    @pytest.mark.asyncio
    async def test_get_statistics_success(self):
        """Test successful statistics retrieval"""
        total_count = 50
        
        total_result = MagicMock()
        total_result.scalar.return_value = total_count
        
        convenio_result = MagicMock()
        convenio_result.fetchall.return_value = [("EMPRESA_ABC", 20), (None, 15)]
        
        month_result = MagicMock()
        month_result.fetchall.return_value = [(datetime(2024, 1, 1), 10)]
        
        self.mock_db.execute.side_effect = [total_result, convenio_result, month_result]
        
        with patch.object(self.repository, 'count_total', return_value=total_count):
            result = await self.repository.get_statistics()
        
        assert result["total"] == total_count
        assert "by_convenio" in result
        assert "by_month" in result


class TestErrorHandling(TestSupabaseLoanApplicationRepository):
    """Test repository error handling"""
    
    @pytest.mark.asyncio
    async def test_get_by_id_database_error(self):
        """Test get by ID with database error"""
        application_id = 1
        self.mock_db.execute.side_effect = Exception("Database error")
        
        with pytest.raises(Exception) as exc_info:
            await self.repository.get_by_id(application_id)
        
        assert "Error getting application by ID" in str(exc_info.value)
    
    @pytest.mark.asyncio
    async def test_get_by_cedula_database_error(self):
        """Test get by cedula with database error"""
        cedula = "12345678"
        self.mock_db.execute.side_effect = Exception("Database error")
        
        with pytest.raises(Exception) as exc_info:
            await self.repository.get_by_cedula(cedula)
        
        assert "Error getting applications by cedula" in str(exc_info.value)
    
    @pytest.mark.asyncio
    async def test_search_by_name_success(self):
        """Test successful application search by name"""
        search_name = "Juan"
        
        mock_result = MagicMock()
        mock_result.scalars.return_value.all.return_value = [self.sample_model]
        self.mock_db.execute.return_value = mock_result
        
        result = await self.repository.search_by_name(search_name)
        
        assert len(result) == 1
        assert "Juan" in result[0].name
        self.mock_db.execute.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_get_by_convenio_success(self):
        """Test successful retrieval of applications by convenio"""
        convenio = "EMPRESA_ABC"
        
        mock_result = MagicMock()
        mock_result.scalars.return_value.all.return_value = [self.sample_model]
        self.mock_db.execute.return_value = mock_result
        
        result = await self.repository.get_by_convenio(convenio)
        
        assert len(result) == 1
        assert result[0].convenio == convenio
        self.mock_db.execute.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_get_by_date_range_success(self):
        """Test successful retrieval of applications by date range"""
        start_date = date(2024, 1, 1)
        end_date = date(2024, 12, 31)
        
        mock_result = MagicMock()
        mock_result.scalars.return_value.all.return_value = [self.sample_model]
        self.mock_db.execute.return_value = mock_result
        
        result = await self.repository.get_by_date_range(start_date, end_date)
        
        assert len(result) == 1
        assert isinstance(result[0], LoanApplication)
        self.mock_db.execute.assert_called_once()