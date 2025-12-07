import { useMutation, useQueryClient } from '@tanstack/react-query'
import { deleteClient } from '../api/clients'
import { clientsQueryKey } from './use-clients-query'

type UseDeleteClientOptions = {
  onSuccess?: () => void
  onError?: (error: Error) => void
}

export function useDeleteClient(options: UseDeleteClientOptions = {}) {
  const queryClient = useQueryClient()

  return useMutation<void, Error, number>({
    mutationFn: (clientId) => deleteClient(clientId),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: clientsQueryKey })
      options.onSuccess?.()
    },
    onError: (error) => {
      options.onError?.(error)
    },
  })
}
