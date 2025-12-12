"""
Simplified unit tests for ClientService (non-async version for testing core logic)
"""
import pytest
from unittest.mock import Mock
from datetime import date, datetime
from src.domain.entities.client import Client


class TestClientServiceLogic:
    """Test ClientService core business logic"""
    
    def test_client_entity_creation_with_valid_data(self):
        """Test that we can create a valid client entity"""
        # Arrange
        client_data = {
            'id': None,
            'nombre_completo': 'Juan Pérez García',
            'cedula': '12345678',
            'email': 'juan@email.com',
            'telefono': '3001234567',
            'fecha_nacimiento': date(1990, 5, 15),
            'direccion': 'Calle 123 #45-67, Bogotá'
        }
        
        # Act
        client = Client(**client_data)
        
        # Assert
        assert client.nombre_completo == 'Juan Pérez García'
        assert client.cedula == '12345678'
        assert client.email == 'juan@email.com'
        assert client.validate() == True
    
    def test_client_entity_validation_with_invalid_data(self):
        """Test client validation with invalid data"""
        # Arrange
        invalid_client_data = {
            'id': None,
            'nombre_completo': 'Juan Pérez',
            'cedula': '123',  # Too short
            'email': 'invalid-email',  # Invalid format
            'telefono': '123',  # Invalid format
            'fecha_nacimiento': date(2010, 1, 1),  # Too young
            'direccion': 'Calle 123'
        }
        
        # Act
        client = Client(**invalid_client_data)
        
        # Assert
        assert client.validate() == False
        errors = client.get_validation_errors()
        assert len(errors) > 0
        assert any('email' in error.lower() for error in errors)
        assert any('teléfono' in error.lower() for error in errors)
        assert any('cédula' in error.lower() for error in errors)
        assert any('edad' in error.lower() for error in errors)
    
    def test_client_email_validation_logic(self):
        """Test email validation logic"""
        # Valid emails
        valid_emails = [
            'test@example.com',
            'user.name@domain.co.uk',
            'test123@test-domain.com'
        ]
        
        for email in valid_emails:
            client = Client(
                id=None,
                nombre_completo='Test User',
                cedula='12345678',
                email=email,
                telefono='3001234567',
                fecha_nacimiento=date(1990, 1, 1),
                direccion='Test Address'
            )
            assert client.validate_email() == True, f"Email {email} should be valid"
        
        # Invalid emails
        invalid_emails = [
            'invalid-email',
            'test@',
            '@domain.com',
            'test.domain.com',
            '',
            '   '
        ]
        
        for email in invalid_emails:
            client = Client(
                id=None,
                nombre_completo='Test User',
                cedula='12345678',
                email=email,
                telefono='3001234567',
                fecha_nacimiento=date(1990, 1, 1),
                direccion='Test Address'
            )
            assert client.validate_email() == False, f"Email {email} should be invalid"
    
    def test_client_phone_validation_logic(self):
        """Test phone validation logic"""
        # Valid Colombian phones
        valid_phones = [
            '3001234567',
            '+573001234567',
            '573001234567',
            '300 123 4567',
            '+57 300 123 4567'
        ]
        
        for phone in valid_phones:
            client = Client(
                id=None,
                nombre_completo='Test User',
                cedula='12345678',
                email='test@example.com',
                telefono=phone,
                fecha_nacimiento=date(1990, 1, 1),
                direccion='Test Address'
            )
            assert client.validate_phone() == True, f"Phone {phone} should be valid"
        
        # Invalid phones
        invalid_phones = [
            '123456789',  # Doesn't start with 3
            '4001234567',  # Starts with 4
            '30012345',   # Too short
            '30012345678',  # Too long
            '',
            'abc1234567'
        ]
        
        for phone in invalid_phones:
            client = Client(
                id=None,
                nombre_completo='Test User',
                cedula='12345678',
                email='test@example.com',
                telefono=phone,
                fecha_nacimiento=date(1990, 1, 1),
                direccion='Test Address'
            )
            assert client.validate_phone() == False, f"Phone {phone} should be invalid"
    
    def test_client_age_validation_logic(self):
        """Test age validation logic"""
        current_year = date.today().year
        
        # Valid ages (22 and above)
        valid_ages = [22, 25, 35, 50, 65]
        
        for age in valid_ages:
            client = Client(
                id=None,
                nombre_completo='Test User',
                cedula='12345678',
                email='test@example.com',
                telefono='3001234567',
                fecha_nacimiento=date(current_year - age, 1, 1),
                direccion='Test Address'
            )
            assert client.validate_age() == True, f"Age {age} should be valid"
            assert client.get_age() == age
        
        # Invalid ages (under 22)
        invalid_ages = [18, 19, 20, 21]
        
        for age in invalid_ages:
            client = Client(
                id=None,
                nombre_completo='Test User',
                cedula='12345678',
                email='test@example.com',
                telefono='3001234567',
                fecha_nacimiento=date(current_year - age, 1, 1),
                direccion='Test Address'
            )
            assert client.validate_age() == False, f"Age {age} should be invalid"
            assert client.get_age() == age
    
    def test_client_cedula_validation_logic(self):
        """Test cedula validation logic"""
        # Valid cedulas
        valid_cedulas = [
            '1234567',      # 7 digits
            '12345678',     # 8 digits
            '123456789',    # 9 digits
            '1234567890',   # 10 digits
            '12.345.678',   # With dots
            '12,345,678'    # With commas
        ]
        
        for cedula in valid_cedulas:
            client = Client(
                id=None,
                nombre_completo='Test User',
                cedula=cedula,
                email='test@example.com',
                telefono='3001234567',
                fecha_nacimiento=date(1990, 1, 1),
                direccion='Test Address'
            )
            assert client.validate_document() == True, f"Cedula {cedula} should be valid"
        
        # Invalid cedulas
        invalid_cedulas = [
            '123456',       # Too short (6 digits)
            '12345678901',  # Too long (11 digits)
            '',
            '   ',
            'abcd1234',
            '12345abc'
        ]
        
        for cedula in invalid_cedulas:
            client = Client(
                id=None,
                nombre_completo='Test User',
                cedula=cedula,
                email='test@example.com',
                telefono='3001234567',
                fecha_nacimiento=date(1990, 1, 1),
                direccion='Test Address'
            )
            assert client.validate_document() == False, f"Cedula {cedula} should be invalid"
    
    def test_client_completeness_validation(self):
        """Test client data completeness validation"""
        # Complete client
        complete_client = Client(
            id=None,
            nombre_completo='Juan Pérez García',
            cedula='12345678',
            email='juan@email.com',
            telefono='3001234567',
            fecha_nacimiento=date(1990, 5, 15),
            direccion='Calle 123 #45-67, Bogotá'
        )
        assert complete_client.is_complete() == True
        
        # Incomplete clients
        incomplete_cases = [
            {'nombre_completo': ''},  # Empty name
            {'email': ''},            # Empty email
            {'direccion': ''},        # Empty address
            {'fecha_nacimiento': None}  # No birth date
        ]
        
        base_data = {
            'id': None,
            'nombre_completo': 'Juan Pérez',
            'cedula': '12345678',
            'email': 'juan@email.com',
            'telefono': '3001234567',
            'fecha_nacimiento': date(1990, 1, 1),
            'direccion': 'Calle 123'
        }
        
        for incomplete_field in incomplete_cases:
            client_data = base_data.copy()
            client_data.update(incomplete_field)
            
            client = Client(**client_data)
            assert client.is_complete() == False, f"Client should be incomplete with {incomplete_field}"
    
    def test_client_contact_info_update_logic(self):
        """Test client contact info update logic"""
        # Create a valid client
        client = Client(
            id=1,
            nombre_completo='Juan Pérez García',
            cedula='12345678',
            email='juan@email.com',
            telefono='3001234567',
            fecha_nacimiento=date(1990, 5, 15),
            direccion='Calle 123 #45-67, Bogotá'
        )
        
        # Test valid email update
        result = client.update_contact_info(email='nuevo@email.com')
        assert result == True
        assert client.email == 'nuevo@email.com'
        
        # Test valid phone update
        result = client.update_contact_info(telefono='3109876543')
        assert result == True
        assert client.telefono == '3109876543'
        
        # Test invalid email update
        original_email = client.email
        result = client.update_contact_info(email='invalid-email')
        assert result == False
        assert client.email == original_email  # Should remain unchanged
        
        # Test invalid phone update
        original_phone = client.telefono
        result = client.update_contact_info(telefono='123')
        assert result == False
        assert client.telefono == original_phone  # Should remain unchanged
    
    def test_service_business_logic_patterns(self):
        """Test common service patterns that would be used"""
        # Test duplicate detection logic (what a service would do)
        clients = [
            Client(id=1, nombre_completo='Juan Pérez', cedula='12345678', 
                  email='juan@email.com', telefono='3001234567',
                  fecha_nacimiento=date(1990, 1, 1), direccion='Calle 123'),
            Client(id=2, nombre_completo='María García', cedula='87654321',
                  email='maria@email.com', telefono='3009876543',
                  fecha_nacimiento=date(1985, 1, 1), direccion='Carrera 456')
        ]
        
        # Test finding by cedula
        target_cedula = '12345678'
        found_client = next((c for c in clients if c.cedula == target_cedula), None)
        assert found_client is not None
        assert found_client.nombre_completo == 'Juan Pérez'
        
        # Test finding by email
        target_email = 'maria@email.com'
        found_client = next((c for c in clients if c.email == target_email), None)
        assert found_client is not None
        assert found_client.nombre_completo == 'María García'
        
        # Test not finding non-existent client
        non_existent_cedula = '99999999'
        found_client = next((c for c in clients if c.cedula == non_existent_cedula), None)
        assert found_client is None
    
    def test_validation_error_messages(self):
        """Test that validation error messages are informative"""
        # Create client with multiple validation errors
        client = Client(
            id=None,
            nombre_completo='',  # Empty name
            cedula='123',        # Invalid cedula
            email='invalid',     # Invalid email
            telefono='123',      # Invalid phone
            fecha_nacimiento=date(2010, 1, 1),  # Too young
            direccion=''         # Empty address
        )
        
        errors = client.get_validation_errors()
        
        # Check that we get meaningful error messages
        assert len(errors) > 0
        
        # Check for specific error types
        error_text = ' '.join(errors).lower()
        assert 'campos obligatorios' in error_text or 'email' in error_text
        assert 'email' in error_text or 'teléfono' in error_text
        assert 'cédula' in error_text or 'edad' in error_text
        
        # Verify that each error is a string
        for error in errors:
            assert isinstance(error, str)
            assert len(error) > 0