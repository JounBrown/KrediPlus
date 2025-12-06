import { cn } from '@/lib/utils'
import { ListChecks, Settings, UploadCloud, Users } from 'lucide-react'

const adminTabs = [
  { id: 'requests', label: 'Solicitudes Registradas', icon: ListChecks },
  { id: 'upload', label: 'Carga de Documentos', icon: UploadCloud },
  { id: 'clients', label: 'Gestión Clientes', icon: Users },
  { id: 'simulator', label: 'Configuración Simulador', icon: Settings },
] as const

export type AdminTabId = (typeof adminTabs)[number]['id']

type AdminTabsProps = {
  activeTab: AdminTabId
  onSelect: (tab: AdminTabId) => void
}

export function AdminTabs({ activeTab, onSelect }: AdminTabsProps) {
  return (
    <div>
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
              onClick={() => onSelect(tab.id)}
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
    </div>
  )
}
