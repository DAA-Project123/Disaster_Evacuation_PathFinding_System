import clsx from 'clsx'
import { theme } from '../../styles/theme'

const variants: Record<string, { bg: string; color: string }> = {
  success: { bg: 'rgba(16,185,129,0.2)', color: theme.colors.success },
  warning: { bg: 'rgba(245,158,11,0.2)', color: theme.colors.warning },
  danger: { bg: 'rgba(239,68,68,0.2)', color: theme.colors.danger },
  info: { bg: 'rgba(59,130,246,0.2)', color: theme.colors.accent },
  purple: { bg: 'rgba(139,92,246,0.2)', color: theme.colors.purple },
  gray: { bg: 'rgba(75,85,99,0.3)', color: theme.colors.textSecondary },
}

export function Badge({
  label,
  variant = 'gray',
}: {
  label: string
  variant?: keyof typeof variants
}) {
  const v = variants[variant]
  return (
    <span
      className={clsx('badge')}
      style={{
        display: 'inline-flex',
        alignItems: 'center',
        padding: '2px 10px',
        borderRadius: 999,
        fontSize: 12,
        fontWeight: 500,
        background: v.bg,
        color: v.color,
      }}
    >
      {label}
    </span>
  )
}
