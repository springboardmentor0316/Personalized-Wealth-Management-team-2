import { useState, useEffect, useCallback } from 'react'
import toast from 'react-hot-toast'
import { goalsAPI, Goal, GoalType, GoalStatus } from '../api/services'

const GOAL_COLORS: Record<GoalType, string> = { retirement: '#f59e0b', home: '#3b82f6', education: '#10b981', custom: '#8b5cf6' }
const GOAL_ICONS: Record<GoalType, string> = { retirement: '🏖️', home: '🏠', education: '🎓', custom: '⭐' }

const fmt = (n: number) => new Intl.NumberFormat('en-US', { style: 'currency', currency: 'USD', maximumFractionDigits: 0 }).format(n)
const fmtSmall = (n: number) => new Intl.NumberFormat('en-US', { style: 'currency', currency: 'USD', minimumFractionDigits: 2 }).format(n)

function ProgressRing({ value, max, color, size = 88 }: any) {
  const p = Math.min(100, (value / max) * 100)
  const r = (size - 12) / 2
  const circ = 2 * Math.PI * r
  const dash = (p / 100) * circ
  return (
    <svg width={size} height={size} viewBox={`0 0 ${size} ${size}`} style={{ transform: 'rotate(-90deg)' }}>
      <circle cx={size / 2} cy={size / 2} r={r} fill="none" stroke="#1e293b" strokeWidth={6} />
      <circle cx={size / 2} cy={size / 2} r={r} fill="none" stroke={color} strokeWidth={6}
        strokeDasharray={`${dash} ${circ - dash}`} strokeLinecap="round" style={{ transition: 'stroke-dasharray 0.8s ease' }} />
    </svg>
  )
}

const EMPTY_FORM = { goal_type: 'retirement' as GoalType, target_amount: '', target_date: '', monthly_contribution: '', status: 'active' as GoalStatus }

export default function GoalsPage() {
  const [goals, setGoals] = useState<Goal[]>([])
  const [loading, setLoading] = useState(true)
  const [showModal, setShowModal] = useState(false)
  const [editGoal, setEditGoal] = useState<Goal | null>(null)
  const [form, setForm] = useState(EMPTY_FORM)
  const [saving, setSaving] = useState(false)

  const load = useCallback(async () => {
    try {
      const data = await goalsAPI.list()
      setGoals(data)
    } catch { toast.error('Failed to load goals') }
    finally { setLoading(false) }
  }, [])

  useEffect(() => { load() }, [load])

  const openAdd = () => { setEditGoal(null); setForm(EMPTY_FORM); setShowModal(true) }
  const openEdit = (g: Goal) => {
    setEditGoal(g)
    setForm({ goal_type: g.goal_type, target_amount: String(g.target_amount), target_date: g.target_date, monthly_contribution: String(g.monthly_contribution), status: g.status })
    setShowModal(true)
  }

  const save = async () => {
    if (!form.target_amount || !form.target_date || !form.monthly_contribution) return toast.error('Fill in all fields')
    setSaving(true)
    try {
      const payload = { ...form, target_amount: +form.target_amount, monthly_contribution: +form.monthly_contribution }
      if (editGoal) {
        await goalsAPI.update(editGoal.id, payload)
        toast.success('Goal updated')
      } else {
        await goalsAPI.create(payload as any)
        toast.success('Goal created!')
      }
      setShowModal(false)
      load()
    } catch (e: any) {
      toast.error(e?.response?.data?.detail || 'Error saving goal')
    } finally { setSaving(false) }
  }

  const deleteGoal = async (id: number) => {
    if (!confirm('Delete this goal?')) return
    try { await goalsAPI.delete(id); toast.success('Goal deleted'); load() }
    catch { toast.error('Failed to delete') }
  }

  const toggleStatus = async (id: number) => {
    try { await goalsAPI.toggleStatus(id); load() }
    catch { toast.error('Failed to update status') }
  }

  const totalTarget = goals.reduce((a, g) => a + Number(g.target_amount), 0)
  const totalSaved  = goals.reduce((a, g) => a + Number(g.saved || 0), 0)

  if (loading) return <Spinner />

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '1.5rem' }}>
      {/* Summary */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)', gap: '1rem' }}>
        {[
          { label: 'Total Goal Value', value: fmt(totalTarget), sub: 'across all goals' },
          { label: 'Total Saved', value: fmt(totalSaved), sub: `${totalTarget > 0 ? ((totalSaved / totalTarget) * 100).toFixed(1) : 0}% funded` },
          { label: 'Active Goals', value: goals.filter(g => g.status === 'active').length, sub: `${goals.length} total goals` },
        ].map((c, i) => (
          <div key={i} style={{ background: '#0f172a', border: '1px solid #1e293b', borderRadius: 16, padding: '1.25rem' }}>
            <p style={{ color: '#475569', fontSize: 11, textTransform: 'uppercase', letterSpacing: '0.07em', marginBottom: 4 }}>{c.label}</p>
            <p style={{ color: 'white', fontSize: 24, fontWeight: 700, margin: 0 }}>{c.value}</p>
            <p style={{ color: '#475569', fontSize: 11, marginTop: 4 }}>{c.sub}</p>
          </div>
        ))}
      </div>

      {/* Header */}
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <h2 style={{ color: 'white', fontFamily: "'DM Serif Display', serif", fontSize: 22, margin: 0 }}>Your Goals</h2>
        <button onClick={openAdd} style={btnStyle('#f59e0b', 'black')}>+ Add Goal</button>
      </div>

      {goals.length === 0 && (
        <EmptyState icon="🎯" text="No goals yet. Create your first financial goal!" action={<button onClick={openAdd} style={btnStyle('#f59e0b', 'black')}>+ Add Goal</button>} />
      )}

      {/* Goal Cards */}
      {goals.map(g => {
        const progress = Number(g.progress_pct || 0)
        const months = Number(g.months_remaining || 0)
        const color = GOAL_COLORS[g.goal_type]
        const saved = Number(g.saved || 0)
        return (
          <div key={g.id} style={{ background: '#0f172a', border: '1px solid #1e293b', borderRadius: 16, padding: '1.25rem' }}>
            <div style={{ display: 'flex', gap: '1.25rem', alignItems: 'flex-start' }}>
              {/* Ring */}
              <div style={{ position: 'relative', flexShrink: 0 }}>
                <ProgressRing value={saved} max={Number(g.target_amount)} color={color} />
                <div style={{ position: 'absolute', inset: 0, display: 'flex', alignItems: 'center', justifyContent: 'center', fontSize: 22 }}>{GOAL_ICONS[g.goal_type]}</div>
              </div>
              {/* Info */}
              <div style={{ flex: 1 }}>
                <div style={{ display: 'flex', alignItems: 'center', gap: 8, marginBottom: 6 }}>
                  <span style={{ color: 'white', fontWeight: 700, textTransform: 'capitalize', fontSize: 15 }}>{g.goal_type}</span>
                  <StatusBadge status={g.status} />
                  {g.on_track ? <span style={{ color: '#10b981', fontSize: 11, fontWeight: 600 }}>✓ On Track</span>
                    : <span style={{ color: '#ef4444', fontSize: 11, fontWeight: 600 }}>⚠ Behind</span>}
                </div>
                <p style={{ color: '#94a3b8', fontSize: 13, margin: '2px 0' }}>Target: <b style={{ color: 'white' }}>{fmt(Number(g.target_amount))}</b></p>
                <p style={{ color: '#94a3b8', fontSize: 13, margin: '2px 0' }}>Saved: <b style={{ color }}>{fmt(saved)}</b> <span style={{ color: '#475569' }}>({progress}%)</span></p>
                <p style={{ color: '#94a3b8', fontSize: 13, margin: '2px 0' }}>Monthly: <b style={{ color: 'white' }}>{fmt(Number(g.monthly_contribution))}</b> · {months} months left</p>
                <p style={{ color: '#475569', fontSize: 11, marginTop: 4 }}>Target: {g.target_date}</p>

                {/* Progress bar */}
                <div style={{ marginTop: 10, height: 6, background: '#1e293b', borderRadius: 3, overflow: 'hidden' }}>
                  <div style={{ height: '100%', background: color, width: `${progress}%`, borderRadius: 3, transition: 'width 0.7s ease' }} />
                </div>
              </div>
              {/* Actions */}
              <div style={{ display: 'flex', flexDirection: 'column', gap: 6, alignItems: 'flex-end' }}>
                <button onClick={() => toggleStatus(g.id)} style={smallBtn(g.status === 'active' ? '#f59e0b' : '#10b981')}>
                  {g.status === 'active' ? 'Pause' : 'Resume'}
                </button>
                <button onClick={() => openEdit(g)} style={smallBtn('#94a3b8')}>Edit</button>
                <button onClick={() => deleteGoal(g.id)} style={smallBtn('#ef4444')}>Delete</button>
              </div>
            </div>
          </div>
        )
      })}

      {/* Modal */}
      {showModal && (
        <Modal title={editGoal ? 'Edit Goal' : 'New Goal'} onClose={() => setShowModal(false)}>
          <ModalField label="Goal Type">
            <select value={form.goal_type} onChange={e => setForm({ ...form, goal_type: e.target.value as GoalType })} style={selectStyle}>
              <option value="retirement">🏖️ Retirement</option>
              <option value="home">🏠 Home Purchase</option>
              <option value="education">🎓 Education</option>
              <option value="custom">⭐ Custom</option>
            </select>
          </ModalField>
          <ModalField label="Target Amount ($)">
            <input type="number" value={form.target_amount} onChange={e => setForm({ ...form, target_amount: e.target.value })} placeholder="500000" style={inputStyle} />
          </ModalField>
          <ModalField label="Target Date">
            <input type="date" value={form.target_date} onChange={e => setForm({ ...form, target_date: e.target.value })} style={inputStyle} />
          </ModalField>
          <ModalField label="Monthly Contribution ($)">
            <input type="number" value={form.monthly_contribution} onChange={e => setForm({ ...form, monthly_contribution: e.target.value })} placeholder="1000" style={inputStyle} />
          </ModalField>
          <ModalField label="Status">
            <select value={form.status} onChange={e => setForm({ ...form, status: e.target.value as GoalStatus })} style={selectStyle}>
              <option value="active">Active</option><option value="paused">Paused</option><option value="completed">Completed</option>
            </select>
          </ModalField>
          <div style={{ display: 'flex', gap: 10, marginTop: 8 }}>
            <button onClick={save} disabled={saving} style={{ ...btnStyle('#f59e0b', 'black'), flex: 1, padding: '10px' }}>
              {saving ? 'Saving…' : editGoal ? 'Save Changes' : 'Create Goal'}
            </button>
            <button onClick={() => setShowModal(false)} style={btnStyle('#1e293b', '#94a3b8')}>Cancel</button>
          </div>
        </Modal>
      )}
    </div>
  )
}

// ── Shared UI helpers ─────────────────────────────────────────
export function Modal({ title, onClose, children }: { title: string; onClose: () => void; children: React.ReactNode }) {
  return (
    <div style={{ position: 'fixed', inset: 0, zIndex: 50, display: 'flex', alignItems: 'center', justifyContent: 'center', background: 'rgba(0,0,0,0.75)', backdropFilter: 'blur(4px)' }}>
      <div style={{ background: '#0f172a', border: '1px solid #1e293b', borderRadius: 20, padding: '1.5rem', width: '100%', maxWidth: 480 }}>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1.25rem' }}>
          <h3 style={{ color: 'white', fontFamily: "'DM Serif Display', serif", fontSize: 18, margin: 0 }}>{title}</h3>
          <button onClick={onClose} style={{ color: '#64748b', background: 'none', border: 'none', fontSize: 18, cursor: 'pointer' }}>✕</button>
        </div>
        <div style={{ display: 'flex', flexDirection: 'column', gap: '0.875rem' }}>{children}</div>
      </div>
    </div>
  )
}
export function ModalField({ label, children }: { label: string; children: React.ReactNode }) {
  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: 5 }}>
      <label style={{ color: '#94a3b8', fontSize: 11, fontWeight: 600, textTransform: 'uppercase', letterSpacing: '0.05em' }}>{label}</label>
      {children}
    </div>
  )
}
export function StatusBadge({ status }: { status: string }) {
  const colors: Record<string, any> = {
    active: { bg: '#052e16', color: '#4ade80', border: '#166534' },
    paused: { bg: '#451a03', color: '#fbbf24', border: '#78350f' },
    completed: { bg: '#1e3a5f', color: '#60a5fa', border: '#1d4ed8' },
    buy: { bg: '#052e16', color: '#4ade80', border: '#166534' },
    sell: { bg: '#450a0a', color: '#f87171', border: '#7f1d1d' },
    dividend: { bg: '#2e1065', color: '#c084fc', border: '#6b21a8' },
    contribution: { bg: '#1e3a5f', color: '#60a5fa', border: '#1d4ed8' },
    withdrawal: { bg: '#431407', color: '#fb923c', border: '#9a3412' },
  }
  const c = colors[status] || { bg: '#1e293b', color: '#94a3b8', border: '#334155' }
  return <span style={{ fontSize: 11, fontWeight: 600, padding: '2px 8px', borderRadius: 100, background: c.bg, color: c.color, border: `1px solid ${c.border}` }}>{status}</span>
}
export function Spinner() {
  return <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', padding: '4rem', color: '#475569' }}>Loading…</div>
}
export function EmptyState({ icon, text, action }: { icon: string; text: string; action?: React.ReactNode }) {
  return (
    <div style={{ textAlign: 'center', padding: '3rem', color: '#475569' }}>
      <div style={{ fontSize: 40, marginBottom: 12 }}>{icon}</div>
      <p style={{ marginBottom: 16 }}>{text}</p>
      {action}
    </div>
  )
}
export const btnStyle = (bg: string, color: string) => ({ background: bg, color, border: 'none', borderRadius: 10, padding: '8px 16px', fontSize: 13, fontWeight: 600, cursor: 'pointer', fontFamily: 'inherit' } as React.CSSProperties)
export const smallBtn = (color: string) => ({ background: '#1e293b', color, border: 'none', borderRadius: 8, padding: '4px 10px', fontSize: 11, fontWeight: 600, cursor: 'pointer', fontFamily: 'inherit' } as React.CSSProperties)
export const inputStyle = { background: '#1e293b', border: '1px solid #334155', borderRadius: 10, color: 'white', padding: '9px 12px', fontSize: 13, fontFamily: 'inherit', width: '100%', outline: 'none', boxSizing: 'border-box' } as React.CSSProperties
export const selectStyle = { background: '#1e293b', border: '1px solid #334155', borderRadius: 10, color: 'white', padding: '9px 12px', fontSize: 13, fontFamily: 'inherit', width: '100%', outline: 'none' } as React.CSSProperties