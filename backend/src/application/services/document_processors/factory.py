from typing import Optional
from .base import DocumentProcessor
from .pdf_processor import PDFProcessor
from .word_processor import WordProcessor


class DocumentProcessorFactory:
    """
    Factory for creating document processors based on file type.
    
    Supports:
    - PDF files (.pdf)
    - Word documents (.docx, .doc)
    """
    
    SUPPORTED_EXTENSIONS = ['pdf', 'docx', 'doc']
    
    def __init__(self):
        self._processors = [
            PDFProcessor(),
            WordProcessor()
        ]
    
    def get_processor(self, filename: str) -> Optional[DocumentProcessor]:
        """
        Get the appropriate processor for a file.
        
        Args:
            filename: Name of the file to process
            
        Returns:
            DocumentProcessor if format is supported, None otherwise
        """
        for processor in self._processors:
            if processor.supports_format(filename):
                return processor
        return None
    
    def is_supported(self, filename: str) -> bool:
        """
        Check if a file format is supported.
        
        Args:
            filename: Name of the file to check
            
        Returns:
            True if the file format is supported
        """
        return self.get_processor(filename) is not None
    
    @classmethod
    def get_supported_extensions(cls) -> list:
        """Get list of supported file extensions"""
        return cls.SUPPORTED_EXTENSIONS.copy()
    
    @classmethod
    def get_supported_extensions_string(cls) -> str:
        """Get comma-separated string of supported extensions"""
        return ", ".join(f".{ext}" for ext in cls.SUPPORTED_EXTENSIONS)
