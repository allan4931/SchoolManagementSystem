import { Outlet } from 'react-router-dom'
import Sidebar from './Sidebar'
import Navbar from './Navbar'
import { useUIStore } from '../../store/uiStore'

export default function Layout() {
  const { sidebarOpen } = useUIStore()
  const ml = sidebarOpen ? 260 : 70

  return (
    <div style={{ display: 'flex', minHeight: '100vh', background: '#f1f5f9' }}>
      <Sidebar />
      <div style={{ flex: 1, marginLeft: ml, transition: 'margin-left 0.28s ease', display: 'flex', flexDirection: 'column', minHeight: '100vh' }}>
        <Navbar />
        <main style={{ flex: 1, padding: '22px', marginTop: 64 }}>
          <div className="page-in">
            <Outlet />
          </div>
        </main>
      </div>
    </div>
  )
}
