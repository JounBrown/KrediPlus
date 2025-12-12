import type { Session } from '@supabase/supabase-js'
import { supabase } from './supabase'

async function requireSession(): Promise<Session> {
  const { data, error } = await supabase.auth.getSession()

  if (error) {
    throw new Error(error.message || 'No fue posible validar la sesión actual.')
  }

  if (!data.session) {
    throw new Error('Tu sesión expiró. Vuelve a iniciar sesión e inténtalo de nuevo.')
  }

  return data.session
}

export async function fetchWithAuth(input: RequestInfo | URL, init: RequestInit = {}) {
  const session = await requireSession()
  const headers = new Headers(init.headers)
  headers.set('Authorization', `Bearer ${session.access_token}`)

  return fetch(input, {
    ...init,
    headers,
  })
}
