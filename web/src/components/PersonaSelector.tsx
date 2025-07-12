export interface PersonaSelectorProps {
  personas: string[]
  selected: string
  onChange: (value: string) => void
}

export function PersonaSelector({ personas, selected, onChange }: PersonaSelectorProps) {
  return (
    <div className="persona-selector">
      <select value={selected} onChange={e => onChange(e.target.value)}>
        <option value="">All Personas</option>
        {personas.map(p => (
          <option key={p} value={p}>{p}</option>
        ))}
      </select>
      <p data-testid="mode-indicator">
        {selected ? '🔍 Deep Dive Mode' : '📊 Comparison Mode'}
      </p>
    </div>
  )
}

export default PersonaSelector
