import { fetchWithAuth } from '@/lib/api-client'

const clientCreditsResourceRoot = '/clients'
const creditsByClientResourceRoot = '/credits/by_client/'

export type ClientCreditRecord = {
  id: number
  clientId: number
  montoAprobado: number
  plazoMeses: number
  tasaInteres: number
  estado: string
  fechaDesembolso: string | null
  createdAt: string
}

export type CreateClientCreditPayload = {
  monto_aprobado: number
  plazo_meses: number
  tasa_interes: number
  fecha_desembolso?: string
}

export type ClientCreditStatus =
  | 'EN_ESTUDIO'
  | 'APROBADO'
  | 'RECHAZADO'
  | 'DESEMBOLSADO'
  | 'AL_DIA'
  | 'EN_MORA'
  | 'PAGADO'

export type UpdateClientCreditPayload = Partial<{
  monto_aprobado: number
  plazo_meses: number
  tasa_interes: number
  estado: ClientCreditStatus
  fecha_desembolso: string | null
}>

type ClientCreditApiResponse = {
  id: number
  client_id: number
  monto_aprobado: number | string
  plazo_meses: number | string
  tasa_interes: number | string
  estado: string
  fecha_desembolso: string | null
  created_at: string
}

function getApiBaseUrl() {
  const baseUrl = import.meta.env.VITE_API_URL
  if (!baseUrl) {
    throw new Error('VITE_API_URL is not defined')
  }
  return baseUrl.replace(/\/$/, '')
}

function resolveClientCreditsUrl(clientId: number | string) {
  return `${getApiBaseUrl()}${clientCreditsResourceRoot}/${clientId}/credits`
}

function resolveClientCreditDetailUrl(clientId: number | string, creditId: number | string) {
  return `${resolveClientCreditsUrl(clientId)}/${creditId}`
}

function mapClientCredit(response: ClientCreditApiResponse): ClientCreditRecord {
  return {
    id: response.id,
    clientId: response.client_id,
    montoAprobado: Number(response.monto_aprobado),
    plazoMeses: Number(response.plazo_meses),
    tasaInteres: Number(response.tasa_interes),
    estado: response.estado,
    fechaDesembolso: response.fecha_desembolso,
    createdAt: response.created_at,
  }
}

function resolveCreditsByClientUrl(clientId: number | string) {
  return `${getApiBaseUrl()}${creditsByClientResourceRoot}${clientId}`
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

export async function createClientCredit(
  clientId: number,
  payload: CreateClientCreditPayload,
): Promise<ClientCreditRecord> {
  const response = await fetchWithAuth(resolveClientCreditsUrl(clientId), {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      Accept: 'application/json',
    },
    body: JSON.stringify(payload),
  })

  if (!response.ok) {
    return parseError(response, 'No fue posible crear el crédito')
  }

  const data: ClientCreditApiResponse = await response.json()
  return mapClientCredit(data)
}

export async function fetchClientCredits(clientId: number): Promise<ClientCreditRecord[]> {
  const response = await fetchWithAuth(resolveCreditsByClientUrl(clientId), {
    method: 'GET',
    headers: {
      Accept: 'application/json',
    },
  })

  if (!response.ok) {
    return parseError(response, 'No fue posible cargar los créditos del cliente')
  }

  const data: ClientCreditApiResponse[] = await response.json()
  return data.map(mapClientCredit)
}

export async function updateClientCredit(
  clientId: number,
  creditId: number,
  payload: UpdateClientCreditPayload,
): Promise<ClientCreditRecord> {
  const response = await fetchWithAuth(resolveClientCreditDetailUrl(clientId, creditId), {
    method: 'PUT',
    headers: {
      'Content-Type': 'application/json',
      Accept: 'application/json',
    },
    body: JSON.stringify(payload),
  })

  if (!response.ok) {
    return parseError(response, 'No fue posible actualizar el crédito')
  }

  const data: ClientCreditApiResponse = await response.json()
  return mapClientCredit(data)
}
