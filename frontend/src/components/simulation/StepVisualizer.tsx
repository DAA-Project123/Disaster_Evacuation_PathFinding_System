import { StepChain } from '../ui/StepChain'
import type { EdgeInfo, MissionStatus } from '../../types'

export function StepVisualizer(props: {
  path: string[]
  pathNames: string[]
  currentStep: number
  edges: EdgeInfo[]
  status: MissionStatus
}) {
  return <StepChain {...props} />
}
