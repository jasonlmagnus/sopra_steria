import React, { useState } from 'react'

export interface ExpandableCardProps {
  title: string
  children: React.ReactNode
  defaultExpanded?: boolean
}

export function ExpandableCard({ title, children, defaultExpanded = false }: ExpandableCardProps) {
  const [open, setOpen] = useState(defaultExpanded)
  return (
    <div className={`expandable-card${open ? ' expanded' : ''}`}>\
      <div className="expandable-card__header" onClick={() => setOpen(!open)} style={{cursor:'pointer'}}>
        {open ? '▼' : '▶'} {title}
      </div>
      <div
        className="expandable-card__body"
        style={{ maxHeight: open ? '1000px' : '0', overflow: 'hidden', transition: 'max-height 0.3s ease' }}
      >
        {open && <div>{children}</div>}
      </div>
    </div>
  )
}

export default ExpandableCard
