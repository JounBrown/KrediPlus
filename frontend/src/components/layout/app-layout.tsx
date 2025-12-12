import type { ReactNode } from 'react'
import { SiteHeader } from './site-header'
import { Footer } from './Footer'
import { cn } from '@/lib/utils'

type AppLayoutProps = {
  children: ReactNode
  headerActive?: 'home' | 'admin'
  showFooter?: boolean
  wrapperClassName?: string
  mainClassName?: string
}

export function AppLayout({
  children,
  headerActive = 'home',
  showFooter = true,
  wrapperClassName,
  mainClassName,
}: AppLayoutProps) {
  return (
    <div className={cn('min-h-screen bg-[hsl(var(--background))] text-slate-900', wrapperClassName)}>
      <SiteHeader active={headerActive} />
      <main className={cn('flex-1', mainClassName)}>{children}</main>
      {showFooter && <Footer />}
    </div>
  )
}
