"""
Unit tests for Client entity
"""
import pytest
from datetime import date
from src.domain.entities.client import Client


class TestClientValidation:
    """Test client validation methods"""
    
    def test_validate_email_valid(self):
        """Test valid email formats"""
        client = Client(
            id=None,
            nombre_completo="Juan Pérez",
            cedula="12345678",
            email="juan@email.com",
            telefono="3001234567",
            fecha_nacimiento=date(1950, 1, 1),
            direccion="Calle 123"
        )
        
        assert client.validate_email() == True
    
    def test_validate_email_invalid_formats(self):
        """Test invalid email formats"""
        invalid_emails = [
            "invalid-email",
            "test@",
            "@domain.com",
            "test.domain.com",
            "",
            "   ",
            "test@domain",
            "test@.com"
        ]
        
        for invalid_email in invalid_emails:
            client = Client(
                id=None,
                nombre_completo="Juan Pérez",
                cedula="12345678",
                email=invalid_email,
                telefono="3001234567",
                fecha_nacimiento=date(1950, 1, 1),
                direccion="Calle 123"
            )
            assert client.validate_email() == False, f"Email '{invalid_email}' should be invalid"
    
    def test_validate_phone_valid_formats(self):
        """Test valid Colombian phone formats"""
        valid_phones = [
            "3001234567",
            "+573001234567",
            "573001234567",
            "300 123 4567",
            "+57 300 123 4567",
            "3109876543",
            "3209876543"
        ]
        
        for valid_phone in valid_phones:
            client = Client(
                id=None,
                nombre_completo="Juan Pérez",
                cedula="12345678",
                email="juan@email.com",
                telefono=valid_phone,
                fecha_nacimiento=date(1950, 1, 1),
                direccion="Calle 123"
            )
            assert client.validate_phone() == True, f"Phone '{valid_phone}' should be valid"
    
    def test_validate_phone_invalid_formats(self):
        """Test invalid phone formats"""
        invalid_phones = [
            "123456789",  # No empieza con 3
            "4001234567",  # Empieza con 4
            "30012345",   # Muy corto
            "30012345678",  # Muy largo
            "",
            "   ",
            "abc1234567",
            "+541234567890"  # Argentina
        ]
        
        for invalid_phone in invalid_phones:
            client = Client(
                id=None,
                nombre_completo="Juan Pérez",
                cedula="12345678",
                email="juan@email.com",
                telefono=invalid_phone,
                fecha_nacimiento=date(1950, 1, 1),
                direccion="Calle 123"
            )
            assert client.validate_phone() == False, f"Phone '{invalid_phone}' should be invalid"
    
    def test_validate_document_valid(self):
        """Test valid cedula formats"""
        valid_cedulas = [
            "1234567",      # 7 digits
            "12345678",     # 8 digits
            "123456789",    # 9 digits
            "1234567890",   # 10 digits
            "12.345.678",   # With dots
            "12,345,678"    # With commas
        ]
        
        for valid_cedula in valid_cedulas:
            client = Client(
                id=None,
                nombre_completo="Juan Pérez",
                cedula=valid_cedula,
                email="juan@email.com",
                telefono="3001234567",
                fecha_nacimiento=date(1950, 1, 1),
                direccion="Calle 123"
            )
            assert client.validate_document() == True, f"Cedula '{valid_cedula}' should be valid"
    
    def test_validate_document_invalid(self):
        """Test invalid cedula formats"""
        invalid_cedulas = [
            "123456",       # Too short (6 digits)
            "12345678901",  # Too long (11 digits)
            "",
            "   ",
            "abcd1234",
            "12345abc"
        ]
        
        for invalid_cedula in invalid_cedulas:
            client = Client(
                id=None,
                nombre_completo="Juan Pérez",
                cedula=invalid_cedula,
                email="juan@email.com",
                telefono="3001234567",
                fecha_nacimiento=date(1950, 1, 1),
                direccion="Calle 123"
            )
            assert client.validate_document() == False, f"Cedula '{invalid_cedula}' should be invalid"
    
    def test_validate_age_valid_range(self):
        """Test valid age range (70-110 years)"""
        current_year = date.today().year
        
        # Test 70 years old (minimum)
        client_70 = Client(
            id=None,
            nombre_completo="Juan Pérez",
            cedula="12345678",
            email="juan@email.com",
            telefono="3001234567",
            fecha_nacimiento=date(current_year - 70, 1, 1),
            direccion="Calle 123"
        )
        assert client_70.validate_age() == True
        assert client_70.get_age() == 70
        
        # Test 110 years old (maximum)
        client_110 = Client(
            id=None,
            nombre_completo="María García",
            cedula="87654321",
            email="maria@email.com",
            telefono="3001234567",
            fecha_nacimiento=date(current_year - 110, 1, 1),
            direccion="Calle 456"
        )
        assert client_110.validate_age() == True
        assert client_110.get_age() == 110
        
        # Test 85 years old (middle range)
        client_85 = Client(
            id=None,
            nombre_completo="Carlos López",
            cedula="11223344",
            email="carlos@email.com",
            telefono="3001234567",
            fecha_nacimiento=date(current_year - 85, 6, 15),
            direccion="Carrera 789"
        )
        assert client_85.validate_age() == True
    
    def test_validate_age_invalid_range(self):
        """Test invalid age range (outside 70-110 years)"""
        current_year = date.today().year
        
        # Test 69 years old (too young)
        client_young = Client(
            id=None,
            nombre_completo="Joven Pérez",
            cedula="12345678",
            email="joven@email.com",
            telefono="3001234567",
            fecha_nacimiento=date(current_year - 69, 1, 1),
            direccion="Calle 123"
        )
        assert client_young.validate_age() == False
        assert client_young.get_age() == 69
        
        # Test 111 years old (too old)
        client_old = Client(
            id=None,
            nombre_completo="Muy Viejo",
            cedula="87654321",
            email="viejo@email.com",
            telefono="3001234567",
            fecha_nacimiento=date(current_year - 111, 1, 1),
            direccion="Calle 456"
        )
        assert client_old.validate_age() == False
        assert client_old.get_age() == 111
    
    def test_is_complete_valid(self, sample_client):
        """Test complete client data"""
        assert sample_client.is_complete() == True
    
    def test_is_complete_missing_fields(self):
        """Test incomplete client data"""
        # Missing name
        client_no_name = Client(
            id=None,
            nombre_completo="",
            cedula="12345678",
            email="juan@email.com",
            telefono="3001234567",
            fecha_nacimiento=date(1950, 1, 1),
            direccion="Calle 123"
        )
        assert client_no_name.is_complete() == False
        
        # Missing email
        client_no_email = Client(
            id=None,
            nombre_completo="Juan Pérez",
            cedula="12345678",
            email="",
            telefono="3001234567",
            fecha_nacimiento=date(1950, 1, 1),
            direccion="Calle 123"
        )
        assert client_no_email.is_complete() == False
        
        # Missing birth date
        client_no_birth = Client(
            id=None,
            nombre_completo="Juan Pérez",
            cedula="12345678",
            email="juan@email.com",
            telefono="3001234567",
            fecha_nacimiento=None,
            direccion="Calle 123"
        )
        assert client_no_birth.is_complete() == False


class TestClientBusinessLogic:
    """Test client business logic methods"""
    
    def test_update_contact_info_valid(self, sample_client):
        """Test updating contact info with valid data"""
        new_email = "nuevo@email.com"
        new_phone = "3109876543"
        
        result = sample_client.update_contact_info(email=new_email, telefono=new_phone)
        
        assert result == True
        assert sample_client.email == new_email
        assert sample_client.telefono == new_phone
    
    def test_update_contact_info_invalid_email(self, sample_client):
        """Test updating contact info with invalid email"""
        original_email = sample_client.email
        invalid_email = "invalid-email"
        
        result = sample_client.update_contact_info(email=invalid_email)
        
        assert result == False
        assert sample_client.email == original_email  # Should remain unchanged
    
    def test_update_contact_info_invalid_phone(self, sample_client):
        """Test updating contact info with invalid phone"""
        original_phone = sample_client.telefono
        invalid_phone = "123"
        
        result = sample_client.update_contact_info(telefono=invalid_phone)
        
        assert result == False
        assert sample_client.telefono == original_phone  # Should remain unchanged
    
    def test_update_contact_info_partial(self, sample_client):
        """Test updating only email or only phone"""
        original_phone = sample_client.telefono
        new_email = "nuevo@email.com"
        
        # Update only email
        result = sample_client.update_contact_info(email=new_email)
        
        assert result == True
        assert sample_client.email == new_email
        assert sample_client.telefono == original_phone  # Should remain unchanged
    
    def test_validate_complete_valid_client(self, sample_client):
        """Test complete validation on valid client"""
        assert sample_client.validate() == True
        assert len(sample_client.get_validation_errors()) == 0
    
    def test_validate_complete_invalid_client(self, invalid_client):
        """Test complete validation on invalid client"""
        assert invalid_client.validate() == False
        
        errors = invalid_client.get_validation_errors()
        assert len(errors) > 0
        assert "Faltan campos obligatorios" in errors
        assert "Formato de email inválido" in errors
        assert "Formato de teléfono inválido (debe ser número colombiano)" in errors
        assert "Formato de cédula inválido (7-10 dígitos)" in errors
        assert "Edad inválida" in errors[4]  # Age error message contains the actual age
    
    def test_get_validation_errors_specific(self):
        """Test specific validation error messages"""
        client = Client(
            id=None,
            nombre_completo="Juan Pérez",
            cedula="123",  # Invalid cedula
            email="invalid-email",  # Invalid email
            telefono="123",  # Invalid phone
            fecha_nacimiento=date(2010, 1, 1),  # Invalid age
            direccion="Calle 123"
        )
        
        errors = client.get_validation_errors()
        
        assert "Formato de email inválido" in errors
        assert "Formato de teléfono inválido (debe ser número colombiano)" in errors
        assert "Formato de cédula inválido (7-10 dígitos)" in errors
        assert "años (debe estar entre 70 y 110 años)" in errors[3]


class TestClientEdgeCases:
    """Test edge cases and boundary conditions"""
    
    def test_age_calculation_with_birthday_not_passed(self):
        """Test age calculation when birthday hasn't occurred this year"""
        current_date = date.today()
        
        # Create client born next month (if possible)
        if current_date.month < 12:
            birth_date = date(current_date.year - 75, current_date.month + 1, 1)
        else:
            birth_date = date(current_date.year - 75, 1, 1)
        
        client = Client(
            id=None,
            nombre_completo="Test Client",
            cedula="12345678",
            email="test@email.com",
            telefono="3001234567",
            fecha_nacimiento=birth_date,
            direccion="Test Address"
        )
        
        # Age should be calculated correctly
        expected_age = current_date.year - birth_date.year
        if (current_date.month < birth_date.month or 
            (current_date.month == birth_date.month and current_date.day < birth_date.day)):
            expected_age -= 1
        
        assert client.get_age() == expected_age
    
    def test_phone_with_spaces_and_special_chars(self):
        """Test phone validation with various formatting"""
        phones_with_formatting = [
            "+57 300 123 4567",
            "300-123-4567",
            "(300) 123-4567",
            "300 123 4567"
        ]
        
        for phone in phones_with_formatting:
            client = Client(
                id=None,
                nombre_completo="Test Client",
                cedula="12345678",
                email="test@email.com",
                telefono=phone,
                fecha_nacimiento=date(1950, 1, 1),
                direccion="Test Address"
            )
            assert client.validate_phone() == True, f"Phone '{phone}' should be valid"
    
    def test_cedula_with_formatting(self):
        """Test cedula validation with dots and commas"""
        cedulas_with_formatting = [
            "12.345.678",
            "12,345,678",
            "12 345 678",
            "12-345-678"
        ]
        
        for cedula in cedulas_with_formatting:
            client = Client(
                id=None,
                nombre_completo="Test Client",
                cedula=cedula,
                email="test@email.com",
                telefono="3001234567",
                fecha_nacimiento=date(1950, 1, 1),
                direccion="Test Address"
            )
            assert client.validate_document() == True, f"Cedula '{cedula}' should be valid"