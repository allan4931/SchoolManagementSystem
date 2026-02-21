import type { ReactNode } from 'react'

interface PageHeaderProps {
  title: string
  subtitle?: string
  actions?: ReactNode
}

export default function PageHeader({ title, subtitle, actions }: PageHeaderProps) {
  return (
    <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '22px', flexWrap: 'wrap', gap: '12px' }}>
      <div>
        <h1 style={{ fontSize: '21px', fontWeight: 800, color: '#1e293b' }}>{title}</h1>
        {subtitle && <p style={{ color: '#64748b', fontSize: '13px', marginTop: '2px' }}>{subtitle}</p>}
      </div>
      {actions && <div style={{ display: 'flex', gap: '10px', flexWrap: 'wrap' }}>{actions}</div>}
    </div>
  )
}
