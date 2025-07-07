import { useQuery } from '@tanstack/react-query'
import React from 'react'
import { PageContainer, ScoreCard, ChartCard, PlotlyChart, ExpandableCard, MetricsCard } from '../components'

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

  const { data: oppData } = useQuery({
    queryKey: ['opportunities'],
    queryFn: async () => {
      const res = await fetch(`${apiBase}/api/opportunities?limit=3`)
      if (!res.ok) throw new Error('Failed to load opportunities')
      return res.json()
    }
  })
  const opps = Array.isArray(oppData?.opportunities) ? oppData.opportunities : []

  return (
    <PageContainer title="Executive Dashboard">
      <ExpandableCard title="Brand Health" defaultExpanded>
        <p>
          Score: <strong>{brand.raw_score}</strong> {brand.emoji}
        </p>
      </ExpandableCard>

      <ExpandableCard title="Key Metrics" defaultExpanded>
        <div className="filter-bar">
          <MetricsCard label="Total Pages" value={metrics.total_pages} />
          <MetricsCard label="Critical Issues" value={metrics.critical_issues} multiplier={1.5} />
          <MetricsCard label="Quick Wins" value={metrics.quick_wins} />
          <MetricsCard label="Success Pages" value={metrics.success_pages} />
        </div>
      </ExpandableCard>

      <ExpandableCard title="Sentiment" defaultExpanded>
        <p>Net Sentiment: {data?.sentiment?.net_sentiment}%</p>
      </ExpandableCard>

      <ExpandableCard title="Conversion Readiness" defaultExpanded>
        <p>
          {data?.conversion?.status}: {data?.conversion?.score}
        </p>
      </ExpandableCard>

      <ExpandableCard title="Average Score by Tier" defaultExpanded>
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
      </ExpandableCard>

      <ExpandableCard title="Top Opportunities" defaultExpanded>
        <ul>
          {opps.map((o: any, idx: number) => (
            <li key={idx}>{o.page_title}</li>
          ))}
        </ul>
      </ExpandableCard>

      <ExpandableCard title="Top Recommendations" defaultExpanded>
        <ul>
          {recs.map((r: string, idx: number) => (
            <li key={idx}>{r}</li>
          ))}
        </ul>
      </ExpandableCard>
    </PageContainer>
  )
}

export default ExecutiveDashboard
