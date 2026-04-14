import { Canvas } from '@react-three/fiber'
import { OrbitControls } from '@react-three/drei'
import { theme } from '../../styles/theme'
import type { CityGraph } from '../../types'

function Scene({ graph }: { graph: CityGraph }) {
  const nodes = graph.nodes
  const xs = nodes.map((n) => n.x ?? 0)
  const ys = nodes.map((n) => n.y ?? 0)
  const minX = Math.min(...xs)
  const maxX = Math.max(...xs)
  const minY = Math.min(...ys)
  const maxY = Math.max(...ys)
  const scale = 0.02
  const cx = ((minX + maxX) / 2) * scale
  const cz = ((minY + maxY) / 2) * scale

  return (
    <>
      <ambientLight intensity={0.4} color="#333" />
      <directionalLight position={[10, 20, 10]} intensity={0.8} />
      <group position={[-cx, 0, -cz]}>
        {nodes.map((n) => {
          const h = 0.2 + ((n.people_stranded ?? 0) / 100) * 0.8
          const x = (n.x ?? 0) * scale
          const z = (n.y ?? 0) * scale
          return (
            <mesh key={n.id} position={[x, h / 2, z]}>
              <cylinderGeometry args={[0.35, 0.35, h, 16]} />
              <meshStandardMaterial color={theme.colors.accent} />
            </mesh>
          )
        })}
      </group>
      <OrbitControls />
    </>
  )
}

export function ThreeMap({ graph, height = 400 }: { graph: CityGraph; height?: number }) {
  return (
    <div style={{ height, background: theme.colors.bg, borderRadius: 12 }}>
      <Canvas camera={{ position: [8, 12, 8], fov: 45 }}>
        <Scene graph={graph} />
      </Canvas>
    </div>
  )
}
