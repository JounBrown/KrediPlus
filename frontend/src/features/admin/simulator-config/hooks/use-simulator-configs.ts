import { useEffect, useMemo, useState } from 'react'
import {
  defaultSimulatorConfig,
  initialSimulatorConfigs,
  type SimulatorConfig,
} from '@/data/simulator-config'

export type SimulatorConfigForm = {
  tasaInteresMensual: string
  montoMinimo: string
  montoMaximo: string
  plazosDisponibles: string
}

const emptyForm: SimulatorConfigForm = {
  tasaInteresMensual: '',
  montoMinimo: '',
  montoMaximo: '',
  plazosDisponibles: '',
}

function parsePlazos(value: string) {
  return value
    .split(',')
    .map((item) => Number(item.trim()))
    .filter((item) => !Number.isNaN(item) && item > 0)
}

export function useSimulatorConfigs(
  initialConfigs: SimulatorConfig[] = initialSimulatorConfigs,
  defaultSelectionId: number | null = defaultSimulatorConfig.id,
) {
  const [simConfigs, setSimConfigs] = useState<SimulatorConfig[]>(initialConfigs)
  const [selectedConfigId, setSelectedConfigId] = useState<number | null>(
    defaultSelectionId ?? initialConfigs[0]?.id ?? null,
  )
  const [dialogOpen, setDialogOpen] = useState(false)
  const [dialogMode, setDialogMode] = useState<'create' | 'edit'>('create')
  const [activeSimConfig, setActiveSimConfig] = useState<SimulatorConfig | null>(null)
  const [configForm, setConfigForm] = useState<SimulatorConfigForm>(emptyForm)

  useEffect(() => {
    setSimConfigs(initialConfigs)
  }, [initialConfigs])

  useEffect(() => {
    setSelectedConfigId((prev) => {
      if (prev && initialConfigs.some((config) => config.id === prev)) {
        return prev
      }
      if (defaultSelectionId && initialConfigs.some((config) => config.id === defaultSelectionId)) {
        return defaultSelectionId
      }
      return initialConfigs[0]?.id ?? null
    })
  }, [initialConfigs, defaultSelectionId])

  const selectedConfig = useMemo(() => {
    if (!simConfigs.length) return null
    if (selectedConfigId == null) return simConfigs[0]
    return simConfigs.find((config) => config.id === selectedConfigId) ?? simConfigs[0]
  }, [simConfigs, selectedConfigId])

  const openDialog = (mode: 'create' | 'edit', config?: SimulatorConfig) => {
    setDialogMode(mode)

    if (mode === 'edit' && config) {
      setActiveSimConfig(config)
      setConfigForm({
        tasaInteresMensual: config.tasaInteresMensual.toString(),
        montoMinimo: config.montoMinimo.toString(),
        montoMaximo: config.montoMaximo.toString(),
        plazosDisponibles: config.plazosDisponibles.join(', '),
      })
    } else {
      setActiveSimConfig(null)
      setConfigForm(emptyForm)
    }

    setDialogOpen(true)
  }

  const closeDialog = () => {
    setDialogOpen(false)
    setActiveSimConfig(null)
  }

  const handleFormChange = (field: keyof SimulatorConfigForm, value: string) => {
    setConfigForm((prev) => ({ ...prev, [field]: value }))
  }

  const handleSaveConfig = () => {
    const parsedRate = parseFloat(configForm.tasaInteresMensual) || 0
    const parsedMin = parseInt(configForm.montoMinimo, 10) || 0
    const parsedMax = parseInt(configForm.montoMaximo, 10) || 0
    const parsedPlazos = parsePlazos(configForm.plazosDisponibles)
    const safePlazos = parsedPlazos.length ? parsedPlazos : [12]

    if (dialogMode === 'create') {
      const newConfig: SimulatorConfig = {
        id: Date.now(),
        createdAt: new Date().toISOString(),
        tasaInteresMensual: parsedRate,
        montoMinimo: parsedMin,
        montoMaximo: parsedMax,
        plazosDisponibles: safePlazos,
      }
      setSimConfigs((prev) => [newConfig, ...prev])
      setSelectedConfigId(newConfig.id)
    } else if (dialogMode === 'edit' && activeSimConfig) {
      const updatedConfig: SimulatorConfig = {
        ...activeSimConfig,
        tasaInteresMensual: parsedRate,
        montoMinimo: parsedMin,
        montoMaximo: parsedMax,
        plazosDisponibles: safePlazos,
      }
      setSimConfigs((prev) =>
        prev.map((config) => (config.id === updatedConfig.id ? updatedConfig : config)),
      )
      setSelectedConfigId(updatedConfig.id)
    }

    closeDialog()
  }

  const handleSelectConfig = (configId: number) => {
    setSelectedConfigId(configId)
  }

  return {
    simConfigs,
    selectedConfigId,
    selectedConfig,
    dialogOpen,
    dialogMode,
    configForm,
    openDialog,
    closeDialog,
    handleFormChange,
    handleSaveConfig,
    handleSelectConfig,
  }
}
