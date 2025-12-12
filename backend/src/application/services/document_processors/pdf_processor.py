from typing import List
from io import BytesIO
from pypdf import PdfReader

from .base import DocumentProcessor, ExtractedText


class PDFProcessor(DocumentProcessor):
    """Processor for PDF documents using PyPDF"""
    
    SUPPORTED_EXTENSIONS = ['pdf']
    
    async def extract_text(self, content: bytes, filename: str) -> List[ExtractedText]:
        """
        Extract text from a PDF document.
        
        Args:
            content: Raw bytes of the PDF file
            filename: Original filename
            
        Returns:
            List of ExtractedText objects, one per page
        """
        try:
            pdf_file = BytesIO(content)
            reader = PdfReader(pdf_file)
            
            extracted_texts = []
            
            for page_num, page in enumerate(reader.pages, start=1):
                text = page.extract_text() or ""
                
                # Skip empty pages
                if not text.strip():
                    continue
                
                extracted_texts.append(ExtractedText(
                    text=text.strip(),
                    page_number=page_num,
                    metadata={
                        "source_file": filename,
                        "file_type": "pdf",
                        "page": page_num,
                        "total_pages": len(reader.pages)
                    }
                ))
            
            return extracted_texts
            
        except Exception as e:
            raise Exception(f"Error extracting text from PDF: {str(e)}")
    
    def supports_format(self, filename: str) -> bool:
        """Check if this processor supports PDF files"""
        return self.get_extension(filename) in self.SUPPORTED_EXTENSIONS
