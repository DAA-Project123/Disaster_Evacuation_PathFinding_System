import { create } from 'zustand'
import type { CityGraph } from '../types'

interface CityStore {
  activeCity: string
  cityGraph: CityGraph | null
  setActiveCity: (c: string) => void
  setCityGraph: (g: CityGraph | null) => void
}

export const useCityStore = create<CityStore>((set) => ({
  activeCity: 'Veridian City',
  cityGraph: null,
  setActiveCity: (c) => set({ activeCity: c }),
  setCityGraph: (g) => set({ cityGraph: g }),
}))
