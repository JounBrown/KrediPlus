import { useEffect, useMemo, useState } from 'react'
import { cn } from '@/lib/utils'
import { Slider } from '@/components/ui/slider'
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { CheckCircle2 } from 'lucide-react'
import { useCreditSimulation } from '@/features/simulator/hooks/use-credit-simulation'

const currencyFormatter = new Intl.NumberFormat('es-CO', {
  style: 'currency',
  currency: 'COP',
  maximumFractionDigits: 0,
})

type Mode = 'slider' | 'input'

type CreditSimulatorProps = {
  className?: string
  title?: string
  subtitle?: string
  badgeText?: string
  minAmount: number
  maxAmount: number
  monthlyRate: number
  terms: number[]
  initialAmount?: number
  initialTerm?: number
  imageUrl?: string
  imageAlt?: string
  features?: string[]
  showModeToggle?: boolean
  actionLabel?: string
}

const defaultFeatures = [
  'Somos 100% digitales',
  'Trabajamos con reportados y pensionados',
]

const clampAmount = (value: number, min: number, max: number) => {
  if (Number.isNaN(value)) return min
  if (value < min) return min
  if (value > max) return max
  return value
}

export function CreditSimulator(props: CreditSimulatorProps) {
  const {
    className,
    title = 'Simula tu crédito aquí',
    subtitle,
    badgeText,
    minAmount,
    maxAmount,
    monthlyRate,
    terms,
    initialAmount,
    initialTerm,
    imageUrl = 'https://images.unsplash.com/photo-1470770841072-f978cf4d019e?auto=format&fit=crop&w=720&q=80',
    imageAlt = 'Paisaje tranquilo',
    features = defaultFeatures,
    showModeToggle = false,
    actionLabel = 'Simular',
  } = props

  const [mode, setMode] = useState<Mode>('slider')
  const [amount, setAmount] = useState(() => clampAmount(initialAmount ?? minAmount, minAmount, maxAmount))
  const [term, setTerm] = useState(() => (initialTerm ?? terms[0] ?? 12).toString())
  const [manualAmount, setManualAmount] = useState(() => amount.toString())
  const [lastSimulatedKey, setLastSimulatedKey] = useState<string | null>(null)
  const {
    mutate: runSimulation,
    data: simulationResult,
    isPending: isSimulating,
    isError: simulationHasError,
    error: simulationError,
  } = useCreditSimulation()

  useEffect(() => {
    setAmount((prev) => clampAmount(prev, minAmount, maxAmount))
  }, [minAmount, maxAmount])

  useEffect(() => {
    setTerm((prev) => {
      if (terms.some((t) => t.toString() === prev)) {
        return prev
      }
      return (terms[0] ?? 12).toString()
    })
  }, [terms])

  useEffect(() => {
    if (typeof initialAmount === 'number') {
      const clamped = clampAmount(initialAmount, minAmount, maxAmount)
      setAmount(clamped)
      setManualAmount(clamped.toString())
    }
  }, [initialAmount, minAmount, maxAmount])

  useEffect(() => {
    if (typeof initialTerm === 'number') {
      setTerm(initialTerm.toString())
    }
  }, [initialTerm])

  useEffect(() => {
    if (!showModeToggle) return
    setManualAmount((prev) => {
      if (mode === 'input') {
        return prev
      }
      return amount.toString()
    })
  }, [mode, amount, showModeToggle])

  const selectedTerm = Number(term) || 1

  const estimatedPayment = useMemo(() => {
    const months = selectedTerm
    const monthlyRateDecimal = monthlyRate / 100
    if (monthlyRateDecimal <= 0) {
      return amount / months
    }
    const numerator = amount * monthlyRateDecimal
    const denominator = 1 - Math.pow(1 + monthlyRateDecimal, -months)
    if (denominator === 0) return 0
    return numerator / denominator
  }, [amount, selectedTerm, monthlyRate])

  const formattedAmount = currencyFormatter.format(amount)
  const formattedPayment = currencyFormatter.format(Math.round(estimatedPayment || 0))
  const currentSimulationKey = `${amount}-${selectedTerm}`
  const activeSimulationResult =
    simulationResult && lastSimulatedKey === currentSimulationKey ? simulationResult : null
  const simulationRatePercent = activeSimulationResult
    ? (activeSimulationResult.monthlyRate * 100).toFixed(2)
    : null

  const handleManualChange = (value: string) => {
    const sanitized = value.replace(/[^0-9]/g, '')
    setManualAmount(sanitized)
    if (!sanitized) return
    setAmount(Number(sanitized))
  }

  const handleManualBlur = () => {
    const numeric = manualAmount === '' ? minAmount : Number(manualAmount)
    const clamped = clampAmount(Number.isNaN(numeric) ? minAmount : numeric, minAmount, maxAmount)
    setAmount(clamped)
    setManualAmount(clamped.toString())
  }

  const handleSimulate = () => {
    const simulationTerm = selectedTerm || terms[0] || 12
    const simulationAmount = amount
    const simulationKey = `${simulationAmount}-${simulationTerm}`
    setLastSimulatedKey(null)
    runSimulation(
      { amount: simulationAmount, termMonths: simulationTerm },
      {
        onSuccess: () => {
          setLastSimulatedKey(simulationKey)
        },
      },
    )
  }

  return (
    <section className={cn('mx-auto grid max-w-7xl items-start gap-10 rounded-3xl bg-white p-8 shadow-xl ring-1 ring-slate-200 md:grid-cols-[1.1fr,0.9fr]', className)}>
      <div className="rounded-3xl bg-white">
        <div className="rounded-2xl bg-white p-8 shadow-lg ring-1 ring-slate-200">
          <div className="flex items-start justify-between">
            <div>
              <h4 className="text-2xl font-extrabold text-[#0d2f62]">{title}</h4>
              {subtitle && <p className="text-sm text-slate-500">{subtitle}</p>}
            </div>
            <span className="rounded-full border border-slate-200 px-3 py-1 text-xs font-semibold text-[#0d2f62]">
              {badgeText ?? `${monthlyRate.toFixed(2)}% mensual`}
            </span>
          </div>

          <div className="mt-6 space-y-6">
            <div className="space-y-2">
              <div className="flex flex-wrap items-center justify-between gap-3">
                <p className="text-sm font-semibold text-[#f26522]">Monto</p>
                {showModeToggle && (
                  <div className="flex rounded-full border border-slate-200 bg-slate-50 text-xs font-semibold text-slate-500">
                    <button
                      type="button"
                      onClick={() => setMode('slider')}
                      className={cn(
                        'rounded-full px-3 py-1 transition',
                        mode === 'slider' ? 'bg-white text-[#f26522] shadow' : 'hover:text-[#f26522]',
                      )}
                    >
                      Deslizar
                    </button>
                    <button
                      type="button"
                      onClick={() => setMode('input')}
                      className={cn(
                        'rounded-full px-3 py-1 transition',
                        mode === 'input' ? 'bg-white text-[#f26522] shadow' : 'hover:text-[#f26522]',
                      )}
                    >
                      Digitar
                    </button>
                  </div>
                )}
              </div>

              {mode === 'input' && showModeToggle ? (
                <Input
                  type="text"
                  inputMode="numeric"
                  pattern="[0-9]*"
                  value={manualAmount}
                  onChange={(event) => handleManualChange(event.target.value)}
                  onBlur={handleManualBlur}
                  placeholder="Ingresa el monto"
                  className="h-12 rounded-2xl border-slate-200 text-right text-lg font-bold text-[#0d2f62] [&::-webkit-inner-spin-button]:appearance-none [&::-webkit-outer-spin-button]:appearance-none"
                />
              ) : (
                <>
                  <div className="text-lg font-bold text-[#0d2f62]">{formattedAmount}</div>
                  <Slider
                    value={[amount]}
                    min={minAmount}
                    max={maxAmount}
                    step={100000}
                    onValueChange={(value) => setAmount(clampAmount(value[0] ?? minAmount, minAmount, maxAmount))}
                  />
                </>
              )}

              <div className="flex justify-between text-xs text-slate-500">
                <span>{currencyFormatter.format(minAmount)}</span>
                <span>{currencyFormatter.format(maxAmount)}</span>
              </div>
            </div>

            <div className="space-y-2">
              <p className="text-sm font-semibold text-[#f26522]">Plazo (meses)</p>
              <Select value={term} onValueChange={setTerm}>
                <SelectTrigger className="h-11">
                  <SelectValue placeholder="Selecciona plazo" />
                </SelectTrigger>
                <SelectContent>
                  {terms.map((option) => (
                    <SelectItem key={option} value={option.toString()}>
                      {option} meses
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>

            <div className="rounded-2xl bg-[#0d2f62] p-4 text-white">
              <p className="text-xs uppercase text-white/70">Cuota estimada</p>
              <p className="text-2xl font-bold">{formattedPayment}</p>
              <p className="text-xs text-white/80">Tasas calculadas con {monthlyRate.toFixed(2)}% mensual</p>
            </div>

            <Button
              type="button"
              className="w-full bg-[#f26522] text-white hover:bg-[#d85314]"
              onClick={handleSimulate}
              disabled={isSimulating}
            >
              {isSimulating ? 'Calculando...' : actionLabel}
            </Button>

            {simulationHasError && (
              <p className="text-sm text-red-600">
                {simulationError?.message || 'No fue posible simular el crédito.'}
              </p>
            )}

            {activeSimulationResult && (
              <div className="rounded-2xl border border-slate-200 bg-slate-50 p-4 text-sm text-slate-700">
                <div className="flex flex-wrap items-baseline justify-between gap-2">
                  <p className="text-xs font-semibold uppercase text-[#f26522]">Resultado oficial</p>
                  <p className="text-xs text-slate-500">
                    Tasa{' '}
                    {simulationRatePercent ? `${simulationRatePercent}% mensual` : 'no disponible'}
                  </p>
                </div>
                <div className="mt-3 grid gap-4 sm:grid-cols-3">
                  <div>
                    <p className="text-xs text-slate-500">Cuota mensual</p>
                    <p className="text-lg font-bold text-[#0d2f62]">
                      {currencyFormatter.format(Math.round(activeSimulationResult.monthlyPayment))}
                    </p>
                  </div>
                  <div>
                    <p className="text-xs text-slate-500">Total a pagar</p>
                    <p className="text-lg font-bold text-[#0d2f62]">
                      {currencyFormatter.format(Math.round(activeSimulationResult.totalToPay))}
                    </p>
                  </div>
                  <div>
                    <p className="text-xs text-slate-500">Total intereses</p>
                    <p className="text-lg font-bold text-[#0d2f62]">
                      {currencyFormatter.format(Math.round(activeSimulationResult.totalInterests))}
                    </p>
                  </div>
                </div>
              </div>
            )}
          </div>
        </div>
      </div>

      <div className="space-y-6 text-slate-700">
        <div className="relative">
          <div className="absolute inset-10 rounded-full bg-[#0d2f62]/10 blur-3xl" aria-hidden />
          <img
            src={imageUrl}
            alt={imageAlt}
            className="relative mx-auto h-72 w-72 rounded-full object-cover shadow-xl ring-4 ring-white"
          />
        </div>
        <ul className="space-y-3 text-sm">
          {features.map((feature) => (
            <li key={feature} className="flex items-center gap-3">
              <CheckCircle2 className="h-5 w-5 text-[#f26522]" /> {feature}
            </li>
          ))}
        </ul>
      </div>
    </section>
  )
}
