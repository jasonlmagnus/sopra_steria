import React, { useState } from 'react'

export interface EvidenceItem {
  title: string
  url: string
  score: number
}

export interface EvidenceBrowserProps {
  items: EvidenceItem[]
}

export function EvidenceBrowser({ items }: EvidenceBrowserProps) {
  const [query, setQuery] = useState('')
  const filtered = items.filter(i =>
    i.title.toLowerCase().includes(query.toLowerCase()) ||
    i.url.toLowerCase().includes(query.toLowerCase())
  )
  return (
    <div className="evidence-browser">
      <input
        placeholder="Search evidence..."
        value={query}
        onChange={e => setQuery(e.target.value)}
      />
      <ul>
        {filtered.map((i, idx) => (
          <li key={idx}>
            <a href={i.url}>{i.title}</a> ({i.score})
          </li>
        ))}
      </ul>
    </div>
  )
}

export default EvidenceBrowser
