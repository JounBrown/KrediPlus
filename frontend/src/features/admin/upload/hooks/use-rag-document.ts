import { useQuery } from '@tanstack/react-query'
import { fetchRagDocumentById, type RagDocument } from '../api/rag-documents'
import { ragDocumentsQueryKey } from './use-rag-documents'

export function ragDocumentQueryKey(documentId: number | string) {
  return [...ragDocumentsQueryKey, documentId] as const
}

type UseRagDocumentOptions = {
  enabled?: boolean
}

export function useRagDocument(documentId: number | string, options: UseRagDocumentOptions = {}) {
  return useQuery<RagDocument>({
    queryKey: ragDocumentQueryKey(documentId),
    queryFn: () => fetchRagDocumentById(documentId),
    enabled: options.enabled ?? Boolean(documentId),
  })
}
