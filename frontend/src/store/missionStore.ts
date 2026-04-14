import { create } from 'zustand'
import type { Mission } from '../types'

interface MissionStore {
  selectedTargetNode: string | null
  setSelectedTargetNode: (id: string | null) => void
  dispatchWizardStep: number
  setDispatchWizardStep: (n: number) => void
  highlightedMission: Mission | null
  setHighlightedMission: (m: Mission | null) => void
}

export const useMissionStore = create<MissionStore>((set) => ({
  selectedTargetNode: null,
  setSelectedTargetNode: (id) => set({ selectedTargetNode: id }),
  dispatchWizardStep: 1,
  setDispatchWizardStep: (n) => set({ dispatchWizardStep: n }),
  highlightedMission: null,
  setHighlightedMission: (m) => set({ highlightedMission: m }),
}))
