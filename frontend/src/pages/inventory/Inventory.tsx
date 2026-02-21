import { useState, useEffect } from 'react'
import { Plus, Search, Wrench, Package } from 'lucide-react'
import { getInventory, addItem, updateItem, deleteItem, addMaintenance } from '../../api/inventoryApi'
import { formatDate, formatCurrency, getStatusBadge } from '../../utils/helpers'
import PageHeader from '../../components/ui/PageHeader'
import Modal from '../../components/ui/Modal'
import SearchInput from '../../components/ui/SearchInput'
import EmptyState from '../../components/ui/EmptyState'
import Pagination from '../../components/ui/Pagination'
import type { InventoryItem } from '../../types'
import toast from 'react-hot-toast'

const CATS = ['furniture','electronics','sports','laboratory','stationery','building','vehicle','other']
const CONDS = ['excellent','good','fair','poor','damaged']
const LIMIT = 20

export default function InventoryPage() {
  const [items, setItems] = useState<InventoryItem[]>([])
  const [total, setTotal] = useState(0)
  const [page, setPage] = useState(0)
  const [search, setSearch] = useState('')
  const [category, setCategory] = useState('')
  const [addModal, setAddModal] = useState(false)
  const [maintModal, setMaintModal] = useState(false)
  const [selectedItem, setSelectedItem] = useState<InventoryItem | null>(null)
  const [form, setForm] = useState({ name: '', asset_tag: '', category: 'other', quantity: '1', condition: 'good', location: '', purchase_price: '', purchase_date: '', serial_number: '', supplier: '', notes: '' })
  const [mForm, setMForm] = useState({ item_id: '', maintenance_date: new Date().toISOString().split('T')[0], description: '', cost: '', performed_by: '', condition_after: 'good' })

  const load = async () => {
    try {
      const { data } = await getInventory({ search: search || undefined, category: category || undefined, limit: LIMIT, skip: page * LIMIT })
      const d = data as any; setItems(d.items ?? d); setTotal(d.total ?? 0)
    } catch {}
  }

  useEffect(() => { load() }, [search, category, page])

  const handleAdd = async () => {
    if (!form.name) return toast.error('Name required')
    try {
      await addItem({ ...form, quantity: parseInt(form.quantity), purchase_price: form.purchase_price ? parseFloat(form.purchase_price) : undefined } as any)
      toast.success('Item added'); setAddModal(false); load()
    } catch { toast.error('Failed') }
  }

  const handleMaint = async () => {
    if (!mForm.description) return toast.error('Description required')
    try {
      await addMaintenance(mForm.item_id, { ...mForm, cost: mForm.cost ? parseFloat(mForm.cost) : null })
      toast.success('Maintenance recorded'); setMaintModal(false)
    } catch { toast.error('Failed') }
  }

  const openMaint = (item: InventoryItem) => { setSelectedItem(item); setMForm((p) => ({ ...p, item_id: item.id })); setMaintModal(true) }
  const sf = (f: string) => (e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement | HTMLTextAreaElement>) => setForm((p) => ({ ...p, [f]: e.target.value }))
  const sm = (f: string) => (e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement | HTMLTextAreaElement>) => setMForm((p) => ({ ...p, [f]: e.target.value }))

  const condBadge: Record<string, string> = { excellent: 'badge-green', good: 'badge-blue', fair: 'badge-yellow', poor: 'badge-red', damaged: 'badge-red' }

  return (
    <div>
      <PageHeader title="Inventory" subtitle={`${total} assets tracked`} actions={<button className="btn btn-primary" onClick={() => setAddModal(true)}><Plus size={14} /> Add Item</button>} />

      <div className="card" style={{ padding: '13px 18px', marginBottom: 13, display: 'flex', gap: 10, flexWrap: 'wrap' }}>
        <SearchInput value={search} onChange={(v) => { setSearch(v); setPage(0) }} placeholder="Search items..." style={{ flex: 1, minWidth: 200 }} />
        <select className="input" style={{ width: 180 }} value={category} onChange={(e) => { setCategory(e.target.value); setPage(0) }}>
          <option value="">All Categories</option>
          {CATS.map((c) => <option key={c} value={c}>{c.charAt(0).toUpperCase() + c.slice(1)}</option>)}
        </select>
      </div>

      <div className="card">
        <div className="table-wrap">
          <table>
            <thead><tr><th>Item</th><th>Asset Tag</th><th>Category</th><th>Qty</th><th>Condition</th><th>Location</th><th>Value</th><th>Actions</th></tr></thead>
            <tbody>
              {items.length === 0 ? <tr><td colSpan={8}><EmptyState icon={Package} title="No items found" /></td></tr>
                : items.map((item) => (
                  <tr key={item.id}>
                    <td style={{ fontWeight: 600 }}>{item.name}</td>
                    <td><span className="chip">{item.asset_tag ?? '—'}</span></td>
                    <td><span className="badge badge-blue">{item.category}</span></td>
                    <td style={{ fontWeight: 700 }}>{item.quantity}</td>
                    <td><span className={`badge ${condBadge[item.condition] ?? 'badge-gray'}`}>{item.condition}</span></td>
                    <td>{item.location ?? '—'}</td>
                    <td>{item.purchase_price ? formatCurrency(item.purchase_price) : '—'}</td>
                    <td>
                      <div style={{ display: 'flex', gap: 5 }}>
                        <button onClick={() => openMaint(item)} style={{ padding: 5, background: '#fef9c3', border: 'none', borderRadius: 6, cursor: 'pointer' }}><Wrench size={12} color="#92400e" /></button>
                        <button onClick={async () => { if (!confirm('Deactivate?')) return; try { await deleteItem(item.id); toast.success('Deactivated'); load() } catch { toast.error('Failed') } }} style={{ padding: 5, background: '#fee2e2', border: 'none', borderRadius: 6, cursor: 'pointer' }}><Package size={12} color="#dc2626" /></button>
                      </div>
                    </td>
                  </tr>
                ))}
            </tbody>
          </table>
        </div>
        {total > LIMIT && <Pagination page={page} total={total} limit={LIMIT} onPrev={() => setPage((p) => p - 1)} onNext={() => setPage((p) => p + 1)} />}
      </div>

      <Modal isOpen={addModal} onClose={() => setAddModal(false)} title="Add Inventory Item" size="lg">
        <div className="form-grid">
          <div className="span-2"><label className="label">Item Name *</label><input className="input" value={form.name} onChange={sf('name')} /></div>
          <div><label className="label">Asset Tag</label><input className="input" value={form.asset_tag} onChange={sf('asset_tag')} placeholder="e.g. IT-001" /></div>
          <div><label className="label">Serial Number</label><input className="input" value={form.serial_number} onChange={sf('serial_number')} /></div>
          <div><label className="label">Category</label>
            <select className="input" value={form.category} onChange={sf('category')}>
              {CATS.map((c) => <option key={c} value={c}>{c.charAt(0).toUpperCase() + c.slice(1)}</option>)}
            </select></div>
          <div><label className="label">Condition</label>
            <select className="input" value={form.condition} onChange={sf('condition')}>
              {CONDS.map((c) => <option key={c} value={c}>{c.charAt(0).toUpperCase() + c.slice(1)}</option>)}
            </select></div>
          <div><label className="label">Quantity</label><input className="input" type="number" value={form.quantity} onChange={sf('quantity')} /></div>
          <div><label className="label">Location</label><input className="input" value={form.location} onChange={sf('location')} placeholder="e.g. Lab 1" /></div>
          <div><label className="label">Purchase Price ($)</label><input className="input" type="number" value={form.purchase_price} onChange={sf('purchase_price')} /></div>
          <div><label className="label">Purchase Date</label><input className="input" type="date" value={form.purchase_date} onChange={sf('purchase_date')} /></div>
          <div><label className="label">Supplier</label><input className="input" value={form.supplier} onChange={sf('supplier')} /></div>
          <div className="span-2"><label className="label">Notes</label><textarea className="input" rows={3} value={form.notes} onChange={sf('notes')} /></div>
        </div>
        <div style={{ display: 'flex', gap: 10, justifyContent: 'flex-end', marginTop: 20 }}>
          <button className="btn btn-secondary" onClick={() => setAddModal(false)}>Cancel</button>
          <button className="btn btn-primary" onClick={handleAdd}>Add Item</button>
        </div>
      </Modal>

      <Modal isOpen={maintModal} onClose={() => setMaintModal(false)} title={`Maintenance — ${selectedItem?.name}`}>
        <div style={{ display: 'flex', flexDirection: 'column', gap: 14 }}>
          <div><label className="label">Date</label><input className="input" type="date" value={mForm.maintenance_date} onChange={sm('maintenance_date')} /></div>
          <div><label className="label">Description *</label><textarea className="input" rows={3} value={mForm.description} onChange={sm('description')} /></div>
          <div><label className="label">Performed By</label><input className="input" value={mForm.performed_by} onChange={sm('performed_by')} /></div>
          <div><label className="label">Cost ($)</label><input className="input" type="number" value={mForm.cost} onChange={sm('cost')} /></div>
          <div><label className="label">Condition After</label>
            <select className="input" value={mForm.condition_after} onChange={sm('condition_after')}>
              {CONDS.map((c) => <option key={c} value={c}>{c.charAt(0).toUpperCase() + c.slice(1)}</option>)}
            </select></div>
          <div style={{ display: 'flex', gap: 10, justifyContent: 'flex-end' }}>
            <button className="btn btn-secondary" onClick={() => setMaintModal(false)}>Cancel</button>
            <button className="btn btn-primary" onClick={handleMaint}>Save Record</button>
          </div>
        </div>
      </Modal>
    </div>
  )
}
