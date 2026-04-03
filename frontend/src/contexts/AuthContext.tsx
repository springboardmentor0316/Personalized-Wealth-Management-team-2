import React, { createContext, useContext, useReducer, useEffect, ReactNode } from 'react';
import { User, AuthResponse, RiskProfile, KYCStatus } from '../types';
import { authAPI, userAPI } from '../services/api';

interface AuthState {
  user: User | null;
  isAuthenticated: boolean;
  loading: boolean;
  error: string | null;
}

interface AuthContextType extends AuthState {
  login: (email: string, password: string) => Promise<void>;
  register: (userData: { email: string; full_name: string; password: string; risk_profile: RiskProfile; kyc_status: KYCStatus }) => Promise<void>;
  logout: () => void;
  updateProfile: (userData: Partial<User>) => Promise<void>;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

type AuthAction =
  | { type: 'LOGIN_START' }
  | { type: 'LOGIN_SUCCESS'; payload: User }
  | { type: 'LOGIN_FAILURE'; payload: string }
  | { type: 'LOGOUT' }
  | { type: 'UPDATE_PROFILE'; payload: User }
  | { type: 'SET_LOADING'; payload: boolean };

const authReducer = (state: AuthState, action: AuthAction): AuthState => {
  switch (action.type) {
    case 'LOGIN_START':
      return { ...state, loading: true, error: null };
    case 'LOGIN_SUCCESS':
      return { ...state, user: action.payload, isAuthenticated: true, loading: false, error: null };
    case 'LOGIN_FAILURE':
      return { ...state, user: null, isAuthenticated: false, loading: false, error: action.payload };
    case 'LOGOUT':
      return { ...state, user: null, isAuthenticated: false, loading: false, error: null };
    case 'UPDATE_PROFILE':
      return { ...state, user: action.payload };
    case 'SET_LOADING':
      return { ...state, loading: action.payload };
    default:
      return state;
  }
};

const initialState: AuthState = {
  user: null,
  isAuthenticated: false,
  loading: true,
  error: null,
};

interface AuthProviderProps {
  children: ReactNode;
}

export const AuthProvider: React.FC<AuthProviderProps> = ({ children }) => {
  const [state, dispatch] = useReducer(authReducer, initialState);

  useEffect(() => {
    const token = localStorage.getItem('access_token');
    if (token) {
      loadUser();
    } else {
      dispatch({ type: 'SET_LOADING', payload: false });
    }
  }, []);

  const loadUser = async () => {
    try {
      const user = await userAPI.getProfile();
      dispatch({ type: 'LOGIN_SUCCESS', payload: user });
    } catch (error) {
      localStorage.removeItem('access_token');
      localStorage.removeItem('refresh_token');
      dispatch({ type: 'LOGIN_FAILURE', payload: 'Session expired' });
    }
  };

  const login = async (email: string, password: string) => {
    dispatch({ type: 'LOGIN_START' });
    try {
      const response: AuthResponse = await authAPI.login({ email, password });
      localStorage.setItem('access_token', response.access_token);
      localStorage.setItem('refresh_token', response.refresh_token);
      const user = await userAPI.getProfile();
      dispatch({ type: 'LOGIN_SUCCESS', payload: user });
    } catch (error: any) {
      let errorMessage = 'Login failed';
      if (error.response?.data?.detail) {
        if (typeof error.response.data.detail === 'string') {
          errorMessage = error.response.data.detail;
        } else if (Array.isArray(error.response.data.detail)) {
          errorMessage = error.response.data.detail.map((e: any) => e.msg || String(e)).join(', ');
        } else {
          errorMessage = JSON.stringify(error.response.data.detail);
        }
      }
      dispatch({ type: 'LOGIN_FAILURE', payload: errorMessage });
      throw error;
    }
  };

  const register = async (userData: { email: string; full_name: string; password: string; risk_profile: RiskProfile; kyc_status: KYCStatus }) => {
    dispatch({ type: 'LOGIN_START' });
    try {
      // First register the user
      await authAPI.register(userData);
      // Then login with the credentials
      const response: AuthResponse = await authAPI.login({ email: userData.email, password: userData.password });
      localStorage.setItem('access_token', response.access_token);
      localStorage.setItem('refresh_token', response.refresh_token);
      const user = await userAPI.getProfile();
      dispatch({ type: 'LOGIN_SUCCESS', payload: user });
    } catch (error: any) {
      let errorMessage = 'Registration failed';
      
      // Log the error structure for debugging
      console.error('Registration error:', error);
      
      if (error.response) {
        // API returned an error response
        if (error.response.data?.detail) {
          if (typeof error.response.data.detail === 'string') {
            errorMessage = error.response.data.detail;
          } else if (Array.isArray(error.response.data.detail)) {
            errorMessage = error.response.data.detail.map((e: any) => e.msg || String(e)).join(', ');
          } else {
            errorMessage = JSON.stringify(error.response.data.detail);
          }
        } else if (error.response.data?.message) {
          errorMessage = error.response.data.message;
        } else if (typeof error.response.data === 'string') {
          errorMessage = error.response.data;
        }
      } else if (error.request) {
        // Request was made but no response (network error)
        errorMessage = 'Network error - please check your connection';
      } else if (error.message) {
        errorMessage = error.message;
      }
      
      dispatch({ type: 'LOGIN_FAILURE', payload: errorMessage });
      throw error;
    }
  };

  const logout = () => {
    localStorage.removeItem('access_token');
    localStorage.removeItem('refresh_token');
    dispatch({ type: 'LOGOUT' });
  };

  const updateProfile = async (userData: Partial<User>) => {
    try {
      const updatedUser = await userAPI.updateProfile(userData);
      dispatch({ type: 'UPDATE_PROFILE', payload: updatedUser });
    } catch (error: any) {
      const errorMessage = error.response?.data?.detail || 'Profile update failed';
      dispatch({ type: 'LOGIN_FAILURE', payload: errorMessage });
      throw error;
    }
  };

  const value: AuthContextType = {
    ...state,
    login,
    register,
    logout,
    updateProfile,
  };

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
};

export const useAuth = (): AuthContextType => {
  const context = useContext(AuthContext);
  if (context === undefined) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};
