import { useState, useEffect, useCallback } from 'react'
import toast from 'react-hot-toast'
import { transactionsAPI, Transaction, TxnType } from '../api/services'
import { Modal, ModalField, StatusBadge, Spinner, EmptyState, btnStyle, smallBtn, inputStyle, selectStyle } from './GoalsPage'

const fmt = (n: number) => new Intl.NumberFormat('en-US', { style: 'currency', currency: 'USD', maximumFractionDigits: 0 }).format(n)
const fmtSmall = (n: number) => new Intl.NumberFormat('en-US', { style: 'currency', currency: 'USD', minimumFractionDigits: 2 }).format(n)
const TYPES: TxnType[] = ['buy', 'sell', 'dividend', 'contribution', 'withdrawal']
const EMPTY_FORM = { symbol: '', type: 'buy' as TxnType, quantity: '', price: '', fees: '' }

export default function TransactionsPage() {
  const [txns, setTxns] = useState<Transaction[]>([])
  const [loading, setLoading] = useState(true)
  const [filter, setFilter] = useState<TxnType | 'all'>('all')
  const [showModal, setShowModal] = useState(false)
  const [form, setForm] = useState(EMPTY_FORM)
  const [saving, setSaving] = useState(false)

  const load = useCallback(async () => {
    try {
      const data = await transactionsAPI.list(filter !== 'all' ? { type: filter } : {})
      setTxns(data)
    } catch { toast.error('Failed to load transactions') }
    finally { setLoading(false) }
  }, [filter])

  useEffect(() => { load() }, [load])

  const save = async () => {
    if (!form.symbol || !form.quantity || !form.price) return toast.error('Fill in all fields')
    setSaving(true)
    try {
      await transactionsAPI.create({
        symbol: form.symbol.toUpperCase(),
        type: form.type,
        quantity: +form.quantity,
        price: +form.price,
        fees: +form.fees || 0,
        executed_at: new Date().toISOString(),
      } as any)
      toast.success('Transaction logged!')
      setShowModal(false)
      setForm(EMPTY_FORM)
      load()
    } catch (e: any) {
      toast.error(e?.response?.data?.detail || 'Error saving')
    } finally { setSaving(false) }
  }

  const deleteTxn = async (id: number) => {
    if (!confirm('Delete this transaction?')) return
    try { await transactionsAPI.delete(id); toast.success('Deleted'); load() }
    catch { toast.error('Failed to delete') }
  }

  const totalBought = txns.filter(t => t.type === 'buy').reduce((a, t) => a + t.quantity * t.price + t.fees, 0)
  const totalFees   = txns.reduce((a, t) => a + t.fees, 0)

  if (loading) return <Spinner />

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '1.5rem' }}>
      {/* Summary */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)', gap: '1rem' }}>
        {[
          { label: 'Total Transactions', value: txns.length },
          { label: 'Total Invested (Buys)', value: fmt(totalBought) },
          { label: 'Fees Paid', value: fmtSmall(totalFees) },
        ].map((c, i) => (
          <div key={i} style={{ background: '#0f172a', border: '1px solid #1e293b', borderRadius: 16, padding: '1.25rem' }}>
            <p style={{ color: '#475569', fontSize: 11, textTransform: 'uppercase', letterSpacing: '0.07em', marginBottom: 4 }}>{c.label}</p>
            <p style={{ color: 'white', fontSize: 24, fontWeight: 700, margin: 0 }}>{c.value}</p>
          </div>
        ))}
      </div>

      {/* Filter + Add */}
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', flexWrap: 'wrap', gap: 10 }}>
        <div style={{ display: 'flex', gap: 4, flexWrap: 'wrap' }}>
          {(['all', ...TYPES] as const).map(f => (
            <button key={f} onClick={() => setFilter(f)} style={{
              ...btnStyle(filter === f ? '#f59e0b' : '#1e293b', filter === f ? 'black' : '#64748b'),
              padding: '6px 14px', fontSize: 12, textTransform: 'capitalize'
            }}>{f}</button>
          ))}
        </div>
        <button onClick={() => setShowModal(true)} style={btnStyle('#f59e0b', 'black')}>+ Add Transaction</button>
      </div>

      {txns.length === 0 ? (
        <EmptyState icon="🔄" text="No transactions yet." action={<button onClick={() => setShowModal(true)} style={btnStyle('#f59e0b', 'black')}>+ Add Transaction</button>} />
      ) : (
        <div style={{ borderRadius: 16, overflow: 'hidden', border: '1px solid #1e293b' }}>
          <table style={{ width: '100%', borderCollapse: 'collapse', fontSize: 13 }}>
            <thead>
              <tr style={{ background: '#0b1120', borderBottom: '1px solid #1e293b' }}>
                {['Symbol', 'Type', 'Qty', 'Price', 'Total', 'Fees', 'Date', ''].map(h => (
                  <th key={h} style={{ textAlign: 'left', padding: '12px 16px', color: '#475569', fontSize: 11, textTransform: 'uppercase', letterSpacing: '0.05em', fontWeight: 600 }}>{h}</th>
                ))}
              </tr>
            </thead>
            <tbody>
              {txns.map((t, idx) => (
                <tr key={t.id} style={{ background: idx % 2 === 0 ? '#0f172a' : '#0b1120', borderBottom: '1px solid #1e293b' }}>
                  <td style={{ padding: '12px 16px', color: 'white', fontWeight: 700 }}>{t.symbol}</td>
                  <td style={{ padding: '12px 16px' }}><StatusBadge status={t.type} /></td>
                  <td style={{ padding: '12px 16px', color: '#94a3b8' }}>{t.quantity}</td>
                  <td style={{ padding: '12px 16px', color: '#94a3b8' }}>{fmtSmall(t.price)}</td>
                  <td style={{ padding: '12px 16px', color: 'white', fontWeight: 600 }}>{fmtSmall(t.quantity * t.price)}</td>
                  <td style={{ padding: '12px 16px', color: '#64748b' }}>{t.fees > 0 ? fmtSmall(t.fees) : '—'}</td>
                  <td style={{ padding: '12px 16px', color: '#64748b' }}>{t.executed_at?.slice(0, 10)}</td>
                  <td style={{ padding: '12px 16px' }}>
                    <button onClick={() => deleteTxn(t.id)} style={smallBtn('#ef4444')}>Del</button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}

      {showModal && (
        <Modal title="New Transaction" onClose={() => setShowModal(false)}>
          <ModalField label="Symbol">
            <input value={form.symbol} onChange={e => setForm({ ...form, symbol: e.target.value.toUpperCase() })} placeholder="AAPL" style={inputStyle} />
          </ModalField>
          <ModalField label="Transaction Type">
            <select value={form.type} onChange={e => setForm({ ...form, type: e.target.value as TxnType })} style={selectStyle}>
              {TYPES.map(t => <option key={t} value={t}>{t.charAt(0).toUpperCase() + t.slice(1)}</option>)}
            </select>
          </ModalField>
          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 12 }}>
            <ModalField label="Quantity">
              <input type="number" value={form.quantity} onChange={e => setForm({ ...form, quantity: e.target.value })} placeholder="10" style={inputStyle} />
            </ModalField>
            <ModalField label="Price ($)">
              <input type="number" value={form.price} onChange={e => setForm({ ...form, price: e.target.value })} placeholder="150.00" style={inputStyle} />
            </ModalField>
          </div>
          <ModalField label="Fees ($)">
            <input type="number" value={form.fees} onChange={e => setForm({ ...form, fees: e.target.value })} placeholder="0.00" style={inputStyle} />
          </ModalField>
          {form.quantity && form.price && (
            <div style={{ background: '#1e293b', borderRadius: 10, padding: '8px 12px', fontSize: 13 }}>
              <span style={{ color: '#64748b' }}>Total: </span>
              <span style={{ color: 'white', fontWeight: 600 }}>${(+form.quantity * +form.price + (+form.fees || 0)).toFixed(2)}</span>
            </div>
          )}
          <div style={{ display: 'flex', gap: 10 }}>
            <button onClick={save} disabled={saving} style={{ ...btnStyle('#f59e0b', 'black'), flex: 1, padding: '10px' }}>
              {saving ? 'Saving…' : 'Log Transaction'}
            </button>
            <button onClick={() => setShowModal(false)} style={btnStyle('#1e293b', '#94a3b8')}>Cancel</button>
          </div>
        </Modal>
      )}
    </div>
  )
}