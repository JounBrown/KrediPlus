import { fetchWithAuth } from '@/lib/api-client'

const uploadResourcePath = '/documents/upload'
const clientDocumentsResourcePath = '/documents/client/'

const clientDocumentDeleteRoot = '/clients'

export type DocumentType =
  | 'CEDULA_FRENTE'
  | 'CEDULA_REVERSO'
  | 'COMPROBANTE_INGRESOS'
  | 'CERTIFICADO_LABORAL'
  | 'SOLICITUD_CREDITO_FIRMADA'
  | 'PAGARE_FIRMADO'
  | 'COMPROBANTE_DOMICILIO'
  | 'EXTRACTO_BANCARIO'
  | 'OTRO'

export type UploadClientDocumentPayload = {
  file: File
  documentType: DocumentType
  clientId: number
  creditId?: number
}

export type UploadClientDocumentResponse = {
  status: string
  message: string
  path: string
  document_id: number
  file_url: string
}

export type ClientDocumentRecord = {
  id: number
  fileName: string
  storagePath: string
  documentType: DocumentType
  clientId: number
  creditId: number | null
  createdAt: string
  fileUrl: string
}

export type DeleteClientDocumentResponse = {
  status: string
  message: string
}

type ClientDocumentApiResponse = {
  id: number
  file_name: string
  storage_path: string
  document_type: DocumentType
  client_id: number
  credit_id: number | null
  created_at: string
  file_url: string
}

function getApiBaseUrl() {
  const baseUrl = import.meta.env.VITE_API_URL
  if (!baseUrl) {
    throw new Error('VITE_API_URL is not defined')
  }
  return baseUrl.replace(/\/$/, '')
}

function getUploadUrl() {
  return `${getApiBaseUrl()}${uploadResourcePath}`
}

function getClientDocumentsUrl(clientId: number | string) {
  return `${getApiBaseUrl()}${clientDocumentsResourcePath}${clientId}`
}

function getDeleteClientDocumentUrl(clientId: number | string, documentId: number | string) {
  return `${getApiBaseUrl()}${clientDocumentDeleteRoot}/${clientId}/documents/${documentId}`
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

function mapClientDocument(apiResponse: ClientDocumentApiResponse): ClientDocumentRecord {
  return {
    id: apiResponse.id,
    fileName: apiResponse.file_name,
    storagePath: apiResponse.storage_path,
    documentType: apiResponse.document_type,
    clientId: apiResponse.client_id,
    creditId: apiResponse.credit_id,
    createdAt: apiResponse.created_at,
    fileUrl: apiResponse.file_url,
  }
}

export async function uploadClientDocument(
  payload: UploadClientDocumentPayload,
): Promise<UploadClientDocumentResponse> {
  const { file, documentType, clientId, creditId } = payload
  const formData = new FormData()
  formData.append('file', file)
  formData.append('document_type', documentType)
  formData.append('client_id', String(clientId))
  if (typeof creditId === 'number') {
    formData.append('credit_id', String(creditId))
  }

  const response = await fetchWithAuth(getUploadUrl(), {
    method: 'POST',
    body: formData,
  })

  if (!response.ok) {
    return parseError(response, 'No fue posible subir el documento')
  }

  return response.json()
}

export async function fetchClientDocuments(clientId: number): Promise<ClientDocumentRecord[]> {
  const response = await fetchWithAuth(getClientDocumentsUrl(clientId), {
    method: 'GET',
    headers: {
      Accept: 'application/json',
    },
  })

  if (!response.ok) {
    return parseError(response, 'No fue posible cargar los documentos del cliente')
  }

  const data: ClientDocumentApiResponse[] = await response.json()
  return data.map(mapClientDocument)
}

export async function deleteClientDocument(
  clientId: number,
  documentId: number,
): Promise<DeleteClientDocumentResponse> {
  const response = await fetchWithAuth(getDeleteClientDocumentUrl(clientId, documentId), {
    method: 'DELETE',
    headers: {
      Accept: 'application/json',
    },
  })

  if (!response.ok) {
    return parseError(response, 'No fue posible eliminar el documento')
  }

  return response.json()
}
