import React, { useEffect, useState } from 'react'

function PersonaInsights() {
  const [personas, setPersonas] = useState<string[]>([])

  useEffect(() => {
    fetch('http://localhost:3000/api/personas')
      .then((res) => res.json())
      .then((data) => setPersonas(data.personas || []))
  }, [])

  return (
    <div>
      <h2>Persona Insights</h2>
      <ul>
        {personas.map((p) => (
          <li key={p}>{p}</li>
        ))}
      </ul>
    </div>
  )
}

export default PersonaInsights;
