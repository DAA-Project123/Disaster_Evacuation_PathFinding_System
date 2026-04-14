import { theme } from '../../styles/theme'
import { Badge } from '../ui/Badge'
import { useCityStore } from '../../store/cityStore'
import { switchCity } from '../../api/client'
import { useQueryClient } from '@tanstack/react-query'

export function TopBar({
  title,
  tick,
  simTime,
  running,
}: {
  title: string
  tick: number
  simTime: number
  running: boolean
}) {
  const activeCity = useCityStore((s) => s.activeCity)
  const setCity = useCityStore((s) => s.setActiveCity)
  const qc = useQueryClient()

  return (
    <header
      style={{
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'space-between',
        padding: '16px 24px',
        borderBottom: `1px solid ${theme.colors.border}`,
        background: theme.colors.bg,
        position: 'sticky',
        top: 0,
        zIndex: 10,
      }}
    >
      <h1 style={{ fontSize: 20 }}>{title}</h1>
      <div style={{ display: 'flex', alignItems: 'center', gap: 16 }}>
        <select
          value={activeCity}
          onChange={async (e) => {
            const c = e.target.value
            await switchCity(c)
            setCity(c)
            void qc.invalidateQueries()
          }}
          style={{
            padding: '8px 12px',
            borderRadius: 8,
            background: theme.colors.surface,
            color: theme.colors.textPrimary,
            border: `1px solid ${theme.colors.border}`,
          }}
        >
          {['Veridian City', 'Harborfield', 'Maplecrest'].map((c) => (
            <option key={c} value={c}>
              {c}
            </option>
          ))}
        </select>
        <Badge label={running ? 'RUNNING' : 'PAUSED'} variant={running ? 'success' : 'gray'} />
        <span style={{ fontSize: 13, color: theme.colors.textMuted, fontFamily: theme.fonts.mono }}>
          tick {tick} | {simTime.toFixed(1)} min
        </span>
      </div>
    </header>
  )
}
