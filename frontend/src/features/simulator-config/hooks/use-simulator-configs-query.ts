import { useQuery } from '@tanstack/react-query'
import type { SimulatorConfig } from '@/data/simulator-config'
import { fetchSimulatorConfigs } from '../api/simulator-config'

export const simulatorConfigsQueryKey = ['simulatorConfigs'] as const

export function useSimulatorConfigsQuery() {
  return useQuery<SimulatorConfig[]>({
    queryKey: simulatorConfigsQueryKey,
    queryFn: fetchSimulatorConfigs,
    staleTime: 60_000,
  })
}
