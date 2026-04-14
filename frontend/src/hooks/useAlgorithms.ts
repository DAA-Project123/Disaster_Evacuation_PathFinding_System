import { useMutation } from '@tanstack/react-query'
import { compareAlgorithms, runGreedy, runKnapsack } from '../api/client'

export function useCompareAlgorithms() {
  return useMutation({
    mutationFn: compareAlgorithms,
  })
}

export function useGreedy() {
  return useMutation({
    mutationFn: runGreedy,
  })
}

export function useKnapsack() {
  return useMutation({
    mutationFn: runKnapsack,
  })
}
