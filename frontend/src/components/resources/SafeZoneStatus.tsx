import { theme } from '../../styles/theme'

export function SafeZoneStatus({
  zones,
}: {
  zones: Array<{ id: string; name?: string; capacity?: number; occupancy?: number }>
}) {
  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: 8 }}>
      {zones.map((z) => (
        <div
          key={z.id}
          style={{
            padding: 12,
            borderRadius: 8,
            background: theme.colors.surface,
            border: `1px solid ${theme.colors.border}`,
            fontSize: 13,
          }}
        >
          <strong>{z.name ?? z.id}</strong>
          <div style={{ color: theme.colors.textMuted }}>
            Occupancy {z.occupancy ?? 0} / {z.capacity ?? '—'}
          </div>
        </div>
      ))}
    </div>
  )
}
