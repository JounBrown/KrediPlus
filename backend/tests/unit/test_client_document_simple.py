"""
Simplified unit tests for ClientDocument entity and related logic
"""
import pytest
from datetime import datetime
from src.domain.entities.client_document import ClientDocument, DocumentType


class TestClientDocumentEntity:
    """Test ClientDocument entity functionality"""
    
    def test_client_document_creation_with_valid_data(self):
        """Test creating a valid client document"""
        # Arrange & Act
        document = ClientDocument(
            id=1,
            file_name="cedula_frente.jpg",
            storage_path="clients/123/documents/cedula_frente_unique.jpg",
            document_type=DocumentType.CEDULA_FRENTE,
            client_id=123,
            credit_id=None
        )
        
        # Assert
        assert document.id == 1
        assert document.file_name == "cedula_frente.jpg"
        assert document.storage_path == "clients/123/documents/cedula_frente_unique.jpg"
        assert document.document_type == DocumentType.CEDULA_FRENTE
        assert document.client_id == 123
        assert document.credit_id is None
        assert isinstance(document.created_at, datetime)
    
    def test_client_document_validation_success(self):
        """Test successful document validation"""
        # Arrange
        document = ClientDocument(
            file_name="test_document.pdf",
            storage_path="clients/123/documents/test_document.pdf",
            document_type=DocumentType.COMPROBANTE_INGRESOS,
            client_id=123
        )
        
        # Act & Assert
        assert document.validate() == True
    
    def test_client_document_validation_failures(self):
        """Test document validation failures"""
        # Test empty file name
        document = ClientDocument(
            file_name="",
            storage_path="clients/123/documents/test.pdf",
            document_type=DocumentType.CEDULA_FRENTE,
            client_id=123
        )
        assert document.validate() == False
        
        # Test empty storage path
        document = ClientDocument(
            file_name="test.pdf",
            storage_path="",
            document_type=DocumentType.CEDULA_FRENTE,
            client_id=123
        )
        assert document.validate() == False
        
        # Test invalid client_id
        document = ClientDocument(
            file_name="test.pdf",
            storage_path="clients/123/documents/test.pdf",
            document_type=DocumentType.CEDULA_FRENTE,
            client_id=0
        )
        assert document.validate() == False
        
        # Test negative client_id
        document = ClientDocument(
            file_name="test.pdf",
            storage_path="clients/123/documents/test.pdf",
            document_type=DocumentType.CEDULA_FRENTE,
            client_id=-1
        )
        assert document.validate() == False
    
    def test_document_type_enum_values(self):
        """Test that all document types are valid"""
        # Test all enum values
        valid_types = [
            DocumentType.CEDULA_FRENTE,
            DocumentType.CEDULA_REVERSO,
            DocumentType.COMPROBANTE_INGRESOS,
            DocumentType.CERTIFICADO_LABORAL,
            DocumentType.SOLICITUD_CREDITO_FIRMADA,
            DocumentType.PAGARE_FIRMADO,
            DocumentType.COMPROBANTE_DOMICILIO,
            DocumentType.EXTRACTO_BANCARIO,
            DocumentType.OTRO
        ]
        
        for doc_type in valid_types:
            document = ClientDocument(
                file_name="test.pdf",
                storage_path="clients/123/documents/test.pdf",
                document_type=doc_type,
                client_id=123
            )
            assert document.validate() == True
            assert document.document_type == doc_type
    
    def test_document_file_extension_detection(self):
        """Test file extension detection"""
        # Test various file extensions
        test_cases = [
            ("document.pdf", "pdf"),
            ("image.jpg", "jpg"),
            ("image.jpeg", "jpeg"),
            ("image.png", "png"),
            ("document.docx", "docx"),
            ("file_without_extension", ""),
            ("file.with.multiple.dots.pdf", "pdf")
        ]
        
        for filename, expected_ext in test_cases:
            document = ClientDocument(
                file_name=filename,
                storage_path="clients/123/documents/" + filename,
                document_type=DocumentType.OTRO,
                client_id=123
            )
            assert document.get_file_extension() == expected_ext
    
    def test_document_type_detection_methods(self):
        """Test document type detection methods"""
        # Test image detection
        image_files = ["photo.jpg", "scan.jpeg", "image.png", "pic.gif", "bitmap.bmp", "modern.webp"]
        
        for filename in image_files:
            document = ClientDocument(
                file_name=filename,
                storage_path="clients/123/documents/" + filename,
                document_type=DocumentType.CEDULA_FRENTE,
                client_id=123
            )
            assert document.is_image() == True
            assert document.is_pdf() == False
        
        # Test PDF detection
        pdf_files = ["document.pdf", "contract.PDF"]
        
        for filename in pdf_files:
            document = ClientDocument(
                file_name=filename,
                storage_path="clients/123/documents/" + filename,
                document_type=DocumentType.COMPROBANTE_INGRESOS,
                client_id=123
            )
            assert document.is_pdf() == True
            assert document.is_image() == False
        
        # Test other file types
        other_files = ["document.docx", "spreadsheet.xlsx", "text.txt"]
        
        for filename in other_files:
            document = ClientDocument(
                file_name=filename,
                storage_path="clients/123/documents/" + filename,
                document_type=DocumentType.OTRO,
                client_id=123
            )
            assert document.is_pdf() == False
            assert document.is_image() == False
    
    def test_document_with_credit_id(self):
        """Test document associated with a credit"""
        # Arrange & Act
        document = ClientDocument(
            file_name="pagare_firmado.pdf",
            storage_path="clients/123/documents/pagare_firmado.pdf",
            document_type=DocumentType.PAGARE_FIRMADO,
            client_id=123,
            credit_id=456
        )
        
        # Assert
        assert document.validate() == True
        assert document.client_id == 123
        assert document.credit_id == 456
        assert document.document_type == DocumentType.PAGARE_FIRMADO
    
    def test_document_creation_with_defaults(self):
        """Test document creation with default values"""
        # Arrange & Act
        document = ClientDocument()
        
        # Assert
        assert document.id is None
        assert document.file_name == ""
        assert document.storage_path == ""
        assert document.document_type == DocumentType.OTRO
        assert document.client_id == 0
        assert document.credit_id is None
        assert isinstance(document.created_at, datetime)
        
        # Should not validate with defaults
        assert document.validate() == False
    
    def test_document_string_representations(self):
        """Test that document enum values are strings"""
        # Test that enum values can be converted to strings
        for doc_type in DocumentType:
            assert isinstance(doc_type.value, str)
            assert len(doc_type.value) > 0
            assert doc_type.value.isupper()  # All enum values should be uppercase
    
    def test_document_business_logic_patterns(self):
        """Test common patterns that would be used in services"""
        # Create multiple documents for testing
        documents = [
            ClientDocument(
                id=1,
                file_name="cedula_frente.jpg",
                storage_path="clients/123/documents/cedula_frente.jpg",
                document_type=DocumentType.CEDULA_FRENTE,
                client_id=123
            ),
            ClientDocument(
                id=2,
                file_name="cedula_reverso.jpg",
                storage_path="clients/123/documents/cedula_reverso.jpg",
                document_type=DocumentType.CEDULA_REVERSO,
                client_id=123
            ),
            ClientDocument(
                id=3,
                file_name="pagare.pdf",
                storage_path="clients/123/documents/pagare.pdf",
                document_type=DocumentType.PAGARE_FIRMADO,
                client_id=123,
                credit_id=456
            ),
            ClientDocument(
                id=4,
                file_name="comprobante.pdf",
                storage_path="clients/456/documents/comprobante.pdf",
                document_type=DocumentType.COMPROBANTE_INGRESOS,
                client_id=456
            )
        ]
        
        # Test filtering by client_id
        client_123_docs = [doc for doc in documents if doc.client_id == 123]
        assert len(client_123_docs) == 3
        
        # Test filtering by credit_id
        credit_docs = [doc for doc in documents if doc.credit_id == 456]
        assert len(credit_docs) == 1
        assert credit_docs[0].document_type == DocumentType.PAGARE_FIRMADO
        
        # Test filtering by document type
        cedula_docs = [doc for doc in documents if doc.document_type in [DocumentType.CEDULA_FRENTE, DocumentType.CEDULA_REVERSO]]
        assert len(cedula_docs) == 2
        
        # Test finding by ID
        target_id = 2
        found_doc = next((doc for doc in documents if doc.id == target_id), None)
        assert found_doc is not None
        assert found_doc.document_type == DocumentType.CEDULA_REVERSO
        
        # Test validation of all documents
        valid_docs = [doc for doc in documents if doc.validate()]
        assert len(valid_docs) == len(documents)  # All should be valid
    
    def test_document_edge_cases(self):
        """Test edge cases and boundary conditions"""
        # Test with whitespace in file names
        document = ClientDocument(
            file_name="  test.pdf  ",
            storage_path="clients/123/documents/test.pdf",
            document_type=DocumentType.OTRO,
            client_id=123
        )
        # Should still validate (service layer should handle trimming)
        assert document.validate() == True
        
        # Test with very long file names
        long_filename = "a" * 200 + ".pdf"
        document = ClientDocument(
            file_name=long_filename,
            storage_path="clients/123/documents/" + long_filename,
            document_type=DocumentType.OTRO,
            client_id=123
        )
        assert document.validate() == True
        
        # Test with special characters in file names
        special_filename = "documento_ñ_áéíóú_#$%&.pdf"
        document = ClientDocument(
            file_name=special_filename,
            storage_path="clients/123/documents/" + special_filename,
            document_type=DocumentType.OTRO,
            client_id=123
        )
        assert document.validate() == True
    
    def test_document_type_string_values(self):
        """Test that document type enum string values are correct"""
        expected_values = {
            DocumentType.CEDULA_FRENTE: "CEDULA_FRENTE",
            DocumentType.CEDULA_REVERSO: "CEDULA_REVERSO",
            DocumentType.COMPROBANTE_INGRESOS: "COMPROBANTE_INGRESOS",
            DocumentType.CERTIFICADO_LABORAL: "CERTIFICADO_LABORAL",
            DocumentType.SOLICITUD_CREDITO_FIRMADA: "SOLICITUD_CREDITO_FIRMADA",
            DocumentType.PAGARE_FIRMADO: "PAGARE_FIRMADO",
            DocumentType.COMPROBANTE_DOMICILIO: "COMPROBANTE_DOMICILIO",
            DocumentType.EXTRACTO_BANCARIO: "EXTRACTO_BANCARIO",
            DocumentType.OTRO: "OTRO"
        }
        
        for doc_type, expected_value in expected_values.items():
            assert doc_type.value == expected_value