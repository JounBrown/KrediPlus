from typing import List, Optional
from dataclasses import dataclass
import time

from src.domain.ports.chunk_repository import ChunkRepositoryPort
from src.domain.ports.embedding_port import EmbeddingPort
from src.domain.ports.llm_port import LLMPort


@dataclass
class ChunkReference:
    """Reference to a source chunk used in response generation"""
    chunk_id: int
    document_id: int
    content_preview: str
    similarity: float
    metadata: dict


@dataclass
class ChatResponse:
    """Response from the chat service"""
    response: str
    sources: List[ChunkReference]
    processing_time: float
    query: str


class ChatService:
    """
    Service for processing chat queries using RAG.
    
    Flow:
    1. Generate embedding for user query
    2. Search for similar chunks in vector database
    3. Build context from retrieved chunks
    4. Generate response using LLM with context
    5. Return response with source references
    """
    
    def __init__(
        self,
        chunk_repository: ChunkRepositoryPort,
        embedding_port: EmbeddingPort,
        llm_port: LLMPort,
        match_threshold: float = 0.0,  # Always return top matches, let LLM decide relevance
        max_chunks: int = 5
    ):
        self._chunk_repository = chunk_repository
        self._embedding_port = embedding_port
        self._llm_port = llm_port
        self._match_threshold = match_threshold
        self._max_chunks = max_chunks
    
    async def process_query(self, query: str) -> ChatResponse:
        """
        Process a user query and generate a response.
        
        Args:
            query: User's question
            
        Returns:
            ChatResponse with answer and source references
        """
        start_time = time.time()
        
        if not query or not query.strip():
            return ChatResponse(
                response="Por favor, escribe una pregunta.",
                sources=[],
                processing_time=0,
                query=query
            )
        
        query = query.strip()
        
        # Generate embedding for query
        try:
            query_embedding = await self._embedding_port.generate_embedding(query)
        except Exception as e:
            return ChatResponse(
                response="Lo siento, hubo un error procesando tu pregunta. Por favor intenta de nuevo.",
                sources=[],
                processing_time=time.time() - start_time,
                query=query
            )
        
        # Search for similar chunks
        try:
            similar_chunks = await self._chunk_repository.search_similar(
                query_embedding=query_embedding,
                match_threshold=self._match_threshold,
                match_count=self._max_chunks
            )
        except Exception as e:
            print(f"[RAG] Error searching chunks: {str(e)}", flush=True)
            return ChatResponse(
                response="Lo siento, hubo un error buscando información. Por favor intenta de nuevo.",
                sources=[],
                processing_time=time.time() - start_time,
                query=query
            )
        
        # If no relevant chunks found
        if not similar_chunks:
            return ChatResponse(
                response="No encontré información relevante en los documentos disponibles para responder tu pregunta. ¿Podrías reformularla o preguntar sobre otro tema?",
                sources=[],
                processing_time=time.time() - start_time,
                query=query
            )
        
        # Build context from chunks
        context = self._build_context(similar_chunks)
        
        # Generate response using LLM
        try:
            response_text = await self._llm_port.generate_response(query, context)
        except Exception as e:
            return ChatResponse(
                response="Lo siento, hubo un error generando la respuesta. Por favor intenta de nuevo.",
                sources=[],
                processing_time=time.time() - start_time,
                query=query
            )
        
        # Build source references
        sources = self._build_sources(similar_chunks)
        
        processing_time = time.time() - start_time
        
        return ChatResponse(
            response=response_text,
            sources=sources,
            processing_time=processing_time,
            query=query
        )
    
    def _build_context(self, chunks: List[dict]) -> str:
        """Build context string from retrieved chunks"""
        context_parts = []
        
        for i, chunk in enumerate(chunks, start=1):
            content = chunk.get("content", "")
            metadata = chunk.get("metadata", {})
            source_file = metadata.get("source_file", "Documento")
            
            context_parts.append(f"[Fuente {i}: {source_file}]\n{content}")
        
        return "\n\n---\n\n".join(context_parts)
    
    def _build_sources(self, chunks: List[dict]) -> List[ChunkReference]:
        """Build source references from chunks"""
        sources = []
        
        for chunk in chunks:
            content = chunk.get("content", "")
            preview = content[:200] + "..." if len(content) > 200 else content
            
            sources.append(ChunkReference(
                chunk_id=chunk.get("id", 0),
                document_id=chunk.get("document_id", 0),
                content_preview=preview,
                similarity=chunk.get("similarity", 0),
                metadata=chunk.get("metadata", {})
            ))
        
        return sources
