import { useState } from 'react'
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import {
  compareAlgorithms,
  confirmRescue,
  dispatchMission,
  getSimState,
  startReturn,
} from '../api/client'
import { CityMap } from '../components/map/CityMap'
import { AlgoBarCharts } from '../components/algorithms/AlgoBarCharts'
import { AlgoCompareTable } from '../components/algorithms/AlgoCompareTable'
import { KnapsackTable } from '../components/algorithms/KnapsackTable'
import { MissionCard } from '../components/simulation/MissionCard'
import { SimulationControls } from '../components/simulation/SimulationControls'
import { AgentTracker } from '../components/simulation/AgentTracker'
import { DataTable } from '../components/ui/DataTable'
import { theme } from '../styles/theme'
import { useCityGraph } from '../hooks/useCityGraph'
import { useSimulation } from '../hooks/useSimulation'
import { useKnapsack } from '../hooks/useAlgorithms'
import type { AlgoRecommended, AlgoResult, Mission, RescueUnit } from '../types'
import { ThreeMap } from '../components/map/ThreeMap'
import { useCityStore } from '../store/cityStore'

export function RescueOps() {
  const qc = useQueryClient()
  const { data: graph } = useCityGraph()
  const city = useCityStore((s) => s.activeCity)
  const {
    snapshot,
    isRunning,
    tick,
    agentPositions,
    activeMissions,
    startSim,
    pauseSim,
    resumeSim,
    resetSim,
    setSpeed,
    advanceMission,
  } = useSimulation()

  const { data: fullState } = useQuery({
    queryKey: ['simState'],
    queryFn: getSimState,
    refetchInterval: 2000,
  })

  const [teamId, setTeamId] = useState('')
  const [target, setTarget] = useState('')
  const [algo, setAlgo] = useState('recommended')
  const [compare, setCompare] = useState<{
    all_results: AlgoResult[]
    recommended: AlgoRecommended
  } | null>(null)
  const [show3d, setShow3d] = useState(false)
  const knapsack = useKnapsack()

  const simPaused = !isRunning

  const disp = useMutation({
    mutationFn: dispatchMission,
    onSuccess: () => void qc.invalidateQueries(),
  })
  const conf = useMutation({
    mutationFn: ({ id, n }: { id: string; n: number }) => confirmRescue(id, n),
    onSuccess: () => void qc.invalidateQueries(),
  })
  const ret = useMutation({
    mutationFn: startReturn,
    onSuccess: () => void qc.invalidateQueries(),
  })
  const cmp = useMutation({
    mutationFn: compareAlgorithms,
    onSuccess: (d) => setCompare(d),
  })

  if (!graph) return <div style={{ color: theme.colors.textMuted }}>Loading…</div>

  const victimRows: Record<string, unknown>[] = graph.nodes
    .filter((n) => (n.people_stranded ?? 0) > 0)
    .map((n) => ({
      id: n.id,
      node: n.name ?? n.id,
      zone: n.zone,
      stranded: n.people_stranded,
      injury: n.injury_level,
      survival: n.survival_chance,
      risk: '',
    }))
    .sort((a, b) => {
      const order = ['critical', 'high', 'medium', 'low', 'none']
      return order.indexOf(String(a.injury)) - order.indexOf(String(b.injury))
    })

  const ru = (fullState?.rescue_units ?? {}) as Record<string, RescueUnit>
  const units: RescueUnit[] = Object.values(ru)

  const paths = activeMissions.map((m: Mission, i: number) => ({
    path: m.path,
    color: ['#22c55e', '#38bdf8', '#f97316'][i % 3],
    width: 3,
  }))

  return (
    <div>
      <SimulationControls
        isRunning={isRunning}
        onStart={startSim}
        onPause={pauseSim}
        onResume={resumeSim}
        onReset={resetSim}
        onSpeed={setSpeed}
        tick={tick}
        simTime={snapshot?.sim_time_min ?? 0}
      />
      <button
        type="button"
        onClick={() => setShow3d((s) => !s)}
        style={{ marginBottom: 16, padding: '8px 12px', borderRadius: 8, cursor: 'pointer' }}
      >
        {show3d ? 'Switch to 2D View' : 'Switch to 3D View'}
      </button>
      {show3d ? <ThreeMap graph={graph} height={320} /> : null}

      <h2 style={{ margin: '24px 0 12px' }}>Teams</h2>
      <AgentTracker units={units} />

      <h2 style={{ margin: '24px 0 12px' }}>Active missions</h2>
      {activeMissions.map((m: Mission) => (
        <MissionCard
          key={m.mission_id}
          mission={m}
          graph={graph}
          isRunning={isRunning}
          simPaused={simPaused}
          onConfirm={(id, n) => conf.mutate({ id, n })}
          onStartReturn={(id) => ret.mutate(id)}
          onAdvance={(id) => advanceMission(id)}
          peopleDefault={m.people_at_target ?? 0}
        />
      ))}

      <h2 style={{ margin: '24px 0 12px' }}>Dispatch mission</h2>
      <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 20 }}>
        <div>
          <h3>Step 1: Target</h3>
          <DataTable
            columns={[
              { key: 'node', header: 'Node' },
              { key: 'zone', header: 'Zone' },
              { key: 'stranded', header: 'Stranded' },
              { key: 'injury', header: 'Injury' },
            ]}
            rows={victimRows}
            getRowKey={(r, i) => `${String(r.id)}-${i}`}
            onRowClick={(r) => setTarget(String(r.id))}
            rowClassName={(r) => (String(r.id) === target ? 'selected-row' : undefined)}
          />
        </div>
        <div>
          <h3>Step 2: Team & algorithms</h3>
          <input
            placeholder="Team id e.g. U001"
            value={teamId}
            onChange={(e) => setTeamId(e.target.value)}
            style={{ width: '100%', padding: 10, marginBottom: 8, borderRadius: 8 }}
          />
          <button
            type="button"
            onClick={() => {
              if (!teamId || !target) return
              const start = ru[teamId]?.current_node ?? ''
              if (!start) return
              cmp.mutate({
                start_node: start,
                goal_node: target,
                unit_type: ru[teamId]?.unit_type === 'helicopter' ? 'helicopter' : 'ground',
                city,
              })
            }}
            style={{ marginBottom: 12, padding: '8px 12px', borderRadius: 8, cursor: 'pointer' }}
          >
            Compare algorithms
          </button>
          {compare ? (
            <>
              <AlgoCompareTable results={compare.all_results} recommended={compare.recommended.algorithm} />
              <AlgoBarCharts results={compare.all_results} />
            </>
          ) : null}
          <CityMap
            cityGraph={graph}
            highlightPaths={
              compare?.recommended?.path?.length
                ? [{ path: compare.recommended.path, color: '#22c55e', width: 5 }]
                : []
            }
            width={480}
            height={280}
          />
        </div>
      </div>
      <div style={{ marginTop: 20 }}>
        <h3>Step 3: Confirm</h3>
        <select value={algo} onChange={(e) => setAlgo(e.target.value)} style={{ padding: 8, borderRadius: 8 }}>
          {['recommended', 'BFS', 'DFS', 'Dijkstra', 'A*', 'UCS'].map((a) => (
            <option key={a} value={a}>
              {a}
            </option>
          ))}
        </select>
        <button
          type="button"
          onClick={() => {
            if (!teamId || !target) return
            disp.mutate({ team_id: teamId, target_node: target, algorithm: algo, city })
          }}
          style={{ marginLeft: 12, padding: '10px 16px', borderRadius: 8, cursor: 'pointer' }}
        >
          Dispatch Mission
        </button>
      </div>

      <h2 style={{ margin: '24px 0 12px' }}>Knapsack</h2>
      <button
        type="button"
        onClick={() => knapsack.mutate({ team_id: teamId || null, city })}
        style={{ marginBottom: 12, padding: '8px 12px', borderRadius: 8, cursor: 'pointer' }}
      >
        Run knapsack
      </button>
      {knapsack.data ? (
        <KnapsackTable
          dpTable={knapsack.data.dp_table}
          traceback={knapsack.data.traceback}
          victims={[]}
          selected={[]}
        />
      ) : null}

      <h2 style={{ margin: '24px 0 12px' }}>Map overview</h2>
      <CityMap
        cityGraph={graph}
        highlightPaths={paths}
        agentPositions={agentPositions}
        nodepeople={snapshot?.node_people}
        width={800}
        height={480}
      />
    </div>
  )
}
