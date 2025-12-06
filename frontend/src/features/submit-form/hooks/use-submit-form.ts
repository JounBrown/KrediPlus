import { useCallback, useState } from 'react'
import type { SubmitFormPayload } from '../types/loan-application'

type UseSubmitFormOptions = {
  onSubmit?: (payload: SubmitFormPayload) => Promise<void> | void
}

export function useSubmitForm(options: UseSubmitFormOptions = {}) {
  const { onSubmit } = options
  const [isSubmitting, setIsSubmitting] = useState(false)

  const handleSubmit = useCallback(
    async (event: React.FormEvent<HTMLFormElement>) => {
      event.preventDefault()
      if (!onSubmit) return

      const formData = new FormData(event.currentTarget)
      const payload: SubmitFormPayload = {
        name: formData.get('name')?.toString() ?? '',
        cedula: formData.get('cedula')?.toString() ?? '',
        convenio: formData.get('convenio')?.toString() ?? '',
        telefono: formData.get('telefono')?.toString() ?? '',
        fecha_nacimiento: formData.get('fecha_nacimiento')?.toString() ?? '',
        monto_solicitado: Number(formData.get('monto_solicitado') ?? 0),
        plazo: Number(formData.get('plazo') ?? 0),
        estado: formData.get('estado')?.toString() ?? 'pendiente',
        policyAccepted: formData.get('policyAccepted')?.toString() === 'true',
      }

      try {
        setIsSubmitting(true)
        await onSubmit(payload)
      } finally {
        setIsSubmitting(false)
      }
    },
    [onSubmit],
  )

  return {
    handleSubmit,
    isSubmitting,
  }
}
