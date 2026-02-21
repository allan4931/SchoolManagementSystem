import type { LucideIcon } from 'lucide-react'

interface EmptyStateProps {
  icon: LucideIcon
  title: string
  subtitle?: string
  action?: React.ReactNode
}

export default function EmptyState({ icon: Icon, title, subtitle, action }: EmptyStateProps) {
  return (
    <div className="empty-state">
      <Icon size={44} strokeWidth={1.2} />
      <p style={{ fontWeight: 700, fontSize: '15px', marginBottom: '4px' }}>{title}</p>
      {subtitle && <p style={{ fontSize: '13px' }}>{subtitle}</p>}
      {action && <div style={{ marginTop: '16px' }}>{action}</div>}
    </div>
  )
}
