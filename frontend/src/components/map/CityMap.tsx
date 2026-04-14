import * as d3 from 'd3'
import { useEffect, useRef } from 'react'
import { theme } from '../../styles/theme'
import type { CityGraph, Mission, PathHighlight } from '../../types'

const TYPE_FILL: Record<string, string> = {
  safe_zone: theme.colors.success,
  hospital: theme.colors.accent,
  shelter: theme.colors.purple,
  bridge: theme.colors.warning,
  intersection: theme.colors.borderHigh,
}

function unitColor(unitType: string) {
  if (unitType === 'ambulance') return theme.colors.danger
  if (unitType === 'fire') return theme.colors.warning
  if (unitType === 'police') return theme.colors.accent
  if (unitType === 'helicopter') return theme.colors.purple
  return theme.colors.textSecondary
}

export function CityMap({
  cityGraph,
  highlightPaths = [],
  blockedEdges = [],
  agentPositions = {},
  nodepeople = {},
  activeMissions = [],
  rescueUnits = {},
  width = 900,
  height = 520,
  onNodeClick,
}: {
  cityGraph: CityGraph
  highlightPaths?: PathHighlight[]
  blockedEdges?: [string, string][]
  agentPositions?: Record<string, string>
  nodepeople?: Record<string, number>
  activeMissions?: Mission[]
  rescueUnits?: Record<string, { name?: string; unit_type?: string; status?: string }>
  width?: number
  height?: number
  onNodeClick?: (nodeId: string) => void
}) {
  const ref = useRef<SVGSVGElement | null>(null)

  useEffect(() => {
    const svgEl = ref.current
    if (!svgEl) return

    const nodes = cityGraph.nodes
    const edges = cityGraph.edges
    const pos = new Map(nodes.map((n) => [n.id, { x: n.x ?? 0, y: n.y ?? 0 }]))
    const blocked = new Set(blockedEdges.map(([u, v]) => [u, v].sort().join('|')))

    const xs = nodes.map((n) => n.x ?? 0)
    const ys = nodes.map((n) => n.y ?? 0)
    const minX = Math.min(...xs)
    const maxX = Math.max(...xs)
    const minY = Math.min(...ys)
    const maxY = Math.max(...ys)
    const pad = 40
    const sx = (x: number) => pad + ((x - minX) / (maxX - minX || 1)) * (width - 2 * pad)
    const sy = (y: number) => pad + ((y - minY) / (maxY - minY || 1)) * (height - 2 * pad)

    const svg = d3.select(svgEl)
    svg.selectAll('*').remove()
    svg.attr('viewBox', `0 0 ${width} ${height}`).style('background', theme.colors.bg)

    const root = svg.append('g')
    const zoom = d3
      .zoom<SVGSVGElement, unknown>()
      .scaleExtent([0.4, 4])
      .on('zoom', (ev) => {
        root.attr('transform', ev.transform.toString())
      })
    svg.call(zoom)

    const gEdges = root.append('g').attr('class', 'edges')
    const gPath = root.append('g').attr('class', 'path-overlays')
    const gNodes = root.append('g').attr('class', 'nodes')
    const gAgents = root.append('g').attr('class', 'agents')

    for (const e of edges) {
      const p0 = pos.get(e.source)
      const p1 = pos.get(e.target)
      if (!p0 || !p1) continue
      const key = [e.source, e.target].sort().join('|')
      const isAir = !!(e.air_only || e.road_type === 'air')
      const isBlocked = blocked.has(key)
      gEdges
        .append('line')
        .attr('x1', sx(p0.x))
        .attr('y1', sy(p0.y))
        .attr('x2', sx(p1.x))
        .attr('y2', sy(p1.y))
        .attr('stroke', isBlocked ? theme.colors.danger : isAir ? theme.colors.accent : theme.colors.borderHigh)
        .attr('stroke-width', isBlocked ? 2 : 1.5)
        .attr('stroke-dasharray', isAir ? '6,3' : isBlocked ? '4,4' : 'none')
        .attr('opacity', isBlocked ? 0.9 : isAir ? 0.6 : 0.7)
    }

    const pathColors = ['#22c55e', '#a855f7', '#f97316', '#06b6d4', '#eab308']
    highlightPaths.forEach((ph, idx) => {
      const col = ph.color || pathColors[idx % pathColors.length]
      const line = d3
        .line<{ x: number; y: number }>()
        .x((d) => sx(d.x))
        .y((d) => sy(d.y))
      const pts = ph.path
        .map((id) => pos.get(id))
        .filter(Boolean)
        .map((p) => ({ x: p!.x, y: p!.y }))
      if (pts.length < 2) return
      const dPath = line(pts as { x: number; y: number }[])
      if (!dPath) return
      const total = 500
      gPath
        .append('path')
        .attr('d', dPath)
        .attr('fill', 'none')
        .attr('stroke', col)
        .attr('stroke-width', ph.width ?? 3)
        .attr('stroke-dasharray', `${total}`)
        .attr('stroke-dashoffset', total)
        .transition()
        .duration(1000)
        .attr('stroke-dashoffset', 0)
    })

    for (const n of nodes) {
      const p = pos.get(n.id)
      if (!p) continue
      const stranded = nodepeople[n.id] ?? n.people_stranded ?? 0
      const r = n.type === 'safe_zone' ? 12 : n.type === 'intersection' ? 7 : 10
      const fill = TYPE_FILL[n.type ?? 'intersection'] ?? theme.colors.borderHigh
      let stroke = stranded > 0 ? theme.colors.danger : theme.colors.success
      if (stranded > 300) stroke = theme.colors.danger
      gNodes
        .append('circle')
        .attr('cx', sx(p.x))
        .attr('cy', sy(p.y))
        .attr('r', r)
        .attr('fill', fill)
        .attr('stroke', stroke)
        .attr('stroke-width', 2)
        .style('cursor', onNodeClick ? 'pointer' : 'default')
        .on('click', () => onNodeClick?.(n.id))
    }

    Object.entries(agentPositions).forEach(([uid, nodeId]) => {
      const p = pos.get(nodeId)
      if (!p) return
      const unit = rescueUnits[uid]
      const c = unitColor(unit?.unit_type ?? '')
      const g = gAgents.append('g').attr('data-unit', uid)
      g.append('polygon')
        .attr(
          'points',
          `${sx(p.x)},${sy(p.y) - 8} ${sx(p.x) - 7},${sy(p.y) + 6} ${sx(p.x) + 7},${sy(p.y) + 6}`,
        )
        .attr('fill', c)
        .attr('stroke', '#fff')
        .attr('stroke-width', 1)
      g.append('text')
        .attr('x', sx(p.x))
        .attr('y', sy(p.y) + 18)
        .attr('text-anchor', 'middle')
        .attr('fill', theme.colors.textSecondary)
        .attr('font-size', 9)
        .text(unit?.name ?? uid)
    })

  }, [cityGraph, highlightPaths, blockedEdges, agentPositions, nodepeople, activeMissions, rescueUnits, width, height, onNodeClick])

  return <svg ref={ref} width={width} height={height} style={{ borderRadius: 12, maxWidth: '100%' }} />
}
