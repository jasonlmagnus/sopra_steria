import React, { useEffect, useState } from 'react'
import { useQuery } from '@tanstack/react-query'
import { PlotlyChart } from '../components'

const apiBase = import.meta.env.VITE_API_URL || 'http://localhost:3000'

function PersonaInsights() {
  const [personas, setPersonas] = useState<string[]>([])

  useEffect(() => {
    fetch(`${apiBase}/api/personas`)
      .then((res) => res.json())
      .then((data) => setPersonas(data.personas || []))
  }, [])

  const { data: comparison } = useQuery({
    queryKey: ['persona-comparison'],
    queryFn: async () => {
      const res = await fetch(`${apiBase}/api/persona-comparison`)
      if (!res.ok) throw new Error('Failed to load comparison')
      return res.json()
    }
  })

  return (
    <div>
      <h2>Persona Insights</h2>
      <ul>
        {personas.map((p) => (
          <li key={p}>{p}</li>
        ))}
      </ul>
      {Array.isArray(comparison) && (
        <PlotlyChart
          data={[{
            x: comparison.map((c: any) => c.persona_id),
            y: comparison.map((c: any) => c.final_score_mean || c.raw_score_mean),
            type: 'bar',
            marker: { color: '#3d4a6b' }
          }]}
          layout={{ height: 300, xaxis: { title: 'Persona' }, yaxis: { title: 'Avg Score' } }}
        />
      )}
    </div>
  )
}

export default PersonaInsights;
