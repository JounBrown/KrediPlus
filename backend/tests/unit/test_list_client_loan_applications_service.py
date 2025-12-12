"""Tests for ListClientLoanApplicationsService"""
import pytest
from datetime import date, datetime
from unittest.mock import AsyncMock
from src.application.services.list_client_loan_applications_service import ListClientLoanApplicationsService
from src.application.dtos.loan_application_dtos import ListClientLoanApplicationsRequest
from src.domain.entities.loan_application import LoanApplication


@pytest.fixture
def mock_repository():
    return AsyncMock()


@pytest.fixture
def service(mock_repository):
    return ListClientLoanApplicationsService(mock_repository)


@pytest.fixture
def sample_applications():
    return [
        LoanApplication(
            id=1,
            name="Juan Perez",
            cedula="12345678901",
            convenio="Convenio A",
            telefono="3001234567",
            fecha_nacimiento=date(1990, 5, 15),
            created_at=datetime(2024, 1, 1, 10, 0, 0)
        ),
        LoanApplication(
            id=2,
            name="Juan Perez",
            cedula="12345678901",
            convenio="Convenio B",
            telefono="3001234567",
            fecha_nacimiento=date(1990, 5, 15),
            created_at=datetime(2024, 2, 1, 10, 0, 0)
        ),
        LoanApplication(
            id=3,
            name="Juan Perez",
            cedula="12345678901",
            convenio="Convenio C",
            telefono="3001234567",
            fecha_nacimiento=date(1990, 5, 15),
            created_at=datetime(2024, 3, 1, 10, 0, 0)
        ),
    ]


class TestListClientLoanApplicationsServiceExecute:
    """Tests for ListClientLoanApplicationsService.execute"""

    async def test_execute_returns_applications(self, service, mock_repository, sample_applications):
        """Test successful listing of applications"""
        mock_repository.get_by_cedula.return_value = sample_applications
        request = ListClientLoanApplicationsRequest(cedula="12345678901", skip=0, limit=20)

        result = await service.execute(request)

        assert result.total == 3
        assert len(result.applications) == 3
        assert result.page == 1
        assert result.page_size == 20
        assert result.total_pages == 1

    async def test_execute_sorts_by_date_descending(self, service, mock_repository, sample_applications):
        """Test that applications are sorted by date (newest first)"""
        mock_repository.get_by_cedula.return_value = sample_applications
        request = ListClientLoanApplicationsRequest(cedula="12345678901", skip=0, limit=20)

        result = await service.execute(request)

        assert result.applications[0].id == 3  # March (newest)
        assert result.applications[1].id == 2  # February
        assert result.applications[2].id == 1  # January (oldest)

    async def test_execute_pagination_first_page(self, service, mock_repository, sample_applications):
        """Test pagination - first page"""
        mock_repository.get_by_cedula.return_value = sample_applications
        request = ListClientLoanApplicationsRequest(cedula="12345678901", skip=0, limit=2)

        result = await service.execute(request)

        assert len(result.applications) == 2
        assert result.total == 3
        assert result.page == 1
        assert result.total_pages == 2

    async def test_execute_pagination_second_page(self, service, mock_repository, sample_applications):
        """Test pagination - second page"""
        mock_repository.get_by_cedula.return_value = sample_applications
        request = ListClientLoanApplicationsRequest(cedula="12345678901", skip=2, limit=2)

        result = await service.execute(request)

        assert len(result.applications) == 1
        assert result.total == 3
        assert result.page == 2
        assert result.total_pages == 2

    async def test_execute_empty_results(self, service, mock_repository):
        """Test when no applications found"""
        mock_repository.get_by_cedula.return_value = []
        request = ListClientLoanApplicationsRequest(cedula="99999999999", skip=0, limit=20)

        result = await service.execute(request)

        assert result.total == 0
        assert len(result.applications) == 0
        assert result.page == 1
        assert result.total_pages == 1

    async def test_execute_repository_error(self, service, mock_repository):
        """Test handling of repository errors"""
        mock_repository.get_by_cedula.side_effect = Exception("Database error")
        request = ListClientLoanApplicationsRequest(cedula="12345678901", skip=0, limit=20)

        with pytest.raises(Exception) as exc_info:
            await service.execute(request)

        assert "Error al consultar las solicitudes" in str(exc_info.value)


class TestGetClientApplicationSummary:
    """Tests for ListClientLoanApplicationsService.get_client_application_summary"""

    async def test_summary_with_applications(self, service, mock_repository, sample_applications):
        """Test summary when client has applications"""
        mock_repository.get_by_cedula.return_value = sample_applications

        result = await service.get_client_application_summary("12345678901")

        assert result["total_applications"] == 3
        assert "latest_application_date" in result
        assert result["latest_application_date"] == datetime(2024, 3, 1, 10, 0, 0)

    async def test_summary_no_applications(self, service, mock_repository):
        """Test summary when client has no applications"""
        mock_repository.get_by_cedula.return_value = []

        result = await service.get_client_application_summary("99999999999")

        assert result["total_applications"] == 0
        assert result["has_pending"] is False
        assert result["has_approved"] is False
        assert result["latest_status"] is None
        assert result["total_requested"] == 0.0

    async def test_summary_repository_error(self, service, mock_repository):
        """Test handling of repository errors in summary"""
        mock_repository.get_by_cedula.side_effect = Exception("Database error")

        with pytest.raises(Exception) as exc_info:
            await service.get_client_application_summary("12345678901")

        assert "Error al obtener resumen de solicitudes" in str(exc_info.value)

    async def test_summary_single_application(self, service, mock_repository):
        """Test summary with single application"""
        single_app = [
            LoanApplication(
                id=1,
                name="Juan Perez",
                cedula="12345678901",
                convenio="Convenio A",
                telefono="3001234567",
                fecha_nacimiento=date(1990, 5, 15),
                created_at=datetime(2024, 1, 1, 10, 0, 0)
            )
        ]
        mock_repository.get_by_cedula.return_value = single_app

        result = await service.get_client_application_summary("12345678901")

        assert result["total_applications"] == 1
        assert result["latest_application_date"] == datetime(2024, 1, 1, 10, 0, 0)
