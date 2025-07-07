import React, { createContext, useContext, useState } from 'react'

export interface FilterState {
  persona: string
  tier: string
  scoreRange: [number, number]
}

interface FilterContextValue extends FilterState {
  setPersona: (p: string) => void
  setTier: (t: string) => void
  setScoreRange: (r: [number, number]) => void
}

const FilterContext = createContext<FilterContextValue | undefined>(undefined)

export function useFilters() {
  const ctx = useContext(FilterContext)
  if (!ctx) throw new Error('useFilters must be used within FilterProvider')
  return ctx
}

export function FilterProvider({ children }: { children: React.ReactNode }) {
  const [persona, setPersona] = useState('')
  const [tier, setTier] = useState('')
  const [scoreRange, setScoreRange] = useState<[number, number]>([0, 10])

  const value: FilterContextValue = {
    persona,
    tier,
    scoreRange,
    setPersona,
    setTier,
    setScoreRange
  }

  return <FilterContext.Provider value={value}>{children}</FilterContext.Provider>
}

export default FilterContext
