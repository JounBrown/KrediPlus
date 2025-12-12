import { useMutation, useQueryClient } from '@tanstack/react-query'
import type { ClientRecord } from '@/data/admin-clients'
import { createClient, type CreateClientPayload } from '../api/clients'
import { clientsQueryKey } from './use-clients-query'

type UseCreateClientOptions = {
  onSuccess?: (client: ClientRecord) => void
  onError?: (error: Error) => void
}

export function useCreateClient(options: UseCreateClientOptions = {}) {
  const queryClient = useQueryClient()

  return useMutation<ClientRecord, Error, CreateClientPayload>({
    mutationFn: (payload) => createClient(payload),
    onSuccess: (client) => {
      queryClient.invalidateQueries({ queryKey: clientsQueryKey })
      options.onSuccess?.(client)
    },
    onError: (error) => {
      options.onError?.(error)
    },
  })
}
