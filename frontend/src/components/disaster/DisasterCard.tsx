import { theme } from '../../styles/theme'
import type { DisasterEvent } from '../../types'
import { Badge } from '../ui/Badge'

export function DisasterCard({ event }: { event: DisasterEvent }) {
  return (
    <div
      style={{
        background: theme.colors.surface,
        border: `1px solid ${theme.colors.border}`,
        borderRadius: 12,
        padding: 14,
        marginBottom: 10,
      }}
    >
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <strong style={{ textTransform: 'capitalize' }}>{event.type}</strong>
        <Badge label={event.severity} variant="danger" />
      </div>
      <div style={{ fontSize: 12, color: theme.colors.textMuted, marginTop: 6 }}>{event.timestamp}</div>
      <div style={{ fontSize: 13, color: theme.colors.textSecondary, marginTop: 8 }}>
        Affected nodes: {event.affected_nodes?.length ?? 0} | Blocked roads: {event.blocked_edges?.length ?? 0}
      </div>
    </div>
  )
}
