import { Phone } from 'lucide-react'

export function Footer() {
  return (
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
          <p className="flex items-center gap-2 text-sm">
            <Phone className="h-4 w-4" /> Línea telefónica: 304-589-7423
          </p>
          <p className="flex items-center gap-2 text-sm">
            <Phone className="h-4 w-4" /> WhatsApp: 304-589-7423
          </p>
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
  )
}
