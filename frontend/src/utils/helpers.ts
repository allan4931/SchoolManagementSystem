export const formatDate = (date?: string | null): string => {
  if (!date) return '—'
  return new Date(date).toLocaleDateString('en-GB', {
    day: '2-digit', month: 'short', year: 'numeric',
  })
}

export const formatCurrency = (amount?: number | null): string => {
  if (amount == null) return '—'
  return new Intl.NumberFormat('en-US', {
    style: 'currency', currency: 'USD', minimumFractionDigits: 2,
  }).format(amount)
}

export const getInitials = (name?: string | null): string => {
  if (!name) return '?'
  return name.split(' ').map((n) => n[0]).slice(0, 2).join('').toUpperCase()
}

export const getStatusBadge = (status?: string): string => {
  const map: Record<string, string> = {
    active: 'badge-green',
    inactive: 'badge-gray',
    paid: 'badge-green',
    partial: 'badge-yellow',
    unpaid: 'badge-red',
    overdue: 'badge-red',
    cancelled: 'badge-gray',
    present: 'badge-green',
    absent: 'badge-red',
    late: 'badge-yellow',
    excused: 'badge-blue',
    half_day: 'badge-orange',
    transferred: 'badge-purple',
    suspended: 'badge-red',
    graduated: 'badge-blue',
    on_leave: 'badge-yellow',
    resigned: 'badge-gray',
    terminated: 'badge-red',
    maintenance: 'badge-yellow',
    retired: 'badge-gray',
    excellent: 'badge-green',
    good: 'badge-blue',
    fair: 'badge-yellow',
    poor: 'badge-red',
    damaged: 'badge-red',
  }
  return map[status?.toLowerCase() ?? ''] ?? 'badge-gray'
}

export const downloadBlob = (blob: Blob, filename: string): void => {
  const url = window.URL.createObjectURL(blob)
  const a = document.createElement('a')
  a.href = url
  a.download = filename
  a.click()
  window.URL.revokeObjectURL(url)
}

export const truncate = (str: string, n: number): string =>
  str.length > n ? str.slice(0, n) + '...' : str

export const getAvatarUrl = (photoUrl?: string | null, type: 'student' | 'teacher' = 'student'): string => {
  if (photoUrl) return photoUrl
  return type === 'teacher' ? '/images/placeholder-teacher.svg' : '/images/placeholder-student.svg'
}
