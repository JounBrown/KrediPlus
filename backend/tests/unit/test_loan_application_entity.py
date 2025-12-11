"""
Unit tests for LoanApplication entity
"""
import pytest
from datetime import date, datetime
from src.domain.entities.loan_application import LoanApplication


class TestLoanApplicationEntity:
    """Test LoanApplication entity functionality"""
    
    def test_loan_application_creation_with_valid_data(self):
        """Test creating a valid loan application"""
        # Arrange & Act
        application = LoanApplication(
            id=1,
            name="Juan Pérez García",
            cedula="12345678",
            convenio="EMPRESA_ABC",
            telefono="3001234567",
            fecha_nacimiento=date(1985, 6, 15)
        )
        
        # Assert
        assert application.id == 1
        assert application.name == "Juan Pérez García"
        assert application.cedula == "12345678"
        assert application.convenio == "EMPRESA_ABC"
        assert application.telefono == "3001234567"
        assert application.fecha_nacimiento == date(1985, 6, 15)
        assert isinstance(application.created_at, datetime)
    
    def test_loan_application_creation_without_convenio(self):
        """Test creating loan application without convenio"""
        # Arrange & Act
        application = LoanApplication(
            id=2,
            name="María González",
            cedula="87654321",
            convenio=None,
            telefono="3009876543",
            fecha_nacimiento=date(1990, 3, 20)
        )
        
        # Assert
        assert application.id == 2
        assert application.name == "María González"
        assert application.convenio is None
        assert application.telefono == "3009876543"
    
    def test_loan_application_creation_with_defaults(self):
        """Test loan application creation with default values"""
        # Arrange & Act
        application = LoanApplication(
            id=None,
            name="Test User",
            cedula="11223344",
            convenio=None,
            telefono="3001111111",
            fecha_nacimiento=date(1980, 1, 1)
        )
        
        # Assert
        assert application.id is None
        assert isinstance(application.created_at, datetime)
        assert application.created_at <= datetime.now()


class TestLoanApplicationValidation:
    """Test loan application validation methods"""
    
    def test_validate_cedula_valid_formats(self):
        """Test valid cedula formats"""
        valid_cedulas = [
            "12345678",      # 8 digits
            "123456789",     # 9 digits
            "1234567890",    # 10 digits
            "12345678901",   # 11 digits
            "12.345.678",    # With dots
            "12,345,678",    # With commas
            "12-345-678",    # With dashes
            "12 345 678"     # With spaces
        ]
        
        for cedula in valid_cedulas:
            application = LoanApplication(
                id=1,
                name="Test User",
                cedula=cedula,
                convenio=None,
                telefono="3001234567",
                fecha_nacimiento=date(1990, 1, 1)
            )
            assert application.validate_cedula() == True, f"Cedula '{cedula}' should be valid"
    
    def test_validate_cedula_invalid_formats(self):
        """Test invalid cedula formats"""
        invalid_cedulas = [
            "1234567",       # 7 digits (too short)
            "123456789012",  # 12 digits (too long)
            "",              # Empty
            "   ",           # Only spaces
            "abcd1234",      # Contains letters
            "12345abc",      # Contains letters
            "12345@78"       # Contains special characters
        ]
        
        for cedula in invalid_cedulas:
            application = LoanApplication(
                id=1,
                name="Test User",
                cedula=cedula,
                convenio=None,
                telefono="3001234567",
                fecha_nacimiento=date(1990, 1, 1)
            )
            assert application.validate_cedula() == False, f"Cedula '{cedula}' should be invalid"
    
    def test_is_adult_valid_ages(self):
        """Test is_adult with valid ages (18 and above)"""
        current_year = date.today().year
        
        valid_ages = [18, 19, 25, 35, 50, 65, 80]
        
        for age in valid_ages:
            application = LoanApplication(
                id=1,
                name="Test User",
                cedula="12345678",
                convenio=None,
                telefono="3001234567",
                fecha_nacimiento=date(current_year - age, 1, 1)
            )
            assert application.is_adult() == True, f"Age {age} should be considered adult"
    
    def test_is_adult_invalid_ages(self):
        """Test is_adult with invalid ages (under 18)"""
        current_year = date.today().year
        
        invalid_ages = [17, 16, 15, 10, 5, 1]
        
        for age in invalid_ages:
            application = LoanApplication(
                id=1,
                name="Test User",
                cedula="12345678",
                convenio=None,
                telefono="3001234567",
                fecha_nacimiento=date(current_year - age, 1, 1)
            )
            assert application.is_adult() == False, f"Age {age} should not be considered adult"
    
    def test_is_adult_birthday_edge_cases(self):
        """Test is_adult with birthday edge cases"""
        today = date.today()
        
        # Test someone who turns 18 today
        birthday_today = LoanApplication(
            id=1,
            name="Birthday Today",
            cedula="12345678",
            convenio=None,
            telefono="3001234567",
            fecha_nacimiento=date(today.year - 18, today.month, today.day)
        )
        assert birthday_today.is_adult() == True
        
        # Test someone who turns 18 tomorrow (still 17)
        if today.day < 28:  # Avoid month-end complications
            birthday_tomorrow = LoanApplication(
                id=2,
                name="Birthday Tomorrow",
                cedula="87654321",
                convenio=None,
                telefono="3009876543",
                fecha_nacimiento=date(today.year - 18, today.month, today.day + 1)
            )
            assert birthday_tomorrow.is_adult() == False
        
        # Test someone who turned 18 yesterday
        if today.day > 1:  # Avoid month-start complications
            birthday_yesterday = LoanApplication(
                id=3,
                name="Birthday Yesterday",
                cedula="11223344",
                convenio=None,
                telefono="3001111111",
                fecha_nacimiento=date(today.year - 18, today.month, today.day - 1)
            )
            assert birthday_yesterday.is_adult() == True
    
    def test_validate_application_data_success(self):
        """Test successful application data validation"""
        # Arrange
        application = LoanApplication(
            id=1,
            name="Carlos Rodríguez",
            cedula="98765432",
            convenio="CONVENIO_XYZ",
            telefono="3005555555",
            fecha_nacimiento=date(1988, 12, 10)
        )
        
        # Act & Assert
        assert application.validate_application_data() == True
    
    def test_validate_application_data_failures(self):
        """Test application data validation failures"""
        # Test empty name
        application = LoanApplication(
            id=1,
            name="",
            cedula="12345678",
            convenio=None,
            telefono="3001234567",
            fecha_nacimiento=date(1990, 1, 1)
        )
        assert not application.validate_application_data()
        
        # Test whitespace-only name
        application = LoanApplication(
            id=1,
            name="   ",
            cedula="12345678",
            convenio=None,
            telefono="3001234567",
            fecha_nacimiento=date(1990, 1, 1)
        )
        assert not application.validate_application_data()
        
        # Test invalid cedula
        application = LoanApplication(
            id=1,
            name="Valid Name",
            cedula="123",  # Too short
            convenio=None,
            telefono="3001234567",
            fecha_nacimiento=date(1990, 1, 1)
        )
        assert not application.validate_application_data()
        
        # Test empty telefono
        application = LoanApplication(
            id=1,
            name="Valid Name",
            cedula="12345678",
            convenio=None,
            telefono="",
            fecha_nacimiento=date(1990, 1, 1)
        )
        assert not application.validate_application_data()
        
        # Test whitespace-only telefono
        application = LoanApplication(
            id=1,
            name="Valid Name",
            cedula="12345678",
            convenio=None,
            telefono="   ",
            fecha_nacimiento=date(1990, 1, 1)
        )
        assert not application.validate_application_data()
        
        # Test underage applicant
        current_year = date.today().year
        application = LoanApplication(
            id=1,
            name="Valid Name",
            cedula="12345678",
            convenio=None,
            telefono="3001234567",
            fecha_nacimiento=date(current_year - 17, 1, 1)  # 17 years old
        )
        assert not application.validate_application_data()


class TestLoanApplicationBusinessLogic:
    """Test loan application business logic"""
    
    def test_application_with_convenio_validation(self):
        """Test application with convenio"""
        # Arrange
        application = LoanApplication(
            id=1,
            name="Employee Name",
            cedula="55566677",
            convenio="COMPANY_PAYROLL",
            telefono="3007777777",
            fecha_nacimiento=date(1985, 8, 25)
        )
        
        # Act & Assert
        assert application.validate_application_data() == True
        assert application.convenio == "COMPANY_PAYROLL"
        assert application.validate_cedula() == True
        assert application.is_adult() == True
    
    def test_application_without_convenio_validation(self):
        """Test application without convenio"""
        # Arrange
        application = LoanApplication(
            id=1,
            name="Independent Worker",
            cedula="44455566",
            convenio=None,
            telefono="3008888888",
            fecha_nacimiento=date(1992, 4, 12)
        )
        
        # Act & Assert
        assert application.validate_application_data() == True
        assert application.convenio is None
        assert application.validate_cedula() == True
        assert application.is_adult() == True
    
    def test_application_age_calculation_accuracy(self):
        """Test accurate age calculation for different scenarios"""
        today = date.today()
        
        # Test exact 18 years
        exactly_18 = LoanApplication(
            id=1,
            name="Exactly 18",
            cedula="12345678",
            convenio=None,
            telefono="3001234567",
            fecha_nacimiento=date(today.year - 18, today.month, today.day)
        )
        assert exactly_18.is_adult() == True
        
        # Test 18 years and 1 day
        if today.day > 1:
            over_18 = LoanApplication(
                id=2,
                name="Over 18",
                cedula="87654321",
                convenio=None,
                telefono="3009876543",
                fecha_nacimiento=date(today.year - 18, today.month, today.day - 1)
            )
            assert over_18.is_adult() == True
        
        # Test 17 years and 364 days
        if today.day < 28:  # Avoid month complications
            under_18 = LoanApplication(
                id=3,
                name="Under 18",
                cedula="11223344",
                convenio=None,
                telefono="3001111111",
                fecha_nacimiento=date(today.year - 18, today.month, today.day + 1)
            )
            assert under_18.is_adult() == False


class TestLoanApplicationEdgeCases:
    """Test edge cases and boundary conditions"""
    
    def test_application_with_special_characters_in_name(self):
        """Test application with special characters in name"""
        special_names = [
            "José María",
            "Ana-Sofía",
            "O'Connor",
            "María José Pérez-González",
            "Jean-Pierre",
            "José Ángel"
        ]
        
        for name in special_names:
            application = LoanApplication(
                id=1,
                name=name,
                cedula="12345678",
                convenio=None,
                telefono="3001234567",
                fecha_nacimiento=date(1990, 1, 1)
            )
            assert application.validate_application_data() == True, f"Name '{name}' should be valid"
    
    def test_application_with_long_names(self):
        """Test application with very long names"""
        # Test reasonable long name
        long_name = "María Fernanda Alejandra González Rodríguez de la Cruz"
        application = LoanApplication(
            id=1,
            name=long_name,
            cedula="12345678",
            convenio=None,
            telefono="3001234567",
            fecha_nacimiento=date(1990, 1, 1)
        )
        assert application.validate_application_data() == True
        
        # Test extremely long name
        very_long_name = "A" * 200
        application = LoanApplication(
            id=2,
            name=very_long_name,
            cedula="87654321",
            convenio=None,
            telefono="3009876543",
            fecha_nacimiento=date(1990, 1, 1)
        )
        assert application.validate_application_data() == True
    
    def test_application_with_various_phone_formats(self):
        """Test application with different phone formats"""
        phone_formats = [
            "3001234567",
            "300 123 4567",
            "300-123-4567",
            "(300) 123-4567",
            "+57 300 123 4567",
            "573001234567"
        ]
        
        for phone in phone_formats:
            application = LoanApplication(
                id=1,
                name="Test User",
                cedula="12345678",
                convenio=None,
                telefono=phone,
                fecha_nacimiento=date(1990, 1, 1)
            )
            # Note: The validation only checks if telefono is not empty/whitespace
            # More specific phone validation would be in a separate validator
            assert application.validate_application_data() == True, f"Phone '{phone}' should be valid"
    
    def test_application_with_various_convenio_formats(self):
        """Test application with different convenio formats"""
        convenio_formats = [
            "EMPRESA_ABC",
            "empresa_xyz",
            "Convenio-123",
            "PAYROLL_COMPANY_2024",
            "Gov_Entity_001",
            None  # No convenio
        ]
        
        for convenio in convenio_formats:
            application = LoanApplication(
                id=1,
                name="Test User",
                cedula="12345678",
                convenio=convenio,
                telefono="3001234567",
                fecha_nacimiento=date(1990, 1, 1)
            )
            assert application.validate_application_data() == True, f"Convenio '{convenio}' should be valid"
    
    def test_application_leap_year_birth_dates(self):
        """Test application with leap year birth dates"""
        # Test leap year birth date
        leap_year_application = LoanApplication(
            id=1,
            name="Leap Year Baby",
            cedula="12345678",
            convenio=None,
            telefono="3001234567",
            fecha_nacimiento=date(2000, 2, 29)  # Leap year
        )
        assert leap_year_application.validate_application_data() == True
        assert leap_year_application.is_adult() == True  # Should be over 18
    
    def test_application_boundary_dates(self):
        """Test application with boundary dates"""
        today = date.today()
        
        # Test very old applicant
        very_old = LoanApplication(
            id=1,
            name="Very Old Person",
            cedula="12345678",
            convenio=None,
            telefono="3001234567",
            fecha_nacimiento=date(1920, 1, 1)  # Over 100 years old
        )
        assert very_old.validate_application_data() == True
        assert very_old.is_adult() == True
        
        # Test applicant born on January 1st
        jan_first = LoanApplication(
            id=2,
            name="New Year Baby",
            cedula="87654321",
            convenio=None,
            telefono="3009876543",
            fecha_nacimiento=date(1990, 1, 1)
        )
        assert jan_first.validate_application_data() == True
        assert jan_first.is_adult() == True
        
        # Test applicant born on December 31st
        dec_last = LoanApplication(
            id=3,
            name="Year End Baby",
            cedula="11223344",
            convenio=None,
            telefono="3001111111",
            fecha_nacimiento=date(1990, 12, 31)
        )
        assert dec_last.validate_application_data() == True
        assert dec_last.is_adult() == True
    
    def test_application_data_consistency(self):
        """Test that application data remains consistent"""
        # Arrange
        original_data = {
            'id': 1,
            'name': "Consistent User",
            'cedula': "99887766",
            'convenio': "TEST_CONVENIO",
            'telefono': "3009999999",
            'fecha_nacimiento': date(1985, 7, 20)
        }
        
        application = LoanApplication(**original_data)
        
        # Act - Perform validations (should not modify data)
        application.validate_cedula()
        application.is_adult()
        application.validate_application_data()
        
        # Assert - Data should remain unchanged
        assert application.id == original_data['id']
        assert application.name == original_data['name']
        assert application.cedula == original_data['cedula']
        assert application.convenio == original_data['convenio']
        assert application.telefono == original_data['telefono']
        assert application.fecha_nacimiento == original_data['fecha_nacimiento']
    
    def test_application_created_at_timestamp(self):
        """Test that created_at timestamp is set correctly"""
        # Arrange
        before_creation = datetime.now()
        
        # Act
        application = LoanApplication(
            id=1,
            name="Timestamp Test",
            cedula="12345678",
            convenio=None,
            telefono="3001234567",
            fecha_nacimiento=date(1990, 1, 1)
        )
        
        after_creation = datetime.now()
        
        # Assert
        assert before_creation <= application.created_at <= after_creation
        assert isinstance(application.created_at, datetime)