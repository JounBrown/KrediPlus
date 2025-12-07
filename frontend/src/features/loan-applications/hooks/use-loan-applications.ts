import { useQuery } from '@tanstack/react-query'
import type { LoanApplication } from '@/features/submit-form/types/loan-application'
import { fetchLoanApplications } from '../api/loan-applications'

export const loanApplicationsQueryKey = ['loanApplications'] as const

export function useLoanApplications() {
  return useQuery<LoanApplication[]>({
    queryKey: loanApplicationsQueryKey,
    queryFn: fetchLoanApplications,
    staleTime: 30_000,
  })
}
