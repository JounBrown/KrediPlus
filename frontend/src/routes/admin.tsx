import { useEffect, useMemo, useState } from 'react'
import { Route, useNavigate } from '@tanstack/react-router'
import { rootRoute } from './root'
import { UploadPanel } from '@/features/admin/upload/components/upload-panel'
import { AdminTabs, type AdminTabId } from '@/features/admin/layout/admin-tabs'
import { RequestsPanel } from '@/features/admin/requests/components/requests-panel'
import { ClientTable } from '@/features/admin/clients/components/client-table'
import { SimulatorConfigTable } from '@/features/admin/simulator-config/components/config-table'
import { SimulatorConfigDialog } from '@/features/admin/simulator-config/components/config-dialog'
import { SimulatorConfigDeleteDialog } from '@/features/admin/simulator-config/components/delete-dialog'
import { useSimulatorConfigs } from '@/features/admin/simulator-config/hooks/use-simulator-configs'
import { useSimulatorConfigsQuery } from '@/features/simulator-config/hooks/use-simulator-configs-query'
import { AppLayout } from '@/components/layout/app-layout'
import { useAuthStore } from '@/store/auth-store'

function AdminPage() {
  const user = useAuthStore((state) => state.user)
  const navigate = useNavigate()

  useEffect(() => {
    if (!user) {
      navigate({ to: '/', replace: true })
    }
  }, [navigate, user])

  if (!user) {
    return null
  }
  const [activeTab, setActiveTab] = useState<AdminTabId>('requests')
  const {
    data: remoteSimulatorConfigs = [],
    isLoading: isSimulatorLoading,
    isError: simulatorError,
    error: simulatorErrorData,
  } = useSimulatorConfigsQuery()
  const activeBackendConfigId =
    remoteSimulatorConfigs.find((config) => config.isActive)?.id ?? remoteSimulatorConfigs[0]?.id ?? null
  const {
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
    savingConfig,
    saveError,
    updatingConfig,
    updateError,
    activatingConfig,
    activateError,
    deletingConfig,
    deleteError,
    deleteDialogOpen,
    configPendingDelete,
  } = useSimulatorConfigs(remoteSimulatorConfigs, activeBackendConfigId)

  const dialogSubmitting = dialogMode === 'create' ? savingConfig : updatingConfig
  const dialogErrorMessage = dialogMode === 'create' ? saveError?.message : updateError?.message

  const currencyFormatter = useMemo(() => {
    return new Intl.NumberFormat('es-CO', {
      style: 'currency',
      currency: 'COP',
      maximumFractionDigits: 0,
    })
  }, [])

  return (
    <>
      <AppLayout
        headerActive="admin"
        showFooter={false}
        wrapperClassName="bg-[#f4f7fb]"
        mainClassName="mx-auto flex w-full max-w-6xl flex-col gap-6 px-6 pb-16 pt-10"
      >
        <div className="rounded-3xl border border-slate-100 bg-white p-8 shadow-sm">
          <AdminTabs activeTab={activeTab} onSelect={setActiveTab} />

          {activeTab === 'requests' ? (
            <RequestsPanel />
          ) : activeTab === 'upload' ? (
            <UploadPanel onBackToRequests={() => setActiveTab('requests')} />
          ) : activeTab === 'clients' ? (
            <ClientTable />
          ) : (
            isSimulatorLoading ? (
              <div className="py-16 text-center text-sm text-slate-500">Cargando configuraciones...</div>
            ) : simulatorError ? (
              <div className="py-16 text-center text-sm text-red-600">
                {simulatorErrorData?.message || 'No fue posible cargar las configuraciones del simulador.'}
              </div>
            ) : (
              <SimulatorConfigTable
                configs={simConfigs}
                selectedConfigId={selectedConfigId}
                selectedConfig={selectedConfig}
                onCreate={() => openDialog('create')}
                onEdit={(config) => openDialog('edit', config)}
                onSelect={handleSelectConfig}
                onDeleteRequest={requestDeleteConfig}
                formatCurrency={(value) => currencyFormatter.format(value)}
                activating={activatingConfig}
                activateError={activateError?.message}
                deletingConfig={deletingConfig}
                deleteError={deleteError?.message}
              />
            )
          )}
        </div>
      </AppLayout>

      <SimulatorConfigDialog
        open={dialogOpen}
        mode={dialogMode}
        form={configForm}
        onOpenChange={(open) => {
          if (!open) closeDialog()
        }}
        onChange={handleFormChange}
        onSubmit={handleSaveConfig}
        submitting={dialogSubmitting}
        errorMessage={dialogErrorMessage}
      />

      <SimulatorConfigDeleteDialog
        open={deleteDialogOpen}
        config={configPendingDelete}
        onOpenChange={(open) => {
          if (!open) {
            closeDeleteDialog()
          }
        }}
        onConfirm={confirmDeleteConfig}
        deleting={deletingConfig}
        errorMessage={deleteError?.message}
      />
    </>
  )
}

export const adminRoute = new Route({
  getParentRoute: () => rootRoute,
  path: 'admin',
  component: AdminPage,
})
