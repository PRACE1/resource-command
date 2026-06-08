import { StrictMode } from 'react'
import { createRoot } from 'react-dom/client'
import SovereignDashboard from '../SovereignDashboard.jsx'

createRoot(document.getElementById('root')).render(
  <StrictMode>
    <SovereignDashboard />
  </StrictMode>
)
