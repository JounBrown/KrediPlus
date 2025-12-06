import { Route } from '@tanstack/router'
import { rootRoute } from '../router' // Importar rootRoute desde router.tsx

export const indexRoute = new Route({
  getParentRoute: () => rootRoute,
  path: '/',
  component: function Index() {
    return (
      <div className="p-2">
        <h3>¡Bienvenido!</h3>
      </div>
    )
  },
})