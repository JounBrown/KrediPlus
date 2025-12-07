import { useMutation, useQueryClient } from '@tanstack/react-query'
import { deleteSimulatorConfig } from '../api/simulator-config'
import { simulatorConfigsQueryKey } from './use-simulator-configs-query'

type UseDeleteSimulatorConfigOptions = {
  onSuccess?: (message: string, configId: number) => void
  onError?: (error: Error) => void
}

export function useDeleteSimulatorConfig(options: UseDeleteSimulatorConfigOptions = {}) {
  const queryClient = useQueryClient()

  return useMutation<string, Error, number>({
    mutationFn: (configId) => deleteSimulatorConfig(configId),
    onSuccess: (message, configId) => {
      queryClient.invalidateQueries({ queryKey: simulatorConfigsQueryKey })
      options.onSuccess?.(message, configId)
    },
    onError: (error) => {
      options.onError?.(error)
    },
  })
}
