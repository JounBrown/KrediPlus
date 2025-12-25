"""
Unit tests for Credit Repository
"""
import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from datetime import date, datetime
from decimal import Decimal
from sqlalchemy.ext.asyncio import AsyncSession

from src.infrastructure.outbound.database.credit_repository import SupabaseCreditRepository
from src.infrastructure.outbound.database.models import CreditModel, EstadoCreditoEnum
from src.domain.entities.credit import Credit, CreditStatus


class TestSupabaseCreditRepository:
    """Test SupabaseCreditRepository functionality"""
    
    def setup_method(self):
        """Setup test fixtures"""
        self.mock_db = AsyncMock(spec=AsyncSession)
        self.repository = SupabaseCreditRepository(self.mock_db)
        
        # Sample credit entity
        self.sample_credit = Credit(
            id=1,
            client_id=1,
            monto_aprobado=Decimal('1000000'),
            plazo_meses=12,
            tasa_interes=Decimal('15.5'),
            estado=CreditStatus.EN_ESTUDIO.value,
            fecha_desembolso=None,
            created_at=datetime(2024, 1, 15, 10, 30, 0)
        )
        
        # Sample credit model
        self.sample_model = CreditModel(
            id=1,
            client_id=1,
            monto_aprobado=Decimal('1000000'),
            plazo_meses=12,
            tasa_interes=Decimal('15.5'),
            estado=EstadoCreditoEnum.EN_ESTUDIO,
            fecha_desembolso=None,
            created_at=datetime(2024, 1, 15, 10, 30, 0)
        )


class TestModelEntityConversion(TestSupabaseCreditRepository):
    """Test model to entity conversion methods"""
    
    def test_model_to_entity_conversion(self):
        """Test converting database model to domain entity"""
        # Act
        entity = self.repository._model_to_entity(self.sample_model)
        
        # Assert
        assert isinstance(entity, Credit)
        assert entity.id == self.sample_model.id
        assert entity.client_id == self.sample_model.client_id
        assert entity.monto_aprobado == self.sample_model.monto_aprobado
        assert entity.plazo_meses == self.sample_model.plazo_meses
        assert entity.tasa_interes == self.sample_model.tasa_interes
        assert entity.estado == self.sample_model.estado.value
        assert entity.fecha_desembolso == self.sample_model.fecha_desembolso
        assert entity.created_at == self.sample_model.created_at
    
    def test_model_to_entity_with_string_estado(self):
        """Test model to entity conversion when estado is already a string"""
        # Arrange
        model_with_string_estado = CreditModel(
            id=1,
            client_id=1,
            monto_aprobado=Decimal('500000'),
            plazo_meses=24,
            tasa_interes=Decimal('12.0'),
            estado="APROBADO",  # String instead of enum
            fecha_desembolso=date(2024, 6, 15),
            created_at=datetime.now()
        )
        
        # Act
        entity = self.repository._model_to_entity(model_with_string_estado)
        
        # Assert
        assert entity.estado == "APROBADO"
    
    def test_entity_to_model_conversion(self):
        """Test converting domain entity to database model"""
        # Act
        model = self.repository._entity_to_model(self.sample_credit)
        
        # Assert
        assert isinstance(model, CreditModel)
        assert model.id == self.sample_credit.id
        assert model.client_id == self.sample_credit.client_id
        assert model.monto_aprobado == self.sample_credit.monto_aprobado
        assert model.plazo_meses == self.sample_credit.plazo_meses
        assert model.tasa_interes == self.sample_credit.tasa_interes
        assert model.estado == EstadoCreditoEnum.EN_ESTUDIO
        assert model.fecha_desembolso == self.sample_credit.fecha_desembolso
        assert model.created_at == self.sample_credit.created_at
    
    def test_entity_to_model_with_none_created_at(self):
        """Test entity to model conversion when created_at is None"""
        # Arrange
        credit_without_created_at = Credit(
            id=1,
            client_id=1,
            monto_aprobado=Decimal('500000'),
            plazo_meses=12,
            tasa_interes=Decimal('15.0'),
            estado=CreditStatus.APROBADO.value,
            created_at=None
        )
        
        # Act
        model = self.repository._entity_to_model(credit_without_created_at)
        
        # Assert - created_at should be set to current time (not None)
        assert model.created_at is not None
        assert isinstance(model.created_at, datetime)
    
    def test_entity_to_model_enum_conversion(self):
        """Test that all credit status values convert properly to enum"""
        # Arrange
        status_mappings = [
            (CreditStatus.EN_ESTUDIO.value, EstadoCreditoEnum.EN_ESTUDIO),
            (CreditStatus.APROBADO.value, EstadoCreditoEnum.APROBADO),
            (CreditStatus.RECHAZADO.value, EstadoCreditoEnum.RECHAZADO),
            (CreditStatus.DESEMBOLSADO.value, EstadoCreditoEnum.DESEMBOLSADO),
            (CreditStatus.AL_DIA.value, EstadoCreditoEnum.AL_DIA),
            (CreditStatus.EN_MORA.value, EstadoCreditoEnum.EN_MORA),
            (CreditStatus.PAGADO.value, EstadoCreditoEnum.PAGADO)
        ]
        
        for status_string, expected_enum in status_mappings:
            # Arrange
            credit = Credit(
                id=1,
                client_id=1,
                monto_aprobado=Decimal('500000'),
                plazo_meses=12,
                tasa_interes=Decimal('15.0'),
                estado=status_string,
                created_at=datetime.now()
            )
            
            # Act
            model = self.repository._entity_to_model(credit)
            
            # Assert
            assert model.estado == expected_enum


class TestCreateCredit(TestSupabaseCreditRepository):
    """Test create credit functionality"""
    
    @pytest.mark.asyncio
    async def test_create_credit_success(self):
        """Test successful credit creation"""
        # Arrange
        new_credit = Credit(
            id=None,  # New credit without ID
            client_id=1,
            monto_aprobado=Decimal('750000'),
            plazo_meses=18,
            tasa_interes=Decimal('14.0'),
            estado=CreditStatus.EN_ESTUDIO.value,
            fecha_desembolso=None,
            created_at=None
        )
        
        # Mock the model that will be created
        created_model = CreditModel(
            id=2,  # Database assigns ID
            client_id=1,
            monto_aprobado=Decimal('750000'),
            plazo_meses=18,
            tasa_interes=Decimal('14.0'),
            estado=EstadoCreditoEnum.EN_ESTUDIO,
            fecha_desembolso=None,
            created_at=datetime.now()
        )
        
        # Setup mocks
        self.mock_db.flush = AsyncMock()
        self.mock_db.refresh = AsyncMock()
        
        # Mock the model creation and ID assignment
        with patch.object(self.repository, '_entity_to_model') as mock_entity_to_model, \
             patch.object(self.repository, '_model_to_entity') as mock_model_to_entity:
            
            mock_entity_to_model.return_value = created_model
            mock_model_to_entity.return_value = Credit(
                id=2,
                client_id=1,
                monto_aprobado=Decimal('750000'),
                plazo_meses=18,
                tasa_interes=Decimal('14.0'),
                estado=CreditStatus.EN_ESTUDIO.value,
                fecha_desembolso=None,
                created_at=datetime.now()
            )
            
            # Act
            result = await self.repository.create(new_credit)
            
            # Assert
            assert result.id == 2
            assert result.client_id == 1
            assert result.monto_aprobado == Decimal('750000')
            
            # Verify database operations
            self.mock_db.add.assert_called_once()
            self.mock_db.flush.assert_called_once()
            self.mock_db.refresh.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_create_credit_database_error(self):
        """Test credit creation with database error"""
        # Arrange
        new_credit = Credit(
            id=None,
            client_id=1,
            monto_aprobado=Decimal('500000'),
            plazo_meses=12,
            tasa_interes=Decimal('15.0'),
            estado=CreditStatus.EN_ESTUDIO.value
        )
        
        # Setup mock to raise exception
        self.mock_db.add.side_effect = Exception("Database connection error")
        
        # Act & Assert
        with pytest.raises(Exception) as exc_info:
            await self.repository.create(new_credit)
        
        assert "Error creating credit" in str(exc_info.value)
        assert "Database connection error" in str(exc_info.value)
    
    @pytest.mark.asyncio
    async def test_create_credit_ensures_no_id(self):
        """Test that create method ensures model has no ID"""
        # Arrange
        credit_with_id = Credit(
            id=999,  # Should be ignored
            client_id=1,
            monto_aprobado=Decimal('500000'),
            plazo_meses=12,
            tasa_interes=Decimal('15.0'),
            estado=CreditStatus.EN_ESTUDIO.value
        )
        
        # Setup mocks
        self.mock_db.flush = AsyncMock()
        self.mock_db.refresh = AsyncMock()
        
        created_model = CreditModel(
            id=1,  # Database assigns new ID
            client_id=1,
            monto_aprobado=Decimal('500000'),
            plazo_meses=12,
            tasa_interes=Decimal('15.0'),
            estado=EstadoCreditoEnum.EN_ESTUDIO,
            created_at=datetime.now()
        )
        
        with patch.object(self.repository, '_entity_to_model', return_value=created_model) as mock_entity_to_model, \
             patch.object(self.repository, '_model_to_entity') as mock_model_to_entity:
            
            mock_model_to_entity.return_value = Credit(
                id=1,
                client_id=1,
                monto_aprobado=Decimal('500000'),
                plazo_meses=12,
                tasa_interes=Decimal('15.0'),
                estado=CreditStatus.EN_ESTUDIO.value,
                created_at=datetime.now()
            )
            
            # Act
            result = await self.repository.create(credit_with_id)
            
            # Assert
            # Verify that the model's ID was set to None before adding
            added_model = self.mock_db.add.call_args[0][0]
            assert added_model.id is None
            assert result.id == 1  # Database assigned ID


class TestGetCredit(TestSupabaseCreditRepository):
    """Test get credit functionality"""
    
    @pytest.mark.asyncio
    async def test_get_by_id_success(self):
        """Test successful credit retrieval by ID"""
        # Arrange
        credit_id = 1
        
        # Mock database result
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = self.sample_model
        self.mock_db.execute.return_value = mock_result
        
        # Act
        result = await self.repository.get_by_id(credit_id)
        
        # Assert
        assert result is not None
        assert isinstance(result, Credit)
        assert result.id == credit_id
        assert result.monto_aprobado == Decimal('1000000')
        
        # Verify database query
        self.mock_db.execute.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_get_by_id_not_found(self):
        """Test credit retrieval when ID not found"""
        # Arrange
        credit_id = 999
        
        # Mock database result - no credit found
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = None
        self.mock_db.execute.return_value = mock_result
        
        # Act
        result = await self.repository.get_by_id(credit_id)
        
        # Assert
        assert result is None
        self.mock_db.execute.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_get_by_client_id_success(self):
        """Test successful retrieval of credits by client ID"""
        # Arrange
        client_id = 1
        credit_models = [
            self.sample_model,
            CreditModel(
                id=2,
                client_id=1,
                monto_aprobado=Decimal('500000'),
                plazo_meses=24,
                tasa_interes=Decimal('12.0'),
                estado=EstadoCreditoEnum.APROBADO,
                fecha_desembolso=date(2024, 6, 15),
                created_at=datetime.now()
            )
        ]
        
        # Mock database result
        mock_result = MagicMock()
        mock_result.scalars.return_value.all.return_value = credit_models
        self.mock_db.execute.return_value = mock_result
        
        # Act
        result = await self.repository.get_by_client_id(client_id)
        
        # Assert
        assert len(result) == 2
        assert all(isinstance(credit, Credit) for credit in result)
        assert all(credit.client_id == client_id for credit in result)
        assert result[0].monto_aprobado == Decimal('1000000')
        assert result[1].monto_aprobado == Decimal('500000')
        self.mock_db.execute.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_get_by_client_id_empty_result(self):
        """Test get credits by client ID with no credits"""
        # Arrange
        client_id = 999
        
        mock_result = MagicMock()
        mock_result.scalars.return_value.all.return_value = []
        self.mock_db.execute.return_value = mock_result
        
        # Act
        result = await self.repository.get_by_client_id(client_id)
        
        # Assert
        assert result == []
        self.mock_db.execute.assert_called_once()


class TestGetAllCredits(TestSupabaseCreditRepository):
    """Test get all credits functionality"""
    
    @pytest.mark.asyncio
    async def test_get_all_success(self):
        """Test successful retrieval of all credits"""
        # Arrange
        credit_models = [
            self.sample_model,
            CreditModel(
                id=2,
                client_id=2,
                monto_aprobado=Decimal('500000'),
                plazo_meses=24,
                tasa_interes=Decimal('12.0'),
                estado=EstadoCreditoEnum.APROBADO,
                fecha_desembolso=None,
                created_at=datetime.now()
            )
        ]
        
        # Mock database result
        mock_result = MagicMock()
        mock_result.scalars.return_value.all.return_value = credit_models
        self.mock_db.execute.return_value = mock_result
        
        # Act
        result = await self.repository.get_all(skip=0, limit=100)
        
        # Assert
        assert len(result) == 2
        assert all(isinstance(credit, Credit) for credit in result)
        assert result[0].monto_aprobado == Decimal('1000000')
        assert result[1].monto_aprobado == Decimal('500000')
        self.mock_db.execute.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_get_all_with_pagination(self):
        """Test get all credits with pagination parameters"""
        # Arrange
        skip = 10
        limit = 5
        
        mock_result = MagicMock()
        mock_result.scalars.return_value.all.return_value = []
        self.mock_db.execute.return_value = mock_result
        
        # Act
        result = await self.repository.get_all(skip=skip, limit=limit)
        
        # Assert
        assert result == []
        self.mock_db.execute.assert_called_once()


class TestUpdateCredit(TestSupabaseCreditRepository):
    """Test update credit functionality"""
    
    @pytest.mark.asyncio
    async def test_update_credit_success(self):
        """Test successful credit update"""
        # Arrange
        updated_credit = Credit(
            id=1,
            client_id=1,
            monto_aprobado=Decimal('1500000'),  # Updated amount
            plazo_meses=24,  # Updated term
            tasa_interes=Decimal('12.0'),  # Updated rate
            estado=CreditStatus.APROBADO.value,  # Updated status
            fecha_desembolso=date(2024, 6, 15),  # Updated date
            created_at=datetime(2024, 1, 15, 10, 30, 0)
        )
        
        # Mock finding existing model
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = self.sample_model
        self.mock_db.execute.return_value = mock_result
        
        # Mock database operations
        self.mock_db.flush = AsyncMock()
        self.mock_db.refresh = AsyncMock()
        
        # Act
        with patch.object(self.repository, '_model_to_entity', return_value=updated_credit):
            result = await self.repository.update(updated_credit)
        
        # Assert
        assert result.monto_aprobado == Decimal('1500000')
        assert result.plazo_meses == 24
        assert result.tasa_interes == Decimal('12.0')
        assert result.estado == CreditStatus.APROBADO.value
        assert result.fecha_desembolso == date(2024, 6, 15)
        
        # Verify database operations
        self.mock_db.execute.assert_called_once()
        self.mock_db.flush.assert_called_once()
        self.mock_db.refresh.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_update_credit_not_found(self):
        """Test update when credit not found"""
        # Arrange
        non_existent_credit = Credit(
            id=999,
            client_id=1,
            monto_aprobado=Decimal('500000'),
            plazo_meses=12,
            tasa_interes=Decimal('15.0'),
            estado=CreditStatus.EN_ESTUDIO.value
        )
        
        # Mock not finding the credit
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = None
        self.mock_db.execute.return_value = mock_result
        
        # Act & Assert
        with pytest.raises(Exception) as exc_info:
            await self.repository.update(non_existent_credit)
        
        assert "Error updating credit" in str(exc_info.value)
        assert "Credit with ID 999 not found" in str(exc_info.value)


class TestDeleteCredit(TestSupabaseCreditRepository):
    """Test delete credit functionality"""
    
    @pytest.mark.asyncio
    async def test_delete_credit_success(self):
        """Test successful credit deletion"""
        # Arrange
        credit_id = 1
        
        # Mock finding the credit
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = self.sample_model
        self.mock_db.execute.return_value = mock_result
        
        # Mock database operations
        self.mock_db.delete = AsyncMock()
        self.mock_db.flush = AsyncMock()
        
        # Act
        result = await self.repository.delete(credit_id)
        
        # Assert
        assert result is True
        self.mock_db.execute.assert_called_once()
        self.mock_db.delete.assert_called_once_with(self.sample_model)
        self.mock_db.flush.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_delete_credit_not_found(self):
        """Test delete when credit not found"""
        # Arrange
        credit_id = 999
        
        # Mock not finding the credit
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = None
        self.mock_db.execute.return_value = mock_result
        
        # Act
        result = await self.repository.delete(credit_id)
        
        # Assert
        assert result is False
        self.mock_db.execute.assert_called_once()
        # Verify delete was not called
        self.mock_db.delete.assert_not_called()


class TestCreditStatusQueries(TestSupabaseCreditRepository):
    """Test credit status-based query functionality"""
    
    @pytest.mark.asyncio
    async def test_get_by_status_success(self):
        """Test successful retrieval of credits by status"""
        # Arrange
        status = CreditStatus.APROBADO.value
        
        mock_result = MagicMock()
        mock_result.scalars.return_value.all.return_value = [self.sample_model]
        self.mock_db.execute.return_value = mock_result
        
        # Act
        result = await self.repository.get_by_status(status, skip=0, limit=100)
        
        # Assert
        assert len(result) == 1
        assert isinstance(result[0], Credit)
        self.mock_db.execute.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_get_active_credits_success(self):
        """Test successful retrieval of active credits"""
        # Arrange
        active_credit_models = [
            CreditModel(
                id=1,
                client_id=1,
                monto_aprobado=Decimal('1000000'),
                plazo_meses=12,
                tasa_interes=Decimal('15.0'),
                estado=EstadoCreditoEnum.AL_DIA,
                created_at=datetime.now()
            ),
            CreditModel(
                id=2,
                client_id=2,
                monto_aprobado=Decimal('500000'),
                plazo_meses=24,
                tasa_interes=Decimal('12.0'),
                estado=EstadoCreditoEnum.DESEMBOLSADO,
                created_at=datetime.now()
            )
        ]
        
        mock_result = MagicMock()
        mock_result.scalars.return_value.all.return_value = active_credit_models
        self.mock_db.execute.return_value = mock_result
        
        # Act
        result = await self.repository.get_active_credits(skip=0, limit=100)
        
        # Assert
        assert len(result) == 2
        assert all(isinstance(credit, Credit) for credit in result)
        self.mock_db.execute.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_get_overdue_credits_success(self):
        """Test successful retrieval of overdue credits"""
        # Arrange
        overdue_model = CreditModel(
            id=1,
            client_id=1,
            monto_aprobado=Decimal('1000000'),
            plazo_meses=12,
            tasa_interes=Decimal('15.0'),
            estado=EstadoCreditoEnum.EN_MORA,
            created_at=datetime.now()
        )
        
        mock_result = MagicMock()
        mock_result.scalars.return_value.all.return_value = [overdue_model]
        self.mock_db.execute.return_value = mock_result
        
        # Act
        result = await self.repository.get_overdue_credits()
        
        # Assert
        assert len(result) == 1
        assert result[0].estado == CreditStatus.EN_MORA.value
        self.mock_db.execute.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_get_credits_for_disbursement_success(self):
        """Test successful retrieval of credits ready for disbursement"""
        # Arrange
        approved_model = CreditModel(
            id=1,
            client_id=1,
            monto_aprobado=Decimal('1000000'),
            plazo_meses=12,
            tasa_interes=Decimal('15.0'),
            estado=EstadoCreditoEnum.APROBADO,
            created_at=datetime.now()
        )
        
        mock_result = MagicMock()
        mock_result.scalars.return_value.all.return_value = [approved_model]
        self.mock_db.execute.return_value = mock_result
        
        # Act
        result = await self.repository.get_credits_for_disbursement()
        
        # Assert
        assert len(result) == 1
        assert result[0].estado == CreditStatus.APROBADO.value
        self.mock_db.execute.assert_called_once()


class TestCreditDateQueries(TestSupabaseCreditRepository):
    """Test credit date-based query functionality"""
    
    @pytest.mark.asyncio
    async def test_get_by_date_range_success(self):
        """Test successful retrieval of credits by date range"""
        # Arrange
        start_date = datetime(2024, 1, 1)
        end_date = datetime(2024, 12, 31)
        
        mock_result = MagicMock()
        mock_result.scalars.return_value.all.return_value = [self.sample_model]
        self.mock_db.execute.return_value = mock_result
        
        # Act
        result = await self.repository.get_by_date_range(start_date, end_date)
        
        # Assert
        assert len(result) == 1
        assert isinstance(result[0], Credit)
        self.mock_db.execute.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_get_by_date_range_with_pagination(self):
        """Test date range query with pagination"""
        # Arrange
        start_date = datetime(2024, 1, 1)
        end_date = datetime(2024, 12, 31)
        skip = 5
        limit = 10
        
        mock_result = MagicMock()
        mock_result.scalars.return_value.all.return_value = []
        self.mock_db.execute.return_value = mock_result
        
        # Act
        result = await self.repository.get_by_date_range(start_date, end_date, skip=skip, limit=limit)
        
        # Assert
        assert result == []
        self.mock_db.execute.assert_called_once()


class TestCreditStatusUpdate(TestSupabaseCreditRepository):
    """Test credit status update functionality"""
    
    @pytest.mark.asyncio
    async def test_update_status_success(self):
        """Test successful credit status update"""
        # Arrange
        credit_id = 1
        new_status = CreditStatus.APROBADO.value
        
        # Mock finding the credit
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = self.sample_model
        self.mock_db.execute.return_value = mock_result
        
        # Mock database operations
        self.mock_db.flush = AsyncMock()
        
        # Act
        result = await self.repository.update_status(credit_id, new_status)
        
        # Assert
        assert result is True
        self.mock_db.execute.assert_called_once()
        self.mock_db.flush.assert_called_once()
        
        # Verify the model's status was updated
        assert self.sample_model.estado == EstadoCreditoEnum.APROBADO
    
    @pytest.mark.asyncio
    async def test_update_status_not_found(self):
        """Test status update when credit not found"""
        # Arrange
        credit_id = 999
        new_status = CreditStatus.APROBADO.value
        
        # Mock not finding the credit
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = None
        self.mock_db.execute.return_value = mock_result
        
        # Act
        result = await self.repository.update_status(credit_id, new_status)
        
        # Assert
        assert result is False
        self.mock_db.execute.assert_called_once()
        # Verify flush was not called
        self.mock_db.flush.assert_not_called()


class TestCreditCounting(TestSupabaseCreditRepository):
    """Test credit counting functionality"""
    
    @pytest.mark.asyncio
    async def test_count_total_success(self):
        """Test successful total count of credits"""
        # Arrange
        expected_count = 25
        
        # Mock database result
        mock_result = MagicMock()
        mock_result.scalar.return_value = expected_count
        self.mock_db.execute.return_value = mock_result
        
        # Act
        result = await self.repository.count_total()
        
        # Assert
        assert result == expected_count
        self.mock_db.execute.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_count_by_status_success(self):
        """Test successful count of credits by status"""
        # Arrange
        status = CreditStatus.APROBADO.value
        expected_count = 5
        
        # Mock database result
        mock_result = MagicMock()
        mock_result.scalar.return_value = expected_count
        self.mock_db.execute.return_value = mock_result
        
        # Act
        result = await self.repository.count_by_status(status)
        
        # Assert
        assert result == expected_count
        self.mock_db.execute.assert_called_once()


class TestCreditPortfolioAnalytics(TestSupabaseCreditRepository):
    """Test credit portfolio analytics functionality"""
    
    @pytest.mark.asyncio
    async def test_get_portfolio_summary_success(self):
        """Test successful portfolio summary retrieval"""
        # Arrange
        total_count = 10
        total_amount = Decimal('5000000')
        
        # Mock database results
        count_result = MagicMock()
        count_result.scalar.return_value = total_count
        
        amount_result = MagicMock()
        amount_result.scalar.return_value = total_amount
        
        self.mock_db.execute.side_effect = [count_result, amount_result]
        
        # Act
        result = await self.repository.get_portfolio_summary()
        
        # Assert
        assert result["total_credits"] == total_count
        assert result["total_amount"] == float(total_amount)
        assert result["average_amount"] == float(total_amount / total_count)
        assert self.mock_db.execute.call_count == 2
    
    @pytest.mark.asyncio
    async def test_get_portfolio_summary_zero_credits(self):
        """Test portfolio summary with zero credits"""
        # Arrange
        total_count = 0
        total_amount = Decimal('0')
        
        # Mock database results
        count_result = MagicMock()
        count_result.scalar.return_value = total_count
        
        amount_result = MagicMock()
        amount_result.scalar.return_value = total_amount
        
        self.mock_db.execute.side_effect = [count_result, amount_result]
        
        # Act
        result = await self.repository.get_portfolio_summary()
        
        # Assert
        assert result["total_credits"] == 0
        assert result["total_amount"] == 0.0
        assert result["average_amount"] == 0  # Should handle division by zero
    
    @pytest.mark.asyncio
    async def test_calculate_total_disbursed_success(self):
        """Test successful calculation of total disbursed amount"""
        # Arrange
        expected_amount = Decimal('2500000')
        
        # Mock database result
        mock_result = MagicMock()
        mock_result.scalar.return_value = expected_amount
        self.mock_db.execute.return_value = mock_result
        
        # Act
        result = await self.repository.calculate_total_disbursed()
        
        # Assert
        assert result == float(expected_amount)
        self.mock_db.execute.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_calculate_total_outstanding_success(self):
        """Test successful calculation of total outstanding amount"""
        # Arrange
        expected_amount = Decimal('1500000')
        
        # Mock database result
        mock_result = MagicMock()
        mock_result.scalar.return_value = expected_amount
        self.mock_db.execute.return_value = mock_result
        
        # Act
        result = await self.repository.calculate_total_outstanding()
        
        # Assert
        assert result == float(expected_amount)
        self.mock_db.execute.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_calculate_amounts_with_none_result(self):
        """Test amount calculations when database returns None"""
        # Arrange
        mock_result = MagicMock()
        mock_result.scalar.return_value = None
        self.mock_db.execute.return_value = mock_result
        
        # Act
        disbursed_result = await self.repository.calculate_total_disbursed()
        outstanding_result = await self.repository.calculate_total_outstanding()
        
        # Assert
        assert disbursed_result == 0.0  # Should default to 0
        assert outstanding_result == 0.0  # Should default to 0


class TestRepositoryErrorHandling(TestSupabaseCreditRepository):
    """Test repository error handling"""
    
    @pytest.mark.asyncio
    async def test_all_methods_handle_database_errors(self):
        """Test that all repository methods handle database errors properly"""
        # Arrange
        self.mock_db.execute.side_effect = Exception("Connection lost")
        
        # Test various methods
        methods_to_test = [
            (self.repository.get_by_id, (1,)),
            (self.repository.get_by_client_id, (1,)),
            (self.repository.get_all, ()),
            (self.repository.get_by_status, (CreditStatus.APROBADO.value,)),
            (self.repository.get_active_credits, ()),
            (self.repository.get_overdue_credits, ()),
            (self.repository.count_total, ()),
            (self.repository.count_by_status, (CreditStatus.APROBADO.value,)),
            (self.repository.calculate_total_disbursed, ()),
            (self.repository.calculate_total_outstanding, ())
        ]
        
        # Act & Assert
        for method, args in methods_to_test:
            with pytest.raises(Exception) as exc_info:
                await method(*args)
            
            # Verify error message contains method-specific context
            assert "Error" in str(exc_info.value)
            assert "Connection lost" in str(exc_info.value)