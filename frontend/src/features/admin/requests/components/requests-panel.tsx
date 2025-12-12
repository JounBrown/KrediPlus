import { useEffect, useMemo, useState } from 'react'
import { Link } from '@tanstack/react-router'
import { Search, MoreHorizontal } from 'lucide-react'
import { Input } from '@/components/ui/input'
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from '@/components/ui/table'
import { Button } from '@/components/ui/button'
import { useLoanApplications } from '@/features/loan-applications/hooks/use-loan-applications'
import type { LoanApplication } from '@/features/submit-form/types/loan-application'

function useRequestsFilter(requests: LoanApplication[]) {
  const [searchTerm, setSearchTerm] = useState('')

  const filteredRequests = useMemo(() => {
    const query = searchTerm.toLowerCase()
    return requests.filter((request) => `${request.name} ${request.cedula}`.toLowerCase().includes(query))
  }, [searchTerm, requests])

  return { searchTerm, setSearchTerm, filteredRequests }
}

const PAGE_SIZE = 8

export function RequestsPanel() {
  const {
    data: loanApplications = [],
    isLoading,
    isError,
    error,
  } = useLoanApplications()
  const { searchTerm, setSearchTerm, filteredRequests } = useRequestsFilter(loanApplications)
  const [page, setPage] = useState(1)
  const createdAtFormatter = useMemo(
    () =>
      new Intl.DateTimeFormat('es-CO', {
        dateStyle: 'medium',
        timeStyle: 'short',
      }),
    [],
  )

  useEffect(() => {
    setPage(1)
  }, [searchTerm])

  const totalPages = Math.max(1, Math.ceil(filteredRequests.length / PAGE_SIZE))
  const currentPage = Math.min(page, totalPages)
  const startIndex = (currentPage - 1) * PAGE_SIZE
  const currentRequests = filteredRequests.slice(startIndex, startIndex + PAGE_SIZE)

  return (
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
            placeholder="Filtra por nombre o cédula"
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
              <TableHead className="text-xs font-bold uppercase text-slate-500">Creada</TableHead>
              <TableHead>
                <span className="sr-only">Acciones</span>
              </TableHead>
            </TableRow>
          </TableHeader>
          <TableBody>
            {isLoading ? (
              <TableRow>
                <TableCell colSpan={7} className="py-6 text-center text-sm text-slate-500">
                  Cargando solicitudes...
                </TableCell>
              </TableRow>
            ) : isError ? (
              <TableRow>
                <TableCell colSpan={7} className="py-6 text-center text-sm text-red-600">
                  {error?.message || 'No fue posible cargar las solicitudes.'}
                </TableCell>
              </TableRow>
            ) : filteredRequests.length === 0 ? (
              <TableRow>
                <TableCell colSpan={7} className="py-6 text-center text-sm text-slate-500">
                  No se encontraron solicitudes con ese criterio.
                </TableCell>
              </TableRow>
            ) : (
              currentRequests.map((request) => (
                <TableRow key={request.id} className="text-sm">
                  <TableCell className="font-semibold text-[#0d2f62]">{request.name}</TableCell>
                  <TableCell>{request.cedula}</TableCell>
                  <TableCell className="uppercase text-xs font-semibold text-[#f26522]">
                    {request.convenio || 'N/A'}
                  </TableCell>
                  <TableCell>{request.telefono}</TableCell>
                  <TableCell>{request.fecha_nacimiento}</TableCell>
                  <TableCell>
                    {request.created_at
                      ? createdAtFormatter.format(new Date(request.created_at))
                      : 'Sin fecha'}
                  </TableCell>
                  <TableCell className="text-right">
                    <button
                      className="rounded-full p-1 text-slate-400 transition hover:bg-slate-100 hover:text-slate-600"
                      aria-label="Más acciones"
                    >
                      <MoreHorizontal className="h-5 w-5" />
                    </button>
                  </TableCell>
                </TableRow>
              ))
            )}
          </TableBody>
        </Table>
      </div>

      {filteredRequests.length > 0 && (
        <div className="mt-4 flex flex-wrap items-center justify-between gap-3 rounded-2xl border border-slate-100 bg-white px-4 py-3 text-sm text-slate-600 shadow-sm">
          <p>
            Mostrando {filteredRequests.length === 0 ? 0 : startIndex + 1}-{startIndex + currentRequests.length} de{' '}
            {filteredRequests.length} solicitudes
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
}
