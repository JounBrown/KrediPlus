import { useMutation, useQueryClient } from '@tanstack/react-query'
import {
  createClientCredit,
  type ClientCreditRecord,
  type CreateClientCreditPayload,
} from '../api/credits'
import { clientCreditsQueryKey } from './use-client-credits'

type CreateClientCreditArgs = {
  clientId: number
  payload: CreateClientCreditPayload
}

type UseCreateClientCreditOptions = {
  onSuccess?: (credit: ClientCreditRecord) => void
  onError?: (error: Error) => void
}

export function useCreateClientCredit(options: UseCreateClientCreditOptions = {}) {
  const queryClient = useQueryClient()

  return useMutation<ClientCreditRecord, Error, CreateClientCreditArgs>({
    mutationFn: ({ clientId, payload }) => createClientCredit(clientId, payload),
    onSuccess: (credit, variables) => {
      queryClient.invalidateQueries({ queryKey: [...clientCreditsQueryKey, variables.clientId] })
      options.onSuccess?.(credit)
    },
    onError: (error) => {
      options.onError?.(error)
    },
  })
}
