import React from 'react'
import { useQuery } from '@tanstack/react-query'
import { type ColumnDef } from '@tanstack/react-table'
import { PageContainer, ScoreCard, DataTable, ChartCard, PlotlyChart } from '../components'

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

  const columns = React.useMemo<ColumnDef<Opportunity>[]>(
    () => [
      { accessorKey: 'page', header: 'Page' },
      { accessorKey: 'impact', header: 'Impact' },
      { accessorKey: 'effort', header: 'Effort' },
      { accessorKey: 'tier', header: 'Tier' },
      { accessorKey: 'currentScore', header: 'Current Score' }
    ],
    []
  )

  return (
    <PageContainer title="Opportunity Impact">
      <div className="filter-bar">
        <ScoreCard label="Total Opps" value={total} />
        <ScoreCard label="Avg Impact" value={avgImpact.toFixed(1)} />
        <ScoreCard label="High Impact" value={highImpact} />
        <ScoreCard label="Low Effort" value={lowEffort} />
      </div>

      <ChartCard title="Impact vs Effort">
        <PlotlyChart
          data={[
            {
              x: opps.map(o => o.effort),
              y: opps.map(o => o.impact),
              text: opps.map(o => o.page),
              mode: 'markers',
              type: 'scatter',
              marker: { color: '#dc3545' }
            }
          ]}
          layout={{ xaxis: { title: 'Effort' }, yaxis: { title: 'Impact' }, height: 300 }}
        />
      </ChartCard>

      <DataTable data={opps} columns={columns} />
    </PageContainer>
  )
}

export default OpportunityImpact
