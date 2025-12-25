import { useEffect, useState } from 'react'
import { Link } from '@tanstack/react-router'
import { Menu, X } from 'lucide-react'
import { cn } from '@/lib/utils'
import { AuthButton } from '@/features/auth/components/auth-button'
import { useAuthStore } from '@/store/auth-store'

interface SiteHeaderProps {
  active?: 'home' | 'admin'
}

const mobileNavClasses =
  'block py-3 text-base font-medium text-slate-700 hover:text-[#f26522] transition-colors'

export function SiteHeader({ active = 'home' }: SiteHeaderProps) {
  const user = useAuthStore((state) => state.user)
  const [isMenuOpen, setIsMenuOpen] = useState(false)
  const [isAtTop, setIsAtTop] = useState(true)

  useEffect(() => {
    const handleScroll = () => setIsAtTop(window.scrollY < 10)
    window.addEventListener('scroll', handleScroll, { passive: true })
    handleScroll()
    return () => window.removeEventListener('scroll', handleScroll)
  }, [])

  // En admin siempre usar colores oscuros (fondo claro)
  const useLight = isAtTop && active !== 'admin'

  const linkClasses = cn(
    'hover:text-[#f26522] transition-colors text-sm font-medium',
    useLight ? 'text-white' : 'text-slate-700'
  )

  return (
    <header
      className={cn(
        'fixed top-0 left-0 right-0 z-50 transition-all duration-300',
        isAtTop && active !== 'admin' ? 'bg-transparent' : 'bg-white/70 shadow-md backdrop-blur-lg',
      )}
    >
      <div className="mx-auto flex max-w-7xl items-center justify-between px-6 py-3">
        <a href="/" className="flex items-center gap-3">
          <div className="flex h-10 w-10 items-center justify-center rounded-full bg-orange-100 text-[#f26522]">
            <span className="text-xl font-black">K</span>
          </div>
          <div className="leading-tight">
            <p className={cn('text-sm font-semibold', useLight ? 'text-white/80' : 'text-slate-500')}>KrediPlus</p>
            <p className={cn('text-base font-bold', useLight ? 'text-white' : 'text-[#0d2f62]')}>Soluciones financieras</p>
          </div>
        </a>

        {/* Desktop nav */}
        <nav className="hidden items-center gap-6 md:flex">
          <a href="/#simulador" className={linkClasses}>
            Simulador
          </a>
          <a href="/#condiciones" className={linkClasses}>
            Condiciones
          </a>
          <a href="/#quienes" className={linkClasses}>
            ¿Quiénes Somos?
          </a>
          {user ? (
            <Link
              to="/admin"
              className={cn(
                linkClasses,
                active === 'admin' ? 'text-[#f26522] font-semibold' : undefined,
              )}
            >
              Administrador
            </Link>
          ) : null}
        </nav>

        <div className="flex items-center gap-3">
          <div className="hidden md:block">
            <AuthButton />
          </div>

          {/* Mobile hamburger */}
          <button
            className={cn(
              'flex h-10 w-10 items-center justify-center rounded-lg md:hidden',
              useLight ? 'text-white hover:bg-white/20' : 'text-slate-700 hover:bg-slate-100'
            )}
            onClick={() => setIsMenuOpen(!isMenuOpen)}
            aria-label={isMenuOpen ? 'Cerrar menú' : 'Abrir menú'}
          >
            {isMenuOpen ? <X className="h-6 w-6" /> : <Menu className="h-6 w-6" />}
          </button>
        </div>
      </div>

      {/* Mobile menu */}
      <nav
        className={cn(
          'overflow-hidden border-t border-slate-200 bg-white px-6 transition-all duration-300 ease-in-out md:hidden',
          isMenuOpen ? 'max-h-96 py-4 opacity-100' : 'max-h-0 py-0 opacity-0'
        )}
      >
        <a href="/#simulador" className={mobileNavClasses} onClick={() => setIsMenuOpen(false)}>
          Simulador
        </a>
        <a href="/#condiciones" className={mobileNavClasses} onClick={() => setIsMenuOpen(false)}>
          Condiciones
        </a>
        <a href="/#quienes" className={mobileNavClasses} onClick={() => setIsMenuOpen(false)}>
          ¿Quiénes Somos?
        </a>
        {user && (
          <Link
            to="/admin"
            className={cn(mobileNavClasses, active === 'admin' && 'text-[#f26522]')}
            onClick={() => setIsMenuOpen(false)}
          >
            Administrador
          </Link>
        )}
        <div className="mt-4 border-t border-slate-200 pt-4">
          <AuthButton />
        </div>
      </nav>
    </header>
  )
}
