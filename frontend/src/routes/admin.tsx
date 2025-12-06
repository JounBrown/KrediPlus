import { useMemo, useState } from 'react'
import { Route } from '@tanstack/react-router'
import { rootRoute } from './root'
import { UploadPanel } from '@/features/admin/upload/components/upload-panel'
import { AdminTabs, type AdminTabId } from '@/features/admin/layout/admin-tabs'
import { RequestsPanel } from '@/features/admin/requests/components/requests-panel'
import { ClientTable } from '@/features/admin/clients/components/client-table'
import { SimulatorConfigTable } from '@/features/admin/simulator-config/components/config-table'
import { SimulatorConfigDialog } from '@/features/admin/simulator-config/components/config-dialog'
import { useSimulatorConfigs } from '@/features/admin/simulator-config/hooks/use-simulator-configs'
import { AppLayout } from '@/components/layout/app-layout'

function AdminPage() {
  const [activeTab, setActiveTab] = useState<AdminTabId>('requests')
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
  } = useSimulatorConfigs()

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
            <SimulatorConfigTable
              configs={simConfigs}
              selectedConfigId={selectedConfigId}
              selectedConfig={selectedConfig}
              onCreate={() => openDialog('create')}
              onEdit={(config) => openDialog('edit', config)}
              onSelect={handleSelectConfig}
              formatCurrency={(value) => currencyFormatter.format(value)}
            />
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
      />
    </>
  )
}

export const adminRoute = new Route({
  getParentRoute: () => rootRoute,
  path: 'admin',
  component: AdminPage,
})
