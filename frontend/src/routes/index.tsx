import { useMemo, useState } from 'react'
import { Route } from '@tanstack/react-router'
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
import { Slider } from '@/components/ui/slider'
import { rootRoute } from './root'
import {
  CalendarIcon,
  CheckCircle2,
  MessageCircle,
  Phone,
  Send,
  ShieldCheck,
  X,
} from 'lucide-react'
import { SiteHeader } from '@/components/layout/site-header'

const currencyFormatter = new Intl.NumberFormat('es-CO', {
  style: 'currency',
  currency: 'COP',
  maximumFractionDigits: 0,
})

function IndexPage() {
  const [amount, setAmount] = useState(5_000_000)
  const [term, setTerm] = useState('24')
  const [isChatOpen, setIsChatOpen] = useState(false)
  const minAmount = 1_000_000
  const maxAmount = 140_000_000

  const formattedAmount = useMemo(() => currencyFormatter.format(amount), [amount])

  return (
    <div className="min-h-screen bg-[hsl(var(--background))] text-slate-900">
      <SiteHeader active="home" />

      <main className="space-y-16 pb-16">
        <section id="clientes" className="bg-gradient-to-br from-white via-[#f9fafb] to-[#f7f7f7] pb-10 pt-8">
          <div className="mx-auto grid max-w-7xl items-start gap-10 px-6 lg:grid-cols-2">
            <div className="space-y-6">
              <div className="rounded-2xl bg-[#0d2f62] p-8 text-white shadow-xl">
                <p className="text-3xl font-extrabold leading-tight">
                  <span className="text-[#f26522]">Atendemos</span> clientes pensionados y reportados
                </p>
                <p className="mt-3 text-sm text-slate-100/90">
                  Descubre nuestros servicios de libranza hoy mismo y en línea.
                </p>
              </div>

              <div className="overflow-hidden rounded-2xl bg-white shadow-xl ring-1 ring-slate-200">
                <img
                  src="https://images.unsplash.com/photo-1508672019048-805c876b67e2?auto=format&fit=crop&w=900&q=80"
                  alt="Cliente cubierto con manta"
                  className="h-full w-full object-cover"
                />
              </div>
            </div>

            <div className="rounded-2xl bg-white shadow-xl ring-1 ring-orange-50">
              <div className="rounded-t-2xl bg-gradient-to-br from-orange-50 via-white to-white px-8 pb-4 pt-8 text-center">
                <div className="mx-auto mb-4 flex h-14 w-14 items-center justify-center rounded-2xl bg-orange-100 text-[#f26522]">
                  <ShieldCheck className="h-7 w-7" />
                </div>
                <h2 className="text-lg font-bold text-[#0d2f62]">¡Toma el control de tu vida financiera!</h2>
                <p className="text-sm text-slate-600">Obtén tu crédito rápido y fácil</p>
              </div>

              <div className="space-y-4 px-8 pb-8">
                <div className="space-y-1">
                  <label className="text-sm font-semibold text-slate-700">Nombre Completo</label>
                  <Input placeholder="Tu nombre completo" />
                </div>

                <div className="space-y-1">
                  <label className="text-sm font-semibold text-slate-700">Cédula</label>
                  <Input placeholder="Número de documento" />
                </div>

                <div className="space-y-1">
                  <label className="text-sm font-semibold text-slate-700">Convenio</label>
                  <Select defaultValue="">
                    <SelectTrigger>
                      <SelectValue placeholder="Selecciona una opción" />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="fondo">Fondo de pensiones</SelectItem>
                      <SelectItem value="pagaduria">Pagaduría aliada</SelectItem>
                      <SelectItem value="otros">Otro convenio</SelectItem>
                    </SelectContent>
                  </Select>
                </div>

                <div className="space-y-1">
                  <label className="text-sm font-semibold text-slate-700">Teléfono</label>
                  <Input placeholder="Tu número de teléfono" />
                </div>

                <div className="space-y-1">
                  <label className="text-sm font-semibold text-slate-700">Fecha de Nacimiento</label>
                  <div className="flex items-center gap-2">
                    <Input type="date" className="flex-1" />
                    <CalendarIcon className="h-5 w-5 text-slate-400" />
                  </div>
                </div>

                <div className="flex items-start gap-3 rounded-md bg-slate-50 px-3 py-2">
                  <Checkbox id="policy" className="mt-1" />
                  <label htmlFor="policy" className="text-sm text-slate-600">
                    He leído y acepto la política de privacidad de datos.
                  </label>
                </div>

                <Button className="w-full bg-[#f26522] text-white hover:bg-[#d85314]">
                  Solicitar mi crédito
                </Button>
              </div>
            </div>
          </div>
        </section>

        <section id="condiciones" className="bg-white py-14 shadow-sm">
          <div className="mx-auto flex max-w-7xl flex-col gap-10 px-6">
            <div className="text-center">
              <p className="text-sm font-semibold uppercase text-[#f26522] tracking-wide">Condiciones</p>
              <h3 className="text-3xl font-extrabold text-[#0d2f62]">
                ¿Qué condiciones necesitas?
              </h3>
              <p className="mt-2 text-sm text-slate-600">
                Ofrecemos condiciones flexibles y claras para que puedas acceder a tu crédito sin complicaciones.
              </p>
            </div>

            <div className="grid items-center gap-10 rounded-3xl bg-[#f8fafc] p-8 shadow-inner md:grid-cols-[1.2fr,1fr]">
              <div className="space-y-3 rounded-2xl bg-white p-8 shadow-lg ring-1 ring-slate-200">
                <span className="inline-flex w-fit rounded-full bg-[#f26522] px-4 py-1 text-xs font-bold uppercase text-white">
                  Pensionado
                </span>
                <div className="grid gap-3 text-slate-700">
                  <div>
                    <p className="text-sm font-semibold text-[#f26522]">Edad</p>
                    <p>Hasta 92 años</p>
                  </div>
                  <div>
                    <p className="text-sm font-semibold text-[#f26522]">Plazo</p>
                    <p>Hasta 180 meses</p>
                  </div>
                  <div>
                    <p className="text-sm font-semibold text-[#f26522]">Monto</p>
                    <p>Desde $1 millón y hasta 140 millones</p>
                  </div>
                  <div>
                    <p className="text-sm font-semibold text-[#f26522]">Condiciones</p>
                    <p>Ser pensionado de alguna de las pagadurías o fondos de pensiones con los cuales tenemos convenio.</p>
                  </div>
                </div>
              </div>

              <div className="relative">
                <div className="absolute inset-6 rounded-full bg-orange-100 blur-3xl opacity-40" aria-hidden />
                <img
                  src="https://images.unsplash.com/photo-1500530855697-b586d89ba3ee?auto=format&fit=crop&w=720&q=80"
                  alt="Cliente sonriente en vehículo"
                  className="relative mx-auto h-80 w-80 rounded-full object-cover shadow-2xl ring-4 ring-white"
                />
              </div>
            </div>
          </div>
        </section>

        <section id="simulador" className="mx-auto grid max-w-7xl items-start gap-10 px-6 md:grid-cols-[1.1fr,0.9fr]">
          <div className="rounded-3xl bg-white p-8 shadow-xl ring-1 ring-slate-200">
            <h4 className="text-2xl font-extrabold text-[#0d2f62]">Simula tu crédito aquí</h4>
            <div className="mt-6 space-y-6">
              <div className="space-y-2">
                <p className="text-sm font-semibold text-[#f26522]">Monto</p>
                <div className="text-lg font-bold text-[#0d2f62]">{formattedAmount}</div>
                <Slider
                  value={[amount]}
                  min={minAmount}
                  max={maxAmount}
                  step={100_000}
                  onValueChange={(value) => setAmount(value[0] ?? amount)}
                />
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
                    <SelectItem value="12">12 meses</SelectItem>
                    <SelectItem value="24">24 meses</SelectItem>
                    <SelectItem value="36">36 meses</SelectItem>
                    <SelectItem value="48">48 meses</SelectItem>
                    <SelectItem value="60">60 meses</SelectItem>
                  </SelectContent>
                </Select>
              </div>

              <Button className="w-full bg-[#f26522] text-white hover:bg-[#d85314]">Simular</Button>
            </div>
          </div>

          <div className="space-y-6 text-slate-700">
            <div className="relative">
              <div className="absolute inset-10 rounded-full bg-[#0d2f62]/10 blur-3xl" aria-hidden />
              <img
                src="https://images.unsplash.com/photo-1470770841072-f978cf4d019e?auto=format&fit=crop&w=720&q=80"
                alt="Paisaje tranquilo"
                className="relative mx-auto h-72 w-72 rounded-full object-cover shadow-xl ring-4 ring-white"
              />
            </div>
            <ul className="space-y-3">
              <li className="flex items-center gap-3 text-sm">
                <CheckCircle2 className="h-5 w-5 text-[#f26522]" /> Somos 100% digitales
              </li>
              <li className="flex items-center gap-3 text-sm">
                <CheckCircle2 className="h-5 w-5 text-[#f26522]" /> Trabajamos con reportados y pensionados
              </li>
            </ul>
          </div>
        </section>

        <section id="quienes" className="bg-white py-14 shadow-inner">
          <div className="mx-auto max-w-7xl px-6 text-center">
            <h5 className="text-3xl font-extrabold text-[#0d2f62]">¿Quiénes Somos?</h5>
            <p className="mt-3 text-sm text-slate-600">
              Somos KrediPlus, especializados en créditos de libranza para pensionados y personas reportadas.
              Ofrecemos soluciones financieras sólidas y confiables con un enfoque profesional.
            </p>

            <div className="mt-10 grid gap-6 md:grid-cols-2">
              <div className="rounded-2xl bg-white p-8 shadow-lg ring-1 ring-slate-200">
                <p className="text-lg font-bold text-[#f26522]">Misión</p>
                <p className="mt-3 text-sm text-slate-700">
                  Ayudar a pensionados y personas reportadas mediante créditos de libranza accesibles, siendo el puente hacia
                  oportunidades financieras que cumplan sus metas y sueños con soluciones innovadoras orientadas al cliente.
                </p>
              </div>
              <div className="rounded-2xl bg-white p-8 shadow-lg ring-1 ring-slate-200">
                <p className="text-lg font-bold text-[#f26522]">Visión</p>
                <p className="mt-3 text-sm text-slate-700">
                  Consolidarnos como referente confiable en créditos de libranza por nuestro compromiso con la atención
                  personalizada y la solidez financiera, generando un impacto positivo en la vida de nuestros clientes.
                </p>
              </div>
            </div>
          </div>
        </section>
      </main>

      {/* Botón flotante de chatbot */}
      <button
        aria-label="Abrir chatbot"
        onClick={() => setIsChatOpen(true)}
        className="fixed bottom-6 right-6 z-40 flex h-14 w-14 items-center justify-center rounded-full bg-[#f26522] text-white shadow-lg shadow-orange-200 transition hover:scale-105"
      >
        <MessageCircle className="h-7 w-7" />
      </button>

      {isChatOpen && (
        <>
          <div
            className="fixed inset-0 z-40 bg-black/50 backdrop-blur-[1px]"
            onClick={() => setIsChatOpen(false)}
          />

          <div className="fixed bottom-20 right-6 z-50 w-[360px] max-w-[calc(100%-2rem)] rounded-2xl bg-white shadow-2xl ring-1 ring-slate-200">
            <div className="flex items-center justify-between border-b px-4 py-3">
              <div>
                <p className="text-sm font-semibold text-[#0d2f62]">Contáctanos</p>
                <p className="text-xs text-slate-500">¿Cómo podemos ayudarte?</p>
              </div>
              <button
                className="rounded-full p-1 text-slate-500 transition hover:bg-slate-100"
                onClick={() => setIsChatOpen(false)}
                aria-label="Cerrar chatbot"
              >
                <X className="h-5 w-5" />
              </button>
            </div>

            <div className="h-64 bg-slate-50/80 px-4 py-3 text-center text-sm text-slate-500">
              <p className="mt-20">Estamos en línea para ayudarte.</p>
              <p className="text-xs text-slate-400">Escribe tu mensaje abajo.</p>
            </div>

            <div className="flex items-center gap-2 border-t px-4 py-3">
              <input
                type="text"
                placeholder="Escribe tu mensaje..."
                className="flex-1 rounded-lg border border-slate-200 px-3 py-2 text-sm outline-none focus:border-[#f26522] focus:ring-2 focus:ring-[#f26522]/20"
              />
              <Button
                size="icon"
                className="h-10 w-10 bg-[#f26522] text-white hover:bg-[#d85314]"
                aria-label="Enviar mensaje"
              >
                <Send className="h-4 w-4" />
              </Button>
            </div>
          </div>
        </>
      )}

      <footer id="contacto" className="mt-4 bg-[#0d2f62] py-12 text-white">
        <div className="mx-auto grid max-w-7xl gap-10 px-6 md:grid-cols-4 md:items-start">
          <div className="space-y-2">
            <div className="flex items-center gap-3 text-lg font-bold">
              <div className="flex h-10 w-10 items-center justify-center rounded-full bg-white/10">K+</div>
              <span>KrediPlus</span>
            </div>
            <p className="text-sm text-slate-200">Soluciones financieras a tu alcance.</p>
          </div>

          <div className="space-y-2">
            <p className="text-sm font-semibold uppercase tracking-wide text-orange-200">Puedes comunicarte al</p>
            <p className="flex items-center gap-2 text-sm"><Phone className="h-4 w-4" /> Línea telefónica: 304-589-7423</p>
            <p className="flex items-center gap-2 text-sm"><Phone className="h-4 w-4" /> WhatsApp: 304-589-7423</p>
          </div>

          <div className="space-y-2">
            <p className="text-sm font-semibold uppercase tracking-wide text-orange-200">Nuestras redes</p>
            <p className="text-sm">Instagram: @KrediPlus</p>
            <p className="text-sm">Facebook: KrediPlus</p>
          </div>

          <div className="space-y-2">
            <p className="text-sm font-semibold uppercase tracking-wide text-orange-200">Página web</p>
            <p className="text-sm">Sitio oficial</p>
            <p className="text-sm">www.krediplus.com.co</p>
          </div>
        </div>
        <p className="mt-10 text-center text-xs text-slate-300">© 2025 Todos los derechos reservados. KrediPlus.</p>
      </footer>
    </div>
  )
}

export const indexRoute = new Route({
  getParentRoute: () => rootRoute,
  path: '/',
  component: IndexPage,
})