import { useMutation, useQueryClient } from '@tanstack/react-query'
import type { SimulatorConfig } from '@/data/simulator-config'
import {
  createSimulatorConfig,
  type CreateSimulatorConfigPayload,
} from '../api/simulator-config'
import { simulatorConfigsQueryKey } from './use-simulator-configs-query'

type UseCreateSimulatorConfigOptions = {
  onSuccess?: (config: SimulatorConfig) => void
  onError?: (error: Error) => void
}

export function useCreateSimulatorConfig(options: UseCreateSimulatorConfigOptions = {}) {
  const queryClient = useQueryClient()

  return useMutation<SimulatorConfig, Error, CreateSimulatorConfigPayload>({
    mutationFn: (payload) => createSimulatorConfig(payload),
    onSuccess: (config) => {
      queryClient.invalidateQueries({ queryKey: simulatorConfigsQueryKey })
      options.onSuccess?.(config)
    },
    onError: (error) => {
      options.onError?.(error)
    },
  })
}
