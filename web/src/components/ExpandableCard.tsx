import React, { useState } from 'react'
import './../styles/components/card.css'

export interface ExpandableCardProps {
  title: string
  children: React.ReactNode
  defaultExpanded?: boolean
}

export function ExpandableCard({ title, children, defaultExpanded = false }: ExpandableCardProps) {
  const [open, setOpen] = useState(defaultExpanded)
  
  const cardClasses = `expandable-card${open ? ' expanded' : ''}`
  
  return (
    <div className={cardClasses}>
      <div className="expandable-card__header" onClick={() => setOpen(!open)}>
        <span className="expandable-card__header-icon">▶</span>
        {title}
      </div>
      <div className="expandable-card__body">
        {children}
      </div>
    </div>
  )
}

export default ExpandableCard
