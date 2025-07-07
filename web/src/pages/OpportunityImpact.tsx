import React from 'react'
import { useQuery } from '@tanstack/react-query'
import { ScatterChart, Scatter, XAxis, YAxis, Tooltip } from 'recharts'
import { ColumnDef } from '@tanstack/react-table'
import { PageContainer, ScoreCard, DataTable, ChartCard } from '../components'

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
        <ScatterChart width={600} height={300}>
          <XAxis type="number" dataKey="effort" name="Effort" domain={[0, 10]} />
          <YAxis type="number" dataKey="impact" name="Impact" domain={[0, 10]} />
          <Tooltip cursor={{ stroke: '#8884d8', strokeDasharray: '3 3' }} />
          <Scatter data={opps} fill="#dc3545" />
        </ScatterChart>
      </ChartCard>

      <DataTable data={opps} columns={columns} />
    </PageContainer>
  )
}

export default OpportunityImpact
