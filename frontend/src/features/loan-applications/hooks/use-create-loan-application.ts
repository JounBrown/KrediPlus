import { useMutation, useQueryClient } from '@tanstack/react-query'
import type { LoanApplication } from '@/features/submit-form/types/loan-application'
import {
  createLoanApplication,
  type CreateLoanApplicationPayload,
} from '../api/loan-applications'
import { loanApplicationsQueryKey } from './use-loan-applications'

type UseCreateLoanApplicationOptions = {
  onSuccess?: (data: LoanApplication) => void
  onError?: (error: Error) => void
}

export function useCreateLoanApplication(options: UseCreateLoanApplicationOptions = {}) {
  const queryClient = useQueryClient()

  return useMutation<LoanApplication, Error, CreateLoanApplicationPayload>({
    mutationFn: (payload) => createLoanApplication(payload),
    onSuccess: (data) => {
      queryClient.invalidateQueries({ queryKey: loanApplicationsQueryKey })
      options.onSuccess?.(data)
    },
    onError: (error) => {
      options.onError?.(error)
    },
  })
}
