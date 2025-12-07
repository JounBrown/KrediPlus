import type { SimulatorConfig } from '@/data/simulator-config'

const resourcePath = '/simulator/config'

type SimulatorConfigResponse = {
  id: number
  tasa_interes_mensual: number
  monto_minimo: number
  monto_maximo: number
  plazos_disponibles: number[]
  is_active: boolean
  created_at?: string | null
}
export type CreateSimulatorConfigPayload = {
  tasa_interes_mensual: number
  monto_minimo: number
  monto_maximo: number
  plazos_disponibles: number[]
}

function resolveResourceUrl() {
  const baseUrl = import.meta.env.VITE_API_URL
  if (!baseUrl) {
    throw new Error('VITE_API_URL is not defined')
  }
  return `${baseUrl.replace(/\/$/, '')}${resourcePath}`
}

function mapSimulatorConfig(apiConfig: SimulatorConfigResponse): SimulatorConfig {
  return {
    id: apiConfig.id,
    tasaInteresMensual: apiConfig.tasa_interes_mensual,
    montoMinimo: apiConfig.monto_minimo,
    montoMaximo: apiConfig.monto_maximo,
    plazosDisponibles: apiConfig.plazos_disponibles,
    isActive: apiConfig.is_active,
    createdAt: apiConfig.created_at ?? undefined,
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

export async function fetchSimulatorConfigs(): Promise<SimulatorConfig[]> {
  const response = await fetch(resolveResourceUrl(), {
    method: 'GET',
    headers: {
      Accept: 'application/json',
    },
  })

  if (!response.ok) {
    return parseError(response, 'No fue posible cargar las configuraciones del simulador')
  }

  const data: SimulatorConfigResponse[] = await response.json()
  return data.map(mapSimulatorConfig)
}

export async function createSimulatorConfig(
  payload: CreateSimulatorConfigPayload,
): Promise<SimulatorConfig> {
  const response = await fetch(resolveResourceUrl(), {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      Accept: 'application/json',
    },
    body: JSON.stringify(payload),
  })

  if (!response.ok) {
    return parseError(response, 'No fue posible guardar la configuración del simulador')
  }

  const data: SimulatorConfigResponse = await response.json()
  return mapSimulatorConfig(data)
}

export async function activateSimulatorConfig(configId: number): Promise<SimulatorConfig> {
  const response = await fetch(`${resolveResourceUrl()}/${configId}/activate`, {
    method: 'POST',
    headers: {
      Accept: 'application/json',
    },
  })

  if (!response.ok) {
    return parseError(response, 'No fue posible activar la configuración del simulador')
  }

  const data: SimulatorConfigResponse = await response.json()
  return mapSimulatorConfig(data)
}
