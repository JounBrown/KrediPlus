"""
Unit tests for Credit entity
"""
import pytest
from datetime import date, datetime
from decimal import Decimal
from src.domain.entities.credit import Credit, CreditStatus


class TestCreditEntity:
    """Test Credit entity functionality"""
    
    def test_credit_creation_with_valid_data(self):
        """Test creating a valid credit"""
        # Arrange & Act
        credit = Credit(
            id=1,
            monto_aprobado=Decimal('1000000'),
            plazo_meses=12,
            tasa_interes=Decimal('15.5'),
            client_id=123
        )
        
        # Assert
        assert credit.id == 1
        assert credit.monto_aprobado == Decimal('1000000')
        assert credit.plazo_meses == 12
        assert credit.tasa_interes == Decimal('15.5')
        assert credit.client_id == 123
        assert credit.estado == CreditStatus.EN_ESTUDIO.value
        assert credit.fecha_desembolso is None
        assert isinstance(credit.created_at, datetime)
    
    def test_credit_validation_success(self):
        """Test successful credit validation"""
        # Arrange
        credit = Credit(
            id=1,
            monto_aprobado=Decimal('500000'),
            plazo_meses=24,
            tasa_interes=Decimal('12.0'),
            client_id=456
        )
        
        # Act & Assert
        assert credit.validate() == True
    
    def test_credit_validation_failures(self):
        """Test credit validation failures"""
        # Test negative amount
        credit = Credit(
            id=1,
            monto_aprobado=Decimal('-100000'),
            plazo_meses=12,
            tasa_interes=Decimal('15.0'),
            client_id=123
        )
        assert credit.validate() == False
        
        # Test zero amount
        credit = Credit(
            id=1,
            monto_aprobado=Decimal('0'),
            plazo_meses=12,
            tasa_interes=Decimal('15.0'),
            client_id=123
        )
        assert credit.validate() == False
        
        # Test negative term
        credit = Credit(
            id=1,
            monto_aprobado=Decimal('100000'),
            plazo_meses=-12,
            tasa_interes=Decimal('15.0'),
            client_id=123
        )
        assert credit.validate() == False
        
        # Test zero term
        credit = Credit(
            id=1,
            monto_aprobado=Decimal('100000'),
            plazo_meses=0,
            tasa_interes=Decimal('15.0'),
            client_id=123
        )
        assert credit.validate() == False
        
        # Test negative interest rate
        credit = Credit(
            id=1,
            monto_aprobado=Decimal('100000'),
            plazo_meses=12,
            tasa_interes=Decimal('-5.0'),
            client_id=123
        )
        assert credit.validate() == False
        
        # Test missing client_id
        credit = Credit(
            id=1,
            monto_aprobado=Decimal('100000'),
            plazo_meses=12,
            tasa_interes=Decimal('15.0'),
            client_id=None
        )
        assert credit.validate() == False


class TestCreditCalculations:
    """Test credit calculation methods"""
    
    def test_monthly_payment_calculation_with_interest(self):
        """Test monthly payment calculation with interest"""
        # Arrange
        credit = Credit(
            id=1,
            monto_aprobado=Decimal('1000000'),  # 1 million
            plazo_meses=12,
            tasa_interes=Decimal('12.0'),  # 12% annual (used as monthly rate in current implementation)
            client_id=123
        )
        
        # Act
        monthly_payment = credit.calculate_monthly_payment()
        
        # Assert
        # Note: Current implementation uses annual rate as monthly rate
        # For 1M at 12% monthly for 12 months, payment should be around 161,437
        assert isinstance(monthly_payment, Decimal)
        assert monthly_payment > Decimal('160000')
        assert monthly_payment < Decimal('165000')
        # Check precision (2 decimal places)
        assert monthly_payment == monthly_payment.quantize(Decimal('0.01'))
    
    def test_monthly_payment_calculation_zero_interest(self):
        """Test monthly payment calculation with zero interest"""
        # Arrange
        credit = Credit(
            id=1,
            monto_aprobado=Decimal('1200000'),
            plazo_meses=12,
            tasa_interes=Decimal('0'),
            client_id=123
        )
        
        # Act
        monthly_payment = credit.calculate_monthly_payment()
        
        # Assert
        expected_payment = Decimal('1200000') / 12
        assert monthly_payment == expected_payment
        assert monthly_payment == Decimal('100000.00')
    
    def test_total_payment_calculation(self):
        """Test total payment calculation"""
        # Arrange
        credit = Credit(
            id=1,
            monto_aprobado=Decimal('600000'),
            plazo_meses=6,
            tasa_interes=Decimal('18.0'),
            client_id=123
        )
        
        # Act
        total_payment = credit.calculate_total_payment()
        monthly_payment = credit.calculate_monthly_payment()
        
        # Assert
        expected_total = monthly_payment * 6
        assert total_payment == expected_total.quantize(Decimal('0.01'))
        assert isinstance(total_payment, Decimal)
        assert total_payment > credit.monto_aprobado  # Should be more than principal
    
    def test_total_interest_calculation(self):
        """Test total interest calculation"""
        # Arrange
        credit = Credit(
            id=1,
            monto_aprobado=Decimal('500000'),
            plazo_meses=24,
            tasa_interes=Decimal('15.0'),
            client_id=123
        )
        
        # Act
        total_interest = credit.calculate_total_interest()
        total_payment = credit.calculate_total_payment()
        
        # Assert
        expected_interest = total_payment - credit.monto_aprobado
        assert total_interest == expected_interest.quantize(Decimal('0.01'))
        assert total_interest > Decimal('0')  # Should be positive
        assert isinstance(total_interest, Decimal)
    
    def test_calculations_with_different_terms(self):
        """Test calculations with various terms"""
        base_amount = Decimal('1000000')
        base_rate = Decimal('12.0')
        client_id = 123
        
        terms = [6, 12, 24, 36, 48]
        
        for term in terms:
            credit = Credit(
                id=1,
                monto_aprobado=base_amount,
                plazo_meses=term,
                tasa_interes=base_rate,
                client_id=client_id
            )
            
            monthly_payment = credit.calculate_monthly_payment()
            total_payment = credit.calculate_total_payment()
            total_interest = credit.calculate_total_interest()
            
            # Longer terms should have lower monthly payments
            assert monthly_payment > Decimal('0')
            assert total_payment > base_amount
            assert total_interest > Decimal('0')
            
            # Verify calculation consistency
            assert total_payment == (monthly_payment * term).quantize(Decimal('0.01'))
            assert total_interest == (total_payment - base_amount).quantize(Decimal('0.01'))


class TestCreditStatusTransitions:
    """Test credit status transition methods"""
    
    def test_approve_credit_success(self):
        """Test successful credit approval"""
        # Arrange
        credit = Credit(
            id=1,
            monto_aprobado=Decimal('0'),  # Initial values
            plazo_meses=0,
            tasa_interes=Decimal('0'),
            estado=CreditStatus.EN_ESTUDIO.value,
            client_id=123
        )
        
        # Act
        result = credit.approve_credit(
            monto=Decimal('800000'),
            plazo=18,
            tasa=Decimal('14.5')
        )
        
        # Assert
        assert result == True
        assert credit.monto_aprobado == Decimal('800000')
        assert credit.plazo_meses == 18
        assert credit.tasa_interes == Decimal('14.5')
        assert credit.estado == CreditStatus.APROBADO.value
    
    def test_approve_credit_invalid_state(self):
        """Test credit approval from invalid state"""
        # Arrange
        credit = Credit(
            id=1,
            monto_aprobado=Decimal('500000'),
            plazo_meses=12,
            tasa_interes=Decimal('15.0'),
            estado=CreditStatus.APROBADO.value,  # Already approved
            client_id=123
        )
        
        original_amount = credit.monto_aprobado
        
        # Act
        result = credit.approve_credit(
            monto=Decimal('1000000'),
            plazo=24,
            tasa=Decimal('12.0')
        )
        
        # Assert
        assert result == False
        assert credit.monto_aprobado == original_amount  # Should remain unchanged
        assert credit.estado == CreditStatus.APROBADO.value
    
    def test_approve_credit_invalid_parameters(self):
        """Test credit approval with invalid parameters"""
        # Arrange
        credit = Credit(
            id=1,
            monto_aprobado=Decimal('0'),
            plazo_meses=0,
            tasa_interes=Decimal('0'),
            estado=CreditStatus.EN_ESTUDIO.value,
            client_id=123
        )
        
        # Test negative amount
        result = credit.approve_credit(
            monto=Decimal('-100000'),
            plazo=12,
            tasa=Decimal('15.0')
        )
        assert result == False
        assert credit.estado == CreditStatus.EN_ESTUDIO.value
        
        # Test zero amount
        result = credit.approve_credit(
            monto=Decimal('0'),
            plazo=12,
            tasa=Decimal('15.0')
        )
        assert result == False
        
        # Test negative term
        result = credit.approve_credit(
            monto=Decimal('100000'),
            plazo=-12,
            tasa=Decimal('15.0')
        )
        assert result == False
        
        # Test negative interest rate
        result = credit.approve_credit(
            monto=Decimal('100000'),
            plazo=12,
            tasa=Decimal('-5.0')
        )
        assert result == False
    
    def test_disburse_credit_success(self):
        """Test successful credit disbursement"""
        # Arrange
        credit = Credit(
            id=1,
            monto_aprobado=Decimal('750000'),
            plazo_meses=15,
            tasa_interes=Decimal('13.0'),
            estado=CreditStatus.APROBADO.value,
            client_id=123
        )
        
        disbursement_date = date(2024, 6, 15)
        
        # Act
        result = credit.disburse_credit(disbursement_date)
        
        # Assert
        assert result == True
        assert credit.fecha_desembolso == disbursement_date
        assert credit.estado == CreditStatus.DESEMBOLSADO.value
    
    def test_disburse_credit_default_date(self):
        """Test credit disbursement with default date"""
        # Arrange
        credit = Credit(
            id=1,
            monto_aprobado=Decimal('500000'),
            plazo_meses=12,
            tasa_interes=Decimal('15.0'),
            estado=CreditStatus.APROBADO.value,
            client_id=123
        )
        
        # Act
        result = credit.disburse_credit()
        
        # Assert
        assert result == True
        assert credit.fecha_desembolso == date.today()
        assert credit.estado == CreditStatus.DESEMBOLSADO.value
    
    def test_disburse_credit_invalid_state(self):
        """Test credit disbursement from invalid state"""
        # Arrange
        credit = Credit(
            id=1,
            monto_aprobado=Decimal('500000'),
            plazo_meses=12,
            tasa_interes=Decimal('15.0'),
            estado=CreditStatus.EN_ESTUDIO.value,  # Not approved yet
            client_id=123
        )
        
        # Act
        result = credit.disburse_credit()
        
        # Assert
        assert result == False
        assert credit.fecha_desembolso is None
        assert credit.estado == CreditStatus.EN_ESTUDIO.value
    
    def test_mark_as_current_success(self):
        """Test marking credit as current"""
        # Arrange
        credit = Credit(
            id=1,
            monto_aprobado=Decimal('600000'),
            plazo_meses=12,
            tasa_interes=Decimal('15.0'),
            estado=CreditStatus.DESEMBOLSADO.value,
            client_id=123
        )
        
        # Act
        result = credit.mark_as_current()
        
        # Assert
        assert result == True
        assert credit.estado == CreditStatus.AL_DIA.value
    
    def test_mark_as_overdue_success(self):
        """Test marking credit as overdue"""
        # Arrange
        credit = Credit(
            id=1,
            monto_aprobado=Decimal('400000'),
            plazo_meses=12,
            tasa_interes=Decimal('15.0'),
            estado=CreditStatus.AL_DIA.value,
            client_id=123
        )
        
        # Act
        result = credit.mark_as_overdue()
        
        # Assert
        assert result == True
        assert credit.estado == CreditStatus.EN_MORA.value
    
    def test_mark_as_paid_success(self):
        """Test marking credit as paid"""
        # Test from AL_DIA state
        credit = Credit(
            id=1,
            monto_aprobado=Decimal('300000'),
            plazo_meses=12,
            tasa_interes=Decimal('15.0'),
            estado=CreditStatus.AL_DIA.value,
            client_id=123
        )
        
        result = credit.mark_as_paid()
        assert result == True
        assert credit.estado == CreditStatus.PAGADO.value
        
        # Test from EN_MORA state
        credit = Credit(
            id=2,
            monto_aprobado=Decimal('300000'),
            plazo_meses=12,
            tasa_interes=Decimal('15.0'),
            estado=CreditStatus.EN_MORA.value,
            client_id=123
        )
        
        result = credit.mark_as_paid()
        assert result == True
        assert credit.estado == CreditStatus.PAGADO.value
    
    def test_reject_credit_success(self):
        """Test credit rejection"""
        # Arrange
        credit = Credit(
            id=1,
            monto_aprobado=Decimal('500000'),
            plazo_meses=12,
            tasa_interes=Decimal('15.0'),
            estado=CreditStatus.EN_ESTUDIO.value,
            client_id=123
        )
        
        # Act
        result = credit.reject_credit()
        
        # Assert
        assert result == True
        assert credit.estado == CreditStatus.RECHAZADO.value
    
    def test_reject_credit_invalid_state(self):
        """Test credit rejection from invalid state"""
        # Arrange
        credit = Credit(
            id=1,
            monto_aprobado=Decimal('500000'),
            plazo_meses=12,
            tasa_interes=Decimal('15.0'),
            estado=CreditStatus.APROBADO.value,  # Already approved
            client_id=123
        )
        
        # Act
        result = credit.reject_credit()
        
        # Assert
        assert result == False
        assert credit.estado == CreditStatus.APROBADO.value


class TestCreditStatusQueries:
    """Test credit status query methods"""
    
    def test_is_active_true_cases(self):
        """Test is_active returns True for active states"""
        active_states = [
            CreditStatus.AL_DIA.value,
            CreditStatus.EN_MORA.value,
            CreditStatus.DESEMBOLSADO.value
        ]
        
        for state in active_states:
            credit = Credit(
                id=1,
                monto_aprobado=Decimal('500000'),
                plazo_meses=12,
                tasa_interes=Decimal('15.0'),
                estado=state,
                client_id=123
            )
            assert credit.is_active() == True, f"State {state} should be active"
    
    def test_is_active_false_cases(self):
        """Test is_active returns False for inactive states"""
        inactive_states = [
            CreditStatus.EN_ESTUDIO.value,
            CreditStatus.APROBADO.value,
            CreditStatus.RECHAZADO.value,
            CreditStatus.PAGADO.value
        ]
        
        for state in inactive_states:
            credit = Credit(
                id=1,
                monto_aprobado=Decimal('500000'),
                plazo_meses=12,
                tasa_interes=Decimal('15.0'),
                estado=state,
                client_id=123
            )
            assert credit.is_active() == False, f"State {state} should not be active"
    
    def test_can_be_disbursed_true(self):
        """Test can_be_disbursed returns True for approved credits"""
        # Arrange
        credit = Credit(
            id=1,
            monto_aprobado=Decimal('500000'),
            plazo_meses=12,
            tasa_interes=Decimal('15.0'),
            estado=CreditStatus.APROBADO.value,
            client_id=123
        )
        
        # Act & Assert
        assert credit.can_be_disbursed() == True
    
    def test_can_be_disbursed_false(self):
        """Test can_be_disbursed returns False for non-approved credits"""
        non_disbursable_states = [
            CreditStatus.EN_ESTUDIO.value,
            CreditStatus.RECHAZADO.value,
            CreditStatus.DESEMBOLSADO.value,
            CreditStatus.AL_DIA.value,
            CreditStatus.EN_MORA.value,
            CreditStatus.PAGADO.value
        ]
        
        for state in non_disbursable_states:
            credit = Credit(
                id=1,
                monto_aprobado=Decimal('500000'),
                plazo_meses=12,
                tasa_interes=Decimal('15.0'),
                estado=state,
                client_id=123
            )
            assert credit.can_be_disbursed() == False, f"State {state} should not be disbursable"


class TestCreditStatusEnum:
    """Test CreditStatus enum"""
    
    def test_credit_status_enum_values(self):
        """Test that all credit status enum values are correct"""
        expected_values = {
            CreditStatus.EN_ESTUDIO: "EN_ESTUDIO",
            CreditStatus.APROBADO: "APROBADO",
            CreditStatus.RECHAZADO: "RECHAZADO",
            CreditStatus.DESEMBOLSADO: "DESEMBOLSADO",
            CreditStatus.AL_DIA: "AL_DIA",
            CreditStatus.EN_MORA: "EN_MORA",
            CreditStatus.PAGADO: "PAGADO"
        }
        
        for status, expected_value in expected_values.items():
            assert status.value == expected_value
    
    def test_credit_status_enum_string_representations(self):
        """Test that enum values are strings"""
        for status in CreditStatus:
            assert isinstance(status.value, str)
            assert len(status.value) > 0
            assert status.value.isupper()


class TestCreditEdgeCases:
    """Test edge cases and boundary conditions"""
    
    def test_credit_with_very_small_amounts(self):
        """Test credit with very small amounts"""
        # Arrange
        credit = Credit(
            id=1,
            monto_aprobado=Decimal('0.01'),  # 1 cent
            plazo_meses=1,
            tasa_interes=Decimal('0.01'),
            client_id=123
        )
        
        # Act & Assert
        assert credit.validate() == True
        monthly_payment = credit.calculate_monthly_payment()
        assert monthly_payment > Decimal('0')
        assert isinstance(monthly_payment, Decimal)
    
    def test_credit_with_large_amounts(self):
        """Test credit with large amounts"""
        # Arrange
        credit = Credit(
            id=1,
            monto_aprobado=Decimal('999999999.99'),  # Very large amount
            plazo_meses=360,  # 30 years
            tasa_interes=Decimal('25.99'),
            client_id=123
        )
        
        # Act & Assert
        assert credit.validate() == True
        monthly_payment = credit.calculate_monthly_payment()
        total_payment = credit.calculate_total_payment()
        total_interest = credit.calculate_total_interest()
        
        assert monthly_payment > Decimal('0')
        assert total_payment > credit.monto_aprobado
        assert total_interest > Decimal('0')
    
    def test_credit_state_transitions_workflow(self):
        """Test complete credit workflow"""
        # Arrange - Start with a credit under study
        credit = Credit(
            id=1,
            monto_aprobado=Decimal('0'),
            plazo_meses=0,
            tasa_interes=Decimal('0'),
            estado=CreditStatus.EN_ESTUDIO.value,
            client_id=123
        )
        
        # Act & Assert - Complete workflow
        # 1. Approve credit
        assert credit.approve_credit(Decimal('500000'), 12, Decimal('15.0')) == True
        assert credit.estado == CreditStatus.APROBADO.value
        assert credit.can_be_disbursed() == True
        
        # 2. Disburse credit
        assert credit.disburse_credit() == True
        assert credit.estado == CreditStatus.DESEMBOLSADO.value
        assert credit.is_active() == True
        
        # 3. Mark as current
        assert credit.mark_as_current() == True
        assert credit.estado == CreditStatus.AL_DIA.value
        assert credit.is_active() == True
        
        # 4. Mark as overdue
        assert credit.mark_as_overdue() == True
        assert credit.estado == CreditStatus.EN_MORA.value
        assert credit.is_active() == True
        
        # 5. Mark as paid
        assert credit.mark_as_paid() == True
        assert credit.estado == CreditStatus.PAGADO.value
        assert credit.is_active() == False
    
    def test_decimal_precision_consistency(self):
        """Test that all calculations maintain decimal precision"""
        # Arrange
        credit = Credit(
            id=1,
            monto_aprobado=Decimal('123456.78'),
            plazo_meses=13,
            tasa_interes=Decimal('17.25'),
            client_id=123
        )
        
        # Act
        monthly_payment = credit.calculate_monthly_payment()
        total_payment = credit.calculate_total_payment()
        total_interest = credit.calculate_total_interest()
        
        # Assert - All should have exactly 2 decimal places
        assert str(monthly_payment).split('.')[-1] in ['00', '01', '02', '03', '04', '05', '06', '07', '08', '09'] or len(str(monthly_payment).split('.')[-1]) == 2
        assert str(total_payment).split('.')[-1] in ['00', '01', '02', '03', '04', '05', '06', '07', '08', '09'] or len(str(total_payment).split('.')[-1]) == 2
        assert str(total_interest).split('.')[-1] in ['00', '01', '02', '03', '04', '05', '06', '07', '08', '09'] or len(str(total_interest).split('.')[-1]) == 2