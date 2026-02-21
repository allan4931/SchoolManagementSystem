import { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import { Plus, Edit, Trash2 } from 'lucide-react'
import { getTeachers, deleteTeacher } from '../../api/teacherApi'
import { getStatusBadge } from '../../utils/helpers'
import Avatar from '../../components/ui/Avatar'
import SearchInput from '../../components/ui/SearchInput'
import PageHeader from '../../components/ui/PageHeader'
import EmptyState from '../../components/ui/EmptyState'
import type { Teacher } from '../../types'
import { Users } from 'lucide-react'
import toast from 'react-hot-toast'

export default function TeacherList() {
  const navigate = useNavigate()
  const [teachers, setTeachers] = useState<Teacher[]>([])
  const [total, setTotal] = useState(0)
  const [search, setSearch] = useState('')
  const [loading, setLoading] = useState(true)

  const load = async () => {
    setLoading(true)
    try {
      const { data } = await getTeachers({ search: search || undefined, limit: 50 })
      const resp = data as any
      setTeachers(resp.items ?? resp)
      setTotal(resp.total ?? 0)
    } catch { toast.error('Failed') }
    setLoading(false)
  }

  useEffect(() => { load() }, [search])

  const handleDelete = async (id: string, name: string) => {
    if (!confirm(`Delete ${name}?`)) return
    try { await deleteTeacher(id); toast.success('Deleted'); load() }
    catch { toast.error('Failed') }
  }

  return (
    <div>
      <PageHeader title="Teachers" subtitle={`${total} staff members`} actions={<button className="btn btn-primary" onClick={() => navigate('/teachers/new')}><Plus size={14} /> Add Teacher</button>} />
      <div className="card" style={{ padding: '14px 18px', marginBottom: 14 }}>
        <SearchInput value={search} onChange={setSearch} placeholder="Search teachers..." />
      </div>
      <div className="card">
        <div className="table-wrap">
          <table>
            <thead><tr><th>Teacher</th><th>ID</th><th>Specialization</th><th>Phone</th><th>Email</th><th>Status</th><th>Actions</th></tr></thead>
            <tbody>
              {loading ? (
                <tr><td colSpan={7} style={{ textAlign: 'center', padding: '40px', color: '#94a3b8' }}>Loading...</td></tr>
              ) : teachers.length === 0 ? (
                <tr><td colSpan={7}><EmptyState icon={Users} title="No teachers found" /></td></tr>
              ) : teachers.map((t) => (
                <tr key={t.id}>
                  <td>
                    <div style={{ display: 'flex', alignItems: 'center', gap: 10 }}>
                      <Avatar name={t.full_name} photoUrl={t.photo_url} size={34} radius={8} type="teacher" />
                      <div>
                        <div style={{ fontWeight: 600, fontSize: '13.5px' }}>{t.full_name}</div>
                        <div style={{ fontSize: '11.5px', color: '#94a3b8' }}>{t.qualification ?? '—'}</div>
                      </div>
                    </div>
                  </td>
                  <td><span className="chip">{t.teacher_id}</span></td>
                  <td>{t.specialization ?? '—'}</td>
                  <td>{t.phone ?? '—'}</td>
                  <td>{t.email ?? '—'}</td>
                  <td><span className={`badge ${getStatusBadge(t.status)}`}>{t.status}</span></td>
                  <td>
                    <div style={{ display: 'flex', gap: 5 }}>
                      <button onClick={() => navigate(`/teachers/${t.id}/edit`)} style={{ padding: 5, background: '#f0fdf4', border: 'none', borderRadius: 6, cursor: 'pointer' }}><Edit size={12} color="#16a34a" /></button>
                      <button onClick={() => handleDelete(t.id, t.full_name)} style={{ padding: 5, background: '#fee2e2', border: 'none', borderRadius: 6, cursor: 'pointer' }}><Trash2 size={12} color="#dc2626" /></button>
                    </div>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  )
}
