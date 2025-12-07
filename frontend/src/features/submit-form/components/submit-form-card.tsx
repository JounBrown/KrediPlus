import { useState } from 'react'
import { ShieldCheck, CalendarIcon, Check, AlertCircle } from 'lucide-react'
import { cn } from '@/lib/utils'
import { Button } from '@/components/ui/button'
import { Checkbox } from '@/components/ui/checkbox'
import { Input } from '@/components/ui/input'
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select'
import { useSubmitForm } from '../hooks/use-submit-form'
import type { SubmitFormPayload } from '../types/loan-application'
import { useCreateLoanApplication } from '@/features/loan-applications/hooks/use-create-loan-application'

type SubmitFormCardProps = {
  className?: string
  title?: string
  subtitle?: string
  ctaLabel?: string
  onSubmit?: (payload: SubmitFormPayload) => Promise<void> | void
  defaultMontoSolicitado?: number
  defaultPlazo?: number
  defaultEstado?: string
}

const convenioOptions = [
  'Colpensiones',
  'Colfondos',
  'FOPEP',
  'Porvenir',
  'Fiduprevisora',
  'CASUR',
  'CREMIL',
  'Sin convenio',
].map((option) => ({ value: option, label: option }))

export function SubmitFormCard({
  className,
  title = '¡Toma el control de tu vida financiera!',
  subtitle = 'Obtén tu crédito rápido y fácil',
  ctaLabel = 'Solicitar mi crédito',
  onSubmit,
  defaultMontoSolicitado = 100000,
  defaultPlazo = 6,
  defaultEstado = 'pendiente',
}: SubmitFormCardProps) {
  const [convenio, setConvenio] = useState<string | undefined>(undefined)
  const [policyAccepted, setPolicyAccepted] = useState(false)
  const [feedback, setFeedback] = useState<{ type: 'success' | 'error'; message: string } | null>(null)
  const loanApplicationMutation = useCreateLoanApplication({
    onSuccess: () => {
      setFeedback({ type: 'success', message: 'Solicitud enviada correctamente. Te contactaremos pronto.' })
      setConvenio(undefined)
      setPolicyAccepted(false)
    },
    onError: (error) => {
      setFeedback({ type: 'error', message: error.message })
    },
  })
  const { handleSubmit, isSubmitting } = useSubmitForm({
    onSubmit: async (payload) => {
      if (onSubmit) {
        await onSubmit({ ...payload })
        return
      }

      const apiPayload = {
        name: payload.name,
        cedula: payload.cedula,
        convenio: payload.convenio,
        telefono: payload.telefono,
        fecha_nacimiento: payload.fecha_nacimiento,
        monto_solicitado: payload.monto_solicitado,
        plazo: payload.plazo,
      }

      setFeedback(null)
      await loanApplicationMutation.mutateAsync(apiPayload)
    },
  })

  return (
    <form
      onSubmit={handleSubmit}
      className={cn('rounded-2xl bg-white shadow-xl ring-1 ring-orange-50', className)}
    >
      <div className="rounded-t-2xl bg-gradient-to-br from-orange-50 via-white to-white px-8 pb-4 pt-8 text-center">
        <div className="mx-auto mb-4 flex h-14 w-14 items-center justify-center rounded-2xl bg-orange-100 text-[#f26522]">
          <ShieldCheck className="h-7 w-7" />
        </div>
        <h2 className="text-lg font-bold text-[#0d2f62]">{title}</h2>
        <p className="text-sm text-slate-600">{subtitle}</p>
      </div>

      <div className="space-y-4 px-8 pb-8 pt-6">
        {feedback && (
          <div
            className={cn(
              'flex items-center gap-2 rounded-xl px-4 py-3 text-sm',
              feedback.type === 'success'
                ? 'bg-green-50 text-green-700'
                : 'bg-red-50 text-red-600',
            )}
          >
            {feedback.type === 'success' ? <Check className="h-4 w-4" /> : <AlertCircle className="h-4 w-4" />}
            {feedback.message}
          </div>
        )}

        <div className="space-y-1">
          <label className="text-sm font-semibold text-slate-700" htmlFor="name">
            Nombre Completo
          </label>
          <Input id="name" name="name" placeholder="Tu nombre completo" required />
        </div>

        <div className="space-y-1">
          <label className="text-sm font-semibold text-slate-700" htmlFor="cedula">
            Cédula
          </label>
          <Input id="cedula" name="cedula" placeholder="Número de documento" required />
        </div>

        <div className="space-y-1">
          <label className="text-sm font-semibold text-slate-700">Convenio</label>
          <Select value={convenio} onValueChange={setConvenio}>
            <SelectTrigger>
              <SelectValue placeholder="Selecciona una opción" />
            </SelectTrigger>
            <SelectContent>
              {convenioOptions.map((option) => (
                <SelectItem key={option.value} value={option.value}>
                  {option.label}
                </SelectItem>
              ))}
            </SelectContent>
          </Select>
          <input type="hidden" name="convenio" value={convenio ?? ''} />
        </div>

        <div className="space-y-1">
          <label className="text-sm font-semibold text-slate-700" htmlFor="telefono">
            Teléfono
          </label>
          <Input id="telefono" name="telefono" placeholder="Tu número de teléfono" required />
        </div>

        <div className="space-y-1">
          <label className="text-sm font-semibold text-slate-700" htmlFor="fechaNacimiento">
            Fecha de Nacimiento
          </label>
          <div className="flex items-center gap-2">
            <Input type="date" id="fecha_nacimiento" name="fecha_nacimiento" className="flex-1" required />
            <CalendarIcon className="h-5 w-5 text-slate-400" />
          </div>
        </div>

        <div className="flex items-start gap-3 rounded-md bg-slate-50 px-3 py-2">
          <Checkbox
            id="policy"
            checked={policyAccepted}
            onCheckedChange={(checked) => setPolicyAccepted(Boolean(checked))}
            name="policy"
          />
          <input type="hidden" name="policyAccepted" value={policyAccepted ? 'true' : 'false'} />
          <label htmlFor="policy" className="text-sm text-slate-600">
            He leído y acepto la política de privacidad de datos.
          </label>
        </div>

        <input type="hidden" name="monto_solicitado" value={defaultMontoSolicitado} />
        <input type="hidden" name="plazo" value={defaultPlazo} />
        <input type="hidden" name="estado" value={defaultEstado} />

        <Button
          type="submit"
          className="w-full bg-[#f26522] text-white hover:bg-[#d85314]"
          disabled={isSubmitting}
        >
          {isSubmitting ? 'Enviando...' : ctaLabel}
        </Button>
      </div>
    </form>
  )
}
