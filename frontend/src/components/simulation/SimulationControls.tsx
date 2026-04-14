import type { CSSProperties } from 'react'
import { theme } from '../../styles/theme'
import { Badge } from '../ui/Badge'

export function SimulationControls({
  isRunning,
  onStart,
  onPause,
  onResume,
  onReset,
  onSpeed,
  tick,
  simTime,
}: {
  isRunning: boolean
  onStart: () => void
  onPause: () => void
  onResume: () => void
  onReset: () => void
  onSpeed: (s: number) => void
  tick: number
  simTime: number
}) {
  return (
    <div
      style={{
        display: 'flex',
        flexWrap: 'wrap',
        alignItems: 'center',
        gap: 12,
        padding: 16,
        background: theme.colors.surface,
        borderRadius: 12,
        border: `1px solid ${theme.colors.border}`,
        marginBottom: 20,
      }}
    >
      <button type="button" onClick={onStart} style={btn}>
        Start Simulation
      </button>
      <button type="button" onClick={onPause} style={btn}>
        Pause
      </button>
      <button type="button" onClick={onResume} style={btn}>
        Resume
      </button>
      <button type="button" onClick={onReset} style={btn}>
        Reset
      </button>
      <div style={{ display: 'flex', gap: 6, marginLeft: 8 }}>
        {[0.5, 1, 1.5, 2, 3].map((s) => (
          <button key={s} type="button" onClick={() => onSpeed(s)} style={{ ...btn, padding: '6px 10px' }}>
            {s}x
          </button>
        ))}
      </div>
      <Badge label={isRunning ? 'RUNNING' : 'PAUSED / IDLE'} variant={isRunning ? 'success' : 'gray'} />
      <span style={{ fontSize: 13, color: theme.colors.textSecondary, fontFamily: theme.fonts.mono }}>
        tick {tick} | {simTime.toFixed(1)} min
      </span>
    </div>
  )
}

const btn: CSSProperties = {
  background: theme.colors.surfaceHigh,
  color: theme.colors.textPrimary,
  border: `1px solid ${theme.colors.borderHigh}`,
  borderRadius: 8,
  padding: '8px 14px',
  cursor: 'pointer',
  fontSize: 13,
}
