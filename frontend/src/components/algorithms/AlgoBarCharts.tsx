import { Bar } from 'react-chartjs-2'
import { useEffect } from 'react'
import { darkChartOptions, registerCharts } from '../../lib/chartTheme'
import { theme } from '../../styles/theme'
import type { AlgoResult } from '../../types'

export function AlgoBarCharts({ results }: { results: AlgoResult[] }) {
  useEffect(() => {
    registerCharts()
  }, [])

  const labels = results.map((r) => r.Algorithm)
  const opts = darkChartOptions()
  const bg = theme.colors.surfaceHigh
  const common = {
    labels,
    datasets: [
      {
        label: '',
        data: [] as number[],
        backgroundColor: bg,
        borderColor: theme.colors.borderHigh,
        borderWidth: 1,
      },
    ],
  }

  const explored = {
    ...common,
    datasets: [
      {
        ...common.datasets[0],
        label: 'Nodes explored',
        data: results.map((r) => (r['Path Found'] ? r['Nodes Explored'] : 0)),
      },
    ],
  }
  const time = {
    ...common,
    datasets: [
      {
        ...common.datasets[0],
        label: 'Time (ms)',
        data: results.map((r) => (r['Path Found'] ? r['Time (ms)'] : 0)),
      },
    ],
  }
  const plen = {
    ...common,
    datasets: [
      {
        ...common.datasets[0],
        label: 'Path length',
        data: results.map((r) => (r['Path Found'] ? r['Path Length'] : 0)),
      },
    ],
  }

  return (
    <div style={{ display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)', gap: 16, minHeight: 200 }}>
      <div style={{ height: 180 }}>
        <Bar data={explored} options={{ ...opts, indexAxis: 'y' }} />
      </div>
      <div style={{ height: 180 }}>
        <Bar data={time} options={{ ...opts, indexAxis: 'y' }} />
      </div>
      <div style={{ height: 180 }}>
        <Bar data={plen} options={{ ...opts, indexAxis: 'y' }} />
      </div>
    </div>
  )
}
