import { useQuery } from '@tanstack/react-query'
import { fetchClientCredits, type ClientCreditRecord } from '../api/credits'

export const clientCreditsQueryKey = ['client-credits'] as const

type UseClientCreditsOptions = {
  enabled?: boolean
}

export function useClientCredits(clientId: number | null, options: UseClientCreditsOptions = {}) {
  return useQuery<ClientCreditRecord[]>({
    queryKey: [...clientCreditsQueryKey, clientId],
    queryFn: () => {
      if (clientId == null) {
        throw new Error('El identificador del cliente es requerido')
      }
      return fetchClientCredits(clientId)
    },
    enabled: Boolean(clientId) && (options.enabled ?? true),
  })
}
