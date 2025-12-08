import { useState } from 'react'
import { Button } from '@/components/ui/button'
import type { ClientRecord } from '@/data/admin-clients'
import { useClientDetails } from '@/features/clients/hooks/use-client-details'

const detailTabs = [
  { id: 'info', label: 'Información' },
  { id: 'documents', label: 'Documentos Cliente' },
  { id: 'credits', label: 'Créditos' },
] as const

type DetailTabId = (typeof detailTabs)[number]['id']

type ClientDetailViewProps = {
  client: ClientRecord
  onBack: () => void
  onEdit: (client: ClientRecord) => void
}

export function ClientDetailView({ client, onBack, onEdit }: ClientDetailViewProps) {
  const [activeTab, setActiveTab] = useState<DetailTabId>('info')
  const {
    data: remoteClient,
    isFetching,
    error,
  } = useClientDetails(client.id, { enabled: true })
  const resolvedClient = remoteClient ?? client

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
