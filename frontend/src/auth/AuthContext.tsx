import { createContext, useContext, useEffect, useState, type ReactNode } from 'react'

export interface User {
  id: number
  first_name: string
  last_name: string
  email: string
}

export interface RegisterData {
  first_name: string
  last_name: string
  email: string
  password: string
}

interface AuthState {
  user: User | null
  checking: boolean // true until we know whether a session cookie is still valid
  login: (email: string, password: string) => Promise<void>
  register: (data: RegisterData) => Promise<void>
  logout: () => Promise<void>
}

const AuthContext = createContext<AuthState | null>(null)

// POST JSON and return the response body; throw the backend's error message on failure.
async function postJson<T>(url: string, body?: unknown): Promise<T> {
  const res = await fetch(url, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: body === undefined ? undefined : JSON.stringify(body),
  })
  const data = await res.json().catch(() => ({}))
  if (!res.ok) throw new Error(typeof data.detail === 'string' ? data.detail : 'Something went wrong. Please try again.')
  return data as T
}

// Wraps the app so every page and the nav bar can see who is logged in.
export function AuthProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<User | null>(null)
  const [checking, setChecking] = useState(true)

  // On page load, ask the backend whether the session cookie still belongs to someone.
  useEffect(() => {
    fetch('/api/auth/me')
      .then((res) => (res.ok ? res.json() : null))
      .then((data: User | null) => setUser(data))
      .catch(() => setUser(null))
      .finally(() => setChecking(false))
  }, [])

  const value: AuthState = {
    user,
    checking,
    login: async (email, password) => setUser(await postJson<User>('/api/auth/login', { email, password })),
    register: async (data) => setUser(await postJson<User>('/api/auth/register', data)),
    logout: async () => {
      await postJson('/api/auth/logout')
      setUser(null)
    },
  }

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>
}

// eslint-disable-next-line react-refresh/only-export-components
export function useAuth(): AuthState {
  const ctx = useContext(AuthContext)
  if (!ctx) throw new Error('useAuth must be used inside <AuthProvider>')
  return ctx
}
