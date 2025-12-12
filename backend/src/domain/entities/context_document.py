from datetime import datetime
from typing import Optional
from enum import Enum


class ProcessingStatus(Enum):
    """Processing status enumeration for RAG documents"""
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"


class ContextDocument:
    """Context Document domain entity for RAG system"""
    
    def __init__(
        self,
        id: Optional[int] = None,
        filename: str = "",
        storage_url: str = "",
        processing_status: ProcessingStatus = ProcessingStatus.PENDING,
        created_at: Optional[datetime] = None
    ):
        self.id = id
        self.filename = filename
        self.storage_url = storage_url
        self.processing_status = processing_status
        self.created_at = created_at or datetime.now()
    
    def validate(self) -> bool:
        """Validate context document data"""
        if not self.filename or not self.filename.strip():
            return False
        
        if not self.storage_url or not self.storage_url.strip():
            return False
        
        if not isinstance(self.processing_status, ProcessingStatus):
            return False
        
        return True
    
    def get_file_extension(self) -> str:
        """Get file extension from filename"""
        if '.' in self.filename:
            return self.filename.split('.')[-1].lower()
        return ""
    
    def is_pdf(self) -> bool:
        """Check if document is a PDF"""
        return self.get_file_extension() == 'pdf'
    
    def is_word(self) -> bool:
        """Check if document is a Word document"""
        return self.get_file_extension() in ['doc', 'docx']
    
    def is_supported_format(self) -> bool:
        """Check if document format is supported for RAG processing"""
        return self.is_pdf() or self.is_word()
    
    def mark_as_processing(self) -> None:
        """Mark document as being processed"""
        self.processing_status = ProcessingStatus.PROCESSING
    
    def mark_as_completed(self) -> None:
        """Mark document as successfully processed"""
        self.processing_status = ProcessingStatus.COMPLETED
    
    def mark_as_failed(self) -> None:
        """Mark document as failed processing"""
        self.processing_status = ProcessingStatus.FAILED
