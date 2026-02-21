import type { LucideIcon } from 'lucide-react'

interface StatCardProps {
  title: string
  value: string | number
  subtitle?: string
  icon: LucideIcon
  color?: string
  trend?: number
}

export default function StatCard({ title, value, subtitle, icon: Icon, color = '#3b82f6', trend }: StatCardProps) {
  return (
    <div className="stat-card">
      <div style={{ display: 'flex', alignItems: 'flex-start', justifyContent: 'space-between' }}>
        <div>
          <p style={{ fontSize: '12.5px', fontWeight: 600, color: '#64748b', marginBottom: '8px' }}>{title}</p>
          <p style={{ fontSize: '28px', fontWeight: 800, color: '#1e293b', lineHeight: 1 }}>{value}</p>
          {subtitle && <p style={{ fontSize: '12px', color: '#94a3b8', marginTop: '5px' }}>{subtitle}</p>}
          {trend != null && (
            <span style={{ fontSize: '12px', fontWeight: 600, color: trend > 0 ? '#10b981' : '#ef4444', marginTop: '6px', display: 'inline-block' }}>
              {trend > 0 ? '↑' : '↓'} {Math.abs(trend)}% vs last month
            </span>
          )}
        </div>
        <div style={{ width: '46px', height: '46px', background: `${color}18`, borderRadius: '13px', display: 'flex', alignItems: 'center', justifyContent: 'center', flexShrink: 0 }}>
          <Icon size={21} color={color} />
        </div>
      </div>
    </div>
  )
}
