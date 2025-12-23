from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any, Literal


class Message(BaseModel):
    """Represents a single message in conversation history"""
    role: Literal["user", "assistant"]
    content: str


class ChatRequest(BaseModel):
    """DTO for chat request from frontend"""
    question: str = Field(..., min_length=1, max_length=2000)
    history: Optional[List[Message]] = []


class ChunkReferenceDto(BaseModel):
    """DTO for chunk reference in chat response"""
    chunk_id: int
    document_id: int
    content_preview: str
    similarity: float
    metadata: Dict[str, Any] = {}


class ChatResponse(BaseModel):
    """DTO for chat response"""
    response: str = Field(..., description="Generated response from the chatbot")
    sources: List[ChunkReferenceDto] = Field(default=[], description="Source references used")
    processing_time: float = Field(..., description="Time taken to process in seconds")
    query: str = Field(..., description="Original query")
    
    class Config:
        from_attributes = True
