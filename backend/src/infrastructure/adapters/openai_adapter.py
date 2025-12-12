from typing import List
from openai import AsyncOpenAI
from src.domain.ports.embedding_port import EmbeddingPort
from src.domain.ports.llm_port import LLMPort
from src.config import OPENAI_API_KEY


class OpenAIAdapter(EmbeddingPort, LLMPort):
    """
    OpenAI adapter implementing EmbeddingPort and LLMPort.
    
    This adapter can be replaced with another implementation
    (e.g., CohereAdapter, AnthropicAdapter) without changing business logic.
    """
    
    def __init__(self):
        if not OPENAI_API_KEY:
            raise ValueError("OPENAI_API_KEY environment variable is not set")
        self.client = AsyncOpenAI(api_key=OPENAI_API_KEY)
        self.embedding_model = "text-embedding-3-small"
        self.chat_model = "gpt-4o-mini"
    
    # EmbeddingPort implementation
    async def generate_embedding(self, text: str) -> List[float]:
        """Generate embedding for a single text using OpenAI."""
        try:
            response = await self.client.embeddings.create(
                model=self.embedding_model,
                input=text
            )
            return response.data[0].embedding
        except Exception as e:
            raise Exception(f"Error generating embedding: {str(e)}")
    
    async def generate_embeddings_batch(self, texts: List[str]) -> List[List[float]]:
        """Generate embeddings for multiple texts in batch."""
        try:
            response = await self.client.embeddings.create(
                model=self.embedding_model,
                input=texts
            )
            return [item.embedding for item in response.data]
        except Exception as e:
            raise Exception(f"Error generating batch embeddings: {str(e)}")
    
    # LLMPort implementation
    async def generate_response(self, query: str, context: str) -> str:
        """Generate a response using GPT with RAG context."""
        system_prompt = """Eres un asistente virtual de KrediPlus, una plataforma financiera digital innovadora dedicada a democratizar el acceso al crédito para pequeñas y medianas empresas (PYMEs) y emprendedores.

Tu objetivo es responder preguntas de los usuarios basándote en el contexto proporcionado.

Reglas:
- Responde en español de manera clara, amigable y profesional
- Usa el contexto proporcionado para dar respuestas precisas
- Si la pregunta es muy general (como "hola", "qué sabes", etc.), presenta brevemente a KrediPlus y ofrece ayuda
- Si no encuentras información específica en el contexto, puedes dar información general sobre KrediPlus
- Sé conciso pero completo en tus respuestas
- Si el usuario pregunta algo completamente fuera del alcance de KrediPlus, redirige amablemente

Información básica de KrediPlus que siempre puedes mencionar:
- KrediPlus es una plataforma de crédito digital para PYMEs y emprendedores
- Ofrece acceso rápido y equitativo a crédito
- Simplifica procesos de solicitud y aprobación de créditos"""

        return await self.generate_response_with_system_prompt(query, context, system_prompt)
    
    async def generate_response_with_system_prompt(
        self, 
        query: str, 
        context: str, 
        system_prompt: str
    ) -> str:
        """Generate a response with a custom system prompt."""
        try:
            messages = [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": f"""Contexto de documentos:
{context}

Pregunta del usuario: {query}

Responde basándote en el contexto proporcionado."""}
            ]
            
            response = await self.client.chat.completions.create(
                model=self.chat_model,
                messages=messages,
                temperature=0.7,
                max_tokens=1000
            )
            
            return response.choices[0].message.content or ""
        except Exception as e:
            raise Exception(f"Error generating response: {str(e)}")
