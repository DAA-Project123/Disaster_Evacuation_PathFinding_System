import type { ReactNode } from 'react'
import { theme } from '../../styles/theme'
import { Sidebar } from './Sidebar'
import { TopBar } from './TopBar'

export function Layout({
  children,
  title,
  tick,
  simTime,
  running,
}: {
  children: ReactNode
  title: string
  tick: number
  simTime: number
  running: boolean
}) {
  return (
    <div
      style={{
        display: 'grid',
        gridTemplateColumns: '240px 1fr',
        minHeight: '100vh',
        background: theme.colors.bg,
        color: theme.colors.textPrimary,
      }}
    >
      <Sidebar />
      <div style={{ display: 'flex', flexDirection: 'column', minWidth: 0 }}>
        <TopBar title={title} tick={tick} simTime={simTime} running={running} />
        <main style={{ flex: 1, overflow: 'auto', padding: 24 }}>{children}</main>
      </div>
    </div>
  )
}
