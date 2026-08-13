import { NavLink } from 'react-router-dom'

const links = [
  { to: '/', label: 'Dashboard' },
  { to: '/upload', label: 'Upload' },
  { to: '/simulate', label: 'Simulate' },
  { to: '/vendors', label: 'Vendors' },
  { to: '/cv-verify', label: 'CV Verify' },
]

export default function NavBar() {
  return (
    <nav style={{
      display: 'flex', gap: 4, padding: '14px 24px',
      borderBottom: '1px solid var(--line)', marginBottom: 8,
    }}>
      {links.map((link) => (
        <NavLink
          key={link.to}
          to={link.to}
          end={link.to === '/'}
          style={({ isActive }) => ({
            padding: '7px 14px', borderRadius: 7, fontSize: 13.5, fontWeight: 600,
            textDecoration: 'none',
            color: isActive ? '#1a0e08' : 'var(--muted)',
            background: isActive ? 'var(--critical)' : 'transparent',
          })}
        >
          {link.label}
        </NavLink>
      ))}
    </nav>
  )
}