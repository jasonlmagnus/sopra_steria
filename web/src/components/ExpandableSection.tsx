import React, { useState } from 'react'

export interface ExpandableSectionProps {
  title: string
  children: React.ReactNode
  defaultExpanded?: boolean
}

export function ExpandableSection({ title, children, defaultExpanded = false }: ExpandableSectionProps) {
  const [open, setOpen] = useState(defaultExpanded)
  return (
    <section className="expandable-section">
      <h4 onClick={() => setOpen(!open)} style={{cursor: 'pointer'}}>
        {open ? '▼' : '▶'} {title}
      </h4>
      {open && <div className="expandable-content">{children}</div>}
    </section>
  )
}

export default ExpandableSection
