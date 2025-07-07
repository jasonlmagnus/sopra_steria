import React, { useEffect } from 'react'
import { useFilters } from '../context/FilterContext'

export interface FilterSystemProps {
  personaOptions: string[]
  tierOptions: string[]
}

export function FilterSystem({ personaOptions, tierOptions }: FilterSystemProps) {
  const { persona, setPersona, tier, setTier, scoreRange, setScoreRange } = useFilters()

  useEffect(() => {
    const saved = sessionStorage.getItem('filters')
    if (saved) {
      try {
        const f = JSON.parse(saved)
        if (f.persona) setPersona(f.persona)
        if (f.tier) setTier(f.tier)
        if (f.scoreRange) setScoreRange(f.scoreRange)
      } catch {
        // ignore parse errors
      }
    }
  }, [setPersona, setTier, setScoreRange])

  useEffect(() => {
    sessionStorage.setItem('filters', JSON.stringify({ persona, tier, scoreRange }))
  }, [persona, tier, scoreRange])

  return (
    <div className="filter-system">
      <select value={persona} onChange={(e) => setPersona(e.target.value)}>
        <option value="">All Personas</option>
        {personaOptions.map((p) => (
          <option key={p} value={p}>
            {p}
          </option>
        ))}
      </select>
      <select value={tier} onChange={(e) => setTier(e.target.value)} style={{ marginLeft: '0.5rem' }}>
        <option value="">All Tiers</option>
        {tierOptions.map((t) => (
          <option key={t} value={t}>
            {t}
          </option>
        ))}
      </select>
      <label style={{ marginLeft: '0.5rem' }}>
        Score ≥ {scoreRange[0]}
        <input
          type="range"
          min="0"
          max="10"
          step="0.5"
          value={scoreRange[0]}
          onChange={(e) => setScoreRange([Number(e.target.value), scoreRange[1]])}
        />
      </label>
    </div>
  )
}

export default FilterSystem
