from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from src.application.services.chat_service import ChatService
from src.application.dtos.chat_dtos import ChatRequest, ChatResponse, ChunkReferenceDto
from src.infrastructure.adapters.database.connection import get_db_session
from src.infrastructure.adapters.database.chunk_repository import SupabaseChunkRepository
from src.infrastructure.adapters.openai_adapter import OpenAIAdapter

# PUBLIC router - NO authentication required
router = APIRouter(
    prefix="/chat",
    tags=["Chat"]
    # Note: No dependencies=[Depends(get_current_user)] - this is intentionally public
)


def get_chat_service(db: AsyncSession = Depends(get_db_session)) -> ChatService:
    """Dependency to get ChatService"""
    chunk_repository = SupabaseChunkRepository(db)
    openai_adapter = OpenAIAdapter()
    return ChatService(
        chunk_repository=chunk_repository,
        embedding_port=openai_adapter,
        llm_port=openai_adapter
    )


@router.post("/", response_model=ChatResponse)
async def chat(
    request: ChatRequest,
    service: ChatService = Depends(get_chat_service)
):
    """
    Send a question to the KrediPlus chatbot.
    
    This endpoint is PUBLIC and does not require authentication.
    
    The chatbot will:
    1. Search for relevant information in uploaded documents
    2. Generate a contextual response based on found information
    3. Return the response with source references
    
    If no relevant information is found, the chatbot will indicate this.
    """
    try:
        # Convert history to list of dicts
        history = [{"role": msg.role, "content": msg.content} for msg in (request.history or [])]
        
        result = await service.process_query(request.question, history)
        
        return ChatResponse(
            response=result.response,
            sources=[
                ChunkReferenceDto(
                    chunk_id=src.chunk_id,
                    document_id=src.document_id,
                    content_preview=src.content_preview,
                    similarity=src.similarity,
                    metadata=src.metadata
                )
                for src in result.sources
            ],
            processing_time=result.processing_time,
            query=result.query
        )
    except Exception as e:
        raise HTTPException(
            status_code=500, 
            detail=f"Error processing chat request: {str(e)}"
        )


@router.get("/health")
async def chat_health():
    """
    Health check for the chat service.
    
    Returns basic status information.
    """
    return {
        "status": "healthy",
        "service": "KrediPlus Chat",
        "version": "1.0.0"
    }
