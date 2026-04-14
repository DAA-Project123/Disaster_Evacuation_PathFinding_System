import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import { useEffect } from 'react'
import {
  advanceMission,
  getMissions,
  getSnapshot,
  pauseSim,
  resetSim,
  resumeSim,
  setSimSpeed,
  startSim,
} from '../api/client'
import { useSimulationStore } from '../store/simulationStore'
import { useCityStore } from '../store/cityStore'

export function useSimulation() {
  const queryClient = useQueryClient()
  const activeCity = useCityStore((s) => s.activeCity)
  const setSnapshot = useSimulationStore((s) => s.setSnapshot)

  const snapQ = useQuery({
    queryKey: ['snapshot'],
    queryFn: getSnapshot,
    refetchInterval: (q) => (q.state.data?.running ? 500 : 2000),
  })

  useEffect(() => {
    if (snapQ.data) setSnapshot(snapQ.data)
  }, [snapQ.data, setSnapshot])

  const missionsQ = useQuery({
    queryKey: ['missions', activeCity],
    queryFn: () => getMissions(activeCity),
  })

  const startMut = useMutation({
    mutationFn: startSim,
    onSuccess: () => {
      void queryClient.invalidateQueries({ queryKey: ['snapshot'] })
    },
  })
  const pauseMut = useMutation({
    mutationFn: pauseSim,
    onSuccess: () => void queryClient.invalidateQueries({ queryKey: ['snapshot'] }),
  })
  const resumeMut = useMutation({
    mutationFn: resumeSim,
    onSuccess: () => void queryClient.invalidateQueries({ queryKey: ['snapshot'] }),
  })
  const resetMut = useMutation({
    mutationFn: resetSim,
    onSuccess: () => {
      void queryClient.invalidateQueries()
    },
  })
  const speedMut = useMutation({
    mutationFn: setSimSpeed,
  })
  const advanceMut = useMutation({
    mutationFn: advanceMission,
    onSuccess: () => void queryClient.invalidateQueries(),
  })

  const snapshot = snapQ.data ?? null
  const activeMissions = (missionsQ.data ?? []).filter((m) => m.status !== 'complete')

  return {
    snapshot,
    isRunning: snapshot?.running ?? false,
    tick: snapshot?.tick ?? 0,
    agentPositions: snapshot?.agent_positions ?? {},
    activeMissions,
    missionsLoading: missionsQ.isLoading,
    startSim: () => startMut.mutate(),
    pauseSim: () => pauseMut.mutate(),
    resumeSim: () => resumeMut.mutate(),
    resetSim: () => resetMut.mutate(),
    setSpeed: (seconds: number) => speedMut.mutate(seconds),
    advanceMission: (id: string) => advanceMut.mutate(id),
    isLoading: snapQ.isLoading,
  }
}
