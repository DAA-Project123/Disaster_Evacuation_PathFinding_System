import type { CSSProperties } from 'react'
import { useQuery, useQueryClient } from '@tanstack/react-query'
import { useNavigate } from 'react-router-dom'
import { getCities, getDisasters, switchCity } from '../api/client'
import { CityMap } from '../components/map/CityMap'
import { DisasterCard } from '../components/disaster/DisasterCard'
import { MetricCard } from '../components/ui/MetricCard'
import { DataTable } from '../components/ui/DataTable'
import { theme } from '../styles/theme'
import { useCityGraph } from '../hooks/useCityGraph'
import { useCityStore } from '../store/cityStore'
import { useSimulation } from '../hooks/useSimulation'
import type { DisasterEvent } from '../types'

export function Dashboard() {
  const nav = useNavigate()
  const qc = useQueryClient()
  const activeCity = useCityStore((s) => s.activeCity)
  const setActiveCity = useCityStore((s) => s.setActiveCity)
  const { data: graph } = useCityGraph()
  const { data: cities } = useQuery({ queryKey: ['cities'], queryFn: getCities })
  const { data: disasters } = useQuery({ queryKey: ['disasters'], queryFn: getDisasters })
  const { agentPositions, snapshot } = useSimulation()

  if (!graph) return <div style={{ color: theme.colors.textMuted }}>Loading map…</div>

  const blocked: [string, string][] = []
  for (const ev of (disasters as DisasterEvent[]) ?? []) {
    if (!ev.active) continue
    for (const p of ev.blocked_edges ?? []) {
      if (p.length >= 2) blocked.push([p[0], p[1]])
    }
  }

  const missions = snapshot?.missions ?? []
  const paths = missions.map((m, i) => ({
    path: m.path,
    color: ['#22c55e', '#a855f7', '#f97316'][i % 3],
    width: 4,
  }))

  const rows = graph.nodes
    .filter((n) => (n.people_stranded ?? 0) > 0)
    .map((n) => ({
      zone: n.zone ?? '',
      stranded: n.people_stranded ?? 0,
      critical: n.injury_level === 'critical' ? 'Yes' : '',
      teams: '',
    }))
    .sort((a, b) => b.stranded - a.stranded)

  const meta = cities?.find((c) => c.name === activeCity)
  const safeZoneCount = graph.nodes.filter((n) => n.type === 'safe_zone').length

  return (
    <div>
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)', gap: 16, marginBottom: 20 }}>
        {(cities ?? []).map((c) => {
          const sel = c.name === activeCity
          return (
            <button
              key={c.name}
              type="button"
              onClick={async () => {
                await switchCity(c.name)
                setActiveCity(c.name)
                void qc.invalidateQueries()
              }}
              style={{
                textAlign: 'left',
                padding: 16,
                borderRadius: 12,
                border: `1px solid ${sel ? theme.colors.accent : theme.colors.border}`,
                background: sel ? 'rgba(59,130,246,0.12)' : theme.colors.surface,
                color: theme.colors.textPrimary,
                cursor: 'pointer',
                boxShadow: sel ? '0 4px 20px rgba(0,0,0,0.35)' : 'none',
              }}
            >
              <strong>{c.name}</strong>
              <div style={{ fontSize: 13, color: theme.colors.textSecondary, marginTop: 6 }}>{c.description}</div>
              <div style={{ fontSize: 12, color: theme.colors.textMuted, marginTop: 8 }}>
                {c.node_count} nodes · {c.active_disasters} active disasters
              </div>
            </button>
          )
        })}
      </div>
      <div style={{ display: 'flex', gap: 12, flexWrap: 'wrap', marginBottom: 20 }}>
        <MetricCard label="Total Nodes" value={graph.nodes.length} />
        <MetricCard label="Active Disasters" value={meta?.active_disasters ?? 0} />
        <MetricCard label="Blocked Roads" value={blocked.length} />
        <MetricCard
          label="Total Stranded"
          value={graph.nodes.reduce((s, n) => s + (n.people_stranded ?? 0), 0)}
        />
        <MetricCard label="Safe Zones Available" value={safeZoneCount} />
      </div>
      <div style={{ display: 'grid', gridTemplateColumns: '1.85fr 1fr', gap: 20 }}>
        <CityMap
          cityGraph={graph}
          highlightPaths={paths}
          blockedEdges={blocked}
          agentPositions={agentPositions}
          nodepeople={snapshot?.node_people}
          rescueUnits={{}}
          width={720}
          height={480}
        />
        <div>
          <h3 style={{ marginBottom: 12 }}>Active disasters</h3>
          <div style={{ maxHeight: 220, overflow: 'auto', marginBottom: 20 }}>
            {((disasters as DisasterEvent[]) ?? [])
              .filter((d) => d.active)
              .map((d) => (
                <DisasterCard key={d.event_id} event={d} />
              ))}
          </div>
          <h3 style={{ marginBottom: 12 }}>Stranded population</h3>
          <DataTable
            columns={[
              { key: 'zone', header: 'Zone' },
              { key: 'stranded', header: 'Stranded' },
              { key: 'critical', header: 'Critical' },
              { key: 'teams', header: 'Teams' },
            ]}
            rows={rows}
            getRowKey={(r, i) => `${r.zone}-${i}`}
          />
        </div>
      </div>
      <div style={{ display: 'flex', gap: 12, marginTop: 24 }}>
        <button type="button" style={btn} onClick={() => nav('/disaster')}>
          Go to Disaster Control
        </button>
        <button type="button" style={btn} onClick={() => nav('/rescue')}>
          Dispatch Rescue
        </button>
        <button type="button" style={btn} onClick={() => nav('/resources')}>
          Manage Resources
        </button>
      </div>
    </div>
  )
}

const btn: CSSProperties = {
  padding: '12px 18px',
  borderRadius: 10,
  border: `1px solid ${theme.colors.borderHigh}`,
  background: theme.colors.surfaceHigh,
  color: theme.colors.textPrimary,
  cursor: 'pointer',
}
