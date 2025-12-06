import { useMemo, useState } from 'react'
import { initialClients, type ClientRecord } from '@/data/admin-clients'

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

  const handleFieldChange = (field: keyof ClientFormState, value: string) => {
    setFormState((prev) => ({ ...prev, [field]: value }))
  }

  const handleSaveClient = () => {
    if (!dialogType) return

    if (dialogType === 'create') {
      const newClient: ClientRecord = {
        id: Date.now(),
        createdAt: new Date().toISOString(),
        ...formState,
      }
      setClients((prev) => [newClient, ...prev])
    }

    if (dialogType === 'edit' && activeClient) {
      setClients((prev) =>
        prev.map((client) => (client.id === activeClient.id ? { ...client, ...formState } : client)),
      )
    }

    closeDialog()
  }

  const handleDeleteClient = () => {
    if (activeClient) {
      setClients((prev) => prev.filter((client) => client.id !== activeClient.id))
    }

    closeDialog()
  }

  return {
    clientSearch,
    setClientSearch,
    filteredClients,
    openDialog,
    closeDialog,
    dialogOpen,
    dialogType,
    activeClient,
    formState,
    handleFieldChange,
    handleSaveClient,
    handleDeleteClient,
  }
}
