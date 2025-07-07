import React from 'react'

export interface FilterBarProps {
  children?: React.ReactNode
}

export function FilterBar({ children }: FilterBarProps) {
  return <div className="filter-bar">{children}</div>
}

export default FilterBar
