"""
Unit tests for Loan Application Service
"""
import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from datetime import datetime, date

from src.application.services.loan_application_service import LoanApplicationService
from src.domain.entities.loan_application import LoanApplication
from src.application.dtos.loan_application_dtos import (
    CreateLoanApplicationRequest,
    UpdateLoanApplicationRequest,
    ListClientLoanApplicationsRequest
)


class TestLoanApplicationService:
    """Test LoanApplicationService functionality"""
    
    def setup_method(self):
        """Setup test fixtures"""
        self.mock_repository = MagicMock()
        self.service = LoanApplicationService(self.mock_repository)
        
        self.sample_application = LoanApplication(
            id=1,
            name="Juan Pérez",
            cedula="1234567890",
            convenio="Empresa ABC",
            telefono="3001234567",
            fecha_nacimiento=date(1990, 5, 15),
            created_at=datetime.now()
        )


class TestUpdateApplication(TestLoanApplicationService):
    """Test update_application method"""
    
    @pytest.mark.asyncio
    async def test_update_application_success(self):
        """Test successful application update"""
        request = UpdateLoanApplicationRequest(
            name="Juan Carlos Pérez",
            telefono="3009876543"
        )
        
        updated_app = LoanApplication(
            id=1,
            name="Juan Carlos Pérez",
            cedula="1234567890",
            convenio="Empresa ABC",
            telefono="3009876543",
            fecha_nacimiento=date(1990, 5, 15),
            created_at=datetime.now()
        )
        
        self.mock_repository.get_by_id = AsyncMock(return_value=self.sample_application)
        self.mock_repository.update = AsyncMock(return_value=updated_app)
        
        result = await self.service.update_application(1, request)
        
        assert result.name == "Juan Carlos Pérez"
        assert result.telefono == "3009876543"
    
    @pytest.mark.asyncio
    async def test_update_application_not_found(self):
        """Test update when application not found"""
        request = UpdateLoanApplicationRequest(name="Nuevo Nombre")
        
        self.mock_repository.get_by_id = AsyncMock(return_value=None)
        
        with pytest.raises(Exception) as exc_info:
            await self.service.update_application(999, request)
        
        assert "no encontrada" in str(exc_info.value)
    
    @pytest.mark.asyncio
    async def test_update_application_convenio(self):
        """Test updating convenio field"""
        request = UpdateLoanApplicationRequest(convenio="Nueva Empresa XYZ")
        
        updated_app = LoanApplication(
            id=1,
            name="Juan Pérez",
            cedula="1234567890",
            convenio="Nueva Empresa XYZ",
            telefono="3001234567",
            fecha_nacimiento=date(1990, 5, 15),
            created_at=datetime.now()
        )
        
        self.mock_repository.get_by_id = AsyncMock(return_value=self.sample_application)
        self.mock_repository.update = AsyncMock(return_value=updated_app)
        
        result = await self.service.update_application(1, request)
        
        assert result.convenio == "Nueva Empresa XYZ"
    
    @pytest.mark.asyncio
    async def test_update_application_fecha_nacimiento(self):
        """Test updating birth date"""
        new_date = date(1985, 3, 20)
        request = UpdateLoanApplicationRequest(fecha_nacimiento=new_date)
        
        updated_app = LoanApplication(
            id=1,
            name="Juan Pérez",
            cedula="1234567890",
            convenio="Empresa ABC",
            telefono="3001234567",
            fecha_nacimiento=new_date,
            created_at=datetime.now()
        )
        
        self.mock_repository.get_by_id = AsyncMock(return_value=self.sample_application)
        self.mock_repository.update = AsyncMock(return_value=updated_app)
        
        result = await self.service.update_application(1, request)
        
        assert result.fecha_nacimiento == new_date
    
    @pytest.mark.asyncio
    async def test_update_application_repository_error(self):
        """Test update with repository error"""
        request = UpdateLoanApplicationRequest(name="Nuevo Nombre")
        
        self.mock_repository.get_by_id = AsyncMock(return_value=self.sample_application)
        self.mock_repository.update = AsyncMock(side_effect=Exception("Database error"))
        
        with pytest.raises(Exception) as exc_info:
            await self.service.update_application(1, request)
        
        assert "Error al actualizar solicitud" in str(exc_info.value)


class TestGetApplicationById(TestLoanApplicationService):
    """Test get_application_by_id method"""
    
    @pytest.mark.asyncio
    async def test_get_application_by_id_success(self):
        """Test successful application retrieval"""
        self.mock_repository.get_by_id = AsyncMock(return_value=self.sample_application)
        
        result = await self.service.get_application_by_id(1)
        
        assert result is not None
        assert result.id == 1
        assert result.name == "Juan Pérez"
        assert result.cedula == "1234567890"
    
    @pytest.mark.asyncio
    async def test_get_application_by_id_not_found(self):
        """Test retrieval when application not found"""
        self.mock_repository.get_by_id = AsyncMock(return_value=None)
        
        result = await self.service.get_application_by_id(999)
        
        assert result is None


class TestListAllApplications(TestLoanApplicationService):
    """Test list_all_applications method"""
    
    @pytest.mark.asyncio
    async def test_list_all_applications_success(self):
        """Test listing all applications"""
        applications = [
            self.sample_application,
            LoanApplication(
                id=2,
                name="María García",
                cedula="0987654321",
                convenio="Empresa XYZ",
                telefono="3109876543",
                fecha_nacimiento=date(1988, 8, 20),
                created_at=datetime.now()
            )
        ]
        
        self.mock_repository.get_all = AsyncMock(return_value=applications)
        self.mock_repository.count_total = AsyncMock(return_value=2)
        
        result = await self.service.list_all_applications()
        
        assert result.total == 2
        assert len(result.applications) == 2
        assert result.page == 1
    
    @pytest.mark.asyncio
    async def test_list_all_applications_with_convenio_filter(self):
        """Test listing applications with convenio filter"""
        filtered_apps = [self.sample_application]
        
        self.mock_repository.get_by_convenio = AsyncMock(return_value=filtered_apps)
        self.mock_repository.count_by_convenio = AsyncMock(return_value=1)
        
        result = await self.service.list_all_applications(convenio_filter="Empresa ABC")
        
        assert result.total == 1
        assert len(result.applications) == 1
        self.mock_repository.get_by_convenio.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_list_all_applications_with_pagination(self):
        """Test listing applications with pagination"""
        applications = [self.sample_application]
        
        self.mock_repository.get_all = AsyncMock(return_value=applications)
        self.mock_repository.count_total = AsyncMock(return_value=50)
        
        result = await self.service.list_all_applications(skip=20, limit=10)
        
        assert result.total == 50
        assert result.page == 3  # skip=20, limit=10 -> page 3
        assert result.total_pages == 5
    
    @pytest.mark.asyncio
    async def test_list_all_applications_empty(self):
        """Test listing when no applications exist"""
        self.mock_repository.get_all = AsyncMock(return_value=[])
        self.mock_repository.count_total = AsyncMock(return_value=0)
        
        result = await self.service.list_all_applications()
        
        assert result.total == 0
        assert len(result.applications) == 0
        assert result.total_pages == 1
    
    @pytest.mark.asyncio
    async def test_list_all_applications_repository_error(self):
        """Test listing with repository error"""
        self.mock_repository.get_all = AsyncMock(side_effect=Exception("Database error"))
        
        with pytest.raises(Exception) as exc_info:
            await self.service.list_all_applications()
        
        assert "Error al listar solicitudes" in str(exc_info.value)


class TestGetApplicationStatistics(TestLoanApplicationService):
    """Test get_application_statistics method"""
    
    @pytest.mark.asyncio
    async def test_get_application_statistics_success(self):
        """Test successful statistics retrieval"""
        stats = {
            'total': 100,
            'by_convenio': {'Empresa ABC': 50, 'Empresa XYZ': 50},
            'by_month': {'2024-01': 30, '2024-02': 70}
        }
        
        self.mock_repository.get_statistics = AsyncMock(return_value=stats)
        
        result = await self.service.get_application_statistics()
        
        assert result.total_applications == 100
        assert result.applications_by_convenio == {'Empresa ABC': 50, 'Empresa XYZ': 50}
    
    @pytest.mark.asyncio
    async def test_get_application_statistics_empty(self):
        """Test statistics when no data"""
        stats = {}
        
        self.mock_repository.get_statistics = AsyncMock(return_value=stats)
        
        result = await self.service.get_application_statistics()
        
        assert result.total_applications == 0
        assert result.applications_by_convenio == {}
    
    @pytest.mark.asyncio
    async def test_get_application_statistics_repository_error(self):
        """Test statistics with repository error"""
        self.mock_repository.get_statistics = AsyncMock(side_effect=Exception("Database error"))
        
        with pytest.raises(Exception) as exc_info:
            await self.service.get_application_statistics()
        
        assert "Error al obtener estadísticas" in str(exc_info.value)


class TestSearchApplicationsByName(TestLoanApplicationService):
    """Test search_applications_by_name method"""
    
    @pytest.mark.asyncio
    async def test_search_applications_by_name_success(self):
        """Test successful name search"""
        matching_apps = [self.sample_application]
        
        self.mock_repository.search_by_name = AsyncMock(return_value=matching_apps)
        
        result = await self.service.search_applications_by_name("Juan")
        
        assert result.total == 1
        assert len(result.applications) == 1
        assert result.applications[0].name == "Juan Pérez"
    
    @pytest.mark.asyncio
    async def test_search_applications_by_name_no_results(self):
        """Test search with no matching results"""
        self.mock_repository.search_by_name = AsyncMock(return_value=[])
        
        result = await self.service.search_applications_by_name("NoExiste")
        
        assert result.total == 0
        assert len(result.applications) == 0
    
    @pytest.mark.asyncio
    async def test_search_applications_by_name_with_pagination(self):
        """Test search with pagination"""
        apps = [self.sample_application]
        all_matching = [self.sample_application] * 25  # 25 total matches
        
        self.mock_repository.search_by_name = AsyncMock(side_effect=[apps, all_matching])
        
        result = await self.service.search_applications_by_name("Juan", skip=0, limit=10)
        
        assert result.total == 25
        assert result.total_pages == 3
    
    @pytest.mark.asyncio
    async def test_search_applications_by_name_repository_error(self):
        """Test search with repository error"""
        self.mock_repository.search_by_name = AsyncMock(side_effect=Exception("Database error"))
        
        with pytest.raises(Exception) as exc_info:
            await self.service.search_applications_by_name("Juan")
        
        assert "Error al buscar solicitudes" in str(exc_info.value)
