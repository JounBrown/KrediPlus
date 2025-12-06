import { StrictMode } from 'react'
import { createRoot } from 'react-dom/client'
import './index.css'
// import App from './App.tsx' // No necesitamos App.tsx directamente ahora
import { RouterProvider } from '@tanstack/router' // Importar RouterProvider
import { router } from './router.tsx' // Importar la instancia del router

createRoot(document.getElementById('root')!).render(
  <StrictMode>
    <RouterProvider router={router} /> {/* Usar RouterProvider y pasarle el router */}
  </StrictMode>,
)
