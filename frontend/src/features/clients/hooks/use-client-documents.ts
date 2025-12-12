import { useQuery } from '@tanstack/react-query'
import { fetchClientDocuments, type ClientDocumentRecord } from '../api/documents'

export const clientDocumentsQueryKey = ['client-documents']

type UseClientDocumentsOptions = {
  enabled?: boolean
}

export function useClientDocuments(clientId: number | null, options: UseClientDocumentsOptions = {}) {
  return useQuery<ClientDocumentRecord[]>({
    queryKey: [...clientDocumentsQueryKey, clientId],
    queryFn: () => {
      if (clientId == null) {
        throw new Error('El identificador del cliente es requerido')
      }
      return fetchClientDocuments(clientId)
    },
    enabled: Boolean(clientId) && (options.enabled ?? true),
  })
}
