import * as d3 from 'd3'
import { useMemo } from 'react'
import { theme } from '../../styles/theme'

export function KnapsackTable({
  dpTable,
  traceback,
  victims: _victims,
  selected: _selected,
}: {
  dpTable: number[][]
  traceback: number[]
  victims: Array<Record<string, unknown>>
  selected: number[]
}) {
  void _victims
  void _selected
  const maxVal = useMemo(() => d3.max(dpTable.flat()) ?? 1, [dpTable])
  const color = useMemo(() => d3.scaleSequential(d3.interpolateViridis).domain([0, maxVal]), [maxVal])

  if (!dpTable.length) return null
  const cols = dpTable[0].length
  const showRows = Math.min(dpTable.length, 14)
  const showCols = Math.min(cols, 16)

  return (
    <div style={{ overflow: 'auto', maxHeight: 320 }}>
      <table style={{ borderCollapse: 'collapse', fontSize: 11 }}>
        <tbody>
          {dpTable.slice(0, showRows).map((row, i) => (
            <tr key={i}>
              {row.slice(0, showCols).map((cell, j) => (
                <td
                  key={j}
                  style={{
                    padding: 4,
                    border: `1px solid ${theme.colors.border}`,
                    background: color(cell),
                    color: cell > maxVal * 0.5 ? '#fff' : '#111',
                    textAlign: 'center',
                    minWidth: 36,
                  }}
                >
                  {Math.round(cell)}
                </td>
              ))}
            </tr>
          ))}
        </tbody>
      </table>
      <div style={{ fontSize: 11, color: theme.colors.textMuted, marginTop: 8 }}>
        Trace indices: {traceback.join(', ')}
      </div>
    </div>
  )
}
