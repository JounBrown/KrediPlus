import type { SimulatorConfig } from '@/data/simulator-config'

const resourcePath = '/simulator/config'

type SimulatorConfigResponse = {
  id: number
  tasa_interes_mensual: number
  monto_minimo: number
  monto_maximo: number
  plazos_disponibles: number[]
  is_active: boolean
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
  }
}

async function parseError(response: Response): Promise<never> {
  const contentType = response.headers.get('content-type')
  if (contentType?.includes('application/json')) {
    const data = await response.json()
    const message = typeof data.detail === 'string' ? data.detail : JSON.stringify(data)
    throw new Error(message || 'No fue posible cargar las configuraciones del simulador')
  }
  const fallback = await response.text()
  throw new Error(fallback || 'No fue posible cargar las configuraciones del simulador')
}

export async function fetchSimulatorConfigs(): Promise<SimulatorConfig[]> {
  const response = await fetch(resolveResourceUrl(), {
    method: 'GET',
    headers: {
      Accept: 'application/json',
    },
  })

  if (!response.ok) {
    return parseError(response)
  }

  const data: SimulatorConfigResponse[] = await response.json()
  return data.map(mapSimulatorConfig)
}
