import { motion } from 'framer-motion'
import type { PathHighlight } from '../../types'

/** Path overlays are integrated in CityMap; this component is a framer-motion wrapper for standalone use. */
export function PathOverlay({ paths, visible }: { paths: PathHighlight[]; visible: boolean }) {
  if (!visible) return null
  return (
    <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} exit={{ opacity: 0 }} style={{ display: 'none' }}>
      {paths.length}
    </motion.div>
  )
}
