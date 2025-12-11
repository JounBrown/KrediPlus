"""Tests for auth_middleware"""
import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from fastapi import HTTPException
from src.domain.entities.user import User


class TestGetCurrentUser:
    """Tests for get_current_user dependency"""

    @pytest.fixture
    def mock_auth_service(self):
        return AsyncMock()

    @pytest.fixture
    def valid_user(self):
        return User(
            id="user-123",
            email="test@example.com",
            role="user"
        )

    @pytest.fixture
    def admin_user(self):
        return User(
            id="admin-123",
            email="admin@example.com",
            role="admin"
        )

    async def test_get_current_user_success(self, mock_auth_service, valid_user):
        """Test successful user authentication"""
        mock_auth_service.authenticate_user.return_value = valid_user
        mock_credentials = MagicMock()
        mock_credentials.credentials = "valid_token"

        with patch('src.api.middleware.auth_middleware._auth_service', mock_auth_service):
            from src.api.middleware.auth_middleware import get_current_user
            result = await get_current_user(mock_credentials)

        assert result.id == "user-123"
        assert result.email == "test@example.com"
        mock_auth_service.authenticate_user.assert_called_once_with("valid_token")

    async def test_get_current_user_invalid_token(self, mock_auth_service):
        """Test authentication with invalid token"""
        mock_auth_service.authenticate_user.return_value = None
        mock_credentials = MagicMock()
        mock_credentials.credentials = "invalid_token"

        with patch('src.api.middleware.auth_middleware._auth_service', mock_auth_service):
            from src.api.middleware.auth_middleware import get_current_user
            with pytest.raises(HTTPException) as exc_info:
                await get_current_user(mock_credentials)

        assert exc_info.value.status_code == 401
        assert "Token inválido" in exc_info.value.detail


class TestGetCurrentUserOptional:
    """Tests for get_current_user_optional dependency"""

    @pytest.fixture
    def mock_auth_service(self):
        return AsyncMock()

    @pytest.fixture
    def valid_user(self):
        return User(
            id="user-123",
            email="test@example.com",
            role="user"
        )

    async def test_get_current_user_optional_with_valid_token(self, mock_auth_service, valid_user):
        """Test optional auth with valid token"""
        mock_auth_service.authenticate_user.return_value = valid_user
        mock_credentials = MagicMock()
        mock_credentials.credentials = "valid_token"

        with patch('src.api.middleware.auth_middleware._auth_service', mock_auth_service):
            from src.api.middleware.auth_middleware import get_current_user_optional
            result = await get_current_user_optional(mock_credentials)

        assert result is not None
        assert result.id == "user-123"

    async def test_get_current_user_optional_no_credentials(self, mock_auth_service):
        """Test optional auth without credentials"""
        with patch('src.api.middleware.auth_middleware._auth_service', mock_auth_service):
            from src.api.middleware.auth_middleware import get_current_user_optional
            result = await get_current_user_optional(None)

        assert result is None
        mock_auth_service.authenticate_user.assert_not_called()

    async def test_get_current_user_optional_invalid_token(self, mock_auth_service):
        """Test optional auth with invalid token returns None"""
        mock_auth_service.authenticate_user.return_value = None
        mock_credentials = MagicMock()
        mock_credentials.credentials = "invalid_token"

        with patch('src.api.middleware.auth_middleware._auth_service', mock_auth_service):
            from src.api.middleware.auth_middleware import get_current_user_optional
            result = await get_current_user_optional(mock_credentials)

        assert result is None


class TestRequireAdmin:
    """Tests for require_admin dependency"""

    @pytest.fixture
    def admin_user(self):
        user = MagicMock(spec=User)
        user.is_admin.return_value = True
        user.id = "admin-123"
        return user

    @pytest.fixture
    def regular_user(self):
        user = MagicMock(spec=User)
        user.is_admin.return_value = False
        user.id = "user-123"
        return user

    async def test_require_admin_success(self, admin_user):
        """Test admin access granted"""
        from src.api.middleware.auth_middleware import require_admin
        result = await require_admin(admin_user)

        assert result.id == "admin-123"
        admin_user.is_admin.assert_called_once()

    async def test_require_admin_forbidden(self, regular_user):
        """Test admin access denied for regular user"""
        from src.api.middleware.auth_middleware import require_admin
        with pytest.raises(HTTPException) as exc_info:
            await require_admin(regular_user)

        assert exc_info.value.status_code == 403
        assert "administrador" in exc_info.value.detail
