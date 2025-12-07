import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from '@/components/ui/dialog'
import { Button } from '@/components/ui/button'
import type { SimulatorConfig } from '@/data/simulator-config'

type SimulatorConfigDeleteDialogProps = {
  open: boolean
  config?: SimulatorConfig | null
  onOpenChange: (open: boolean) => void
  onConfirm: () => void
  deleting?: boolean
  errorMessage?: string
}

export function SimulatorConfigDeleteDialog({
  open,
  config,
  onOpenChange,
  onConfirm,
  deleting = false,
  errorMessage,
}: SimulatorConfigDeleteDialogProps) {
  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent>
        <DialogHeader>
          <DialogTitle>Eliminar configuración</DialogTitle>
          <DialogDescription>
            Esta acción eliminará la configuración #{config?.id ?? ''} del simulador.
          </DialogDescription>
        </DialogHeader>
        <p className="text-sm text-slate-600">
          ¿Confirmas que deseas eliminar esta configuración? Esta acción no se puede deshacer y no estará disponible
          para futuras simulaciones.
        </p>
        {errorMessage && <p className="text-sm text-red-600">{errorMessage}</p>}
        <DialogFooter>
          <Button variant="outline" onClick={() => onOpenChange(false)} disabled={deleting}>
            Cancelar
          </Button>
          <Button variant="destructive" onClick={onConfirm} disabled={deleting}>
            {deleting ? 'Eliminando...' : 'Eliminar'}
          </Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  )
}
