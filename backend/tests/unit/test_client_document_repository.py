"""Tests for SupabaseClientDocumentRepository"""
import pytest
from datetime import datetime
from unittest.mock import AsyncMock, MagicMock, patch
from src.infrastructure.outbound.database.client_document_repository import SupabaseClientDocumentRepository
from src.infrastructure.outbound.database.models import ClientDocumentModel, DocumentTypeEnum
from src.domain.entities.client_document import ClientDocument, DocumentType


@pytest.fixture
def mock_db_session():
    session = AsyncMock()
    return session


@pytest.fixture
def repository(mock_db_session):
    return SupabaseClientDocumentRepository(mock_db_session)


@pytest.fixture
def sample_document():
    return ClientDocument(
        id=1,
        file_name="cedula_front.pdf",
        storage_path="client_files/1/cedula_front.pdf",
        document_type=DocumentType.CEDULA_FRENTE,
        client_id=1,
        credit_id=None,
        created_at=datetime(2024, 1, 1)
    )


@pytest.fixture
def sample_model():
    model = MagicMock(spec=ClientDocumentModel)
    model.id = 1
    model.file_name = "cedula_front.pdf"
    model.storage_path = "client_files/1/cedula_front.pdf"
    model.document_type = DocumentTypeEnum.CEDULA_FRENTE
    model.client_id = 1
    model.credit_id = None
    model.created_at = datetime(2024, 1, 1)
    return model


class TestModelToEntity:
    """Tests for _model_to_entity conversion"""

    def test_model_to_entity_with_enum(self, repository, sample_model):
        """Test conversion from model with enum to entity"""
        result = repository._model_to_entity(sample_model)

        assert result.id == 1
        assert result.file_name == "cedula_front.pdf"
        assert result.document_type == DocumentType.CEDULA_FRENTE
        assert result.client_id == 1

    def test_model_to_entity_with_string(self, repository):
        """Test conversion from model with string document_type"""
        model = MagicMock(spec=ClientDocumentModel)
        model.id = 2
        model.file_name = "test.pdf"
        model.storage_path = "path/test.pdf"
        model.document_type = "CEDULA_FRENTE"  # String instead of enum
        model.client_id = 1
        model.credit_id = None
        model.created_at = datetime(2024, 1, 1)

        result = repository._model_to_entity(model)

        assert result.document_type == DocumentType.CEDULA_FRENTE


class TestEntityToModel:
    """Tests for _entity_to_model conversion"""

    def test_entity_to_model(self, repository, sample_document):
        """Test conversion from entity to model"""
        result = repository._entity_to_model(sample_document)

        assert result.file_name == "cedula_front.pdf"
        assert result.document_type == DocumentTypeEnum.CEDULA_FRENTE
        assert result.client_id == 1


class TestCreate:
    """Tests for create method"""

    async def test_create_success(self, repository, mock_db_session, sample_document, sample_model):
        """Test successful document creation"""
        mock_db_session.flush = AsyncMock()
        mock_db_session.refresh = AsyncMock()
        
        with patch.object(repository, '_entity_to_model', return_value=sample_model):
            with patch.object(repository, '_model_to_entity', return_value=sample_document):
                result = await repository.create(sample_document)

        assert result.id == 1
        mock_db_session.add.assert_called_once()

    async def test_create_error(self, repository, mock_db_session, sample_document):
        """Test create with database error"""
        mock_db_session.flush.side_effect = Exception("DB Error")

        with pytest.raises(Exception) as exc_info:
            await repository.create(sample_document)

        assert "Error creating client document" in str(exc_info.value)


class TestGetById:
    """Tests for get_by_id method"""

    async def test_get_by_id_found(self, repository, mock_db_session, sample_model, sample_document):
        """Test getting document by ID when found"""
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = sample_model
        mock_db_session.execute.return_value = mock_result

        with patch.object(repository, '_model_to_entity', return_value=sample_document):
            result = await repository.get_by_id(1)

        assert result is not None
        assert result.id == 1

    async def test_get_by_id_not_found(self, repository, mock_db_session):
        """Test getting document by ID when not found"""
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = None
        mock_db_session.execute.return_value = mock_result

        result = await repository.get_by_id(999)

        assert result is None

    async def test_get_by_id_error(self, repository, mock_db_session):
        """Test get_by_id with database error"""
        mock_db_session.execute.side_effect = Exception("DB Error")

        with pytest.raises(Exception) as exc_info:
            await repository.get_by_id(1)

        assert "Error getting client document by ID" in str(exc_info.value)


class TestGetByClientId:
    """Tests for get_by_client_id method"""

    async def test_get_by_client_id_success(self, repository, mock_db_session, sample_model, sample_document):
        """Test getting documents by client ID"""
        mock_scalars = MagicMock()
        mock_scalars.all.return_value = [sample_model]
        mock_result = MagicMock()
        mock_result.scalars.return_value = mock_scalars
        mock_db_session.execute.return_value = mock_result

        with patch.object(repository, '_model_to_entity', return_value=sample_document):
            result = await repository.get_by_client_id(1)

        assert len(result) == 1

    async def test_get_by_client_id_empty(self, repository, mock_db_session):
        """Test getting documents when client has none"""
        mock_scalars = MagicMock()
        mock_scalars.all.return_value = []
        mock_result = MagicMock()
        mock_result.scalars.return_value = mock_scalars
        mock_db_session.execute.return_value = mock_result

        result = await repository.get_by_client_id(999)

        assert len(result) == 0

    async def test_get_by_client_id_error(self, repository, mock_db_session):
        """Test get_by_client_id with database error"""
        mock_db_session.execute.side_effect = Exception("DB Error")

        with pytest.raises(Exception) as exc_info:
            await repository.get_by_client_id(1)

        assert "Error getting documents by client ID" in str(exc_info.value)


class TestGetByCreditId:
    """Tests for get_by_credit_id method"""

    async def test_get_by_credit_id_success(self, repository, mock_db_session, sample_model, sample_document):
        """Test getting documents by credit ID"""
        mock_scalars = MagicMock()
        mock_scalars.all.return_value = [sample_model]
        mock_result = MagicMock()
        mock_result.scalars.return_value = mock_scalars
        mock_db_session.execute.return_value = mock_result

        with patch.object(repository, '_model_to_entity', return_value=sample_document):
            result = await repository.get_by_credit_id(1)

        assert len(result) == 1

    async def test_get_by_credit_id_error(self, repository, mock_db_session):
        """Test get_by_credit_id with database error"""
        mock_db_session.execute.side_effect = Exception("DB Error")

        with pytest.raises(Exception) as exc_info:
            await repository.get_by_credit_id(1)

        assert "Error getting documents by credit ID" in str(exc_info.value)


class TestUpdate:
    """Tests for update method"""

    async def test_update_success(self, repository, mock_db_session, sample_model, sample_document):
        """Test successful document update"""
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = sample_model
        mock_db_session.execute.return_value = mock_result
        mock_db_session.flush = AsyncMock()
        mock_db_session.refresh = AsyncMock()

        with patch.object(repository, '_model_to_entity', return_value=sample_document):
            result = await repository.update(sample_document)

        assert result.id == 1

    async def test_update_not_found(self, repository, mock_db_session, sample_document):
        """Test update when document not found"""
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = None
        mock_db_session.execute.return_value = mock_result

        with pytest.raises(Exception) as exc_info:
            await repository.update(sample_document)

        assert "not found" in str(exc_info.value)

    async def test_update_error(self, repository, mock_db_session, sample_document):
        """Test update with database error"""
        mock_db_session.execute.side_effect = Exception("DB Error")

        with pytest.raises(Exception) as exc_info:
            await repository.update(sample_document)

        assert "Error updating client document" in str(exc_info.value)


class TestDelete:
    """Tests for delete method"""

    async def test_delete_success(self, repository, mock_db_session, sample_model):
        """Test successful document deletion"""
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = sample_model
        mock_db_session.execute.return_value = mock_result
        mock_db_session.delete = AsyncMock()
        mock_db_session.flush = AsyncMock()

        result = await repository.delete(1)

        assert result is True
        mock_db_session.delete.assert_called_once()

    async def test_delete_not_found(self, repository, mock_db_session):
        """Test delete when document not found"""
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = None
        mock_db_session.execute.return_value = mock_result

        result = await repository.delete(999)

        assert result is False

    async def test_delete_error(self, repository, mock_db_session):
        """Test delete with database error"""
        mock_db_session.execute.side_effect = Exception("DB Error")

        with pytest.raises(Exception) as exc_info:
            await repository.delete(1)

        assert "Error deleting client document" in str(exc_info.value)


class TestGetAll:
    """Tests for get_all method"""

    async def test_get_all_success(self, repository, mock_db_session, sample_model, sample_document):
        """Test getting all documents"""
        mock_scalars = MagicMock()
        mock_scalars.all.return_value = [sample_model]
        mock_result = MagicMock()
        mock_result.scalars.return_value = mock_scalars
        mock_db_session.execute.return_value = mock_result

        with patch.object(repository, '_model_to_entity', return_value=sample_document):
            result = await repository.get_all()

        assert len(result) == 1

    async def test_get_all_error(self, repository, mock_db_session):
        """Test get_all with database error"""
        mock_db_session.execute.side_effect = Exception("DB Error")

        with pytest.raises(Exception) as exc_info:
            await repository.get_all()

        assert "Error getting all client documents" in str(exc_info.value)
