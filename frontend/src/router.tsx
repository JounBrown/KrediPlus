
import { createRouter, RootRoute, Outlet } from '@tanstack/router'

const rootRoute = new RootRoute({
  component: () => (
    <>
      <Outlet /> {/* El Outlet es donde se renderizarán las rutas hijas */}
    </>
  ),
})

// Importa tus archivos de ruta aquí
import { indexRoute } from './routes/index'

const routeTree = rootRoute.addChildren([
  // Añade tus rutas hijas aquí
  indexRoute,
])

export const router = createRouter({ routeTree })

declare module '@tanstack/router' {
  interface Register {
    router: typeof router
  }
}
