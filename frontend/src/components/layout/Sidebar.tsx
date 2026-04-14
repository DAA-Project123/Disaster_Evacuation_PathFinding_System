import { NavLink } from 'react-router-dom'
import { theme } from '../../styles/theme'
import { useCityStore } from '../../store/cityStore'

const links = [
  { to: '/', label: 'Dashboard' },
  { to: '/disaster', label: 'Disaster Control' },
  { to: '/rescue', label: 'Rescue Operations' },
  { to: '/resources', label: 'Resource Hub' },
]

export function Sidebar() {
  const city = useCityStore((s) => s.activeCity)
  return (
    <aside
      style={{
        background: theme.colors.surface,
        borderRight: `1px solid ${theme.colors.border}`,
        display: 'flex',
        flexDirection: 'column',
        padding: '20px 0',
        minHeight: '100vh',
      }}
    >
      <div style={{ padding: '0 20px 20px', fontFamily: theme.fonts.mono, color: theme.colors.accent, fontWeight: 700 }}>
        DAA Rescue System
      </div>
      <div style={{ padding: '0 20px 16px' }}>
        <span
          style={{
            fontSize: 11,
            padding: '4px 10px',
            borderRadius: 999,
            background: theme.colors.surfaceHigh,
            color: theme.colors.textSecondary,
          }}
        >
          {city}
        </span>
      </div>
      <nav style={{ display: 'flex', flexDirection: 'column', gap: 4 }}>
        {links.map((l) => (
          <NavLink
            key={l.to}
            to={l.to}
            end={l.to === '/'}
            style={({ isActive }) => ({
              padding: '10px 20px',
              color: isActive ? theme.colors.accent : theme.colors.textSecondary,
              background: isActive ? 'rgba(59,130,246,0.12)' : 'transparent',
              borderLeft: isActive ? `3px solid ${theme.colors.accent}` : '3px solid transparent',
              fontSize: 14,
 })}
          >
            {l.label}
          </NavLink>
        ))}
      </nav>
      <div style={{ marginTop: 'auto', padding: 20, fontSize: 11, color: theme.colors.textMuted }}>
        DAA / core + FastAPI
      </div>
    </aside>
  )
}
