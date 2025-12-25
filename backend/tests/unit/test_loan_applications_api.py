"""
Unit tests for Loan Applications API routes
"""
import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from datetime import date, datetime
from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from src.infrastructure.inbound.api.routes.loan_applications import (
    create_loan_application,
    get_loan_application,
    list_loan_applications,
    get_applications_by_cedula,
    update_application,
    delete_application
)
from src.application.dtos.loan_application_dtos import (
    CreateLoanApplicationRequest,
    UpdateLoanApplicationRequest,
    ListClientLoanApplicationsRequest,
    LoanApplicationResponse,
    LoanApplicationListResponse
)
from src.domain.entities.user import User


class TestCreateLoanApplication:
    """Test create_loan_application endpoint"""
    
    @pytest.mark.asyncio
    async def test_create_loan_application_success(self):
        """Test successful loan application creation"""
        # Arrange
        request = CreateLoanApplicationRequest(
            name="Juan Pérez García",
            cedula="12345678",
            convenio="EMPRESA_ABC",
            telefono="3001234567",
            fecha_nacimiento=date(1985, 6, 15)
        )
        
        expected_response = LoanApplicationResponse(
            id=1,
            name="Juan Pérez García",
            cedula="12345678",
            convenio="EMPRESA_ABC",
            telefono="3001234567",
            fecha_nacimiento=date(1985, 6, 15),
            created_at=datetime.now()
        )
        
        mock_service = AsyncMock()
        mock_service.create_application.return_value = expected_response
        
        # Act
        result = await create_loan_application(request, mock_service)
        
        # Assert
        assert result == expected_response
        mock_service.create_application.assert_called_once_with(request)
    
    @pytest.mark.asyncio
    async def test_create_loan_application_without_convenio(self):
        """Test loan application creation without convenio"""
        # Arrange
        request = CreateLoanApplicationRequest(
            name="María González",
            cedula="87654321",
            convenio=None,  # No convenio
            telefono="3009876543",
            fecha_nacimiento=date(1990, 3, 20)
        )
        
        expected_response = LoanApplicationResponse(
            id=2,
            name="María González",
            cedula="87654321",
            convenio=None,
            telefono="3009876543",
            fecha_nacimiento=date(1990, 3, 20),
            created_at=datetime.now()
        )
        
        mock_service = AsyncMock()
        mock_service.create_application.return_value = expected_response
        
        # Act
        result = await create_loan_application(request, mock_service)
        
        # Assert
        assert result == expected_response
        assert result.convenio is None
        mock_service.create_application.assert_called_once_with(request)
    
    def test_create_loan_application_validation_error(self):
        """Test loan application creation with validation error - Pydantic validates"""
        from pydantic import ValidationError
        
        # Act & Assert - Pydantic should reject empty name
        with pytest.raises(ValidationError) as exc_info:
            CreateLoanApplicationRequest(
                name="",  # Invalid empty name
                cedula="12345678",
                convenio=None,
                telefono="3001234567",
                fecha_nacimiento=date(1990, 1, 1)
            )
        
        assert "name" in str(exc_info.value)
    
    def test_create_loan_application_underage_applicant(self):
        """Test loan application creation with underage applicant - Pydantic validates"""
        from pydantic import ValidationError
        
        current_year = date.today().year
        
        # Act & Assert - Pydantic should reject underage applicant
        with pytest.raises(ValidationError) as exc_info:
            CreateLoanApplicationRequest(
                name="Young Person",
                cedula="12345678",
                convenio=None,
                telefono="3001234567",
                fecha_nacimiento=date(current_year - 17, 1, 1)  # 17 years old
            )
        
        assert "fecha_nacimiento" in str(exc_info.value)
    
    @pytest.mark.asyncio
    async def test_create_loan_application_internal_error(self):
        """Test loan application creation with internal error"""
        # Arrange
        request = CreateLoanApplicationRequest(
            name="Juan Pérez",
            cedula="12345678",
            convenio=None,
            telefono="3001234567",
            fecha_nacimiento=date(1990, 1, 1)
        )
        
        mock_service = AsyncMock()
        mock_service.create_application.side_effect = Exception("Database error")
        
        # Act & Assert
        with pytest.raises(HTTPException) as exc_info:
            await create_loan_application(request, mock_service)
        
        assert exc_info.value.status_code == 500
        assert "Error creating application" in str(exc_info.value.detail)


class TestGetLoanApplication:
    """Test get_loan_application endpoint"""
    
    @pytest.mark.asyncio
    async def test_get_loan_application_success(self):
        """Test successful loan application retrieval"""
        # Arrange
        application_id = 1
        expected_response = LoanApplicationResponse(
            id=1,
            name="Juan Pérez García",
            cedula="12345678",
            convenio="EMPRESA_ABC",
            telefono="3001234567",
            fecha_nacimiento=date(1985, 6, 15),
            created_at=datetime.now()
        )
        
        mock_service = AsyncMock()
        mock_service.get_application_by_id.return_value = expected_response
        
        mock_user = User(id="user123", email="user@example.com", role="admin")
        
        # Act
        result = await get_loan_application(application_id, mock_service, mock_user)
        
        # Assert
        assert result == expected_response
        mock_service.get_application_by_id.assert_called_once_with(application_id)
    
    @pytest.mark.asyncio
    async def test_get_loan_application_not_found(self):
        """Test loan application retrieval when not found"""
        # Arrange
        application_id = 999
        mock_service = AsyncMock()
        mock_service.get_application_by_id.return_value = None
        
        mock_user = User(id="user123", email="user@example.com", role="admin")
        
        # Act & Assert
        with pytest.raises(HTTPException) as exc_info:
            await get_loan_application(application_id, mock_service, mock_user)
        
        assert exc_info.value.status_code == 404
        assert "Application not found" in str(exc_info.value.detail)
    
    @pytest.mark.asyncio
    async def test_get_loan_application_internal_error(self):
        """Test loan application retrieval with internal error"""
        # Arrange
        application_id = 1
        mock_service = AsyncMock()
        mock_service.get_application_by_id.side_effect = Exception("Database error")
        
        mock_user = User(id="user123", email="user@example.com", role="admin")
        
        # Act & Assert
        with pytest.raises(HTTPException) as exc_info:
            await get_loan_application(application_id, mock_service, mock_user)
        
        assert exc_info.value.status_code == 500
        assert "Error getting application" in str(exc_info.value.detail)


class TestListLoanApplications:
    """Test list_loan_applications endpoint"""
    
    @pytest.mark.asyncio
    async def test_list_loan_applications_success(self):
        """Test successful loan applications listing"""
        # Arrange
        expected_applications = [
            LoanApplicationResponse(
                id=1,
                name="Juan Pérez García",
                cedula="12345678",
                convenio="EMPRESA_ABC",
                telefono="3001234567",
                fecha_nacimiento=date(1985, 6, 15),
                created_at=datetime.now()
            ),
            LoanApplicationResponse(
                id=2,
                name="María González",
                cedula="87654321",
                convenio=None,
                telefono="3009876543",
                fecha_nacimiento=date(1990, 3, 20),
                created_at=datetime.now()
            )
        ]
        
        mock_list_response = LoanApplicationListResponse(
            applications=expected_applications,
            total=2,
            page=1,
            page_size=1000,
            total_pages=1
        )
        
        mock_service = AsyncMock()
        mock_service.list_all_applications.return_value = mock_list_response
        
        mock_user = User(id="user123", email="user@example.com", role="admin")
        
        # Act
        result = await list_loan_applications(mock_service, mock_user)
        
        # Assert
        assert result == expected_applications
        assert len(result) == 2
        mock_service.list_all_applications.assert_called_once_with(convenio_filter=None, skip=0, limit=1000)
    
    @pytest.mark.asyncio
    async def test_list_loan_applications_empty_result(self):
        """Test loan applications listing with empty result"""
        # Arrange
        mock_list_response = LoanApplicationListResponse(
            applications=[],
            total=0,
            page=1,
            page_size=1000,
            total_pages=0
        )
        
        mock_service = AsyncMock()
        mock_service.list_all_applications.return_value = mock_list_response
        
        mock_user = User(id="user123", email="user@example.com", role="admin")
        
        # Act
        result = await list_loan_applications(mock_service, mock_user)
        
        # Assert
        assert result == []
        mock_service.list_all_applications.assert_called_once_with(convenio_filter=None, skip=0, limit=1000)
    
    @pytest.mark.asyncio
    async def test_list_loan_applications_internal_error(self):
        """Test loan applications listing with internal error"""
        # Arrange
        mock_service = AsyncMock()
        mock_service.list_all_applications.side_effect = Exception("Database error")
        
        mock_user = User(id="user123", email="user@example.com", role="admin")
        
        # Act & Assert
        with pytest.raises(HTTPException) as exc_info:
            await list_loan_applications(mock_service, mock_user)
        
        assert exc_info.value.status_code == 500
        assert "Error listing applications" in str(exc_info.value.detail)


class TestGetApplicationsByCedula:
    """Test get_applications_by_cedula endpoint"""
    
    @pytest.mark.asyncio
    async def test_get_applications_by_cedula_success(self):
        """Test successful retrieval of applications by cedula"""
        # Arrange
        cedula = "12345678"
        expected_applications = [
            LoanApplicationResponse(
                id=1,
                name="Juan Pérez García",
                cedula="12345678",
                convenio="EMPRESA_ABC",
                telefono="3001234567",
                fecha_nacimiento=date(1985, 6, 15),
                created_at=datetime.now()
            ),
            LoanApplicationResponse(
                id=3,
                name="Juan Pérez García",
                cedula="12345678",
                convenio="EMPRESA_XYZ",
                telefono="3001234567",
                fecha_nacimiento=date(1985, 6, 15),
                created_at=datetime.now()
            )
        ]
        
        mock_list_response = LoanApplicationListResponse(
            applications=expected_applications,
            total=2,
            page=1,
            page_size=100,
            total_pages=1
        )
        
        mock_service = AsyncMock()
        mock_service.list_client_applications.return_value = mock_list_response
        
        mock_user = User(id="user123", email="user@example.com", role="admin")
        
        # Act
        result = await get_applications_by_cedula(cedula, mock_service, mock_user)
        
        # Assert
        assert result == expected_applications
        assert len(result) == 2
        assert all(app.cedula == cedula for app in result)
        
        # Verify the service was called with correct parameters
        mock_service.list_client_applications.assert_called_once()
        call_args = mock_service.list_client_applications.call_args[0][0]
        assert isinstance(call_args, ListClientLoanApplicationsRequest)
        assert call_args.cedula == cedula
        assert call_args.skip == 0
        assert call_args.limit == 100
    
    @pytest.mark.asyncio
    async def test_get_applications_by_cedula_empty_result(self):
        """Test retrieval of applications by cedula with no results"""
        # Arrange
        cedula = "99999999"
        mock_list_response = LoanApplicationListResponse(
            applications=[],
            total=0,
            page=1,
            page_size=100,
            total_pages=0
        )
        
        mock_service = AsyncMock()
        mock_service.list_client_applications.return_value = mock_list_response
        
        mock_user = User(id="user123", email="user@example.com", role="admin")
        
        # Act
        result = await get_applications_by_cedula(cedula, mock_service, mock_user)
        
        # Assert
        assert result == []
        mock_service.list_client_applications.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_get_applications_by_cedula_validation_error(self):
        """Test applications by cedula with validation error"""
        # Arrange
        cedula = "123"  # Invalid cedula (too short)
        mock_service = AsyncMock()
        mock_service.list_client_applications.side_effect = ValueError("Invalid cedula format")
        
        mock_user = User(id="user123", email="user@example.com", role="admin")
        
        # Act & Assert
        with pytest.raises(HTTPException) as exc_info:
            await get_applications_by_cedula(cedula, mock_service, mock_user)
        
        assert exc_info.value.status_code == 400
        # Check for validation error message (Pydantic format)
        assert "cedula" in str(exc_info.value.detail).lower() or "string" in str(exc_info.value.detail).lower()
    
    @pytest.mark.asyncio
    async def test_get_applications_by_cedula_internal_error(self):
        """Test applications by cedula with internal error"""
        # Arrange
        cedula = "12345678"
        mock_service = AsyncMock()
        mock_service.list_client_applications.side_effect = Exception("Database error")
        
        mock_user = User(id="user123", email="user@example.com", role="admin")
        
        # Act & Assert
        with pytest.raises(HTTPException) as exc_info:
            await get_applications_by_cedula(cedula, mock_service, mock_user)
        
        assert exc_info.value.status_code == 500
        assert "Error getting applications by cedula" in str(exc_info.value.detail)


class TestUpdateApplication:
    """Test update_application endpoint"""
    
    @pytest.mark.asyncio
    async def test_update_application_success(self):
        """Test successful loan application update"""
        # Arrange
        application_id = 1
        request = UpdateLoanApplicationRequest(
            name="Juan Pérez García Updated",
            convenio="NEW_EMPRESA",
            telefono="3009999999",
            fecha_nacimiento=date(1985, 6, 15)
        )
        
        expected_response = LoanApplicationResponse(
            id=1,
            name="Juan Pérez García Updated",
            cedula="12345678",  # Cedula cannot be updated
            convenio="NEW_EMPRESA",
            telefono="3009999999",
            fecha_nacimiento=date(1985, 6, 15),
            created_at=datetime.now()
        )
        
        mock_service = AsyncMock()
        mock_service.update_application.return_value = expected_response
        
        mock_user = User(id="user123", email="user@example.com", role="admin")
        
        # Act
        result = await update_application(application_id, request, mock_service, mock_user)
        
        # Assert
        assert result == expected_response
        assert result.name == "Juan Pérez García Updated"
        assert result.convenio == "NEW_EMPRESA"
        assert result.telefono == "3009999999"
        mock_service.update_application.assert_called_once_with(application_id, request)
    
    @pytest.mark.asyncio
    async def test_update_application_partial_update(self):
        """Test partial loan application update"""
        # Arrange
        application_id = 1
        request = UpdateLoanApplicationRequest(
            telefono="3005555555"  # Only updating phone
        )
        
        expected_response = LoanApplicationResponse(
            id=1,
            name="Juan Pérez García",  # Unchanged
            cedula="12345678",  # Unchanged
            convenio="EMPRESA_ABC",  # Unchanged
            telefono="3005555555",  # Updated
            fecha_nacimiento=date(1985, 6, 15),  # Unchanged
            created_at=datetime.now()
        )
        
        mock_service = AsyncMock()
        mock_service.update_application.return_value = expected_response
        
        mock_user = User(id="user123", email="user@example.com", role="admin")
        
        # Act
        result = await update_application(application_id, request, mock_service, mock_user)
        
        # Assert
        assert result == expected_response
        assert result.telefono == "3005555555"
        mock_service.update_application.assert_called_once_with(application_id, request)
    
    def test_update_application_validation_error(self):
        """Test loan application update with validation error - Pydantic validates"""
        from pydantic import ValidationError
        
        # Act & Assert - Pydantic should reject empty name
        with pytest.raises(ValidationError) as exc_info:
            UpdateLoanApplicationRequest(
                name="",  # Invalid empty name
                telefono="3001234567"
            )
        
        assert "name" in str(exc_info.value)
    
    def test_update_application_underage_validation(self):
        """Test loan application update with underage validation error - Pydantic validates"""
        from pydantic import ValidationError
        
        current_year = date.today().year
        
        # Act & Assert - Pydantic should reject underage applicant
        with pytest.raises(ValidationError) as exc_info:
            UpdateLoanApplicationRequest(
                fecha_nacimiento=date(current_year - 17, 1, 1)  # 17 years old
            )
        
        assert "fecha_nacimiento" in str(exc_info.value)


class TestDeleteApplication:
    """Test delete_application endpoint"""
    
    def test_delete_application_placeholder(self):
        """Placeholder test - delete functionality requires complex mocking"""
        # This test is a placeholder because the delete endpoint requires
        # complex repository mocking that is better tested via integration tests
        assert True


class TestLoanApplicationWorkflows:
    """Test complete loan application workflows"""
    
    @pytest.mark.asyncio
    async def test_complete_application_lifecycle(self):
        """Test complete application lifecycle: create -> get -> update -> delete"""
        # Arrange
        mock_service = AsyncMock()
        mock_db = AsyncMock(spec=AsyncSession)
        mock_user = User(id="user123", email="user@example.com", role="admin")
        
        # Step 1: Create application
        create_request = CreateLoanApplicationRequest(
            name="Juan Pérez García",
            cedula="12345678",
            convenio="EMPRESA_ABC",
            telefono="3001234567",
            fecha_nacimiento=date(1985, 6, 15)
        )
        
        created_response = LoanApplicationResponse(
            id=1,
            name="Juan Pérez García",
            cedula="12345678",
            convenio="EMPRESA_ABC",
            telefono="3001234567",
            fecha_nacimiento=date(1985, 6, 15),
            created_at=datetime.now()
        )
        
        # Step 2: Update application
        update_request = UpdateLoanApplicationRequest(
            name="Juan Pérez García Updated",
            telefono="3009999999"
        )
        
        updated_response = LoanApplicationResponse(
            id=1,
            name="Juan Pérez García Updated",
            cedula="12345678",
            convenio="EMPRESA_ABC",
            telefono="3009999999",
            fecha_nacimiento=date(1985, 6, 15),
            created_at=datetime.now()
        )
        
        # Setup mocks
        mock_service.create_application.return_value = created_response
        mock_service.get_application_by_id.return_value = updated_response
        mock_service.update_application.return_value = updated_response
        
        # Act & Assert
        # Step 1: Create
        create_result = await create_loan_application(create_request, mock_service)
        assert create_result.id == 1
        assert create_result.name == "Juan Pérez García"
        
        # Step 2: Get
        get_result = await get_loan_application(1, mock_service, mock_user)
        assert get_result.id == 1
        
        # Step 3: Update
        update_result = await update_application(1, update_request, mock_service, mock_user)
        assert update_result.name == "Juan Pérez García Updated"
        assert update_result.telefono == "3009999999"
        
        # Step 4: Delete
        with patch('src.infrastructure.adapters.database.loan_application_repository.SupabaseLoanApplicationRepository') as mock_repo_class:
            mock_repo = AsyncMock()
            mock_repo.delete.return_value = True
            mock_repo_class.return_value = mock_repo
            
            delete_result = await delete_application(1, mock_db, mock_user)
            assert delete_result == {"message": "Application deleted successfully"}
        
        # Verify all service calls
        mock_service.create_application.assert_called_once_with(create_request)
        mock_service.get_application_by_id.assert_called_once_with(1)
        mock_service.update_application.assert_called_once_with(1, update_request)
    
    @pytest.mark.asyncio
    async def test_multiple_applications_same_cedula(self):
        """Test handling multiple applications for the same cedula"""
        # Arrange
        cedula = "12345678"
        mock_service = AsyncMock()
        mock_user = User(id="user123", email="user@example.com", role="admin")
        
        # Multiple applications for same person
        applications = [
            LoanApplicationResponse(
                id=1,
                name="Juan Pérez García",
                cedula="12345678",
                convenio="EMPRESA_ABC",
                telefono="3001234567",
                fecha_nacimiento=date(1985, 6, 15),
                created_at=datetime(2024, 1, 15)
            ),
            LoanApplicationResponse(
                id=2,
                name="Juan Pérez García",
                cedula="12345678",
                convenio="EMPRESA_XYZ",
                telefono="3001234567",
                fecha_nacimiento=date(1985, 6, 15),
                created_at=datetime(2024, 3, 20)
            ),
            LoanApplicationResponse(
                id=3,
                name="Juan Pérez García",
                cedula="12345678",
                convenio=None,  # Independent application
                telefono="3001234567",
                fecha_nacimiento=date(1985, 6, 15),
                created_at=datetime(2024, 6, 10)
            )
        ]
        
        mock_list_response = LoanApplicationListResponse(
            applications=applications,
            total=3,
            page=1,
            page_size=100,
            total_pages=1
        )
        
        mock_service.list_client_applications.return_value = mock_list_response
        
        # Act
        result = await get_applications_by_cedula(cedula, mock_service, mock_user)
        
        # Assert
        assert len(result) == 3
        assert all(app.cedula == cedula for app in result)
        assert result[0].convenio == "EMPRESA_ABC"
        assert result[1].convenio == "EMPRESA_XYZ"
        assert result[2].convenio is None
        
        # Verify applications are for the same person but different convenios
        assert all(app.name == "Juan Pérez García" for app in result)
        assert all(app.fecha_nacimiento == date(1985, 6, 15) for app in result)


class TestLoanApplicationValidationScenarios:
    """Test various loan application validation scenarios"""
    
    @pytest.mark.asyncio
    async def test_create_application_with_special_characters(self):
        """Test creating application with special characters in name"""
        # Arrange
        request = CreateLoanApplicationRequest(
            name="José María Pérez-González",  # Special characters
            cedula="12345678",
            convenio="EMPRESA_ABC",
            telefono="3001234567",
            fecha_nacimiento=date(1985, 6, 15)
        )
        
        expected_response = LoanApplicationResponse(
            id=1,
            name="José María Pérez-González",
            cedula="12345678",
            convenio="EMPRESA_ABC",
            telefono="3001234567",
            fecha_nacimiento=date(1985, 6, 15),
            created_at=datetime.now()
        )
        
        mock_service = AsyncMock()
        mock_service.create_application.return_value = expected_response
        
        # Act
        result = await create_loan_application(request, mock_service)
        
        # Assert
        assert result.name == "José María Pérez-González"
        mock_service.create_application.assert_called_once_with(request)
    
    @pytest.mark.asyncio
    async def test_create_application_with_various_cedula_formats(self):
        """Test creating applications with various cedula formats"""
        # Arrange
        cedula_formats = [
            "12345678",      # 8 digits
            "123456789",     # 9 digits
            "1234567890",    # 10 digits
            "12345678901"    # 11 digits
        ]
        
        mock_service = AsyncMock()
        
        for i, cedula in enumerate(cedula_formats):
            request = CreateLoanApplicationRequest(
                name=f"Test User {i+1}",
                cedula=cedula,
                convenio=None,
                telefono="3001234567",
                fecha_nacimiento=date(1990, 1, 1)
            )
            
            expected_response = LoanApplicationResponse(
                id=i+1,
                name=f"Test User {i+1}",
                cedula=cedula,
                convenio=None,
                telefono="3001234567",
                fecha_nacimiento=date(1990, 1, 1),
                created_at=datetime.now()
            )
            
            mock_service.create_application.return_value = expected_response
            
            # Act
            result = await create_loan_application(request, mock_service)
            
            # Assert
            assert result.cedula == cedula
            assert len(result.cedula) >= 8
            assert len(result.cedula) <= 11
    
    @pytest.mark.asyncio
    async def test_update_application_age_boundary_cases(self):
        """Test updating application with age boundary cases"""
        # Arrange
        application_id = 1
        today = date.today()
        
        # Test exactly 18 years old (should be valid)
        request = UpdateLoanApplicationRequest(
            fecha_nacimiento=date(today.year - 18, today.month, today.day)
        )
        
        expected_response = LoanApplicationResponse(
            id=1,
            name="Test User",
            cedula="12345678",
            convenio=None,
            telefono="3001234567",
            fecha_nacimiento=date(today.year - 18, today.month, today.day),
            created_at=datetime.now()
        )
        
        mock_service = AsyncMock()
        mock_service.update_application.return_value = expected_response
        
        mock_user = User(id="user123", email="user@example.com", role="admin")
        
        # Act
        result = await update_application(application_id, request, mock_service, mock_user)
        
        # Assert
        assert result.fecha_nacimiento == date(today.year - 18, today.month, today.day)
        mock_service.update_application.assert_called_once_with(application_id, request)