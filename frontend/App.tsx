import { useEffect } from 'react'
import { BrowserRouter, Routes, Route, NavLink, Navigate, useNavigate } from 'react-router-dom'
import { Toaster } from 'react-hot-toast'
import { useAuthStore } from './store/authStore'
import LoginPage from './pages/LoginPage'
import GoalsPage from './pages/GoalsPage'
import PortfolioPage from './pages/PortfolioPage'
import TransactionsPage from './pages/TransactionsPage'

function ProtectedLayout() {
  const { user, isAuthenticated, logout, fetchMe } = useAuthStore()
  const navigate = useNavigate()

  useEffect(() => {
    if (isAuthenticated) fetchMe()
    else navigate('/login')
  }, [])

  if (!isAuthenticated) return null

  const navItems = [
    { to: '/goals', label: 'Goals', icon: '🎯' },
    { to: '/portfolio', label: 'Portfolio', icon: '📊' },
    { to: '/transactions', label: 'Transactions', icon: '🔄' },
  ]

  return (
    <div style={{ minHeight: '100vh', background: '#060e1a', fontFamily: "'Sora', sans-serif" }}>
      {/* Header */}
      <header style={{ background: '#0a1628', borderBottom: '1px solid #1e293b', position: 'sticky', top: 0, zIndex: 40 }}>
        <div style={{ maxWidth: 1200, margin: '0 auto', padding: '0 1.5rem', height: 60, display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: 12 }}>
            <div style={{ width: 32, height: 32, background: '#f59e0b', borderRadius: 8, display: 'flex', alignItems: 'center', justifyContent: 'center', fontWeight: 800, color: 'black', fontSize: 15 }}>W</div>
            <div>
              <p style={{ color: 'white', fontWeight: 700, fontSize: 14, fontFamily: "'DM Serif Display', serif", margin: 0 }}>WealthTracker</p>
              <p style={{ color: '#475569', fontSize: 10, margin: 0 }}>Milestone 2</p>
            </div>
          </div>

          <nav style={{ display: 'flex', gap: 4 }}>
            {navItems.map(n => (
              <NavLink key={n.to} to={n.to} style={({ isActive }) => ({
                display: 'flex', alignItems: 'center', gap: 6, padding: '6px 14px', borderRadius: 10, fontSize: 13, fontWeight: 600,
                textDecoration: 'none', fontFamily: 'inherit',
                background: isActive ? '#f59e0b' : 'transparent',
                color: isActive ? 'black' : '#64748b',
              })}>
                <span>{n.icon}</span>{n.label}
              </NavLink>
            ))}
          </nav>

          <div style={{ display: 'flex', alignItems: 'center', gap: 12 }}>
            {user && <span style={{ color: '#64748b', fontSize: 12 }}>{user.name}</span>}
            <button onClick={() => { logout(); navigate('/login') }}
              style={{ background: '#1e293b', color: '#94a3b8', border: 'none', borderRadius: 8, padding: '6px 14px', fontSize: 12, fontWeight: 600, cursor: 'pointer', fontFamily: 'inherit' }}>
              Sign Out
            </button>
          </div>
        </div>
      </header>

      {/* Content */}
      <main style={{ maxWidth: 1200, margin: '0 auto', padding: '2rem 1.5rem' }}>
        <Routes>
          <Route path="/goals"        element={<GoalsPage />} />
          <Route path="/portfolio"    element={<PortfolioPage />} />
          <Route path="/transactions" element={<TransactionsPage />} />
          <Route path="*"             element={<Navigate to="/goals" replace />} />
        </Routes>
      </main>
    </div>
  )
}

export default function App() {
  return (
    <BrowserRouter>
      <style>{`@import url('https://fonts.googleapis.com/css2?family=DM+Serif+Display&family=Sora:wght@300;400;500;600;700&display=swap'); * { box-sizing: border-box; } body { margin: 0; background: #060e1a; }`}</style>
      <Toaster position="top-right" toastOptions={{ style: { background: '#1e293b', color: 'white', border: '1px solid #334155' } }} />
      <Routes>
        <Route path="/login" element={<LoginPage />} />
        <Route path="/*"     element={<ProtectedLayout />} />
      </Routes>
    </BrowserRouter>
  )
}