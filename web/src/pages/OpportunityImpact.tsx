import React from 'react'
import { ScatterChart, Scatter, XAxis, YAxis, Tooltip } from 'recharts'

interface Opportunity {
  page: string
  impact: number
  effort: number
  tier: string
  currentScore: number
}

const data: Opportunity[] = [
  { page: 'Homepage Messaging', impact: 9.2, effort: 4, tier: 'Tier 1', currentScore: 3.5 },
  { page: 'Navigation UX', impact: 7.5, effort: 6, tier: 'Tier 2', currentScore: 4.8 },
  { page: 'Visual Brand Elements', impact: 6.8, effort: 5, tier: 'Tier 2', currentScore: 5.1 },
  { page: 'Social Media Consistency', impact: 8.0, effort: 3, tier: 'Tier 3', currentScore: 4.0 },
  { page: 'Page Performance', impact: 5.5, effort: 2, tier: 'Tier 1', currentScore: 6.5 },
]

function OpportunityImpact() {
  const total = data.length
  const avgImpact = data.reduce((s, d) => s + d.impact, 0) / total
  const highImpact = data.filter(d => d.impact >= 7).length
  const lowEffort = data.filter(d => d.effort <= 3).length

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
        <Scatter data={data} fill="#dc3545" />
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
          {data.map((d, i) => (
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
