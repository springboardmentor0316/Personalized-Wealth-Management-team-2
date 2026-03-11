import axios from 'axios';
import { User, UserCreate, UserLogin, AuthResponse, Goal, GoalCreate, Investment, InvestmentCreate, Transaction, TransactionCreate, Portfolio } from '../types';

const API_BASE_URL = 'http://localhost:8001/api';

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

api.interceptors.request.use((config) => {
  const token = localStorage.getItem('access_token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

api.interceptors.response.use(
  (response) => response,
  async (error) => {
    const originalRequest = error.config;
    if (error.response?.status === 401 && !originalRequest._retry) {
      originalRequest._retry = true;
      try {
        const refreshToken = localStorage.getItem('refresh_token');
        if (refreshToken) {
          const response = await axios.post(`${API_BASE_URL}/auth/refresh`, {}, {
            headers: {
              Authorization: `Bearer ${refreshToken}`,
            },
          });
          const { access_token } = response.data;
          localStorage.setItem('access_token', access_token);
          originalRequest.headers.Authorization = `Bearer ${access_token}`;
          return api(originalRequest);
        }
      } catch (refreshError) {
        localStorage.removeItem('access_token');
        localStorage.removeItem('refresh_token');
        window.location.href = '/login';
      }
    }
    return Promise.reject(error);
  }
);

export const authAPI = {
  register: async (userData: UserCreate): Promise<User> => {
    const response = await api.post('/auth/register', userData);
    return response.data;
  },
  login: async (credentials: UserLogin): Promise<AuthResponse> => {
    const response = await api.post('/auth/login', credentials);
    return response.data;
  },
  refreshToken: async (): Promise<{ access_token: string; token_type: string }> => {
    const response = await api.post('/auth/refresh');
    return response.data;
  },
};

export const userAPI = {
  getProfile: async (): Promise<User> => {
    const response = await api.get('/users/profile');
    return response.data;
  },
  updateProfile: async (userData: Partial<User>): Promise<User> => {
    const response = await api.put('/users/profile', userData);
    return response.data;
  },
};

export const goalsAPI = {
  getGoals: async (): Promise<Goal[]> => {
    const response = await api.get('/goals');
    return response.data;
  },
  getGoal: async (id: number): Promise<Goal> => {
    const response = await api.get(`/goals/${id}`);
    return response.data;
  },
  createGoal: async (goalData: GoalCreate): Promise<Goal> => {
    const response = await api.post('/goals', goalData);
    return response.data;
  },
  updateGoal: async (id: number, goalData: Partial<GoalCreate>): Promise<Goal> => {
    const response = await api.put(`/goals/${id}`, goalData);
    return response.data;
  },
  deleteGoal: async (id: number): Promise<void> => {
    await api.delete(`/goals/${id}`);
  },
};

export const investmentsAPI = {
  getInvestments: async (): Promise<Investment[]> => {
    const response = await api.get('/investments');
    return response.data;
  },
  createInvestment: async (investmentData: InvestmentCreate): Promise<Investment> => {
    const response = await api.post('/investments', investmentData);
    return response.data;
  },
};

export const transactionsAPI = {
  getTransactions: async (): Promise<Transaction[]> => {
    const response = await api.get('/transactions');
    return response.data;
  },
  createTransaction: async (transactionData: TransactionCreate): Promise<Transaction> => {
    const response = await api.post('/transactions', transactionData);
    return response.data;
  },
};

export const portfolioAPI = {
  getPortfolio: async (): Promise<Portfolio> => {
    const response = await api.get('/portfolio');
    return response.data;
  },
};

export default api;
