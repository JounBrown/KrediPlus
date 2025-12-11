"""
Unit tests for Client Document Service - Full Coverage
"""
import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from datetime import datetime

from src.application.services.client_document_service import ClientDocumentService
from src.domain.entities.client_document import ClientDocument, DocumentType


class TestClientDocumentServiceFull:
    """Test ClientDocumentService functionality"""
    
    def setup_method(self):
        """Setup test fixtures"""
        self.mock_repository = MagicMock()
        
        # Patch the storage service
        with patch('src.application.services.client_document_service.SupabaseStorageService'):
            self.service = ClientDocumentService(self.mock_repository)
            self.service._storage_service = MagicMock()
        
        self.sample_document = ClientDocument(
            id=1,
            file_name="cedula_frente.jpg",
            storage_path="clients/100/cedula_frente_123.jpg",
            document_type=DocumentType.CEDULA_FRENTE,
            client_id=100,
            credit_id=None,
            created_at=datetime.now()
        )


class TestUploadDocumentFull(TestClientDocumentServiceFull):
    """Test upload_document method - full coverage"""
    
    @pytest.mark.asyncio
    async def test_upload_document_success(self):
        """Test successful document upload"""
        mock_file = MagicMock()
        mock_file.filename = "cedula.jpg"
        mock_file.read = AsyncMock(return_value=b"file content")
        
        self.service._storage_service.generate_unique_filename = MagicMock(
            return_value="cedula_frente_123.jpg"
        )
        self.service._storage_service.build_storage_path = MagicMock(
            return_value="clients/100/cedula_frente_123.jpg"
        )
        self.service._storage_service.upload_file = AsyncMock()
        self.service._storage_service.get_public_url = MagicMock(
            return_value="https://storage.example.com/cedula.jpg"
        )
        
        self.mock_repository.create = AsyncMock(return_value=self.sample_document)
        
        result = await self.service.upload_document(
            file=mock_file,
            document_type="CEDULA_FRENTE",  # Use uppercase enum value
            client_id=100
        )
        
        assert result["status"] == "success"
        assert result["document_id"] == 1
    
    @pytest.mark.asyncio
    async def test_upload_document_invalid_type(self):
        """Test upload with invalid document type"""
        mock_file = MagicMock()
        mock_file.filename = "document.jpg"
        
        with pytest.raises(ValueError) as exc_info:
            await self.service.upload_document(
                file=mock_file,
                document_type="invalid_type",
                client_id=100
            )
        
        assert "Invalid document_type" in str(exc_info.value)
    
    @pytest.mark.asyncio
    async def test_upload_document_no_filename(self):
        """Test upload with no filename"""
        mock_file = MagicMock()
        mock_file.filename = None
        
        with pytest.raises(ValueError) as exc_info:
            await self.service.upload_document(
                file=mock_file,
                document_type="CEDULA_FRENTE",  # Use uppercase enum value
                client_id=100
            )
        
        assert "File must have a filename" in str(exc_info.value)
    
    @pytest.mark.asyncio
    async def test_upload_document_empty_file(self):
        """Test upload with empty file"""
        mock_file = MagicMock()
        mock_file.filename = "empty.jpg"
        mock_file.read = AsyncMock(return_value=b"")
        
        self.service._storage_service.generate_unique_filename = MagicMock(
            return_value="empty_123.jpg"
        )
        self.service._storage_service.build_storage_path = MagicMock(
            return_value="clients/100/empty_123.jpg"
        )
        
        with pytest.raises(ValueError) as exc_info:
            await self.service.upload_document(
                file=mock_file,
                document_type="CEDULA_FRENTE",  # Use uppercase enum value
                client_id=100
            )
        
        assert "File is empty" in str(exc_info.value)
    
    @pytest.mark.asyncio
    async def test_upload_document_storage_error(self):
        """Test upload with storage error"""
        mock_file = MagicMock()
        mock_file.filename = "cedula.jpg"
        mock_file.read = AsyncMock(return_value=b"file content")
        
        self.service._storage_service.generate_unique_filename = MagicMock(
            return_value="cedula_123.jpg"
        )
        self.service._storage_service.build_storage_path = MagicMock(
            return_value="clients/100/cedula_123.jpg"
        )
        self.service._storage_service.upload_file = AsyncMock(
            side_effect=Exception("Storage error")
        )
        
        with pytest.raises(Exception) as exc_info:
            await self.service.upload_document(
                file=mock_file,
                document_type="CEDULA_FRENTE",  # Use uppercase enum value
                client_id=100
            )
        
        assert "Error al subir el archivo" in str(exc_info.value)


class TestGetDocumentsFull(TestClientDocumentServiceFull):
    """Test get documents methods"""
    
    @pytest.mark.asyncio
    async def test_get_client_documents_success(self):
        """Test successful retrieval of client documents"""
        self.mock_repository.get_by_client_id = AsyncMock(return_value=[self.sample_document])
        self.service._storage_service.get_public_url = MagicMock(
            return_value="https://storage.example.com/doc.jpg"
        )
        
        result = await self.service.get_client_documents(100)
        
        assert len(result) == 1
        assert result[0].id == 1
        assert result[0].client_id == 100
    
    @pytest.mark.asyncio
    async def test_get_client_documents_with_signed_url_fallback(self):
        """Test retrieval with signed URL fallback"""
        self.mock_repository.get_by_client_id = AsyncMock(return_value=[self.sample_document])
        self.service._storage_service.get_public_url = MagicMock(
            side_effect=Exception("Public URL failed")
        )
        self.service._storage_service.create_signed_url = MagicMock(
            return_value="https://storage.example.com/signed/doc.jpg"
        )
        
        result = await self.service.get_client_documents(100)
        
        assert len(result) == 1
        self.service._storage_service.create_signed_url.assert_called()
    
    @pytest.mark.asyncio
    async def test_get_client_documents_repository_error(self):
        """Test retrieval with repository error"""
        self.mock_repository.get_by_client_id = AsyncMock(
            side_effect=Exception("Database error")
        )
        
        with pytest.raises(Exception) as exc_info:
            await self.service.get_client_documents(100)
        
        assert "Error getting client documents" in str(exc_info.value)
    
    @pytest.mark.asyncio
    async def test_get_credit_documents_success(self):
        """Test successful retrieval of credit documents"""
        doc_with_credit = ClientDocument(
            id=2,
            file_name="pagare.pdf",
            storage_path="clients/100/credits/50/pagare.pdf",
            document_type=DocumentType.PAGARE_FIRMADO,
            client_id=100,
            credit_id=50,
            created_at=datetime.now()
        )
        
        self.mock_repository.get_by_credit_id = AsyncMock(return_value=[doc_with_credit])
        self.service._storage_service.get_public_url = MagicMock(
            return_value="https://storage.example.com/pagare.pdf"
        )
        
        result = await self.service.get_credit_documents(50)
        
        assert len(result) == 1
        assert result[0].credit_id == 50
    
    @pytest.mark.asyncio
    async def test_get_credit_documents_repository_error(self):
        """Test credit documents retrieval with error"""
        self.mock_repository.get_by_credit_id = AsyncMock(
            side_effect=Exception("Database error")
        )
        
        with pytest.raises(Exception) as exc_info:
            await self.service.get_credit_documents(50)
        
        assert "Error getting credit documents" in str(exc_info.value)


class TestDeleteDocumentFull(TestClientDocumentServiceFull):
    """Test delete document methods"""
    
    @pytest.mark.asyncio
    async def test_delete_document_success(self):
        """Test successful document deletion"""
        self.mock_repository.get_by_id = AsyncMock(return_value=self.sample_document)
        self.mock_repository.delete = AsyncMock(return_value=True)
        self.service._storage_service.delete_file = AsyncMock()
        
        result = await self.service.delete_document(1)
        
        assert result["status"] == "success"
        self.mock_repository.delete.assert_called_once_with(1)
    
    @pytest.mark.asyncio
    async def test_delete_document_not_found(self):
        """Test deletion when document not found"""
        self.mock_repository.get_by_id = AsyncMock(return_value=None)
        
        with pytest.raises(ValueError) as exc_info:
            await self.service.delete_document(999)
        
        assert "not found" in str(exc_info.value)
    
    @pytest.mark.asyncio
    async def test_delete_client_document_success(self):
        """Test successful client document deletion"""
        self.mock_repository.get_by_id = AsyncMock(return_value=self.sample_document)
        self.mock_repository.delete = AsyncMock(return_value=True)
        self.service._storage_service.delete_file = AsyncMock()
        
        result = await self.service.delete_client_document(100, 1)
        
        assert result["status"] == "success"
    
    @pytest.mark.asyncio
    async def test_delete_client_document_wrong_client(self):
        """Test deletion with wrong client ID"""
        self.mock_repository.get_by_id = AsyncMock(return_value=self.sample_document)
        
        with pytest.raises(ValueError) as exc_info:
            await self.service.delete_client_document(999, 1)
        
        assert "does not belong to client" in str(exc_info.value)
    
    @pytest.mark.asyncio
    async def test_delete_credit_document_success(self):
        """Test successful credit document deletion"""
        doc_with_credit = ClientDocument(
            id=2,
            file_name="pagare.pdf",
            storage_path="clients/100/credits/50/pagare.pdf",
            document_type=DocumentType.PAGARE_FIRMADO,
            client_id=100,
            credit_id=50,
            created_at=datetime.now()
        )
        
        self.mock_repository.get_by_id = AsyncMock(return_value=doc_with_credit)
        self.mock_repository.delete = AsyncMock(return_value=True)
        self.service._storage_service.delete_file = AsyncMock()
        
        result = await self.service.delete_credit_document(50, 2)
        
        assert result["status"] == "success"
    
    @pytest.mark.asyncio
    async def test_delete_credit_document_wrong_credit(self):
        """Test deletion with wrong credit ID"""
        doc_with_credit = ClientDocument(
            id=2,
            file_name="pagare.pdf",
            storage_path="clients/100/credits/50/pagare.pdf",
            document_type=DocumentType.PAGARE_FIRMADO,
            client_id=100,
            credit_id=50,
            created_at=datetime.now()
        )
        
        self.mock_repository.get_by_id = AsyncMock(return_value=doc_with_credit)
        
        with pytest.raises(ValueError) as exc_info:
            await self.service.delete_credit_document(999, 2)
        
        assert "does not belong to credit" in str(exc_info.value)


class TestGetDocumentDownloadUrl(TestClientDocumentServiceFull):
    """Test get_document_download_url method"""
    
    @pytest.mark.asyncio
    async def test_get_download_url_success(self):
        """Test successful download URL generation"""
        self.mock_repository.get_by_id = AsyncMock(return_value=self.sample_document)
        self.service._storage_service.create_signed_url = MagicMock(
            return_value="https://storage.example.com/signed/doc.jpg?token=abc"
        )
        
        result = await self.service.get_document_download_url(1)
        
        assert "https://storage.example.com" in result
    
    @pytest.mark.asyncio
    async def test_get_download_url_not_found(self):
        """Test download URL when document not found"""
        self.mock_repository.get_by_id = AsyncMock(return_value=None)
        
        with pytest.raises(ValueError) as exc_info:
            await self.service.get_document_download_url(999)
        
        assert "not found" in str(exc_info.value)
    
    @pytest.mark.asyncio
    async def test_get_download_url_storage_error(self):
        """Test download URL with storage error"""
        self.mock_repository.get_by_id = AsyncMock(return_value=self.sample_document)
        self.service._storage_service.create_signed_url = MagicMock(
            side_effect=Exception("Storage error")
        )
        
        with pytest.raises(Exception) as exc_info:
            await self.service.get_document_download_url(1)
        
        assert "Error creating download URL" in str(exc_info.value)
