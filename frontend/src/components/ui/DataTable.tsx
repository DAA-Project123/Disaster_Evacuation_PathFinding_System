import type { ReactNode } from 'react'
import { theme } from '../../styles/theme'

export function DataTable<T extends Record<string, unknown>>({
  columns,
  rows,
  getRowKey,
  onRowClick,
  rowClassName,
}: {
  columns: { key: keyof T | string; header: string; render?: (row: T) => ReactNode }[]
  rows: T[]
  getRowKey: (row: T, i: number) => string
  onRowClick?: (row: T) => void
  rowClassName?: (row: T) => string | undefined
}) {
  return (
    <div style={{ overflow: 'auto', borderRadius: 8, border: `1px solid ${theme.colors.border}` }}>
      <table style={{ width: '100%', borderCollapse: 'collapse', fontSize: 13 }}>
        <thead>
          <tr style={{ background: theme.colors.surfaceHigh }}>
            {columns.map((c) => (
              <th
                key={String(c.key)}
                style={{
                  textAlign: 'left',
                  padding: '10px 12px',
                  color: theme.colors.textSecondary,
                  fontWeight: 600,
                  borderBottom: `1px solid ${theme.colors.border}`,
                }}
              >
                {c.header}
              </th>
            ))}
          </tr>
        </thead>
        <tbody>
          {rows.map((row, i) => (
            <tr
              key={getRowKey(row, i)}
              onClick={() => onRowClick?.(row)}
              className={rowClassName?.(row) ?? undefined}
              style={{
                cursor: onRowClick ? 'pointer' : undefined,
                background: i % 2 ? theme.colors.surface : theme.colors.bg,
              }}
            >
              {columns.map((c) => (
                <td
                  key={String(c.key)}
                  style={{
                    padding: '10px 12px',
                    borderBottom: `1px solid ${theme.colors.border}`,
                    color: theme.colors.textPrimary,
                  }}
                >
                  {c.render ? c.render(row) : String(row[c.key as keyof T] ?? '')}
                </td>
              ))}
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  )
}
