import { useMutation, useQueryClient } from '@tanstack/react-query'
import type { ClientRecord } from '@/data/admin-clients'
import { updateClient, type UpdateClientPayload } from '../api/clients'
import { clientsQueryKey } from './use-clients-query'

type UpdateClientArgs = {
  clientId: number
  payload: UpdateClientPayload
}

type UseUpdateClientOptions = {
  onSuccess?: (client: ClientRecord) => void
  onError?: (error: Error) => void
}

export function useUpdateClient(options: UseUpdateClientOptions = {}) {
  const queryClient = useQueryClient()

  return useMutation<ClientRecord, Error, UpdateClientArgs>({
    mutationFn: ({ clientId, payload }) => updateClient(clientId, payload),
    onSuccess: (client) => {
      queryClient.invalidateQueries({ queryKey: clientsQueryKey })
      queryClient.invalidateQueries({ queryKey: [...clientsQueryKey, client.id] })
      options.onSuccess?.(client)
    },
    onError: (error) => {
      options.onError?.(error)
    },
  })
}
