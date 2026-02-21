import { Bell, Search } from 'lucide-react'
import { useAuthStore } from '../../store/authStore'
import { useUIStore } from '../../store/uiStore'
import Avatar from '../ui/Avatar'
import SyncBadge from '../ui/SyncBadge'

export default function Navbar() {
  const { user } = useAuthStore()
  const { sidebarOpen } = useUIStore()

  return (
    <header style={{
      position: 'fixed', top: 0, left: sidebarOpen ? 260 : 70, right: 0,
      height: 64, background: 'white',
      borderBottom: '1px solid #e2e8f0',
      display: 'flex', alignItems: 'center', padding: '0 22px',
      zIndex: 50, gap: '14px', transition: 'left 0.28s ease',
      boxShadow: '0 1px 3px rgba(0,0,0,0.03)',
    }}>
      <div style={{ flex: 1, display: 'flex', alignItems: 'center', gap: '14px' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '9px', background: '#f8fafc', border: '1px solid #e2e8f0', borderRadius: '9px', padding: '7px 13px', maxWidth: '380px', width: '100%' }}>
          <Search size={14} color="#94a3b8" />
          <input placeholder="Search students, teachers..." style={{ border: 'none', background: 'none', outline: 'none', fontSize: '13.5px', color: '#374151', width: '100%', fontFamily: 'inherit' }} />
        </div>
      </div>
      <SyncBadge />
      <button style={{ width: 36, height: 36, borderRadius: '9px', border: '1px solid #e2e8f0', background: 'white', display: 'flex', alignItems: 'center', justifyContent: 'center', cursor: 'pointer', position: 'relative' }}>
        <Bell size={15} color="#64748b" />
        <span style={{ position: 'absolute', top: 7, right: 7, width: 7, height: 7, background: '#ef4444', borderRadius: '50%', border: '2px solid white' }} />
      </button>
      <div style={{ display: 'flex', alignItems: 'center', gap: '9px' }}>
        <Avatar name={user?.full_name} size={34} radius={9} />
        <div>
          <div style={{ fontSize: '13px', fontWeight: 700, color: '#1e293b' }}>{user?.full_name}</div>
          <div style={{ fontSize: '11px', color: '#94a3b8', textTransform: 'capitalize' }}>{user?.role}</div>
        </div>
      </div>
    </header>
  )
}
