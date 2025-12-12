import { useMutation, useQueryClient } from '@tanstack/react-query'
import {
  updateClientCredit,
  type ClientCreditRecord,
  type UpdateClientCreditPayload,
} from '../api/credits'
import { clientCreditsQueryKey } from './use-client-credits'

type UpdateClientCreditArgs = {
  clientId: number
  creditId: number
  payload: UpdateClientCreditPayload
}

type UseUpdateClientCreditOptions = {
  onSuccess?: (credit: ClientCreditRecord) => void
  onError?: (error: Error) => void
}

export function useUpdateClientCredit(options: UseUpdateClientCreditOptions = {}) {
  const queryClient = useQueryClient()

  return useMutation<ClientCreditRecord, Error, UpdateClientCreditArgs>({
    mutationFn: ({ clientId, creditId, payload }) => updateClientCredit(clientId, creditId, payload),
    onSuccess: (credit, variables) => {
      queryClient.invalidateQueries({ queryKey: [...clientCreditsQueryKey, variables.clientId] })
      options.onSuccess?.(credit)
    },
    onError: (error) => {
      options.onError?.(error)
    },
  })
}
