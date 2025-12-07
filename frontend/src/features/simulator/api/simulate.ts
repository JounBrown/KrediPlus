const resourcePath = '/simulator/simulate'

export type SimulateCreditParams = {
  amount: number
  termMonths: number
}

export type CreditSimulationResult = {
  amountRequested: number
  termMonths: number
  monthlyRate: number
  monthlyPayment: number
  totalToPay: number
  totalInterests: number
}

type CreditSimulationResponse = {
  monto_solicitado: number
  plazo_meses: number
  tasa_interes_mensual: number
  cuota_mensual: number
  total_a_pagar: number
  total_intereses: number
}

function resolveResourceUrl() {
  const baseUrl = import.meta.env.VITE_API_URL
  if (!baseUrl) {
    throw new Error('VITE_API_URL is not defined')
  }
  return `${baseUrl.replace(/\/$/, '')}${resourcePath}`
}

function mapSimulationResponse(response: CreditSimulationResponse): CreditSimulationResult {
  return {
    amountRequested: response.monto_solicitado,
    termMonths: response.plazo_meses,
    monthlyRate: response.tasa_interes_mensual,
    monthlyPayment: response.cuota_mensual,
    totalToPay: response.total_a_pagar,
    totalInterests: response.total_intereses,
  }
}

async function parseError(response: Response): Promise<never> {
  const contentType = response.headers.get('content-type')
  if (contentType?.includes('application/json')) {
    const data = await response.json()
    const message = typeof data.detail === 'string' ? data.detail : JSON.stringify(data)
    throw new Error(message || 'No fue posible simular el crédito')
  }
  const fallback = await response.text()
  throw new Error(fallback || 'No fue posible simular el crédito')
}

export async function simulateCredit(params: SimulateCreditParams): Promise<CreditSimulationResult> {
  const url = new URL(resolveResourceUrl())
  url.searchParams.set('monto', params.amount.toString())
  url.searchParams.set('plazo_meses', params.termMonths.toString())

  const response = await fetch(url.toString(), {
    method: 'GET',
    headers: {
      Accept: 'application/json',
    },
  })

  if (!response.ok) {
    return parseError(response)
  }

  const data: CreditSimulationResponse = await response.json()
  return mapSimulationResponse(data)
}
