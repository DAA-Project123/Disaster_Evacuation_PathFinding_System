import { useState } from 'react'
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import { getResources, dispatchResource, confirmDelivery, restockResource } from '../api/client'
import { HubInventory } from '../components/resources/HubInventory'
import { DispatchForm } from '../components/resources/DispatchForm'
import { SafeZoneStatus } from '../components/resources/SafeZoneStatus'
import { MetricCard } from '../components/ui/MetricCard'
import { DataTable } from '../components/ui/DataTable'
import { useKnapsack } from '../hooks/useAlgorithms'
import { KnapsackTable } from '../components/algorithms/KnapsackTable'
import { useCityStore } from '../store/cityStore'

function RestockInline({
  inventory,
  onRestock,
}: {
  inventory: Array<Record<string, unknown>>
  onRestock: (p: { resource_id: string; quantity: number; reason: string }) => void
}) {
  const [rid, setRid] = useState(String(inventory[0]?.resource_id ?? ''))
  const [qty, setQty] = useState(10)
  const [reason, setReason] = useState('replenishment')
  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: 8 }}>
      <select value={rid} onChange={(e) => setRid(e.target.value)} style={{ padding: 8 }}>
        {inventory.map((i) => (
          <option key={String(i.resource_id)} value={String(i.resource_id)}>
            {String(i.name)}
          </option>
        ))}
      </select>
      <input type="number" value={qty} onChange={(e) => setQty(Number(e.target.value))} />
      <input value={reason} onChange={(e) => setReason(e.target.value)} />
      <button type="button" onClick={() => onRestock({ resource_id: rid, quantity: qty, reason })}>
        Restock
      </button>
    </div>
  )
}

export function ResourceHub() {
  const qc = useQueryClient()
  const city = useCityStore((s) => s.activeCity)
  const { data } = useQuery({ queryKey: ['resources'], queryFn: getResources })
  const knapsack = useKnapsack()

  const dispatchMut = useMutation({
    mutationFn: dispatchResource,
    onSuccess: () => void qc.invalidateQueries({ queryKey: ['resources'] }),
  })
  const deliverMut = useMutation({
    mutationFn: confirmDelivery,
    onSuccess: () => void qc.invalidateQueries({ queryKey: ['resources'] }),
  })
  const restockMut = useMutation({
    mutationFn: restockResource,
    onSuccess: () => void qc.invalidateQueries({ queryKey: ['resources'] }),
  })

  const inventory = (data?.inventory as Array<Record<string, unknown>>) ?? []
  const allocations = (data?.safe_zone_allocations as Array<Record<string, unknown>>) ?? []
  const log = (data?.distribution_log as Array<Record<string, unknown>>) ?? []

  const zones = [
    { id: 'SZ1', name: 'North shelter' },
    { id: 'SZ2', name: 'East hub' },
  ]

  const summary = data
    ? {
        total_available: inventory.reduce(
          (s, i) =>
            s +
            Math.max(
              0,
              Number(i.total_stock ?? 0) - Number(i.distributed ?? 0) - Number(i.in_transit ?? 0),
            ),
          0,
        ),
      }
    : { total_available: 0 }

  return (
    <div>
      <h2 style={{ marginBottom: 16 }}>Resource hub</h2>
      <div style={{ display: 'flex', gap: 12, marginBottom: 20, flexWrap: 'wrap' }}>
        <MetricCard label="SKU count" value={inventory.length} />
        <MetricCard label="Approx. available units" value={summary.total_available} />
        <MetricCard label="City" value={city} />
      </div>
      <HubInventory inventory={inventory} />
      <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 20, marginTop: 24 }}>
        <DispatchForm
          inventory={inventory}
          zones={zones}
          onDispatch={(resource_id, quantity, safe_zone_id, safe_zone_name) =>
            dispatchMut.mutate({ resource_id, quantity, safe_zone_id, safe_zone_name })
          }
        />
        <div>
          <h3>Restock</h3>
          <RestockInline onRestock={(a) => restockMut.mutate(a)} inventory={inventory} />
        </div>
      </div>
      <h3 style={{ marginTop: 24 }}>Active shipments</h3>
      <DataTable
        columns={[
          { key: 'allocation_id', header: 'ID' },
          { key: 'resource_name', header: 'Resource' },
          { key: 'quantity', header: 'Qty' },
          { key: 'safe_zone_name', header: 'Zone' },
          { key: 'status', header: 'Status' },
          {
            key: 'actions',
            header: 'Deliver',
            render: (row) => (
              <button
                type="button"
                onClick={() => deliverMut.mutate(String(row.allocation_id))}
                style={{ cursor: 'pointer' }}
              >
                Confirm delivery
              </button>
            ),
          },
        ]}
        rows={allocations as Record<string, unknown>[]}
        getRowKey={(r, i) => String(r.allocation_id ?? i)}
      />
      <h3 style={{ marginTop: 24 }}>Safe zones</h3>
      <SafeZoneStatus zones={zones.map((z) => ({ ...z, capacity: 500, occupancy: 120 }))} />
      <h3 style={{ marginTop: 24 }}>Distribution log</h3>
      <DataTable
        columns={[
          { key: 'time', header: 'Time' },
          { key: 'action', header: 'Action' },
          { key: 'resource_name', header: 'Resource' },
          { key: 'quantity', header: 'Qty' },
        ]}
        rows={log.slice(-30).reverse() as Record<string, unknown>[]}
        getRowKey={(r, i) => `${String(r.time)}-${i}`}
      />
      <h3 style={{ marginTop: 24 }}>Supply knapsack (demo)</h3>
      <button
        type="button"
        onClick={() => knapsack.mutate({ city })}
        style={{ marginBottom: 12, padding: '8px 12px', borderRadius: 8, cursor: 'pointer' }}
      >
        Run knapsack on supply proxies
      </button>
      {knapsack.data ? (
        <KnapsackTable
          dpTable={knapsack.data.dp_table}
          traceback={knapsack.data.traceback}
          victims={[]}
          selected={[]}
        />
      ) : null}
    </div>
  )
}
