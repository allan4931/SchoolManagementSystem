import { useState, useEffect } from 'react'
import { Plus, Edit, Trash2, Users } from 'lucide-react'
import { getClasses, createClass, updateClass, deleteClass } from '../../api/classApi'
import { getTeachers } from '../../api/teacherApi'
import Modal from '../../components/ui/Modal'
import PageHeader from '../../components/ui/PageHeader'
import EmptyState from '../../components/ui/EmptyState'
import type { Class, Teacher } from '../../types'
import { School2 } from 'lucide-react'
import toast from 'react-hot-toast'

const gradients = ['linear-gradient(135deg,#1e40af,#3b82f6)','linear-gradient(135deg,#059669,#10b981)','linear-gradient(135deg,#7c3aed,#8b5cf6)','linear-gradient(135deg,#b45309,#f59e0b)','linear-gradient(135deg,#be123c,#f43f5e)']

export default function ClassList() {
  const [classes, setClasses] = useState<Class[]>([])
  const [teachers, setTeachers] = useState<Teacher[]>([])
  const [modal, setModal] = useState(false)
  const [editItem, setEditItem] = useState<Class | null>(null)
  const [form, setForm] = useState({ name: '', grade_level: '', stream: '', academic_year: '2024', capacity: '40', class_teacher_id: '' })

  const load = async () => {
    const [c, t] = await Promise.all([getClasses(), getTeachers({ limit: 100 })])
    setClasses(c.data as any)
    setTeachers(((t.data as any).items ?? t.data) as Teacher[])
  }

  useEffect(() => { load() }, [])

  const open = (item: Class | null = null) => {
    setEditItem(item)
    setForm(item ? { ...item, class_teacher_id: item.class_teacher_id ?? '', capacity: String(item.capacity) } : { name: '', grade_level: '', stream: '', academic_year: '2024', capacity: '40', class_teacher_id: '' })
    setModal(true)
  }

  const handleSave = async () => {
    if (!form.name || !form.grade_level) return toast.error('Name & grade required')
    try {
      const payload = { ...form, capacity: parseInt(form.capacity), class_teacher_id: form.class_teacher_id || null }
      if (editItem) { await updateClass(editItem.id, payload as any); toast.success('Updated') }
      else { await createClass(payload as any); toast.success('Class created') }
      setModal(false); load()
    } catch { toast.error('Failed') }
  }

  const set = (f: string) => (e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement>) => setForm((p) => ({ ...p, [f]: e.target.value }))

  return (
    <div>
      <PageHeader title="Classes & Subjects" subtitle={`${classes.length} classes`} actions={<button className="btn btn-primary" onClick={() => open()}><Plus size={14} /> Add Class</button>} />
      {classes.length === 0 ? (
        <EmptyState icon={School2} title="No classes yet" action={<button className="btn btn-primary" onClick={() => open()}><Plus size={14} /> Create First Class</button>} />
      ) : (
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(255px, 1fr))', gap: 14 }}>
          {classes.map((c, i) => (
            <div key={c.id} className="card" style={{ padding: 20 }}>
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: 14 }}>
                <div style={{ width: 44, height: 44, background: gradients[i % gradients.length], borderRadius: 12, display: 'flex', alignItems: 'center', justifyContent: 'center', color: 'white', fontWeight: 800, fontSize: 16 }}>
                  {c.stream || c.grade_level?.slice(-1) || 'C'}
                </div>
                <div style={{ display: 'flex', gap: 5 }}>
                  <button onClick={() => open(c)} style={{ padding: 5, background: '#f0fdf4', border: 'none', borderRadius: 6, cursor: 'pointer' }}><Edit size={12} color="#16a34a" /></button>
                  <button onClick={async () => { if (!confirm('Delete?')) return; try { await deleteClass(c.id); toast.success('Deleted'); load() } catch { toast.error('Failed') } }} style={{ padding: 5, background: '#fee2e2', border: 'none', borderRadius: 6, cursor: 'pointer' }}><Trash2 size={12} color="#dc2626" /></button>
                </div>
              </div>
              <h3 style={{ fontSize: 15, fontWeight: 700, color: '#1e293b' }}>{c.name}</h3>
              <p style={{ fontSize: 12, color: '#94a3b8', marginTop: 2 }}>{c.grade_level} • {c.academic_year}</p>
              <div style={{ marginTop: 12, display: 'flex', alignItems: 'center', gap: 6, fontSize: 12, color: '#64748b' }}>
                <Users size={12} /> Capacity: {c.capacity}
              </div>
            </div>
          ))}
        </div>
      )}

      <Modal isOpen={modal} onClose={() => setModal(false)} title={editItem ? 'Edit Class' : 'Create Class'}>
        <div className="form-grid">
          <div><label className="label">Class Name *</label><input className="input" value={form.name} onChange={set('name')} placeholder="e.g. Form 3A" /></div>
          <div><label className="label">Grade Level *</label><input className="input" value={form.grade_level} onChange={set('grade_level')} placeholder="e.g. Form 3" /></div>
          <div><label className="label">Stream</label><input className="input" value={form.stream} onChange={set('stream')} placeholder="e.g. A" /></div>
          <div><label className="label">Academic Year</label>
            <select className="input" value={form.academic_year} onChange={set('academic_year')}>
              {['2022','2023','2024','2025'].map((y) => <option key={y}>{y}</option>)}
            </select></div>
          <div><label className="label">Capacity</label><input className="input" type="number" value={form.capacity} onChange={set('capacity')} /></div>
          <div><label className="label">Class Teacher</label>
            <select className="input" value={form.class_teacher_id} onChange={set('class_teacher_id')}>
              <option value="">None</option>
              {teachers.map((t) => <option key={t.id} value={t.id}>{t.full_name}</option>)}
            </select></div>
        </div>
        <div style={{ display: 'flex', gap: 10, justifyContent: 'flex-end', marginTop: 20 }}>
          <button className="btn btn-secondary" onClick={() => setModal(false)}>Cancel</button>
          <button className="btn btn-primary" onClick={handleSave}>Save Class</button>
        </div>
      </Modal>
    </div>
  )
}
