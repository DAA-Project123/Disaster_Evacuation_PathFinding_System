import { motion } from 'framer-motion'
import { theme } from '../../styles/theme'

export function ProgressBar({
  value,
  max,
  color,
  showLabel,
}: {
  value: number
  max: number
  color?: string
  showLabel?: boolean
}) {
  const pct = max > 0 ? Math.min(100, (value / max) * 100) : 0
  const fill = color ?? theme.colors.accent
  return (
    <div>
      <div
        style={{
          height: 8,
          borderRadius: 4,
          background: theme.colors.surfaceHigh,
          overflow: 'hidden',
        }}
      >
        <motion.div
          layout
          initial={false}
          animate={{ width: `${pct}%` }}
          transition={{ type: 'spring', stiffness: 300, damping: 30 }}
          style={{ height: '100%', background: fill, borderRadius: 4 }}
        />
      </div>
      {showLabel ? (
        <div style={{ fontSize: 11, color: theme.colors.textMuted, marginTop: 4 }}>
          {value} / {max}
        </div>
      ) : null}
    </div>
  )
}
