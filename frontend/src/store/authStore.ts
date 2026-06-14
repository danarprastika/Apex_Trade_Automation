import { create } from 'zustand'
import { persist } from 'zustand/middleware'

export type AuthUser = {
  id: string
  email: string
  username: string
  role?: string
}

type AuthState = {
  token: string | null
  user: AuthUser | null
  isAuthenticated: boolean
  setSession: (token: string, user: AuthUser | null) => void
  clear: () => void
}

export const useAuthStore = create<AuthState>()(
  persist(
    (set) => ({
      token: null,
      user: null,
      isAuthenticated: false,
      setSession: (token, user) => set({ token, user, isAuthenticated: Boolean(token) }),
      clear: () => set({ token: null, user: null, isAuthenticated: false }),
    }),
    {
      name: 'apex-auth-storage',
    }
  )
)
