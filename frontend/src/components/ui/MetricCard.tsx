import { theme } from '../../styles/theme'

export function MetricCard({
  label,
  value,
  delta,
  deltaPositive,
  unit,
}: {
  label: string
  value: string | number
  delta?: string
  deltaPositive?: boolean
  unit?: string
}) {
  return (
    <div
      style={{
        background: theme.colors.surface,
        border: `1px solid ${theme.colors.border}`,
        borderRadius: 12,
        padding: '16px 20px',
        minWidth: 140,
      }}
    >
      <div style={{ fontSize: 12, color: theme.colors.textSecondary, marginBottom: 6 }}>{label}</div>
      <div style={{ display: 'flex', alignItems: 'baseline', gap: 8 }}>
        <span style={{ fontSize: 28, fontWeight: 700, fontFamily: theme.fonts.mono }}>{value}</span>
        {unit ? <span style={{ fontSize: 13, color: theme.colors.textMuted }}>{unit}</span> : null}
      </div>
      {delta ? (
        <div
          style={{
            marginTop: 8,
            fontSize: 12,
            color:
              deltaPositive === undefined
                ? theme.colors.textMuted
                : deltaPositive
                  ? theme.colors.success
                  : theme.colors.danger,
          }}
        >
          {delta}
        </div>
      ) : null}
    </div>
  )
}
