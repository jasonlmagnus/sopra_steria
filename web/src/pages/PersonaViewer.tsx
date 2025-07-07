import React, { useEffect, useState } from 'react'
import ReactMarkdown from 'react-markdown'

function PersonaViewer() {
  const [personas, setPersonas] = useState<string[]>([])
  const [selected, setSelected] = useState('')
  const [content, setContent] = useState('')

  useEffect(() => {
    fetch('http://localhost:3000/api/personas')
      .then((res) => res.json())
      .then((data) => setPersonas(data.personas || []))
  }, [])

  useEffect(() => {
    if (selected) {
      fetch(`http://localhost:3000/api/personas/${selected}`)
        .then((res) => res.json())
        .then((data) => setContent(data.content))
    }
  }, [selected])

  return (
    <div>
      <h2>Persona Viewer</h2>
      <select value={selected} onChange={(e) => setSelected(e.target.value)}>
        <option value="">Select persona</option>
        {personas.map((p) => (
          <option key={p} value={p}>
            {p}
          </option>
        ))}
      </select>
      {content && (
        <div style={{ marginTop: '1rem' }}>
          <ReactMarkdown>{content}</ReactMarkdown>
        </div>
      )}
    </div>
  )
}

export default PersonaViewer;
