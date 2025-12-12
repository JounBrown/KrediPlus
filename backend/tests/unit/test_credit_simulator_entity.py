"""
Unit tests for CreditSimulator entity
"""
import pytest
from datetime import datetime
from src.domain.entities.credit_simulator import CreditSimulator


class TestCreditSimulatorCreation:
    """Test CreditSimulator entity creation"""
    
    def test_credit_simulator_creation_with_defaults(self):
        """Test creating a credit simulator with default values"""
        # Arrange & Act
        simulator = CreditSimulator()
        
        # Assert
        assert simulator.id is None
        assert simulator.tasa_interes_mensual == 0.013
        assert simulator.monto_minimo == 100000
        assert simulator.monto_maximo == 100000000
        assert simulator.plazos_disponibles == [6, 12, 18, 24, 36, 48, 60, 72]
        assert simulator.is_active == False
        assert isinstance(simulator.created_at, datetime)
    
    def test_credit_simulator_creation_with_all_fields(self):
        """Test creating a credit simulator with all fields"""
        # Arrange
        created_at = datetime(2024, 1, 15, 10, 30, 0)
        custom_plazos = [12, 24, 36, 48]
        
        # Act
        simulator = CreditSimulator(
            id=123,
            tasa_interes_mensual=0.015,
            monto_minimo=200000,
            monto_maximo=50000000,
            plazos_disponibles=custom_plazos,
            is_active=True,
            created_at=created_at
        )
        
        # Assert
        assert simulator.id == 123
        assert simulator.tasa_interes_mensual == 0.015
        assert simulator.monto_minimo == 200000
        assert simulator.monto_maximo == 50000000
        assert simulator.plazos_disponibles == custom_plazos
        assert simulator.is_active == True
        assert simulator.created_at == created_at
    
    def test_credit_simulator_creation_with_partial_fields(self):
        """Test creating a credit simulator with some fields"""
        # Arrange & Act
        simulator = CreditSimulator(
            tasa_interes_mensual=0.02,
            monto_minimo=500000,
            is_active=True
        )
        
        # Assert
        assert simulator.id is None
        assert simulator.tasa_interes_mensual == 0.02
        assert simulator.monto_minimo == 500000
        assert simulator.monto_maximo == 100000000  # Default
        assert simulator.plazos_disponibles == [6, 12, 18, 24, 36, 48, 60, 72]  # Default
        assert simulator.is_active == True
        assert isinstance(simulator.created_at, datetime)


class TestCreditSimulatorValidation:
    """Test CreditSimulator validation methods"""
    
    def test_validate_valid_simulator(self):
        """Test validation with valid simulator data"""
        # Arrange
        simulator = CreditSimulator(
            tasa_interes_mensual=0.015,
            monto_minimo=100000,
            monto_maximo=10000000,
            plazos_disponibles=[12, 24, 36],
            is_active=True
        )
        
        # Act & Assert
        assert simulator.validate() == True
    
    def test_validate_invalid_interest_rate_negative(self):
        """Test validation with negative interest rate"""
        # Arrange
        simulator = CreditSimulator(
            tasa_interes_mensual=-0.01,
            monto_minimo=100000,
            monto_maximo=10000000,
            plazos_disponibles=[12, 24, 36]
        )
        
        # Act & Assert
        assert simulator.validate() == False
    
    def test_validate_invalid_interest_rate_zero(self):
        """Test validation with zero interest rate"""
        # Arrange
        simulator = CreditSimulator(
            tasa_interes_mensual=0.0,
            monto_minimo=100000,
            monto_maximo=10000000,
            plazos_disponibles=[12, 24, 36]
        )
        
        # Act & Assert
        assert simulator.validate() == False
    
    def test_validate_invalid_interest_rate_too_high(self):
        """Test validation with interest rate too high"""
        # Arrange
        simulator = CreditSimulator(
            tasa_interes_mensual=0.25,  # 25% monthly (too high)
            monto_minimo=100000,
            monto_maximo=10000000,
            plazos_disponibles=[12, 24, 36]
        )
        
        # Act & Assert
        assert simulator.validate() == False
    
    def test_validate_valid_interest_rate_boundary_values(self):
        """Test validation with boundary interest rate values"""
        # Test minimum valid rate (just above 0)
        simulator1 = CreditSimulator(
            tasa_interes_mensual=0.001,
            monto_minimo=100000,
            monto_maximo=10000000,
            plazos_disponibles=[12, 24, 36]
        )
        assert simulator1.validate() == True
        
        # Test maximum valid rate (exactly 0.2)
        simulator2 = CreditSimulator(
            tasa_interes_mensual=0.2,
            monto_minimo=100000,
            monto_maximo=10000000,
            plazos_disponibles=[12, 24, 36]
        )
        assert simulator2.validate() == True
    
    def test_validate_invalid_amounts_negative(self):
        """Test validation with negative amounts"""
        # Negative minimum amount
        simulator1 = CreditSimulator(
            tasa_interes_mensual=0.015,
            monto_minimo=-100000,
            monto_maximo=10000000,
            plazos_disponibles=[12, 24, 36]
        )
        assert simulator1.validate() == False
        
        # Negative maximum amount
        simulator2 = CreditSimulator(
            tasa_interes_mensual=0.015,
            monto_minimo=100000,
            monto_maximo=-10000000,
            plazos_disponibles=[12, 24, 36]
        )
        assert simulator2.validate() == False
    
    def test_validate_invalid_amounts_zero(self):
        """Test validation with zero amounts"""
        # Zero minimum amount
        simulator1 = CreditSimulator(
            tasa_interes_mensual=0.015,
            monto_minimo=0,
            monto_maximo=10000000,
            plazos_disponibles=[12, 24, 36]
        )
        assert simulator1.validate() == False
        
        # Zero maximum amount
        simulator2 = CreditSimulator(
            tasa_interes_mensual=0.015,
            monto_minimo=100000,
            monto_maximo=0,
            plazos_disponibles=[12, 24, 36]
        )
        assert simulator2.validate() == False
    
    def test_validate_invalid_amount_relationship(self):
        """Test validation when minimum >= maximum amount"""
        # Minimum equals maximum
        simulator1 = CreditSimulator(
            tasa_interes_mensual=0.015,
            monto_minimo=1000000,
            monto_maximo=1000000,
            plazos_disponibles=[12, 24, 36]
        )
        assert simulator1.validate() == False
        
        # Minimum greater than maximum
        simulator2 = CreditSimulator(
            tasa_interes_mensual=0.015,
            monto_minimo=2000000,
            monto_maximo=1000000,
            plazos_disponibles=[12, 24, 36]
        )
        assert simulator2.validate() == False
    
    def test_validate_invalid_plazos_empty(self):
        """Test validation with empty plazos list"""
        # Create simulator and then manually set empty list (bypassing constructor logic)
        simulator1 = CreditSimulator(
            tasa_interes_mensual=0.015,
            monto_minimo=100000,
            monto_maximo=10000000,
            plazos_disponibles=[12, 24]  # Valid initially
        )
        simulator1.plazos_disponibles = []  # Manually set to empty
        assert simulator1.validate() == False
        
        # None plazos (manually set after construction)
        simulator2 = CreditSimulator(
            tasa_interes_mensual=0.015,
            monto_minimo=100000,
            monto_maximo=10000000,
            plazos_disponibles=[12, 24]  # Valid initially
        )
        simulator2.plazos_disponibles = None  # Manually set to None
        assert simulator2.validate() == False
    
    def test_validate_invalid_plazos_values(self):
        """Test validation with invalid plazo values"""
        # Negative plazos
        simulator1 = CreditSimulator(
            tasa_interes_mensual=0.015,
            monto_minimo=100000,
            monto_maximo=10000000,
            plazos_disponibles=[12, -24, 36]
        )
        assert simulator1.validate() == False
        
        # Zero plazos
        simulator2 = CreditSimulator(
            tasa_interes_mensual=0.015,
            monto_minimo=100000,
            monto_maximo=10000000,
            plazos_disponibles=[12, 0, 36]
        )
        assert simulator2.validate() == False
        
        # Plazos too high (> 120 months)
        simulator3 = CreditSimulator(
            tasa_interes_mensual=0.015,
            monto_minimo=100000,
            monto_maximo=10000000,
            plazos_disponibles=[12, 24, 150]
        )
        assert simulator3.validate() == False
    
    def test_validate_valid_plazos_boundary_values(self):
        """Test validation with boundary plazo values"""
        # Minimum valid plazo (1 month)
        simulator1 = CreditSimulator(
            tasa_interes_mensual=0.015,
            monto_minimo=100000,
            monto_maximo=10000000,
            plazos_disponibles=[1, 12, 24]
        )
        assert simulator1.validate() == True
        
        # Maximum valid plazo (120 months)
        simulator2 = CreditSimulator(
            tasa_interes_mensual=0.015,
            monto_minimo=100000,
            monto_maximo=10000000,
            plazos_disponibles=[12, 24, 120]
        )
        assert simulator2.validate() == True


class TestCreditSimulatorCalculations:
    """Test CreditSimulator calculation methods"""
    
    def test_calculate_monthly_payment_valid_inputs(self):
        """Test monthly payment calculation with valid inputs"""
        # Arrange
        simulator = CreditSimulator(
            tasa_interes_mensual=0.02,  # 2% monthly
            monto_minimo=100000,
            monto_maximo=10000000,
            plazos_disponibles=[12, 24, 36]
        )
        
        # Act
        payment = simulator.calculate_monthly_payment(1000000, 12)
        
        # Assert
        # Using formula: P * (r * (1+r)^n) / ((1+r)^n - 1)
        # Where P=1000000, r=0.02, n=12
        expected = 1000000 * (0.02 * (1.02**12)) / ((1.02**12) - 1)
        expected = round(expected, 2)
        
        assert payment == expected
        assert isinstance(payment, float)
    
    def test_calculate_monthly_payment_zero_interest(self):
        """Test monthly payment calculation with zero interest rate"""
        # Arrange
        simulator = CreditSimulator(
            tasa_interes_mensual=0.0,
            monto_minimo=100000,
            monto_maximo=10000000,
            plazos_disponibles=[12, 24, 36]
        )
        
        # Act
        payment = simulator.calculate_monthly_payment(1200000, 12)
        
        # Assert
        # With zero interest, payment should be monto / plazo_meses
        expected = 1200000 / 12
        assert payment == expected
        assert payment == 100000.0
    
    def test_calculate_monthly_payment_different_amounts(self):
        """Test monthly payment calculation with different amounts"""
        # Arrange
        simulator = CreditSimulator(
            tasa_interes_mensual=0.015,  # 1.5% monthly
            monto_minimo=100000,
            monto_maximo=10000000,
            plazos_disponibles=[12, 24, 36]
        )
        
        test_cases = [
            (500000, 12),
            (1000000, 24),
            (2000000, 36)
        ]
        
        for monto, plazo in test_cases:
            # Act
            payment = simulator.calculate_monthly_payment(monto, plazo)
            
            # Assert
            assert payment > 0
            assert isinstance(payment, float)
            # Payment should be greater than simple division (due to interest)
            assert payment > monto / plazo
    
    def test_calculate_monthly_payment_invalid_plazo(self):
        """Test monthly payment calculation with invalid plazo"""
        # Arrange
        simulator = CreditSimulator(
            tasa_interes_mensual=0.015,
            monto_minimo=100000,
            monto_maximo=10000000,
            plazos_disponibles=[12, 24, 36]
        )
        
        # Act & Assert
        with pytest.raises(ValueError, match="Plazo 18 no está disponible"):
            simulator.calculate_monthly_payment(1000000, 18)
        
        with pytest.raises(ValueError, match="Plazo 48 no está disponible"):
            simulator.calculate_monthly_payment(1000000, 48)
    
    def test_calculate_monthly_payment_amount_too_low(self):
        """Test monthly payment calculation with amount below minimum"""
        # Arrange
        simulator = CreditSimulator(
            tasa_interes_mensual=0.015,
            monto_minimo=500000,
            monto_maximo=10000000,
            plazos_disponibles=[12, 24, 36]
        )
        
        # Act & Assert
        with pytest.raises(ValueError, match="Monto debe estar entre 500000 y 10000000"):
            simulator.calculate_monthly_payment(400000, 12)
    
    def test_calculate_monthly_payment_amount_too_high(self):
        """Test monthly payment calculation with amount above maximum"""
        # Arrange
        simulator = CreditSimulator(
            tasa_interes_mensual=0.015,
            monto_minimo=100000,
            monto_maximo=5000000,
            plazos_disponibles=[12, 24, 36]
        )
        
        # Act & Assert
        with pytest.raises(ValueError, match="Monto debe estar entre 100000 y 5000000"):
            simulator.calculate_monthly_payment(6000000, 12)
    
    def test_calculate_monthly_payment_rounding(self):
        """Test that monthly payment is properly rounded to 2 decimal places"""
        # Arrange
        simulator = CreditSimulator(
            tasa_interes_mensual=0.0123456,  # Rate that will produce many decimals
            monto_minimo=100000,
            monto_maximo=10000000,
            plazos_disponibles=[13]  # Odd number to create more decimals
        )
        
        # Act
        payment = simulator.calculate_monthly_payment(1000000, 13)
        
        # Assert
        # Check that result has at most 2 decimal places
        assert len(str(payment).split('.')[-1]) <= 2
        assert isinstance(payment, float)


class TestCreditSimulatorBusinessLogic:
    """Test CreditSimulator business logic and workflows"""
    
    def test_standard_credit_simulator_configuration(self):
        """Test standard credit simulator configuration"""
        # Arrange
        simulator = CreditSimulator(
            tasa_interes_mensual=0.013,  # 1.3% monthly (typical Colombian rate)
            monto_minimo=100000,         # 100k COP minimum
            monto_maximo=100000000,      # 100M COP maximum
            plazos_disponibles=[6, 12, 18, 24, 36, 48, 60, 72],
            is_active=True
        )
        
        # Act & Assert
        assert simulator.validate() == True
        assert simulator.is_active == True
        
        # Test typical loan scenarios
        payment_6m = simulator.calculate_monthly_payment(1000000, 6)
        payment_12m = simulator.calculate_monthly_payment(1000000, 12)
        payment_24m = simulator.calculate_monthly_payment(1000000, 24)
        
        # Longer terms should have lower monthly payments
        assert payment_6m > payment_12m > payment_24m
    
    def test_premium_credit_simulator_configuration(self):
        """Test premium credit simulator with better rates"""
        # Arrange
        premium_simulator = CreditSimulator(
            tasa_interes_mensual=0.01,   # 1% monthly (better rate)
            monto_minimo=500000,         # Higher minimum
            monto_maximo=200000000,      # Higher maximum
            plazos_disponibles=[12, 24, 36, 48, 60, 72, 84, 96],
            is_active=True
        )
        
        # Act & Assert
        assert premium_simulator.validate() == True
        
        # Compare with standard simulator
        standard_simulator = CreditSimulator()
        
        premium_payment = premium_simulator.calculate_monthly_payment(5000000, 24)
        # Can't compare directly with standard due to different amount limits
        # But premium should have lower payment due to better rate
        assert premium_payment > 0
    
    def test_short_term_credit_simulator(self):
        """Test short-term credit simulator configuration"""
        # Arrange
        short_term_simulator = CreditSimulator(
            tasa_interes_mensual=0.025,  # Higher rate for short term
            monto_minimo=50000,          # Lower minimum
            monto_maximo=5000000,        # Lower maximum
            plazos_disponibles=[3, 6, 9, 12],  # Short terms only
            is_active=True
        )
        
        # Act & Assert
        assert short_term_simulator.validate() == True
        
        # Test short-term calculations
        payment_3m = short_term_simulator.calculate_monthly_payment(500000, 3)
        payment_6m = short_term_simulator.calculate_monthly_payment(500000, 6)
        payment_12m = short_term_simulator.calculate_monthly_payment(500000, 12)
        
        assert payment_3m > payment_6m > payment_12m
    
    def test_simulator_activation_workflow(self):
        """Test simulator activation and deactivation workflow"""
        # Arrange
        simulator = CreditSimulator(
            tasa_interes_mensual=0.015,
            monto_minimo=100000,
            monto_maximo=10000000,
            plazos_disponibles=[12, 24, 36],
            is_active=False  # Start inactive
        )
        
        # Act & Assert
        assert simulator.validate() == True
        assert simulator.is_active == False
        
        # Activate simulator
        simulator.is_active = True
        assert simulator.is_active == True
        assert simulator.validate() == True


class TestCreditSimulatorEdgeCases:
    """Test edge cases and boundary conditions"""
    
    def test_very_small_amounts(self):
        """Test calculations with very small amounts"""
        # Arrange
        simulator = CreditSimulator(
            tasa_interes_mensual=0.01,
            monto_minimo=1000,  # Very small minimum
            monto_maximo=1000000,
            plazos_disponibles=[12, 24]
        )
        
        # Act
        payment = simulator.calculate_monthly_payment(1000, 12)
        
        # Assert
        assert payment > 0
        assert payment < 100  # Should be a small payment
        assert isinstance(payment, float)
    
    def test_very_large_amounts(self):
        """Test calculations with very large amounts"""
        # Arrange
        simulator = CreditSimulator(
            tasa_interes_mensual=0.01,
            monto_minimo=1000000,
            monto_maximo=1000000000,  # 1 billion
            plazos_disponibles=[60, 72, 84]
        )
        
        # Act
        payment = simulator.calculate_monthly_payment(500000000, 60)  # 500M over 5 years
        
        # Assert
        assert payment > 0
        assert payment > 8000000  # Should be a large payment
        assert isinstance(payment, float)
    
    def test_many_plazos_available(self):
        """Test simulator with many available plazos"""
        # Arrange
        many_plazos = list(range(6, 121, 6))  # Every 6 months from 6 to 120
        simulator = CreditSimulator(
            tasa_interes_mensual=0.015,
            monto_minimo=100000,
            monto_maximo=10000000,
            plazos_disponibles=many_plazos
        )
        
        # Act & Assert
        assert simulator.validate() == True
        assert len(simulator.plazos_disponibles) == 20  # 6, 12, 18, ..., 120
        
        # Test calculation with various plazos
        for plazo in [6, 30, 60, 90, 120]:
            payment = simulator.calculate_monthly_payment(1000000, plazo)
            assert payment > 0
    
    def test_single_plazo_available(self):
        """Test simulator with only one plazo available"""
        # Arrange
        simulator = CreditSimulator(
            tasa_interes_mensual=0.02,
            monto_minimo=100000,
            monto_maximo=10000000,
            plazos_disponibles=[24]  # Only 24 months
        )
        
        # Act & Assert
        assert simulator.validate() == True
        
        # Should work with the available plazo
        payment = simulator.calculate_monthly_payment(1000000, 24)
        assert payment > 0
        
        # Should fail with unavailable plazo
        with pytest.raises(ValueError):
            simulator.calculate_monthly_payment(1000000, 12)
    
    def test_created_at_edge_cases(self):
        """Test created_at with various datetime values"""
        # Test very old date
        old_date = datetime(1970, 1, 1, 0, 0, 0)
        simulator1 = CreditSimulator(
            tasa_interes_mensual=0.015,
            monto_minimo=100000,
            monto_maximo=10000000,
            plazos_disponibles=[12, 24],
            created_at=old_date
        )
        assert simulator1.validate() == True
        assert simulator1.created_at == old_date
        
        # Test future date
        future_date = datetime(2030, 12, 31, 23, 59, 59)
        simulator2 = CreditSimulator(
            tasa_interes_mensual=0.015,
            monto_minimo=100000,
            monto_maximo=10000000,
            plazos_disponibles=[12, 24],
            created_at=future_date
        )
        assert simulator2.validate() == True
        assert simulator2.created_at == future_date
    
    def test_calculation_precision_edge_cases(self):
        """Test calculation precision with edge case values"""
        # Test with very small interest rate
        simulator1 = CreditSimulator(
            tasa_interes_mensual=0.0001,  # 0.01% monthly
            monto_minimo=100000,
            monto_maximo=10000000,
            plazos_disponibles=[12]
        )
        
        payment1 = simulator1.calculate_monthly_payment(1000000, 12)
        # With very small interest, should be close to simple division
        simple_payment = 1000000 / 12
        assert abs(payment1 - simple_payment) < 1000  # Small difference
        
        # Test with high interest rate
        simulator2 = CreditSimulator(
            tasa_interes_mensual=0.19,  # 19% monthly (near maximum)
            monto_minimo=100000,
            monto_maximo=10000000,
            plazos_disponibles=[12]
        )
        
        payment2 = simulator2.calculate_monthly_payment(1000000, 12)
        # With high interest, should be much higher than simple division
        assert payment2 > simple_payment * 1.5
    
    def test_validation_immutability(self):
        """Test that validation and calculation methods don't modify simulator data"""
        # Arrange
        original_data = {
            'id': 123,
            'tasa_interes_mensual': 0.015,
            'monto_minimo': 100000,
            'monto_maximo': 10000000,
            'plazos_disponibles': [12, 24, 36],
            'is_active': True,
            'created_at': datetime(2024, 1, 1, 12, 0, 0)
        }
        
        simulator = CreditSimulator(**original_data)
        
        # Act - Call methods multiple times
        for _ in range(5):
            simulator.validate()
            simulator.calculate_monthly_payment(1000000, 12)
        
        # Assert - Data should remain unchanged
        assert simulator.id == original_data['id']
        assert simulator.tasa_interes_mensual == original_data['tasa_interes_mensual']
        assert simulator.monto_minimo == original_data['monto_minimo']
        assert simulator.monto_maximo == original_data['monto_maximo']
        assert simulator.plazos_disponibles == original_data['plazos_disponibles']
        assert simulator.is_active == original_data['is_active']
        assert simulator.created_at == original_data['created_at']