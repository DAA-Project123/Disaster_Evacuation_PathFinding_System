import { useState } from 'react'
import { Flame, Mountain, TrafficCone, Waves } from 'lucide-react'
import { theme } from '../../styles/theme'
import type { CityGraph } from '../../types'

const TYPES: { id: string; label: string; icon: typeof Flame }[] = [
  { id: 'flood', label: 'Flood', icon: Waves },
  { id: 'earthquake', label: 'Earthquake', icon: Mountain },
  { id: 'fire', label: 'Fire', icon: Flame },
  { id: 'landslide', label: 'Landslide', icon: Mountain },
  { id: 'congestion', label: 'Congestion', icon: TrafficCone },
]

export function DisasterForm({
  graph,
  onSubmit,
}: {
  graph: CityGraph
  onSubmit: (payload: { type: string; severity: string; epicenter_node: string; radius: number }) => void
}) {
  const [type, setType] = useState('flood')
  const [severity, setSeverity] = useState('medium')
  const [epicenter, setEpicenter] = useState(graph.nodes[0]?.id ?? '')
  const [radius, setRadius] = useState(2)

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: 16 }}>
      <div>
        <div style={{ fontSize: 13, color: theme.colors.textSecondary, marginBottom: 8 }}>Disaster type</div>
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)', gap: 8 }}>
          {TYPES.map((t) => {
            const Icon = t.icon
            const sel = type === t.id
            return (
              <button
                key={t.id}
                type="button"
                onClick={() => setType(t.id)}
                style={{
                  display: 'flex',
                  flexDirection: 'column',
                  alignItems: 'center',
                  gap: 6,
                  padding: 12,
                  borderRadius: 10,
                  border: `1px solid ${sel ? theme.colors.accent : theme.colors.border}`,
                  background: sel ? 'rgba(59,130,246,0.12)' : theme.colors.surface,
                  color: theme.colors.textPrimary,
                  cursor: 'pointer',
                }}
              >
                <Icon size={22} />
                <span style={{ fontSize: 12 }}>{t.label}</span>
              </button>
            )
          })}
        </div>
      </div>
      <div>
        <div style={{ fontSize: 13, marginBottom: 8 }}>Severity</div>
        <div style={{ display: 'flex', gap: 6 }}>
          {(['low', 'medium', 'high', 'critical'] as const).map((s) => (
            <button
              key={s}
              type="button"
              onClick={() => setSeverity(s)}
              style={{
                flex: 1,
                padding: '8px 0',
                borderRadius: 8,
                border: `1px solid ${severity === s ? theme.colors.accent : theme.colors.border}`,
                background: severity === s ? 'rgba(59,130,246,0.15)' : theme.colors.surfaceHigh,
                color: theme.colors.textPrimary,
                cursor: 'pointer',
                textTransform: 'capitalize',
              }}
            >
              {s}
            </button>
          ))}
        </div>
      </div>
      <label style={{ display: 'flex', flexDirection: 'column', gap: 6, fontSize: 13 }}>
        Epicenter node
        <select
          value={epicenter}
          onChange={(e) => setEpicenter(e.target.value)}
          style={{
            padding: 10,
            borderRadius: 8,
            background: theme.colors.surfaceHigh,
            color: theme.colors.textPrimary,
            border: `1px solid ${theme.colors.border}`,
          }}
        >
          {graph.nodes.map((n) => (
            <option key={n.id} value={n.id}>
              {n.name ?? n.id} ({n.zone})
            </option>
          ))}
        </select>
      </label>
      <label style={{ display: 'flex', flexDirection: 'column', gap: 6, fontSize: 13 }}>
        Spread radius ({radius})
        <input
          type="range"
          min={1}
          max={5}
          value={radius}
          onChange={(e) => setRadius(Number(e.target.value))}
        />
      </label>
      <button
        type="button"
        onClick={() => onSubmit({ type, severity, epicenter_node: epicenter, radius })}
        style={{
          marginTop: 8,
          padding: '12px 16px',
          borderRadius: 10,
          border: 'none',
          background: theme.colors.danger,
          color: '#fff',
          fontWeight: 600,
          cursor: 'pointer',
        }}
      >
        Trigger Disaster
      </button>
    </div>
  )
}
