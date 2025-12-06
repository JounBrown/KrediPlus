import { useMemo, useState } from 'react'
import { Link, Route } from '@tanstack/react-router'
import { rootRoute } from './root'
import { SiteHeader } from '@/components/layout/site-header'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
import { Input } from '@/components/ui/input'
import { Textarea } from '@/components/ui/textarea'
import { cn } from '@/lib/utils'
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
} from '@/components/ui/dropdown-menu'
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from '@/components/ui/dialog'
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from '@/components/ui/table'
import { ListChecks, MoreHorizontal, Search, Settings, Users, UploadCloud } from 'lucide-react'
import { CreditSimulator } from '@/features/simulator/components/credit-simulator'
import {
  defaultSimulatorConfig,
  initialSimulatorConfigs,
  type SimulatorConfig,
} from '@/data/simulator-config'

type TabId = 'requests' | 'upload' | 'clients' | 'simulator'

type RequestRecord = {
  name: string
  id: string
  convenio: string
  phone: string
  birthDate: string
}

type ClientRecord = {
  id: number
  createdAt: string
  nombreCompleto: string
  cedula: string
  email: string
  telefono: string
  fechaNacimiento: string
  direccion: string
  infoAdicional: string
}

type SimulatorConfigForm = {
  tasaInteresMensual: string
  montoMinimo: string
  montoMaximo: string
  plazosDisponibles: string
}

const adminTabs = [
  { id: 'requests', label: 'Solicitudes Registradas', icon: ListChecks },
  { id: 'upload', label: 'Carga de Documentos', icon: UploadCloud },
  { id: 'clients', label: 'Gestión Clientes', icon: Users },
  { id: 'simulator', label: 'Configuración Simulador', icon: Settings },
] as const satisfies ReadonlyArray<{ id: TabId; label: string; icon: typeof ListChecks }>

const requestsData: RequestRecord[] = [
  {
    name: 'Carlos Prada Claro',
    id: '1022423',
    convenio: 'option3',
    phone: '84032321',
    birthDate: '24/05/2015',
  },
  {
    name: 'Johan Scripts',
    id: '1234567891',
    convenio: 'option1',
    phone: '3214567890',
    birthDate: '22/10/2024',
  },
  {
    name: 'Isidor Estrada Morez',
    id: '21321312131',
    convenio: 'option1',
    phone: '3052892121',
    birthDate: '07/10/2024',
  },
  {
    name: 'Moreno Moreno',
    id: '12313',
    convenio: 'option2',
    phone: '3052892121',
    birthDate: '05/05/2008',
  },
  {
    name: 'Prueba Despliegue',
    id: '1111111111',
    convenio: 'option2',
    phone: '3214567890',
    birthDate: '08/07/1952',
  },
]

const initialClients: ClientRecord[] = [
  {
    id: 1,
    createdAt: '2024-10-12T10:00:00.000Z',
    nombreCompleto: 'Andrea Ríos',
    cedula: '1034567890',
    email: 'andrea.rios@email.com',
    telefono: '3125556677',
    fechaNacimiento: '1989-05-14',
    direccion: 'Cra 15 #120-45, Bogotá',
    infoAdicional: 'Cliente con buen historial, interesada en ampliación de cupo.',
  },
  {
    id: 2,
    createdAt: '2024-09-30T08:30:00.000Z',
    nombreCompleto: 'Luis Peña',
    cedula: '987654321',
    email: 'luis.pena@email.com',
    telefono: '3001112233',
    fechaNacimiento: '1978-11-02',
    direccion: 'Cll 45 #12-80, Medellín',
    infoAdicional: 'Solicita crédito para remodelación. Esperando documentos.',
  },
  {
    id: 3,
    createdAt: '2024-11-05T14:20:00.000Z',
    nombreCompleto: 'María Gómez',
    cedula: '456789123',
    email: 'maria.gomez@email.com',
    telefono: '3169874560',
    fechaNacimiento: '1965-03-28',
    direccion: 'Av. Boyacá #85-12, Bogotá',
    infoAdicional: 'Reportada en centrales, requiere seguimiento cercano.',
  },
]

function AdminPage() {
  const [activeTab, setActiveTab] = useState<TabId>('requests')
  const [searchTerm, setSearchTerm] = useState('')
  const [clientSearch, setClientSearch] = useState('')
  const [clients, setClients] = useState<ClientRecord[]>(initialClients)
  const [simConfigs, setSimConfigs] = useState<SimulatorConfig[]>(initialSimulatorConfigs)
  const [selectedConfigId, setSelectedConfigId] = useState<number>(defaultSimulatorConfig.id)
  const [dialogType, setDialogType] = useState<'create' | 'edit' | 'delete' | 'view' | null>(null)
  const [dialogOpen, setDialogOpen] = useState(false)
  const [activeClient, setActiveClient] = useState<ClientRecord | null>(null)
  const [formState, setFormState] = useState<Omit<ClientRecord, 'id' | 'createdAt'>>({
    nombreCompleto: '',
    cedula: '',
    email: '',
    telefono: '',
    fechaNacimiento: '',
    direccion: '',
    infoAdicional: '',
  })
  const [configDialogOpen, setConfigDialogOpen] = useState(false)
  const [configDialogMode, setConfigDialogMode] = useState<'create' | 'edit'>('create')
  const [activeSimConfig, setActiveSimConfig] = useState<SimulatorConfig | null>(null)
  const [configForm, setConfigForm] = useState<SimulatorConfigForm>({
    tasaInteresMensual: '',
    montoMinimo: '',
    montoMaximo: '',
    plazosDisponibles: '',
  })

  const filteredRequests = useMemo(() => {
    const query = searchTerm.toLowerCase()
    return requestsData.filter((request) =>
      `${request.name} ${request.id}`.toLowerCase().includes(query),
    )
  }, [searchTerm])

  const filteredClients = useMemo(() => {
    const query = clientSearch.toLowerCase()
    return clients.filter((client) =>
      `${client.nombreCompleto} ${client.cedula}`.toLowerCase().includes(query),
    )
  }, [clients, clientSearch])

  const currencyFormatter = useMemo(() => {
    return new Intl.NumberFormat('es-CO', {
      style: 'currency',
      currency: 'COP',
      maximumFractionDigits: 0,
    })
  }, [])

  const selectedConfig = useMemo(() => {
    if (!simConfigs.length) return null
    return simConfigs.find((config) => config.id === selectedConfigId) ?? simConfigs[0]
  }, [selectedConfigId, simConfigs])

  const openDialog = (type: 'create' | 'edit' | 'delete' | 'view', client?: ClientRecord) => {
    setDialogType(type)
    setActiveClient(client ?? null)
    if (type === 'edit' && client) {
      const { createdAt, id, ...rest } = client
      setFormState(rest)
    } else if (type === 'create') {
      setFormState({
        nombreCompleto: '',
        cedula: '',
        email: '',
        telefono: '',
        fechaNacimiento: '',
        direccion: '',
        infoAdicional: '',
      })
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

  const handleFieldChange = (
    field: keyof Omit<ClientRecord, 'id' | 'createdAt'>,
    value: string,
  ) => {
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

  const openSimConfigDialog = (mode: 'create' | 'edit', config?: SimulatorConfig) => {
    setConfigDialogMode(mode)
    if (mode === 'edit' && config) {
      setActiveSimConfig(config)
      setConfigForm({
        tasaInteresMensual: config.tasaInteresMensual.toString(),
        montoMinimo: config.montoMinimo.toString(),
        montoMaximo: config.montoMaximo.toString(),
        plazosDisponibles: config.plazosDisponibles.join(', '),
      })
    } else {
      setActiveSimConfig(null)
      setConfigForm({
        tasaInteresMensual: '',
        montoMinimo: '',
        montoMaximo: '',
        plazosDisponibles: '',
      })
    }
    setConfigDialogOpen(true)
  }

  const closeSimConfigDialog = () => {
    setConfigDialogOpen(false)
    setActiveSimConfig(null)
  }

  const handleConfigFormChange = (field: keyof SimulatorConfigForm, value: string) => {
    setConfigForm((prev) => ({ ...prev, [field]: value }))
  }

  const handleSaveSimConfig = () => {
    const parsedRate = parseFloat(configForm.tasaInteresMensual) || 0
    const parsedMin = parseInt(configForm.montoMinimo, 10) || 0
    const parsedMax = parseInt(configForm.montoMaximo, 10) || 0
    const parsedPlazos = configForm.plazosDisponibles
      .split(',')
      .map((value) => Number(value.trim()))
      .filter((value) => !Number.isNaN(value) && value > 0)

    const safePlazos = parsedPlazos.length ? parsedPlazos : [12]

    if (configDialogMode === 'create') {
      const newConfig: SimulatorConfig = {
        id: Date.now(),
        createdAt: new Date().toISOString(),
        tasaInteresMensual: parsedRate,
        montoMinimo: parsedMin,
        montoMaximo: parsedMax,
        plazosDisponibles: safePlazos,
      }
      setSimConfigs((prev) => [newConfig, ...prev])
      setSelectedConfigId(newConfig.id)
    } else if (configDialogMode === 'edit' && activeSimConfig) {
      const updatedConfig: SimulatorConfig = {
        ...activeSimConfig,
        tasaInteresMensual: parsedRate,
        montoMinimo: parsedMin,
        montoMaximo: parsedMax,
        plazosDisponibles: safePlazos,
      }
      setSimConfigs((prev) =>
        prev.map((config) => (config.id === updatedConfig.id ? updatedConfig : config)),
      )
      setSelectedConfigId(updatedConfig.id)
    }

    closeSimConfigDialog()
  }

  const handleSelectConfig = (configId: number) => {
    setSelectedConfigId(configId)
  }

  return (
    <div className="min-h-screen bg-[#f4f7fb]">
      <SiteHeader />
      <main className="mx-auto flex w-full max-w-6xl flex-col gap-6 px-6 pb-16 pt-10">
        <div className="rounded-3xl border border-slate-100 bg-white p-8 shadow-sm">
          <div className="space-y-2">
            <p className="text-sm font-semibold uppercase tracking-wide text-[#f26522]">
              Panel administrativo
            </p>
            <h1 className="text-3xl font-bold text-[#0d2f62]">Gestiona KrediPlus</h1>
            <p className="text-slate-500">
              Gestiona las solicitudes, documentos y configuraciones del simulador en un solo lugar.
            </p>
          </div>

          <div className="mt-6 flex flex-wrap gap-3">
            {adminTabs.map((tab) => {
              const Icon = tab.icon
              const isActive = tab.id === activeTab
              return (
                <button
                  key={tab.id}
                  onClick={() => setActiveTab(tab.id)}
                  className={cn(
                    'flex items-center gap-2 rounded-full border px-4 py-2 text-sm font-semibold transition',
                    isActive
                      ? 'border-transparent bg-[#f26522] text-white shadow-lg'
                      : 'border-slate-200 text-[#0d2f62] hover:border-[#f26522]/40',
                  )}
                >
                  <Icon className="h-4 w-4" />
                  {tab.label}
                </button>
              )
            })}
          </div>

          <hr className="my-6 border-slate-100" />

          {activeTab === 'requests' ? (
            <section>
              <div className="flex flex-wrap items-center justify-between gap-4">
                <div>
                  <p className="text-lg font-semibold text-[#0d2f62]">Solicitudes Registradas</p>
                  <p className="text-sm text-slate-500">Revisa el estado de las solicitudes recibidas.</p>
                </div>
                <Link
                  to="/"
                  className="rounded-full border border-[#f26522]/40 px-4 py-2 text-sm font-semibold text-[#f26522] transition hover:bg-[#f26522]/10"
                >
                  Volver al inicio
                </Link>
              </div>

              <div className="mt-4 flex w-full flex-col gap-2">
                <label className="text-xs font-semibold uppercase tracking-wide text-slate-500">
                  Buscar por cédula o nombre
                </label>
                <div className="flex items-center gap-2 rounded-2xl border border-[#e2e8f0] bg-[#f1f5f9] px-4 py-3 text-[#0f172a] shadow-inner">
                  <Search className="h-4 w-4 text-[#475569]" />
                  <Input
                    value={searchTerm}
                    onChange={(event) => setSearchTerm(event.target.value)}
                    placeholder="Buscar..."
                    className="border-0 bg-transparent text-[#0f172a] placeholder:text-[#475569]/60 focus-visible:ring-0"
                  />
                </div>
              </div>

              <div className="mt-6 overflow-hidden rounded-2xl border border-slate-100 shadow-sm">
                <Table>
                  <TableHeader className="bg-slate-50">
                    <TableRow>
                      <TableHead className="text-xs font-bold uppercase text-slate-500">Nombre</TableHead>
                      <TableHead className="text-xs font-bold uppercase text-slate-500">Cédula</TableHead>
                      <TableHead className="text-xs font-bold uppercase text-slate-500">Convenio</TableHead>
                      <TableHead className="text-xs font-bold uppercase text-slate-500">Teléfono</TableHead>
                      <TableHead className="text-xs font-bold uppercase text-slate-500">Fecha de nacimiento</TableHead>
                      <TableHead>
                        <span className="sr-only">Acciones</span>
                      </TableHead>
                    </TableRow>
                  </TableHeader>
                  <TableBody>
                    {filteredRequests.map((request) => (
                      <TableRow key={request.id} className="text-sm">
                        <TableCell className="font-semibold text-[#0d2f62]">{request.name}</TableCell>
                        <TableCell>{request.id}</TableCell>
                        <TableCell className="uppercase text-xs font-semibold text-[#f26522]">
                          {request.convenio}
                        </TableCell>
                        <TableCell>{request.phone}</TableCell>
                        <TableCell>{request.birthDate}</TableCell>
                        <TableCell className="text-right">
                          <button
                            className="rounded-full p-1 text-slate-400 transition hover:bg-slate-100 hover:text-slate-600"
                            aria-label="Más acciones"
                          >
                            <MoreHorizontal className="h-5 w-5" />
                          </button>
                        </TableCell>
                      </TableRow>
                    ))}
                  </TableBody>
                </Table>
              </div>
            </section>
          ) : activeTab === 'upload' ? (
            <section className="space-y-6">
              <div className="flex flex-wrap items-center justify-between gap-4">
                <div>
                  <p className="text-lg font-semibold text-[#0d2f62]">Carga de Documentos</p>
                  <p className="text-sm text-slate-500">Arrastra archivos PDF o DOCX para añadir soportes.</p>
                </div>
                <Button
                  className="bg-[#0d2f62] text-white hover:bg-[#0b2772]"
                  onClick={() => setActiveTab('requests')}
                >
                  Ver solicitudes
                </Button>
              </div>

              <div className="rounded-3xl border-2 border-dashed border-slate-300 bg-slate-50 px-6 py-12 text-center">
                <UploadCloud className="mx-auto h-10 w-10 text-[#0d2f62]" />
                <p className="mt-4 text-base font-semibold text-[#0d2f62]">
                  Arrastra y suelta archivos PDF o DOCX aquí
                </p>
                <p className="text-sm text-slate-500">o haz clic para seleccionar archivos</p>
                <Button variant="outline" className="mt-6 border-[#0d2f62] text-[#0d2f62] hover:bg-white">
                  Seleccionar archivos
                </Button>
              </div>
            </section>
          ) : activeTab === 'clients' ? (
            <section className="space-y-6">
              <div className="flex flex-wrap items-center justify-between gap-4">
                <div>
                  <p className="text-lg font-semibold text-[#0d2f62]">Gestión de Clientes</p>
                  <p className="text-sm text-slate-500">Administra la base de clientes registrados.</p>
                </div>
                <Button
                  className="bg-[#f26522] text-white hover:bg-[#d85314]"
                  onClick={() => openDialog('create')}
                >
                  Agregar cliente
                </Button>
              </div>

              <div className="mt-2 flex w-full flex-col gap-2">
                <label className="text-xs font-semibold uppercase tracking-wide text-slate-500">
                  Buscar por cédula o nombre
                </label>
                <div className="flex items-center gap-2 rounded-2xl border border-[#e2e8f0] bg-[#f1f5f9] px-4 py-3 text-[#0f172a] shadow-inner">
                  <Search className="h-4 w-4 text-[#475569]" />
                  <Input
                    value={clientSearch}
                    onChange={(event) => setClientSearch(event.target.value)}
                    placeholder="Buscar clientes..."
                    className="border-0 bg-transparent text-[#0f172a] placeholder:text-[#475569]/60 focus-visible:ring-0"
                  />
                </div>
              </div>

              <div className="overflow-hidden rounded-2xl border border-slate-100 shadow-sm">
                <Table>
                  <TableHeader className="bg-slate-50">
                    <TableRow>
                      <TableHead className="text-xs font-bold uppercase text-slate-500">Nombre</TableHead>
                      <TableHead className="text-xs font-bold uppercase text-slate-500">Cédula</TableHead>
                      <TableHead className="text-xs font-bold uppercase text-slate-500">Email</TableHead>
                      <TableHead className="text-xs font-bold uppercase text-slate-500">Teléfono</TableHead>
                      <TableHead className="text-xs font-bold uppercase text-slate-500">Dirección</TableHead>
                      <TableHead>
                        <span className="sr-only">Acciones</span>
                      </TableHead>
                    </TableRow>
                  </TableHeader>
                  <TableBody>
                    {filteredClients.map((client) => (
                      <TableRow key={client.id} className="text-sm">
                        <TableCell className="font-semibold text-[#0d2f62]">{client.nombreCompleto}</TableCell>
                        <TableCell>{client.cedula}</TableCell>
                        <TableCell>{client.email}</TableCell>
                        <TableCell>{client.telefono}</TableCell>
                        <TableCell>{client.direccion}</TableCell>
                        <TableCell className="text-right">
                          <DropdownMenu>
                            <DropdownMenuTrigger asChild>
                              <button
                                className="rounded-full p-1 text-slate-400 transition hover:bg-slate-100 hover:text-slate-600"
                                aria-label="Más acciones"
                              >
                                <MoreHorizontal className="h-5 w-5" />
                              </button>
                            </DropdownMenuTrigger>
                            <DropdownMenuContent align="end">
                              <DropdownMenuItem onClick={() => openDialog('view', client)}>
                                Ver detalles
                              </DropdownMenuItem>
                              <DropdownMenuItem onClick={() => openDialog('edit', client)}>
                                Editar
                              </DropdownMenuItem>
                              <DropdownMenuItem
                                className="text-red-600"
                                onClick={() => openDialog('delete', client)}
                              >
                                Eliminar
                              </DropdownMenuItem>
                            </DropdownMenuContent>
                          </DropdownMenu>
                        </TableCell>
                      </TableRow>
                    ))}
                  </TableBody>
                </Table>
              </div>
            </section>
          ) : (
            <section className="space-y-6">
              <div className="flex flex-wrap items-center justify-between gap-4">
                <div>
                  <p className="text-lg font-semibold text-[#0d2f62]">Configuración del Simulador</p>
                  <p className="text-sm text-slate-500">
                    Ajusta los parámetros financieros que usa el simulador de crédito.
                  </p>
                </div>
                <Button
                  className="bg-[#f26522] text-white hover:bg-[#d85314]"
                  onClick={() => openSimConfigDialog('create')}
                >
                  Agregar nueva configuración
                </Button>
              </div>

              <div className="overflow-hidden rounded-2xl border border-slate-100 shadow-sm">
                <Table>
                  <TableHeader className="bg-slate-50">
                    <TableRow>
                      <TableHead className="text-xs font-bold uppercase text-slate-500">ID</TableHead>
                      <TableHead className="text-xs font-bold uppercase text-slate-500">Creado el</TableHead>
                      <TableHead className="text-xs font-bold uppercase text-slate-500">Tasa interés mensual</TableHead>
                      <TableHead className="text-xs font-bold uppercase text-slate-500">Monto mínimo</TableHead>
                      <TableHead className="text-xs font-bold uppercase text-slate-500">Monto máximo</TableHead>
                      <TableHead className="text-xs font-bold uppercase text-slate-500">Plazos disponibles</TableHead>
                      <TableHead>
                        <span className="sr-only">Acciones</span>
                      </TableHead>
                    </TableRow>
                  </TableHeader>
                  <TableBody>
                    {simConfigs.map((config) => (
                      <TableRow
                        key={config.id}
                        className={cn(
                          'text-sm',
                          selectedConfig?.id === config.id && 'bg-orange-50/60',
                        )}
                      >
                        <TableCell>
                          <div className="flex items-center gap-2">
                            <span className="font-semibold text-[#0d2f62]">#{config.id}</span>
                            {selectedConfig?.id === config.id && (
                              <Badge variant="outline" className="border-[#f26522] text-[#f26522]">
                                Activo
                              </Badge>
                            )}
                          </div>
                        </TableCell>
                        <TableCell>
                          {new Date(config.createdAt).toLocaleDateString('es-CO', {
                            year: 'numeric',
                            month: 'short',
                            day: 'numeric',
                          })}
                        </TableCell>
                        <TableCell>{config.tasaInteresMensual.toFixed(2)}%</TableCell>
                        <TableCell>{currencyFormatter.format(config.montoMinimo)}</TableCell>
                        <TableCell>{currencyFormatter.format(config.montoMaximo)}</TableCell>
                        <TableCell>
                          {config.plazosDisponibles.map((plazo) => `${plazo}m`).join(', ')}
                        </TableCell>
                        <TableCell className="text-right">
                          <DropdownMenu>
                            <DropdownMenuTrigger asChild>
                              <button
                                className="rounded-full p-1 text-slate-400 transition hover:bg-slate-100 hover:text-slate-600"
                                aria-label="Acciones de configuración"
                              >
                                <MoreHorizontal className="h-5 w-5" />
                              </button>
                            </DropdownMenuTrigger>
                            <DropdownMenuContent align="end">
                              <DropdownMenuItem onClick={() => openSimConfigDialog('edit', config)}>
                                Editar
                              </DropdownMenuItem>
                              <DropdownMenuItem onClick={() => handleSelectConfig(config.id)}>
                                Seleccionar
                              </DropdownMenuItem>
                            </DropdownMenuContent>
                          </DropdownMenu>
                        </TableCell>
                      </TableRow>
                    ))}
                  </TableBody>
                </Table>
              </div>

              {selectedConfig && (
                <div className="space-y-3">
                  <CreditSimulator
                    key={selectedConfig.id}
                    minAmount={selectedConfig.montoMinimo}
                    maxAmount={selectedConfig.montoMaximo}
                    monthlyRate={selectedConfig.tasaInteresMensual}
                    terms={selectedConfig.plazosDisponibles}
                    initialAmount={selectedConfig.montoMinimo}
                    initialTerm={selectedConfig.plazosDisponibles[0]}
                    showModeToggle
                  />
                  <p className="text-center text-sm text-slate-500">
                    Configuración activa #{selectedConfig.id} creada el{' '}
                    {new Date(selectedConfig.createdAt).toLocaleDateString('es-CO')}
                  </p>
                </div>
              )}
            </section>
          )}
        </div>
      </main>

      <Dialog
        open={dialogOpen && Boolean(dialogType)}
        onOpenChange={(open: boolean) => {
          if (!open) closeDialog()
        }}
      >
        <DialogContent>
          {dialogType === 'view' && activeClient ? (
            <>
              <DialogHeader>
                <DialogTitle>Detalles del cliente</DialogTitle>
                <DialogDescription>
                  Creado el {new Date(activeClient.createdAt).toLocaleString('es-CO')}
                </DialogDescription>
              </DialogHeader>
              <div className="space-y-3 text-sm text-slate-600">
                <p>
                  <span className="font-semibold">Nombre:</span> {activeClient.nombreCompleto}
                </p>
                <p>
                  <span className="font-semibold">Cédula:</span> {activeClient.cedula}
                </p>
                <p>
                  <span className="font-semibold">Email:</span> {activeClient.email}
                </p>
                <p>
                  <span className="font-semibold">Teléfono:</span> {activeClient.telefono}
                </p>
                <p>
                  <span className="font-semibold">Fecha de nacimiento:</span> {activeClient.fechaNacimiento}
                </p>
                <p>
                  <span className="font-semibold">Dirección:</span> {activeClient.direccion}
                </p>
                <p>
                  <span className="font-semibold">Info adicional:</span> {activeClient.infoAdicional}
                </p>
              </div>
              <DialogFooter>
                <Button variant="outline" onClick={closeDialog}>
                  Cerrar
                </Button>
              </DialogFooter>
            </>
          ) : dialogType === 'delete' && activeClient ? (
            <>
              <DialogHeader>
                <DialogTitle>Eliminar cliente</DialogTitle>
                <DialogDescription>
                  Esta acción eliminará los registros de {activeClient.nombreCompleto}.
                </DialogDescription>
              </DialogHeader>
              <p className="text-sm text-slate-600">
                ¿Confirmas que deseas eliminar este cliente? Esta acción no se puede deshacer.
              </p>
              <DialogFooter>
                <Button variant="outline" onClick={closeDialog}>
                  Cancelar
                </Button>
                <Button variant="destructive" onClick={handleDeleteClient}>
                  Eliminar
                </Button>
              </DialogFooter>
            </>
          ) : dialogType && (dialogType === 'create' || dialogType === 'edit') ? (
            <>
              <DialogHeader>
                <DialogTitle>
                  {dialogType === 'create' ? 'Agregar cliente' : 'Editar cliente'}
                </DialogTitle>
                <DialogDescription>
                  Completa la información del cliente para continuar.
                </DialogDescription>
              </DialogHeader>
              <div className="space-y-4">
                <Input
                  value={formState.nombreCompleto}
                  onChange={(event) => handleFieldChange('nombreCompleto', event.target.value)}
                  placeholder="Nombre completo"
                />
                <Input
                  value={formState.cedula}
                  onChange={(event) => handleFieldChange('cedula', event.target.value)}
                  placeholder="Cédula"
                />
                <Input
                  type="email"
                  value={formState.email}
                  onChange={(event) => handleFieldChange('email', event.target.value)}
                  placeholder="Correo electrónico"
                />
                <Input
                  value={formState.telefono}
                  onChange={(event) => handleFieldChange('telefono', event.target.value)}
                  placeholder="Teléfono"
                />
                <Input
                  type="date"
                  value={formState.fechaNacimiento}
                  onChange={(event) => handleFieldChange('fechaNacimiento', event.target.value)}
                />
                <Input
                  value={formState.direccion}
                  onChange={(event) => handleFieldChange('direccion', event.target.value)}
                  placeholder="Dirección"
                />
                <Textarea
                  value={formState.infoAdicional}
                  onChange={(event) => handleFieldChange('infoAdicional', event.target.value)}
                  placeholder="Información adicional"
                  rows={4}
                />
              </div>
              <DialogFooter>
                <Button variant="outline" onClick={closeDialog}>
                  Cancelar
                </Button>
                <Button className="bg-[#f26522] text-white" onClick={handleSaveClient}>
                  {dialogType === 'create' ? 'Agregar' : 'Guardar cambios'}
                </Button>
              </DialogFooter>
            </>
          ) : null}
        </DialogContent>
      </Dialog>

      <Dialog
        open={configDialogOpen}
        onOpenChange={(open: boolean) => {
          if (!open) closeSimConfigDialog()
        }}
      >
        <DialogContent>
          <DialogHeader>
            <DialogTitle>
              {configDialogMode === 'create'
                ? 'Agregar configuración del simulador'
                : 'Editar configuración del simulador'}
            </DialogTitle>
            <DialogDescription>
              Define los parámetros que controlan el simulador mostrado a los usuarios.
            </DialogDescription>
          </DialogHeader>

          <div className="space-y-4">
            <div className="space-y-1">
              <label className="text-xs font-semibold text-slate-600">Tasa de interés mensual (%)</label>
              <Input
                type="number"
                value={configForm.tasaInteresMensual}
                onChange={(event) => handleConfigFormChange('tasaInteresMensual', event.target.value)}
                placeholder="Ej: 1.55"
                min={0}
                step="0.01"
              />
            </div>
            <div className="grid gap-4 md:grid-cols-2">
              <div className="space-y-1">
                <label className="text-xs font-semibold text-slate-600">Monto mínimo</label>
                <Input
                  type="number"
                  value={configForm.montoMinimo}
                  onChange={(event) => handleConfigFormChange('montoMinimo', event.target.value)}
                  placeholder="Ej: 3000000"
                  min={0}
                />
              </div>
              <div className="space-y-1">
                <label className="text-xs font-semibold text-slate-600">Monto máximo</label>
                <Input
                  type="number"
                  value={configForm.montoMaximo}
                  onChange={(event) => handleConfigFormChange('montoMaximo', event.target.value)}
                  placeholder="Ej: 40000000"
                  min={0}
                />
              </div>
            </div>
            <div className="space-y-1">
              <label className="text-xs font-semibold text-slate-600">Plazos disponibles (meses)</label>
              <Input
                value={configForm.plazosDisponibles}
                onChange={(event) => handleConfigFormChange('plazosDisponibles', event.target.value)}
                placeholder="Ej: 12, 24, 36"
              />
              <p className="text-xs text-slate-500">Separa cada plazo con comas.</p>
            </div>
          </div>

          <DialogFooter>
            <Button variant="outline" onClick={closeSimConfigDialog}>
              Cancelar
            </Button>
            <Button className="bg-[#f26522] text-white" onClick={handleSaveSimConfig}>
              {configDialogMode === 'create' ? 'Guardar configuración' : 'Guardar cambios'}
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </div>
  )
}

export const adminRoute = new Route({
  getParentRoute: () => rootRoute,
  path: 'admin',
  component: AdminPage,
})
