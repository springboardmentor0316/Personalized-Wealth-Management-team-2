import { useState, useEffect, useCallback } from 'react'
import toast from 'react-hot-toast'
import { investmentsAPI, Investment, AssetType, PortfolioSummary } from '../api/services'
import { Modal, ModalField, Spinner, EmptyState, btnStyle, smallBtn, inputStyle, selectStyle } from './GoalsPage'

const ASSET_COLORS: Record<AssetType, string> = { stock: '#f59e0b', etf: '#3b82f6', mutual_fund: '#10b981', bond: '#8b5cf6', cash: '#6b7280' }
const ASSET_ICONS: Record<AssetType, string> = { stock: '📈', etf: '📊', mutual_fund: '🏦', bond: '📜', cash: '💵' }

const fmt = (n: number) => new Intl.NumberFormat('en-US', { style: 'currency', currency: 'USD', maximumFractionDigits: 0 }).format(n)
const fmtSmall = (n: number) => new Intl.NumberFormat('en-US', { style: 'currency', currency: 'USD', minimumFractionDigits: 2 }).format(n)

const EMPTY_FORM = { asset_type: 'stock' as AssetType, symbol: '', units: '', avg_buy_price: '' }

export default function PortfolioPage() {
  const [summary, setSummary] = useState<PortfolioSummary | null>(null)
  const [loading, setLoading] = useState(true)
  const [showModal, setShowModal] = useState(false)
  const [editInv, setEditInv] = useState<Investment | null>(null)
  const [form, setForm] = useState(EMPTY_FORM)
  const [saving, setSaving] = useState(false)

  const load = useCallback(async () => {
    try {
      const data = await investmentsAPI.summary()
      setSummary(data)
    } catch { toast.error('Failed to load portfolio') }
    finally { setLoading(false) }
  }, [])

  useEffect(() => { load() }, [load])

  const openAdd = () => { setEditInv(null); setForm(EMPTY_FORM); setShowModal(true) }
  const openEdit = (inv: Investment) => {
    setEditInv(inv)
    setForm({ asset_type: inv.asset_type, symbol: inv.symbol, units: String(inv.units), avg_buy_price: String(inv.avg_buy_price) })
    setShowModal(true)
  }

  const save = async () => {
    if (!form.symbol || !form.units || !form.avg_buy_price) return toast.error('Fill in all fields')
    setSaving(true)
    try {
      const payload = { asset_type: form.asset_type, symbol: form.symbol.toUpperCase(), units: +form.units, avg_buy_price: +form.avg_buy_price }
      if (editInv) {
        await investmentsAPI.update(editInv.id, payload)
        toast.success('Position updated')
      } else {
        await investmentsAPI.create(payload)
        toast.success('Position added!')
      }
      setShowModal(false)
      load()
    } catch (e: any) {
      toast.error(e?.response?.data?.detail || 'Error saving')
    } finally { setSaving(false) }
  }

  const deleteInv = async (id: number) => {
    if (!confirm('Remove this position?')) return
    try { await investmentsAPI.delete(id); toast.success('Position removed'); load() }
    catch { toast.error('Failed to delete') }
  }

  if (loading || !summary) return <Spinner />

  const positions = summary.positions
  const gainColor = summary.total_gain_loss >= 0 ? '#10b981' : '#ef4444'
  const totalVal = Number(summary.total_current_value)

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '1.5rem' }}>
      {/* Summary Cards */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(4, 1fr)', gap: '1rem' }}>
        {[
          { label: 'Portfolio Value', value: fmt(Number(summary.total_current_value)), color: 'white' },
          { label: 'Total Invested', value: fmt(Number(summary.total_cost_basis)), color: 'white' },
          { label: 'Gain / Loss', value: `${summary.total_gain_loss >= 0 ? '+' : ''}${fmt(Number(summary.total_gain_loss))}`, color: gainColor, sub: `${summary.total_gain_loss_pct}%` },
          { label: 'Positions', value: positions.length, color: 'white' },
        ].map((c, i) => (
          <div key={i} style={{ background: '#0f172a', border: '1px solid #1e293b', borderRadius: 16, padding: '1.25rem' }}>
            <p style={{ color: '#475569', fontSize: 11, textTransform: 'uppercase', letterSpacing: '0.07em', marginBottom: 4 }}>{c.label}</p>
            <p style={{ color: c.color, fontSize: 22, fontWeight: 700, margin: 0 }}>{c.value}</p>
            {c.sub && <p style={{ color: c.color, fontSize: 11, marginTop: 2 }}>{c.sub} return</p>}
          </div>
        ))}
      </div>

      {/* Allocation Bar */}
      {positions.length > 0 && (
        <div style={{ background: '#0f172a', border: '1px solid #1e293b', borderRadius: 16, padding: '1.25rem' }}>
          <p style={{ color: '#475569', fontSize: 11, textTransform: 'uppercase', letterSpacing: '0.07em', marginBottom: 12 }}>Asset Allocation</p>
          <div style={{ display: 'flex', height: 12, borderRadius: 6, overflow: 'hidden', gap: 2 }}>
            {Object.entries(summary.allocation_by_type).map(([type, pct]) => (
              <div key={type} style={{ height: '100%', background: ASSET_COLORS[type as AssetType] || '#6b7280', width: `${pct}%`, transition: 'width 0.5s ease' }} title={`${type}: ${pct}%`} />
            ))}
          </div>
          <div style={{ display: 'flex', flexWrap: 'wrap', gap: '1rem', marginTop: 10 }}>
            {Object.entries(summary.allocation_by_type).map(([type, pct]) => (
              <div key={type} style={{ display: 'flex', alignItems: 'center', gap: 6 }}>
                <div style={{ width: 10, height: 10, borderRadius: '50%', background: ASSET_COLORS[type as AssetType] || '#6b7280' }} />
                <span style={{ color: '#94a3b8', fontSize: 12, textTransform: 'capitalize' }}>{type.replace('_', ' ')}</span>
                <span style={{ color: '#475569', fontSize: 12 }}>{pct}%</span>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Holdings Table */}
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <h2 style={{ color: 'white', fontFamily: "'DM Serif Display', serif", fontSize: 22, margin: 0 }}>Holdings</h2>
        <button onClick={openAdd} style={btnStyle('#f59e0b', 'black')}>+ Add Position</button>
      </div>

      {positions.length === 0 ? (
        <EmptyState icon="📊" text="No positions yet. Add your first investment!" action={<button onClick={openAdd} style={btnStyle('#f59e0b', 'black')}>+ Add Position</button>} />
      ) : (
        <div style={{ borderRadius: 16, overflow: 'hidden', border: '1px solid #1e293b' }}>
          <table style={{ width: '100%', borderCollapse: 'collapse', fontSize: 13 }}>
            <thead>
              <tr style={{ background: '#0b1120', borderBottom: '1px solid #1e293b' }}>
                {['Asset', 'Symbol', 'Units', 'Avg Price', 'Cost Basis', 'Current Value', 'Gain/Loss', ''].map(h => (
                  <th key={h} style={{ textAlign: 'left', padding: '12px 16px', color: '#475569', fontSize: 11, textTransform: 'uppercase', letterSpacing: '0.05em', fontWeight: 600 }}>{h}</th>
                ))}
              </tr>
            </thead>
            <tbody>
              {positions.map((inv, idx) => {
                const gain = Number(inv.current_value) - Number(inv.cost_basis)
                const gainPct = Number(inv.cost_basis) > 0 ? ((gain / Number(inv.cost_basis)) * 100).toFixed(2) : '0'
                const gc = gain >= 0 ? '#10b981' : '#ef4444'
                return (
                  <tr key={inv.id} style={{ background: idx % 2 === 0 ? '#0f172a' : '#0b1120', borderBottom: '1px solid #1e293b' }}>
                    <td style={{ padding: '12px 16px' }}>
                      <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
                        <span>{ASSET_ICONS[inv.asset_type]}</span>
                        <span style={{ fontSize: 11, fontWeight: 600, padding: '2px 8px', borderRadius: 100, background: (ASSET_COLORS[inv.asset_type] || '#6b7280') + '22', color: ASSET_COLORS[inv.asset_type] || '#6b7280', textTransform: 'capitalize' }}>{inv.asset_type.replace('_', ' ')}</span>
                      </div>
                    </td>
                    <td style={{ padding: '12px 16px', color: 'white', fontWeight: 700 }}>{inv.symbol}</td>
                    <td style={{ padding: '12px 16px', color: '#94a3b8' }}>{inv.units}</td>
                    <td style={{ padding: '12px 16px', color: '#94a3b8' }}>{fmtSmall(Number(inv.avg_buy_price))}</td>
                    <td style={{ padding: '12px 16px', color: '#94a3b8' }}>{fmtSmall(Number(inv.cost_basis))}</td>
                    <td style={{ padding: '12px 16px', color: 'white', fontWeight: 600 }}>{fmtSmall(Number(inv.current_value))}</td>
                    <td style={{ padding: '12px 16px' }}>
                      <span style={{ color: gc, fontWeight: 600 }}>{gain >= 0 ? '+' : ''}{fmtSmall(gain)} ({gainPct}%)</span>
                    </td>
                    <td style={{ padding: '12px 16px' }}>
                      <div style={{ display: 'flex', gap: 6 }}>
                        <button onClick={() => openEdit(inv)} style={smallBtn('#94a3b8')}>Edit</button>
                        <button onClick={() => deleteInv(inv.id)} style={smallBtn('#ef4444')}>Del</button>
                      </div>
                    </td>
                  </tr>
                )
              })}
            </tbody>
          </table>
        </div>
      )}

      {/* Modal */}
      {showModal && (
        <Modal title={editInv ? 'Edit Position' : 'Add Position'} onClose={() => setShowModal(false)}>
          <ModalField label="Asset Type">
            <select value={form.asset_type} onChange={e => setForm({ ...form, asset_type: e.target.value as AssetType })} style={selectStyle}>
              {(['stock', 'etf', 'mutual_fund', 'bond', 'cash'] as AssetType[]).map(v => (
                <option key={v} value={v}>{ASSET_ICONS[v]} {v.replace('_', ' ').toUpperCase()}</option>
              ))}
            </select>
          </ModalField>
          <ModalField label="Symbol / Ticker">
            <input value={form.symbol} onChange={e => setForm({ ...form, symbol: e.target.value.toUpperCase() })} placeholder="AAPL" style={inputStyle} />
          </ModalField>
          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 12 }}>
            <ModalField label="Units / Shares">
              <input type="number" value={form.units} onChange={e => setForm({ ...form, units: e.target.value })} placeholder="10" style={inputStyle} />
            </ModalField>
            <ModalField label="Avg Buy Price ($)">
              <input type="number" value={form.avg_buy_price} onChange={e => setForm({ ...form, avg_buy_price: e.target.value })} placeholder="150.00" style={inputStyle} />
            </ModalField>
          </div>
          {form.units && form.avg_buy_price && (
            <div style={{ background: '#1e293b', borderRadius: 10, padding: '8px 12px', fontSize: 13 }}>
              <span style={{ color: '#64748b' }}>Cost Basis: </span>
              <span style={{ color: 'white', fontWeight: 600 }}>${(+form.units * +form.avg_buy_price).toFixed(2)}</span>
            </div>
          )}
          <div style={{ display: 'flex', gap: 10 }}>
            <button onClick={save} disabled={saving} style={{ ...btnStyle('#f59e0b', 'black'), flex: 1, padding: '10px' }}>
              {saving ? 'Saving…' : editInv ? 'Save Changes' : 'Add Position'}
            </button>
            <button onClick={() => setShowModal(false)} style={btnStyle('#1e293b', '#94a3b8')}>Cancel</button>
          </div>
        </Modal>
      )}
    </div>
  )
}