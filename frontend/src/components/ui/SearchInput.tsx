import { Search } from 'lucide-react'

interface SearchInputProps {
  value: string
  onChange: (v: string) => void
  placeholder?: string
  style?: React.CSSProperties
}

export default function SearchInput({ value, onChange, placeholder = 'Search...', style }: SearchInputProps) {
  return (
    <div style={{ position: 'relative', ...style }}>
      <Search size={14} color="#94a3b8" style={{ position: 'absolute', left: '11px', top: '50%', transform: 'translateY(-50%)' }} />
      <input
        className="input"
        style={{ paddingLeft: '34px' }}
        placeholder={placeholder}
        value={value}
        onChange={(e) => onChange(e.target.value)}
      />
    </div>
  )
}
