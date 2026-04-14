import { create } from 'zustand'

interface DisasterStore {
  previewEnabled: boolean
  setPreviewEnabled: (v: boolean) => void
}

export const useDisasterStore = create<DisasterStore>((set) => ({
  previewEnabled: false,
  setPreviewEnabled: (v) => set({ previewEnabled: v }),
}))
