import { create } from 'zustand'
import type { Mission, SimSnapshot } from '../types'

interface SimulationStore {
  snapshot: SimSnapshot | null
  setSnapshot: (s: SimSnapshot | null) => void
  activeMissionsDetail: Mission[]
  setActiveMissionsDetail: (m: Mission[]) => void
}

export const useSimulationStore = create<SimulationStore>((set) => ({
  snapshot: null,
  setSnapshot: (s) => set({ snapshot: s }),
  activeMissionsDetail: [],
  setActiveMissionsDetail: (m) => set({ activeMissionsDetail: m }),
}))
