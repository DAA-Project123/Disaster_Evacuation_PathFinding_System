export interface CityNode {
  id: string
  name?: string
  type?: string
  x?: number
  y?: number
  zone?: string
  people_stranded?: number
  injury_level?: string
  survival_chance?: number
  rescue_cost?: number
  helipad?: boolean
}

export interface CityEdge {
  source: string
  target: string
  road_name?: string
  distance_km?: number
  base_travel_time_min?: number
  air_only?: boolean
  road_type?: string
}

export interface CityGraph {
  nodes: CityNode[]
  edges: CityEdge[]
  description?: string
}

export interface DisasterEvent {
  event_id: string
  type: string
  severity: string
  affected_nodes: string[]
  blocked_edges: [string, string][]
  timestamp: string
  active?: boolean
}

export interface RescueUnit {
  unit_id: string
  name: string
  unit_type: string
  current_node: string
  base_node?: string
  status: string
  fuel_remaining?: number
  fuel_capacity?: number
  medical_kits?: number
  total_rescued?: number
  capacity?: number
}

export type MissionStatus =
  | 'en_route'
  | 'arrived'
  | 'rescued'
  | 'returning'
  | 'complete'

export interface Mission {
  mission_id: string
  city: string
  team_id: string
  team_name: string
  team_type: string
  target_node: string
  target_name: string
  path: string[]
  path_names: string[]
  current_step: number
  algorithm_used: string
  why_selected?: string
  total_path_length: number
  nodes_explored: number
  time_ms: number
  status: MissionStatus
  used_air_edges?: boolean
  replanned?: boolean
  people_at_target?: number
  fuel_used?: number
}

export interface AlgoResult {
  Algorithm: string
  'Path Found': boolean
  Path: string[]
  'Path Length': number
  'Nodes Explored': number
  'Time (ms)': number
  'Safety Score': number
  used_air_edges?: boolean
  'Composite Score'?: number
}

export interface AlgoRecommended {
  algorithm: string
  path: string[]
  path_length: number
  nodes_explored: number
  runtime_ms: number
  safety_score: number
  used_air_edges: boolean
  why_selected: string
  composite_score?: number
}

export interface SafeZone {
  id: string
  name?: string
  capacity?: number
  occupancy?: number
  resources?: Record<string, number>
}

export interface SimSnapshot {
  tick: number
  sim_time_min: number
  running: boolean
  agent_positions: Record<string, string>
  missions: Array<{
    mission_id: string
    status: MissionStatus
    current_step: number
    team_id: string
    path: string[]
  }>
  node_people: Record<string, number>
}

export interface PathHighlight {
  path: string[]
  color: string
  width?: number
  label?: string
  showSteps?: boolean
}

export interface EdgeInfo {
  from: string
  to: string
  road_name: string
  km: number
  air_only: boolean
  blocked: boolean
}

export interface KnapsackResult {
  selected: Array<Record<string, unknown>>
  not_selected: Array<Record<string, unknown>>
  total_value: number
  dp_table: number[][]
  traceback: number[]
  capacity: number
}

export interface ResourceItem {
  resource_id: string
  name?: string
  category?: string
  total_stock?: number
  distributed?: number
  in_transit?: number
  unit?: string
}

export interface CityMeta {
  name: string
  slug: string
  node_count: number
  edge_count: number
  active_disasters: number
  description: string
}
