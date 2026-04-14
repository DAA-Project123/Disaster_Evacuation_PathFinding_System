import { BrowserRouter, Navigate, Route, Routes } from 'react-router-dom'
import { AppShell } from './App'
import { Dashboard } from './pages/Dashboard'
import { DisasterControl } from './pages/DisasterControl'
import { RescueOps } from './pages/RescueOps'
import { ResourceHub } from './pages/ResourceHub'

export function AppRouter() {
  return (
    <BrowserRouter>
      <Routes>
        <Route element={<AppShell />}>
          <Route path="/" element={<Dashboard />} />
          <Route path="/disaster" element={<DisasterControl />} />
          <Route path="/rescue" element={<RescueOps />} />
          <Route path="/resources" element={<ResourceHub />} />
          <Route path="*" element={<Navigate to="/" replace />} />
        </Route>
      </Routes>
    </BrowserRouter>
  )
}
