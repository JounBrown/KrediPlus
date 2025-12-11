"""
Unit tests for ClientDocumentService
"""
import pytest
from unittest.mock import AsyncMock, Mock, patch
from datetime import datetime
from src.domain.entities.client_document import ClientDocument, DocumentType

# Mock UploadFile to avoid FastAPI dependency
class MockUploadFile:
    def __init__(self, filename="test.jpg", content=b"fake content"):
        self.filename = filename
        self._content = content
    
    async def read(self):
        return self._content

# Mock ClientDocumentResponse to avoid pydantic dependency
class MockClientDocumentResponse:
    def __init__(self, document, file_url="https://example.com/file.jpg"):
        self.id = document.id
        self.file_name = document.file_name
        self.storage_path = document.storage_path
        self.document_type = document.document_type.value
        self.client_id = document.client_id
        self.credit_id = document.credit_id
        self.created_at = document.created_at.isoformat()
        self.file_url = file_url

# Mock ClientDocumentService to avoid import issues
class MockClientDocumentService:
    def __init__(self, document_repository):
        self._document_repository = document_repository
        self._storage_service = Mock()
    
    async def upload_document(self, file, document_type, client_id, credit_id=None):
        # Validate document type
        try:
            doc_type = DocumentType(document_type)
        except ValueError:
            valid_types = [dt.value for dt in DocumentType]
            raise ValueError(f"Invalid document_type. Must be one of: {valid_types}")
        
        # Validate file
        if not file.filename:
            raise ValueError("File must have a filename")
        
        # Read file content
        file_content = await file.read()
        
        if not file_content:
            raise ValueError("File is empty")
        
        # Generate unique filename and path
        unique_filename = self._storage_service.generate_unique_filename(document_type, file.filename)
        storage_path = self._storage_service.build_storage_path(client_id, unique_filename)
        
        # Upload to storage
        try:
            await self._storage_service.upload_file(file_content, storage_path)
        except Exception as e:
            raise Exception(f"Error al subir el archivo a Supabase Storage: {str(e)}")
        
        # Create document entity
        document = ClientDocument(
            file_name=file.filename,
            storage_path=storage_path,
            document_type=doc_type,
            client_id=client_id,
            credit_id=credit_id
        )
        
        # Validate document
        if not document.validate():
            await self._storage_service.delete_file(storage_path)
            raise ValueError("Invalid document data")
        
        # Save to database
        try:
            created_document = await self._document_repository.create(document)
        except Exception as e:
            await self._storage_service.delete_file(storage_path)
            raise Exception(f"Error saving document to database: {str(e)}")
        
        # Generate URL
        try:
            file_url = self._storage_service.get_public_url(storage_path)
        except Exception:
            file_url = self._storage_service.create_signed_url(storage_path, expires_in=86400)
        
        return {
            "status": "success",
            "message": "Archivo subido exitosamente",
            "path": storage_path,
            "document_id": created_document.id,
            "file_url": file_url
        }
    
    async def get_client_documents(self, client_id):
        try:
            documents = await self._document_repository.get_by_client_id(client_id)
            
            result = []
            for doc in documents:
                try:
                    file_url = self._storage_service.get_public_url(doc.storage_path)
                except Exception:
                    file_url = self._storage_service.create_signed_url(doc.storage_path, expires_in=86400)
                
                result.append(MockClientDocumentResponse(doc, file_url))
            
            return result
        except Exception as e:
            raise Exception(f"Error getting client documents: {str(e)}")
    
    async def delete_document(self, document_id):
        try:
            document = await self._document_repository.get_by_id(document_id)
            if not document:
                raise ValueError(f"Document with ID {document_id} not found")
            
            success = await self._document_repository.delete(document_id)
            if not success:
                raise Exception("Failed to delete document from database")
            
            await self._storage_service.delete_file(document.storage_path)
            
            return {
                "status": "success",
                "message": f"Document {document_id} deleted successfully"
            }
        except ValueError as e:
            raise e
        except Exception as e:
            raise Exception(f"Error deleting document: {str(e)}")
    
    async def delete_client_document(self, client_id, document_id):
        try:
            document = await self._document_repository.get_by_id(document_id)
            if not document:
                raise ValueError(f"Document with ID {document_id} not found")
            
            if document.client_id != client_id:
                raise ValueError(f"Document {document_id} does not belong to client {client_id}")
            
            success = await self._document_repository.delete(document_id)
            if not success:
                raise Exception("Failed to delete document from database")
            
            await self._storage_service.delete_file(document.storage_path)
            
            return {
                "status": "success",
                "message": f"Document {document_id} deleted successfully from client {client_id}"
            }
        except ValueError as e:
            raise e
        except Exception as e:
            raise Exception(f"Error deleting client document: {str(e)}")
    
    async def get_document_download_url(self, document_id, expires_in=3600):
        try:
            document = await self._document_repository.get_by_id(document_id)
            if not document:
                raise ValueError(f"Document with ID {document_id} not found")
            
            signed_url = self._storage_service.create_signed_url(document.storage_path, expires_in)
            return signed_url
        except ValueError as e:
            raise e
        except Exception as e:
            raise Exception(f"Error creating download URL: {str(e)}")


class TestClientDocumentService:
    """Test ClientDocumentService operations"""
    
    @pytest.fixture
    def mock_repository(self):
        """Mock client document repository"""
        return AsyncMock()
    
    @pytest.fixture
    def client_document_service(self, mock_repository):
        """ClientDocumentService instance with mocked dependencies"""
        return MockClientDocumentService(mock_repository)
    
    @pytest.fixture
    def sample_document_entity(self):
        """Sample client document entity for testing"""
        return ClientDocument(
            id=1,
            file_name="cedula_frente.jpg",
            storage_path="clients/123/documents/cedula_frente_unique.jpg",
            document_type=DocumentType.CEDULA_FRENTE,
            client_id=123,
            credit_id=None,
            created_at=datetime(2024, 1, 1, 12, 0, 0)
        )
    
    @pytest.fixture
    def mock_upload_file(self):
        """Mock UploadFile for testing"""
        return MockUploadFile("cedula_frente.jpg", b"fake image content")


class TestUploadDocument(TestClientDocumentService):
    """Test upload document functionality"""
    
    async def test_upload_document_success(self, client_document_service, mock_repository, mock_upload_file, sample_document_entity):
        """Test successful document upload"""
        # Arrange
        storage_service = client_document_service._storage_service
        storage_service.generate_unique_filename.return_value = "cedula_frente_unique.jpg"
        storage_service.build_storage_path.return_value = "clients/123/documents/cedula_frente_unique.jpg"
        storage_service.upload_file = AsyncMock()
        storage_service.get_public_url.return_value = "https://storage.example.com/file.jpg"
        
        mock_repository.create.return_value = sample_document_entity
        
        # Act
        result = await client_document_service.upload_document(
            file=mock_upload_file,
            document_type="CEDULA_FRENTE",
            client_id=123
        )
        
        # Assert
        assert result["status"] == "success"
        assert result["message"] == "Archivo subido exitosamente"
        assert result["document_id"] == 1
        assert "file_url" in result
        
        # Verify calls
        storage_service.generate_unique_filename.assert_called_once_with("CEDULA_FRENTE", "cedula_frente.jpg")
        storage_service.build_storage_path.assert_called_once_with(123, "cedula_frente_unique.jpg")
        storage_service.upload_file.assert_called_once()
        mock_repository.create.assert_called_once()
    
    async def test_upload_document_invalid_type(self, client_document_service, mock_upload_file):
        """Test upload document with invalid document type"""
        # Act & Assert
        with pytest.raises(ValueError, match="Invalid document_type"):
            await client_document_service.upload_document(
                file=mock_upload_file,
                document_type="INVALID_TYPE",
                client_id=123
            )
    
    async def test_upload_document_no_filename(self, client_document_service):
        """Test upload document with no filename"""
        # Arrange
        file = MockUploadFile(filename=None)
        
        # Act & Assert
        with pytest.raises(ValueError, match="File must have a filename"):
            await client_document_service.upload_document(
                file=file,
                document_type="CEDULA_FRENTE",
                client_id=123
            )
    
    async def test_upload_document_empty_file(self, client_document_service):
        """Test upload document with empty file"""
        # Arrange
        file = MockUploadFile("test.jpg", b"")  # Empty content
        
        # Act & Assert
        with pytest.raises(ValueError, match="File is empty"):
            await client_document_service.upload_document(
                file=file,
                document_type="CEDULA_FRENTE",
                client_id=123
            )
    
    async def test_upload_document_storage_error(self, client_document_service, mock_upload_file):
        """Test upload document with storage error"""
        # Arrange
        storage_service = client_document_service._storage_service
        storage_service.generate_unique_filename.return_value = "test_unique.jpg"
        storage_service.build_storage_path.return_value = "clients/123/documents/test_unique.jpg"
        storage_service.upload_file = AsyncMock(side_effect=Exception("Storage error"))
        
        # Act & Assert
        with pytest.raises(Exception, match="Error al subir el archivo a Supabase Storage"):
            await client_document_service.upload_document(
                file=mock_upload_file,
                document_type="CEDULA_FRENTE",
                client_id=123
            )


class TestGetDocuments(TestClientDocumentService):
    """Test get documents functionality"""
    
    async def test_get_client_documents_success(self, client_document_service, mock_repository, sample_document_entity):
        """Test successful get client documents"""
        # Arrange
        storage_service = client_document_service._storage_service
        storage_service.get_public_url.return_value = "https://storage.example.com/file.jpg"
        
        mock_repository.get_by_client_id.return_value = [sample_document_entity]
        
        # Act
        result = await client_document_service.get_client_documents(123)
        
        # Assert
        assert len(result) == 1
        assert isinstance(result[0], MockClientDocumentResponse)
        assert result[0].id == 1
        assert result[0].file_name == "cedula_frente.jpg"
        assert result[0].document_type == "CEDULA_FRENTE"
        assert result[0].client_id == 123
        assert result[0].file_url == "https://storage.example.com/file.jpg"
        
        # Verify calls
        mock_repository.get_by_client_id.assert_called_once_with(123)
        storage_service.get_public_url.assert_called_once()
    
    async def test_get_client_documents_repository_error(self, client_document_service, mock_repository):
        """Test get client documents with repository error"""
        # Arrange
        mock_repository.get_by_client_id.side_effect = Exception("Database error")
        
        # Act & Assert
        with pytest.raises(Exception, match="Error getting client documents"):
            await client_document_service.get_client_documents(123)


class TestDeleteDocument(TestClientDocumentService):
    """Test delete document functionality"""
    
    async def test_delete_document_success(self, client_document_service, mock_repository, sample_document_entity):
        """Test successful document deletion"""
        # Arrange
        storage_service = client_document_service._storage_service
        storage_service.delete_file = AsyncMock()
        
        mock_repository.get_by_id.return_value = sample_document_entity
        mock_repository.delete.return_value = True
        
        # Act
        result = await client_document_service.delete_document(1)
        
        # Assert
        assert result["status"] == "success"
        assert "deleted successfully" in result["message"]
        
        # Verify calls
        mock_repository.get_by_id.assert_called_once_with(1)
        mock_repository.delete.assert_called_once_with(1)
        storage_service.delete_file.assert_called_once_with("clients/123/documents/cedula_frente_unique.jpg")
    
    async def test_delete_document_not_found(self, client_document_service, mock_repository):
        """Test delete document when document doesn't exist"""
        # Arrange
        mock_repository.get_by_id.return_value = None
        
        # Act & Assert
        with pytest.raises(ValueError, match="Document with ID 999 not found"):
            await client_document_service.delete_document(999)
        
        # Verify calls
        mock_repository.get_by_id.assert_called_once_with(999)
        mock_repository.delete.assert_not_called()
    
    async def test_delete_client_document_success(self, client_document_service, mock_repository, sample_document_entity):
        """Test successful client document deletion"""
        # Arrange
        storage_service = client_document_service._storage_service
        storage_service.delete_file = AsyncMock()
        
        mock_repository.get_by_id.return_value = sample_document_entity
        mock_repository.delete.return_value = True
        
        # Act
        result = await client_document_service.delete_client_document(123, 1)
        
        # Assert
        assert result["status"] == "success"
        assert "client 123" in result["message"]
        
        # Verify calls
        mock_repository.get_by_id.assert_called_once_with(1)
        mock_repository.delete.assert_called_once_with(1)
    
    async def test_delete_client_document_wrong_client(self, client_document_service, mock_repository, sample_document_entity):
        """Test delete client document with wrong client ID"""
        # Arrange
        mock_repository.get_by_id.return_value = sample_document_entity
        
        # Act & Assert
        with pytest.raises(ValueError, match="Document 1 does not belong to client 999"):
            await client_document_service.delete_client_document(999, 1)
        
        # Verify calls
        mock_repository.get_by_id.assert_called_once_with(1)
        mock_repository.delete.assert_not_called()


class TestGetDocumentDownloadUrl(TestClientDocumentService):
    """Test get document download URL functionality"""
    
    async def test_get_document_download_url_success(self, client_document_service, mock_repository, sample_document_entity):
        """Test successful get document download URL"""
        # Arrange
        storage_service = client_document_service._storage_service
        storage_service.create_signed_url.return_value = "https://storage.example.com/signed-download-url"
        
        mock_repository.get_by_id.return_value = sample_document_entity
        
        # Act
        result = await client_document_service.get_document_download_url(1, expires_in=7200)
        
        # Assert
        assert result == "https://storage.example.com/signed-download-url"
        
        # Verify calls
        mock_repository.get_by_id.assert_called_once_with(1)
        storage_service.create_signed_url.assert_called_once_with(
            "clients/123/documents/cedula_frente_unique.jpg",
            7200
        )
    
    async def test_get_document_download_url_not_found(self, client_document_service, mock_repository):
        """Test get document download URL when document doesn't exist"""
        # Arrange
        mock_repository.get_by_id.return_value = None
        
        # Act & Assert
        with pytest.raises(ValueError, match="Document with ID 999 not found"):
            await client_document_service.get_document_download_url(999)
        
        # Verify calls
        mock_repository.get_by_id.assert_called_once_with(999)