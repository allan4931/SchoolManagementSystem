import { getStatusBadge } from '../../utils/helpers'

interface BadgeProps {
  status: string
  label?: string
}

export default function Badge({ status, label }: BadgeProps) {
  return (
    <span className={`badge ${getStatusBadge(status)}`}>
      {label ?? status}
    </span>
  )
}
