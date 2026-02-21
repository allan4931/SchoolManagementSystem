import { useState, useEffect } from 'react'
import { CheckCircle, XCircle, Clock, AlertCircle, Save } from 'lucide-react'
import { getClasses, getClassStudents } from '../../api/classApi'
import { bulkMarkAttendance } from '../../api/attendanceApi'
import PageHeader from '../../components/ui/PageHeader'
import type { Class, Student } from '../../types'
import toast from 'react-hot-toast'

type Status = 'present' | 'absent' | 'late' | 'excused'

const STATUS_OPTIONS: { value: Status; label: string; color: string; icon: typeof CheckCircle }[] = [
  { value: 'present', label: 'Present', color: '#10b981', icon: CheckCircle },
  { value: 'absent', label: 'Absent', color: '#ef4444', icon: XCircle },
  { value: 'late', label: 'Late', color: '#f59e0b', icon: Clock },
  { value: 'excused', label: 'Excused', color: '#3b82f6', icon: AlertCircle },
]

export default function AttendancePage() {
  const [classes, setClasses] = useState<Class[]>([])
  const [students, setStudents] = useState<Student[]>([])
  const [selectedClass, setSelectedClass] = useState('')
  const [date, setDate] = useState(new Date().toISOString().split('T')[0])
  const [term, setTerm] = useState('Term 1')
  const [attendance, setAttendance] = useState<Record<string, Status>>({})
  const [saving, setSaving] = useState(false)

  useEffect(() => { getClasses().then(({ data }) => setClasses(data as any)).catch(() => {}) }, [])

  useEffect(() => {
    if (!selectedClass) return
    getClassStudents(selectedClass).then(({ data }) => {
      setStudents(data as any)
      const init: Record<string, Status> = {}
      ;(data as Student[]).forEach((s) => { init[s.id] = 'present' })
      setAttendance(init)
    })
  }, [selectedClass])

  const handleSave = async () => {
    if (!selectedClass) return toast.error('Select a class')
    setSaving(true)
    try {
      const records = students.map((s) => ({ student_id: s.id, status: attendance[s.id] ?? 'present' }))
      await bulkMarkAttendance({ class_id: selectedClass, date, term, academic_year: '2024', records })
      toast.success(`Attendance saved for ${students.length} students`)
    } catch { toast.error('Failed to save') }
    setSaving(false)
  }

  const counts = { present: 0, absent: 0, late: 0, excused: 0 }
  Object.values(attendance).forEach((s) => { counts[s as Status]++ })

  return (
    <div>
      <PageHeader title="Attendance" subtitle="Mark daily student attendance"
        actions={<button className="btn btn-primary" onClick={handleSave} disabled={saving || !students.length}><Save size={14} />{saving ? 'Saving...' : `Save (${students.length})`}</button>} />

      {/* Controls */}
      <div className="card" style={{ padding: '14px 18px', marginBottom: 14, display: 'flex', gap: 12, flexWrap: 'wrap', alignItems: 'flex-end' }}>
        <div><label className="label">Date</label><input className="input" type="date" value={date} onChange={(e) => setDate(e.target.value)} style={{ width: 170 }} /></div>
        <div><label className="label">Class</label>
          <select className="input" value={selectedClass} onChange={(e) => setSelectedClass(e.target.value)} style={{ width: 200 }}>
            <option value="">Select class...</option>
            {classes.map((c) => <option key={c.id} value={c.id}>{c.name}</option>)}
          </select></div>
        <div><label className="label">Term</label>
          <select className="input" value={term} onChange={(e) => setTerm(e.target.value)} style={{ width: 130 }}>
            <option>Term 1</option><option>Term 2</option><option>Term 3</option>
          </select></div>
      </div>

      {/* Counts */}
      {students.length > 0 && (
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(4, 1fr)', gap: 12, marginBottom: 14 }}>
          {STATUS_OPTIONS.map(({ value, label, color, icon: Icon }) => (
            <div key={value} className="card" style={{ padding: '14px 18px', display: 'flex', alignItems: 'center', gap: 12 }}>
              <div style={{ width: 36, height: 36, background: `${color}18`, borderRadius: 10, display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
                <Icon size={16} color={color} />
              </div>
              <div>
                <p style={{ fontSize: 20, fontWeight: 800, color: '#1e293b' }}>{counts[value]}</p>
                <p style={{ fontSize: 11.5, color: '#94a3b8' }}>{label}</p>
              </div>
            </div>
          ))}
        </div>
      )}

      {!selectedClass ? (
        <div className="card" style={{ padding: '50px', textAlign: 'center', color: '#94a3b8' }}>
          <p style={{ fontWeight: 600 }}>Select a class to begin marking attendance</p>
        </div>
      ) : students.length === 0 ? (
        <div className="card" style={{ padding: '50px', textAlign: 'center', color: '#94a3b8' }}>No students found in this class</div>
      ) : (
        <div className="card">
          <div className="table-wrap">
            <table>
              <thead>
                <tr>
                  <th>#</th><th>Student</th>
                  {STATUS_OPTIONS.map(({ value, label, color }) => (
                    <th key={value} style={{ color }}>{label}</th>
                  ))}
                </tr>
              </thead>
              <tbody>
                {students.map((s, i) => (
                  <tr key={s.id}>
                    <td style={{ color: '#94a3b8', fontWeight: 600 }}>{i + 1}</td>
                    <td>
                      <div style={{ fontWeight: 600 }}>{s.full_name}</div>
                      <div style={{ fontSize: 11.5, color: '#94a3b8' }}>{s.student_id}</div>
                    </td>
                    {STATUS_OPTIONS.map(({ value, color }) => (
                      <td key={value}>
                        <label style={{ cursor: 'pointer', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
                          <input type="radio" name={s.id} value={value}
                            checked={attendance[s.id] === value}
                            onChange={() => setAttendance((p) => ({ ...p, [s.id]: value as Status }))}
                            style={{ accentColor: color, width: 16, height: 16 }} />
                        </label>
                      </td>
                    ))}
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}
    </div>
  )
}
