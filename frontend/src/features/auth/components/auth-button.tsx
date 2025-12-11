import { useState } from 'react'
import { useRouter, useRouterState } from '@tanstack/react-router'
import { useForm } from 'react-hook-form'
import { zodResolver } from '@hookform/resolvers/zod'
import { z } from 'zod'

import { Button } from '@/components/ui/button'
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from '@/components/ui/dialog'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { supabase } from '@/lib/supabase'
import { useAuthStore } from '@/store/auth-store'

const loginSchema = z.object({
  email: z.string().email('Ingresa un correo válido'),
  password: z.string().min(6, 'La contraseña debe tener al menos 6 caracteres'),
})

type LoginFormValues = z.infer<typeof loginSchema>

export function AuthButton() {
  const [open, setOpen] = useState(false)
  const [authError, setAuthError] = useState<string | null>(null)

  const router = useRouter()
  const currentPath = useRouterState({ select: (state) => state.location.pathname })
  const user = useAuthStore((state) => state.user)
  const setSession = useAuthStore((state) => state.setSession)
  const logout = useAuthStore((state) => state.logout)

  const {
    register,
    handleSubmit,
    formState: { errors, isSubmitting },
    reset,
  } = useForm<LoginFormValues>({
    resolver: zodResolver(loginSchema),
    defaultValues: {
      email: '',
      password: '',
    },
  })

  const handleOpenChange = (value: boolean) => {
    setOpen(value)
    if (!value) {
      reset()
      setAuthError(null)
    }
  }

  const closeDialog = () => {
    handleOpenChange(false)
  }

  const onSubmit = handleSubmit(async (values) => {
    setAuthError(null)

    const { data, error } = await supabase.auth.signInWithPassword(values)

    if (error) {
      setAuthError(error.message)
      return
    }

    setSession(data.session)
    closeDialog()
  })

  const handleLogout = async () => {
    try {
      await logout()
      setAuthError(null)

      const isOnAdmin = currentPath.startsWith('/admin')
      if (isOnAdmin) {
        router.navigate({ to: '/' })
      }
    } catch (error) {
      const message = error instanceof Error ? error.message : 'No se pudo cerrar sesión.'
      setAuthError(message)
    }
  }

  if (user) {
    return (
      <div className="flex flex-col items-end gap-1">
        <div className="flex items-center gap-3">
          <p className="hidden text-sm font-medium text-slate-600 md:block">{user.email}</p>
          <Button
            onClick={handleLogout}
            className="rounded-full bg-[#f26522] px-5 py-2 text-sm font-semibold text-white shadow hover:bg-[#d85314]"
          >
            Logout
          </Button>
        </div>
        {authError ? <p className="text-xs text-red-600">{authError}</p> : null}
      </div>
    )
  }

  return (
    <Dialog open={open} onOpenChange={handleOpenChange}>
      <DialogTrigger asChild>
        <Button className="rounded-full bg-[#f26522] px-5 py-2 text-sm font-semibold text-white shadow hover:bg-[#d85314]">
          Iniciar sesión
        </Button>
      </DialogTrigger>
      <DialogContent>
        <DialogHeader>
          <DialogTitle>Accede al panel</DialogTitle>
          <DialogDescription>Ingresa tus credenciales de administrador.</DialogDescription>
        </DialogHeader>
        <form className="space-y-4" onSubmit={onSubmit}>
          <div className="space-y-2">
            <Label htmlFor="email">Correo electrónico</Label>
            <Input id="email" type="email" placeholder="admin@krediplus.com" {...register('email')} />
            {errors.email ? (
              <p className="text-sm text-red-500">{errors.email.message}</p>
            ) : null}
          </div>
          <div className="space-y-2">
            <Label htmlFor="password">Contraseña</Label>
            <Input id="password" type="password" placeholder="••••••••" {...register('password')} />
            {errors.password ? (
              <p className="text-sm text-red-500">{errors.password.message}</p>
            ) : null}
          </div>
          {authError ? <p className="text-sm text-red-600">{authError}</p> : null}
          <DialogFooter>
            <Button type="submit" disabled={isSubmitting} className="w-full bg-[#f26522] hover:bg-[#d85314]">
              {isSubmitting ? 'Ingresando…' : 'Iniciar sesión'}
            </Button>
          </DialogFooter>
        </form>
      </DialogContent>
    </Dialog>
  )
}
