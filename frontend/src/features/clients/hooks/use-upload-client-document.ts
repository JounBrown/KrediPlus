import { useMutation, useQueryClient } from '@tanstack/react-query'
import {
  uploadClientDocument,
  type UploadClientDocumentPayload,
  type UploadClientDocumentResponse,
} from '../api/documents'
import { clientDocumentsQueryKey } from './use-client-documents'

type UseUploadClientDocumentOptions = {
  onSuccess?: (result: UploadClientDocumentResponse) => void
  onError?: (error: Error) => void
}

export function useUploadClientDocument(options: UseUploadClientDocumentOptions = {}) {
  const queryClient = useQueryClient()

  return useMutation<UploadClientDocumentResponse, Error, UploadClientDocumentPayload>({
    mutationFn: (payload) => uploadClientDocument(payload),
    onSuccess: (result, variables) => {
      queryClient.invalidateQueries({ queryKey: [...clientDocumentsQueryKey, variables.clientId] })
      options.onSuccess?.(result)
    },
    onError: (error) => {
      options.onError?.(error)
    },
  })
}
