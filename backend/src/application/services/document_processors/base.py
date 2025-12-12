from abc import ABC, abstractmethod
from typing import List
from dataclasses import dataclass


@dataclass
class ExtractedText:
    """Represents extracted text from a document with metadata"""
    text: str
    page_number: int = 0
    metadata: dict = None
    
    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}


class DocumentProcessor(ABC):
    """
    Abstract base class for document processors.
    
    Each processor handles a specific document format (PDF, Word, etc.)
    and extracts text content for RAG processing.
    """
    
    @abstractmethod
    async def extract_text(self, content: bytes, filename: str) -> List[ExtractedText]:
        """
        Extract text content from a document.
        
        Args:
            content: Raw bytes of the document file
            filename: Original filename (used for metadata)
            
        Returns:
            List of ExtractedText objects, one per page/section
            
        Raises:
            Exception: If text extraction fails
        """
        pass
    
    @abstractmethod
    def supports_format(self, filename: str) -> bool:
        """
        Check if this processor supports the given file format.
        
        Args:
            filename: Filename to check (uses extension)
            
        Returns:
            True if this processor can handle the file format
        """
        pass
    
    def get_extension(self, filename: str) -> str:
        """Get lowercase file extension from filename"""
        if '.' in filename:
            return filename.split('.')[-1].lower()
        return ""
