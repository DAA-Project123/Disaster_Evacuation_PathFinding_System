import {
  BarElement,
  CategoryScale,
  Chart as ChartJS,
  type ChartOptions,
  Legend,
  LinearScale,
  Title,
  Tooltip,
} from 'chart.js'

const gridColor = '#1f2937'
const textColor = '#9ca3af'

export function darkChartOptions(): ChartOptions<'bar'> {
  return {
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
      legend: { labels: { color: textColor } },
    },
    scales: {
      x: {
        ticks: { color: textColor },
        grid: { color: gridColor },
      },
      y: {
        ticks: { color: textColor },
        grid: { color: gridColor },
      },
    },
  }
}

let registered = false
export function registerCharts() {
  if (registered) return
  ChartJS.register(CategoryScale, LinearScale, BarElement, Title, Tooltip, Legend)
  registered = true
}
