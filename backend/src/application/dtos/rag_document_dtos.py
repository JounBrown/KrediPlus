from pydantic import BaseModel, Field
from typing import Optional
from enum import Enum


class ProcessingStatusDto(str, Enum):
    """Processing status enumeration for DTOs"""
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"


class ContextDocumentResponse(BaseModel):
    """DTO for context document response"""
    id: int
    filename: str
    storage_url: str
    processing_status: ProcessingStatusDto
    created_at: Optional[str] = None
    chunks_count: int = 0
    
    class Config:
        from_attributes = True


class DocumentUploadResponse(BaseModel):
    """DTO for document upload response"""
    status: str
    message: str
    document_id: int
    filename: str
    processing_status: ProcessingStatusDto


class DocumentListResponse(BaseModel):
    """DTO for list of documents response"""
    documents: list[ContextDocumentResponse]
    total: int


class DocumentDeleteResponse(BaseModel):
    """DTO for document deletion response"""
    status: str
    message: str
