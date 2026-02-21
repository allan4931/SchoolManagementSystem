import { useState, useEffect } from 'react'
import { useNavigate, useParams } from 'react-router-dom'
import { ArrowLeft, Save, User, UserCheck, Heart } from 'lucide-react'
import { createStudent, getStudent, updateStudent } from '../../api/studentApi'
import { getClasses } from '../../api/classApi'
import PageHeader from '../../components/ui/PageHeader'
import type { Class } from '../../types'
import toast from 'react-hot-toast'

type Tab = 'personal' | 'guardian' | 'medical'
const TABS: { id: Tab; label: string; icon: typeof User }[] = [
  { id: 'personal', label: 'Personal', icon: User },
  { id: 'guardian', label: 'Guardian', icon: UserCheck },
  { id: 'medical', label: 'Medical', icon: Heart },
]

type FormData = Record<string, string | boolean>

const INIT: FormData = {
  first_name: '', last_name: '', middle_name: '', date_of_birth: '',
  gender: 'male', nationality: '', national_id: '', religion: '',
  class_id: '', admission_date: new Date().toISOString().split('T')[0],
  academic_year: '2024', previous_school: '',
  guardian_name: '', guardian_phone: '', guardian_alt_phone: '',
  guardian_email: '', guardian_relationship: 'Father',
  guardian_occupation: '', guardian_address: '',
  emergency_contact_name: '', emergency_contact_phone: '',
  blood_group: '', medical_conditions: '', allergies: '',
  disability: '', doctor_name: '', doctor_phone: '',
  uses_school_transport: false,
}

export default function StudentForm() {
  const { id } = useParams<{ id: string }>()
  const isEdit = Boolean(id)
  const navigate = useNavigate()
  const [tab, setTab] = useState<Tab>('personal')
  const [classes, setClasses] = useState<Class[]>([])
  const [loading, setLoading] = useState(false)
  const [form, setForm] = useState<FormData>(INIT)

  useEffect(() => {
    getClasses().then(({ data }) => setClasses(data as any)).catch(() => {})
    if (isEdit && id) {
      getStudent(id).then(({ data }) => setForm({ ...INIT, ...data as any })).catch(() => toast.error('Failed to load'))
    }
  }, [id, isEdit])

  const set = (field: string) => (e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement | HTMLTextAreaElement>) => {
    const value = (e.target as HTMLInputElement).type === 'checkbox' ? (e.target as HTMLInputElement).checked : e.target.value
    setForm((p) => ({ ...p, [field]: value }))
  }

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!form.first_name || !form.last_name || !form.guardian_name || !form.guardian_phone)
      return toast.error('Fill required fields')
    setLoading(true)
    try {
      const payload = { ...form, class_id: form.class_id || null }
      if (isEdit && id) { await updateStudent(id, payload as any); toast.success('Student updated') }
      else { await createStudent(payload as any); toast.success('Student registered') }
      navigate('/students')
    } catch (err: any) { toast.error(err.response?.data?.detail || 'Failed') }
    setLoading(false)
  }

  const Field = ({ label, field, type = 'text', options, required = false }: {
    label: string; field: string; type?: string; options?: { value: string; label: string }[] | string[]; required?: boolean
  }) => (
    <div>
      <label className="label">{label}{required && <span style={{ color: '#ef4444' }}> *</span>}</label>
      {options ? (
        <select className="input" value={form[field] as string} onChange={set(field)}>
          <option value="">Select...</option>
          {options.map((o) => typeof o === 'string'
            ? <option key={o} value={o}>{o}</option>
            : <option key={o.value} value={o.value}>{o.label}</option>
          )}
        </select>
      ) : (
        <input className="input" type={type} value={form[field] as string} onChange={set(field)} />
      )}
    </div>
  )

  return (
    <div style={{ maxWidth: 880 }}>
      <PageHeader
        title={isEdit ? 'Edit Student' : 'Register New Student'}
        subtitle="Fill in student details below"
        actions={<button className="btn btn-secondary" onClick={() => navigate('/students')} style={{ padding: '8px 14px' }}><ArrowLeft size={14} /> Back</button>}
      />

      <div className="tabs" style={{ marginBottom: 18, width: 'fit-content' }}>
        {TABS.map(({ id: tid, label, icon: Icon }) => (
          <button key={tid} className={`tab-btn${tab === tid ? ' active' : ''}`} onClick={() => setTab(tid)}>
            <Icon size={13} style={{ display: 'inline', marginRight: 5 }} />{label}
          </button>
        ))}
      </div>

      <form onSubmit={handleSubmit}>
        <div className="card" style={{ padding: 26 }}>
          {tab === 'personal' && (
            <div className="form-grid">
              <Field label="First Name" field="first_name" required />
              <Field label="Last Name" field="last_name" required />
              <Field label="Middle Name" field="middle_name" />
              <Field label="Date of Birth" field="date_of_birth" type="date" />
              <Field label="Gender" field="gender" required options={[{value:'male',label:'Male'},{value:'female',label:'Female'},{value:'other',label:'Other'}]} />
              <Field label="Nationality" field="nationality" />
              <Field label="National ID" field="national_id" />
              <Field label="Religion" field="religion" />
              <Field label="Class" field="class_id" options={classes.map((c) => ({ value: c.id, label: c.name }))} />
              <Field label="Admission Date" field="admission_date" type="date" required />
              <Field label="Academic Year" field="academic_year" options={['2022','2023','2024','2025']} />
              <Field label="Previous School" field="previous_school" />
              <div className="span-2">
                <label style={{ display: 'flex', alignItems: 'center', gap: 10, cursor: 'pointer' }}>
                  <input type="checkbox" checked={form.uses_school_transport as boolean} onChange={set('uses_school_transport')} style={{ width: 16, height: 16, accentColor: '#1e40af' }} />
                  <span className="label" style={{ margin: 0 }}>Uses School Transport</span>
                </label>
              </div>
            </div>
          )}
          {tab === 'guardian' && (
            <div className="form-grid">
              <Field label="Guardian Full Name" field="guardian_name" required />
              <Field label="Relationship" field="guardian_relationship" options={['Father','Mother','Uncle','Aunt','Grandparent','Sibling','Other']} />
              <Field label="Primary Phone" field="guardian_phone" required />
              <Field label="Alternate Phone" field="guardian_alt_phone" />
              <Field label="Email" field="guardian_email" type="email" />
              <Field label="Occupation" field="guardian_occupation" />
              <div className="span-2">
                <label className="label">Address</label>
                <textarea className="input" rows={3} value={form.guardian_address as string} onChange={set('guardian_address')} />
              </div>
              <Field label="Emergency Contact Name" field="emergency_contact_name" />
              <Field label="Emergency Contact Phone" field="emergency_contact_phone" />
            </div>
          )}
          {tab === 'medical' && (
            <div className="form-grid">
              <Field label="Blood Group" field="blood_group" options={['A+','A-','B+','B-','AB+','AB-','O+','O-']} />
              <Field label="Doctor Name" field="doctor_name" />
              <Field label="Doctor Phone" field="doctor_phone" />
              <div />
              <div className="span-2">
                <label className="label">Medical Conditions</label>
                <textarea className="input" rows={3} value={form.medical_conditions as string} onChange={set('medical_conditions')} placeholder="List any known conditions..." />
              </div>
              <div className="span-2">
                <label className="label">Allergies</label>
                <textarea className="input" rows={3} value={form.allergies as string} onChange={set('allergies')} placeholder="List any allergies..." />
              </div>
              <div className="span-2">
                <label className="label">Disability / Special Needs</label>
                <textarea className="input" rows={3} value={form.disability as string} onChange={set('disability')} placeholder="Describe if any..." />
              </div>
            </div>
          )}
        </div>
        <div style={{ display: 'flex', gap: 10, justifyContent: 'flex-end', marginTop: 16 }}>
          <button type="button" className="btn btn-secondary" onClick={() => navigate('/students')}>Cancel</button>
          <button type="submit" className="btn btn-primary" disabled={loading}>
            <Save size={14} />{loading ? 'Saving...' : isEdit ? 'Update Student' : 'Register Student'}
          </button>
        </div>
      </form>
    </div>
  )
}
