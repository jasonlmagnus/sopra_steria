import React from 'react'
import { useQuery } from '@tanstack/react-query'
import { type ColumnDef } from '@tanstack/react-table'
import { PageContainer, ScoreCard, DataTable, ChartCard, PlotlyChart, ExpandableSection, FilterBar, FilterSystem, ActionRoadmap } from '../components'
import { useFilters } from '../context/FilterContext'

interface Opportunity {
  page: string
  impact: number
  effort: number
  tier: string
  currentScore: number
  persona?: string
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

  const { persona, tier } = useFilters()

  const opps: Opportunity[] = Array.isArray(data?.opportunities)
    ? data.opportunities.map((o: any) => ({
        page: o.page_title,
        impact: o.potential_impact,
        effort:
          o.effort_level === 'Low' ? 1 : o.effort_level === 'Medium' ? 2 : 3,
        tier: o.tier_name || o.tier,
        currentScore: o.current_score,
        persona: o.persona_id
      }))
    : []

  const personaOptions = Array.from(new Set(opps.map(o => o.persona).filter(Boolean))) as string[]
  const tierOptions = Array.from(new Set(opps.map(o => o.tier).filter(Boolean)))

  const filteredOpps = opps.filter(o =>
    (!persona || o.persona === persona) && (!tier || o.tier === tier)
  )

  const total = filteredOpps.length
  const avgImpact = total ? filteredOpps.reduce((s, d) => s + d.impact, 0) / total : 0
  const highImpact = filteredOpps.filter(d => d.impact >= 7).length
  const lowEffort = filteredOpps.filter(d => d.effort <= 2).length

  const roadmapData = [
    {
      phase: 'Phase 1 (0-30 days)',
      category: 'Quick Wins',
      count: filteredOpps.filter(o => o.effort <= 2 && o.impact >= 6).length,
      color: '#10b981'
    },
    {
      phase: 'Phase 2 (30-90 days)',
      category: 'Fill-ins',
      count: filteredOpps.filter(o => o.effort === 2).length,
      color: '#f59e0b'
    },
    {
      phase: 'Phase 3 (90+ days)',
      category: 'Major Projects',
      count: filteredOpps.filter(o => o.effort === 3 && o.impact >= 7).length,
      color: '#dc2626'
    }
  ]

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

  if (isLoading) return <p>Loading opportunities...</p>
  if (error) return <p>Error loading opportunities</p>

  return (
    <PageContainer title="Opportunity Impact">
      <FilterBar>
        <FilterSystem personaOptions={personaOptions} tierOptions={tierOptions} />
        <ScoreCard label="Total Opps" value={total} />
        <ScoreCard
          label="Avg Impact"
          value={avgImpact.toFixed(1)}
          variant={avgImpact >= 7 ? 'success' : avgImpact >= 4 ? 'warning' : 'danger'}
        />
        <ScoreCard label="High Impact" value={highImpact} variant="success" />
        <ScoreCard label="Low Effort" value={lowEffort} variant="success" />
      </FilterBar>

      <ExpandableSection title="Impact vs Effort Chart" defaultExpanded>
        <ChartCard title="Impact vs Effort">
          <PlotlyChart
            data={[
              {
                x: filteredOpps.map(o => o.effort),
                y: filteredOpps.map(o => o.impact),
                text: filteredOpps.map(o => o.page),
                mode: 'markers',
                type: 'scatter',
                marker: { color: '#dc3545' }
              }
            ]}
            layout={{ xaxis: { title: 'Effort' }, yaxis: { title: 'Impact' }, height: 300 }}
          />
        </ChartCard>
      </ExpandableSection>

      <ExpandableSection title="Opportunity Table" defaultExpanded>
        <DataTable data={filteredOpps} columns={columns} />
      </ExpandableSection>
      <ExpandableSection title="Action Roadmap" defaultExpanded>
        <ActionRoadmap data={roadmapData} />
      </ExpandableSection>
    </PageContainer>
  )
}

export default OpportunityImpact
