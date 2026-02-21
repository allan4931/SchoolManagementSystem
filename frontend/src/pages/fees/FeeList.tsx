import { useState, useEffect } from 'react'
import { Plus, DollarSign } from 'lucide-react'
import { getArrears, getFeeStructures, generateInvoice, makePayment } from '../../api/feeApi'
import { getStudents } from '../../api/studentApi'
import { formatCurrency, formatDate, getStatusBadge, downloadBlob } from '../../utils/helpers'
import PageHeader from '../../components/ui/PageHeader'
import Modal from '../../components/ui/Modal'
import type { FeeInvoice, FeeStructure, Student } from '../../types'
import toast from 'react-hot-toast'
import { downloadReceipt } from '../../api/feeApi'
import { Download } from 'lucide-react'

type InvoiceItem = { description: string; amount: string; quantity: number }

export default function FeeList() {
  const [arrears, setArrears] = useState<FeeInvoice[]>([])
  const [structures, setStructures] = useState<FeeStructure[]>([])
  const [students, setStudents] = useState<Student[]>([])
  const [loading, setLoading] = useState(true)
  const [tab, setTab] = useState<'arrears' | 'structures'>('arrears')
  const [invModal, setInvModal] = useState(false)
  const [payModal, setPayModal] = useState(false)
  const [invForm, setInvForm] = useState({ student_id: '', term: 'Term 1', academic_year: '2024', due_date: '', discount: '0', items: [{ description: 'Tuition Fee', amount: '', quantity: 1 }] as InvoiceItem[] })
  const [payForm, setPayForm] = useState({ invoice_id: '', amount: '', payment_date: new Date().toISOString().split('T')[0], payment_method: 'cash', reference_number: '' })

  const load = async () => {
    setLoading(true)
    try {
      const [a, s, fs] = await Promise.all([getArrears(), getStudents({ limit: 300 }), getFeeStructures()])
      setArrears(a.data as FeeInvoice[])
      setStudents(((s.data as any).items ?? s.data) as Student[])
      setStructures(fs.data as FeeStructure[])
    } catch {}
    setLoading(false)
  }

  useEffect(() => { load() }, [])

  const handleInvoice = async () => {
    try {
      await generateInvoice({ ...invForm, discount: parseFloat(invForm.discount) || 0, items: invForm.items.map((i) => ({ ...i, amount: parseFloat(i.amount) })) })
      toast.success('Invoice generated'); setInvModal(false); load()
    } catch (err: any) { toast.error(err.response?.data?.detail || 'Failed') }
  }

  const handlePayment = async () => {
    try {
      const { data } = await makePayment({ ...payForm, amount: parseFloat(payForm.amount) }) as any
      toast.success(`Payment recorded — ${data.receipt_number}`); setPayModal(false); load()
    } catch (err: any) { toast.error(err.response?.data?.detail || 'Failed') }
  }

  const handleReceipt = async (paymentId: string) => {
    try { const { data } = await downloadReceipt(paymentId); downloadBlob(data as Blob, `receipt_${paymentId}.pdf`) }
    catch { toast.error('Failed to download') }
  }

  const totalArrears = arrears.reduce((s, i) => s + (i.balance ?? 0), 0)
  const si = (f: string) => (e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement>) => setInvForm((p) => ({ ...p, [f]: e.target.value }))
  const sp = (f: string) => (e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement>) => setPayForm((p) => ({ ...p, [f]: e.target.value }))

  return (
    <div>
      <PageHeader title="Fees & Payments" subtitle={`Total arrears: ${formatCurrency(totalArrears)}`}
        actions={<>
          <button className="btn btn-secondary" onClick={() => setInvModal(true)}><Plus size={14} /> Invoice</button>
          <button className="btn btn-primary" onClick={() => setPayModal(true)}><DollarSign size={14} /> Record Payment</button>
        </>} />

      <div className="tabs" style={{ marginBottom: 18, width: 'fit-content' }}>
        <button className={`tab-btn${tab === 'arrears' ? ' active' : ''}`} onClick={() => setTab('arrears')}>Fee Arrears ({arrears.length})</button>
        <button className={`tab-btn${tab === 'structures' ? ' active' : ''}`} onClick={() => setTab('structures')}>Fee Structures</button>
      </div>

      <div className="card">
        <div className="table-wrap">
          {tab === 'arrears' ? (
            <table>
              <thead><tr><th>Invoice #</th><th>Term</th><th>Year</th><th>Total</th><th>Paid</th><th>Balance</th><th>Due</th><th>Status</th></tr></thead>
              <tbody>
                {loading ? <tr><td colSpan={8} style={{ textAlign: 'center', padding: '40px', color: '#94a3b8' }}>Loading...</td></tr>
                  : arrears.length === 0 ? <tr><td colSpan={8} style={{ textAlign: 'center', padding: '40px', color: '#94a3b8' }}>No arrears — all fees cleared!</td></tr>
                  : arrears.map((inv) => (
                    <tr key={inv.id}>
                      <td><span className="chip">{inv.invoice_number}</span></td>
                      <td>{inv.term}</td>
                      <td>{inv.academic_year}</td>
                      <td>{formatCurrency(inv.total_amount)}</td>
                      <td style={{ color: '#10b981', fontWeight: 600 }}>{formatCurrency(inv.paid_amount)}</td>
                      <td style={{ color: '#dc2626', fontWeight: 700 }}>{formatCurrency(inv.balance)}</td>
                      <td>{formatDate(inv.due_date)}</td>
                      <td><span className={`badge ${getStatusBadge(inv.status)}`}>{inv.status}</span></td>
                    </tr>
                  ))}
              </tbody>
            </table>
          ) : (
            <table>
              <thead><tr><th>Name</th><th>Type</th><th>Amount</th><th>Term</th><th>Year</th><th>Compulsory</th></tr></thead>
              <tbody>
                {structures.map((s) => (
                  <tr key={s.id}>
                    <td style={{ fontWeight: 600 }}>{s.name}</td>
                    <td><span className="badge badge-blue">{s.fee_type}</span></td>
                    <td style={{ fontWeight: 700 }}>{formatCurrency(s.amount)}</td>
                    <td>{s.term}</td>
                    <td>{s.academic_year}</td>
                    <td><span className={`badge ${s.is_compulsory ? 'badge-green' : 'badge-gray'}`}>{s.is_compulsory ? 'Yes' : 'No'}</span></td>
                  </tr>
                ))}
              </tbody>
            </table>
          )}
        </div>
      </div>

      {/* Invoice Modal */}
      <Modal isOpen={invModal} onClose={() => setInvModal(false)} title="Generate Invoice" size="lg">
        <div className="form-grid">
          <div className="span-2"><label className="label">Student *</label>
            <select className="input" value={invForm.student_id} onChange={si('student_id')}>
              <option value="">Select student...</option>
              {students.map((s) => <option key={s.id} value={s.id}>{s.full_name} ({s.student_id})</option>)}
            </select></div>
          <div><label className="label">Term</label>
            <select className="input" value={invForm.term} onChange={si('term')}>
              <option>Term 1</option><option>Term 2</option><option>Term 3</option>
            </select></div>
          <div><label className="label">Academic Year</label>
            <select className="input" value={invForm.academic_year} onChange={si('academic_year')}>
              {['2023','2024','2025'].map((y) => <option key={y}>{y}</option>)}
            </select></div>
          <div><label className="label">Due Date</label><input className="input" type="date" value={invForm.due_date} onChange={si('due_date')} /></div>
          <div><label className="label">Discount ($)</label><input className="input" type="number" value={invForm.discount} onChange={si('discount')} /></div>
          <div className="span-2">
            <label className="label">Invoice Items</label>
            {invForm.items.map((item, i) => (
              <div key={i} style={{ display: 'grid', gridTemplateColumns: '1fr 130px', gap: 8, marginBottom: 8 }}>
                <input className="input" placeholder="Description" value={item.description}
                  onChange={(e) => { const it = [...invForm.items]; it[i].description = e.target.value; setInvForm((p) => ({ ...p, items: it })) }} />
                <input className="input" type="number" placeholder="Amount" value={item.amount}
                  onChange={(e) => { const it = [...invForm.items]; it[i].amount = e.target.value; setInvForm((p) => ({ ...p, items: it })) }} />
              </div>
            ))}
            <button className="btn btn-secondary" onClick={() => setInvForm((p) => ({ ...p, items: [...p.items, { description: '', amount: '', quantity: 1 }] }))} style={{ fontSize: 12, padding: '6px 12px' }}>+ Add Item</button>
          </div>
        </div>
        <div style={{ display: 'flex', gap: 10, justifyContent: 'flex-end', marginTop: 20 }}>
          <button className="btn btn-secondary" onClick={() => setInvModal(false)}>Cancel</button>
          <button className="btn btn-primary" onClick={handleInvoice}>Generate Invoice</button>
        </div>
      </Modal>

      {/* Payment Modal */}
      <Modal isOpen={payModal} onClose={() => setPayModal(false)} title="Record Payment">
        <div style={{ display: 'flex', flexDirection: 'column', gap: 14 }}>
          <div><label className="label">Invoice ID *</label><input className="input" placeholder="Paste invoice UUID..." value={payForm.invoice_id} onChange={sp('invoice_id')} /></div>
          <div><label className="label">Amount ($) *</label><input className="input" type="number" value={payForm.amount} onChange={sp('amount')} /></div>
          <div><label className="label">Payment Date</label><input className="input" type="date" value={payForm.payment_date} onChange={sp('payment_date')} /></div>
          <div><label className="label">Payment Method</label>
            <select className="input" value={payForm.payment_method} onChange={sp('payment_method')}>
              <option value="cash">Cash</option><option value="bank_transfer">Bank Transfer</option>
              <option value="mobile_money">Mobile Money</option><option value="cheque">Cheque</option>
            </select></div>
          <div><label className="label">Reference Number</label><input className="input" value={payForm.reference_number} onChange={sp('reference_number')} /></div>
          <div style={{ display: 'flex', gap: 10, justifyContent: 'flex-end' }}>
            <button className="btn btn-secondary" onClick={() => setPayModal(false)}>Cancel</button>
            <button className="btn btn-primary" onClick={handlePayment}>Record Payment</button>
          </div>
        </div>
      </Modal>
    </div>
  )
}
