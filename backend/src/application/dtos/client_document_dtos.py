from pydantic import BaseModel, Field, validator
from typing import Optional
from enum import Enum


class DocumentTypeDto(str, Enum):
    """Document type enumeration for DTOs"""
    CEDULA_FRENTE = "CEDULA_FRENTE"
    CEDULA_REVERSO = "CEDULA_REVERSO"
    COMPROBANTE_INGRESOS = "COMPROBANTE_INGRESOS"
    CERTIFICADO_LABORAL = "CERTIFICADO_LABORAL"
    SOLICITUD_CREDITO_FIRMADA = "SOLICITUD_CREDITO_FIRMADA"
    PAGARE_FIRMADO = "PAGARE_FIRMADO"
    COMPROBANTE_DOMICILIO = "COMPROBANTE_DOMICILIO"
    EXTRACTO_BANCARIO = "EXTRACTO_BANCARIO"
    OTRO = "OTRO"


class CreateClientDocumentRequest(BaseModel):
    """DTO for creating client document"""
    file_name: str = Field(..., min_length=1, description="Document file name")
    storage_path: str = Field(..., min_length=1, description="Storage path for the document")
    document_type: DocumentTypeDto = Field(..., description="Type of document")
    client_id: int = Field(..., gt=0, description="Client ID")
    credit_id: Optional[int] = Field(None, gt=0, description="Credit ID (optional)")
    
    @validator('file_name')
    def validate_file_name(cls, v):
        if not v or not v.strip():
            raise ValueError('El nombre del archivo es requerido')
        return v.strip()
    
    @validator('storage_path')
    def validate_storage_path(cls, v):
        if not v or not v.strip():
            raise ValueError('La ruta de almacenamiento es requerida')
        return v.strip()


class UpdateClientDocumentRequest(BaseModel):
    """DTO for updating client document (partial updates allowed)"""
    file_name: Optional[str] = Field(None, min_length=1, description="Document file name")
    storage_path: Optional[str] = Field(None, min_length=1, description="Storage path for the document")
    document_type: Optional[DocumentTypeDto] = Field(None, description="Type of document")
    credit_id: Optional[int] = Field(None, gt=0, description="Credit ID (optional)")
    
    @validator('file_name')
    def validate_file_name(cls, v):
        if v is not None and (not v or not v.strip()):
            raise ValueError('El nombre del archivo no puede estar vacío')
        return v.strip() if v else v
    
    @validator('storage_path')
    def validate_storage_path(cls, v):
        if v is not None and (not v or not v.strip()):
            raise ValueError('La ruta de almacenamiento no puede estar vacía')
        return v.strip() if v else v


class ClientDocumentResponse(BaseModel):
    """DTO for client document response"""
    id: int
    file_name: str
    storage_path: str
    document_type: DocumentTypeDto
    client_id: int
    credit_id: Optional[int]
    created_at: str
    file_url: str
    
    class Config:
        from_attributes = True