import { useState, useEffect } from 'react'
import { Plus, MapPin, Bus as BusIcon } from 'lucide-react'
import { getBuses, addBus, getRoutes, createRoute } from '../../api/transportApi'
import PageHeader from '../../components/ui/PageHeader'
import Modal from '../../components/ui/Modal'
import EmptyState from '../../components/ui/EmptyState'
import type { Bus, TransportRoute } from '../../types'
import toast from 'react-hot-toast'

export default function TransportPage() {
  const [buses, setBuses] = useState<Bus[]>([])
  const [routes, setRoutes] = useState<TransportRoute[]>([])
  const [tab, setTab] = useState<'buses' | 'routes'>('buses')
  const [busModal, setBusModal] = useState(false)
  const [routeModal, setRouteModal] = useState(false)
  const [bForm, setBForm] = useState({ registration_number: '', bus_number: '', make: '', model: '', capacity: '30', driver_name: '', driver_phone: '' })
  const [rForm, setRForm] = useState({ name: '', bus_id: '', stops: '', morning_departure: '', afternoon_departure: '', monthly_fee: '0' })

  const load = async () => {
    const [b, r] = await Promise.all([getBuses(), getRoutes()])
    setBuses(b.data as Bus[]); setRoutes(r.data as TransportRoute[])
  }

  useEffect(() => { load() }, [])

  const handleAddBus = async () => {
    if (!bForm.registration_number || !bForm.bus_number) return toast.error('Registration & bus number required')
    try { await addBus({ ...bForm, capacity: parseInt(bForm.capacity) } as any); toast.success('Bus added'); setBusModal(false); load() }
    catch { toast.error('Failed') }
  }

  const handleAddRoute = async () => {
    if (!rForm.name || !rForm.bus_id) return toast.error('Name & bus required')
    try { await createRoute({ ...rForm, monthly_fee: parseFloat(rForm.monthly_fee) || 0 } as any); toast.success('Route created'); setRouteModal(false); load() }
    catch { toast.error('Failed') }
  }

  const sb = (f: string) => (e: React.ChangeEvent<HTMLInputElement>) => setBForm((p) => ({ ...p, [f]: e.target.value }))
  const sr = (f: string) => (e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement>) => setRForm((p) => ({ ...p, [f]: e.target.value }))

  const statusColors: Record<string, string> = { active: 'badge-green', maintenance: 'badge-yellow', retired: 'badge-gray' }

  return (
    <div>
      <PageHeader title="Transport" subtitle={`${buses.length} buses • ${routes.length} routes`}
        actions={<>
          <button className="btn btn-secondary" onClick={() => setRouteModal(true)}><MapPin size={14} /> Add Route</button>
          <button className="btn btn-primary" onClick={() => setBusModal(true)}><Plus size={14} /> Add Bus</button>
        </>} />

      <div className="tabs" style={{ marginBottom: 18, width: 'fit-content' }}>
        <button className={`tab-btn${tab === 'buses' ? ' active' : ''}`} onClick={() => setTab('buses')}>Buses ({buses.length})</button>
        <button className={`tab-btn${tab === 'routes' ? ' active' : ''}`} onClick={() => setTab('routes')}>Routes ({routes.length})</button>
      </div>

      {tab === 'buses' && (
        buses.length === 0 ? <EmptyState icon={BusIcon} title="No buses registered" /> : (
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(270px, 1fr))', gap: 14 }}>
            {buses.map((b) => (
              <div key={b.id} className="card" style={{ padding: 20 }}>
                <div style={{ display: 'flex', alignItems: 'center', gap: 12, marginBottom: 14 }}>
                  <div style={{ width: 46, height: 46, background: 'linear-gradient(135deg,#0369a1,#0ea5e9)', borderRadius: 12, display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
                    <BusIcon size={20} color="white" />
                  </div>
                  <div>
                    <h3 style={{ fontSize: 15, fontWeight: 700, color: '#1e293b' }}>{b.bus_number}</h3>
                    <span className="chip">{b.registration_number}</span>
                  </div>
                </div>
                <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 10 }}>
                  {[
                    ['Capacity', `${b.capacity} seats`],
                    ['Status', null],
                    ['Driver', b.driver_name ?? '—'],
                    ['Phone', b.driver_phone ?? '—'],
                  ].map(([label, value], i) => (
                    <div key={i}>
                      <p style={{ fontSize: 10.5, fontWeight: 700, color: '#94a3b8', textTransform: 'uppercase', letterSpacing: '0.06em' }}>{label}</p>
                      {label === 'Status' ? <span className={`badge ${statusColors[b.status] ?? 'badge-gray'}`}>{b.status}</span>
                        : <p style={{ fontSize: 13, fontWeight: 600, color: '#1e293b', marginTop: 2 }}>{value}</p>}
                    </div>
                  ))}
                </div>
              </div>
            ))}
          </div>
        )
      )}

      {tab === 'routes' && (
        <div className="card">
          <div className="table-wrap">
            <table>
              <thead><tr><th>Route</th><th>Bus</th><th>Morning</th><th>Afternoon</th><th>Fee/Month</th><th>Status</th></tr></thead>
              <tbody>
                {routes.length === 0 ? <tr><td colSpan={6} style={{ textAlign: 'center', padding: '40px', color: '#94a3b8' }}>No routes</td></tr>
                  : routes.map((r) => (
                    <tr key={r.id}>
                      <td style={{ fontWeight: 600 }}>{r.name}</td>
                      <td>{buses.find((b) => b.id === r.bus_id)?.bus_number ?? '—'}</td>
                      <td>{r.morning_departure ?? '—'}</td>
                      <td>{r.afternoon_departure ?? '—'}</td>
                      <td style={{ fontWeight: 700 }}>${r.monthly_fee}</td>
                      <td><span className={`badge ${r.is_active ? 'badge-green' : 'badge-gray'}`}>{r.is_active ? 'Active' : 'Inactive'}</span></td>
                    </tr>
                  ))}
              </tbody>
            </table>
          </div>
        </div>
      )}

      <Modal isOpen={busModal} onClose={() => setBusModal(false)} title="Add Bus">
        <div className="form-grid">
          <div><label className="label">Registration Number *</label><input className="input" value={bForm.registration_number} onChange={sb('registration_number')} /></div>
          <div><label className="label">Bus Number *</label><input className="input" value={bForm.bus_number} onChange={sb('bus_number')} placeholder="e.g. Bus 01" /></div>
          <div><label className="label">Make</label><input className="input" value={bForm.make} onChange={sb('make')} placeholder="e.g. Toyota" /></div>
          <div><label className="label">Model</label><input className="input" value={bForm.model} onChange={sb('model')} placeholder="e.g. Coaster" /></div>
          <div><label className="label">Capacity</label><input className="input" type="number" value={bForm.capacity} onChange={sb('capacity')} /></div>
          <div />
          <div><label className="label">Driver Name</label><input className="input" value={bForm.driver_name} onChange={sb('driver_name')} /></div>
          <div><label className="label">Driver Phone</label><input className="input" value={bForm.driver_phone} onChange={sb('driver_phone')} /></div>
        </div>
        <div style={{ display: 'flex', gap: 10, justifyContent: 'flex-end', marginTop: 20 }}>
          <button className="btn btn-secondary" onClick={() => setBusModal(false)}>Cancel</button>
          <button className="btn btn-primary" onClick={handleAddBus}>Add Bus</button>
        </div>
      </Modal>

      <Modal isOpen={routeModal} onClose={() => setRouteModal(false)} title="Create Route">
        <div className="form-grid">
          <div className="span-2"><label className="label">Route Name *</label><input className="input" value={rForm.name} onChange={(e) => setRForm((p) => ({ ...p, name: e.target.value }))} /></div>
          <div className="span-2"><label className="label">Bus *</label>
            <select className="input" value={rForm.bus_id} onChange={sr('bus_id')}>
              <option value="">Select bus...</option>
              {buses.map((b) => <option key={b.id} value={b.id}>{b.bus_number} ({b.registration_number})</option>)}
            </select></div>
          <div><label className="label">Morning Departure</label><input className="input" type="time" value={rForm.morning_departure} onChange={(e) => setRForm((p) => ({ ...p, morning_departure: e.target.value }))} /></div>
          <div><label className="label">Afternoon Departure</label><input className="input" type="time" value={rForm.afternoon_departure} onChange={(e) => setRForm((p) => ({ ...p, afternoon_departure: e.target.value }))} /></div>
          <div><label className="label">Monthly Fee ($)</label><input className="input" type="number" value={rForm.monthly_fee} onChange={(e) => setRForm((p) => ({ ...p, monthly_fee: e.target.value }))} /></div>
          <div />
          <div className="span-2"><label className="label">Stops</label><input className="input" value={rForm.stops} onChange={(e) => setRForm((p) => ({ ...p, stops: e.target.value }))} placeholder="Stop 1, Stop 2..." /></div>
        </div>
        <div style={{ display: 'flex', gap: 10, justifyContent: 'flex-end', marginTop: 20 }}>
          <button className="btn btn-secondary" onClick={() => setRouteModal(false)}>Cancel</button>
          <button className="btn btn-primary" onClick={handleAddRoute}>Create Route</button>
        </div>
      </Modal>
    </div>
  )
}
