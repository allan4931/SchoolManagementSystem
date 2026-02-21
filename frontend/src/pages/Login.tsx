import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { Eye, EyeOff, Lock, User } from 'lucide-react'
import { login, getMe } from '../api/authApi'
import { useAuthStore } from '../store/authStore'
import toast from 'react-hot-toast'

export default function Login() {
  const [form, setForm] = useState({ username: '', password: '' })
  const [showPwd, setShowPwd] = useState(false)
  const [loading, setLoading] = useState(false)
  const { setAuth } = useAuthStore()
  const navigate = useNavigate()

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!form.username || !form.password) return toast.error('Enter credentials')
    setLoading(true)
    try {
      const { data: tokens } = await login(form)
      setAuth(tokens.access_token, tokens.refresh_token, null)
      const { data: user } = await getMe()
      setAuth(tokens.access_token, tokens.refresh_token, user)
      toast.success(`Welcome back, ${user.full_name}!`)
      navigate('/dashboard')
    } catch {
      toast.error('Invalid username or password')
    }
    setLoading(false)
  }

  return (
    <div style={{
      minHeight: '100vh',
      background: 'linear-gradient(135deg, #0f172a 0%, #1e3a8a 55%, #0f172a 100%)',
      display: 'flex', alignItems: 'center', justifyContent: 'center', padding: '20px',
      position: 'relative', overflow: 'hidden',
    }}>
      {/* Decorative blobs */}
      {[
        { size: 500, top: -120, right: -100, opacity: 0.12 },
        { size: 350, bottom: -80, left: -80, opacity: 0.08 },
      ].map((b, i) => (
        <div key={i} style={{
          position: 'absolute', width: b.size, height: b.size,
          background: 'radial-gradient(circle, #3b82f6, transparent 70%)',
          borderRadius: '50%', opacity: b.opacity,
          top: b.top, right: (b as any).right, bottom: (b as any).bottom, left: (b as any).left,
          pointerEvents: 'none',
        }} />
      ))}

      <div style={{ background: 'white', borderRadius: '22px', padding: '44px', width: '100%', maxWidth: '420px', boxShadow: '0 30px 60px rgba(0,0,0,0.4)', position: 'relative', animation: 'slideUp 0.35s ease' }}>
        {/* School logo + name */}
        <div style={{ textAlign: 'center', marginBottom: '34px' }}>
          <img src="/images/school-logo.svg" alt="logo" style={{ width: 64, height: 64, margin: '0 auto 14px', display: 'block' }} />
          <h1 style={{ fontSize: '22px', fontWeight: 800, color: '#1e293b', marginBottom: '4px' }}>SchoolMS</h1>
          <p style={{ color: '#64748b', fontSize: '13.5px' }}>School Management System</p>
        </div>

        <form onSubmit={handleSubmit}>
          <div style={{ marginBottom: '16px' }}>
            <label className="label">Username</label>
            <div style={{ position: 'relative' }}>
              <User size={14} color="#94a3b8" style={{ position: 'absolute', left: 12, top: '50%', transform: 'translateY(-50%)' }} />
              <input className="input" style={{ paddingLeft: 36 }} placeholder="Enter your username"
                value={form.username} onChange={(e) => setForm({ ...form, username: e.target.value })} autoComplete="username" />
            </div>
          </div>

          <div style={{ marginBottom: '26px' }}>
            <label className="label">Password</label>
            <div style={{ position: 'relative' }}>
              <Lock size={14} color="#94a3b8" style={{ position: 'absolute', left: 12, top: '50%', transform: 'translateY(-50%)' }} />
              <input className="input" style={{ paddingLeft: 36, paddingRight: 40 }}
                type={showPwd ? 'text' : 'password'} placeholder="Enter your password"
                value={form.password} onChange={(e) => setForm({ ...form, password: e.target.value })} autoComplete="current-password" />
              <button type="button" onClick={() => setShowPwd(!showPwd)} style={{ position: 'absolute', right: 12, top: '50%', transform: 'translateY(-50%)', border: 'none', background: 'none', cursor: 'pointer' }}>
                {showPwd ? <EyeOff size={15} color="#94a3b8" /> : <Eye size={15} color="#94a3b8" />}
              </button>
            </div>
          </div>

          <button type="submit" className="btn btn-primary" disabled={loading}
            style={{ width: '100%', justifyContent: 'center', padding: '12px', fontSize: '14px' }}>
            {loading ? 'Signing in...' : 'Sign In'}
          </button>
        </form>

        <p style={{ textAlign: 'center', fontSize: '11.5px', color: '#94a3b8', marginTop: '22px' }}>
          © {new Date().getFullYear()} SchoolMS. All rights reserved.
        </p>
      </div>
    </div>
  )
}
