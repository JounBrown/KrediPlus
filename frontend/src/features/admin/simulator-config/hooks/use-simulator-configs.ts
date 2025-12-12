import { useEffect, useMemo, useState } from 'react'
import {
  defaultSimulatorConfig,
  initialSimulatorConfigs,
  type SimulatorConfig,
} from '@/data/simulator-config'
import { useCreateSimulatorConfig } from '@/features/simulator-config/hooks/use-create-simulator-config'
import { useActivateSimulatorConfig } from '@/features/simulator-config/hooks/use-activate-simulator-config'
import { useUpdateSimulatorConfig } from '@/features/simulator-config/hooks/use-update-simulator-config'
import { useDeleteSimulatorConfig } from '@/features/simulator-config/hooks/use-delete-simulator-config'

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

function normalizeRateInput(value: string) {
  const sanitized = value.replace(',', '.')
  const parsed = parseFloat(sanitized)
  if (!Number.isFinite(parsed)) {
    return 0
  }
  return parsed / 100
}

function formatRateForInput(value: number) {
  if (!Number.isFinite(value)) {
    return ''
  }
  const percentValue = value * 100
  return Number(percentValue.toFixed(4)).toString()
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
  const [deleteDialogOpen, setDeleteDialogOpen] = useState(false)
  const [configPendingDelete, setConfigPendingDelete] = useState<SimulatorConfig | null>(null)

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
        tasaInteresMensual: formatRateForInput(config.tasaInteresMensual),
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

  const createSimulatorConfigMutation = useCreateSimulatorConfig({
    onSuccess: (config) => {
      setSimConfigs((prev) => [config, ...prev])
      setSelectedConfigId(config.id)
      closeDialog()
    },
  })

  const activateSimulatorConfigMutation = useActivateSimulatorConfig({
    onSuccess: (activeConfig) => {
      setSimConfigs((prev) =>
        prev.map((config) => ({
          ...config,
          isActive: config.id === activeConfig.id,
        })),
      )
      setSelectedConfigId(activeConfig.id)
    },
  })

  const updateSimulatorConfigMutation = useUpdateSimulatorConfig({
    onSuccess: (config) => {
      setSimConfigs((prev) =>
        prev.map((existing) => (existing.id === config.id ? config : existing)),
      )
      setSelectedConfigId(config.id)
      closeDialog()
    },
  })

  const deleteSimulatorConfigMutation = useDeleteSimulatorConfig({
    onSuccess: (_message, configId) => {
      setSimConfigs((prev) => {
        const updated = prev.filter((config) => config.id !== configId)
        setSelectedConfigId((prevSelected) => {
          if (prevSelected === configId) {
            return updated[0]?.id ?? null
          }
          return prevSelected
        })
        return updated
      })
      setConfigPendingDelete(null)
      setDeleteDialogOpen(false)
    },
    onError: () => {
      setConfigPendingDelete((prev) => prev)
    },
  })

  const handleFormChange = (field: keyof SimulatorConfigForm, value: string) => {
    setConfigForm((prev) => ({ ...prev, [field]: value }))
  }

  const handleSaveConfig = () => {
    const parsedRate = normalizeRateInput(configForm.tasaInteresMensual)
    const parsedMin = parseInt(configForm.montoMinimo, 10) || 0
    const parsedMax = parseInt(configForm.montoMaximo, 10) || 0
    const parsedPlazos = parsePlazos(configForm.plazosDisponibles)
    const safePlazos = parsedPlazos.length ? parsedPlazos : [12]

    if (dialogMode === 'create') {
      createSimulatorConfigMutation.mutate({
        tasa_interes_mensual: parsedRate,
        monto_minimo: parsedMin,
        monto_maximo: parsedMax,
        plazos_disponibles: safePlazos,
      })
      return
    }

    if (dialogMode === 'edit' && activeSimConfig) {
      updateSimulatorConfigMutation.mutate({
        configId: activeSimConfig.id,
        payload: {
          tasa_interes_mensual: parsedRate,
          monto_minimo: parsedMin,
          monto_maximo: parsedMax,
          plazos_disponibles: safePlazos,
        },
      })
      return
    }

    closeDialog()
  }

  const handleSelectConfig = (configId: number) => {
    setSelectedConfigId(configId)
    activateSimulatorConfigMutation.mutate(configId)
  }

  const requestDeleteConfig = (config: SimulatorConfig) => {
    if (config.isActive) return
    setConfigPendingDelete(config)
    setDeleteDialogOpen(true)
  }

  const closeDeleteDialog = () => {
    setDeleteDialogOpen(false)
    setConfigPendingDelete(null)
    deleteSimulatorConfigMutation.reset()
  }

  const confirmDeleteConfig = () => {
    if (!configPendingDelete) return
    deleteSimulatorConfigMutation.mutate(configPendingDelete.id)
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
    requestDeleteConfig,
    closeDeleteDialog,
    confirmDeleteConfig,
    savingConfig: createSimulatorConfigMutation.isPending,
    saveError: createSimulatorConfigMutation.error,
    updatingConfig: updateSimulatorConfigMutation.isPending,
    updateError: updateSimulatorConfigMutation.error,
    activatingConfig: activateSimulatorConfigMutation.isPending,
    activateError: activateSimulatorConfigMutation.error,
    deletingConfig: deleteSimulatorConfigMutation.isPending,
    deleteError: deleteSimulatorConfigMutation.error,
    deleteDialogOpen,
    configPendingDelete,
  }
}
