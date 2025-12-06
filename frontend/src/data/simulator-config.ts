export type SimulatorConfig = {
  id: number
  createdAt: string
  tasaInteresMensual: number
  montoMinimo: number
  montoMaximo: number
  plazosDisponibles: number[]
}

export const initialSimulatorConfigs: SimulatorConfig[] = [
  {
    id: 1,
    createdAt: '2024-11-20T10:00:00.000Z',
    tasaInteresMensual: 1.2,
    montoMinimo: 1_000_000,
    montoMaximo: 140_000_000,
    plazosDisponibles: [12, 24, 36, 48, 60],
  },
  {
    id: 2,
    createdAt: '2024-11-15T12:30:00.000Z',
    tasaInteresMensual: 1.45,
    montoMinimo: 5_000_000,
    montoMaximo: 60_000_000,
    plazosDisponibles: [24, 36, 48, 60],
  },
]

export const defaultSimulatorConfig = initialSimulatorConfigs[0]
