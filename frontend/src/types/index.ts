export enum RiskProfile {
  CONSERVATIVE = 'conservative',
  MODERATE = 'moderate',
  AGGRESSIVE = 'aggressive'
}

export enum KYCStatus {
  PENDING = 'pending',
  VERIFIED = 'verified',
  REJECTED = 'rejected'
}

export enum GoalCategory {
  RETIREMENT = 'retirement',
  EDUCATION = 'education',
  HOME = 'home',
  VACATION = 'vacation',
  EMERGENCY = 'emergency',
  OTHER = 'other'
}

export enum InvestmentType {
  STOCK = 'stock',
  ETF = 'etf',
  MUTUAL_FUND = 'mutual_fund',
  BOND = 'bond',
  CRYPTO = 'crypto'
}

export enum TransactionType {
  BUY = 'buy',
  SELL = 'sell'
}

export interface User {
  id: number;
  email: string;
  full_name: string;
  risk_profile: RiskProfile;
  kyc_status: KYCStatus;
  created_at: string;
  updated_at: string;
}

export interface UserCreate {
  email: string;
  full_name: string;
  password: string;
  risk_profile: RiskProfile;
  kyc_status: KYCStatus;
}

export interface UserLogin {
  email: string;
  password: string;
}

export interface Goal {
  id: number;
  user_id: number;
  title: string;
  description?: string;
  target_amount: number;
  current_amount: number;
  target_date: string;
  monthly_contribution: number;
  category: GoalCategory;
  created_at: string;
  updated_at: string;
}

export interface GoalCreate {
  title: string;
  description?: string;
  target_amount: number;
  current_amount?: number;
  target_date: string;
  monthly_contribution?: number;
  category: GoalCategory;
}

export interface Investment {
  id: number;
  user_id: number;
  symbol: string;
  name: string;
  type: InvestmentType;
  quantity: number;
  average_cost: number;
  current_price: number;
  created_at: string;
  updated_at: string;
}

export interface InvestmentCreate {
  symbol: string;
  name: string;
  type: InvestmentType;
  quantity: number;
  average_cost: number;
  current_price: number;
}

export interface Transaction {
  id: number;
  user_id: number;
  investment_id: number;
  type: TransactionType;
  quantity: number;
  price: number;
  amount: number;
  date: string;
  created_at: string;
}

export interface TransactionCreate {
  investment_id: number;
  type: TransactionType;
  quantity: number;
  price: number;
  amount: number;
  date: string;
}

export interface AuthResponse {
  access_token: string;
  refresh_token: string;
  token_type: string;
  user: User;
}

export interface PortfolioItem {
  id: number;
  symbol: string;
  name: string;
  type: InvestmentType;
  quantity: number;
  average_cost: number;
  current_price: number;
  current_value: number;
  cost_basis: number;
  gain_loss: number;
  gain_loss_percent: number;
}

export interface PortfolioSummary {
  total_value: number;
  total_cost: number;
  total_gain_loss: number;
  total_gain_loss_percent: number;
}

export interface Portfolio {
  investments: PortfolioItem[];
  summary: PortfolioSummary;
}
