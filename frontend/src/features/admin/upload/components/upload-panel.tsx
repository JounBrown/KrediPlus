import { UploadCloud } from 'lucide-react'
import { Button } from '@/components/ui/button'

type UploadPanelProps = {
  onBackToRequests: () => void
}

export function UploadPanel({ onBackToRequests }: UploadPanelProps) {
  return (
    <section className="space-y-6">
      <div className="flex flex-wrap items-center justify-between gap-4">
        <div>
          <p className="text-lg font-semibold text-[#0d2f62]">Carga de Documentos</p>
          <p className="text-sm text-slate-500">
            Arrastra archivos PDF o DOCX para añadir soportes.
          </p>
        </div>
        <Button className="bg-[#0d2f62] text-white hover:bg-[#0b2772]" onClick={onBackToRequests}>
          Ver solicitudes
        </Button>
      </div>

      <div className="rounded-3xl border-2 border-dashed border-slate-300 bg-slate-50 px-6 py-12 text-center">
        <UploadCloud className="mx-auto h-10 w-10 text-[#0d2f62]" />
        <p className="mt-4 text-base font-semibold text-[#0d2f62]">
          Arrastra y suelta archivos PDF o DOCX aquí
        </p>
        <p className="text-sm text-slate-500">o haz clic para seleccionar archivos</p>
        <Button variant="outline" className="mt-6 border-[#0d2f62] text-[#0d2f62] hover:bg-white">
          Seleccionar archivos
        </Button>
      </div>
    </section>
  )
}
