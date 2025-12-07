import { useEffect, useMemo, useState } from 'react'
import { initialClients, type ClientRecord } from '@/data/admin-clients'
import { useCreateClient } from '@/features/clients/hooks/use-create-client'
import { useUpdateClient } from '@/features/clients/hooks/use-update-client'
import { useClientDetails } from '@/features/clients/hooks/use-client-details'
import { useDeleteClient } from '@/features/clients/hooks/use-delete-client'

type ClientDialogType = 'create' | 'edit' | 'delete' | 'view' | null

type ClientFormState = Omit<ClientRecord, 'id' | 'createdAt'>

function createEmptyFormState(): ClientFormState {
  return {
    nombreCompleto: '',
    cedula: '',
    email: '',
    telefono: '',
    fechaNacimiento: '',
    direccion: '',
    infoAdicional: '',
  }
}

export function useClients(defaultClients: ClientRecord[] = initialClients) {
  const [clients, setClients] = useState<ClientRecord[]>(defaultClients)
  useEffect(() => {
    setClients(defaultClients)
  }, [defaultClients])
  const [clientSearch, setClientSearch] = useState('')
  const [dialogType, setDialogType] = useState<ClientDialogType>(null)
  const [dialogOpen, setDialogOpen] = useState(false)
  const [activeClient, setActiveClient] = useState<ClientRecord | null>(null)
  const [formState, setFormState] = useState<ClientFormState>(createEmptyFormState())

  const filteredClients = useMemo(() => {
    const query = clientSearch.toLowerCase()
    return clients.filter((client) =>
      `${client.nombreCompleto} ${client.cedula}`.toLowerCase().includes(query),
    )
  }, [clients, clientSearch])

  const openDialog = (type: Exclude<ClientDialogType, null>, client?: ClientRecord) => {
    setDialogType(type)
    setActiveClient(client ?? null)

    if (type === 'edit' && client) {
      const { createdAt, id, ...rest } = client
      setFormState(rest)
    } else if (type === 'create') {
      setFormState(createEmptyFormState())
    } else if (client) {
      const { createdAt, id, ...rest } = client
      setFormState(rest)
    }

    setDialogOpen(true)
  }

  const closeDialog = () => {
    setDialogOpen(false)
    setDialogType(null)
    setActiveClient(null)
  }

  const {
    data: fetchedClient,
    isFetching: loadingClientDetails,
    error: clientDetailsError,
  } = useClientDetails(activeClient?.id ?? null, {
    enabled: Boolean(activeClient && dialogType && dialogType !== 'create'),
  })
  const resolvedActiveClient = fetchedClient ?? activeClient

  useEffect(() => {
    if (!resolvedActiveClient || dialogType !== 'edit') return
    const { createdAt, id, ...rest } = resolvedActiveClient
    setFormState(rest)
  }, [resolvedActiveClient, dialogType])

  const createClientMutation = useCreateClient({
    onSuccess: () => {
      closeDialog()
    },
  })
  const updateClientMutation = useUpdateClient({
    onSuccess: () => {
      closeDialog()
    },
  })
  const deleteClientMutation = useDeleteClient({
    onSuccess: () => {
      closeDialog()
    },
  })

  const handleFieldChange = (field: keyof ClientFormState, value: string) => {
    setFormState((prev) => ({ ...prev, [field]: value }))
  }

  const handleSaveClient = async () => {
    if (!dialogType) return

    if (dialogType === 'create') {
      await createClientMutation.mutateAsync({
        nombre_completo: formState.nombreCompleto,
        cedula: formState.cedula,
        email: formState.email,
        telefono: formState.telefono,
        fecha_nacimiento: formState.fechaNacimiento,
        direccion: formState.direccion,
        info_adicional: formState.infoAdicional ? { notas: formState.infoAdicional } : undefined,
      })
      return
    }

    if (dialogType === 'edit' && activeClient) {
      await updateClientMutation.mutateAsync({
        clientId: activeClient.id,
        payload: {
          nombre_completo: formState.nombreCompleto,
          email: formState.email,
          telefono: formState.telefono,
          direccion: formState.direccion,
          info_adicional: formState.infoAdicional ? { notas: formState.infoAdicional } : undefined,
        },
      })
      return
    }

    closeDialog()
  }

  const handleDeleteClient = async () => {
    if (!activeClient) return
    await deleteClientMutation.mutateAsync(activeClient.id)
  }

  return {
    clientSearch,
    setClientSearch,
    filteredClients,
    openDialog,
    closeDialog,
    dialogOpen,
    dialogType,
    activeClient: resolvedActiveClient,
    formState,
    handleFieldChange,
    handleSaveClient,
    handleDeleteClient,
    creatingClient: createClientMutation.isPending,
    createError: createClientMutation.error,
    updatingClient: updateClientMutation.isPending,
    updateError: updateClientMutation.error,
    deletingClient: deleteClientMutation.isPending,
    deleteError: deleteClientMutation.error,
    loadingClientDetails,
    clientDetailsError,
  }
}
