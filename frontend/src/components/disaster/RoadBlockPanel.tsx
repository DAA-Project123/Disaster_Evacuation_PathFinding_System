import { useState } from 'react'
import { theme } from '../../styles/theme'
import type { CityGraph } from '../../types'

export function RoadBlockPanel({
  graph,
  onBlock,
  onUnblock,
}: {
  graph: CityGraph
  onBlock: (u: string, v: string) => void
  onUnblock: (u: string, v: string) => void
}) {
  const [edge, setEdge] = useState(() => {
    const e = graph.edges[0]
    return e ? `${e.source}|${e.target}` : ''
  })
  const [u, v] = edge.split('|')

  return (
    <div style={{ background: theme.colors.surface, borderRadius: 12, padding: 16, border: `1px solid ${theme.colors.border}` }}>
      <strong>Road control</strong>
      <select
        value={edge}
        onChange={(e) => setEdge(e.target.value)}
        style={{
          width: '100%',
          marginTop: 10,
          padding: 10,
          borderRadius: 8,
          background: theme.colors.surfaceHigh,
          color: theme.colors.textPrimary,
          border: `1px solid ${theme.colors.border}`,
        }}
      >
        {graph.edges.map((e) => (
          <option key={`${e.source}-${e.target}`} value={`${e.source}|${e.target}`}>
            {e.road_name ?? `${e.source}-${e.target}`}
          </option>
        ))}
      </select>
      <div style={{ display: 'flex', gap: 8, marginTop: 12 }}>
        <button
          type="button"
          onClick={() => u && v && onBlock(u, v)}
          style={{ flex: 1, padding: 10, borderRadius: 8, border: 'none', background: theme.colors.danger, color: '#fff', cursor: 'pointer' }}
        >
          Block
        </button>
        <button
          type="button"
          onClick={() => u && v && onUnblock(u, v)}
          style={{
            flex: 1,
            padding: 10,
            borderRadius: 8,
            border: `1px solid ${theme.colors.border}`,
            background: theme.colors.surfaceHigh,
            color: theme.colors.textPrimary,
            cursor: 'pointer',
          }}
        >
          Unblock
        </button>
      </div>
    </div>
  )
}
