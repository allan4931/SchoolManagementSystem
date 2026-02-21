import { getInitials, getAvatarUrl } from '../../utils/helpers'

interface AvatarProps {
  name?: string | null
  photoUrl?: string | null
  size?: number
  radius?: number
  type?: 'student' | 'teacher'
  gradient?: string
}

export default function Avatar({ name, photoUrl, size = 36, radius = 8, type = 'student', gradient }: AvatarProps) {
  const defaultGrad = type === 'teacher'
    ? 'linear-gradient(135deg,#059669,#10b981)'
    : 'linear-gradient(135deg,#1e40af,#3b82f6)'

  if (photoUrl) {
    return (
      <img
        src={photoUrl}
        alt={name ?? ''}
        style={{ width: size, height: size, borderRadius: radius, objectFit: 'cover', flexShrink: 0 }}
        onError={(e) => { (e.target as HTMLImageElement).src = getAvatarUrl(null, type) }}
      />
    )
  }
  return (
    <div style={{
      width: size, height: size, borderRadius: radius, flexShrink: 0,
      background: gradient ?? defaultGrad,
      display: 'flex', alignItems: 'center', justifyContent: 'center',
      color: 'white', fontWeight: 700,
      fontSize: size * 0.33,
    }}>
      {getInitials(name)}
    </div>
  )
}
