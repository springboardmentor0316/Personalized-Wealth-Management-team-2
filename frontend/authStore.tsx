import { create } from 'zustand'
import { authAPI, User } from '../api/services'

// ── State Shape ───────────────────────────────────────────────
interface AuthState {
  user: User | null
  isLoading: boolean
  isAuthenticated: boolean

  // Actions
  login: (email: string, password: string) => Promise<void>
  register: (name: string, email: string, password: string, risk_profile?: string) => Promise<void>
  logout: () => void
  fetchMe: () => Promise<void>
}

// ── Store ─────────────────────────────────────────────────────
export const useAuthStore = create<AuthState>((set, get) => ({
  // ── Initial State ─────────────────────────────────────────
  user: null,
  isLoading: false,

  // Check localStorage on first load — if a token exists, user is considered authenticated
  isAuthenticated: !!localStorage.getItem('access_token'),

  // ── Login ─────────────────────────────────────────────────
  login: async (email: string, password: string) => {
    set({ isLoading: true })
    try {
      // Step 1: Get JWT tokens from backend
      const tokens = await authAPI.login(email, password)

      // Step 2: Persist tokens in localStorage
      localStorage.setItem('access_token', tokens.access_token)
      localStorage.setItem('refresh_token', tokens.refresh_token)

      // Step 3: Fetch the logged-in user's profile
      const user = await authAPI.me()

      set({ user, isAuthenticated: true })
    } finally {
      set({ isLoading: false })
    }
  },

  // ── Register ──────────────────────────────────────────────
  register: async (
    name: string,
    email: string,
    password: string,
    risk_profile = 'moderate'
  ) => {
    set({ isLoading: true })
    try {
      // Step 1: Create account
      await authAPI.register({ name, email, password, risk_profile: risk_profile as any })

      // Step 2: Immediately log in after registration
      const tokens = await authAPI.login(email, password)

      // Step 3: Persist tokens
      localStorage.setItem('access_token', tokens.access_token)
      localStorage.setItem('refresh_token', tokens.refresh_token)

      // Step 4: Fetch user profile
      const user = await authAPI.me()

      set({ user, isAuthenticated: true })
    } finally {
      set({ isLoading: false })
    }
  },

  // ── Logout ────────────────────────────────────────────────
  logout: () => {
    // Clear all tokens from localStorage
    localStorage.removeItem('access_token')
    localStorage.removeItem('refresh_token')

    // Reset store state
    set({ user: null, isAuthenticated: false })
  },

  // ── Fetch Current User ────────────────────────────────────
  // Called on app mount to restore session if token still valid
  fetchMe: async () => {
    // Only attempt if we have a token
    if (!localStorage.getItem('access_token')) {
      set({ isAuthenticated: false })
      return
    }
    try {
      const user = await authAPI.me()
      set({ user, isAuthenticated: true })
    } catch {
      // Token is invalid or expired — clear everything
      localStorage.removeItem('access_token')
      localStorage.removeItem('refresh_token')
      set({ user: null, isAuthenticated: false })
    }
  },
}))
