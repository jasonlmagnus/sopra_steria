import { useQuery } from '@tanstack/react-query'
import React from 'react'
import { PageContainer, ScoreCard, ChartCard, PlotlyChart } from '../components'

const apiBase = import.meta.env.VITE_API_URL || 'http://localhost:3000'

function ExecutiveDashboard() {
  const { data, isLoading, error } = useQuery({
    queryKey: ['summary'],
    queryFn: async () => {
      const res = await fetch(`${apiBase}/api/summary`)
      if (!res.ok) throw new Error('Failed to load summary')
      return res.json()
    }
  })

  if (isLoading) return <p>Loading summary...</p>
  if (error) return <p>Error loading summary</p>

  const brand = data?.brand_health || {}
  const metrics = data?.key_metrics || {}
  const recs = Array.isArray(data?.recommendations) ? data.recommendations : []
  const tierMetrics = data?.score_by_tier || {}

  return (
    <PageContainer title="Executive Dashboard">
      <p>
        Brand Health: <strong>{brand.raw_score}</strong> {brand.emoji}
      </p>
      <div className="filter-bar">
        <ScoreCard label="Total Pages" value={metrics.total_pages} />
        <ScoreCard
          label="Critical Issues"
          value={metrics.critical_issues}
          variant={
            metrics.critical_issues > 10
              ? 'danger'
              : metrics.critical_issues > 0
              ? 'warning'
              : 'success'
          }
        />
        <ScoreCard
          label="Quick Wins"
          value={metrics.quick_wins}
          variant={metrics.quick_wins > 0 ? 'warning' : 'success'}
        />
        <ScoreCard label="Success Pages" value={metrics.success_pages} variant="success" />
      </div>

      <ChartCard title="Average Score by Tier">
        <PlotlyChart
          data={[{
            x: Object.keys(tierMetrics),
            y: Object.values(tierMetrics),
            type: 'bar',
            marker: { color: '#3d4a6b' }
          }]}
          layout={{ height: 300 }}
        />
      </ChartCard>
      <h3>Top Recommendations</h3>
      <ul>
        {recs.map((r: string, idx: number) => (
          <li key={idx}>{r}</li>
        ))}
      </ul>
    </PageContainer>
  )
}

export default ExecutiveDashboard
