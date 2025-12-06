import { useMemo, useState } from 'react'
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
import { requestsData, type RequestRecord } from '@/data/admin-requests'

function useRequestsFilter() {
  const [searchTerm, setSearchTerm] = useState('')

  const filteredRequests = useMemo(() => {
    const query = searchTerm.toLowerCase()
    return requestsData.filter((request) =>
      `${request.name} ${request.id}`.toLowerCase().includes(query),
    )
  }, [searchTerm])

  return { searchTerm, setSearchTerm, filteredRequests }
}

export function RequestsPanel() {
  const { searchTerm, setSearchTerm, filteredRequests } = useRequestsFilter()

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
            {filteredRequests.map((request: RequestRecord) => (
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
  )
}
