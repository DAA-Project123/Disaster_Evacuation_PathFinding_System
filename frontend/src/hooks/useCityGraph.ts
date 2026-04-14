import { useQuery } from '@tanstack/react-query'
import { getCityGraph } from '../api/client'
import { useCityStore } from '../store/cityStore'
import { useEffect } from 'react'

export function useCityGraph() {
  const activeCity = useCityStore((s) => s.activeCity)
  const setCityGraph = useCityStore((s) => s.setCityGraph)

  const q = useQuery({
    queryKey: ['cityGraph', activeCity],
    queryFn: () => getCityGraph(activeCity),
  })

  useEffect(() => {
    if (q.data) setCityGraph(q.data)
  }, [q.data, setCityGraph])

  return q
}
