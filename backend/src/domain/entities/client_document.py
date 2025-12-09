from datetime import datetime
from typing import Optional
from enum import Enum


class DocumentType(Enum):
    """Document type enumeration"""
    CEDULA_FRENTE = "CEDULA_FRENTE"
    CEDULA_REVERSO = "CEDULA_REVERSO"
    COMPROBANTE_INGRESOS = "COMPROBANTE_INGRESOS"
    CERTIFICADO_LABORAL = "CERTIFICADO_LABORAL"
    SOLICITUD_CREDITO_FIRMADA = "SOLICITUD_CREDITO_FIRMADA"
    PAGARE_FIRMADO = "PAGARE_FIRMADO"
    COMPROBANTE_DOMICILIO = "COMPROBANTE_DOMICILIO"
    EXTRACTO_BANCARIO = "EXTRACTO_BANCARIO"
    OTRO = "OTRO"


class ClientDocument:
    """Client Document domain entity"""
    
    def __init__(
        self,
        id: Optional[int] = None,
        file_name: str = "",
        storage_path: str = "",
        document_type: DocumentType = DocumentType.OTRO,
        client_id: int = 0,
        credit_id: Optional[int] = None,
        created_at: Optional[datetime] = None
    ):
        self.id = id
        self.file_name = file_name
        self.storage_path = storage_path
        self.document_type = document_type
        self.client_id = client_id
        self.credit_id = credit_id
        self.created_at = created_at or datetime.now()
    
    def validate(self) -> bool:
        """Validate client document"""
        if not self.file_name or not self.file_name.strip():
            return False
        
        if not self.storage_path or not self.storage_path.strip():
            return False
        
        if self.client_id <= 0:
            return False
        
        if not isinstance(self.document_type, DocumentType):
            return False
        
        return True
    
    def get_file_extension(self) -> str:
        """Get file extension from file name"""
        if '.' in self.file_name:
            return self.file_name.split('.')[-1].lower()
        return ""
    
    def is_image(self) -> bool:
        """Check if document is an image"""
        image_extensions = ['jpg', 'jpeg', 'png', 'gif', 'bmp', 'webp']
        return self.get_file_extension() in image_extensions
    
    def is_pdf(self) -> bool:
        """Check if document is a PDF"""
        return self.get_file_extension() == 'pdf'