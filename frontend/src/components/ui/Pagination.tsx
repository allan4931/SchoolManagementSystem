interface PaginationProps {
  page: number
  total: number
  limit: number
  onPrev: () => void
  onNext: () => void
}

export default function Pagination({ page, total, limit, onPrev, onNext }: PaginationProps) {
  const start = page * limit + 1
  const end = Math.min((page + 1) * limit, total)
  return (
    <div style={{ padding: '14px 18px', borderTop: '1px solid #f1f5f9', display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
      <span style={{ fontSize: '13px', color: '#64748b' }}>
        Showing {start}–{end} of {total}
      </span>
      <div style={{ display: 'flex', gap: '8px' }}>
        <button className="btn btn-secondary" disabled={page === 0} onClick={onPrev} style={{ padding: '6px 14px' }}>Previous</button>
        <button className="btn btn-secondary" disabled={end >= total} onClick={onNext} style={{ padding: '6px 14px' }}>Next</button>
      </div>
    </div>
  )
}
