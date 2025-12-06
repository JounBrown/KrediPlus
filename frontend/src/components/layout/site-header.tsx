import { Link } from '@tanstack/react-router'
import { Users2 } from 'lucide-react'
import { Button } from '@/components/ui/button'
import { cn } from '@/lib/utils'

interface SiteHeaderProps {
  active?: 'home' | 'admin'
}

const navAnchorClasses =
  'hover:text-[#0d2f62] transition-colors text-sm font-medium text-slate-700'

export function SiteHeader({ active = 'home' }: SiteHeaderProps) {
  return (
    <header className="sticky top-0 z-30 bg-white/90 backdrop-blur shadow-sm">
      <div className="mx-auto flex max-w-7xl items-center justify-between px-6 py-3">
        <div className="flex items-center gap-3">
          <div className="flex h-10 w-10 items-center justify-center rounded-full bg-orange-100 text-[#f26522]">
            <span className="text-xl font-black">K</span>
          </div>
          <div className="leading-tight">
            <p className="text-sm font-semibold text-slate-500">KrediPlus</p>
            <p className="text-base font-bold text-[#0d2f62]">Soluciones financieras</p>
          </div>
        </div>

        <nav className="hidden items-center gap-6 md:flex">
          <a className="flex items-center gap-1 text-[#f26522] text-sm font-semibold" href="/#clientes">
            <Users2 className="h-4 w-4" /> Clientes 500+
          </a>
          <a href="/#simulador" className={navAnchorClasses}>
            Simulador
          </a>
          <a href="/#condiciones" className={navAnchorClasses}>
            Condiciones
          </a>
          <a href="/#quienes" className={navAnchorClasses}>
            ¿Quiénes Somos?
          </a>
          <a href="/#contacto" className={navAnchorClasses}>
            Contáctanos
          </a>
          <Link
            to="/admin"
            className={cn(
              navAnchorClasses,
              active === 'admin' ? 'text-[#f26522] font-semibold' : undefined,
            )}
          >
            Administrador
          </Link>
        </nav>

        <Button className="rounded-full bg-[#f26522] px-5 py-2 text-sm font-semibold text-white shadow hover:bg-[#d85314]">
          Logout
        </Button>
      </div>
    </header>
  )
}
