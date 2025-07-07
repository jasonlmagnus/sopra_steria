import React from 'react'
import { useFilters } from '../context/FilterContext'

export interface FilterControlsProps {
  personas?: string[]
  tiers?: string[]
}

export function FilterControls({ personas = [], tiers = [] }: FilterControlsProps) {
  const { persona, tier, setPersona, setTier } = useFilters()
  return (
    <div className="filter-controls">
      <select value={persona} onChange={(e) => setPersona(e.target.value)}>
        <option value="">All Personas</option>
        {personas.map(p => (
          <option key={p} value={p}>{p}</option>
        ))}
      </select>
      <select value={tier} onChange={(e) => setTier(e.target.value)} style={{ marginLeft: '0.5rem' }}>
        <option value="">All Tiers</option>
        {tiers.map(t => (
          <option key={t} value={t}>{t}</option>
        ))}
      </select>
    </div>
  )
}

export default FilterControls
