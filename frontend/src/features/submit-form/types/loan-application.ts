export type LoanApplication = {
  id: number
  created_at: string
  name: string
  cedula: string
  convenio: string
  telefono: string
  fecha_nacimiento: string
  monto_solicitado: number
  plazo: number
  estado: string
}

export type SubmitFormPayload = Pick<
  LoanApplication,
  'name' | 'cedula' | 'convenio' | 'telefono' | 'fecha_nacimiento' | 'monto_solicitado' | 'plazo' | 'estado'
> & {
  policyAccepted: boolean
}
