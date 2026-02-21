import { useState, useEffect, useCallback } from 'react'
import { useNavigate } from 'react-router-dom'
import { Plus, Eye, Edit, Trash2, UserX } from 'lucide-react'
import { getStudents, deleteStudent } from '../../api/studentApi'
import { getClasses } from '../../api/classApi'
import { formatDate, getStatusBadge } from '../../utils/helpers'
import Avatar from '../../components/ui/Avatar'
import SearchInput from '../../components/ui/SearchInput'
import PageHeader from '../../components/ui/PageHeader'
import EmptyState from '../../components/ui/EmptyState'
import Pagination from '../../components/ui/Pagination'
import type { Student, Class } from '../../types'
import toast from 'react-hot-toast'

const LIMIT = 15

export default function StudentList() {
  const navigate = useNavigate()
  const [students, setStudents] = useState<Student[]>([])
  const [classes, setClasses] = useState<Class[]>([])
  const [total, setTotal] = useState(0)
  const [page, setPage] = useState(0)
  const [search, setSearch] = useState('')
  const [classFilter, setClassFilter] = useState('')
  const [statusFilter, setStatusFilter] = useState('')
  const [loading, setLoading] = useState(true)

  const load = useCallback(async () => {
    setLoading(true)
    try {
      const { data } = await getStudents({ skip: page * LIMIT, limit: LIMIT, search: search || undefined, class_id: classFilter || undefined, status: statusFilter || undefined })
      const resp = data as any
      setStudents(resp.items ?? resp)
      setTotal(resp.total ?? 0)
    } catch { toast.error('Failed to load students') }
    setLoading(false)
  }, [page, search, classFilter, statusFilter])

  useEffect(() => { load() }, [load])
  useEffect(() => { getClasses().then(({ data }) => setClasses(data as any)).catch(() => {}) }, [])

  const handleDelete = async (id: string, name: string) => {
    if (!confirm(`Delete ${name}?`)) return
    try { await deleteStudent(id); toast.success('Deleted'); load() }
    catch { toast.error('Failed to delete') }
  }

  return (
    <div>
      <PageHeader
        title="Students"
        subtitle={`${total} students enrolled`}
        actions={<>
          <button className="btn btn-primary" onClick={() => navigate('/students/new')}><Plus size={14} /> Add Student</button>
        </>}
      />

      {/* Filters */}
      <div className="card" style={{ padding: '14px 18px', marginBottom: '14px', display: 'flex', gap: '10px', flexWrap: 'wrap' }}>
        <SearchInput value={search} onChange={(v) => { setSearch(v); setPage(0) }} placeholder="Search name, ID, phone..." style={{ flex: 1, minWidth: 200 }} />
        <select className="input" style={{ width: 180 }} value={classFilter} onChange={(e) => { setClassFilter(e.target.value); setPage(0) }}>
          <option value="">All Classes</option>
          {classes.map((c) => <option key={c.id} value={c.id}>{c.name}</option>)}
        </select>
        <select className="input" style={{ width: 150 }} value={statusFilter} onChange={(e) => { setStatusFilter(e.target.value); setPage(0) }}>
          <option value="">All Status</option>
          {['active','transferred','suspended','graduated','inactive'].map((s) => <option key={s} value={s}>{s.charAt(0).toUpperCase() + s.slice(1)}</option>)}
        </select>
      </div>

      <div className="card">
        <div className="table-wrap">
          <table>
            <thead>
              <tr>
                <th>Student</th><th>ID</th><th>Class</th><th>Guardian</th><th>Phone</th><th>Admission</th><th>Status</th><th>Actions</th>
              </tr>
            </thead>
            <tbody>
              {loading ? (
                <tr><td colSpan={8} style={{ textAlign: 'center', padding: '40px', color: '#94a3b8' }}>Loading...</td></tr>
              ) : students.length === 0 ? (
                <tr><td colSpan={8}><EmptyState icon={UserX} title="No students found" subtitle="Try adjusting your filters" /></td></tr>
              ) : students.map((s) => (
                <tr key={s.id}>
                  <td>
                    <div style={{ display: 'flex', alignItems: 'center', gap: 10 }}>
                      <Avatar name={s.full_name} photoUrl={s.photo_url} size={34} radius={8} />
                      <div>
                        <div style={{ fontWeight: 600, fontSize: '13.5px' }}>{s.full_name}</div>
                        <div style={{ fontSize: '11.5px', color: '#94a3b8', textTransform: 'capitalize' }}>{s.gender}</div>
                      </div>
                    </div>
                  </td>
                  <td><span className="chip">{s.student_id}</span></td>
                  <td>{classes.find((c) => c.id === s.class_id)?.name ?? '—'}</td>
                  <td>{s.guardian_name}</td>
                  <td>{s.guardian_phone}</td>
                  <td>{formatDate(s.admission_date)}</td>
                  <td><span className={`badge ${getStatusBadge(s.status)}`}>{s.status}</span></td>
                  <td>
                    <div style={{ display: 'flex', gap: 5 }}>
                      <button onClick={() => navigate(`/students/${s.id}`)} style={{ padding: 5, background: '#dbeafe', border: 'none', borderRadius: 6, cursor: 'pointer' }}><Eye size={12} color="#1d4ed8" /></button>
                      <button onClick={() => navigate(`/students/${s.id}/edit`)} style={{ padding: 5, background: '#f0fdf4', border: 'none', borderRadius: 6, cursor: 'pointer' }}><Edit size={12} color="#16a34a" /></button>
                      <button onClick={() => handleDelete(s.id, s.full_name)} style={{ padding: 5, background: '#fee2e2', border: 'none', borderRadius: 6, cursor: 'pointer' }}><Trash2 size={12} color="#dc2626" /></button>
                    </div>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
        {total > LIMIT && <Pagination page={page} total={total} limit={LIMIT} onPrev={() => setPage((p) => p - 1)} onNext={() => setPage((p) => p + 1)} />}
      </div>
    </div>
  )
}
