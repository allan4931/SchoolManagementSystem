import { useState, useEffect } from 'react'
import { Cloud, CloudOff, RefreshCw } from 'lucide-react'
import api from '../../api/axios'

export default function SyncBadge() {
  const [synced, setSynced] = useState<boolean | null>(null)
  const [syncing, setSyncing] = useState(false)

  const check = async () => {
    try { const { data } = await api.get('/sync/status'); setSynced(!!data.last_success) }
    catch { setSynced(false) }
  }

  const sync = async () => {
    setSyncing(true)
    try { await api.post('/sync/trigger'); await check() } catch {}
    setSyncing(false)
  }

  useEffect(() => { check(); const t = setInterval(check, 30000); return () => clearInterval(t) }, [])

  return (
    <button onClick={sync} title="Click to sync" style={{
      display: 'flex', alignItems: 'center', gap: '6px',
      padding: '5px 11px', borderRadius: '20px', border: 'none', cursor: 'pointer',
      background: synced ? '#dcfce7' : '#fee2e2',
      transition: 'all 0.2s',
    }}>
      {syncing ? <RefreshCw size={12} color="#64748b" style={{ animation: 'spin 1s linear infinite' }} />
        : synced ? <Cloud size={12} color="#16a34a" /> : <CloudOff size={12} color="#dc2626" />}
      <span style={{ fontSize: '11.5px', fontWeight: 600, color: synced ? '#16a34a' : '#dc2626' }}>
        {syncing ? 'Syncing...' : synced ? 'Synced' : 'Offline'}
      </span>
    </button>
  )
}
