import { useQuery } from '@tanstack/react-query'
import type { ClientRecord } from '@/data/admin-clients'
import { fetchClientById } from '../api/clients'
import { clientsQueryKey } from './use-clients-query'

type UseClientDetailsOptions = {
  enabled?: boolean
}

export function useClientDetails(clientId: number | null, options: UseClientDetailsOptions = {}) {
  return useQuery<ClientRecord>({
    queryKey: [...clientsQueryKey, clientId],
    queryFn: () => {
      if (clientId == null) {
        throw new Error('El identificador del cliente es requerido')
      }
      return fetchClientById(clientId)
    },
    enabled: Boolean(clientId) && (options.enabled ?? true),
  })
}
