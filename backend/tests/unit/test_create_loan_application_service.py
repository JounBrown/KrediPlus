"""Tests for CreateLoanApplicationService"""
import pytest
from datetime import date, datetime
from unittest.mock import AsyncMock, MagicMock
from src.application.services.create_loan_application_service import CreateLoanApplicationService
from src.application.dtos.loan_application_dtos import CreateLoanApplicationRequest
from src.domain.entities.loan_application import LoanApplication


@pytest.fixture
def mock_repository():
    return AsyncMock()


@pytest.fixture
def service(mock_repository):
    return CreateLoanApplicationService(mock_repository)


@pytest.fixture
def valid_request():
    return CreateLoanApplicationRequest(
        name="Juan Perez",
        cedula="12345678901",
        convenio="Convenio Test",
        telefono="3001234567",
        fecha_nacimiento=date(1990, 5, 15)
    )


@pytest.fixture
def created_application():
    return LoanApplication(
        id=1,
        name="Juan Perez",
        cedula="12345678901",
        convenio="Convenio Test",
        telefono="3001234567",
        fecha_nacimiento=date(1990, 5, 15),
        created_at=datetime(2024, 1, 1, 10, 0, 0)
    )


class TestCreateLoanApplicationService:
    """Tests for CreateLoanApplicationService.execute"""

    async def test_execute_success(self, service, mock_repository, valid_request, created_application):
        """Test successful loan application creation"""
        mock_repository.get_by_cedula.return_value = []
        mock_repository.create.return_value = created_application

        result = await service.execute(valid_request)

        assert result.id == 1
        assert result.name == "Juan Perez"
        assert result.cedula == "12345678901"
        assert result.convenio == "Convenio Test"
        assert result.telefono == "3001234567"
        mock_repository.create.assert_called_once()

    async def test_execute_with_existing_applications(self, service, mock_repository, valid_request, created_application):
        """Test creation when client has existing applications"""
        existing = LoanApplication(
            id=99,
            name="Juan Perez",
            cedula="12345678901",
            convenio="Old Convenio",
            telefono="3001234567",
            fecha_nacimiento=date(1990, 5, 15),
            created_at=datetime(2023, 1, 1)
        )
        mock_repository.get_by_cedula.return_value = [existing]
        mock_repository.create.return_value = created_application

        result = await service.execute(valid_request)

        assert result.id == 1
        mock_repository.create.assert_called_once()

    async def test_execute_without_convenio(self, service, mock_repository, created_application):
        """Test creation without convenio"""
        request = CreateLoanApplicationRequest(
            name="Maria Lopez",
            cedula="98765432101",
            convenio=None,
            telefono="3109876543",
            fecha_nacimiento=date(1985, 3, 20)
        )
        created_app_no_convenio = LoanApplication(
            id=2,
            name="Maria Lopez",
            cedula="98765432101",
            convenio=None,
            telefono="3109876543",
            fecha_nacimiento=date(1985, 3, 20),
            created_at=datetime(2024, 1, 1)
        )
        mock_repository.get_by_cedula.return_value = []
        mock_repository.create.return_value = created_app_no_convenio

        result = await service.execute(request)

        assert result.id == 2
        assert result.convenio is None

    async def test_execute_strips_whitespace(self, service, mock_repository, created_application):
        """Test that whitespace is stripped from input"""
        request = CreateLoanApplicationRequest(
            name="  Juan Perez  ",
            cedula="  12345678901  ",
            convenio="  Convenio Test  ",
            telefono="  3001234567  ",
            fecha_nacimiento=date(1990, 5, 15)
        )
        mock_repository.get_by_cedula.return_value = []
        mock_repository.create.return_value = created_application

        await service.execute(request)

        call_args = mock_repository.create.call_args[0][0]
        assert call_args.name == "Juan Perez"
        assert call_args.cedula == "12345678901"
        assert call_args.convenio == "Convenio Test"
        assert call_args.telefono == "3001234567"

    async def test_execute_repository_error(self, service, mock_repository, valid_request):
        """Test handling of repository errors"""
        mock_repository.get_by_cedula.return_value = []
        mock_repository.create.side_effect = Exception("Database error")

        with pytest.raises(Exception) as exc_info:
            await service.execute(valid_request)

        assert "Error al crear la solicitud" in str(exc_info.value)

    async def test_execute_invalid_data(self, service, mock_repository, valid_request):
        """Test handling of invalid application data"""
        mock_repository.get_by_cedula.return_value = []
        
        # Mock the entity to return invalid validation
        with pytest.raises(ValueError) as exc_info:
            invalid_request = CreateLoanApplicationRequest(
                name="",  # Empty name should fail
                cedula="12345678901",
                convenio=None,
                telefono="3001234567",
                fecha_nacimiento=date(1990, 5, 15)
            )
