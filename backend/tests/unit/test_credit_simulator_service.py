"""Tests for CreditSimulatorService"""
import pytest
from datetime import datetime
from unittest.mock import AsyncMock
from src.application.services.credit_simulator_service import CreditSimulatorService
from src.application.dtos.credit_simulator_dtos import (
    SimulateCreditRequest,
    CreateSimulatorConfigRequest,
    UpdateSimulatorConfigRequest
)
from src.domain.entities.credit_simulator import CreditSimulator


@pytest.fixture
def mock_repository():
    return AsyncMock()


@pytest.fixture
def service(mock_repository):
    return CreditSimulatorService(mock_repository)


@pytest.fixture
def active_config():
    return CreditSimulator(
        id=1,
        tasa_interes_mensual=0.015,
        monto_minimo=100000,
        monto_maximo=50000000,
        plazos_disponibles=[12, 24, 36, 48],
        is_active=True,
        created_at=datetime(2024, 1, 1)
    )


@pytest.fixture
def inactive_config():
    return CreditSimulator(
        id=2,
        tasa_interes_mensual=0.02,
        monto_minimo=200000,
        monto_maximo=30000000,
        plazos_disponibles=[6, 12, 24],
        is_active=False,
        created_at=datetime(2024, 1, 1)
    )


class TestSimulateCredit:
    """Tests for simulate_credit method"""

    async def test_simulate_credit_success(self, service, mock_repository, active_config):
        """Test successful credit simulation"""
        mock_repository.get_active_config.return_value = active_config
        request = SimulateCreditRequest(monto=1000000, plazo_meses=12)

        result = await service.simulate_credit(request)

        assert result.monto_solicitado == 1000000
        assert result.plazo_meses == 12
        assert result.tasa_interes_mensual == 0.015
        assert result.cuota_mensual > 0
        assert result.total_a_pagar > result.monto_solicitado
        assert result.total_intereses > 0

    async def test_simulate_credit_monto_below_minimum(self, service, mock_repository, active_config):
        """Test simulation with amount below minimum"""
        # Config has monto_minimo=100000, so we need a value below that
        # But DTO validates min 100000, so we test with config having higher min
        config_high_min = CreditSimulator(
            id=1,
            tasa_interes_mensual=0.015,
            monto_minimo=500000,  # Higher minimum
            monto_maximo=50000000,
            plazos_disponibles=[12, 24, 36, 48],
            is_active=True,
            created_at=datetime(2024, 1, 1)
        )
        mock_repository.get_active_config.return_value = config_high_min
        request = SimulateCreditRequest(monto=200000, plazo_meses=12)

        with pytest.raises(ValueError) as exc_info:
            await service.simulate_credit(request)

        assert "monto debe estar entre" in str(exc_info.value).lower()

    async def test_simulate_credit_monto_above_maximum(self, service, mock_repository, active_config):
        """Test simulation with amount above maximum"""
        mock_repository.get_active_config.return_value = active_config
        request = SimulateCreditRequest(monto=60000000, plazo_meses=12)

        with pytest.raises(ValueError) as exc_info:
            await service.simulate_credit(request)

        assert "monto debe estar entre" in str(exc_info.value).lower()

    async def test_simulate_credit_invalid_plazo(self, service, mock_repository, active_config):
        """Test simulation with invalid term"""
        mock_repository.get_active_config.return_value = active_config
        request = SimulateCreditRequest(monto=1000000, plazo_meses=6)

        with pytest.raises(ValueError) as exc_info:
            await service.simulate_credit(request)

        assert "plazo" in str(exc_info.value).lower()

    async def test_simulate_credit_no_active_config(self, service, mock_repository):
        """Test simulation when no active config exists"""
        mock_repository.get_active_config.return_value = None
        request = SimulateCreditRequest(monto=1000000, plazo_meses=12)

        with pytest.raises(ValueError) as exc_info:
            await service.simulate_credit(request)

        assert "no existe una configuración activa" in str(exc_info.value).lower()


class TestGetAllSimulatorConfigs:
    """Tests for get_all_simulator_configs method"""

    async def test_get_all_configs_success(self, service, mock_repository, active_config, inactive_config):
        """Test getting all configurations"""
        mock_repository.get_all.return_value = [active_config, inactive_config]

        result = await service.get_all_simulator_configs()

        assert len(result) == 2
        assert result[0].id == 1
        assert result[0].is_active is True
        assert result[1].id == 2
        assert result[1].is_active is False

    async def test_get_all_configs_empty(self, service, mock_repository):
        """Test getting configs when none exist"""
        mock_repository.get_all.return_value = []

        result = await service.get_all_simulator_configs()

        assert len(result) == 0


class TestUpdateSimulatorConfig:
    """Tests for update_simulator_config (create) method"""

    async def test_create_config_success(self, service, mock_repository):
        """Test successful config creation"""
        created_config = CreditSimulator(
            id=3,
            tasa_interes_mensual=0.018,
            monto_minimo=150000,
            monto_maximo=40000000,
            plazos_disponibles=[12, 24, 36],
            is_active=False,
            created_at=datetime(2024, 1, 1)
        )
        mock_repository.create.return_value = created_config
        request = CreateSimulatorConfigRequest(
            tasa_interes_mensual=0.018,
            monto_minimo=150000,
            monto_maximo=40000000,
            plazos_disponibles=[12, 24, 36],
            is_active=False
        )

        result = await service.update_simulator_config(request)

        assert result.id == 3
        assert result.tasa_interes_mensual == 0.018
        mock_repository.create.assert_called_once()

    async def test_create_config_invalid(self, service, mock_repository):
        """Test config creation with invalid data (validation fails in entity)"""
        # DTO validates monto_maximo > monto_minimo, so we test entity validation
        # by mocking a config that fails entity.validate()
        invalid_config = CreditSimulator(
            id=None,
            tasa_interes_mensual=0.018,
            monto_minimo=150000,
            monto_maximo=100000,  # Invalid: less than min
            plazos_disponibles=[12, 24, 36],
            is_active=False
        )
        request = CreateSimulatorConfigRequest(
            tasa_interes_mensual=0.018,
            monto_minimo=150000,
            monto_maximo=200000,
            plazos_disponibles=[12, 24, 36],
            is_active=False
        )
        # Mock create to return invalid config that fails validation
        mock_repository.create.return_value = invalid_config
        
        # The service validates before saving, so we need to test that path
        # Actually, the validation happens on the entity before create
        # Let's test with empty plazos which will fail entity validation
        request_empty_plazos = CreateSimulatorConfigRequest(
            tasa_interes_mensual=0.018,
            monto_minimo=150000,
            monto_maximo=200000,
            plazos_disponibles=[12],  # Valid for DTO
            is_active=False
        )
        
        # Create a config that will fail validate()
        from unittest.mock import patch, MagicMock
        with patch.object(CreditSimulator, 'validate', return_value=False):
            with pytest.raises(ValueError) as exc_info:
                await service.update_simulator_config(request_empty_plazos)
            assert "configuración inválida" in str(exc_info.value).lower()


class TestModifySimulatorConfig:
    """Tests for modify_simulator_config method"""

    async def test_modify_config_success(self, service, mock_repository, active_config):
        """Test successful config modification"""
        mock_repository.get_by_id.return_value = active_config
        updated_config = CreditSimulator(
            id=1,
            tasa_interes_mensual=0.02,
            monto_minimo=100000,
            monto_maximo=50000000,
            plazos_disponibles=[12, 24, 36, 48],
            is_active=True,
            created_at=datetime(2024, 1, 1)
        )
        mock_repository.update.return_value = updated_config
        request = UpdateSimulatorConfigRequest(tasa_interes_mensual=0.02)

        result = await service.modify_simulator_config(1, request)

        assert result.tasa_interes_mensual == 0.02
        mock_repository.update.assert_called_once()

    async def test_modify_config_not_found(self, service, mock_repository):
        """Test modification of non-existent config"""
        mock_repository.get_by_id.return_value = None
        request = UpdateSimulatorConfigRequest(tasa_interes_mensual=0.02)

        with pytest.raises(ValueError) as exc_info:
            await service.modify_simulator_config(999, request)

        assert "no encontrada" in str(exc_info.value).lower()

    async def test_modify_config_invalid_monto_range(self, service, mock_repository, active_config):
        """Test modification with invalid monto range"""
        mock_repository.get_by_id.return_value = active_config
        request = UpdateSimulatorConfigRequest(monto_maximo=50000)  # Less than existing min

        with pytest.raises(ValueError) as exc_info:
            await service.modify_simulator_config(1, request)

        assert "monto máximo debe ser mayor" in str(exc_info.value).lower()


class TestCalcularCuotaMensual:
    """Tests for _calcular_cuota_mensual method"""

    def test_calcular_cuota_with_interest(self, service):
        """Test monthly payment calculation with interest"""
        cuota = service._calcular_cuota_mensual(1000000, 0.015, 12)

        assert cuota > 0
        assert cuota > 1000000 / 12  # Should be more than simple division

    def test_calcular_cuota_zero_interest(self, service):
        """Test monthly payment calculation with zero interest"""
        cuota = service._calcular_cuota_mensual(1200000, 0, 12)

        assert cuota == 100000  # Simple division


class TestValidateSimulationParameters:
    """Tests for validate_simulation_parameters method"""

    async def test_validate_valid_parameters(self, service, mock_repository, active_config):
        """Test validation with valid parameters"""
        mock_repository.get_active_config.return_value = active_config

        result = await service.validate_simulation_parameters(1000000, 12)

        assert result["valid"] is True
        assert len(result["errors"]) == 0
        assert result["monto_valido"] is True
        assert result["plazo_valido"] is True

    async def test_validate_monto_below_min(self, service, mock_repository, active_config):
        """Test validation with amount below minimum"""
        mock_repository.get_active_config.return_value = active_config

        result = await service.validate_simulation_parameters(50000, 12)

        assert result["valid"] is False
        assert result["monto_valido"] is False

    async def test_validate_monto_above_max(self, service, mock_repository, active_config):
        """Test validation with amount above maximum"""
        mock_repository.get_active_config.return_value = active_config

        result = await service.validate_simulation_parameters(60000000, 12)

        assert result["valid"] is False
        assert result["monto_valido"] is False

    async def test_validate_invalid_plazo(self, service, mock_repository, active_config):
        """Test validation with invalid term"""
        mock_repository.get_active_config.return_value = active_config

        result = await service.validate_simulation_parameters(1000000, 6)

        assert result["valid"] is False
        assert result["plazo_valido"] is False


class TestActivateConfig:
    """Tests for activate_config method"""

    async def test_activate_config_success(self, service, mock_repository, inactive_config):
        """Test successful config activation"""
        mock_repository.get_by_id.return_value = inactive_config
        activated = CreditSimulator(
            id=2,
            tasa_interes_mensual=0.02,
            monto_minimo=200000,
            monto_maximo=30000000,
            plazos_disponibles=[6, 12, 24],
            is_active=True,
            created_at=datetime(2024, 1, 1)
        )
        mock_repository.set_active_config.return_value = activated

        result = await service.activate_config(2)

        assert result.id == 2
        assert result.is_active is True
        mock_repository.set_active_config.assert_called_once_with(2)

    async def test_activate_config_not_found(self, service, mock_repository):
        """Test activation of non-existent config"""
        mock_repository.get_by_id.return_value = None

        with pytest.raises(ValueError) as exc_info:
            await service.activate_config(999)

        assert "no encontrada" in str(exc_info.value).lower()


class TestDeleteConfig:
    """Tests for delete_config method"""

    async def test_delete_config_success(self, service, mock_repository, inactive_config):
        """Test successful config deletion"""
        mock_repository.get_by_id.return_value = inactive_config
        mock_repository.delete.return_value = True

        result = await service.delete_config(2)

        assert "eliminada exitosamente" in result["message"]
        mock_repository.delete.assert_called_once_with(2)

    async def test_delete_config_not_found(self, service, mock_repository):
        """Test deletion of non-existent config"""
        mock_repository.get_by_id.return_value = None

        with pytest.raises(ValueError) as exc_info:
            await service.delete_config(999)

        assert "no encontrada" in str(exc_info.value).lower()

    async def test_delete_active_config(self, service, mock_repository, active_config):
        """Test deletion of active config (should fail)"""
        mock_repository.get_by_id.return_value = active_config

        with pytest.raises(ValueError) as exc_info:
            await service.delete_config(1)

        assert "no se puede borrar la configuración activa" in str(exc_info.value).lower()

    async def test_delete_config_repository_error(self, service, mock_repository, inactive_config):
        """Test deletion when repository returns failure"""
        mock_repository.get_by_id.return_value = inactive_config
        mock_repository.delete.return_value = False

        with pytest.raises(ValueError) as exc_info:
            await service.delete_config(2)

        assert "error al eliminar" in str(exc_info.value).lower()
