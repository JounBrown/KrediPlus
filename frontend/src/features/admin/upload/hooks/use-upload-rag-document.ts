import { useMutation, useQueryClient } from '@tanstack/react-query'
import { uploadRagDocument, type UploadRagDocumentResult } from '../api/rag-documents'
import { ragDocumentsQueryKey } from './use-rag-documents'

type UseUploadRagDocumentOptions = {
  onSuccess?: (result: UploadRagDocumentResult) => void
  onError?: (error: Error) => void
}

export function useUploadRagDocument(options: UseUploadRagDocumentOptions = {}) {
  const queryClient = useQueryClient()

  return useMutation<UploadRagDocumentResult, Error, File>({
    mutationFn: (file) => uploadRagDocument(file),
    onSuccess: (result) => {
      queryClient.invalidateQueries({ queryKey: ragDocumentsQueryKey })
      options.onSuccess?.(result)
    },
    onError: (error) => {
      options.onError?.(error)
    },
  })
}
