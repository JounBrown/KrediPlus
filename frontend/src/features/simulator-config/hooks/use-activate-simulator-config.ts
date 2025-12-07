import { useMutation, useQueryClient } from '@tanstack/react-query'
import type { SimulatorConfig } from '@/data/simulator-config'
import { activateSimulatorConfig } from '../api/simulator-config'
import { simulatorConfigsQueryKey } from './use-simulator-configs-query'

type UseActivateSimulatorConfigOptions = {
  onSuccess?: (config: SimulatorConfig) => void
  onError?: (error: Error) => void
}

export function useActivateSimulatorConfig(options: UseActivateSimulatorConfigOptions = {}) {
  const queryClient = useQueryClient()

  return useMutation<SimulatorConfig, Error, number>({
    mutationFn: (configId) => activateSimulatorConfig(configId),
    onSuccess: (config) => {
      queryClient.invalidateQueries({ queryKey: simulatorConfigsQueryKey })
      options.onSuccess?.(config)
    },
    onError: (error) => {
      options.onError?.(error)
    },
  })
}
