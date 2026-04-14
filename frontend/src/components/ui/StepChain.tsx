import { motion } from 'framer-motion'
import { ChevronRight } from 'lucide-react'
import { theme } from '../../styles/theme'
import type { EdgeInfo, MissionStatus } from '../../types'

export function StepChain({
  path,
  pathNames,
  currentStep,
  edges,
  status,
}: {
  path: string[]
  pathNames: string[]
  currentStep: number
  edges: EdgeInfo[]
  status: MissionStatus
}) {
  return (
    <div
      style={{
        display: 'flex',
        alignItems: 'center',
        gap: 4,
        overflowX: 'auto',
        paddingBottom: 8,
        scrollbarWidth: 'thin',
      }}
    >
      {path.map((nodeId, i) => {
        const name = pathNames[i] ?? nodeId
        const isPast = i < currentStep
        const isCur = i === currentStep
        const isFuture = i > currentStep
        let bg: string = theme.colors.surfaceHigh
        let fg: string = theme.colors.textSecondary
        if (isPast) {
          bg = theme.colors.success
          fg = '#fff'
        }
        if (isCur) {
          bg = theme.colors.accent
          fg = '#fff'
        }
        if (isFuture) {
          bg = theme.colors.border
          fg = theme.colors.textMuted
        }
        const edge = edges[i]
        return (
          <div key={`${nodeId}-${i}`} style={{ display: 'flex', alignItems: 'center', gap: 4 }}>
            <motion.div
              animate={isCur && status === 'en_route' ? { scale: [1, 1.05, 1] } : { scale: 1 }}
              transition={{ repeat: isCur && status === 'en_route' ? Infinity : 0, duration: 1.2 }}
              style={{
                padding: '6px 12px',
                borderRadius: 999,
                background: bg,
                color: fg,
                fontSize: 12,
                fontWeight: 600,
                whiteSpace: 'nowrap',
                border: `1px solid ${theme.colors.borderHigh}`,
              }}
            >
              {name}
            </motion.div>
            {i < path.length - 1 ? (
              <div style={{ display: 'flex', alignItems: 'center', gap: 2, color: theme.colors.textMuted }}>
                <ChevronRight size={14} />
                {edge ? (
                  <span style={{ fontSize: 10, maxWidth: 72, overflow: 'hidden', textOverflow: 'ellipsis' }}>
                    {edge.road_name} {edge.km.toFixed(1)}km
                    {edge.air_only ? ' (air)' : ''}
                    {edge.blocked ? ' BLOCKED' : ''}
                  </span>
                ) : null}
              </div>
            ) : null}
          </div>
        )
      })}
    </div>
  )
}
