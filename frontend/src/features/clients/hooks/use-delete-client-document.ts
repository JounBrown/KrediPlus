import { useMutation, useQueryClient } from '@tanstack/react-query'
import { deleteClientDocument, type DeleteClientDocumentResponse } from '../api/documents'
import { clientDocumentsQueryKey } from './use-client-documents'

type DeleteClientDocumentArgs = {
  clientId: number
  documentId: number
}

type UseDeleteClientDocumentOptions = {
  onSuccess?: (response: DeleteClientDocumentResponse) => void
  onError?: (error: Error) => void
}

export function useDeleteClientDocument(options: UseDeleteClientDocumentOptions = {}) {
  const queryClient = useQueryClient()

  return useMutation<DeleteClientDocumentResponse, Error, DeleteClientDocumentArgs>({
    mutationFn: ({ clientId, documentId }) => deleteClientDocument(clientId, documentId),
    onSuccess: (response, variables) => {
      queryClient.invalidateQueries({ queryKey: [...clientDocumentsQueryKey, variables.clientId] })
      options.onSuccess?.(response)
    },
    onError: (error) => {
      options.onError?.(error)
    },
  })
}
