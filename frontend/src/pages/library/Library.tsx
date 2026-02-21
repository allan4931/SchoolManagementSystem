import { useState, useEffect } from 'react'
import { Plus, RotateCcw, BookOpen } from 'lucide-react'
import { getBooks, addBook, issueBook, returnBook, getFines } from '../../api/libraryApi'
import { formatDate, formatCurrency } from '../../utils/helpers'
import PageHeader from '../../components/ui/PageHeader'
import Modal from '../../components/ui/Modal'
import SearchInput from '../../components/ui/SearchInput'
import EmptyState from '../../components/ui/EmptyState'
import type { Book, LibraryIssue } from '../../types'
import toast from 'react-hot-toast'

export default function LibraryPage() {
  const [books, setBooks] = useState<Book[]>([])
  const [fines, setFines] = useState<LibraryIssue[]>([])
  const [tab, setTab] = useState<'books' | 'fines'>('books')
  const [search, setSearch] = useState('')
  const [addModal, setAddModal] = useState(false)
  const [issueModal, setIssueModal] = useState(false)
  const [returnModal, setReturnModal] = useState(false)
  const [bForm, setBForm] = useState({ title: '', isbn: '', author: '', publisher: '', category: '', shelf_location: '', total_copies: '1' })
  const [iForm, setIForm] = useState({ book_id: '', student_id: '', due_date: '', fine_per_day: '0.50' })
  const [rForm, setRForm] = useState({ issue_id: '', condition_on_return: 'Good' })

  const load = async () => {
    const [b, f] = await Promise.all([getBooks({ search: search || undefined, limit: 200 }), getFines()])
    const bd = b.data as any; setBooks(bd.items ?? bd)
    setFines(f.data as LibraryIssue[])
  }

  useEffect(() => { load() }, [search])

  const handleAdd = async () => {
    if (!bForm.title) return toast.error('Title required')
    try { await addBook({ ...bForm, total_copies: parseInt(bForm.total_copies) } as any); toast.success('Book added'); setAddModal(false); load() }
    catch { toast.error('Failed') }
  }

  const handleIssue = async () => {
    try { await issueBook({ ...iForm, fine_per_day: parseFloat(iForm.fine_per_day) }); toast.success('Book issued'); setIssueModal(false); load() }
    catch (err: any) { toast.error(err.response?.data?.detail || 'Failed') }
  }

  const handleReturn = async () => {
    try {
      const { data } = await returnBook(rForm) as any
      toast.success(`Returned. Fine: ${formatCurrency(data.fine_amount)}`); setReturnModal(false); load()
    } catch { toast.error('Failed') }
  }

  const sb = (f: string) => (e: React.ChangeEvent<HTMLInputElement>) => setBForm((p) => ({ ...p, [f]: e.target.value }))

  return (
    <div>
      <PageHeader title="Library" subtitle={`${books.length} books • ${fines.length} overdue`}
        actions={<>
          <button className="btn btn-secondary" onClick={() => setReturnModal(true)}><RotateCcw size={14} /> Return</button>
          <button className="btn btn-secondary" onClick={() => setIssueModal(true)}><BookOpen size={14} /> Issue</button>
          <button className="btn btn-primary" onClick={() => setAddModal(true)}><Plus size={14} /> Add Book</button>
        </>} />

      <div className="tabs" style={{ marginBottom: 18, width: 'fit-content' }}>
        <button className={`tab-btn${tab === 'books' ? ' active' : ''}`} onClick={() => setTab('books')}>Catalogue ({books.length})</button>
        <button className={`tab-btn${tab === 'fines' ? ' active' : ''}`} onClick={() => setTab('fines')}>Overdue & Fines ({fines.length})</button>
      </div>

      {tab === 'books' && (
        <>
          <div className="card" style={{ padding: '13px 18px', marginBottom: 12 }}>
            <SearchInput value={search} onChange={setSearch} placeholder="Search title, author, ISBN..." />
          </div>
          <div className="card">
            <div className="table-wrap">
              <table>
                <thead><tr><th>Title</th><th>Author</th><th>ISBN</th><th>Category</th><th>Shelf</th><th>Total</th><th>Available</th></tr></thead>
                <tbody>
                  {books.length === 0 ? <tr><td colSpan={7}><EmptyState icon={BookOpen} title="No books found" /></td></tr>
                    : books.map((b) => (
                      <tr key={b.id}>
                        <td style={{ fontWeight: 600 }}>{b.title}</td>
                        <td>{b.author ?? '—'}</td>
                        <td><span className="chip">{b.isbn ?? '—'}</span></td>
                        <td>{b.category ?? '—'}</td>
                        <td>{b.shelf_location ?? '—'}</td>
                        <td>{b.total_copies}</td>
                        <td><span className={`badge ${b.available_copies > 0 ? 'badge-green' : 'badge-red'}`}>{b.available_copies}</span></td>
                      </tr>
                    ))}
                </tbody>
              </table>
            </div>
          </div>
        </>
      )}

      {tab === 'fines' && (
        <div className="card">
          <div className="table-wrap">
            <table>
              <thead><tr><th>Issue ID</th><th>Due Date</th><th>Days Overdue</th><th>Fine</th></tr></thead>
              <tbody>
                {fines.length === 0 ? <tr><td colSpan={4} style={{ textAlign: 'center', padding: '40px', color: '#94a3b8' }}>No overdue books</td></tr>
                  : fines.map((f) => (
                    <tr key={f.id}>
                      <td><span className="chip">{f.id.slice(0, 8)}</span></td>
                      <td>{formatDate(f.due_date)}</td>
                      <td><span className="badge badge-red">{f.days_overdue} days</span></td>
                      <td style={{ fontWeight: 700, color: '#dc2626' }}>{formatCurrency(f.calculated_fine)}</td>
                    </tr>
                  ))}
              </tbody>
            </table>
          </div>
        </div>
      )}

      <Modal isOpen={addModal} onClose={() => setAddModal(false)} title="Add Book" size="lg">
        <div className="form-grid">
          <div className="span-2"><label className="label">Title *</label><input className="input" value={bForm.title} onChange={sb('title')} /></div>
          <div><label className="label">Author</label><input className="input" value={bForm.author} onChange={sb('author')} /></div>
          <div><label className="label">ISBN</label><input className="input" value={bForm.isbn} onChange={sb('isbn')} /></div>
          <div><label className="label">Publisher</label><input className="input" value={bForm.publisher} onChange={sb('publisher')} /></div>
          <div><label className="label">Category</label><input className="input" value={bForm.category} onChange={sb('category')} /></div>
          <div><label className="label">Shelf Location</label><input className="input" value={bForm.shelf_location} onChange={sb('shelf_location')} /></div>
          <div><label className="label">Total Copies</label><input className="input" type="number" value={bForm.total_copies} onChange={sb('total_copies')} /></div>
        </div>
        <div style={{ display: 'flex', gap: 10, justifyContent: 'flex-end', marginTop: 20 }}>
          <button className="btn btn-secondary" onClick={() => setAddModal(false)}>Cancel</button>
          <button className="btn btn-primary" onClick={handleAdd}>Add Book</button>
        </div>
      </Modal>

      <Modal isOpen={issueModal} onClose={() => setIssueModal(false)} title="Issue Book">
        <div style={{ display: 'flex', flexDirection: 'column', gap: 14 }}>
          <div><label className="label">Book ID *</label><input className="input" placeholder="Book UUID..." value={iForm.book_id} onChange={(e) => setIForm((p) => ({ ...p, book_id: e.target.value }))} /></div>
          <div><label className="label">Student ID</label><input className="input" placeholder="Student UUID..." value={iForm.student_id} onChange={(e) => setIForm((p) => ({ ...p, student_id: e.target.value }))} /></div>
          <div><label className="label">Due Date *</label><input className="input" type="date" value={iForm.due_date} onChange={(e) => setIForm((p) => ({ ...p, due_date: e.target.value }))} /></div>
          <div><label className="label">Fine Per Day ($)</label><input className="input" type="number" step="0.01" value={iForm.fine_per_day} onChange={(e) => setIForm((p) => ({ ...p, fine_per_day: e.target.value }))} /></div>
          <div style={{ display: 'flex', gap: 10, justifyContent: 'flex-end' }}>
            <button className="btn btn-secondary" onClick={() => setIssueModal(false)}>Cancel</button>
            <button className="btn btn-primary" onClick={handleIssue}>Issue Book</button>
          </div>
        </div>
      </Modal>

      <Modal isOpen={returnModal} onClose={() => setReturnModal(false)} title="Return Book">
        <div style={{ display: 'flex', flexDirection: 'column', gap: 14 }}>
          <div><label className="label">Issue ID *</label><input className="input" placeholder="Issue UUID..." value={rForm.issue_id} onChange={(e) => setRForm((p) => ({ ...p, issue_id: e.target.value }))} /></div>
          <div><label className="label">Condition on Return</label>
            <select className="input" value={rForm.condition_on_return} onChange={(e) => setRForm((p) => ({ ...p, condition_on_return: e.target.value }))}>
              {['Excellent','Good','Fair','Poor','Damaged'].map((c) => <option key={c}>{c}</option>)}
            </select></div>
          <div style={{ display: 'flex', gap: 10, justifyContent: 'flex-end' }}>
            <button className="btn btn-secondary" onClick={() => setReturnModal(false)}>Cancel</button>
            <button className="btn btn-primary" onClick={handleReturn}>Confirm Return</button>
          </div>
        </div>
      </Modal>
    </div>
  )
}
