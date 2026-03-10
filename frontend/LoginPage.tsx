import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import toast from 'react-hot-toast'
import { useAuthStore } from '../store/authStore'

export default function LoginPage() {
  const [mode, setMode] = useState<'login' | 'register'>('login')
  const [form, setForm] = useState({
    name: '',
    email: '',
    password: '',
    risk_profile: 'moderate',
  })
  const { login, register, isLoading } = useAuthStore()
  const navigate = useNavigate()

  const handle = async (e: React.FormEvent) => {
    e.preventDefault()
    try {
      if (mode === 'login') {
        await login(form.email, form.password)
        toast.success('Welcome back!')
      } else {
        await register(form.name, form.email, form.password)
        toast.success('Account created!')
      }
      navigate('/')
    } catch (err: any) {
      toast.error(err?.response?.data?.detail || 'Something went wrong')
    }
  }

  return (
    <div
      style={{
        minHeight: '100vh',
        background: '#060e1a',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        fontFamily: "'Sora', sans-serif",
      }}
    >
      <style>{`
        @import url('https://fonts.googleapis.com/css2?family=DM+Serif+Display&family=Sora:wght@300;400;500;600;700&display=swap');
        * { box-sizing: border-box; }
        input:focus, select:focus { border-color: #f59e0b !important; outline: none; }
      `}</style>

      <div style={{ width: '100%', maxWidth: 420, padding: '0 1rem' }}>

        {/* Logo */}
        <div style={{ textAlign: 'center', marginBottom: '2rem' }}>
          <div
            style={{
              width: 56,
              height: 56,
              background: '#f59e0b',
              borderRadius: 16,
              display: 'inline-flex',
              alignItems: 'center',
              justifyContent: 'center',
              marginBottom: 14,
              boxShadow: '0 0 32px #f59e0b55',
            }}
          >
            <span style={{ color: 'black', fontWeight: 800, fontSize: 24 }}>W</span>
          </div>
          <h1
            style={{
              color: 'white',
              fontFamily: "'DM Serif Display', serif",
              fontSize: 30,
              margin: 0,
            }}
          >
            WealthTracker
          </h1>
          <p style={{ color: '#475569', fontSize: 13, marginTop: 6 }}>
            Milestone 2 — Goals & Portfolio Core
          </p>
        </div>

        {/* Card */}
        <div
          style={{
            background: '#0f172a',
            border: '1px solid #1e293b',
            borderRadius: 20,
            padding: '2rem',
          }}
        >
          {/* Login / Register Tabs */}
          <div
            style={{
              display: 'flex',
              gap: 4,
              background: '#0b1120',
              borderRadius: 10,
              padding: 4,
              marginBottom: '1.5rem',
            }}
          >
            {(['login', 'register'] as const).map((m) => (
              <button
                key={m}
                onClick={() => setMode(m)}
                style={{
                  flex: 1,
                  padding: '8px 0',
                  borderRadius: 8,
                  border: 'none',
                  cursor: 'pointer',
                  fontWeight: 600,
                  fontSize: 13,
                  background: mode === m ? '#f59e0b' : 'transparent',
                  color: mode === m ? 'black' : '#64748b',
                  fontFamily: 'inherit',
                  transition: 'all 0.2s',
                }}
              >
                {m === 'login' ? 'Sign In' : 'Register'}
              </button>
            ))}
          </div>

          {/* Form */}
          <form
            onSubmit={handle}
            style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}
          >
            {/* Name - only on register */}
            {mode === 'register' && (
              <Field
                label="Full Name"
                type="text"
                value={form.name}
                onChange={(v) => setForm({ ...form, name: v })}
                placeholder="John Doe"
              />
            )}

            <Field
              label="Email"
              type="email"
              value={form.email}
              onChange={(v) => setForm({ ...form, email: v })}
              placeholder="you@example.com"
            />

            <Field
              label="Password"
              type="password"
              value={form.password}
              onChange={(v) => setForm({ ...form, password: v })}
              placeholder="••••••••"
            />

            {/* Risk Profile - only on register */}
            {mode === 'register' && (
              <div style={{ display: 'flex', flexDirection: 'column', gap: 6 }}>
                <label style={labelStyle}>Risk Profile</label>
                <select
                  value={form.risk_profile}
                  onChange={(e) => setForm({ ...form, risk_profile: e.target.value })}
                  style={inputStyle}
                >
                  <option value="conservative">🛡️ Conservative</option>
                  <option value="moderate">⚖️ Moderate</option>
                  <option value="aggressive">🚀 Aggressive</option>
                </select>
              </div>
            )}

            <button
              type="submit"
              disabled={isLoading}
              style={{
                background: isLoading ? '#92400e' : '#f59e0b',
                color: 'black',
                border: 'none',
                borderRadius: 12,
                padding: '12px',
                fontWeight: 700,
                fontSize: 14,
                cursor: isLoading ? 'not-allowed' : 'pointer',
                fontFamily: 'inherit',
                marginTop: 4,
                transition: 'background 0.2s',
              }}
            >
              {isLoading
                ? 'Please wait…'
                : mode === 'login'
                ? 'Sign In'
                : 'Create Account'}
            </button>
          </form>

          {/* Switch mode hint */}
          <p
            style={{
              color: '#475569',
              fontSize: 12,
              textAlign: 'center',
              marginTop: '1.25rem',
              marginBottom: 0,
            }}
          >
            {mode === 'login' ? (
              <>
                Don't have an account?{' '}
                <span
                  onClick={() => setMode('register')}
                  style={{ color: '#f59e0b', cursor: 'pointer', fontWeight: 600 }}
                >
                  Register
                </span>
              </>
            ) : (
              <>
                Already have an account?{' '}
                <span
                  onClick={() => setMode('login')}
                  style={{ color: '#f59e0b', cursor: 'pointer', fontWeight: 600 }}
                >
                  Sign In
                </span>
              </>
            )}
          </p>
        </div>

        {/* Demo hint */}
        <p style={{ color: '#334155', fontSize: 12, textAlign: 'center', marginTop: '1rem' }}>
          Demo:{' '}
          <code style={{ color: '#f59e0b' }}>demo@wealthtracker.dev</code> / any password
        </p>
      </div>
    </div>
  )
}

// ── Reusable Field ────────────────────────────────────────────
function Field({
  label,
  type = 'text',
  value,
  onChange,
  placeholder,
}: {
  label: string
  type?: string
  value: string
  onChange: (v: string) => void
  placeholder?: string
}) {
  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: 6 }}>
      <label style={labelStyle}>{label}</label>
      <input
        type={type}
        value={value}
        onChange={(e) => onChange(e.target.value)}
        placeholder={placeholder}
        required
        style={inputStyle}
      />
    </div>
  )
}

// ── Shared Styles ─────────────────────────────────────────────
const labelStyle: React.CSSProperties = {
  color: '#94a3b8',
  fontSize: 11,
  fontWeight: 600,
  textTransform: 'uppercase',
  letterSpacing: '0.05em',
}

const inputStyle: React.CSSProperties = {
  background: '#1e293b',
  border: '1px solid #334155',
  borderRadius: 10,
  color: 'white',
  padding: '10px 12px',
  fontSize: 13,
  fontFamily: 'inherit',
  width: '100%',
  outline: 'none',
}