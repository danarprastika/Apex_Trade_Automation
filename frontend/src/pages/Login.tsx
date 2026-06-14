import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { useAuthStore } from '@/store/authStore'
import { api } from '@/services/api'

export default function Login() {
  const navigate = useNavigate()
  const setSession = useAuthStore((s) => s.setSession)
  const [error, setError] = useState<string | null>(null)

  const onSubmit = async (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault()
    const data = new FormData(e.currentTarget)
    const email = String(data.get('email') || '').trim()
    const password = String(data.get('password') || '')
    setError(null)
    try {
      const { data: payload } = await api.post('/auth/login', new URLSearchParams({ email, password }).toString(), {
        headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
      })
      const token = payload?.data?.access_token as string | undefined
      if (!token) throw new Error('Token tidak diterima')
      setSession(token, null)
      navigate('/dashboard', { replace: true })
    } catch (err) {
      setError('Gagal login. Periksa kredensial Anda.')
    }
  }

  return (
    <div className="flex min-h-screen items-center justify-center bg-slate-950 p-4">
      <form onSubmit={onSubmit} className="w-full max-w-sm rounded-lg border border-slate-800 bg-slate-900 p-6 shadow-lg">
        <h1 className="mb-6 text-center text-2xl font-semibold text-white">Masuk ke APEX</h1>
        {error ? <p className="mb-4 text-sm text-red-400">{error}</p> : null}
        <label className="mb-2 block text-sm text-slate-300">Email</label>
        <input name="email" required type="email" className="mb-4 w-full rounded-md border border-slate-800 bg-slate-950 p-2 text-white outline-none focus:border-slate-500" />
        <label className="mb-2 block text-sm text-slate-300">Password</label>
        <input name="password" required type="password" className="mb-6 w-full rounded-md border border-slate-800 bg-slate-950 p-2 text-white outline-none focus:border-slate-500" />
        <button type="submit" className="w-full rounded-md bg-white p-2 font-medium text-slate-900 hover:bg-slate-200">Login</button>
      </form>
    </div>
  )
}
