import { theme } from '../../styles/theme'
import { Badge } from '../ui/Badge'
import { ProgressBar } from '../ui/ProgressBar'

export function HubInventory({ inventory }: { inventory: Array<Record<string, unknown>> }) {
  return (
    <div style={{ display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)', gap: 12 }}>
      {inventory.map((item) => {
        const id = String(item.resource_id ?? '')
        const name = String(item.name ?? id)
        const total = Number(item.total_stock ?? 0)
        const dist = Number(item.distributed ?? 0)
        const transit = Number(item.in_transit ?? 0)
        const avail = Math.max(0, total - dist - transit)
        const low = total > 0 && avail / total < 0.1
        return (
          <div
            key={id}
            style={{
              background: theme.colors.surface,
              border: `1px solid ${theme.colors.border}`,
              borderRadius: 12,
              padding: 14,
            }}
          >
            <div style={{ display: 'flex', justifyContent: 'space-between' }}>
              <strong>{name}</strong>
              {low ? <Badge label="Low" variant="danger" /> : null}
            </div>
            <div style={{ fontSize: 12, color: theme.colors.textMuted }}>{String(item.category ?? '')}</div>
            <div style={{ marginTop: 10 }}>
              <ProgressBar value={avail} max={total || 1} color={theme.colors.accent} showLabel />
            </div>
            <div style={{ fontSize: 12, marginTop: 8, color: theme.colors.textSecondary }}>
              Avail {avail} | Transit {transit} | Out {dist}
            </div>
          </div>
        )
      })}
    </div>
  )
}
