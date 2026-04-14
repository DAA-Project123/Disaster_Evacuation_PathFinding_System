import { Outlet, useLocation } from 'react-router-dom'
import { Layout } from './components/layout/Layout'
import { useSimulation } from './hooks/useSimulation'

const titles: Record<string, string> = {
  '/': 'Dashboard',
  '/disaster': 'Disaster Control',
  '/rescue': 'Rescue Operations',
  '/resources': 'Resource Hub',
}

export function AppShell() {
  const loc = useLocation()
  const { tick, snapshot, isRunning } = useSimulation()
  const title = titles[loc.pathname] ?? 'DAA Rescue System'
  return (
    <Layout title={title} tick={tick} simTime={snapshot?.sim_time_min ?? 0} running={isRunning}>
      <Outlet />
    </Layout>
  )
}
