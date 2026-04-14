import { motion } from 'framer-motion'
import { theme } from '../../styles/theme'
import type { AlgoResult } from '../../types'

export function AlgoCompareTable({ results, recommended }: { results: AlgoResult[]; recommended: string }) {
  const nums = ['Path Length', 'Nodes Explored', 'Time (ms)'] as const
  const minFor = (key: (typeof nums)[number]) => {
    const vals = results.filter((r) => r['Path Found']).map((r) => Number(r[key]))
    return vals.length ? Math.min(...vals) : 0
  }
  const mins = {
    'Path Length': minFor('Path Length'),
    'Nodes Explored': minFor('Nodes Explored'),
    'Time (ms)': minFor('Time (ms)'),
  }

  return (
    <div style={{ overflow: 'auto', borderRadius: 8, border: `1px solid ${theme.colors.border}` }}>
      <table style={{ width: '100%', borderCollapse: 'collapse', fontSize: 13 }}>
        <thead>
          <tr style={{ background: theme.colors.surfaceHigh }}>
            {['Algorithm', 'Found', 'Steps', 'Nodes Explored', 'Time ms', 'Safety', 'Recommended'].map((h) => (
              <th
                key={h}
                style={{
                  textAlign: 'left',
                  padding: '8px 10px',
                  color: theme.colors.textSecondary,
                  borderBottom: `1px solid ${theme.colors.border}`,
                }}
              >
                {h}
              </th>
            ))}
          </tr>
        </thead>
        <tbody>
          {results.map((r) => {
            const isRec = r.Algorithm === recommended
            const rowBg = !r['Path Found']
              ? 'rgba(239,68,68,0.12)'
              : isRec
                ? 'rgba(59,130,246,0.15)'
                : 'transparent'
            return (
              <motion.tr
                key={r.Algorithm}
                layout
                style={{ background: rowBg }}
              >
                <td style={{ padding: '8px 10px', fontWeight: isRec ? 700 : 400 }}>{r.Algorithm}</td>
                <td style={{ padding: '8px 10px' }}>{r['Path Found'] ? 'Yes' : 'No'}</td>
                <td
                  style={{
                    padding: '8px 10px',
                    fontWeight: r['Path Found'] && r['Path Length'] === mins['Path Length'] ? 700 : 400,
                  }}
                >
                  {r['Path Length']}
                </td>
                <td
                  style={{
                    padding: '8px 10px',
                    fontWeight: r['Path Found'] && r['Nodes Explored'] === mins['Nodes Explored'] ? 700 : 400,
                  }}
                >
                  {r['Nodes Explored']}
                </td>
                <td
                  style={{
                    padding: '8px 10px',
                    fontWeight: r['Path Found'] && r['Time (ms)'] === mins['Time (ms)'] ? 700 : 400,
                  }}
                >
                  {r['Time (ms)'].toFixed(2)}
                </td>
                <td style={{ padding: '8px 10px' }}>{r['Safety Score'].toFixed(2)}</td>
                <td style={{ padding: '8px 10px' }}>{isRec ? 'Yes' : ''}</td>
              </motion.tr>
            )
          })}
        </tbody>
      </table>
    </div>
  )
}
