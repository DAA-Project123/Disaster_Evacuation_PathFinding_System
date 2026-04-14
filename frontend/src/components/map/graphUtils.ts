import type { CityGraph, CityEdge, EdgeInfo } from '../../types'

export function buildEdgeLookup(graph: CityGraph) {
  const m = new Map<string, CityEdge>()
  for (const e of graph.edges) {
    const k = [e.source, e.target].sort().join('|')
    m.set(k, e)
  }
  return m
}

export function buildEdgeInfo(graph: CityGraph, path: string[], blocked?: Set<string>): EdgeInfo[] {
  const lookup = buildEdgeLookup(graph)
  const out: EdgeInfo[] = []
  for (let i = 0; i < path.length - 1; i++) {
    const u = path[i]
    const v = path[i + 1]
    const e = lookup.get([u, v].sort().join('|'))
    const bk = blocked?.has([u, v].sort().join('|')) ?? false
    out.push({
      from: u,
      to: v,
      road_name: e?.road_name ?? `${u}-${v}`,
      km: e?.distance_km ?? 0,
      air_only: !!(e?.air_only || e?.road_type === 'air'),
      blocked: bk,
    })
  }
  return out
}
