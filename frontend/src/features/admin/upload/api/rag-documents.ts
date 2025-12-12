import { fetchWithAuth } from '@/lib/api-client'

const resourcePath = '/rag/documents/'

type RagDocumentApiResponse = {
  id: number
  filename: string
  storage_url: string
  processing_status: string
  created_at: string
  chunks_count: number
}

type RagDocumentUploadApiResponse = {
  status: string
  message: string
  document_id: number
  filename: string
  processing_status: string
}

type DeleteRagDocumentApiResponse = {
  status: string
  message: string
}

export type RagProcessingStatus =
  | 'pending'
  | 'processing'
  | 'completed'
  | 'failed'
  | 'queued'
  | 'unknown'

export type RagDocument = {
  id: number
  filename: string
  storageUrl: string
  processingStatus: RagProcessingStatus
  createdAt: string
  chunksCount: number
}

export type UploadRagDocumentResult = {
  status: string
  message: string
  documentId: number
  filename: string
  processingStatus: RagProcessingStatus
}

export type DeleteRagDocumentResult = {
  status: string
  message: string
}

function resolveCollectionUrl() {
  const baseUrl = import.meta.env.VITE_API_URL
  if (!baseUrl) {
    throw new Error('VITE_API_URL is not defined')
  }
  return `${baseUrl.replace(/\/$/, '')}${resourcePath}`
}

function resolveDetailUrl(documentId: number | string) {
  return `${resolveCollectionUrl()}${documentId}/`
}

function normalizeStatus(status: string | null | undefined): RagProcessingStatus {
  const normalized = (status || '').toLowerCase()
  switch (normalized) {
    case 'pending':
    case 'processing':
    case 'completed':
    case 'failed':
    case 'queued':
      return normalized as RagProcessingStatus
    default:
      return 'unknown'
  }
}

function mapRagDocumentResponse(data: RagDocumentApiResponse): RagDocument {
  return {
    id: data.id,
    filename: data.filename,
    storageUrl: data.storage_url,
    processingStatus: normalizeStatus(data.processing_status),
    createdAt: data.created_at,
    chunksCount: data.chunks_count ?? 0,
  }
}

async function parseError(response: Response, fallbackMessage: string): Promise<never> {
  const contentType = response.headers.get('content-type')
  if (contentType?.includes('application/json')) {
    const data = await response.json()
    const message = typeof data.detail === 'string' ? data.detail : JSON.stringify(data)
    throw new Error(message || fallbackMessage)
  }
  const fallback = await response.text()
  throw new Error(fallback || fallbackMessage)
}

export async function fetchRagDocuments(): Promise<RagDocument[]> {
  const response = await fetchWithAuth(resolveCollectionUrl(), {
    method: 'GET',
    headers: {
      Accept: 'application/json',
    },
  })

  if (!response.ok) {
    return parseError(response, 'No fue posible cargar los documentos RAG.')
  }

  const data: RagDocumentApiResponse[] = await response.json()
  return data.map(mapRagDocumentResponse)
}

export async function fetchRagDocumentById(documentId: number | string): Promise<RagDocument> {
  const response = await fetchWithAuth(resolveDetailUrl(documentId), {
    method: 'GET',
    headers: {
      Accept: 'application/json',
    },
  })

  if (!response.ok) {
    return parseError(response, 'No fue posible obtener el documento RAG solicitado.')
  }

  const data: RagDocumentApiResponse = await response.json()
  return mapRagDocumentResponse(data)
}

export async function uploadRagDocument(file: File): Promise<UploadRagDocumentResult> {
  const formData = new FormData()
  formData.append('file', file)

  const response = await fetchWithAuth(resolveCollectionUrl(), {
    method: 'POST',
    body: formData,
  })

  if (!response.ok) {
    return parseError(response, 'No fue posible cargar el documento. Intenta de nuevo.')
  }

  const data: RagDocumentUploadApiResponse = await response.json()
  return {
    status: data.status,
    message: data.message,
    documentId: data.document_id,
    filename: data.filename,
    processingStatus: normalizeStatus(data.processing_status),
  }
}

export async function deleteRagDocument(documentId: number | string): Promise<DeleteRagDocumentResult> {
  const response = await fetchWithAuth(resolveDetailUrl(documentId), {
    method: 'DELETE',
  })

  if (!response.ok) {
    return parseError(response, 'No fue posible eliminar el documento RAG.')
  }

  const data: DeleteRagDocumentApiResponse = await response.json()
  return {
    status: data.status,
    message: data.message,
  }
}
