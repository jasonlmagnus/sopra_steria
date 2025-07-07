import React from 'react'
import { useQuery } from '@tanstack/react-query'
import { ScatterChart, Scatter, XAxis, YAxis, Tooltip } from 'recharts'

interface Opportunity {
  page: string
  impact: number
  effort: number
  tier: string
  currentScore: number
}

const apiBase = import.meta.env.VITE_API_URL || 'http://localhost:3000'

function OpportunityImpact() {
  const { data, isLoading, error } = useQuery({
    queryKey: ['opportunities'],
    queryFn: async () => {
      const res = await fetch(`${apiBase}/api/opportunities`)
      if (!res.ok) throw new Error('Failed to load opportunities')
      return res.json()
    }
  })

  const opps: Opportunity[] = Array.isArray(data?.opportunities)
    ? data.opportunities.map((o: any) => ({
        page: o.page_title,
        impact: o.potential_impact,
        effort:
          o.effort_level === 'Low' ? 1 : o.effort_level === 'Medium' ? 2 : 3,
        tier: o.tier_name || o.tier,
        currentScore: o.current_score
      }))
    : []

  const total = opps.length
  const avgImpact = total ? opps.reduce((s, d) => s + d.impact, 0) / total : 0
  const highImpact = opps.filter(d => d.impact >= 7).length
  const lowEffort = opps.filter(d => d.effort <= 2).length

  if (isLoading) return <p>Loading opportunities...</p>
  if (error) return <p>Error loading opportunities</p>

  return (
    <div>
      <h2>Opportunity Impact</h2>
      <div style={{ display: 'flex', gap: '1rem', marginBottom: '1rem' }}>
        <div>
          <strong>{total}</strong>
          <div>Total Opps</div>
        </div>
        <div>
          <strong>{avgImpact.toFixed(1)}</strong>
          <div>Avg Impact</div>
        </div>
        <div>
          <strong>{highImpact}</strong>
          <div>High Impact</div>
        </div>
        <div>
          <strong>{lowEffort}</strong>
          <div>Low Effort</div>
        </div>
      </div>

      <ScatterChart width={600} height={300}>
        <XAxis type="number" dataKey="effort" name="Effort" domain={[0,10]} />
        <YAxis type="number" dataKey="impact" name="Impact" domain={[0,10]} />
        <Tooltip cursor={{ stroke: '#8884d8', strokeDasharray: '3 3' }} />
        <Scatter data={opps} fill="#dc3545" />
      </ScatterChart>

      <table style={{ marginTop: '1rem' }}>
        <thead>
          <tr>
            <th>Page</th>
            <th>Impact</th>
            <th>Effort</th>
            <th>Tier</th>
            <th>Current Score</th>
          </tr>
        </thead>
        <tbody>
          {opps.map((d, i) => (
            <tr key={i}>
              <td>{d.page}</td>
              <td>{d.impact}</td>
              <td>{d.effort}</td>
              <td>{d.tier}</td>
              <td>{d.currentScore}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  )
}

export default OpportunityImpact
