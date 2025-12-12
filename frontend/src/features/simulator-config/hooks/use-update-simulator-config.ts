import { useMutation, useQueryClient } from '@tanstack/react-query'
import type { SimulatorConfig } from '@/data/simulator-config'
import {
  updateSimulatorConfig,
  type UpdateSimulatorConfigPayload,
} from '../api/simulator-config'
import { simulatorConfigsQueryKey } from './use-simulator-configs-query'

type UseUpdateSimulatorConfigOptions = {
  onSuccess?: (config: SimulatorConfig, configId: number) => void
  onError?: (error: Error) => void
}

export function useUpdateSimulatorConfig(options: UseUpdateSimulatorConfigOptions = {}) {
  const queryClient = useQueryClient()

  return useMutation<SimulatorConfig, Error, { configId: number; payload: UpdateSimulatorConfigPayload}>({
    mutationFn: ({ configId, payload }) => updateSimulatorConfig(configId, payload),
    onSuccess: (config, variables) => {
      queryClient.invalidateQueries({ queryKey: simulatorConfigsQueryKey })
      options.onSuccess?.(config, variables.configId)
    },
    onError: (error) => {
      options.onError?.(error)
    },
  })
}
