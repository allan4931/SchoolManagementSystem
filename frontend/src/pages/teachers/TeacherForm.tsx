import { useState, useEffect } from 'react'
import { useNavigate, useParams } from 'react-router-dom'
import { ArrowLeft, Save } from 'lucide-react'
import { createTeacher, getTeacher, updateTeacher } from '../../api/teacherApi'
import PageHeader from '../../components/ui/PageHeader'
import toast from 'react-hot-toast'

type FormData = Record<string, string>

const INIT: FormData = {
  first_name: '', last_name: '', gender: 'male', date_of_birth: '',
  nationality: '', national_id: '', phone: '', alt_phone: '', email: '',
  address: '', specialization: '', qualification: '', hire_date: '',
  salary: '', bank_name: '', bank_account: '', tax_id: '',
}

export default function TeacherForm() {
  const { id } = useParams<{ id: string }>()
  const isEdit = Boolean(id)
  const navigate = useNavigate()
  const [loading, setLoading] = useState(false)
  const [form, setForm] = useState<FormData>(INIT)

  useEffect(() => {
    if (isEdit && id) getTeacher(id).then(({ data }) => setForm({ ...INIT, ...data as any, salary: String((data as any).salary ?? '') })).catch(() => toast.error('Failed to load'))
  }, [id, isEdit])

  const set = (f: string) => (e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement>) => setForm((p) => ({ ...p, [f]: e.target.value }))

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!form.first_name || !form.last_name) return toast.error('Name required')
    setLoading(true)
    try {
      const payload = { ...form, salary: form.salary ? parseFloat(form.salary) : null }
      if (isEdit && id) { await updateTeacher(id, payload as any); toast.success('Updated') }
      else { await createTeacher(payload as any); toast.success('Teacher added') }
      navigate('/teachers')
    } catch (err: any) { toast.error(err.response?.data?.detail || 'Failed') }
    setLoading(false)
  }

  const F = ({ label, field, type = 'text', required = false }: { label: string; field: string; type?: string; required?: boolean }) => (
    <div>
      <label className="label">{label}{required && <span style={{ color: '#ef4444' }}> *</span>}</label>
      <input className="input" type={type} value={form[field]} onChange={set(field)} />
    </div>
  )

  return (
    <div style={{ maxWidth: 800 }}>
      <PageHeader title={isEdit ? 'Edit Teacher' : 'Add Teacher'} actions={<button className="btn btn-secondary" onClick={() => navigate('/teachers')} style={{ padding: '8px 14px' }}><ArrowLeft size={14} /> Back</button>} />
      <form onSubmit={handleSubmit}>
        <div className="card" style={{ padding: 24, marginBottom: 14 }}>
          <p style={{ fontSize: '12px', fontWeight: 700, color: '#64748b', textTransform: 'uppercase', marginBottom: 18, letterSpacing: '0.06em' }}>Personal Information</p>
          <div className="form-grid">
            <F label="First Name" field="first_name" required />
            <F label="Last Name" field="last_name" required />
            <F label="Date of Birth" field="date_of_birth" type="date" />
            <div><label className="label">Gender</label>
              <select className="input" value={form.gender} onChange={set('gender')}>
                <option value="male">Male</option><option value="female">Female</option>
              </select></div>
            <F label="Phone" field="phone" />
            <F label="Email" field="email" type="email" />
            <F label="National ID" field="national_id" />
            <F label="Nationality" field="nationality" />
            <F label="Hire Date" field="hire_date" type="date" />
            <F label="Qualification" field="qualification" />
            <F label="Specialization" field="specialization" />
          </div>
        </div>
        <div className="card" style={{ padding: 24, marginBottom: 14 }}>
          <p style={{ fontSize: '12px', fontWeight: 700, color: '#64748b', textTransform: 'uppercase', marginBottom: 18, letterSpacing: '0.06em' }}>Salary & Banking</p>
          <div className="form-grid">
            <F label="Monthly Salary ($)" field="salary" type="number" />
            <F label="Tax ID" field="tax_id" />
            <F label="Bank Name" field="bank_name" />
            <F label="Bank Account" field="bank_account" />
          </div>
        </div>
        <div style={{ display: 'flex', gap: 10, justifyContent: 'flex-end' }}>
          <button type="button" className="btn btn-secondary" onClick={() => navigate('/teachers')}>Cancel</button>
          <button type="submit" className="btn btn-primary" disabled={loading}><Save size={14} />{loading ? 'Saving...' : isEdit ? 'Update' : 'Add Teacher'}</button>
        </div>
      </form>
    </div>
  )
}
