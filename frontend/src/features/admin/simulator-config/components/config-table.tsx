import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
} from '@/components/ui/dropdown-menu'
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from '@/components/ui/table'
import { cn } from '@/lib/utils'
import { MoreHorizontal } from 'lucide-react'
import { CreditSimulator } from '@/features/simulator/components/credit-simulator'
import type { SimulatorConfig } from '@/data/simulator-config'

type ConfigTableProps = {
  configs: SimulatorConfig[]
  selectedConfigId: number | null
  selectedConfig: SimulatorConfig | null
  onCreate: () => void
  onEdit: (config: SimulatorConfig) => void
  onSelect: (configId: number) => void
  formatCurrency: (value: number) => string
}

export function SimulatorConfigTable({
  configs,
  selectedConfigId,
  selectedConfig,
  onCreate,
  onEdit,
  onSelect,
  formatCurrency,
}: ConfigTableProps) {
  return (
    <section className="space-y-6">
      <div className="flex flex-wrap items-center justify-between gap-4">
        <div>
          <p className="text-lg font-semibold text-[#0d2f62]">Configuración del Simulador</p>
          <p className="text-sm text-slate-500">
            Ajusta los parámetros financieros que usa el simulador de crédito.
          </p>
        </div>
        <Button className="bg-[#f26522] text-white hover:bg-[#d85314]" onClick={onCreate}>
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
            {configs.map((config) => (
              <TableRow
                key={config.id}
                className={cn('text-sm', selectedConfigId === config.id && 'bg-orange-50/60')}
              >
                <TableCell>
                  <div className="flex items-center gap-2">
                    <span className="font-semibold text-[#0d2f62]">#{config.id}</span>
                    {config.isActive && (
                      <Badge variant="outline" className="border-[#f26522] text-[#f26522]">
                        Activo
                      </Badge>
                    )}
                  </div>
                </TableCell>
                <TableCell>
                  {config.createdAt
                    ? new Date(config.createdAt).toLocaleDateString('es-CO', {
                        year: 'numeric',
                        month: 'short',
                        day: 'numeric',
                      })
                    : 'Sin fecha'}
                </TableCell>
                <TableCell>{((config.tasaInteresMensual ?? 0) * 100).toFixed(2)}%</TableCell>
                <TableCell>{formatCurrency(config.montoMinimo)}</TableCell>
                <TableCell>{formatCurrency(config.montoMaximo)}</TableCell>
                <TableCell>{config.plazosDisponibles.map((plazo) => `${plazo}m`).join(', ')}</TableCell>
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
                      <DropdownMenuItem onClick={() => onEdit(config)}>Editar</DropdownMenuItem>
                      <DropdownMenuItem onClick={() => onSelect(config.id)}>Seleccionar</DropdownMenuItem>
                    </DropdownMenuContent>
                  </DropdownMenu>
                </TableCell>
              </TableRow>
            ))}
          </TableBody>
        </Table>
      </div>

      {selectedConfig && (() => {
        const previewTerms = selectedConfig.plazosDisponibles.length
          ? selectedConfig.plazosDisponibles
          : [12]
        const previewInitialTerm = previewTerms[0]

        return (
          <div className="space-y-3">
            <CreditSimulator
              key={selectedConfig.id}
              minAmount={selectedConfig.montoMinimo}
              maxAmount={selectedConfig.montoMaximo}
              monthlyRate={selectedConfig.tasaInteresMensual}
              terms={previewTerms}
              initialAmount={selectedConfig.montoMinimo}
              initialTerm={previewInitialTerm}
              showModeToggle
            />
            <p className="text-center text-sm text-slate-500">
              Configuración activa #{selectedConfig.id} creada el{' '}
              {selectedConfig.createdAt
                ? new Date(selectedConfig.createdAt).toLocaleDateString('es-CO')
                : 'fecha no disponible'}
            </p>
          </div>
        )
      })()}
    </section>
  )
}
