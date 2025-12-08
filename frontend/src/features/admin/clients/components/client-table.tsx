import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Textarea } from '@/components/ui/textarea'
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
import { MoreHorizontal, Search } from 'lucide-react'
import { useClients } from '../hooks/use-clients'
import { useClientsQuery } from '@/features/clients/hooks/use-clients-query'
import { useEffect, useMemo, useState } from 'react'
import type { ClientRecord } from '@/data/admin-clients'
import { ClientDetailView } from './client-detail-view'

export function ClientTable() {
  const {
    data: serverClients,
    isLoading,
    isError,
    error,
  } = useClientsQuery()
  const {
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
    creatingClient,
    createError,
    updatingClient,
    updateError,
    loadingClientDetails,
    clientDetailsError,
    deletingClient,
    deleteError,
  } = useClients(serverClients ?? [])
  const [detailClient, setDetailClient] = useState<ClientRecord | null>(null)
  const isCreateMode = dialogType === 'create'
  const isEditMode = dialogType === 'edit'
  const submitPending = isCreateMode ? creatingClient : isEditMode ? updatingClient : false
  const submitError = isCreateMode ? createError : isEditMode ? updateError : null
  const [page, setPage] = useState(1)
  const PAGE_SIZE = 8

  useEffect(() => {
    setPage(1)
  }, [clientSearch])

  useEffect(() => {
    if (!detailClient || !serverClients) return
    const updated = serverClients.find((client) => client.id === detailClient.id)
    if (updated && updated !== detailClient) {
      setDetailClient(updated)
    }
  }, [serverClients, detailClient])

  const totalPages = useMemo(() => Math.max(1, Math.ceil(filteredClients.length / PAGE_SIZE)), [filteredClients.length])
  const currentPage = Math.min(page, totalPages)
  const startIndex = (currentPage - 1) * PAGE_SIZE
  const currentClients = filteredClients.slice(startIndex, startIndex + PAGE_SIZE)

  const handleViewDetails = (client: ClientRecord) => {
    setDetailClient(client)
  }

  const handleBackToList = () => {
    setDetailClient(null)
  }

  const content = detailClient ? (
    <ClientDetailView
      client={detailClient}
      onBack={handleBackToList}
      onEdit={(client) => openDialog('edit', client)}
    />
  ) : (
    <section className="space-y-6">
      <div className="flex flex-wrap items-center justify-between gap-4">
        <div>
          <p className="text-lg font-semibold text-[#0d2f62]">Gestión de Clientes</p>
          <p className="text-sm text-slate-500">Administra la base de clientes registrados.</p>
        </div>
        <Button className="bg-[#f26522] text-white hover:bg-[#d85314]" onClick={() => openDialog('create')}>
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
            placeholder="Filtra por nombre o cédula"
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
            {isLoading ? (
              <TableRow>
                <TableCell colSpan={6} className="py-6 text-center text-sm text-slate-500">
                  Cargando clientes...
                </TableCell>
              </TableRow>
            ) : isError ? (
              <TableRow>
                <TableCell colSpan={6} className="py-6 text-center text-sm text-red-600">
                  {error?.message || 'No fue posible cargar los clientes.'}
                </TableCell>
              </TableRow>
            ) : filteredClients.length === 0 ? (
              <TableRow>
                <TableCell colSpan={6} className="py-6 text-center text-sm text-slate-500">
                  No se encontraron clientes con ese criterio.
                </TableCell>
              </TableRow>
            ) : (
              currentClients.map((client) => (
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
                        <DropdownMenuItem onClick={() => handleViewDetails(client)}>
                          Ver detalles
                        </DropdownMenuItem>
                        <DropdownMenuItem onClick={() => openDialog('edit', client)}>
                          Editar
                        </DropdownMenuItem>
                        <DropdownMenuItem className="text-red-600" onClick={() => openDialog('delete', client)}>
                          Eliminar
                        </DropdownMenuItem>
                      </DropdownMenuContent>
                    </DropdownMenu>
                  </TableCell>
                </TableRow>
              ))
            )}
          </TableBody>
        </Table>
      </div>

      {filteredClients.length > 0 && (
        <div className="flex flex-wrap items-center justify-between gap-3 rounded-2xl border border-slate-100 bg-white px-4 py-3 text-sm text-slate-600 shadow-sm">
          <p>
            Mostrando {startIndex + 1}-{startIndex + currentClients.length} de {filteredClients.length} clientes
          </p>
          <div className="flex items-center gap-2">
            <Button
              variant="outline"
              size="sm"
              onClick={() => setPage((prev) => Math.max(1, prev - 1))}
              disabled={currentPage === 1}
            >
              Anterior
            </Button>
            <span className="text-xs font-semibold uppercase text-slate-500">
              Página {currentPage} de {totalPages}
            </span>
            <Button
              variant="outline"
              size="sm"
              onClick={() => setPage((prev) => Math.min(totalPages, prev + 1))}
              disabled={currentPage === totalPages}
            >
              Siguiente
            </Button>
          </div>
        </div>
      )}
    </section>
  )

  return (
    <>
      {content}

      <Dialog
        open={dialogOpen && Boolean(dialogType)}
        onOpenChange={(open) => {
          if (!open) closeDialog()
        }}
      >
        <DialogContent>
          {dialogType === 'delete' && activeClient ? (
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
              {deleteError && <p className="text-sm text-red-600">{deleteError.message}</p>}
              <DialogFooter>
                <Button variant="outline" onClick={closeDialog}>
                  Cancelar
                </Button>
                <Button
                  variant="destructive"
                  onClick={handleDeleteClient}
                  disabled={deletingClient}
                >
                  {deletingClient ? 'Eliminando...' : 'Eliminar'}
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
              {dialogType === 'edit' && loadingClientDetails && (
                <p className="text-sm text-slate-500">Cargando información actualizada...</p>
              )}
              {dialogType === 'edit' && clientDetailsError && (
                <p className="text-sm text-red-600">{clientDetailsError.message}</p>
              )}
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
                  disabled={isEditMode}
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
                  disabled={isEditMode}
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
                {submitError && (
                  <p className="text-sm text-red-600">{submitError.message}</p>
                )}
                <Button
                  className="bg-[#f26522] text-white"
                  onClick={handleSaveClient}
                  disabled={submitPending}
                >
                  {submitPending ? 'Guardando...' : isCreateMode ? 'Agregar' : 'Guardar cambios'}
                </Button>
              </DialogFooter>
            </>
          ) : null}
        </DialogContent>
      </Dialog>
    </>
  )
}
