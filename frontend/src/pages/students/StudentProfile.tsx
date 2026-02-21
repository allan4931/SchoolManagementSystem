import { useState, useEffect } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import { ArrowLeft, Edit, Camera, UserX, ArrowRightLeft } from 'lucide-react'
import { getStudent, uploadPhoto, suspendStudent, transferStudent } from '../../api/studentApi'
import { formatDate, getStatusBadge, getInitials } from '../../utils/helpers'
import Avatar from '../../components/ui/Avatar'
import Modal from '../../components/ui/Modal'
import type { Student } from '../../types'
import toast from 'react-hot-toast'

interface InfoItem { label: string; value: string }

function InfoGrid({ items }: { items: InfoItem[] }) {
  return (
    <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '14px' }}>
      {items.map(({ label, value }) => (
        <div key={label}>
          <p style={{ fontSize: '10.5px', fontWeight: 700, color: '#94a3b8', textTransform: 'uppercase', letterSpacing: '0.06em' }}>{label}</p>
          <p style={{ fontSize: '13.5px', fontWeight: 600, color: '#1e293b', marginTop: '2px' }}>{value || '—'}</p>
        </div>
      ))}
    </div>
  )
}

export default function StudentProfile() {
  const { id } = useParams<{ id: string }>()
  const navigate = useNavigate()
  const [student, setStudent] = useState<Student | null>(null)
  const [loading, setLoading] = useState(true)
  const [suspendModal, setSuspendModal] = useState(false)
  const [transferModal, setTransferModal] = useState(false)
  const [suspendForm, setSuspendForm] = useState({ start_date: '', end_date: '', reason: '' })
  const [transferForm, setTransferForm] = useState({ transfer_type: 'out', transfer_date: '', to_school: '', reason: '' })

  useEffect(() => {
    if (!id) return
    getStudent(id).then(({ data }) => setStudent(data)).catch(() => toast.error('Failed to load')).finally(() => setLoading(false))
  }, [id])

  const handlePhoto = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0]
    if (!file || !id) return
    try {
      const { data } = await uploadPhoto(id, file)
      setStudent((p) => p ? { ...p, photo_url: data.photo_url } : p)
      toast.success('Photo updated')
    } catch { toast.error('Failed') }
  }

  const handleSuspend = async () => {
    if (!id) return
    try { await suspendStudent(id, suspendForm); toast.success('Suspension recorded'); setSuspendModal(false); setStudent((p) => p ? { ...p, status: 'suspended' } : p) }
    catch { toast.error('Failed') }
  }

  const handleTransfer = async () => {
    if (!id) return
    try { await transferStudent(id, transferForm); toast.success('Transfer recorded'); setTransferModal(false) }
    catch { toast.error('Failed') }
  }

  if (loading) return <div className="empty-state">Loading...</div>
  if (!student) return <div className="empty-state">Student not found</div>

  return (
    <div style={{ maxWidth: 960 }}>
      <div style={{ display: 'flex', alignItems: 'center', gap: 14, marginBottom: 22 }}>
        <button className="btn btn-secondary" onClick={() => navigate('/students')} style={{ padding: '8px 14px' }}><ArrowLeft size={14} /> Back</button>
        <h1 style={{ fontSize: '20px', fontWeight: 800, color: '#1e293b' }}>Student Profile</h1>
      </div>

      <div style={{ display: 'grid', gridTemplateColumns: '270px 1fr', gap: 18 }}>
        {/* Left */}
        <div className="card" style={{ padding: 24, textAlign: 'center' }}>
          <div style={{ position: 'relative', display: 'inline-block', marginBottom: 14 }}>
            {student.photo_url ? (
              <img src={student.photo_url} alt="" style={{ width: 96, height: 96, borderRadius: 18, objectFit: 'cover' }}
                onError={(e) => { (e.target as HTMLImageElement).src = '/images/placeholder-student.svg' }} />
            ) : (
              <div style={{ width: 96, height: 96, borderRadius: 18, background: 'linear-gradient(135deg,#1e40af,#3b82f6)', display: 'flex', alignItems: 'center', justifyContent: 'center', color: 'white', fontSize: 30, fontWeight: 800 }}>
                {getInitials(student.full_name)}
              </div>
            )}
            <label style={{ position: 'absolute', bottom: -8, right: -8, width: 26, height: 26, background: '#1e40af', borderRadius: 8, display: 'flex', alignItems: 'center', justifyContent: 'center', cursor: 'pointer' }}>
              <Camera size={12} color="white" />
              <input type="file" accept="image/*" onChange={handlePhoto} style={{ display: 'none' }} />
            </label>
          </div>
          <h2 style={{ fontSize: '16px', fontWeight: 700, color: '#1e293b' }}>{student.full_name}</h2>
          <p className="chip" style={{ marginTop: 4, display: 'inline-block' }}>{student.student_id}</p>
          <div style={{ marginTop: 10 }}>
            <span className={`badge ${getStatusBadge(student.status)}`}>{student.status}</span>
          </div>
          <div style={{ marginTop: 22, display: 'flex', flexDirection: 'column', gap: 8 }}>
            <button className="btn btn-primary" onClick={() => navigate(`/students/${id}/edit`)} style={{ justifyContent: 'center' }}><Edit size={13} /> Edit</button>
            <button className="btn btn-secondary" onClick={() => setSuspendModal(true)} style={{ justifyContent: 'center' }}><UserX size={13} /> Suspend</button>
            <button className="btn btn-secondary" onClick={() => setTransferModal(true)} style={{ justifyContent: 'center' }}><ArrowRightLeft size={13} /> Transfer</button>
          </div>
        </div>

        {/* Right */}
        <div style={{ display: 'flex', flexDirection: 'column', gap: 16 }}>
          <div className="card" style={{ padding: 22 }}>
            <h3 style={{ fontSize: '12px', fontWeight: 700, color: '#64748b', textTransform: 'uppercase', letterSpacing: '0.06em', marginBottom: 14 }}>Personal Information</h3>
            <InfoGrid items={[
              { label: 'Date of Birth', value: formatDate(student.date_of_birth) },
              { label: 'Gender', value: student.gender },
              { label: 'Nationality', value: student.nationality ?? '' },
              { label: 'Blood Group', value: student.blood_group ?? '' },
              { label: 'Admission Date', value: formatDate(student.admission_date) },
              { label: 'Academic Year', value: student.academic_year ?? '' },
            ]} />
          </div>
          <div className="card" style={{ padding: 22 }}>
            <h3 style={{ fontSize: '12px', fontWeight: 700, color: '#64748b', textTransform: 'uppercase', letterSpacing: '0.06em', marginBottom: 14 }}>Guardian</h3>
            <InfoGrid items={[
              { label: 'Name', value: student.guardian_name },
              { label: 'Relationship', value: student.guardian_relationship ?? '' },
              { label: 'Phone', value: student.guardian_phone },
              { label: 'Alt Phone', value: student.guardian_alt_phone ?? '' },
              { label: 'Email', value: student.guardian_email ?? '' },
              { label: 'Occupation', value: student.guardian_occupation ?? '' },
            ]} />
          </div>
        </div>
      </div>

      {/* Suspend Modal */}
      <Modal isOpen={suspendModal} onClose={() => setSuspendModal(false)} title="Suspend Student">
        <div style={{ display: 'flex', flexDirection: 'column', gap: 14 }}>
          <div className="form-grid">
            <div><label className="label">Start Date</label><input className="input" type="date" value={suspendForm.start_date} onChange={(e) => setSuspendForm((p) => ({ ...p, start_date: e.target.value }))} /></div>
            <div><label className="label">End Date</label><input className="input" type="date" value={suspendForm.end_date} onChange={(e) => setSuspendForm((p) => ({ ...p, end_date: e.target.value }))} /></div>
          </div>
          <div><label className="label">Reason *</label><textarea className="input" rows={4} value={suspendForm.reason} onChange={(e) => setSuspendForm((p) => ({ ...p, reason: e.target.value }))} /></div>
          <div style={{ display: 'flex', gap: 10, justifyContent: 'flex-end' }}>
            <button className="btn btn-secondary" onClick={() => setSuspendModal(false)}>Cancel</button>
            <button className="btn btn-danger" onClick={handleSuspend}>Confirm Suspension</button>
          </div>
        </div>
      </Modal>

      {/* Transfer Modal */}
      <Modal isOpen={transferModal} onClose={() => setTransferModal(false)} title="Transfer Student">
        <div style={{ display: 'flex', flexDirection: 'column', gap: 14 }}>
          <div><label className="label">Transfer Type</label>
            <select className="input" value={transferForm.transfer_type} onChange={(e) => setTransferForm((p) => ({ ...p, transfer_type: e.target.value }))}>
              <option value="out">Transfer Out</option><option value="in">Transfer In</option>
            </select></div>
          <div><label className="label">Transfer Date</label><input className="input" type="date" value={transferForm.transfer_date} onChange={(e) => setTransferForm((p) => ({ ...p, transfer_date: e.target.value }))} /></div>
          <div><label className="label">School Name</label><input className="input" value={transferForm.to_school} onChange={(e) => setTransferForm((p) => ({ ...p, to_school: e.target.value }))} /></div>
          <div><label className="label">Reason</label><textarea className="input" rows={3} value={transferForm.reason} onChange={(e) => setTransferForm((p) => ({ ...p, reason: e.target.value }))} /></div>
          <div style={{ display: 'flex', gap: 10, justifyContent: 'flex-end' }}>
            <button className="btn btn-secondary" onClick={() => setTransferModal(false)}>Cancel</button>
            <button className="btn btn-primary" onClick={handleTransfer}>Confirm Transfer</button>
          </div>
        </div>
      </Modal>
    </div>
  )
}
