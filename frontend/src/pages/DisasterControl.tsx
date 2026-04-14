import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import { blockRoad, getDisasters, triggerDisaster, unblockRoad } from '../api/client'
import { CityMap } from '../components/map/CityMap'
import { DisasterCard } from '../components/disaster/DisasterCard'
import { DisasterForm } from '../components/disaster/DisasterForm'
import { RoadBlockPanel } from '../components/disaster/RoadBlockPanel'
import { theme } from '../styles/theme'
import { useCityGraph } from '../hooks/useCityGraph'
import { useCityStore } from '../store/cityStore'
import type { DisasterEvent } from '../types'
import { useSimulation } from '../hooks/useSimulation'

export function DisasterControl() {
  const qc = useQueryClient()
  const city = useCityStore((s) => s.activeCity)
  const { data: graph } = useCityGraph()
  const { data: disasters } = useQuery({ queryKey: ['disasters'], queryFn: getDisasters })
  const { agentPositions, snapshot } = useSimulation()

  const trig = useMutation({
    mutationFn: triggerDisaster,
    onSuccess: () => void qc.invalidateQueries(),
  })
  const blk = useMutation({
    mutationFn: ({ u, v }: { u: string; v: string }) => blockRoad(u, v),
    onSuccess: () => void qc.invalidateQueries(),
  })
  const ublk = useMutation({
    mutationFn: ({ u, v }: { u: string; v: string }) => unblockRoad(u, v),
    onSuccess: () => void qc.invalidateQueries(),
  })

  if (!graph) return <div style={{ color: theme.colors.textMuted }}>Loading…</div>

  const blocked: [string, string][] = []
  for (const ev of (disasters as DisasterEvent[]) ?? []) {
    if (!ev.active) continue
    for (const p of ev.blocked_edges ?? []) {
      if (p.length >= 2) blocked.push([p[0], p[1]])
    }
  }

  return (
    <div style={{ display: 'grid', gridTemplateColumns: '2fr 3fr', gap: 24 }}>
      <div>
        <h2 style={{ marginBottom: 16 }}>Create disaster</h2>
        <DisasterForm
          graph={graph}
          onSubmit={(p) => trig.mutate({ ...p, city })}
        />
        <div style={{ marginTop: 24 }}>
          <RoadBlockPanel
            graph={graph}
            onBlock={(u, v) => blk.mutate({ u, v })}
            onUnblock={(u, v) => ublk.mutate({ u, v })}
          />
        </div>
      </div>
      <div>
        <h2 style={{ marginBottom: 16 }}>Active disasters</h2>
        <div style={{ maxHeight: 360, overflow: 'auto' }}>
          {((disasters as DisasterEvent[]) ?? [])
            .filter((d) => d.active)
            .map((d) => (
              <DisasterCard key={d.event_id} event={d} />
            ))}
        </div>
        <h3 style={{ marginTop: 24 }}>Map</h3>
        <CityMap
          cityGraph={graph}
          blockedEdges={blocked}
          agentPositions={agentPositions}
          nodepeople={snapshot?.node_people}
          width={640}
          height={400}
        />
      </div>
    </div>
  )
}
