import React, { useEffect, useState } from 'react'
import ReactMarkdown from 'react-markdown'
import { useFilters } from '../context/FilterContext'

const apiBase = import.meta.env.VITE_API_URL || 'http://localhost:3000'

function PersonaViewer() {
  const [personas, setPersonas] = useState<string[]>([])
  const { persona: selected, setPersona: setSelected } = useFilters()
  const [content, setContent] = useState('')
  const [journey, setJourney] = useState<any[]>([])
  const [step, setStep] = useState('')

  useEffect(() => {
    fetch(`${apiBase}/api/personas`)
      .then((res) => res.json())
      .then((data) => setPersonas(data.personas || []))
  }, [])

  useEffect(() => {
    if (selected) {
      fetch(`${apiBase}/api/personas/${selected}`)
        .then((res) => res.json())
        .then((data) => setContent(data.content))

      fetch(`${apiBase}/api/persona-journeys/${selected}`)
        .then((res) => res.json())
        .then((data) => {
          setJourney(data.steps || [])
          setStep('')
        })
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
      {journey.length > 0 && (
        <select value={step} onChange={(e) => setStep(e.target.value)} style={{ marginLeft: '0.5rem' }}>
          <option value="">All Steps</option>
          {journey.map((j, idx) => (
            <option key={idx} value={String(idx)}>
              {j.step.split('**')[1]}
            </option>
          ))}
        </select>
      )}
      {content && (
        <div style={{ marginTop: '1rem' }}>
          <ReactMarkdown>{content}</ReactMarkdown>
        </div>
      )}
      {journey.length > 0 && (
        <div style={{ marginTop: '1rem' }}>
          {(step ? [journey[Number(step)]] : journey).map((j, i) => (
            <div key={i} style={{ marginBottom: '1rem' }}>
              <strong>{j.step}</strong>
              <p dangerouslySetInnerHTML={{ __html: j.evaluation }} />
              <p dangerouslySetInnerHTML={{ __html: j.severity }} />
              <p>{j.quickFix}</p>
            </div>
          ))}
        </div>
      )}
    </div>
  )
}

export default PersonaViewer;
