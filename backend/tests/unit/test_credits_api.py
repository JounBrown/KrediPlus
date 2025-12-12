"""
Unit tests for Credits API routes
"""
import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from datetime import date, datetime
from decimal import Decimal
from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from src.api.routes.credits import (
    create_credit,
    get_credit,
    list_credits,
    get_credits_by_client,
    update_credit,
    delete_credit,
    delete_credit_document
)
from src.application.dtos.credit_dtos import (
    CreateCreditRequest,
    UpdateCreditRequest,
    CreditResponse
)


class TestCreateCredit:
    """Test create_credit endpoint"""
    
    @pytest.mark.asyncio
    async def test_create_credit_success(self):
        """Test successful credit creation"""
        # Arrange
        request = CreateCreditRequest(
            client_id=1,
            monto_aprobado=Decimal('1000000'),
            plazo_meses=12,
            tasa_interes=Decimal('15.5'),
            fecha_desembolso=None
        )
        
        expected_response = CreditResponse(
            id=1,
            client_id=1,
            monto_aprobado=Decimal('1000000'),
            plazo_meses=12,
            tasa_interes=Decimal('15.5'),
            estado="EN_ESTUDIO",
            fecha_desembolso=None,
            created_at=datetime.now()
        )
        
        mock_service = AsyncMock()
        mock_service.create_credit.return_value = expected_response
        
        # Act
        result = await create_credit(request, mock_service)
        
        # Assert
        assert result == expected_response
        mock_service.create_credit.assert_called_once_with(request)
    
    def test_create_credit_validation_error(self):
        """Test credit creation with validation error - Pydantic validates at creation"""
        from pydantic import ValidationError
        
        # Act & Assert - Pydantic should reject negative amount
        with pytest.raises(ValidationError) as exc_info:
            CreateCreditRequest(
                client_id=1,
                monto_aprobado=Decimal('-1000'),  # Invalid negative amount
                plazo_meses=12,
                tasa_interes=Decimal('15.5')
            )
        
        assert "monto_aprobado" in str(exc_info.value)
    
    @pytest.mark.asyncio
    async def test_create_credit_internal_error(self):
        """Test credit creation with internal error"""
        # Arrange
        request = CreateCreditRequest(
            client_id=1,
            monto_aprobado=Decimal('1000000'),
            plazo_meses=12,
            tasa_interes=Decimal('15.5')
        )
        
        mock_service = AsyncMock()
        mock_service.create_credit.side_effect = Exception("Database error")
        
        # Act & Assert
        with pytest.raises(HTTPException) as exc_info:
            await create_credit(request, mock_service)
        
        assert exc_info.value.status_code == 500
        assert "Error creating credit" in str(exc_info.value.detail)


class TestGetCredit:
    """Test get_credit endpoint"""
    
    @pytest.mark.asyncio
    async def test_get_credit_success(self):
        """Test successful credit retrieval"""
        # Arrange
        credit_id = 1
        expected_response = CreditResponse(
            id=1,
            client_id=1,
            monto_aprobado=Decimal('1000000'),
            plazo_meses=12,
            tasa_interes=Decimal('15.5'),
            estado="EN_ESTUDIO",
            fecha_desembolso=None,
            created_at=datetime.now()
        )
        
        mock_service = AsyncMock()
        mock_service.get_credit_by_id.return_value = expected_response
        
        # Act
        result = await get_credit(credit_id, mock_service)
        
        # Assert
        assert result == expected_response
        mock_service.get_credit_by_id.assert_called_once_with(credit_id)
    
    @pytest.mark.asyncio
    async def test_get_credit_not_found(self):
        """Test credit retrieval when credit not found"""
        # Arrange
        credit_id = 999
        mock_service = AsyncMock()
        mock_service.get_credit_by_id.return_value = None
        
        # Act & Assert
        with pytest.raises(HTTPException) as exc_info:
            await get_credit(credit_id, mock_service)
        
        assert exc_info.value.status_code == 404
        assert "Credit not found" in str(exc_info.value.detail)
    
    @pytest.mark.asyncio
    async def test_get_credit_internal_error(self):
        """Test credit retrieval with internal error"""
        # Arrange
        credit_id = 1
        mock_service = AsyncMock()
        mock_service.get_credit_by_id.side_effect = Exception("Database error")
        
        # Act & Assert
        with pytest.raises(HTTPException) as exc_info:
            await get_credit(credit_id, mock_service)
        
        assert exc_info.value.status_code == 500
        assert "Error getting credit" in str(exc_info.value.detail)


class TestListCredits:
    """Test list_credits endpoint"""
    
    @pytest.mark.asyncio
    async def test_list_credits_success(self):
        """Test successful credit listing"""
        # Arrange
        mock_db = AsyncMock(spec=AsyncSession)
        
        # Mock credit models
        from src.infrastructure.adapters.database.models import CreditModel
        mock_credit_models = [
            CreditModel(
                id=1,
                client_id=1,
                monto_aprobado=Decimal('1000000'),
                plazo_meses=12,
                tasa_interes=Decimal('15.5'),
                estado="EN_ESTUDIO",
                fecha_desembolso=None,
                created_at=datetime.now()
            ),
            CreditModel(
                id=2,
                client_id=2,
                monto_aprobado=Decimal('500000'),
                plazo_meses=24,
                tasa_interes=Decimal('12.0'),
                estado="APROBADO",
                fecha_desembolso=None,
                created_at=datetime.now()
            )
        ]
        
        mock_result = MagicMock()
        mock_result.scalars.return_value.all.return_value = mock_credit_models
        mock_db.execute.return_value = mock_result
        
        # Act & Assert
        with patch('src.infrastructure.adapters.database.credit_repository.SupabaseCreditRepository') as mock_repo_class:
            mock_repo = AsyncMock()
            
            # Mock the _model_to_entity method for each credit
            from src.domain.entities.credit import Credit
            mock_credit_entities = [
                Credit(
                    id=1,
                    client_id=1,
                    monto_aprobado=Decimal('1000000'),
                    plazo_meses=12,
                    tasa_interes=Decimal('15.5'),
                    estado="EN_ESTUDIO",
                    fecha_desembolso=None,
                    created_at=datetime.now()
                ),
                Credit(
                    id=2,
                    client_id=2,
                    monto_aprobado=Decimal('500000'),
                    plazo_meses=24,
                    tasa_interes=Decimal('12.0'),
                    estado="APROBADO",
                    fecha_desembolso=None,
                    created_at=datetime.now()
                )
            ]
            
            mock_repo._model_to_entity.side_effect = mock_credit_entities
            mock_repo_class.return_value = mock_repo
            
            result = await list_credits(mock_db)
            
            # Verify we get a list of CreditResponse objects
            assert len(result) == 2
            assert all(isinstance(credit, CreditResponse) for credit in result)
            assert result[0].monto_aprobado == Decimal('1000000')
            assert result[1].monto_aprobado == Decimal('500000')
            
            # Verify database query was executed
            mock_db.execute.assert_called_once()


class TestGetCreditsByClient:
    """Test get_credits_by_client endpoint"""
    
    @pytest.mark.asyncio
    async def test_get_credits_by_client_success(self):
        """Test successful retrieval of credits by client"""
        # Arrange
        client_id = 1
        expected_credits = [
            CreditResponse(
                id=1,
                client_id=1,
                monto_aprobado=Decimal('1000000'),
                plazo_meses=12,
                tasa_interes=Decimal('15.5'),
                estado="EN_ESTUDIO",
                fecha_desembolso=None,
                created_at=datetime.now()
            ),
            CreditResponse(
                id=2,
                client_id=1,
                monto_aprobado=Decimal('500000'),
                plazo_meses=24,
                tasa_interes=Decimal('12.0'),
                estado="APROBADO",
                fecha_desembolso=None,
                created_at=datetime.now()
            )
        ]
        
        mock_service = AsyncMock()
        mock_service.get_credits_by_client.return_value = expected_credits
        
        # Act
        result = await get_credits_by_client(client_id, mock_service)
        
        # Assert
        assert result == expected_credits
        assert len(result) == 2
        assert all(credit.client_id == client_id for credit in result)
        mock_service.get_credits_by_client.assert_called_once_with(client_id)
    
    @pytest.mark.asyncio
    async def test_get_credits_by_client_empty_result(self):
        """Test retrieval of credits by client with no credits"""
        # Arrange
        client_id = 999
        mock_service = AsyncMock()
        mock_service.get_credits_by_client.return_value = []
        
        # Act
        result = await get_credits_by_client(client_id, mock_service)
        
        # Assert
        assert result == []
        mock_service.get_credits_by_client.assert_called_once_with(client_id)
    
    @pytest.mark.asyncio
    async def test_get_credits_by_client_internal_error(self):
        """Test credits by client retrieval with internal error"""
        # Arrange
        client_id = 1
        mock_service = AsyncMock()
        mock_service.get_credits_by_client.side_effect = Exception("Database error")
        
        # Act & Assert
        with pytest.raises(HTTPException) as exc_info:
            await get_credits_by_client(client_id, mock_service)
        
        assert exc_info.value.status_code == 500
        assert "Error getting credits by client" in str(exc_info.value.detail)


class TestUpdateCredit:
    """Test update_credit endpoint"""
    
    @pytest.mark.asyncio
    async def test_update_credit_success(self):
        """Test successful credit update"""
        # Arrange
        credit_id = 1
        request = UpdateCreditRequest(
            monto_aprobado=Decimal('1500000'),
            plazo_meses=24,
            tasa_interes=Decimal('12.0'),
            estado="APROBADO",
            fecha_desembolso=date(2024, 6, 15)
        )
        
        expected_response = CreditResponse(
            id=1,
            client_id=1,
            monto_aprobado=Decimal('1500000'),
            plazo_meses=24,
            tasa_interes=Decimal('12.0'),
            estado="APROBADO",
            fecha_desembolso=date(2024, 6, 15),
            created_at=datetime.now()
        )
        
        mock_service = AsyncMock()
        mock_service.update_credit.return_value = expected_response
        
        # Act
        result = await update_credit(credit_id, request, mock_service)
        
        # Assert
        assert result == expected_response
        mock_service.update_credit.assert_called_once_with(credit_id, request)
    
    def test_update_credit_validation_error(self):
        """Test credit update with validation error - Pydantic validates at creation"""
        from pydantic import ValidationError
        
        # Act & Assert - Pydantic should reject negative amount
        with pytest.raises(ValidationError) as exc_info:
            UpdateCreditRequest(
                monto_aprobado=Decimal('-1000'),  # Invalid negative amount
                plazo_meses=24
            )
        
        assert "monto_aprobado" in str(exc_info.value)
    
    @pytest.mark.asyncio
    async def test_update_credit_partial_update(self):
        """Test credit partial update (only some fields)"""
        # Arrange
        credit_id = 1
        request = UpdateCreditRequest(
            estado="APROBADO"  # Only updating status
        )
        
        expected_response = CreditResponse(
            id=1,
            client_id=1,
            monto_aprobado=Decimal('1000000'),  # Unchanged
            plazo_meses=12,  # Unchanged
            tasa_interes=Decimal('15.5'),  # Unchanged
            estado="APROBADO",  # Updated
            fecha_desembolso=None,
            created_at=datetime.now()
        )
        
        mock_service = AsyncMock()
        mock_service.update_credit.return_value = expected_response
        
        # Act
        result = await update_credit(credit_id, request, mock_service)
        
        # Assert
        assert result == expected_response
        assert result.estado == "APROBADO"
        mock_service.update_credit.assert_called_once_with(credit_id, request)


class TestDeleteCredit:
    """Test delete_credit endpoint"""
    
    @pytest.mark.asyncio
    async def test_delete_credit_success(self):
        """Test successful credit deletion"""
        # Arrange
        credit_id = 1
        mock_service = AsyncMock()
        mock_service.delete_credit.return_value = True
        
        # Act
        result = await delete_credit(credit_id, mock_service)
        
        # Assert
        assert result == {"message": "Credit deleted successfully"}
        mock_service.delete_credit.assert_called_once_with(credit_id)
    
    @pytest.mark.asyncio
    async def test_delete_credit_not_found(self):
        """Test credit deletion when credit not found"""
        # Arrange
        credit_id = 999
        mock_service = AsyncMock()
        mock_service.delete_credit.return_value = False
        
        # Act & Assert
        with pytest.raises(HTTPException) as exc_info:
            await delete_credit(credit_id, mock_service)
        
        assert exc_info.value.status_code == 404
        assert "Credit not found" in str(exc_info.value.detail)
    
    @pytest.mark.asyncio
    async def test_delete_credit_internal_error(self):
        """Test credit deletion with internal error"""
        # Arrange
        credit_id = 1
        mock_service = AsyncMock()
        mock_service.delete_credit.side_effect = Exception("Database error")
        
        # Act & Assert
        with pytest.raises(HTTPException) as exc_info:
            await delete_credit(credit_id, mock_service)
        
        assert exc_info.value.status_code == 500
        assert "Error deleting credit" in str(exc_info.value.detail)


class TestDeleteCreditDocument:
    """Test delete_credit_document endpoint"""
    
    @pytest.mark.asyncio
    async def test_delete_credit_document_success(self):
        """Test successful credit document deletion"""
        # Arrange
        credit_id = 1
        document_id = 1
        mock_db = AsyncMock(spec=AsyncSession)
        
        expected_result = {"message": "Document deleted successfully"}
        
        # Act & Assert
        with patch('src.application.services.client_document_service.ClientDocumentService') as mock_service_class, \
             patch('src.infrastructure.adapters.database.client_document_repository.SupabaseClientDocumentRepository') as mock_repo_class:
            
            mock_service = AsyncMock()
            mock_service.delete_credit_document.return_value = expected_result
            mock_service_class.return_value = mock_service
            
            result = await delete_credit_document(credit_id, document_id, mock_db)
            
            assert result == expected_result
            mock_service.delete_credit_document.assert_called_once_with(credit_id, document_id)
    
    @pytest.mark.asyncio
    async def test_delete_credit_document_not_found(self):
        """Test credit document deletion when document not found"""
        # Arrange
        credit_id = 1
        document_id = 999
        mock_db = AsyncMock(spec=AsyncSession)
        
        # Act & Assert
        with patch('src.application.services.client_document_service.ClientDocumentService') as mock_service_class, \
             patch('src.infrastructure.adapters.database.client_document_repository.SupabaseClientDocumentRepository'):
            
            mock_service = AsyncMock()
            mock_service.delete_credit_document.side_effect = ValueError("Document not found")
            mock_service_class.return_value = mock_service
            
            with pytest.raises(HTTPException) as exc_info:
                await delete_credit_document(credit_id, document_id, mock_db)
            
            assert exc_info.value.status_code == 404
            assert "Document not found" in str(exc_info.value.detail)
    
    @pytest.mark.asyncio
    async def test_delete_credit_document_internal_error(self):
        """Test credit document deletion with internal error"""
        # Arrange
        credit_id = 1
        document_id = 1
        mock_db = AsyncMock(spec=AsyncSession)
        
        # Act & Assert
        with patch('src.application.services.client_document_service.ClientDocumentService') as mock_service_class, \
             patch('src.infrastructure.adapters.database.client_document_repository.SupabaseClientDocumentRepository'):
            
            mock_service = AsyncMock()
            mock_service.delete_credit_document.side_effect = Exception("Database error")
            mock_service_class.return_value = mock_service
            
            with pytest.raises(HTTPException) as exc_info:
                await delete_credit_document(credit_id, document_id, mock_db)
            
            assert exc_info.value.status_code == 500
            assert "Database error" in str(exc_info.value.detail)


class TestCreditStatusTransitions:
    """Test credit status transitions through API"""
    
    @pytest.mark.asyncio
    async def test_credit_approval_workflow(self):
        """Test complete credit approval workflow"""
        # Arrange
        credit_id = 1
        
        # Step 1: Update to APROBADO
        approve_request = UpdateCreditRequest(estado="APROBADO")
        approved_response = CreditResponse(
            id=1,
            client_id=1,
            monto_aprobado=Decimal('1000000'),
            plazo_meses=12,
            tasa_interes=Decimal('15.5'),
            estado="APROBADO",
            fecha_desembolso=None,
            created_at=datetime.now()
        )
        
        # Step 2: Update to DESEMBOLSADO
        disburse_request = UpdateCreditRequest(
            estado="DESEMBOLSADO",
            fecha_desembolso=date(2024, 6, 15)
        )
        disbursed_response = CreditResponse(
            id=1,
            client_id=1,
            monto_aprobado=Decimal('1000000'),
            plazo_meses=12,
            tasa_interes=Decimal('15.5'),
            estado="DESEMBOLSADO",
            fecha_desembolso=date(2024, 6, 15),
            created_at=datetime.now()
        )
        
        mock_service = AsyncMock()
        mock_service.update_credit.side_effect = [approved_response, disbursed_response]
        
        # Act & Assert
        # Step 1: Approve
        result1 = await update_credit(credit_id, approve_request, mock_service)
        assert result1.estado == "APROBADO"
        
        # Step 2: Disburse
        result2 = await update_credit(credit_id, disburse_request, mock_service)
        assert result2.estado == "DESEMBOLSADO"
        assert result2.fecha_desembolso == date(2024, 6, 15)
        
        # Verify service calls
        assert mock_service.update_credit.call_count == 2
    
    @pytest.mark.asyncio
    async def test_credit_rejection_workflow(self):
        """Test credit rejection workflow"""
        # Arrange
        credit_id = 1
        reject_request = UpdateCreditRequest(estado="RECHAZADO")
        
        rejected_response = CreditResponse(
            id=1,
            client_id=1,
            monto_aprobado=Decimal('1000000'),
            plazo_meses=12,
            tasa_interes=Decimal('15.5'),
            estado="RECHAZADO",
            fecha_desembolso=None,
            created_at=datetime.now()
        )
        
        mock_service = AsyncMock()
        mock_service.update_credit.return_value = rejected_response
        
        # Act
        result = await update_credit(credit_id, reject_request, mock_service)
        
        # Assert
        assert result.estado == "RECHAZADO"
        mock_service.update_credit.assert_called_once_with(credit_id, reject_request)


class TestCreditValidationScenarios:
    """Test various credit validation scenarios"""
    
    @pytest.mark.asyncio
    async def test_create_credit_with_future_disbursement(self):
        """Test creating credit with future disbursement date"""
        # Arrange
        future_date = date(2025, 1, 15)
        request = CreateCreditRequest(
            client_id=1,
            monto_aprobado=Decimal('1000000'),
            plazo_meses=12,
            tasa_interes=Decimal('15.5'),
            fecha_desembolso=future_date
        )
        
        expected_response = CreditResponse(
            id=1,
            client_id=1,
            monto_aprobado=Decimal('1000000'),
            plazo_meses=12,
            tasa_interes=Decimal('15.5'),
            estado="EN_ESTUDIO",
            fecha_desembolso=future_date,
            created_at=datetime.now()
        )
        
        mock_service = AsyncMock()
        mock_service.create_credit.return_value = expected_response
        
        # Act
        result = await create_credit(request, mock_service)
        
        # Assert
        assert result.fecha_desembolso == future_date
        mock_service.create_credit.assert_called_once_with(request)
    
    @pytest.mark.asyncio
    async def test_update_credit_with_large_amounts(self):
        """Test updating credit with large amounts"""
        # Arrange
        credit_id = 1
        request = UpdateCreditRequest(
            monto_aprobado=Decimal('100000000'),  # 100 million
            plazo_meses=120,  # 10 years
            tasa_interes=Decimal('25.99')  # High interest rate
        )
        
        expected_response = CreditResponse(
            id=1,
            client_id=1,
            monto_aprobado=Decimal('100000000'),
            plazo_meses=120,
            tasa_interes=Decimal('25.99'),
            estado="EN_ESTUDIO",
            fecha_desembolso=None,
            created_at=datetime.now()
        )
        
        mock_service = AsyncMock()
        mock_service.update_credit.return_value = expected_response
        
        # Act
        result = await update_credit(credit_id, request, mock_service)
        
        # Assert
        assert result.monto_aprobado == Decimal('100000000')
        assert result.plazo_meses == 120
        assert result.tasa_interes == Decimal('25.99')
        mock_service.update_credit.assert_called_once_with(credit_id, request)
    
    def test_create_credit_with_zero_interest_validation(self):
        """Test that zero interest rate is rejected by Pydantic validation"""
        from pydantic import ValidationError
        
        # Act & Assert - Pydantic should reject zero interest
        with pytest.raises(ValidationError) as exc_info:
            CreateCreditRequest(
                client_id=1,
                monto_aprobado=Decimal('500000'),
                plazo_meses=6,
                tasa_interes=Decimal('0')  # Zero interest - invalid
            )
        
        assert "tasa_interes" in str(exc_info.value)