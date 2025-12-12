import type {
  ChatbotResponse,
  ChatRequestPayload,
  ChatSource,
  ChatSourceMetadata,
} from '../types/chat'

const resourcePath = '/chat/'

type ChatSourceApiResponse = {
  chunk_id: number
  document_id: number
  content_preview: string
  similarity: number
  metadata: {
    source_file: string
    file_type: string
    page?: number | null
    total_pages?: number | null
    chunk_index?: number | null
    total_chunks?: number | null
    char_start?: number | null
    char_end?: number | null
  }
}

type ChatApiResponse = {
  response: string
  sources: ChatSourceApiResponse[]
  processing_time?: number
  query: string
}

function resolveChatUrl() {
  const baseUrl = import.meta.env.VITE_API_URL
  if (!baseUrl) {
    throw new Error('VITE_API_URL is not defined')
  }
  return `${baseUrl.replace(/\/$/, '')}${resourcePath}`
}

function mapSourceMetadata(metadata: ChatSourceApiResponse['metadata']): ChatSourceMetadata {
  return {
    sourceFile: metadata.source_file,
    fileType: metadata.file_type,
    page: metadata.page ?? null,
    totalPages: metadata.total_pages ?? null,
    chunkIndex: metadata.chunk_index ?? null,
    totalChunks: metadata.total_chunks ?? null,
    charStart: metadata.char_start ?? null,
    charEnd: metadata.char_end ?? null,
  }
}

function mapSource(source: ChatSourceApiResponse): ChatSource {
  return {
    chunkId: source.chunk_id,
    documentId: source.document_id,
    contentPreview: source.content_preview,
    similarity: source.similarity,
    metadata: mapSourceMetadata(source.metadata),
  }
}

function mapChatResponse(data: ChatApiResponse): ChatbotResponse {
  return {
    response: data.response,
    sources: Array.isArray(data.sources) ? data.sources.map(mapSource) : [],
    processingTime: data.processing_time,
    query: data.query,
  }
}

async function parseChatError(response: Response): Promise<never> {
  const fallbackMessage = 'No fue posible obtener una respuesta del chatbot.'
  const contentType = response.headers.get('content-type')
  if (contentType?.includes('application/json')) {
    const data = await response.json().catch(() => null)
    const detail = data && typeof data.detail === 'string' ? data.detail : null
    throw new Error(detail || fallbackMessage)
  }
  const text = await response.text()
  throw new Error(text || fallbackMessage)
}

export async function sendChatMessage(query: string): Promise<ChatbotResponse> {
  const payload: ChatRequestPayload = { query }
  const response = await fetch(resolveChatUrl(), {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      Accept: 'application/json',
    },
    body: JSON.stringify(payload),
  })

  if (!response.ok) {
    return parseChatError(response)
  }

  const data: ChatApiResponse = await response.json()
  return mapChatResponse(data)
}
