import { useMutation, useQueryClient } from '@tanstack/react-query'
import { deleteRagDocument, type DeleteRagDocumentResult } from '../api/rag-documents'
import { ragDocumentsQueryKey } from './use-rag-documents'
import { ragDocumentQueryKey } from './use-rag-document'

type UseDeleteRagDocumentOptions = {
  onSuccess?: (result: DeleteRagDocumentResult) => void
  onError?: (error: Error) => void
}

export function useDeleteRagDocument(options: UseDeleteRagDocumentOptions = {}) {
  const queryClient = useQueryClient()

  return useMutation<DeleteRagDocumentResult, Error, number | string>({
    mutationFn: (documentId) => deleteRagDocument(documentId),
    onSuccess: (result, documentId) => {
      queryClient.invalidateQueries({ queryKey: ragDocumentsQueryKey })
      queryClient.removeQueries({ queryKey: ragDocumentQueryKey(documentId) })
      options.onSuccess?.(result)
    },
    onError: (error) => {
      options.onError?.(error)
    },
  })
}
