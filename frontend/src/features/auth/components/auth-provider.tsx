import { useEffect, type ReactNode } from 'react'
import type { Session } from '@supabase/supabase-js'

import { supabase } from '@/lib/supabase'
import { useAuthStore } from '@/store/auth-store'

interface AuthProviderProps {
  children: ReactNode
}

export function AuthProvider({ children }: AuthProviderProps) {
  useEffect(() => {
    const syncSession = (session: Session | null) => {
      useAuthStore.getState().setSession(session)
    }

    supabase.auth.getSession().then(({ data }) => {
      syncSession(data.session ?? null)
    })

    const {
      data: { subscription },
    } = supabase.auth.onAuthStateChange((_event, session) => {
      syncSession(session)
    })

    return () => {
      subscription.unsubscribe()
    }
  }, [])

  return <>{children}</>
}
