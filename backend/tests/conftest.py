"""
Shared test configuration and fixtures
"""
import pytest
from datetime import date, datetime
from unittest.mock import Mock, AsyncMock


# ============================================================================
# PYTEST-ASYNCIO CONFIGURATION
# ============================================================================
# This enables async tests to work properly with pytest-asyncio
pytest_plugins = ('pytest_asyncio',)


# ============================================================================
# DOMAIN ENTITY FIXTURES (Sync)
# ============================================================================
@pytest.fixture
def sample_client():
    """Fixture that provides a valid sample client for testing"""
    from src.domain.entities.client import Client
    return Client(
        id=None,
        nombre_completo="Juan Pérez García",
        cedula="12345678",
        email="juan.perez@email.com",
        telefono="3001234567",
        fecha_nacimiento=date(1990, 5, 15),
        direccion="Calle 123 #45-67, Bogotá"
    )


@pytest.fixture
def invalid_client():
    """Fixture that provides an invalid client for testing validation"""
    from src.domain.entities.client import Client
    return Client(
        id=None,
        nombre_completo="",
        cedula="123",
        email="invalid-email",
        telefono="123",
        fecha_nacimiento=date(2010, 1, 1),
        direccion=""
    )


@pytest.fixture
def young_adult_client():
    """Fixture that provides a client at the minimum age boundary (22 years)"""
    from src.domain.entities.client import Client
    current_year = date.today().year
    return Client(
        id=None,
        nombre_completo="María González",
        cedula="87654321",
        email="maria@email.com",
        telefono="+573209876543",
        fecha_nacimiento=date(current_year - 22, 1, 1),
        direccion="Carrera 45 #12-34"
    )


@pytest.fixture
def sample_client_document():
    """Fixture that provides a valid sample client document for testing"""
    from src.domain.entities.client_document import ClientDocument, DocumentType
    return ClientDocument(
        id=1,
        file_name="cedula_frente.jpg",
        storage_path="clients/123/documents/cedula_frente_unique.jpg",
        document_type=DocumentType.CEDULA_FRENTE,
        client_id=123,
        credit_id=None,
        created_at=datetime(2024, 1, 1, 12, 0, 0)
    )


# ============================================================================
# MOCK FIXTURES (For Async Tests)
# ============================================================================
@pytest.fixture
def mock_async_repository():
    """Fixture that provides a mock async repository"""
    return AsyncMock()


@pytest.fixture
def mock_storage_service():
    """Fixture that provides a mock storage service"""
    mock = Mock()
    mock.upload_file = AsyncMock()
    mock.delete_file = AsyncMock()
    mock.generate_unique_filename = Mock()
    mock.build_storage_path = Mock()
    mock.get_public_url = Mock()
    mock.create_signed_url = Mock()
    return mock
