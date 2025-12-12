from typing import List, Dict, Any


class TextChunkingService:
    """
    Service for splitting text into chunks for RAG processing.
    
    Uses a simple character-based chunking strategy with overlap
    to maintain context between chunks.
    """
    
    def __init__(
        self,
        chunk_size: int = 1000,
        chunk_overlap: int = 200
    ):
        """
        Initialize the chunking service.
        
        Args:
            chunk_size: Target size of each chunk in characters
            chunk_overlap: Number of characters to overlap between chunks
        """
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
    
    def chunk_text(
        self, 
        text: str, 
        base_metadata: Dict[str, Any] = None
    ) -> List[Dict[str, Any]]:
        """
        Split text into chunks with metadata.
        
        Args:
            text: Full text to chunk
            base_metadata: Base metadata to include in each chunk
            
        Returns:
            List of dicts with 'text' and 'metadata' keys
        """
        if not text or not text.strip():
            return []
        
        base_metadata = base_metadata or {}
        
        # Clean text
        text = text.strip()
        
        # If text is smaller than chunk size, return as single chunk
        if len(text) <= self.chunk_size:
            return [{
                "text": text,
                "metadata": {
                    **base_metadata,
                    "chunk_index": 0,
                    "total_chunks": 1,
                    "char_start": 0,
                    "char_end": len(text)
                }
            }]
        
        chunks = []
        start = 0
        chunk_index = 0
        
        while start < len(text):
            # Calculate end position
            end = start + self.chunk_size
            
            # If not at the end, try to break at a sentence or paragraph
            if end < len(text):
                # Look for paragraph break first
                paragraph_break = text.rfind('\n\n', start, end)
                if paragraph_break > start + self.chunk_size // 2:
                    end = paragraph_break + 2
                else:
                    # Look for sentence break
                    sentence_break = self._find_sentence_break(text, start, end)
                    if sentence_break > start + self.chunk_size // 2:
                        end = sentence_break
            else:
                end = len(text)
            
            # Extract chunk
            chunk_text = text[start:end].strip()
            
            if chunk_text:
                chunks.append({
                    "text": chunk_text,
                    "metadata": {
                        **base_metadata,
                        "chunk_index": chunk_index,
                        "char_start": start,
                        "char_end": end
                    }
                })
                chunk_index += 1
            
            # Move start position with overlap
            new_start = end - self.chunk_overlap
            # Ensure we always make progress to avoid infinite loop
            if new_start <= start:
                new_start = end
            start = new_start
            
            if start >= len(text):
                break
        
        # Update total_chunks in all metadata
        total_chunks = len(chunks)
        for chunk in chunks:
            chunk["metadata"]["total_chunks"] = total_chunks
        
        return chunks
    
    def _find_sentence_break(self, text: str, start: int, end: int) -> int:
        """Find the best sentence break point in the given range"""
        # Look for sentence endings
        for punct in ['. ', '! ', '? ', '.\n', '!\n', '?\n']:
            pos = text.rfind(punct, start, end)
            if pos > start + self.chunk_size // 2:
                return pos + len(punct)
        
        # Fall back to any whitespace
        space_pos = text.rfind(' ', start, end)
        if space_pos > start + self.chunk_size // 2:
            return space_pos + 1
        
        return end
