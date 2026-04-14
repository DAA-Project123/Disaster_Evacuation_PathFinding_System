import type { CSSProperties } from 'react'
import { theme } from '../../styles/theme'
import type { CityGraph, Mission } from '../../types'
import { Badge } from '../ui/Badge'
import { ProgressBar } from '../ui/ProgressBar'
import { StepChain } from '../ui/StepChain'
import { buildEdgeInfo } from '../map/graphUtils'

export function MissionCard({
  mission,
  graph,
  isRunning,
  simPaused,
  onConfirm,
  onStartReturn,
  onAdvance,
  peopleDefault,
}: {
  mission: Mission
  graph: CityGraph
  isRunning: boolean
  simPaused: boolean
  onConfirm: (id: string, n: number) => void
  onStartReturn: (id: string) => void
  onAdvance: (id: string) => void
  peopleDefault: number
}) {
  const edges = buildEdgeInfo(graph, mission.path)
  const total = Math.max(1, mission.path.length - 1)
  const step = mission.current_step
  const curName = mission.path_names[step] ?? mission.path[step]

  return (
    <div
      style={{
        background: theme.colors.surface,
        border: `1px solid ${theme.colors.border}`,
        borderRadius: 12,
        padding: 16,
        marginBottom: 16,
      }}
    >
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 12 }}>
        <div style={{ display: 'flex', gap: 10, alignItems: 'center' }}>
          <strong style={{ fontFamily: theme.fonts.mono }}>{mission.mission_id}</strong>
          <span style={{ color: theme.colors.textSecondary }}>{mission.team_name}</span>
          <Badge label={mission.algorithm_used} variant="info" />
          <Badge label={mission.status} variant="warning" />
        </div>
      </div>
      {mission.replanned ? (
        <div
          style={{
            background: 'rgba(245,158,11,0.15)',
            padding: 8,
            borderRadius: 8,
            marginBottom: 8,
            fontSize: 13,
          }}
        >
          Path was replanned. Algorithm: {mission.algorithm_used}
        </div>
      ) : null}
      <StepChain
        path={mission.path}
        pathNames={mission.path_names}
        currentStep={mission.current_step}
        edges={edges}
        status={mission.status}
      />
      <ProgressBar value={step} max={total} showLabel />
      <div style={{ fontSize: 12, color: theme.colors.textMuted, marginTop: 8 }}>
        Step {step} of {total} — Currently at: {curName}
      </div>
      <div
        style={{
          display: 'flex',
          gap: 16,
          marginTop: 12,
          fontSize: 12,
          color: theme.colors.textSecondary,
          flexWrap: 'wrap',
        }}
      >
        <span>Algorithm: {mission.algorithm_used}</span>
        <span>Path length: {mission.total_path_length}</span>
        <span>Nodes explored: {mission.nodes_explored}</span>
        <span>Time ms: {mission.time_ms?.toFixed?.(1) ?? mission.time_ms}</span>
        <span>Air: {mission.used_air_edges ? 'Y' : 'N'}</span>
      </div>
      <div style={{ display: 'flex', gap: 8, marginTop: 14, flexWrap: 'wrap' }}>
        {mission.status === 'en_route' && isRunning ? (
          <span style={{ fontSize: 12, color: theme.colors.textMuted }}>Auto-advancing while simulation runs.</span>
        ) : null}
        {mission.status === 'en_route' && (!isRunning || simPaused) ? (
          <button type="button" style={miniBtn} onClick={() => onAdvance(mission.mission_id)}>
            Advance Step Manually
          </button>
        ) : null}
        {mission.status === 'arrived' ? (
          <button type="button" style={miniBtn} onClick={() => onConfirm(mission.mission_id, peopleDefault)}>
            Confirm Rescue — {peopleDefault} people
          </button>
        ) : null}
        {mission.status === 'rescued' ? (
          <button type="button" style={miniBtn} onClick={() => onStartReturn(mission.mission_id)}>
            Begin Return Journey
          </button>
        ) : null}
        {mission.status === 'returning' && (!isRunning || simPaused) ? (
          <button type="button" style={miniBtn} onClick={() => onAdvance(mission.mission_id)}>
            Advance Return Step
          </button>
        ) : null}
        {mission.status === 'complete' ? (
          <span style={{ fontSize: 12, color: theme.colors.textMuted }}>Mission complete.</span>
        ) : null}
      </div>
    </div>
  )
}

const miniBtn: CSSProperties = {
  background: theme.colors.accent,
  color: '#fff',
  border: 'none',
  borderRadius: 8,
  padding: '8px 12px',
  cursor: 'pointer',
  fontSize: 13,
}
