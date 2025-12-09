import { useState, type ChangeEvent } from 'react'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select'
import type { ClientRecord } from '@/data/admin-clients'
import type {
  ClientDocumentRecord,
  DocumentType,
  UploadClientDocumentResponse,
} from '@/features/clients/api/documents'
import { useClientDetails } from '@/features/clients/hooks/use-client-details'
import { useClientDocuments } from '@/features/clients/hooks/use-client-documents'
import { useDeleteClientDocument } from '@/features/clients/hooks/use-delete-client-document'
import { useUploadClientDocument } from '@/features/clients/hooks/use-upload-client-document'

const detailTabs = [
  { id: 'info', label: 'Información' },
  { id: 'documents', label: 'Documentos Cliente' },
  { id: 'credits', label: 'Créditos' },
] as const

type DetailTabId = (typeof detailTabs)[number]['id']

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
  const [documentDeletingId, setDocumentDeletingId] = useState<number | null>(null)
  const [deleteSuccessMessage, setDeleteSuccessMessage] = useState<string | null>(null)
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

  const resolveDocumentTypeLabel = (type: DocumentType) =>
    documentTypeOptions.find((option) => option.value === type)?.label ?? type

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
          ) : (
            <div className="py-16 text-center text-sm text-slate-500">
              Aún no hay información disponible para esta sección.
            </div>
          )}
        </div>
      </div>
    </section>
  )
}
