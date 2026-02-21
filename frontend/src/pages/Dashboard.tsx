import { useState, useEffect } from 'react'
import { GraduationCap, Users, DollarSign, BookOpen, TrendingUp, AlertTriangle } from 'lucide-react'
import { BarChart, Bar, LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts'
import StatCard from '../components/ui/StatCard'
import { getStudents } from '../api/studentApi'
import { getTeachers } from '../api/teacherApi'
import { getArrears } from '../api/feeApi'
import { getBooks } from '../api/libraryApi'
import { formatCurrency, formatDate } from '../utils/helpers'
import { useAuthStore } from '../store/authStore'
import type { FeeInvoice } from '../types'

const attendanceData = [
  { day: 'Mon', present: 418, absent: 32 },
  { day: 'Tue', present: 388, absent: 62 },
  { day: 'Wed', present: 432, absent: 18 },
  { day: 'Thu', present: 405, absent: 45 },
  { day: 'Fri', present: 375, absent: 75 },
]

const feeData = [
  { month: 'Aug', collected: 11200 },
  { month: 'Sep', collected: 14800 },
  { month: 'Oct', collected: 13100 },
  { month: 'Nov', collected: 15700 },
  { month: 'Dec', collected: 12400 },
  { month: 'Jan', collected: 17200 },
]

export default function Dashboard() {
  const { user } = useAuthStore()
  const [stats, setStats] = useState({ students: 0, teachers: 0, books: 0 })
  const [arrears, setArrears] = useState<FeeInvoice[]>([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    Promise.allSettled([
      getStudents({ limit: 1 }),
      getTeachers({ limit: 1 }),
      getBooks({ limit: 1 }),
      getArrears(),
    ]).then(([s, t, b, a]) => {
      setStats({
        students: s.status === 'fulfilled' ? (s.value.data as any).total ?? 0 : 0,
        teachers: t.status === 'fulfilled' ? (t.value.data as any).total ?? 0 : 0,
        books: b.status === 'fulfilled' ? (b.value.data as any).total ?? 0 : 0,
      })
      if (a.status === 'fulfilled') setArrears((a.value.data as FeeInvoice[]).slice(0, 6))
    }).finally(() => setLoading(false))
  }, [])

  const totalArrears = arrears.reduce((s, i) => s + (i.balance ?? 0), 0)
  const greet = () => {
    const h = new Date().getHours()
    if (h < 12) return 'Good morning'
    if (h < 17) return 'Good afternoon'
    return 'Good evening'
  }

  return (
    <div>
      <div style={{ marginBottom: '24px' }}>
        <h1 style={{ fontSize: '24px', fontWeight: 800, color: '#1e293b' }}>
          {greet()}, {user?.full_name?.split(' ')[0]} 👋
        </h1>
        <p style={{ color: '#64748b', fontSize: '13px', marginTop: '3px' }}>
          {new Date().toLocaleDateString('en-GB', { weekday: 'long', day: 'numeric', month: 'long', year: 'numeric' })}
        </p>
      </div>

      {/* Stats */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(210px, 1fr))', gap: '14px', marginBottom: '22px' }}>
        <StatCard title="Total Students" value={loading ? '...' : stats.students} subtitle="Enrolled" icon={GraduationCap} color="#3b82f6" trend={3} />
        <StatCard title="Total Teachers" value={loading ? '...' : stats.teachers} subtitle="Active staff" icon={Users} color="#10b981" trend={1} />
        <StatCard title="Fee Arrears" value={loading ? '...' : `$${Math.round(totalArrears).toLocaleString()}`} subtitle={`${arrears.length} students`} icon={DollarSign} color="#f59e0b" />
        <StatCard title="Library Books" value={loading ? '...' : stats.books} subtitle="In catalogue" icon={BookOpen} color="#8b5cf6" trend={2} />
      </div>

      {/* Charts */}
      <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '18px', marginBottom: '22px' }}>
        <div className="card" style={{ padding: '22px' }}>
          <h3 style={{ fontSize: '14px', fontWeight: 700, color: '#1e293b', marginBottom: '4px' }}>Weekly Attendance</h3>
          <p style={{ fontSize: '12px', color: '#94a3b8', marginBottom: '18px' }}>Present vs Absent this week</p>
          <ResponsiveContainer width="100%" height={200}>
            <BarChart data={attendanceData} barSize={18}>
              <CartesianGrid strokeDasharray="3 3" stroke="#f1f5f9" />
              <XAxis dataKey="day" tick={{ fontSize: 11, fill: '#94a3b8' }} axisLine={false} tickLine={false} />
              <YAxis tick={{ fontSize: 11, fill: '#94a3b8' }} axisLine={false} tickLine={false} />
              <Tooltip contentStyle={{ borderRadius: '10px', border: '1px solid #e2e8f0', fontSize: '13px' }} />
              <Bar dataKey="present" fill="#3b82f6" radius={[5, 5, 0, 0]} name="Present" />
              <Bar dataKey="absent" fill="#fee2e2" radius={[5, 5, 0, 0]} name="Absent" />
            </BarChart>
          </ResponsiveContainer>
        </div>

        <div className="card" style={{ padding: '22px' }}>
          <h3 style={{ fontSize: '14px', fontWeight: 700, color: '#1e293b', marginBottom: '4px' }}>Fee Collection</h3>
          <p style={{ fontSize: '12px', color: '#94a3b8', marginBottom: '18px' }}>Monthly trend</p>
          <ResponsiveContainer width="100%" height={200}>
            <LineChart data={feeData}>
              <CartesianGrid strokeDasharray="3 3" stroke="#f1f5f9" />
              <XAxis dataKey="month" tick={{ fontSize: 11, fill: '#94a3b8' }} axisLine={false} tickLine={false} />
              <YAxis tick={{ fontSize: 11, fill: '#94a3b8' }} axisLine={false} tickLine={false} />
              <Tooltip formatter={(v: number) => formatCurrency(v)} contentStyle={{ borderRadius: '10px', border: '1px solid #e2e8f0', fontSize: '13px' }} />
              <Line type="monotone" dataKey="collected" stroke="#3b82f6" strokeWidth={2.5} dot={{ fill: '#3b82f6', r: 4 }} name="Collected" />
            </LineChart>
          </ResponsiveContainer>
        </div>
      </div>

      {/* Arrears table */}
      <div className="card" style={{ padding: '22px' }}>
        <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '18px' }}>
          <div>
            <h3 style={{ fontSize: '14px', fontWeight: 700, color: '#1e293b' }}>Outstanding Fee Arrears</h3>
            <p style={{ fontSize: '12px', color: '#94a3b8' }}>Students with pending balances</p>
          </div>
          <span className="badge badge-red">{arrears.length} students</span>
        </div>
        {arrears.length === 0 ? (
          <div className="empty-state">
            <TrendingUp size={40} strokeWidth={1.2} />
            <p style={{ fontWeight: 700 }}>All fees cleared!</p>
          </div>
        ) : (
          <div className="table-wrap">
            <table>
              <thead><tr><th>Invoice #</th><th>Term</th><th>Total</th><th>Paid</th><th>Balance</th><th>Due</th><th>Status</th></tr></thead>
              <tbody>
                {arrears.map((inv) => (
                  <tr key={inv.id}>
                    <td><span className="chip">{inv.invoice_number}</span></td>
                    <td>{inv.term}</td>
                    <td>{formatCurrency(inv.total_amount)}</td>
                    <td style={{ color: '#10b981', fontWeight: 600 }}>{formatCurrency(inv.paid_amount)}</td>
                    <td style={{ color: '#dc2626', fontWeight: 700 }}>{formatCurrency(inv.balance)}</td>
                    <td>{formatDate(inv.due_date)}</td>
                    <td><span className={`badge ${inv.status === 'overdue' ? 'badge-red' : 'badge-yellow'}`}>{inv.status}</span></td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </div>
  )
}
