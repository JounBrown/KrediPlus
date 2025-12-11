"""
Unit tests for Credit Service
"""
import pytest
from unittest.mock import AsyncMock, MagicMock
from datetime import datetime, date
from decimal import Decimal

from src.application.services.credit_service import CreditService
from src.domain.entities.credit import Credit, CreditStatus
from src.application.dtos.credit_dtos import CreateCreditRequest, UpdateCreditRequest


class TestCreditService:
    """Test CreditService functionality"""
    
    def setup_method(self):
        """Setup test fixtures"""
        self.mock_repository = MagicMock()
        self.service = CreditService(self.mock_repository)
        
        self.sample_credit = Credit(
            id=1,
            client_id=100,
            monto_aprobado=Decimal("5000000"),
            plazo_meses=12,
            tasa_interes=Decimal("1.5"),
            estado=CreditStatus.EN_ESTUDIO.value,
            fecha_desembolso=None,
            created_at=datetime.now()
        )


class TestCreateCredit(TestCreditService):
    """Test create_credit method"""
    
    @pytest.mark.asyncio
    async def test_create_credit_success(self):
        """Test successful credit creation"""
        request = CreateCreditRequest(
            client_id=100,
            monto_aprobado=Decimal("5000000"),
            plazo_meses=12,
            tasa_interes=Decimal("1.5"),
            fecha_desembolso=None
        )
        
        self.mock_repository.create = AsyncMock(return_value=self.sample_credit)
        
        result = await self.service.create_credit(request)
        
        assert result is not None
        assert result.id == 1
        assert result.client_id == 100
        assert result.monto_aprobado == Decimal("5000000")
        assert result.plazo_meses == 12
        self.mock_repository.create.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_create_credit_with_disbursement_date(self):
        """Test credit creation with disbursement date"""
        disbursement_date = date(2024, 6, 15)
        request = CreateCreditRequest(
            client_id=100,
            monto_aprobado=Decimal("3000000"),
            plazo_meses=24,
            tasa_interes=Decimal("1.2"),
            fecha_desembolso=disbursement_date
        )
        
        credit_with_date = Credit(
            id=2,
            client_id=100,
            monto_aprobado=Decimal("3000000"),
            plazo_meses=24,
            tasa_interes=Decimal("1.2"),
            estado=CreditStatus.EN_ESTUDIO.value,
            fecha_desembolso=disbursement_date,
            created_at=datetime.now()
        )
        
        self.mock_repository.create = AsyncMock(return_value=credit_with_date)
        
        result = await self.service.create_credit(request)
        
        assert result.fecha_desembolso == disbursement_date
    
    @pytest.mark.asyncio
    async def test_create_credit_repository_error(self):
        """Test credit creation with repository error"""
        request = CreateCreditRequest(
            client_id=100,
            monto_aprobado=Decimal("5000000"),
            plazo_meses=12,
            tasa_interes=Decimal("1.5"),
            fecha_desembolso=None
        )
        
        self.mock_repository.create = AsyncMock(side_effect=Exception("Database error"))
        
        with pytest.raises(Exception) as exc_info:
            await self.service.create_credit(request)
        
        assert "Error al crear el crédito" in str(exc_info.value)


class TestGetCreditById(TestCreditService):
    """Test get_credit_by_id method"""
    
    @pytest.mark.asyncio
    async def test_get_credit_by_id_success(self):
        """Test successful credit retrieval"""
        self.mock_repository.get_by_id = AsyncMock(return_value=self.sample_credit)
        
        result = await self.service.get_credit_by_id(1)
        
        assert result is not None
        assert result.id == 1
        assert result.client_id == 100
        self.mock_repository.get_by_id.assert_called_once_with(1)
    
    @pytest.mark.asyncio
    async def test_get_credit_by_id_not_found(self):
        """Test credit retrieval when not found"""
        self.mock_repository.get_by_id = AsyncMock(return_value=None)
        
        result = await self.service.get_credit_by_id(999)
        
        assert result is None


class TestUpdateCredit(TestCreditService):
    """Test update_credit method"""
    
    @pytest.mark.asyncio
    async def test_update_credit_success(self):
        """Test successful credit update"""
        request = UpdateCreditRequest(
            monto_aprobado=Decimal("6000000"),
            plazo_meses=18
        )
        
        updated_credit = Credit(
            id=1,
            client_id=100,
            monto_aprobado=Decimal("6000000"),
            plazo_meses=18,
            tasa_interes=Decimal("1.5"),
            estado=CreditStatus.EN_ESTUDIO.value,
            fecha_desembolso=None,
            created_at=datetime.now()
        )
        
        self.mock_repository.get_by_id = AsyncMock(return_value=self.sample_credit)
        self.mock_repository.update = AsyncMock(return_value=updated_credit)
        
        result = await self.service.update_credit(1, request)
        
        assert result.monto_aprobado == Decimal("6000000")
        assert result.plazo_meses == 18
    
    @pytest.mark.asyncio
    async def test_update_credit_not_found(self):
        """Test update when credit not found"""
        request = UpdateCreditRequest(monto_aprobado=Decimal("6000000"))
        
        self.mock_repository.get_by_id = AsyncMock(return_value=None)
        
        with pytest.raises(ValueError) as exc_info:
            await self.service.update_credit(999, request)
        
        assert "no encontrado" in str(exc_info.value)
    
    @pytest.mark.asyncio
    async def test_update_credit_status(self):
        """Test updating credit status"""
        request = UpdateCreditRequest(estado=CreditStatus.APROBADO)
        
        updated_credit = Credit(
            id=1,
            client_id=100,
            monto_aprobado=Decimal("5000000"),
            plazo_meses=12,
            tasa_interes=Decimal("1.5"),
            estado=CreditStatus.APROBADO.value,
            fecha_desembolso=None,
            created_at=datetime.now()
        )
        
        self.mock_repository.get_by_id = AsyncMock(return_value=self.sample_credit)
        self.mock_repository.update = AsyncMock(return_value=updated_credit)
        
        result = await self.service.update_credit(1, request)
        
        assert result.estado == CreditStatus.APROBADO.value
    
    @pytest.mark.asyncio
    async def test_update_credit_repository_error(self):
        """Test update with repository error"""
        request = UpdateCreditRequest(monto_aprobado=Decimal("6000000"))
        
        self.mock_repository.get_by_id = AsyncMock(return_value=self.sample_credit)
        self.mock_repository.update = AsyncMock(side_effect=Exception("Database error"))
        
        with pytest.raises(Exception) as exc_info:
            await self.service.update_credit(1, request)
        
        assert "Error al actualizar el crédito" in str(exc_info.value)


class TestDeleteCredit(TestCreditService):
    """Test delete_credit method"""
    
    @pytest.mark.asyncio
    async def test_delete_credit_success(self):
        """Test successful credit deletion"""
        self.mock_repository.get_by_id = AsyncMock(return_value=self.sample_credit)
        self.mock_repository.delete = AsyncMock(return_value=True)
        
        result = await self.service.delete_credit(1)
        
        assert result is True
        self.mock_repository.delete.assert_called_once_with(1)
    
    @pytest.mark.asyncio
    async def test_delete_credit_not_found(self):
        """Test deletion when credit not found"""
        self.mock_repository.get_by_id = AsyncMock(return_value=None)
        
        result = await self.service.delete_credit(999)
        
        assert result is False
    
    @pytest.mark.asyncio
    async def test_delete_credit_repository_error(self):
        """Test deletion with repository error"""
        self.mock_repository.get_by_id = AsyncMock(return_value=self.sample_credit)
        self.mock_repository.delete = AsyncMock(side_effect=Exception("Database error"))
        
        with pytest.raises(Exception) as exc_info:
            await self.service.delete_credit(1)
        
        assert "Error al eliminar el crédito" in str(exc_info.value)


class TestGetCreditsByClient(TestCreditService):
    """Test get_credits_by_client method"""
    
    @pytest.mark.asyncio
    async def test_get_credits_by_client_success(self):
        """Test successful retrieval of client credits"""
        credits = [
            self.sample_credit,
            Credit(
                id=2,
                client_id=100,
                monto_aprobado=Decimal("3000000"),
                plazo_meses=6,
                tasa_interes=Decimal("1.8"),
                estado=CreditStatus.APROBADO.value,
                fecha_desembolso=date(2024, 1, 15),
                created_at=datetime.now()
            )
        ]
        
        self.mock_repository.get_by_client_id = AsyncMock(return_value=credits)
        
        result = await self.service.get_credits_by_client(100)
        
        assert len(result) == 2
        assert result[0].id == 1
        assert result[1].id == 2
    
    @pytest.mark.asyncio
    async def test_get_credits_by_client_empty(self):
        """Test retrieval when client has no credits"""
        self.mock_repository.get_by_client_id = AsyncMock(return_value=[])
        
        result = await self.service.get_credits_by_client(100)
        
        assert len(result) == 0
    
    @pytest.mark.asyncio
    async def test_get_credits_by_client_repository_error(self):
        """Test retrieval with repository error"""
        self.mock_repository.get_by_client_id = AsyncMock(side_effect=Exception("Database error"))
        
        with pytest.raises(Exception) as exc_info:
            await self.service.get_credits_by_client(100)
        
        assert "Error al obtener créditos del cliente" in str(exc_info.value)
