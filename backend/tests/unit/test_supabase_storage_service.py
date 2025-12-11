"""Tests for SupabaseStorageService"""
import pytest
from unittest.mock import MagicMock, patch, AsyncMock


class TestSupabaseStorageService:
    """Tests for SupabaseStorageService"""

    @pytest.fixture
    def mock_supabase_client(self):
        return MagicMock()

    @pytest.fixture
    def service(self, mock_supabase_client):
        with patch('src.infrastructure.adapters.storage.supabase_storage_service.create_client', return_value=mock_supabase_client):
            from src.infrastructure.adapters.storage.supabase_storage_service import SupabaseStorageService
            svc = SupabaseStorageService()
            svc.supabase = mock_supabase_client
            return svc


class TestGenerateUniqueFilename:
    """Tests for generate_unique_filename method"""

    @pytest.fixture
    def service(self):
        with patch('src.infrastructure.adapters.storage.supabase_storage_service.create_client'):
            from src.infrastructure.adapters.storage.supabase_storage_service import SupabaseStorageService
            return SupabaseStorageService()

    def test_generate_filename_with_extension(self, service):
        """Test filename generation with extension"""
        result = service.generate_unique_filename("CEDULA_FRENTE", "document.pdf")

        assert result.startswith("CEDULA_FRENTE_")
        assert result.endswith(".pdf")
        assert len(result) > len("CEDULA_FRENTE_.pdf")

    def test_generate_filename_without_extension(self, service):
        """Test filename generation without extension"""
        result = service.generate_unique_filename("CEDULA_FRENTE", "document")

        assert result.startswith("CEDULA_FRENTE_")
        assert "." not in result.split("_")[-1]  # No extension in UUID part

    def test_generate_filename_uppercase_extension(self, service):
        """Test filename generation normalizes extension to lowercase"""
        result = service.generate_unique_filename("CEDULA_FRENTE", "document.PDF")

        assert result.endswith(".pdf")

    def test_generate_unique_filenames(self, service):
        """Test that generated filenames are unique"""
        result1 = service.generate_unique_filename("CEDULA_FRENTE", "doc.pdf")
        result2 = service.generate_unique_filename("CEDULA_FRENTE", "doc.pdf")

        assert result1 != result2


class TestBuildStoragePath:
    """Tests for build_storage_path method"""

    @pytest.fixture
    def service(self):
        with patch('src.infrastructure.adapters.storage.supabase_storage_service.create_client'):
            from src.infrastructure.adapters.storage.supabase_storage_service import SupabaseStorageService
            return SupabaseStorageService()

    def test_build_storage_path(self, service):
        """Test storage path building"""
        result = service.build_storage_path(123, "document.pdf")

        assert result == "client_files/123/document.pdf"

    def test_build_storage_path_different_client(self, service):
        """Test storage path with different client ID"""
        result = service.build_storage_path(456, "file.jpg")

        assert result == "client_files/456/file.jpg"


class TestUploadFile:
    """Tests for upload_file method"""

    @pytest.fixture
    def service(self):
        with patch('src.infrastructure.adapters.storage.supabase_storage_service.create_client') as mock_create:
            mock_client = MagicMock()
            mock_create.return_value = mock_client
            from src.infrastructure.adapters.storage.supabase_storage_service import SupabaseStorageService
            svc = SupabaseStorageService()
            return svc, mock_client

    async def test_upload_file_success(self, service):
        """Test successful file upload"""
        svc, mock_client = service
        mock_storage = MagicMock()
        mock_bucket = MagicMock()
        mock_response = MagicMock()
        mock_response.error = None
        mock_bucket.upload.return_value = mock_response
        mock_storage.from_.return_value = mock_bucket
        mock_client.storage = mock_storage

        result = await svc.upload_file(b"file content", "path/file.pdf")

        assert result is True
        mock_bucket.upload.assert_called_once()

    async def test_upload_file_with_error_response(self, service):
        """Test upload with error in response"""
        svc, mock_client = service
        mock_storage = MagicMock()
        mock_bucket = MagicMock()
        mock_response = MagicMock()
        mock_response.error = "Upload failed"
        mock_bucket.upload.return_value = mock_response
        mock_storage.from_.return_value = mock_bucket
        mock_client.storage = mock_storage

        with pytest.raises(Exception) as exc_info:
            await svc.upload_file(b"file content", "path/file.pdf")

        assert "Supabase Storage error" in str(exc_info.value)

    async def test_upload_file_exception(self, service):
        """Test upload with exception"""
        svc, mock_client = service
        mock_storage = MagicMock()
        mock_bucket = MagicMock()
        mock_bucket.upload.side_effect = Exception("Network error")
        mock_storage.from_.return_value = mock_bucket
        mock_client.storage = mock_storage

        with pytest.raises(Exception) as exc_info:
            await svc.upload_file(b"file content", "path/file.pdf")

        assert "Error uploading file" in str(exc_info.value)


class TestDeleteFile:
    """Tests for delete_file method"""

    @pytest.fixture
    def service(self):
        with patch('src.infrastructure.adapters.storage.supabase_storage_service.create_client') as mock_create:
            mock_client = MagicMock()
            mock_create.return_value = mock_client
            from src.infrastructure.adapters.storage.supabase_storage_service import SupabaseStorageService
            svc = SupabaseStorageService()
            return svc, mock_client

    async def test_delete_file_success(self, service):
        """Test successful file deletion"""
        svc, mock_client = service
        mock_storage = MagicMock()
        mock_bucket = MagicMock()
        mock_response = MagicMock()
        mock_response.error = None
        mock_bucket.remove.return_value = mock_response
        mock_storage.from_.return_value = mock_bucket
        mock_client.storage = mock_storage

        result = await svc.delete_file("path/file.pdf")

        assert result is True
        mock_bucket.remove.assert_called_once_with(["path/file.pdf"])

    async def test_delete_file_with_error(self, service):
        """Test delete with error (returns False, doesn't raise)"""
        svc, mock_client = service
        mock_storage = MagicMock()
        mock_bucket = MagicMock()
        mock_bucket.remove.side_effect = Exception("File not found")
        mock_storage.from_.return_value = mock_bucket
        mock_client.storage = mock_storage

        result = await svc.delete_file("path/nonexistent.pdf")

        assert result is False


class TestGetPublicUrl:
    """Tests for get_public_url method"""

    @pytest.fixture
    def service(self):
        with patch('src.infrastructure.adapters.storage.supabase_storage_service.create_client') as mock_create:
            mock_client = MagicMock()
            mock_create.return_value = mock_client
            from src.infrastructure.adapters.storage.supabase_storage_service import SupabaseStorageService
            svc = SupabaseStorageService()
            return svc, mock_client

    def test_get_public_url_success(self, service):
        """Test getting public URL"""
        svc, mock_client = service
        mock_storage = MagicMock()
        mock_bucket = MagicMock()
        mock_bucket.get_public_url.return_value = "https://storage.supabase.co/bucket/file.pdf"
        mock_storage.from_.return_value = mock_bucket
        mock_client.storage = mock_storage

        result = svc.get_public_url("path/file.pdf")

        assert result == "https://storage.supabase.co/bucket/file.pdf"

    def test_get_public_url_error(self, service):
        """Test get_public_url with error"""
        svc, mock_client = service
        mock_storage = MagicMock()
        mock_bucket = MagicMock()
        mock_bucket.get_public_url.side_effect = Exception("Error")
        mock_storage.from_.return_value = mock_bucket
        mock_client.storage = mock_storage

        with pytest.raises(Exception) as exc_info:
            svc.get_public_url("path/file.pdf")

        assert "Error getting public URL" in str(exc_info.value)


class TestCreateSignedUrl:
    """Tests for create_signed_url method"""

    @pytest.fixture
    def service(self):
        with patch('src.infrastructure.adapters.storage.supabase_storage_service.create_client') as mock_create:
            mock_client = MagicMock()
            mock_create.return_value = mock_client
            from src.infrastructure.adapters.storage.supabase_storage_service import SupabaseStorageService
            svc = SupabaseStorageService()
            return svc, mock_client

    def test_create_signed_url_success(self, service):
        """Test creating signed URL"""
        svc, mock_client = service
        mock_storage = MagicMock()
        mock_bucket = MagicMock()
        mock_response = {"signedURL": "https://storage.supabase.co/signed/file.pdf?token=abc"}
        mock_bucket.create_signed_url.return_value = mock_response
        mock_storage.from_.return_value = mock_bucket
        mock_client.storage = mock_storage

        result = svc.create_signed_url("path/file.pdf")

        assert "signed" in result
        mock_bucket.create_signed_url.assert_called_once_with(path="path/file.pdf", expires_in=3600)

    def test_create_signed_url_custom_expiry(self, service):
        """Test creating signed URL with custom expiry"""
        svc, mock_client = service
        mock_storage = MagicMock()
        mock_bucket = MagicMock()
        mock_response = {"signedURL": "https://storage.supabase.co/signed/file.pdf"}
        mock_bucket.create_signed_url.return_value = mock_response
        mock_storage.from_.return_value = mock_bucket
        mock_client.storage = mock_storage

        svc.create_signed_url("path/file.pdf", expires_in=7200)

        mock_bucket.create_signed_url.assert_called_once_with(path="path/file.pdf", expires_in=7200)

    def test_create_signed_url_with_error_response(self, service):
        """Test create_signed_url with error in response"""
        svc, mock_client = service
        mock_storage = MagicMock()
        mock_bucket = MagicMock()
        mock_response = MagicMock()
        mock_response.error = "Token error"
        mock_response.get.return_value = ""
        mock_bucket.create_signed_url.return_value = mock_response
        mock_storage.from_.return_value = mock_bucket
        mock_client.storage = mock_storage

        with pytest.raises(Exception) as exc_info:
            svc.create_signed_url("path/file.pdf")

        assert "Supabase Storage error" in str(exc_info.value)

    def test_create_signed_url_exception(self, service):
        """Test create_signed_url with exception"""
        svc, mock_client = service
        mock_storage = MagicMock()
        mock_bucket = MagicMock()
        mock_bucket.create_signed_url.side_effect = Exception("Network error")
        mock_storage.from_.return_value = mock_bucket
        mock_client.storage = mock_storage

        with pytest.raises(Exception) as exc_info:
            svc.create_signed_url("path/file.pdf")

        assert "Error creating signed URL" in str(exc_info.value)
