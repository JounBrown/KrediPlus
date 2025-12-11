import type { ClientRecord } from '@/data/admin-clients'
import { fetchWithAuth } from '@/lib/api-client'

const resourcePath = '/clients/'

type ClientApiResponse = {
  id: number
  nombre_completo: string
  cedula: string
  email: string
  telefono: string
  fecha_nacimiento: string
  direccion: string
  info_adicional?: Record<string, unknown> | null
  created_at: string
}

function getBaseResourceUrl() {
  const baseUrl = import.meta.env.VITE_API_URL
  if (!baseUrl) {
    throw new Error('VITE_API_URL is not defined')
  }
  return `${baseUrl.replace(/\/$/, '')}${resourcePath}`
}

function resolveCollectionUrl() {
  return getBaseResourceUrl()
}

function resolveDetailUrl(clientId: number | string) {
  return `${getBaseResourceUrl()}${clientId}/`
}

function mapClientResponse(apiClient: ClientApiResponse): ClientRecord {
  return {
    id: apiClient.id,
    createdAt: apiClient.created_at,
    nombreCompleto: apiClient.nombre_completo,
    cedula: apiClient.cedula,
    email: apiClient.email,
    telefono: apiClient.telefono,
    fechaNacimiento: apiClient.fecha_nacimiento,
    direccion: apiClient.direccion,
    infoAdicional: apiClient.info_adicional ? JSON.stringify(apiClient.info_adicional) : '',
  }
}

async function parseError(response: Response): Promise<never> {
  const contentType = response.headers.get('content-type')
  if (contentType?.includes('application/json')) {
    const data = await response.json()
    const message = typeof data.detail === 'string' ? data.detail : JSON.stringify(data)
    throw new Error(message || 'No fue posible cargar los clientes')
  }
  const fallback = await response.text()
  throw new Error(fallback || 'No fue posible cargar los clientes')
}

export async function fetchClients(): Promise<ClientRecord[]> {
  const response = await fetchWithAuth(resolveCollectionUrl(), {
    method: 'GET',
    headers: {
      Accept: 'application/json',
    },
  })

  if (!response.ok) {
    return parseError(response)
  }

  const data: ClientApiResponse[] = await response.json()
  return data.map(mapClientResponse)
}

export type CreateClientPayload = {
  nombre_completo: string
  cedula: string
  email: string
  telefono: string
  fecha_nacimiento: string
  direccion: string
  info_adicional?: Record<string, unknown>
}

export async function createClient(payload: CreateClientPayload): Promise<ClientRecord> {
  const response = await fetchWithAuth(resolveCollectionUrl(), {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      Accept: 'application/json',
    },
    body: JSON.stringify(payload),
  })

  if (!response.ok) {
    return parseError(response)
  }

  const data: ClientApiResponse = await response.json()
  return mapClientResponse(data)
}

export async function fetchClientById(clientId: number): Promise<ClientRecord> {
  const response = await fetchWithAuth(resolveDetailUrl(clientId), {
    method: 'GET',
    headers: {
      Accept: 'application/json',
    },
  })

  if (!response.ok) {
    return parseError(response)
  }

  const data: ClientApiResponse = await response.json()
  return mapClientResponse(data)
}

export type UpdateClientPayload = {
  nombre_completo: string
  email: string
  telefono: string
  direccion: string
  info_adicional?: Record<string, unknown>
}

export async function updateClient(
  clientId: number,
  payload: UpdateClientPayload,
): Promise<ClientRecord> {
  const response = await fetchWithAuth(resolveDetailUrl(clientId), {
    method: 'PUT',
    headers: {
      'Content-Type': 'application/json',
      Accept: 'application/json',
    },
    body: JSON.stringify(payload),
  })

  if (!response.ok) {
    return parseError(response)
  }

  const data: ClientApiResponse = await response.json()
  return mapClientResponse(data)
}

export async function deleteClient(clientId: number): Promise<void> {
  const response = await fetchWithAuth(resolveDetailUrl(clientId), {
    method: 'DELETE',
  })

  if (!response.ok) {
    return parseError(response)
  }
}
