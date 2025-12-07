import { useQuery } from '@tanstack/react-query'
import type { ClientRecord } from '@/data/admin-clients'
import { fetchClients } from '../api/clients'

export const clientsQueryKey = ['clients'] as const

export function useClientsQuery() {
  return useQuery<ClientRecord[]>({
    queryKey: clientsQueryKey,
    queryFn: fetchClients,
    staleTime: 60_000,
  })
}
