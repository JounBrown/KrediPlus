import type { LoanApplication } from '@/features/submit-form/types/loan-application'
import { fetchWithAuth } from '@/lib/api-client'

const resourcePath = '/loan_applications/'

function resolveResourceUrl() {
  const baseUrl = import.meta.env.VITE_API_URL
  if (!baseUrl) {
    throw new Error('VITE_API_URL is not defined')
  }
  const normalizedBase = baseUrl.replace(/\/$/, '')
  return `${normalizedBase}${resourcePath}`
}

async function parseError(response: Response): Promise<never> {
  const contentType = response.headers.get('content-type')
  if (contentType?.includes('application/json')) {
    const data = await response.json()
    const message = typeof data.detail === 'string' ? data.detail : JSON.stringify(data)
    throw new Error(message || 'Error al procesar la solicitud de crédito')
  }
  const fallback = await response.text()
  throw new Error(fallback || 'Error al procesar la solicitud de crédito')
}

export type CreateLoanApplicationPayload = Pick<
  LoanApplication,
  'name' | 'cedula' | 'convenio' | 'telefono' | 'fecha_nacimiento' | 'monto_solicitado' | 'plazo'
>

export async function fetchLoanApplications(): Promise<LoanApplication[]> {
  const response = await fetchWithAuth(resolveResourceUrl(), {
    method: 'GET',
    headers: {
      Accept: 'application/json',
    },
  })

  if (!response.ok) {
    return parseError(response)
  }

  return response.json()
}

export async function createLoanApplication(
  payload: CreateLoanApplicationPayload,
): Promise<LoanApplication> {
  const response = await fetch(resolveResourceUrl(), {
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

  return response.json()
}
