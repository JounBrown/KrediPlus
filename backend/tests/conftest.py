"""
Shared test configuration and fixtures
"""
import pytest
from datetime import date
from src.domain.entities.client import Client


@pytest.fixture
def sample_client():
    """Fixture that provides a valid sample client for testing"""
    return Client(
        id=None,
        nombre_completo="Juan Pérez García",
        cedula="12345678",
        email="juan.perez@email.com",
        telefono="3001234567",
        fecha_nacimiento=date(1950, 5, 15),  # 73 años
        direccion="Calle 123 #45-67, Bogotá"
    )


@pytest.fixture
def invalid_client():
    """Fixture that provides an invalid client for testing validation"""
    return Client(
        id=None,
        nombre_completo="",  # Nombre vacío (inválido)
        cedula="123",  # Cédula muy corta (inválida)
        email="invalid-email",  # Email inválido
        telefono="123",  # Teléfono inválido
        fecha_nacimiento=date(2010, 1, 1),  # Muy joven (inválido)
        direccion=""  # Dirección vacía (inválida)
    )


@pytest.fixture
def elderly_client():
    """Fixture that provides a client at the age boundary (70 years)"""
    return Client(
        id=None,
        nombre_completo="María González",
        cedula="87654321",
        email="maria@email.com",
        telefono="+573209876543",
        fecha_nacimiento=date(1954, 1, 1),  # Exactamente 70 años
        direccion="Carrera 45 #12-34"
    )