import { useState, useEffect } from 'react'
import { useQuery } from '@tanstack/react-query'
import { Banner, BarChart, HeatmapChart, DataTable, StandardCard, PageContainer, PageHeader } from '../components'
import { EvidenceDisplay } from '../components/EvidenceDisplay'
import type { ColumnDef } from '@tanstack/react-table'
import { useFilters } from '../hooks/useFilters'
import { FilterSystem } from '../components/FilterSystem'
import type { FilterConfig } from '../types/filters'

const apiBase = import.meta.env.VITE_API_URL || 'http://localhost:3000'

interface Criteria {
  name: string;
  avgScore: number;
}

interface Page {
  id: string;
  title: string;
  tier: string;
  avgScore: number;
  overall_sentiment?: number;
  personas: string;
  url?: string;
  evidence?: string;
  effective_copy_examples?: string;
  ineffective_copy_examples?: string;
  trust_credibility_assessment?: string;
  business_impact_analysis?: string;
  information_gaps?: string;
}

const contentMatrixFilters: FilterConfig[] = [
  { name: 'persona', label: '👥 Persona', type: 'select', defaultValue: 'All' },
  { name: 'tier', label: '🏗️ Content Tier', type: 'select', defaultValue: 'All' },
  { 
    name: 'minScore', 
    label: '📊 Min Score', 
    type: 'range', 
    defaultValue: 0, 
    min: 0, 
    max: 10, 
    step: 0.5 
  },
  { 
    name: 'performanceLevel', 
    label: '⭐ Performance Level', 
    type: 'select', 
    defaultValue: 'All',
    options: [
      { value: 'All', label: 'All' },
      { value: 'Excellent', label: 'Excellent (≥8)' },
      { value: 'Good', label: 'Good (6-8)' },
      { value: 'Fair', label: 'Fair (4-6)' },
      { value: 'Poor', label: 'Poor (<4)' }
    ]
  }
];


function ContentMatrix() {
  const { filters, setAllFilters } = useFilters();

  useEffect(() => {
    const defaultFilters = contentMatrixFilters.reduce((acc, filter) => {
      acc[filter.name] = filter.defaultValue;
      return acc;
    }, {} as { [key: string]: any });
    setAllFilters(defaultFilters);
  }, [setAllFilters]);

  const { data: contentData, isLoading, error } = useQuery({
    queryKey: ['content-matrix', filters],
    queryFn: async () => {
      const params = new URLSearchParams(filters)
      const res = await fetch(`${apiBase}/api/content-matrix?${params}`)
      if (!res.ok) throw new Error('Failed to load content matrix')
      return res.json()
    }
  })

  if (isLoading) return (
    <div className="container--layout">
      <PageHeader
        title="📊 Content Matrix"
        description="Loading content analysis..."
      />
      <div className="container--section text--display">
        <Banner message={<p className="text--body">🔄 Updating filters...</p>} />
      </div>
    </div>
  )

  if (error) return (
    <div className="container--layout">
      <PageHeader
        title="📊 Content Matrix"
        description="Error loading content analysis"
      />
      <div className="container--section">
        <Banner
          type="error"
          message={
            <>
              <p className="text--body">❌ Error: {error.message}</p>
              <p className="text--body">Please try adjusting your filters or refresh the page.</p>
            </>
          }
        />
      </div>
    </div>
  )

  const data = contentData || {}
  // This transformation is needed for the FilterSystem component
  data.personaOptions = (data.personas || []).map((p: string) => ({ value: p, label: p }));
  data.personaOptions.unshift({ value: 'All', label: 'All Personas' });
  data.tierOptions = (data.tiers || []).map((t: string) => ({ value: t, label: t }));
  data.tierOptions.unshift({ value: 'All', label: 'All Tiers' });
  const metrics = data.metrics || {}
  const heatmapData = data.heatmap || {}
  const criteriaData = data.criteria || []
  const pageData = data.pages || []

  // Handle empty data case
  if (data.error || (metrics.totalPages === 0 && filters.minScore > 0)) {
    return (
      <PageContainer title="📊 Content Matrix">
        <PageHeader
          title="📊 Content Matrix"
          description="Comprehensive content analysis with performance scoring and strategic insights"
        />

        {/* Show filters even when no data */}
        <FilterSystem config={contentMatrixFilters} data={data} />

        <div className="container--section">
          <h2 className="heading--section">📊 No Data Matches Current Filters</h2>
          <Banner
            type="warning"
            message={
              <>
                <h4 className="reset-text">⚠️ Filter Results</h4>
                <p className="text--emphasis">
                  No pages match your current filter criteria
                </p>
                <p className="my-xs">
                  <strong>Try:</strong> Lowering the minimum score slider or selecting "All" for other filters
                </p>
              </>
            }
          />
          
          <div className="container--section text--display">
            <p className="text--body-large text-gray-600">
              Current filters: <strong>Persona:</strong> {filters.persona}, <strong>Tier:</strong> {filters.tier}, 
              <strong>Min Score:</strong> {filters.minScore}, <strong>Performance:</strong> {filters.performanceLevel}
            </p>
          </div>
        </div>
      </PageContainer>
    )
  }

  return (
    <PageContainer title="📊 Content Matrix">
      <PageHeader
        title="📊 Content Matrix"
        description="Comprehensive content analysis with performance scoring and strategic insights"
      />

      {/* Content Analysis Filters */}
      <FilterSystem config={contentMatrixFilters} data={data} />

      {/* Performance Overview */}
      <PerformanceOverview metrics={metrics} />

      {/* Tier Performance Analysis */}
      <TierPerformanceAnalysis data={data} />

      {/* Content Performance Heatmap */}
      <ContentHeatmap heatmapData={heatmapData} />

      {/* Criteria Deep Dive */}
      <CriteriaDeepDive criteriaData={criteriaData} />

      {/* Page Drill Down */}
      <PageDrillDown pageData={pageData} />

      {/* Persona-Specific Evidence Context */}
      <PersonaEvidenceContext data={data} />
    </PageContainer>
  )
}

function PerformanceOverview({ metrics }: any) {
  const avgScore = metrics.avgScore || 0
  const totalPages = metrics.totalPages || 0
  const poorPerformers = metrics.poorPerformers || 0
  
  let businessImpact = "📊 Content analysis ready"
  let bannerType: 'info' | 'success' | 'warning' | 'error' = 'info'
  
  if (avgScore >= 8) {
    businessImpact = "🚀 Strong content performance across pages"
    bannerType = 'success'
  } else if (avgScore >= 6) {
    businessImpact = `⚠️ ${poorPerformers} pages need improvement`
    bannerType = 'warning'
  } else if (avgScore > 0) {
    businessImpact = `🚨 ${poorPerformers} pages require attention`
    bannerType = 'error'
  }

  return (
    <div className="container--section">
      <h2 className="heading--section">📈 Performance Overview</h2>
      
      {/* Business Impact Context */}
      <Banner
        type={bannerType}
        message={
          <>
            <h4 className="reset-text">💡 Content Status</h4>
            <p className="text--body text--emphasis">{businessImpact}</p>
            <p className="text--body">
              <strong>Focus:</strong> Prioritize pages scoring below 6.0 for maximum impact
            </p>
          </>
        }
      />

      {/* Performance Metrics */}
      <div className="container--layout">
        <div className="container--section">
          <div className="text--display">{avgScore.toFixed(1)}</div>
          <div className="text--display">Average Score</div>
        </div>
        <div className="container--section">
          <div className="text--display">{totalPages}</div>
          <div className="text--display">Total Pages</div>
        </div>
        <div className="container--section">
          <div className="text--display">{metrics.excellent || 0}</div>
          <div className="text--display">Excellent (≥8)</div>
        </div>
        <div className="container--section">
          <div className="text--display">{metrics.good || 0}</div>
          <div className="text--display">Good (6-8)</div>
        </div>
        <div className="container--section">
          <div className="text--display">{metrics.fair || 0}</div>
          <div className="text--display">Fair (4-6)</div>
        </div>
        <div className="container--section">
          <div className="text--display">{metrics.poor || 0}</div>
          <div className="text--display">Poor (&lt;4)</div>
        </div>
      </div>

      {/* Performance Distribution Chart */}
      {(metrics.excellent || metrics.good || metrics.fair || metrics.poor) && (
        <div className="spacing--sm">
          <BarChart 
            orientation="h"
            x={[metrics.excellent || 0, metrics.good || 0, metrics.fair || 0, metrics.poor || 0]}
            y={['Excellent (≥8)', 'Good (6-8)', 'Fair (4-6)', 'Poor (&lt;4)']}
          />
        </div>
      )}
    </div>
  )
}

function TierPerformanceAnalysis({ data }: any) {
  const tiers = data.tiers || []
  const tierScores = data.tierScores || {}

  if (tiers.length === 0) return null

  return (
    <div className="container--section">
      <h2 className="heading--section">🏗️ Tier Performance Analysis</h2>
      <div className="container--grid" style={{ gridTemplateColumns: `repeat(${tiers.length}, 1fr)` }}>
        {tiers.map((tier: string) => (
          <div key={tier} className="card">
            <h3 className="heading--card">{tier}</h3>
            <div className="text--display">
              {(tierScores[tier] || 0).toFixed(1)}
            </div>
            <div className="text--body">Average Score</div>
          </div>
        ))}
      </div>
    </div>
  )
}

function ContentHeatmap({ heatmapData }: any) {
  if (!heatmapData || Object.keys(heatmapData).length === 0) return null

  return (
    <div className="container--section">
      <h2 className="heading--section">🔥 Content Performance Heatmap</h2>
      <div className="card">
        <HeatmapChart
          data={heatmapData}
          title="Persona vs. Content Tier Performance"
          xLabel="Content Tiers"
          yLabel="Personas"
        />
      </div>
    </div>
  )
}

function CriteriaDeepDive({ criteriaData }: { criteriaData: Criteria[] }) {
  if (criteriaData.length === 0) return null

  return (
    <div className="container--section">
      <h2 className="heading--section">🎯 Criteria Deep Dive</h2>
      <div className="card">
        <BarChart
          data={criteriaData}
          indexBy="name"
          keys={['avgScore']}
          title="Average Score by Evaluation Criteria"
          yLabel="Average Score"
          xLabel="Criteria"
          layout="horizontal"
          enableGridX={true}
          enableGridY={false}
        />
      </div>
    </div>
  )
}

function PageDrillDown({ pageData }: { pageData: Page[] }) {
  const [selectedPage, setSelectedPage] = useState('')

  const columns: ColumnDef<Page>[] = [
    { accessorKey: 'title', header: 'Page' },
    { accessorKey: 'tier', header: 'Tier' },
    {
      accessorKey: 'avgScore',
      header: 'Score',
      cell: info => {
        const value = info.getValue();
        return typeof value === 'number' ? value.toFixed(1) : 'N/A';
      }
    },
    {
      accessorKey: 'overall_sentiment',
      header: 'Sentiment',
      cell: info => {
        const value = info.getValue();
        return typeof value === 'number' ? value.toFixed(1) : 'N/A';
      }
    },
    { accessorKey: 'personas', header: 'Personas' }
  ]

  return (
    <div className="container--section">
      <h2 className="heading--section">📄 Page Drill-Down</h2>
      
      <Banner
        type="success"
        message={
          <>
            <h4 className="reset-text">💡 Page Analysis</h4>
            <p className="text--body">
              Analyze individual page performance across criteria.
            </p>
            <p className="text--body">
              <strong>Focus:</strong> Select a page to see its detailed scorecard.
            </p>
          </>
        }
      />

      {pageData.length > 0 && (
        <div>
          {/* Page Selection */}
          <div className="container--section">
            <label className="label--form">
              Select Page for Detailed Analysis:
            </label>
            <select 
              value={selectedPage}
              onChange={(e) => setSelectedPage(e.target.value)}
              className="select--form"
            >
              <option value="">Choose a page...</option>
              {pageData.map((page: any) => (
                <option key={page.id} value={page.id}>{page.title}</option>
              ))}
            </select>
          </div>

          {/* Page Performance Summary */}
          <h3 className="heading--subsection">📊 Page Performance Summary</h3>
          <DataTable columns={columns} data={pageData.slice(0, 10)} />

          {/* Selected Page Details */}
          {selectedPage && (
            <div className="spacing--sm">
              {(() => {
                const page = pageData.find((p: any) => p.id === selectedPage)
                if (!page) return null
                
                // Extract evidence from page data
                const evidenceItems = []
                if (page.evidence) {
                  evidenceItems.push({
                    type: 'evidence' as const,
                    content: page.evidence,
                    title: 'AI Analysis'
                  })
                }
                if (page.effective_copy_examples) {
                  evidenceItems.push({
                    type: 'effective_copy' as const,
                    content: page.effective_copy_examples,
                    title: 'Effective Copy Examples'
                  })
                }
                if (page.ineffective_copy_examples) {
                  evidenceItems.push({
                    type: 'ineffective_copy' as const,
                    content: page.ineffective_copy_examples,
                    title: 'Areas for Improvement'
                  })
                }
                if (page.trust_credibility_assessment) {
                  evidenceItems.push({
                    type: 'trust_assessment' as const,
                    content: page.trust_credibility_assessment,
                    title: 'Trust & Credibility Assessment'
                  })
                }
                if (page.business_impact_analysis) {
                  evidenceItems.push({
                    type: 'business_impact' as const,
                    content: page.business_impact_analysis,
                    title: 'Business Impact Analysis'
                  })
                }
                
                return (
                  <div className="container--section">
                    <h3 className="heading--subsection">🔍 Detailed Analysis: {page.title}</h3>
                    <div className="container--layout">
                      <div className="container--section">
                        <div className="text--display">{page.avgScore.toFixed(1)}/10</div>
                        <div className="text--display">Overall Score</div>
                      </div>
                      <div className="container--section">
                        <div className="text--display">{page.tier}</div>
                        <div className="text--display">Content Tier</div>
                      </div>
                      <div className="container--section">
                        <div className="text--display">{page.personas}</div>
                        <div className="text--display">Personas</div>
                      </div>

                      {page.url && (
                        <div className="container--section">
                          <div className="text--display">
                            <a href={page.url} target="_blank" rel="noopener noreferrer" className="text-info no-underline">
                              🔗 View Page
                            </a>
                          </div>
                          <div className="text--display">External Link</div>
                        </div>
                      )}
                    </div>
                    
                    {evidenceItems.length > 0 && (
                      <div className="spacing--sm">
                        <EvidenceDisplay
                          evidence={evidenceItems}
                          title={`Evidence Analysis for ${page.title}`}
                          collapsible={true}
                          defaultExpanded={true}
                        />
                      </div>
                    )}
                  </div>
                )
              })()}
            </div>
          )}
        </div>
      )}
    </div>
  )
}

function PersonaEvidenceContext({ data }: any) {
  const personas = data.personasForEvidence || []
  const evidenceByPersona = data.evidenceByPersona || {}

  return (
    <div className="container--section">
      <h2 className="heading--section">🧑‍🤝‍🧑 Persona-Specific Evidence Context</h2>
      <div className="grid grid-cols-1 md:grid-cols-2 gap-md">
        {personas.map((persona: string) => (
          <StandardCard
            key={persona}
            title={`Evidence for ${persona}`}
          >
            <p className="text--body">Examples of effective and ineffective copy</p>
            <BarChart
              orientation="h"
              x={[
                evidenceByPersona[persona]?.effective_count || 0,
                evidenceByPersona[persona]?.ineffective_count || 0
              ]}
              y={['Effective', 'Ineffective']}
            />
            <EvidenceDisplay
              title="Effective Copy Examples"
              evidence={evidenceByPersona[persona]?.effective_copy_examples || ''}
            />
            <EvidenceDisplay
              title="Ineffective Copy Examples"
              evidence={evidenceByPersona[persona]?.ineffective_copy_examples || ''}
            />
          </StandardCard>
        ))}
      </div>
    </div>
  )
}

export default ContentMatrix
