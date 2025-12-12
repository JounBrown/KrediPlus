import { useCallback, useMemo, useRef, useState } from 'react'
import { RefreshCcw, Trash2, UploadCloud } from 'lucide-react'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from '@/components/ui/table'
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from '@/components/ui/dialog'
import { useRagDocuments } from '../hooks/use-rag-documents'
import { useUploadRagDocument } from '../hooks/use-upload-rag-document'
import { useDeleteRagDocument } from '../hooks/use-delete-rag-document'
import type { RagDocument, RagProcessingStatus } from '../api/rag-documents'

type UploadPanelProps = {
  onBackToRequests: () => void
}

const STATUS_META: Record<
  RagProcessingStatus | 'default',
  { label: string; className: string }
> = {
  completed: {
    label: 'Procesado',
    className: 'border-emerald-200 bg-emerald-50 text-emerald-700',
  },
  processing: {
    label: 'Procesando',
    className: 'border-sky-200 bg-sky-50 text-sky-700',
  },
  pending: {
    label: 'Pendiente',
    className: 'border-amber-200 bg-amber-50 text-amber-700',
  },
  queued: {
    label: 'En cola',
    className: 'border-amber-200 bg-amber-50 text-amber-700',
  },
  failed: {
    label: 'Con errores',
    className: 'border-rose-200 bg-rose-50 text-rose-700',
  },
  unknown: {
    label: 'Desconocido',
    className: 'border-slate-200 bg-slate-100 text-slate-600',
  },
  default: {
    label: 'Desconocido',
    className: 'border-slate-200 bg-slate-100 text-slate-600',
  },
}

function renderStatus(status: RagProcessingStatus) {
  const meta = STATUS_META[status] ?? STATUS_META.default
  return (
    <Badge variant="outline" className={meta.className}>
      {meta.label}
    </Badge>
  )
}

const SUPPORTED_EXTENSIONS = ['pdf', 'doc', 'docx']
const ACCEPTED_MIME_TYPES = '.pdf,.doc,.docx,application/pdf,application/msword,application/vnd.openxmlformats-officedocument.wordprocessingml.document'

export function UploadPanel({ onBackToRequests }: UploadPanelProps) {
  const {
    data: ragDocuments = [],
    isLoading,
    isError,
    error,
    refetch,
    isFetching,
  } = useRagDocuments()
  const [actionSuccessMessage, setActionSuccessMessage] = useState<string | null>(null)
  const [validationError, setValidationError] = useState<string | null>(null)
  const fileInputRef = useRef<HTMLInputElement | null>(null)
  const [documentToDelete, setDocumentToDelete] = useState<RagDocument | null>(null)
  const [deleteDialogOpen, setDeleteDialogOpen] = useState(false)
  const {
    mutate: uploadDocument,
    isPending: isUploading,
    error: uploadError,
    reset: resetUpload,
  } = useUploadRagDocument({
    onSuccess: (result) => {
      setActionSuccessMessage(result.message || 'Documento cargado correctamente.')
    },
    onError: () => {
      setActionSuccessMessage(null)
    },
  })
  const {
    mutate: deleteDocument,
    isPending: isDeleting,
    error: deleteError,
    reset: resetDelete,
  } = useDeleteRagDocument({
    onSuccess: (result) => {
      setActionSuccessMessage(result.message || 'Documento eliminado correctamente.')
      setDocumentToDelete(null)
      setDeleteDialogOpen(false)
    },
    onError: () => {
      setActionSuccessMessage(null)
    },
  })
  const createdAtFormatter = useMemo(
    () =>
      new Intl.DateTimeFormat('es-CO', {
        dateStyle: 'medium',
        timeStyle: 'short',
      }),
    [],
  )

  const processFiles = useCallback(
    (files: FileList | null) => {
      if (!files?.length) {
        return
      }
      const file = files[0]
      const extension = file.name.split('.').pop()?.toLowerCase() ?? ''
      if (!SUPPORTED_EXTENSIONS.includes(extension)) {
        setValidationError('Formato no soportado. Usa PDF, DOC o DOCX.')
        return
      }
      setValidationError(null)
      setActionSuccessMessage(null)
      resetUpload()
      uploadDocument(file)
      if (fileInputRef.current) {
        fileInputRef.current.value = ''
      }
    },
    [resetUpload, uploadDocument],
  )

  const openDeleteDialog = useCallback(
    (document: RagDocument) => {
      setDocumentToDelete(document)
      setDeleteDialogOpen(true)
      setActionSuccessMessage(null)
      resetDelete()
    },
    [resetDelete],
  )

  const handleDeleteConfirm = useCallback(() => {
    if (!documentToDelete) {
      return
    }
    deleteDocument(documentToDelete.id)
  }, [deleteDocument, documentToDelete])

  return (
    <section className="space-y-8">
      <div className="flex flex-wrap items-center justify-between gap-4">
        <div>
          <p className="text-lg font-semibold text-[#0d2f62]">Carga de Documentos</p>
          <p className="text-sm text-slate-500">
            Arrastra archivos PDF o DOCX para añadir soportes.
          </p>
        </div>
        <Button className="bg-[#0d2f62] text-white hover:bg-[#0b2772]" onClick={onBackToRequests}>
          Ver solicitudes
        </Button>
      </div>

      <div
        className="rounded-3xl border-2 border-dashed border-slate-300 bg-slate-50 px-6 py-12 text-center"
        onDragOver={(event) => event.preventDefault()}
        onDrop={(event) => {
          event.preventDefault()
          processFiles(event.dataTransfer.files)
        }}
      >
        <input
          ref={fileInputRef}
          type="file"
          accept={ACCEPTED_MIME_TYPES}
          className="sr-only"
          aria-label="Seleccionar archivo para el chatbot"
          onChange={(event) => processFiles(event.target.files)}
        />
        <UploadCloud className="mx-auto h-10 w-10 text-[#0d2f62]" />
        <p className="mt-4 text-base font-semibold text-[#0d2f62]">
          Arrastra y suelta archivos PDF, DOC o DOCX aquí
        </p>
        <p className="text-sm text-slate-500">o haz clic para seleccionar archivos</p>
        <Button
          variant="outline"
          className="mt-6 border-[#0d2f62] text-[#0d2f62] hover:bg-white"
          onClick={() => fileInputRef.current?.click()}
          disabled={isUploading}
        >
          {isUploading ? 'Procesando...' : 'Seleccionar archivos'}
        </Button>
        <p className="mt-3 text-xs uppercase tracking-wide text-slate-400">
          Formatos soportados: PDF, DOC, DOCX
        </p>
        {isUploading && (
          <p className="mt-4 text-sm font-semibold text-sky-700">
            Subiendo y procesando documento...
          </p>
        )}
        {validationError && (
          <p className="mt-2 text-sm text-red-600">{validationError}</p>
        )}
        {uploadError && (
          <p className="mt-2 text-sm text-red-600">{uploadError.message}</p>
        )}
        {actionSuccessMessage && !uploadError && (
          <p className="mt-2 text-sm text-emerald-600">{actionSuccessMessage}</p>
        )}
      </div>

      <div className="rounded-3xl border border-slate-100 bg-white p-6 shadow-sm">
        <div className="flex flex-wrap items-start justify-between gap-4">
          <div>
            <p className="text-lg font-semibold text-[#0d2f62]">Documentos del chatbot</p>
            <p className="text-sm text-slate-500">
              Seguimiento del estado de procesamiento y cobertura del contexto RAG.
            </p>
          </div>
          <Button
            variant="outline"
            size="sm"
            className="gap-2 border-slate-200 text-[#0d2f62]"
            onClick={() => refetch()}
            disabled={isFetching}
          >
            <RefreshCcw className="h-4 w-4" />
            {isFetching ? 'Actualizando...' : 'Actualizar'}
          </Button>
        </div>

        <div className="mt-6 overflow-hidden rounded-2xl border border-slate-100">
          <Table>
            <TableHeader className="bg-slate-50">
              <TableRow>
                <TableHead className="text-xs font-bold uppercase text-slate-500">Documento</TableHead>
                <TableHead className="text-xs font-bold uppercase text-slate-500">Estado</TableHead>
                <TableHead className="text-xs font-bold uppercase text-slate-500">Chunks</TableHead>
                <TableHead className="text-xs font-bold uppercase text-slate-500">Registrado</TableHead>
                <TableHead>
                  <span className="sr-only">Acciones</span>
                </TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {isLoading ? (
                <TableRow>
                  <TableCell colSpan={4} className="py-6 text-center text-sm text-slate-500">
                    Cargando documentos...
                  </TableCell>
                </TableRow>
              ) : isError ? (
                <TableRow>
                  <TableCell colSpan={4} className="py-6 text-center text-sm text-red-600">
                    {error?.message || 'No fue posible cargar los documentos.'}
                  </TableCell>
                </TableRow>
              ) : ragDocuments.length === 0 ? (
                <TableRow>
                  <TableCell colSpan={4} className="py-6 text-center text-sm text-slate-500">
                    Aún no has cargado documentos para el chatbot.
                  </TableCell>
                </TableRow>
              ) : (
                ragDocuments.map((document) => (
                  <TableRow key={document.id} className="text-sm">
                    <TableCell>
                      <p className="font-semibold text-[#0d2f62]">{document.filename}</p>
                      <p className="text-xs text-slate-500">{document.storageUrl}</p>
                    </TableCell>
                    <TableCell>{renderStatus(document.processingStatus)}</TableCell>
                    <TableCell className="font-semibold text-slate-700">
                      {document.chunksCount.toLocaleString('es-CO')}
                    </TableCell>
                    <TableCell className="text-slate-600">
                      {document.createdAt ? createdAtFormatter.format(new Date(document.createdAt)) : 'Sin fecha'}
                    </TableCell>
                    <TableCell className="text-right">
                      <Button
                        variant="ghost"
                        size="icon"
                        className="text-slate-400 hover:bg-rose-50 hover:text-rose-600"
                        onClick={() => openDeleteDialog(document)}
                        disabled={isDeleting}
                        aria-label={`Eliminar ${document.filename}`}
                      >
                        <Trash2 className="h-4 w-4" />
                      </Button>
                    </TableCell>
                  </TableRow>
                ))
              )}
            </TableBody>
          </Table>
        </div>
      </div>

      <Dialog open={deleteDialogOpen} onOpenChange={(open) => {
        setDeleteDialogOpen(open)
        if (!open) {
          setDocumentToDelete(null)
        }
      }}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>Eliminar documento</DialogTitle>
            <DialogDescription>
              Esta acción elimina el documento y todos sus chunks del contexto del chatbot.
            </DialogDescription>
          </DialogHeader>
          <div className="space-y-2 text-sm text-slate-600">
            <p>Documento seleccionado:</p>
            <p className="font-semibold text-[#0d2f62]">{documentToDelete?.filename}</p>
          </div>
          {(deleteError || actionSuccessMessage) && (
            <p className={`text-sm ${deleteError ? 'text-red-600' : 'text-emerald-600'}`}>
              {deleteError ? deleteError.message : actionSuccessMessage}
            </p>
          )}
          <DialogFooter>
            <Button variant="outline" onClick={() => setDeleteDialogOpen(false)} disabled={isDeleting}>
              Cancelar
            </Button>
            <Button variant="destructive" onClick={handleDeleteConfirm} disabled={isDeleting}>
              {isDeleting ? 'Eliminando...' : 'Eliminar'}
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </section>
  )
}
