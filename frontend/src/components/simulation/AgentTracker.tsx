import { theme } from '../../styles/theme'
import type { RescueUnit } from '../../types'
import { Badge } from '../ui/Badge'
import { ProgressBar } from '../ui/ProgressBar'

export function AgentTracker({ units }: { units: RescueUnit[] }) {
  return (
    <div
      style={{
        display: 'grid',
        gridTemplateColumns: 'repeat(4, 1fr)',
        gap: 12,
      }}
    >
      {units.map((u) => {
        const fuelMax = u.fuel_capacity ?? 100
        const fuel = u.fuel_remaining ?? 0
        const fuelColor = fuel / fuelMax > 0.5 ? theme.colors.success : fuel / fuelMax > 0.2 ? theme.colors.warning : theme.colors.danger
        const st = u.status ?? 'available'
        const badgeVariant = st === 'available' ? 'success' : st === 'dispatched' ? 'warning' : 'info'
        return (
          <div
            key={u.unit_id}
            style={{
              background: theme.colors.surface,
              border: `1px solid ${theme.colors.border}`,
              borderRadius: 12,
              padding: 12,
            }}
          >
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
              <strong>{u.name}</strong>
              <Badge label={u.unit_type} variant="purple" />
            </div>
            <Badge label={st} variant={badgeVariant} />
            <div style={{ fontSize: 12, color: theme.colors.textSecondary, marginTop: 8 }}>Location: {u.current_node}</div>
            <div style={{ marginTop: 8 }}>
              <div style={{ fontSize: 11, color: theme.colors.textMuted }}>Fuel</div>
              <ProgressBar value={fuel} max={fuelMax} color={fuelColor} />
            </div>
            <div style={{ fontSize: 12, marginTop: 8 }}>Kits: {u.medical_kits ?? 0}</div>
            <div style={{ fontSize: 12, color: theme.colors.textMuted }}>
              Rescued: {u.total_rescued ?? 0}
            </div>
          </div>
        )
      })}
    </div>
  )
}
