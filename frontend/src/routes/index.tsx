import { useState } from 'react'
import { Route } from '@tanstack/react-router'
import { Button } from '@/components/ui/button'
import { rootRoute } from './root'
import { MessageCircle, Send, X } from 'lucide-react'
import { CreditSimulator } from '@/features/simulator/components/credit-simulator'
import { defaultSimulatorConfig } from '@/data/simulator-config'
import { SubmitFormCard } from '@/features/submit-form/components/submit-form-card'
import { AppLayout } from '@/components/layout/app-layout'

function IndexPage() {
  const [isChatOpen, setIsChatOpen] = useState(false)

  return (
    <AppLayout headerActive="home" mainClassName="space-y-16 pb-16">
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

            <SubmitFormCard />
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

        <section id="simulador" className="px-6">
          <CreditSimulator
            minAmount={defaultSimulatorConfig.montoMinimo}
            maxAmount={defaultSimulatorConfig.montoMaximo}
            monthlyRate={defaultSimulatorConfig.tasaInteresMensual}
            terms={defaultSimulatorConfig.plazosDisponibles}
            initialAmount={defaultSimulatorConfig.montoMinimo}
            initialTerm={defaultSimulatorConfig.plazosDisponibles[0]}
            showModeToggle
          />
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
    </AppLayout>
  )
}

export const indexRoute = new Route({
  getParentRoute: () => rootRoute,
  path: '/',
  component: IndexPage,
})