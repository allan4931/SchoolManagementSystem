import { useState, useEffect } from 'react'
import { Plus, ClipboardList, Send } from 'lucide-react'
import { getExams, createExam, publishResults } from '../../api/examApi'
import { formatDate } from '../../utils/helpers'
import PageHeader from '../../components/ui/PageHeader'
import Modal from '../../components/ui/Modal'
import EmptyState from '../../components/ui/EmptyState'
import type { Exam } from '../../types'
import toast from 'react-hot-toast'

const TYPE_COLORS: Record<string, string> = {
  end_term: 'badge-blue', mid_term: 'badge-yellow', mock: 'badge-purple',
  continuous_assessment: 'badge-green',
}

const BG = ['linear-gradient(135deg,#7c3aed,#8b5cf6)','linear-gradient(135deg,#1e40af,#3b82f6)','linear-gradient(135deg,#b45309,#f59e0b)','linear-gradient(135deg,#be123c,#f43f5e)']

export default function ExamList() {
  const [exams, setExams] = useState<Exam[]>([])
  const [modal, setModal] = useState(false)
  const [form, setForm] = useState({ name: '', exam_type: 'end_term', academic_year: '2024', term: 'Term 1', start_date: '', end_date: '' })

  const load = async () => { const { data } = await getExams(); setExams(Array.isArray(data) ? data : []) }
  useEffect(() => { load() }, [])

  const handleCreate = async () => {
    if (!form.name) return toast.error('Name required')
    try { await createExam(form as any); toast.success('Exam created'); setModal(false); load() }
    catch (err: any) { toast.error(err.response?.data?.detail || 'Failed') }
  }

  const handlePublish = async (id: string) => {
    if (!confirm('Publish results?')) return
    try { await publishResults(id); toast.success('Published'); load() }
    catch { toast.error('Failed') }
  }

  const set = (f: string) => (e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement>) => setForm((p) => ({ ...p, [f]: e.target.value }))

  return (
    <div>
      <PageHeader title="Exams & Results" subtitle={`${exams.length} exams`} actions={<button className="btn btn-primary" onClick={() => setModal(true)}><Plus size={14} /> Create Exam</button>} />

      {exams.length === 0 ? <EmptyState icon={ClipboardList} title="No exams yet" /> : (
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(290px, 1fr))', gap: 14 }}>
          {exams.map((exam, i) => (
            <div key={exam.id} className="card" style={{ padding: 20 }}>
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: 14 }}>
                <div style={{ width: 42, height: 42, background: BG[i % BG.length], borderRadius: 12, display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
                  <ClipboardList size={19} color="white" />
                </div>
                <span className={`badge ${TYPE_COLORS[exam.exam_type] ?? 'badge-gray'}`}>{exam.exam_type.replace(/_/g, ' ')}</span>
              </div>
              <h3 style={{ fontSize: 15, fontWeight: 700, color: '#1e293b', marginBottom: 4 }}>{exam.name}</h3>
              <p style={{ fontSize: 12, color: '#94a3b8', marginBottom: 12 }}>{exam.term} • {exam.academic_year}</p>
              {exam.start_date && <p style={{ fontSize: 12, color: '#64748b' }}>{formatDate(exam.start_date)} — {formatDate(exam.end_date)}</p>}
              <div style={{ marginTop: 14, display: 'flex', gap: 8, alignItems: 'center' }}>
                <span className={`badge ${exam.is_published ? 'badge-green' : 'badge-gray'}`}>{exam.is_published ? 'Published' : 'Draft'}</span>
                {!exam.is_published && (
                  <button onClick={() => handlePublish(exam.id)} style={{ display: 'flex', alignItems: 'center', gap: 4, padding: '3px 10px', background: '#dbeafe', color: '#1d4ed8', border: 'none', borderRadius: 20, fontSize: 11.5, fontWeight: 600, cursor: 'pointer', fontFamily: 'inherit' }}>
                    <Send size={10} /> Publish
                  </button>
                )}
              </div>
            </div>
          ))}
        </div>
      )}

      <Modal isOpen={modal} onClose={() => setModal(false)} title="Create Exam">
        <div className="form-grid">
          <div className="span-2"><label className="label">Exam Name *</label><input className="input" value={form.name} onChange={set('name')} placeholder="e.g. End of Term 1 2024" /></div>
          <div><label className="label">Type</label>
            <select className="input" value={form.exam_type} onChange={set('exam_type')}>
              <option value="end_term">End of Term</option><option value="mid_term">Mid Term</option>
              <option value="mock">Mock</option><option value="continuous_assessment">Continuous Assessment</option>
            </select></div>
          <div><label className="label">Term</label>
            <select className="input" value={form.term} onChange={set('term')}>
              <option>Term 1</option><option>Term 2</option><option>Term 3</option>
            </select></div>
          <div><label className="label">Academic Year</label>
            <select className="input" value={form.academic_year} onChange={set('academic_year')}>
              {['2023','2024','2025'].map((y) => <option key={y}>{y}</option>)}
            </select></div>
          <div />
          <div><label className="label">Start Date</label><input className="input" type="date" value={form.start_date} onChange={set('start_date')} /></div>
          <div><label className="label">End Date</label><input className="input" type="date" value={form.end_date} onChange={set('end_date')} /></div>
        </div>
        <div style={{ display: 'flex', gap: 10, justifyContent: 'flex-end', marginTop: 20 }}>
          <button className="btn btn-secondary" onClick={() => setModal(false)}>Cancel</button>
          <button className="btn btn-primary" onClick={handleCreate}>Create Exam</button>
        </div>
      </Modal>
    </div>
  )
}
