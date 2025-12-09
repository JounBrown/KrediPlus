import { useState, type ChangeEvent } from 'react'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from '@/components/ui/dialog'
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
} from '@/components/ui/dropdown-menu'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select'
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from '@/components/ui/table'
import { MoreHorizontal } from 'lucide-react'
import type { ClientRecord } from '@/data/admin-clients'
import type {
  ClientDocumentRecord,
  DocumentType,
  UploadClientDocumentResponse,
} from '@/features/clients/api/documents'
import type { ClientCreditRecord } from '@/features/clients/api/credits'
import { useClientDetails } from '@/features/clients/hooks/use-client-details'
import { useClientCredits } from '@/features/clients/hooks/use-client-credits'
import { useClientDocuments } from '@/features/clients/hooks/use-client-documents'
import { useCreateClientCredit } from '@/features/clients/hooks/use-create-client-credit'
import { useDeleteClientDocument } from '@/features/clients/hooks/use-delete-client-document'
import { useUpdateClientCredit } from '@/features/clients/hooks/use-update-client-credit'
import { useUploadClientDocument } from '@/features/clients/hooks/use-upload-client-document'

const detailTabs = [
  { id: 'info', label: 'Información' },
  { id: 'documents', label: 'Documentos Cliente' },
  { id: 'credits', label: 'Créditos' },
] as const

type DetailTabId = (typeof detailTabs)[number]['id']

const currencyFormatter = new Intl.NumberFormat('es-CO', {
  style: 'currency',
  currency: 'COP',
  maximumFractionDigits: 0,
})

const documentTypeOptions: { value: DocumentType; label: string; helper: string }[] = [
  { value: 'CEDULA_FRENTE', label: 'Cédula - Frente', helper: 'Foto frontal del documento de identidad.' },
  { value: 'CEDULA_REVERSO', label: 'Cédula - Reverso', helper: 'Foto del reverso del documento de identidad.' },
  { value: 'COMPROBANTE_INGRESOS', label: 'Comprobante de ingresos', helper: 'Desprendibles de nómina o certificaciones.' },
  { value: 'CERTIFICADO_LABORAL', label: 'Certificado laboral', helper: 'Carta laboral vigente con firma.' },
  { value: 'SOLICITUD_CREDITO_FIRMADA', label: 'Solicitud crédito firmada', helper: 'Formato oficial con firma del cliente.' },
  { value: 'PAGARE_FIRMADO', label: 'Pagaré firmado', helper: 'Documento de pagaré con firmas y huellas.' },
  { value: 'COMPROBANTE_DOMICILIO', label: 'Comprobante de domicilio', helper: 'Recibos públicos o certificados de residencia.' },
  { value: 'EXTRACTO_BANCARIO', label: 'Extracto bancario', helper: 'Últimos movimientos bancarios.' },
  { value: 'OTRO', label: 'Otro documento', helper: 'Cualquier soporte adicional relevante.' },
]

const creditStatusOptions = [
  { value: 'EN_ESTUDIO', label: 'En estudio' },
  { value: 'APROBADO', label: 'Aprobado' },
  { value: 'RECHAZADO', label: 'Rechazado' },
  { value: 'DESEMBOLSADO', label: 'Desembolsado' },
  { value: 'AL_DIA', label: 'Al día' },
  { value: 'EN_MORA', label: 'En mora' },
  { value: 'PAGADO', label: 'Pagado' },
] as const

type ClientDetailViewProps = {
  client: ClientRecord
  onBack: () => void
  onEdit: (client: ClientRecord) => void
}

export function ClientDetailView({ client, onBack, onEdit }: ClientDetailViewProps) {
  const [activeTab, setActiveTab] = useState<DetailTabId>('info')
  const [documentType, setDocumentType] = useState<DocumentType>(documentTypeOptions[0].value)
  const [creditIdInput, setCreditIdInput] = useState('')
  const [selectedFile, setSelectedFile] = useState<File | null>(null)
  const [fileInputKey, setFileInputKey] = useState(0)
  const [formError, setFormError] = useState<string | null>(null)
  const [lastUploadResult, setLastUploadResult] = useState<UploadClientDocumentResponse | null>(null)
  const [creditAmount, setCreditAmount] = useState('')
  const [creditTerm, setCreditTerm] = useState('')
  const [creditRate, setCreditRate] = useState('')
  const [creditDisbursementDate, setCreditDisbursementDate] = useState('')
  const [creditStatus, setCreditStatus] = useState<(typeof creditStatusOptions)[number]['value']>('EN_ESTUDIO')
  const [creditFormError, setCreditFormError] = useState<string | null>(null)
  const [creditSuccessMessage, setCreditSuccessMessage] = useState<string | null>(null)
  const [creditDialogOpen, setCreditDialogOpen] = useState(false)
  const [creditDialogMode, setCreditDialogMode] = useState<'create' | 'edit'>('create')
  const [creditEditingId, setCreditEditingId] = useState<number | null>(null)
  const [documentDeletingId, setDocumentDeletingId] = useState<number | null>(null)
  const [deleteSuccessMessage, setDeleteSuccessMessage] = useState<string | null>(null)

  const resetCreditForm = () => {
    setCreditAmount('')
    setCreditTerm('')
    setCreditRate('')
    setCreditDisbursementDate('')
    setCreditFormError(null)
    setCreditStatus('EN_ESTUDIO')
    setCreditEditingId(null)
  }
  const {
    data: remoteClient,
    isFetching,
    error,
  } = useClientDetails(client.id, { enabled: true })
  const resolvedClient = remoteClient ?? client
  const {
    data: clientDocuments,
    isFetching: loadingDocuments,
    error: clientDocumentsError,
  } = useClientDocuments(resolvedClient.id, { enabled: activeTab === 'documents' })
  const {
    data: clientCredits,
    isFetching: fetchingCredits,
    isLoading: loadingCredits,
    error: clientCreditsError,
  } = useClientCredits(resolvedClient.id, { enabled: activeTab === 'credits' })
  const uploadDocumentMutation = useUploadClientDocument({
    onSuccess: (result) => {
      setLastUploadResult(result)
      setSelectedFile(null)
      setCreditIdInput('')
      setFormError(null)
      setFileInputKey((prev) => prev + 1)
    },
    onError: () => {
      setLastUploadResult(null)
    },
  })
  const createCreditMutation = useCreateClientCredit({
    onSuccess: (credit) => {
      setCreditSuccessMessage(`Crédito #${credit.id} creado correctamente.`)
      resetCreditForm()
      setCreditDialogOpen(false)
    },
    onError: () => {
      setCreditSuccessMessage(null)
    },
  })
  const updateCreditMutation = useUpdateClientCredit({
    onSuccess: (credit) => {
      setCreditSuccessMessage(`Crédito #${credit.id} actualizado correctamente.`)
      resetCreditForm()
      setCreditDialogOpen(false)
    },
    onError: () => {
      setCreditSuccessMessage(null)
    },
  })
  const deleteDocumentMutation = useDeleteClientDocument({
    onSuccess: (response) => {
      setDeleteSuccessMessage(response.message)
      setDocumentDeletingId(null)
    },
    onError: () => {
      setDocumentDeletingId(null)
      setDeleteSuccessMessage(null)
    },
  })

  const handleFileChange = (event: ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0] ?? null
    setSelectedFile(file)
    setLastUploadResult(null)
    setFormError(null)
  }

  const handleUploadDocument = async () => {
    if (!selectedFile) {
      setFormError('Selecciona un archivo para continuar.')
      return
    }

    const normalizedCreditId = creditIdInput.trim()
    if (normalizedCreditId && Number.isNaN(Number(normalizedCreditId))) {
      setFormError('El ID de crédito debe ser numérico.')
      return
    }

    setFormError(null)
    setLastUploadResult(null)

    try {
      await uploadDocumentMutation.mutateAsync({
        file: selectedFile,
        documentType,
        clientId: resolvedClient.id,
        creditId: normalizedCreditId ? Number(normalizedCreditId) : undefined,
      })
    } catch {
      /* El estado de error se maneja por React Query */
    }
  }

  const handleDeleteDocument = async (doc: ClientDocumentRecord) => {
    const confirmed = window.confirm(`¿Eliminar el documento "${doc.fileName}"?`)
    if (!confirmed) {
      return
    }

    setDeleteSuccessMessage(null)
    setDocumentDeletingId(doc.id)

    try {
      await deleteDocumentMutation.mutateAsync({
        clientId: resolvedClient.id,
        documentId: doc.id,
      })
    } catch {
      /* El estado de error se maneja por React Query */
    }
  }

  const handleCreditDialogOpenChange = (open: boolean) => {
    setCreditDialogOpen(open)
    if (!open) {
      resetCreditForm()
      setCreditFormError(null)
      createCreditMutation.reset()
      updateCreditMutation.reset()
      setCreditDialogMode('create')
    }
  }

  const openCreateCreditDialog = () => {
    resetCreditForm()
    setCreditDialogMode('create')
    setCreditSuccessMessage(null)
    setCreditDialogOpen(true)
  }

  const handleEditCredit = (credit: ClientCreditRecord) => {
    setCreditDialogMode('edit')
    setCreditEditingId(credit.id)
    setCreditAmount(String(credit.montoAprobado))
    setCreditTerm(String(credit.plazoMeses))
    setCreditRate(String(credit.tasaInteres))
    setCreditStatus(credit.estado as (typeof creditStatusOptions)[number]['value'])
    setCreditDisbursementDate(credit.fechaDesembolso ?? '')
    setCreditFormError(null)
    setCreditSuccessMessage(null)
    setCreditDialogOpen(true)
  }

  const handleSubmitCredit = async () => {
    const parsedAmount = Number(creditAmount)
    if (!creditAmount || Number.isNaN(parsedAmount) || parsedAmount < 100000 || parsedAmount > 100000000) {
      setCreditFormError('El monto aprobado debe estar entre 100.000 y 100.000.000.')
      return
    }

    const parsedTerm = Number(creditTerm)
    if (!creditTerm || Number.isNaN(parsedTerm) || parsedTerm < 1 || parsedTerm > 120) {
      setCreditFormError('El plazo debe estar entre 1 y 120 meses.')
      return
    }

    const parsedRate = Number(creditRate)
    if (!creditRate || Number.isNaN(parsedRate) || parsedRate < 0 || parsedRate > 100) {
      setCreditFormError('La tasa de interés debe estar entre 0% y 100%.')
      return
    }

    setCreditFormError(null)
    setCreditSuccessMessage(null)

    try {
      const basePayload = {
        monto_aprobado: parsedAmount,
        plazo_meses: parsedTerm,
        tasa_interes: parsedRate,
        estado: creditStatus,
      }
      const createPayload = creditDisbursementDate
        ? { ...basePayload, fecha_desembolso: creditDisbursementDate }
        : basePayload
      const updatePayload = { ...basePayload, fecha_desembolso: creditDisbursementDate || null }

      if (creditDialogMode === 'edit' && creditEditingId) {
        await updateCreditMutation.mutateAsync({
          clientId: resolvedClient.id,
          creditId: creditEditingId,
          payload: updatePayload,
        })
      } else {
        await createCreditMutation.mutateAsync({
          clientId: resolvedClient.id,
          payload: createPayload,
        })
      }
    } catch {
      /* El estado de error se maneja dentro de React Query */
    }
  }

  const isSavingCredit = createCreditMutation.isPending || updateCreditMutation.isPending

  const resolveDocumentTypeLabel = (type: DocumentType) =>
    documentTypeOptions.find((option) => option.value === type)?.label ?? type

  const formatCurrency = (value: number) => currencyFormatter.format(value)

  const formatDateTime = (value: string) =>
    new Date(value).toLocaleString('es-CO', { dateStyle: 'medium', timeStyle: 'short' })

  const formatCreditStatus = (status: string) =>
    status
      .toLowerCase()
      .split('_')
      .map((segment) => segment.charAt(0).toUpperCase() + segment.slice(1))
      .join(' ')

  const statusBadgeClasses: Record<string, string> = {
    EN_ESTUDIO: 'bg-amber-50 text-amber-700 border border-amber-100',
    APROBADO: 'bg-emerald-50 text-emerald-700 border border-emerald-100',
    RECHAZADO: 'bg-red-50 text-red-700 border border-red-100',
  }

  const getCreditStatusBadgeClass = (status: string) =>
    statusBadgeClasses[status] ?? 'bg-slate-100 text-slate-600 border border-slate-200'

  const infoItems = [
    { label: 'Nombre Completo', value: resolvedClient.nombreCompleto },
    { label: 'Cédula', value: resolvedClient.cedula },
    { label: 'Teléfono', value: resolvedClient.telefono },
    { label: 'Email', value: resolvedClient.email },
    { label: 'Dirección', value: resolvedClient.direccion },
    { label: 'Estado', value: 'Activo' },
    {
      label: 'Fecha de nacimiento',
      value: resolvedClient.fechaNacimiento
        ? new Date(resolvedClient.fechaNacimiento).toLocaleDateString('es-CO')
        : 'Sin dato',
    },
    {
      label: 'Creado el',
      value: resolvedClient.createdAt
        ? new Date(resolvedClient.createdAt).toLocaleDateString('es-CO')
        : 'Sin dato',
    },
  ]

  return (
    <>
      <section className="space-y-6">
      <button
        type="button"
        onClick={onBack}
        className="text-sm font-semibold text-[#0d2f62] transition hover:text-[#f26522]"
      >
        &lt; Volver a la lista
      </button>

      <div className="flex flex-wrap items-start justify-between gap-4">
        <div>
          <h2 className="text-3xl font-extrabold text-[#0d2f62]">{resolvedClient.nombreCompleto}</h2>
          <p className="text-sm text-slate-500">C.C. {resolvedClient.cedula}</p>
        </div>
        <Button variant="outline" className="border-[#0d2f62] text-[#0d2f62]" onClick={() => onEdit(resolvedClient)}>
          Editar
        </Button>
      </div>

      <div className="overflow-hidden rounded-3xl border border-slate-100 bg-white shadow-sm">
        <div className="flex flex-wrap gap-3 border-b border-slate-100 bg-slate-50 px-6 py-3 text-sm font-semibold text-slate-500">
          {detailTabs.map((tab) => (
            <button
              key={tab.id}
              type="button"
              onClick={() => setActiveTab(tab.id)}
              className={`rounded-full px-4 py-1 transition ${
                activeTab === tab.id ? 'bg-white text-[#0d2f62] shadow' : 'hover:text-[#0d2f62]'
              }`}
            >
              {tab.label}
            </button>
          ))}
        </div>

        <div className="space-y-6 px-8 py-6">
          {activeTab === 'info' ? (
            <div className="space-y-6">
              <div>
                <p className="text-lg font-semibold text-[#f26522]">Detalles del Cliente</p>
                <p className="text-sm text-slate-500">
                  Información general registrada para este cliente.
                </p>
              </div>
              {isFetching && <p className="text-sm text-slate-500">Actualizando datos...</p>}
              {error && <p className="text-sm text-red-600">{error.message}</p>}
              <div className="grid gap-6 md:grid-cols-2">
                {infoItems.map((item) => (
                  <div key={item.label} className="rounded-2xl border border-slate-100 bg-[#f8fafc] p-5">
                    <p className="text-xs font-semibold uppercase text-slate-500">{item.label}</p>
                    <p className="text-base font-semibold text-[#0d2f62]">{item.value}</p>
                  </div>
                ))}
              </div>
              {resolvedClient.infoAdicional && (
                <div className="rounded-2xl border border-slate-100 bg-white p-5">
                  <p className="text-xs font-semibold uppercase text-slate-500">Notas</p>
                  <p className="text-sm text-slate-700">{resolvedClient.infoAdicional}</p>
                </div>
              )}
            </div>
          ) : activeTab === 'documents' ? (
            <div className="space-y-6">
              <div>
                <p className="text-lg font-semibold text-[#f26522]">Documentos del cliente</p>
                <p className="text-sm text-slate-500">
                  Carga los soportes requeridos directamente al expediente digital.
                </p>
              </div>

              <div className="space-y-5 rounded-2xl border border-slate-100 bg-[#f8fafc] p-6">
                <div className="grid gap-4 md:grid-cols-2">
                  <div className="space-y-2">
                    <Label htmlFor="document-type" className="text-xs font-semibold uppercase text-slate-500">
                      Tipo de documento
                    </Label>
                    <Select value={documentType} onValueChange={(value) => setDocumentType(value as DocumentType)}>
                      <SelectTrigger id="document-type" className="bg-white">
                        <SelectValue placeholder="Selecciona un tipo" />
                      </SelectTrigger>
                      <SelectContent>
                        {documentTypeOptions.map((option) => (
                          <SelectItem key={option.value} value={option.value}>
                            {option.label}
                          </SelectItem>
                        ))}
                      </SelectContent>
                    </Select>
                    <p className="text-xs text-slate-500">
                      {documentTypeOptions.find((option) => option.value === documentType)?.helper}
                    </p>
                  </div>

                  <div className="space-y-2">
                    <Label htmlFor="credit-id" className="text-xs font-semibold uppercase text-slate-500">
                      ID de crédito (opcional)
                    </Label>
                    <Input
                      id="credit-id"
                      type="number"
                      min="0"
                      value={creditIdInput}
                      onChange={(event) => setCreditIdInput(event.target.value)}
                      placeholder="1234"
                      className="bg-white"
                    />
                    <p className="text-xs text-slate-500">Solo si el documento pertenece a un crédito específico.</p>
                  </div>
                </div>

                <div className="space-y-2">
                  <Label htmlFor="client-document-file" className="text-xs font-semibold uppercase text-slate-500">
                    Selecciona el archivo
                  </Label>
                  <Input
                    key={fileInputKey}
                    id="client-document-file"
                    type="file"
                    accept="application/pdf,image/*"
                    onChange={handleFileChange}
                    className="bg-white"
                  />
                  <p className="text-xs text-slate-500">
                    {selectedFile
                      ? `Archivo seleccionado: ${selectedFile.name}`
                      : 'Formatos aceptados: PDF, JPG o PNG.'}
                  </p>
                </div>

                {formError && <p className="text-sm text-red-600">{formError}</p>}
                {uploadDocumentMutation.error && (
                  <p className="text-sm text-red-600">{uploadDocumentMutation.error.message}</p>
                )}
                {lastUploadResult && (
                  <div className="rounded-2xl border border-emerald-200 bg-emerald-50 px-4 py-3 text-sm text-emerald-800">
                    <p className="font-semibold">Archivo subido correctamente</p>
                    <p className="break-all text-xs text-emerald-900">{lastUploadResult.path}</p>
                  </div>
                )}

                <div className="flex flex-wrap items-center gap-3">
                  <Button
                    className="bg-[#0d2f62] text-white hover:bg-[#0b2349]"
                    onClick={handleUploadDocument}
                    disabled={uploadDocumentMutation.isPending}
                  >
                    {uploadDocumentMutation.isPending ? 'Subiendo...' : 'Subir documento'}
                  </Button>
                  <p className="text-xs text-slate-500">
                    El archivo se guardará automáticamente en el expediente digital.
                  </p>
                </div>
              </div>

              <div className="rounded-2xl border border-slate-100 bg-white p-6">
                <div className="flex flex-wrap items-center justify-between gap-4">
                  <div>
                    <p className="text-base font-semibold text-[#0d2f62]">Historial de documentos</p>
                    <p className="text-xs text-slate-500">Archivos que ya fueron cargados por el equipo.</p>
                  </div>
                  <span className="text-xs font-semibold uppercase text-slate-500">
                    {clientDocuments?.length ?? 0} documentos
                  </span>
                </div>

                {loadingDocuments ? (
                  <p className="mt-4 text-sm text-slate-500">Cargando documentos...</p>
                ) : clientDocumentsError ? (
                  <p className="mt-4 text-sm text-red-600">{clientDocumentsError.message}</p>
                ) : clientDocuments && clientDocuments.length > 0 ? (
                  <div className="mt-4 space-y-4">
                    {deleteDocumentMutation.error && (
                      <p className="text-sm text-red-600">{deleteDocumentMutation.error.message}</p>
                    )}
                    {deleteSuccessMessage && (
                      <div className="rounded-2xl border border-emerald-200 bg-emerald-50 px-4 py-3 text-sm text-emerald-800">
                        {deleteSuccessMessage}
                      </div>
                    )}
                    {clientDocuments.map((doc) => (
                      <div
                        key={doc.id}
                        className="flex flex-col gap-3 rounded-2xl border border-slate-100 bg-[#f8fafc] p-4 md:flex-row md:items-center md:justify-between"
                      >
                        <div className="space-y-1">
                          <p className="text-sm font-semibold text-[#0d2f62]">{doc.fileName}</p>
                          <p className="text-xs text-slate-500">
                            Subido el{' '}
                            {new Date(doc.createdAt).toLocaleString('es-CO', {
                              dateStyle: 'medium',
                              timeStyle: 'short',
                            })}
                          </p>
                          <p className="text-xs text-slate-500">
                            {doc.creditId ? `Crédito #${doc.creditId}` : 'Sin crédito asociado'}
                          </p>
                          <p className="break-all text-xs text-slate-400">{doc.storagePath}</p>
                        </div>
                        <div className="flex flex-wrap items-center gap-3">
                          <span className="rounded-full bg-white px-3 py-1 text-xs font-semibold text-[#0d2f62]">
                            {resolveDocumentTypeLabel(doc.documentType)}
                          </span>
                          <Button
                            asChild
                            size="sm"
                            variant="outline"
                            className="border-[#f26522] text-[#f26522] hover:bg-[#f26522]/10"
                          >
                            <a href={doc.fileUrl} target="_blank" rel="noreferrer">
                              Ver archivo
                            </a>
                          </Button>
                          <Button
                            size="sm"
                            variant="ghost"
                            className="text-red-600 hover:bg-red-50 hover:text-red-700"
                            onClick={() => handleDeleteDocument(doc)}
                            disabled={Boolean(documentDeletingId && documentDeletingId === doc.id && deleteDocumentMutation.isPending)}
                          >
                            {documentDeletingId === doc.id && deleteDocumentMutation.isPending
                              ? 'Eliminando...'
                              : 'Eliminar'}
                          </Button>
                        </div>
                      </div>
                    ))}
                  </div>
                ) : (
                  <p className="mt-4 text-sm text-slate-500">Aún no hay documentos cargados.</p>
                )}
              </div>

              <div className="rounded-2xl border border-slate-100 bg-white p-6">
                <p className="text-xs font-semibold uppercase text-slate-500">Tipos soportados</p>
                <div className="mt-4 grid gap-4 md:grid-cols-2">
                  {documentTypeOptions.map((option) => (
                    <div key={option.value} className="rounded-xl border border-slate-100 bg-[#f8fafc] p-4">
                      <p className="text-sm font-semibold text-[#0d2f62]">{option.label}</p>
                      <p className="text-xs text-slate-500">{option.helper}</p>
                    </div>
                  ))}
                </div>
              </div>
            </div>
          ) : activeTab === 'credits' ? (
            <div className="space-y-6">
              <div className="flex flex-wrap items-center justify-between gap-4">
                <div>
                  <p className="text-lg font-semibold text-[#f26522]">Créditos del cliente</p>
                  <p className="text-sm text-slate-500">
                    Consulta el historial de créditos aprobados y registra nuevos desembolsos cuando sea necesario.
                  </p>
                </div>
                <Button className="bg-[#f26522] text-white hover:bg-[#d85314]" onClick={openCreateCreditDialog}>
                  Crear crédito
                </Button>
              </div>

              <div className="overflow-hidden rounded-2xl border border-slate-100 bg-white">
                {creditSuccessMessage && (
                  <div className="border-b border-emerald-100 bg-emerald-50 px-6 py-3 text-sm text-emerald-800">
                    {creditSuccessMessage}
                  </div>
                )}
                {loadingCredits && !clientCredits ? (
                  <div className="py-10 text-center text-sm text-slate-500">Cargando créditos...</div>
                ) : clientCreditsError ? (
                  <div className="py-10 text-center text-sm text-red-600">{clientCreditsError.message}</div>
                ) : clientCredits && clientCredits.length > 0 ? (
                  <div className="overflow-x-auto">
                    {fetchingCredits && (
                      <p className="px-6 py-2 text-xs text-slate-500">Actualizando información...</p>
                    )}
                    <Table>
                      <TableHeader className="bg-slate-50">
                        <TableRow>
                          <TableHead className="text-xs font-bold uppercase text-slate-500">Monto aprobado</TableHead>
                          <TableHead className="text-xs font-bold uppercase text-slate-500">Plazo</TableHead>
                          <TableHead className="text-xs font-bold uppercase text-slate-500">Tasa</TableHead>
                          <TableHead className="text-xs font-bold uppercase text-slate-500">Estado</TableHead>
                          <TableHead className="text-xs font-bold uppercase text-slate-500">Desembolso</TableHead>
                          <TableHead className="text-xs font-bold uppercase text-slate-500">Creado</TableHead>
                          <TableHead>
                            <span className="sr-only">Acciones</span>
                          </TableHead>
                        </TableRow>
                      </TableHeader>
                      <TableBody>
                        {clientCredits.map((credit) => (
                          <TableRow key={credit.id} className="text-sm">
                            <TableCell className="font-semibold text-[#0d2f62]">{formatCurrency(credit.montoAprobado)}</TableCell>
                            <TableCell>{credit.plazoMeses} meses</TableCell>
                            <TableCell>{`${credit.tasaInteres.toFixed(2)}%`}</TableCell>
                            <TableCell>
                              <Badge className={getCreditStatusBadgeClass(credit.estado)}>
                                {formatCreditStatus(credit.estado)}
                              </Badge>
                            </TableCell>
                            <TableCell>
                              {credit.fechaDesembolso
                                ? new Date(credit.fechaDesembolso).toLocaleDateString('es-CO')
                                : 'Pendiente'}
                            </TableCell>
                            <TableCell>{formatDateTime(credit.createdAt)}</TableCell>
                            <TableCell className="text-right">
                              <DropdownMenu>
                                <DropdownMenuTrigger asChild>
                                  <button
                                    className="rounded-full p-1.5 text-slate-500 transition hover:bg-slate-100 hover:text-slate-700"
                                    aria-label="Más acciones"
                                  >
                                    <MoreHorizontal className="h-5 w-5" />
                                  </button>
                                </DropdownMenuTrigger>
                                <DropdownMenuContent align="end">
                                  <DropdownMenuItem onClick={() => handleEditCredit(credit)}>
                                    Editar crédito
                                  </DropdownMenuItem>
                                </DropdownMenuContent>
                              </DropdownMenu>
                            </TableCell>
                          </TableRow>
                        ))}
                      </TableBody>
                    </Table>
                  </div>
                ) : (
                  <div className="py-10 text-center text-sm text-slate-500">
                    Aún no hay créditos registrados para este cliente.
                  </div>
                )}
              </div>
            </div>
          ) : (
            <div className="py-16 text-center text-sm text-slate-500">
              Aún no hay información disponible para esta sección.
            </div>
          )}
        </div>
      </div>
    </section>

    <Dialog open={creditDialogOpen} onOpenChange={handleCreditDialogOpenChange}>
      <DialogContent className="max-w-lg">
        <DialogHeader>
          <DialogTitle>
            {creditDialogMode === 'edit' ? 'Actualizar crédito' : 'Registrar nuevo crédito'}
          </DialogTitle>
          <DialogDescription>
            {creditDialogMode === 'edit'
              ? 'Modifica los datos del crédito seleccionado. Los cambios se reflejan inmediatamente.'
              : 'Completa los datos principales del crédito. Se creará con estado EN_ESTUDIO por defecto.'}
          </DialogDescription>
        </DialogHeader>

        <div className="space-y-4">
          <div className="space-y-2">
            <Label htmlFor="modal-credit-amount" className="text-xs font-semibold uppercase text-slate-500">
              Monto aprobado
            </Label>
            <Input
              id="modal-credit-amount"
              type="number"
              min="100000"
              max="100000000"
              step="10000"
              value={creditAmount}
              onChange={(event) => {
                setCreditAmount(event.target.value)
                setCreditFormError(null)
                setCreditSuccessMessage(null)
              }}
              placeholder="5000000"
            />
            <p className="text-xs text-slate-500">Entre 100.000 y 100.000.000 COP.</p>
          </div>

          <div className="space-y-2">
            <Label htmlFor="modal-credit-term" className="text-xs font-semibold uppercase text-slate-500">
              Plazo (meses)
            </Label>
            <Input
              id="modal-credit-term"
              type="number"
              min="1"
              max="120"
              value={creditTerm}
              onChange={(event) => {
                setCreditTerm(event.target.value)
                setCreditFormError(null)
                setCreditSuccessMessage(null)
              }}
              placeholder="36"
            />
            <p className="text-xs text-slate-500">Definir un plazo entre 1 y 120 meses.</p>
          </div>

          <div className="space-y-2">
            <Label htmlFor="modal-credit-rate" className="text-xs font-semibold uppercase text-slate-500">
              Tasa de interés (% E.A.)
            </Label>
            <Input
              id="modal-credit-rate"
              type="number"
              min="0"
              max="100"
              step="0.01"
              value={creditRate}
              onChange={(event) => {
                setCreditRate(event.target.value)
                setCreditFormError(null)
                setCreditSuccessMessage(null)
              }}
              placeholder="18.5"
            />
            <p className="text-xs text-slate-500">Ingresa la tasa aprobada para este crédito.</p>
          </div>

          <div className="space-y-2">
            <Label htmlFor="modal-credit-status" className="text-xs font-semibold uppercase text-slate-500">
              Estado
            </Label>
            <Select
              value={creditStatus}
              onValueChange={(value) => {
                setCreditStatus(value as (typeof creditStatusOptions)[number]['value'])
                setCreditFormError(null)
              }}
            >
              <SelectTrigger id="modal-credit-status">
                <SelectValue placeholder="Selecciona un estado" />
              </SelectTrigger>
              <SelectContent>
                {creditStatusOptions.map((option) => (
                  <SelectItem key={option.value} value={option.value}>
                    {option.label}
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
          </div>

          <div className="space-y-2">
            <Label htmlFor="modal-credit-disbursement" className="text-xs font-semibold uppercase text-slate-500">
              Fecha de desembolso (opcional)
            </Label>
            <Input
              id="modal-credit-disbursement"
              type="date"
              value={creditDisbursementDate}
              onChange={(event) => {
                setCreditDisbursementDate(event.target.value)
                setCreditFormError(null)
                setCreditSuccessMessage(null)
              }}
            />
            <p className="text-xs text-slate-500">Déjalo en blanco si aún no ha sido desembolsado.</p>
          </div>

          {creditFormError && <p className="text-sm text-red-600">{creditFormError}</p>}
          {(createCreditMutation.error || updateCreditMutation.error) && (
            <p className="text-sm text-red-600">
              {createCreditMutation.error?.message || updateCreditMutation.error?.message}
            </p>
          )}
        </div>

        <DialogFooter className="gap-2 sm:gap-3">
          <Button
            variant="outline"
            onClick={() => handleCreditDialogOpenChange(false)}
            disabled={isSavingCredit}
            className="border-slate-200 text-slate-600 hover:bg-[#f8fafc]"
          >
            Cancelar
          </Button>
          <Button
            className={`text-white ${
              creditDialogMode === 'edit'
                ? 'bg-[#f26522] hover:bg-[#d85314]'
                : 'bg-[#0d2f62] hover:bg-[#0b2349]'
            }`}
            onClick={handleSubmitCredit}
            disabled={isSavingCredit}
          >
            {isSavingCredit
              ? creditDialogMode === 'edit'
                ? 'Actualizando...'
                : 'Registrando...'
              : creditDialogMode === 'edit'
                ? 'Actualizar crédito'
                : 'Guardar crédito'}
          </Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
    </>
  )
}
