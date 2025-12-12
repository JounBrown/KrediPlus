import { useQuery } from '@tanstack/react-query'
import { fetchRagDocuments, type RagDocument } from '../api/rag-documents'

export const ragDocumentsQueryKey = ['ragDocuments'] as const

export function useRagDocuments() {
  return useQuery<RagDocument[]>({
    queryKey: ragDocumentsQueryKey,
    queryFn: fetchRagDocuments,
    staleTime: 15_000,
  })
}
