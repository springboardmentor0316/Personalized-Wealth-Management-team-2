import api from './client'

// ── Types ─────────────────────────────────────────────────────
export type RiskProfile = 'conservative' | 'moderate' | 'aggressive'
export type GoalType    = 'retirement' | 'home' | 'education' | 'custom'
export type GoalStatus  = 'active' | 'paused' | 'completed'
export type AssetType   = 'stock' | 'etf' | 'mutual_fund' | 'bond' | 'cash'
export type TxnType     = 'buy' | 'sell' | 'dividend' | 'contribution' | 'withdrawal'

export interface User {
  id: number; name: string; email: string
  risk_profile: RiskProfile; kyc_status: string; created_at: string
}

export interface Goal {
  id: number; user_id: number; goal_type: GoalType
  target_amount: number; target_date: string
  monthly_contribution: number; status: GoalStatus
  created_at: string; saved?: number; progress_pct?: number
  months_remaining?: number; projected_value?: number; on_track?: boolean
}

export interface Investment {
  id: number; user_id: number; asset_type: AssetType
  symbol: string; units: number; avg_buy_price: number
  cost_basis: number; current_value: number
  last_price: number; last_price_at: string | null
}

export interface PortfolioSummary {
  total_cost_basis: number; total_current_value: number
  total_gain_loss: number; total_gain_loss_pct: number
  allocation_by_type: Record<string, number>
  positions: Investment[]
}

export interface Transaction {
  id: number; user_id: number; symbol: string; type: TxnType
  quantity: number; price: number; fees: number; executed_at: string
}

export interface TokenResponse {
  access_token: string; refresh_token: string; token_type: string
}


// ── Auth ──────────────────────────────────────────────────────
export const authAPI = {
  register: (data: { name: string; email: string; password: string; risk_profile?: RiskProfile }) =>
    api.post<User>('/auth/register', data).then(r => r.data),

  login: (email: string, password: string) =>
    api.post<TokenResponse>('/auth/login', { email, password }).then(r => r.data),

  me: () => api.get<User>('/auth/me').then(r => r.data),
}


// ── Goals ─────────────────────────────────────────────────────
export const goalsAPI = {
  list: (status?: GoalStatus) =>
    api.get<Goal[]>('/goals', { params: status ? { status } : {} }).then(r => r.data),

  get: (id: number) =>
    api.get<Goal>(`/goals/${id}`).then(r => r.data),

  create: (data: Omit<Goal, 'id' | 'user_id' | 'created_at'>) =>
    api.post<Goal>('/goals', data).then(r => r.data),

  update: (id: number, data: Partial<Goal>) =>
    api.patch<Goal>(`/goals/${id}`, data).then(r => r.data),

  delete: (id: number) =>
    api.delete(`/goals/${id}`),

  toggleStatus: (id: number) =>
    api.patch<Goal>(`/goals/${id}/status`).then(r => r.data),
}


// ── Investments ───────────────────────────────────────────────
export const investmentsAPI = {
  list: () =>
    api.get<Investment[]>('/investments').then(r => r.data),

  summary: () =>
    api.get<PortfolioSummary>('/investments/summary').then(r => r.data),

  get: (id: number) =>
    api.get<Investment>(`/investments/${id}`).then(r => r.data),

  create: (data: { asset_type: AssetType; symbol: string; units: number; avg_buy_price: number }) =>
    api.post<Investment>('/investments', data).then(r => r.data),

  update: (id: number, data: Partial<Investment>) =>
    api.patch<Investment>(`/investments/${id}`, data).then(r => r.data),

  delete: (id: number) =>
    api.delete(`/investments/${id}`),
}


// ── Transactions ──────────────────────────────────────────────
export const transactionsAPI = {
  list: (params?: { symbol?: string; type?: TxnType; limit?: number; offset?: number }) =>
    api.get<Transaction[]>('/transactions', { params }).then(r => r.data),

  get: (id: number) =>
    api.get<Transaction>(`/transactions/${id}`).then(r => r.data),

  create: (data: Omit<Transaction, 'id' | 'user_id'>) =>
    api.post<Transaction>('/transactions', data).then(r => r.data),

  delete: (id: number) =>
    api.delete(`/transactions/${id}`),
}