import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from '@/components/ui/dialog'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import type { SimulatorConfigForm } from '../hooks/use-simulator-configs'

type SimulatorConfigDialogProps = {
  open: boolean
  mode: 'create' | 'edit'
  form: SimulatorConfigForm
  onOpenChange: (open: boolean) => void
  onChange: (field: keyof SimulatorConfigForm, value: string) => void
  onSubmit: () => void
  submitting?: boolean
  errorMessage?: string
}

export function SimulatorConfigDialog({
  open,
  mode,
  form,
  onOpenChange,
  onChange,
  onSubmit,
  submitting = false,
  errorMessage,
}: SimulatorConfigDialogProps) {
  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent>
        <DialogHeader>
          <DialogTitle>
            {mode === 'create' ? 'Agregar configuración del simulador' : 'Editar configuración del simulador'}
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
              value={form.tasaInteresMensual}
              onChange={(event) => onChange('tasaInteresMensual', event.target.value)}
              placeholder="Ej: 1.55"
              min={0}
              step="0.01"
            />
            <p className="text-xs text-slate-500">Ingresa el porcentaje; nosotros lo convertimos automáticamente.</p>
          </div>
          <div className="grid gap-4 md:grid-cols-2">
            <div className="space-y-1">
              <label className="text-xs font-semibold text-slate-600">Monto mínimo</label>
              <Input
                type="number"
                value={form.montoMinimo}
                onChange={(event) => onChange('montoMinimo', event.target.value)}
                placeholder="Ej: 3000000"
                min={0}
              />
            </div>
            <div className="space-y-1">
              <label className="text-xs font-semibold text-slate-600">Monto máximo</label>
              <Input
                type="number"
                value={form.montoMaximo}
                onChange={(event) => onChange('montoMaximo', event.target.value)}
                placeholder="Ej: 40000000"
                min={0}
              />
            </div>
          </div>
          <div className="space-y-1">
            <label className="text-xs font-semibold text-slate-600">Plazos disponibles (meses)</label>
            <Input
              value={form.plazosDisponibles}
              onChange={(event) => onChange('plazosDisponibles', event.target.value)}
              placeholder="Ej: 12, 24, 36"
            />
            <p className="text-xs text-slate-500">Separa cada plazo con comas.</p>
          </div>
        </div>

        {errorMessage && <p className="text-sm text-red-600">{errorMessage}</p>}

        <DialogFooter>
          <Button variant="outline" onClick={() => onOpenChange(false)} disabled={submitting}>
            Cancelar
          </Button>
          <Button
            className="bg-[#f26522] text-white"
            onClick={onSubmit}
            disabled={submitting}
          >
            {submitting
              ? 'Guardando...'
              : mode === 'create'
                ? 'Guardar configuración'
                : 'Guardar cambios'}
          </Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  )
}
