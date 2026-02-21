import { NavLink, useNavigate } from 'react-router-dom'
import {
  LayoutDashboard, Users, GraduationCap, School2,
  CalendarCheck, DollarSign, ClipboardList, BookOpen,
  Bus, Package, LogOut, ChevronLeft, ChevronRight,
} from 'lucide-react'
import { useAuthStore } from '../../store/authStore'
import { useUIStore } from '../../store/uiStore'
import Avatar from '../ui/Avatar'

const NAV = [
  { to: '/dashboard', icon: LayoutDashboard, label: 'Dashboard' },
  { to: '/students', icon: GraduationCap, label: 'Students' },
  { to: '/teachers', icon: Users, label: 'Teachers' },
  { to: '/classes', icon: School2, label: 'Classes & Subjects' },
  { to: '/attendance', icon: CalendarCheck, label: 'Attendance' },
  { to: '/fees', icon: DollarSign, label: 'Fees & Payments' },
  { to: '/exams', icon: ClipboardList, label: 'Exams & Results' },
  { to: '/library', icon: BookOpen, label: 'Library' },
  { to: '/transport', icon: Bus, label: 'Transport' },
  { to: '/inventory', icon: Package, label: 'Inventory' },
]

export default function Sidebar() {
  const { user, logout } = useAuthStore()
  const { sidebarOpen, toggleSidebar } = useUIStore()
  const navigate = useNavigate()

  const handleLogout = () => { logout(); navigate('/login') }
  const W = sidebarOpen ? 260 : 70

  return (
    <aside style={{
      position: 'fixed', top: 0, left: 0, bottom: 0, width: W,
      background: '#0f172a', display: 'flex', flexDirection: 'column',
      zIndex: 100, transition: 'width 0.28s ease', overflow: 'hidden',
      borderRight: '1px solid rgba(255,255,255,0.04)',
    }}>
      {/* Logo */}
      <div style={{ padding: '16px 14px', borderBottom: '1px solid rgba(255,255,255,0.06)', display: 'flex', alignItems: 'center', gap: '11px', minHeight: 64 }}>
        <img src="/images/school-logo.svg" alt="logo" style={{ width: 38, height: 38, minWidth: 38, borderRadius: 10 }} />
        {sidebarOpen && (
          <div>
            <div style={{ color: 'white', fontWeight: 800, fontSize: '14px', lineHeight: 1.2 }}>SchoolMS</div>
            <div style={{ color: '#475569', fontSize: '11px' }}>Management System</div>
          </div>
        )}
      </div>

      {/* Toggle button */}
      <button onClick={toggleSidebar} style={{
        position: 'absolute', top: '22px', right: '-11px',
        width: 22, height: 22, borderRadius: '50%',
        background: '#1e40af', border: 'none', cursor: 'pointer',
        display: 'flex', alignItems: 'center', justifyContent: 'center',
        color: 'white', zIndex: 10, boxShadow: '0 2px 8px rgba(0,0,0,0.3)',
      }}>
        {sidebarOpen ? <ChevronLeft size={11} /> : <ChevronRight size={11} />}
      </button>

      {/* Nav */}
      <nav style={{ flex: 1, padding: '10px 9px', overflowY: 'auto', overflowX: 'hidden' }}>
        {sidebarOpen && (
          <p style={{ color: '#334155', fontSize: '10px', fontWeight: 700, padding: '8px 6px 4px', textTransform: 'uppercase', letterSpacing: '0.07em' }}>
            Main Menu
          </p>
        )}
        {NAV.map(({ to, icon: Icon, label }) => (
          <NavLink
            key={to}
            to={to}
            className={({ isActive }) => `sidebar-link${isActive ? ' active' : ''}`}
            style={{ marginBottom: '2px', justifyContent: sidebarOpen ? 'flex-start' : 'center' }}
            title={!sidebarOpen ? label : undefined}
          >
            <Icon size={17} style={{ minWidth: 17 }} />
            {sidebarOpen && <span>{label}</span>}
          </NavLink>
        ))}
      </nav>

      {/* User + logout */}
      <div style={{ padding: '10px 9px', borderTop: '1px solid rgba(255,255,255,0.06)' }}>
        {sidebarOpen && user && (
          <div style={{ padding: '10px 11px', background: 'rgba(255,255,255,0.04)', borderRadius: '10px', marginBottom: '8px', display: 'flex', alignItems: 'center', gap: '10px' }}>
            <Avatar name={user.full_name} size={32} radius={8} />
            <div style={{ overflow: 'hidden' }}>
              <div style={{ color: 'white', fontWeight: 600, fontSize: '12.5px', overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>{user.full_name}</div>
              <span style={{ background: 'rgba(59,130,246,0.2)', color: '#60a5fa', fontSize: '10px', fontWeight: 600, padding: '1px 7px', borderRadius: '10px', textTransform: 'capitalize', display: 'inline-block' }}>{user.role}</span>
            </div>
          </div>
        )}
        <button onClick={handleLogout} className="sidebar-link" style={{ justifyContent: sidebarOpen ? 'flex-start' : 'center', width: '100%' }}>
          <LogOut size={17} style={{ minWidth: 17 }} />
          {sidebarOpen && <span>Logout</span>}
        </button>
      </div>
    </aside>
  )
}
