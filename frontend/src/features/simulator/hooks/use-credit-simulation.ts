import { useMutation } from '@tanstack/react-query'
import {
  simulateCredit,
  type CreditSimulationResult,
  type SimulateCreditParams,
} from '../api/simulate'

type UseCreditSimulationOptions = {
  onSuccess?: (result: CreditSimulationResult) => void
  onError?: (error: Error) => void
}

export function useCreditSimulation(options: UseCreditSimulationOptions = {}) {
  return useMutation<CreditSimulationResult, Error, SimulateCreditParams>({
    mutationFn: (params) => simulateCredit(params),
    onSuccess: (result) => {
      options.onSuccess?.(result)
    },
    onError: (error) => {
      options.onError?.(error)
    },
  })
}
