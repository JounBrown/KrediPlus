"""
Unit tests for ClientDocument entity
"""
import pytest
from datetime import datetime
from src.domain.entities.client_document import ClientDocument, DocumentType


class TestClientDocumentCreation:
    """Test ClientDocument entity creation"""
    
    def test_client_document_creation_with_defaults(self):
        """Test creating a client document with default values"""
        # Arrange & Act
        doc = ClientDocument()
        
        # Assert
        assert doc.id is None
        assert doc.file_name == ""
        assert doc.storage_path == ""
        assert doc.document_type == DocumentType.OTRO
        assert doc.client_id == 0
        assert doc.credit_id is None
        assert isinstance(doc.created_at, datetime)
    
    def test_client_document_creation_with_all_fields(self):
        """Test creating a client document with all fields"""
        # Arrange
        created_at = datetime(2024, 1, 15, 10, 30, 0)
        
        # Act
        doc = ClientDocument(
            id=123,
            file_name="cedula_frente.jpg",
            storage_path="clients/456/documents/cedula_frente_unique.jpg",
            document_type=DocumentType.CEDULA_FRENTE,
            client_id=456,
            credit_id=789,
            created_at=created_at
        )
        
        # Assert
        assert doc.id == 123
        assert doc.file_name == "cedula_frente.jpg"
        assert doc.storage_path == "clients/456/documents/cedula_frente_unique.jpg"
        assert doc.document_type == DocumentType.CEDULA_FRENTE
        assert doc.client_id == 456
        assert doc.credit_id == 789
        assert doc.created_at == created_at
    
    def test_client_document_creation_with_partial_fields(self):
        """Test creating a client document with some fields"""
        # Arrange & Act
        doc = ClientDocument(
            file_name="comprobante_ingresos.pdf",
            storage_path="clients/123/documents/comprobante.pdf",
            document_type=DocumentType.COMPROBANTE_INGRESOS,
            client_id=123
        )
        
        # Assert
        assert doc.id is None
        assert doc.file_name == "comprobante_ingresos.pdf"
        assert doc.storage_path == "clients/123/documents/comprobante.pdf"
        assert doc.document_type == DocumentType.COMPROBANTE_INGRESOS
        assert doc.client_id == 123
        assert doc.credit_id is None
        assert isinstance(doc.created_at, datetime)


class TestClientDocumentValidation:
    """Test ClientDocument validation methods"""
    
    def test_validate_valid_document(self):
        """Test validation with valid document data"""
        # Arrange
        doc = ClientDocument(
            file_name="cedula_frente.jpg",
            storage_path="clients/123/documents/cedula_frente.jpg",
            document_type=DocumentType.CEDULA_FRENTE,
            client_id=123
        )
        
        # Act & Assert
        assert doc.validate() == True
    
    def test_validate_empty_file_name(self):
        """Test validation with empty file name"""
        # Test completely empty
        doc1 = ClientDocument(
            file_name="",
            storage_path="clients/123/documents/file.jpg",
            document_type=DocumentType.CEDULA_FRENTE,
            client_id=123
        )
        assert doc1.validate() == False
        
        # Test whitespace only
        doc2 = ClientDocument(
            file_name="   ",
            storage_path="clients/123/documents/file.jpg",
            document_type=DocumentType.CEDULA_FRENTE,
            client_id=123
        )
        assert doc2.validate() == False
    
    def test_validate_empty_storage_path(self):
        """Test validation with empty storage path"""
        # Test completely empty
        doc1 = ClientDocument(
            file_name="cedula.jpg",
            storage_path="",
            document_type=DocumentType.CEDULA_FRENTE,
            client_id=123
        )
        assert doc1.validate() == False
        
        # Test whitespace only
        doc2 = ClientDocument(
            file_name="cedula.jpg",
            storage_path="   ",
            document_type=DocumentType.CEDULA_FRENTE,
            client_id=123
        )
        assert doc2.validate() == False
    
    def test_validate_invalid_client_id(self):
        """Test validation with invalid client ID"""
        invalid_client_ids = [0, -1, -100]
        
        for client_id in invalid_client_ids:
            doc = ClientDocument(
                file_name="cedula.jpg",
                storage_path="clients/123/documents/cedula.jpg",
                document_type=DocumentType.CEDULA_FRENTE,
                client_id=client_id
            )
            assert doc.validate() == False, f"Client ID {client_id} should be invalid"
    
    def test_validate_invalid_document_type(self):
        """Test validation with invalid document type"""
        # Arrange
        doc = ClientDocument(
            file_name="cedula.jpg",
            storage_path="clients/123/documents/cedula.jpg",
            client_id=123
        )
        
        # Manually set invalid document type (bypassing enum)
        doc.document_type = "INVALID_TYPE"
        
        # Act & Assert
        assert doc.validate() == False
    
    def test_validate_all_document_types(self):
        """Test validation with all valid document types"""
        for doc_type in DocumentType:
            doc = ClientDocument(
                file_name="test_file.jpg",
                storage_path="clients/123/documents/test.jpg",
                document_type=doc_type,
                client_id=123
            )
            assert doc.validate() == True, f"Document type {doc_type} should be valid"


class TestClientDocumentFileOperations:
    """Test ClientDocument file operation methods"""
    
    def test_get_file_extension_common_formats(self):
        """Test getting file extension for common formats"""
        test_cases = [
            ("document.pdf", "pdf"),
            ("image.jpg", "jpg"),
            ("image.jpeg", "jpeg"),
            ("image.png", "png"),
            ("image.gif", "gif"),
            ("image.bmp", "bmp"),
            ("image.webp", "webp"),
            ("Document.PDF", "pdf"),  # Should be lowercase
            ("IMAGE.JPG", "jpg"),     # Should be lowercase
        ]
        
        for file_name, expected_extension in test_cases:
            doc = ClientDocument(file_name=file_name)
            assert doc.get_file_extension() == expected_extension, f"File '{file_name}' should have extension '{expected_extension}'"
    
    def test_get_file_extension_no_extension(self):
        """Test getting file extension when there's no extension"""
        test_cases = ["document", "file_without_extension", ""]
        
        for file_name in test_cases:
            doc = ClientDocument(file_name=file_name)
            assert doc.get_file_extension() == "", f"File '{file_name}' should have empty extension"
    
    def test_get_file_extension_multiple_dots(self):
        """Test getting file extension with multiple dots"""
        test_cases = [
            ("document.backup.pdf", "pdf"),
            ("file.name.with.dots.jpg", "jpg"),
            ("archive.tar.gz", "gz"),
            ("config.json.bak", "bak")
        ]
        
        for file_name, expected_extension in test_cases:
            doc = ClientDocument(file_name=file_name)
            assert doc.get_file_extension() == expected_extension, f"File '{file_name}' should have extension '{expected_extension}'"
    
    def test_is_image_true_cases(self):
        """Test is_image returns True for image files"""
        image_files = [
            "cedula_frente.jpg",
            "cedula_reverso.jpeg",
            "comprobante.png",
            "documento.gif",
            "scan.bmp",
            "photo.webp",
            "IMAGE.JPG",  # Case insensitive
            "PHOTO.PNG"   # Case insensitive
        ]
        
        for file_name in image_files:
            doc = ClientDocument(file_name=file_name)
            assert doc.is_image() == True, f"File '{file_name}' should be recognized as image"
    
    def test_is_image_false_cases(self):
        """Test is_image returns False for non-image files"""
        non_image_files = [
            "document.pdf",
            "contract.doc",
            "spreadsheet.xlsx",
            "text.txt",
            "archive.zip",
            "no_extension",
            "",
            "file.unknown"
        ]
        
        for file_name in non_image_files:
            doc = ClientDocument(file_name=file_name)
            assert doc.is_image() == False, f"File '{file_name}' should not be recognized as image"
    
    def test_is_pdf_true_cases(self):
        """Test is_pdf returns True for PDF files"""
        pdf_files = [
            "document.pdf",
            "contract.PDF",  # Case insensitive
            "file.name.with.dots.pdf",
            "DOCUMENT.PDF"
        ]
        
        for file_name in pdf_files:
            doc = ClientDocument(file_name=file_name)
            assert doc.is_pdf() == True, f"File '{file_name}' should be recognized as PDF"
    
    def test_is_pdf_false_cases(self):
        """Test is_pdf returns False for non-PDF files"""
        non_pdf_files = [
            "image.jpg",
            "document.doc",
            "spreadsheet.xlsx",
            "text.txt",
            "no_extension",
            "",
            "file.unknown",
            "pdffile"  # No extension
        ]
        
        for file_name in non_pdf_files:
            doc = ClientDocument(file_name=file_name)
            assert doc.is_pdf() == False, f"File '{file_name}' should not be recognized as PDF"


class TestDocumentTypeEnum:
    """Test DocumentType enumeration"""
    
    def test_all_document_types_exist(self):
        """Test that all expected document types exist"""
        expected_types = [
            "CEDULA_FRENTE",
            "CEDULA_REVERSO", 
            "COMPROBANTE_INGRESOS",
            "CERTIFICADO_LABORAL",
            "SOLICITUD_CREDITO_FIRMADA",
            "PAGARE_FIRMADO",
            "COMPROBANTE_DOMICILIO",
            "EXTRACTO_BANCARIO",
            "OTRO"
        ]
        
        for type_name in expected_types:
            assert hasattr(DocumentType, type_name), f"DocumentType should have {type_name}"
            assert isinstance(getattr(DocumentType, type_name), DocumentType)
    
    def test_document_type_values(self):
        """Test that document type values match their names"""
        for doc_type in DocumentType:
            assert doc_type.value == doc_type.name
    
    def test_document_type_in_client_document(self):
        """Test using document types in ClientDocument"""
        for doc_type in DocumentType:
            doc = ClientDocument(
                file_name="test.jpg",
                storage_path="test/path.jpg",
                document_type=doc_type,
                client_id=123
            )
            assert doc.document_type == doc_type
            assert doc.validate() == True


class TestClientDocumentBusinessLogic:
    """Test ClientDocument business logic and workflows"""
    
    def test_cedula_document_workflow(self):
        """Test complete cedula document workflow"""
        # Arrange
        cedula_frente = ClientDocument(
            file_name="cedula_frente.jpg",
            storage_path="clients/123/documents/cedula_frente_unique.jpg",
            document_type=DocumentType.CEDULA_FRENTE,
            client_id=123
        )
        
        cedula_reverso = ClientDocument(
            file_name="cedula_reverso.jpg",
            storage_path="clients/123/documents/cedula_reverso_unique.jpg",
            document_type=DocumentType.CEDULA_REVERSO,
            client_id=123
        )
        
        # Act & Assert
        assert cedula_frente.validate() == True
        assert cedula_frente.is_image() == True
        assert cedula_frente.is_pdf() == False
        assert cedula_frente.get_file_extension() == "jpg"
        
        assert cedula_reverso.validate() == True
        assert cedula_reverso.is_image() == True
        assert cedula_reverso.is_pdf() == False
        assert cedula_reverso.get_file_extension() == "jpg"
    
    def test_income_proof_document_workflow(self):
        """Test income proof document workflow"""
        # Arrange
        comprobante = ClientDocument(
            file_name="comprobante_ingresos.pdf",
            storage_path="clients/456/documents/comprobante_ingresos_unique.pdf",
            document_type=DocumentType.COMPROBANTE_INGRESOS,
            client_id=456,
            credit_id=789
        )
        
        # Act & Assert
        assert comprobante.validate() == True
        assert comprobante.is_image() == False
        assert comprobante.is_pdf() == True
        assert comprobante.get_file_extension() == "pdf"
        assert comprobante.credit_id == 789  # Associated with credit
    
    def test_credit_related_documents_workflow(self):
        """Test credit-related documents workflow"""
        credit_documents = [
            (DocumentType.SOLICITUD_CREDITO_FIRMADA, "solicitud_firmada.pdf"),
            (DocumentType.PAGARE_FIRMADO, "pagare_firmado.pdf"),
            (DocumentType.EXTRACTO_BANCARIO, "extracto_bancario.pdf")
        ]
        
        for doc_type, file_name in credit_documents:
            doc = ClientDocument(
                file_name=file_name,
                storage_path=f"clients/123/credits/456/{file_name}",
                document_type=doc_type,
                client_id=123,
                credit_id=456
            )
            
            assert doc.validate() == True
            assert doc.is_pdf() == True
            assert doc.credit_id == 456
    
    def test_document_without_credit_association(self):
        """Test documents that don't need credit association"""
        non_credit_documents = [
            (DocumentType.CEDULA_FRENTE, "cedula_frente.jpg"),
            (DocumentType.CEDULA_REVERSO, "cedula_reverso.jpg"),
            (DocumentType.COMPROBANTE_DOMICILIO, "comprobante_domicilio.pdf"),
            (DocumentType.CERTIFICADO_LABORAL, "certificado_laboral.pdf")
        ]
        
        for doc_type, file_name in non_credit_documents:
            doc = ClientDocument(
                file_name=file_name,
                storage_path=f"clients/123/documents/{file_name}",
                document_type=doc_type,
                client_id=123
                # No credit_id - should remain None
            )
            
            assert doc.validate() == True
            assert doc.credit_id is None


class TestClientDocumentEdgeCases:
    """Test edge cases and boundary conditions"""
    
    def test_file_name_with_special_characters(self):
        """Test file names with special characters"""
        special_file_names = [
            "cédula_frente_ñ.jpg",
            "comprobante (1).pdf",
            "documento-con-guiones.jpg",
            "file_with_underscores.pdf",
            "file with spaces.jpg",
            "file@symbol.pdf",
            "file#hash.jpg",
            "file$dollar.pdf"
        ]
        
        for file_name in special_file_names:
            doc = ClientDocument(
                file_name=file_name,
                storage_path="clients/123/documents/file.jpg",
                document_type=DocumentType.OTRO,
                client_id=123
            )
            assert doc.validate() == True, f"File name '{file_name}' should be valid"
            assert doc.file_name == file_name
    
    def test_storage_path_variations(self):
        """Test different storage path formats"""
        storage_paths = [
            "clients/123/documents/file.jpg",
            "/absolute/path/to/file.jpg",
            "relative/path/file.jpg",
            "clients\\123\\documents\\file.jpg",  # Windows style
            "clients/123/sub/folder/deep/file.jpg",
            "s3://bucket/clients/123/file.jpg",
            "https://storage.example.com/file.jpg"
        ]
        
        for storage_path in storage_paths:
            doc = ClientDocument(
                file_name="test.jpg",
                storage_path=storage_path,
                document_type=DocumentType.OTRO,
                client_id=123
            )
            assert doc.validate() == True, f"Storage path '{storage_path}' should be valid"
            assert doc.storage_path == storage_path
    
    def test_large_client_ids(self):
        """Test with large client IDs"""
        large_client_ids = [999999, 1000000, 2147483647]  # Including max int32
        
        for client_id in large_client_ids:
            doc = ClientDocument(
                file_name="test.jpg",
                storage_path="clients/test/file.jpg",
                document_type=DocumentType.OTRO,
                client_id=client_id
            )
            assert doc.validate() == True, f"Client ID {client_id} should be valid"
            assert doc.client_id == client_id
    
    def test_created_at_edge_cases(self):
        """Test created_at with various datetime values"""
        # Test very old date
        old_date = datetime(1970, 1, 1, 0, 0, 0)
        doc1 = ClientDocument(
            file_name="old_doc.jpg",
            storage_path="clients/123/old_doc.jpg",
            document_type=DocumentType.OTRO,
            client_id=123,
            created_at=old_date
        )
        assert doc1.validate() == True
        assert doc1.created_at == old_date
        
        # Test future date
        future_date = datetime(2030, 12, 31, 23, 59, 59)
        doc2 = ClientDocument(
            file_name="future_doc.jpg",
            storage_path="clients/123/future_doc.jpg",
            document_type=DocumentType.OTRO,
            client_id=123,
            created_at=future_date
        )
        assert doc2.validate() == True
        assert doc2.created_at == future_date
        
        # Test microseconds precision
        precise_date = datetime(2024, 6, 15, 14, 30, 45, 123456)
        doc3 = ClientDocument(
            file_name="precise_doc.jpg",
            storage_path="clients/123/precise_doc.jpg",
            document_type=DocumentType.OTRO,
            client_id=123,
            created_at=precise_date
        )
        assert doc3.validate() == True
        assert doc3.created_at == precise_date
    
    def test_file_extension_edge_cases(self):
        """Test file extension detection edge cases"""
        edge_cases = [
            ("file.", ""),           # Ends with dot
            (".hidden", "hidden"),   # Starts with dot (hidden file) - actually has extension
            ("file..jpg", "jpg"),    # Double dots
            ("file.tar.gz", "gz"),   # Multiple extensions
            ("file.JPEG", "jpeg"),   # Mixed case
            ("file.123", "123"),     # Numeric extension
            ("file.a", "a"),         # Single character extension
            ("file.verylongextension", "verylongextension")  # Long extension
        ]
        
        for file_name, expected_extension in edge_cases:
            doc = ClientDocument(file_name=file_name)
            assert doc.get_file_extension() == expected_extension, f"File '{file_name}' should have extension '{expected_extension}'"
    
    def test_validation_immutability(self):
        """Test that validation methods don't modify document data"""
        # Arrange
        original_data = {
            'id': 123,
            'file_name': "test_document.pdf",
            'storage_path': "clients/456/documents/test.pdf",
            'document_type': DocumentType.COMPROBANTE_INGRESOS,
            'client_id': 456,
            'credit_id': 789,
            'created_at': datetime(2024, 1, 1, 12, 0, 0)
        }
        
        doc = ClientDocument(**original_data)
        
        # Act - Call methods multiple times
        for _ in range(5):
            doc.validate()
            doc.get_file_extension()
            doc.is_image()
            doc.is_pdf()
        
        # Assert - Data should remain unchanged
        assert doc.id == original_data['id']
        assert doc.file_name == original_data['file_name']
        assert doc.storage_path == original_data['storage_path']
        assert doc.document_type == original_data['document_type']
        assert doc.client_id == original_data['client_id']
        assert doc.credit_id == original_data['credit_id']
        assert doc.created_at == original_data['created_at']