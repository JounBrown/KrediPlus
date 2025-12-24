import { Phone, Instagram, Facebook, Globe } from 'lucide-react'

export function Footer() {
  return (
    <footer id="contacto" className="scroll-mt-20 mt-4 bg-[#0d2f62] py-12 text-white">
      {/* Mobile */}
      <div className="flex flex-col items-center gap-8 px-6 text-center md:hidden">
        <div className="space-y-2">
          <div className="flex items-center justify-center gap-3 text-lg font-bold">
            <div className="flex h-10 w-10 items-center justify-center rounded-full bg-orange-100 text-[#f26522]">
              <span className="text-xl font-black">K</span>
            </div>
            <span>KrediPlus</span>
          </div>
          <p className="text-sm text-slate-200">Soluciones financieras a tu alcance.</p>
        </div>

        <div className="space-y-2">
          <p className="text-sm font-semibold uppercase tracking-wide text-orange-200">Contáctanos</p>
          <p className="flex items-center justify-center gap-2 text-sm transition-colors hover:text-[#f26522]">
            <Phone className="h-4 w-4" /> 304-589-7423
          </p>
        </div>

        <div className="space-y-3">
          <p className="text-sm font-semibold uppercase tracking-wide text-orange-200">Síguenos</p>
          <div className="flex items-center justify-center gap-4">
            <span className="flex h-10 w-10 items-center justify-center rounded-full bg-white/10 transition-colors hover:bg-[#f26522]">
              <Instagram className="h-5 w-5" />
            </span>
            <span className="flex h-10 w-10 items-center justify-center rounded-full bg-white/10 transition-colors hover:bg-[#f26522]">
              <Facebook className="h-5 w-5" />
            </span>
            <span className="flex h-10 w-10 items-center justify-center rounded-full bg-white/10 transition-colors hover:bg-[#f26522]">
              <Globe className="h-5 w-5" />
            </span>
          </div>
        </div>
      </div>

      {/* Desktop */}
      <div className="mx-auto hidden max-w-7xl gap-10 px-6 md:grid md:grid-cols-4 md:items-start">
        <div className="space-y-2">
          <div className="flex items-center gap-3 text-lg font-bold">
            <div className="flex h-10 w-10 items-center justify-center rounded-full bg-orange-100 text-[#f26522]">
              <span className="text-xl font-black">K</span>
            </div>
            <span>KrediPlus</span>
          </div>
          <p className="text-sm text-slate-200">Soluciones financieras a tu alcance.</p>
        </div>

        <div className="space-y-2">
          <p className="text-sm font-semibold uppercase tracking-wide text-orange-200">Puedes comunicarte al</p>
          <p className="flex items-center gap-2 text-sm transition-colors hover:text-[#f26522]">
            <Phone className="h-4 w-4" /> Línea telefónica: 304-589-7423
          </p>
          <p className="flex items-center gap-2 text-sm transition-colors hover:text-[#f26522]">
            <Phone className="h-4 w-4" /> WhatsApp: 304-589-7423
          </p>
        </div>

        <div className="space-y-2">
          <p className="text-sm font-semibold uppercase tracking-wide text-orange-200">Nuestras redes</p>
          <p className="flex items-center gap-2 text-sm transition-colors hover:text-[#f26522]">
            <Instagram className="h-4 w-4" /> @KrediPlus
          </p>
          <p className="flex items-center gap-2 text-sm transition-colors hover:text-[#f26522]">
            <Facebook className="h-4 w-4" /> KrediPlus
          </p>
        </div>

        <div className="space-y-2">
          <p className="text-sm font-semibold uppercase tracking-wide text-orange-200">Página web</p>
          <p className="flex items-center gap-2 text-sm transition-colors hover:text-[#f26522]">
            <Globe className="h-4 w-4" /> www.krediplus.com.co
          </p>
        </div>
      </div>

      <p className="mt-10 text-center text-xs text-slate-300">© 2025 Todos los derechos reservados. KrediPlus.</p>
    </footer>
  )
}
