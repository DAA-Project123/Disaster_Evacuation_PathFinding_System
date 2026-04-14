import axios from 'axios'
import type {
  AlgoRecommended,
  AlgoResult,
  CityGraph,
  CityMeta,
  KnapsackResult,
  Mission,
  SimSnapshot,
} from '../types'

const api = axios.create({
  baseURL: import.meta.env.VITE_API_URL ?? 'http://localhost:8000/api',
  headers: { 'Content-Type': 'application/json' },
})

export async function getCities(): Promise<CityMeta[]> {
  const { data } = await api.get<CityMeta[]>('/cities')
  return data
}

export async function getCityGraph(cityName: string): Promise<CityGraph> {
  const { data } = await api.get<CityGraph>(`/cities/${encodeURIComponent(cityName)}/graph`)
  return data
}

export async function switchCity(city: string): Promise<{ ok: boolean; active_city: string }> {
  const { data } = await api.post('/cities/switch', { city })
  return data
}

export async function getSimState(): Promise<Record<string, unknown>> {
  const { data } = await api.get('/simulation/state')
  return data
}

export async function getSnapshot(): Promise<SimSnapshot> {
  const { data } = await api.get<SimSnapshot>('/simulation/snapshot')
  return data
}

export async function startSim(): Promise<void> {
  await api.post('/simulation/start')
}

export async function pauseSim(): Promise<void> {
  await api.post('/simulation/pause')
}

export async function resumeSim(): Promise<void> {
  await api.post('/simulation/resume')
}

export async function resetSim(): Promise<void> {
  await api.post('/simulation/reset')
}

export async function setSimSpeed(seconds: number): Promise<void> {
  await api.post('/simulation/speed', { seconds })
}

export async function advanceMission(missionId: string): Promise<Mission> {
  const { data } = await api.post<Mission>(`/simulation/advance-mission/${missionId}`)
  return data
}

export async function getDisasters(): Promise<unknown[]> {
  const { data } = await api.get('/disasters')
  return data
}

export async function triggerDisaster(payload: {
  type: string
  severity: string
  epicenter_node: string
  radius: number
  city?: string
}): Promise<{ event: unknown }> {
  const { data } = await api.post('/disasters/trigger', payload)
  return data
}

export async function blockRoad(u: string, v: string): Promise<{ ok: boolean; replans: unknown[] }> {
  const { data } = await api.post('/disasters/block-road', { u, v })
  return data
}

export async function unblockRoad(u: string, v: string): Promise<void> {
  await api.post('/disasters/unblock-road', { u, v })
}

export async function deleteDisaster(eventId: string): Promise<void> {
  await api.delete(`/disasters/${encodeURIComponent(eventId)}`)
}

export async function getMissions(city?: string): Promise<Mission[]> {
  const { data } = await api.get<Mission[]>('/missions', { params: city ? { city } : undefined })
  return data
}

export async function dispatchMission(payload: {
  team_id: string
  target_node: string
  algorithm: string
  city?: string
}): Promise<Mission> {
  const { data } = await api.post<Mission>('/missions/dispatch', payload)
  return data
}

export async function confirmRescue(missionId: string, peopleRescued: number): Promise<Mission> {
  const { data } = await api.post<Mission>(`/missions/${missionId}/confirm-rescue`, {
    people_rescued: peopleRescued,
  })
  return data
}

export async function startReturn(missionId: string): Promise<Mission> {
  const { data } = await api.post<Mission>(`/missions/${missionId}/start-return`)
  return data
}

export async function completeMission(missionId: string): Promise<Mission> {
  const { data } = await api.post<Mission>(`/missions/${missionId}/complete`)
  return data
}

export async function compareAlgorithms(payload: {
  start_node: string
  goal_node: string
  unit_type: 'ground' | 'helicopter'
  city?: string
}): Promise<{ recommended: AlgoRecommended; all_results: AlgoResult[]; scenario: unknown }> {
  const { data } = await api.post('/algorithms/compare', payload)
  return data
}

export async function runGreedy(payload: { team_id: string; strategy: 'nearest' | 'priority' }): Promise<
  Record<string, unknown>[]
> {
  const { data } = await api.post('/algorithms/greedy', payload)
  return data
}

export async function runKnapsack(payload: {
  team_id?: string | null
  city?: string
}): Promise<KnapsackResult> {
  const { data } = await api.post<KnapsackResult>('/algorithms/knapsack', payload)
  return data
}

export async function getResources(): Promise<Record<string, unknown>> {
  const { data } = await api.get('/resources')
  return data
}

export async function dispatchResource(payload: {
  resource_id: string
  quantity: number
  safe_zone_id: string
  safe_zone_name: string
}): Promise<unknown> {
  const { data } = await api.post('/resources/dispatch', payload)
  return data
}

export async function confirmDelivery(allocationId: string): Promise<void> {
  await api.post('/resources/deliver', { allocation_id: allocationId })
}

export async function restockResource(payload: {
  resource_id: string
  quantity: number
  reason: string
}): Promise<void> {
  await api.post('/resources/restock', payload)
}
