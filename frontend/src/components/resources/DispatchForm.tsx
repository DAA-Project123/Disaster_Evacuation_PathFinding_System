import type { CSSProperties } from 'react'
import { useState } from 'react'
import { theme } from '../../styles/theme'

export function DispatchForm({
  inventory,
  zones,
  onDispatch,
}: {
  inventory: Array<Record<string, unknown>>
  zones: Array<{ id: string; name?: string }>
  onDispatch: (resource_id: string, quantity: number, safe_zone_id: string, safe_zone_name: string) => void
}) {
  const [rid, setRid] = useState(String(inventory[0]?.resource_id ?? ''))
  const [zid, setZid] = useState(zones[0]?.id ?? '')
  const [qty, setQty] = useState(1)

  return (
    <div style={{ background: theme.colors.surface, borderRadius: 12, padding: 16, border: `1px solid ${theme.colors.border}` }}>
      <strong>Dispatch to safe zone</strong>
      <select
        value={rid}
        onChange={(e) => setRid(e.target.value)}
        style={sel}
      >
        {inventory.map((i) => (
          <option key={String(i.resource_id)} value={String(i.resource_id)}>
            {String(i.name)} ({String(i.resource_id)})
          </option>
        ))}
      </select>
      <select value={zid} onChange={(e) => setZid(e.target.value)} style={sel}>
        {zones.map((z) => (
          <option key={z.id} value={z.id}>
            {z.name ?? z.id}
          </option>
        ))}
      </select>
      <input
        type="number"
        min={1}
        value={qty}
        onChange={(e) => setQty(Number(e.target.value))}
        style={sel}
      />
      <button
        type="button"
        onClick={() => {
          const z = zones.find((x) => x.id === zid)
          onDispatch(rid, qty, zid, z?.name ?? zid)
        }}
        style={{
          marginTop: 12,
          width: '100%',
          padding: 12,
          borderRadius: 8,
          border: 'none',
          background: theme.colors.accent,
          color: '#fff',
          fontWeight: 600,
          cursor: 'pointer',
        }}
      >
        Dispatch
      </button>
    </div>
  )
}

const sel: CSSProperties = {
  width: '100%',
  marginTop: 10,
  padding: 10,
  borderRadius: 8,
  background: theme.colors.surfaceHigh,
  color: theme.colors.textPrimary,
  border: `1px solid ${theme.colors.border}`,
}
