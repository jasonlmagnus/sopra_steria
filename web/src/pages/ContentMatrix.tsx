import { useState } from 'react'
import { useQuery } from '@tanstack/react-query'
import { PlotlyChart } from '../components'
import { EvidenceDisplay } from '../components/EvidenceDisplay'

const apiBase = import.meta.env.VITE_API_URL || 'http://localhost:3000'

function ContentMatrix() {
  const [filters, setFilters] = useState({
    persona: 'All',
    tier: 'All',
    minScore: 0,
    performanceLevel: 'All'
  })

  const { data: contentData, isLoading, error } = useQuery({
    queryKey: ['content-matrix', filters],
    queryFn: async () => {
      const params = new URLSearchParams({
        persona: filters.persona,
        tier: filters.tier,
        minScore: filters.minScore.toString(),
        performanceLevel: filters.performanceLevel
      })
      const res = await fetch(`${apiBase}/api/content-matrix?${params}`)
      if (!res.ok) throw new Error('Failed to load content matrix')
      return res.json()
    }
  })

  if (isLoading) return (
    <div>
      <div className="main-header">
        <h1>📊 Content Matrix</h1>
        <p>Loading content analysis...</p>
      </div>
      <div style={{ padding: '2rem', textAlign: 'center' }}>
        <div style={{ 
          border: '2px solid #e2e8f0', 
          borderRadius: '8px', 
          padding: '2rem',
          backgroundColor: '#f8fafc' 
        }}>
          <p>🔄 Updating filters...</p>
        </div>
      </div>
    </div>
  )

  if (error) return (
    <div>
      <div className="main-header">
        <h1>📊 Content Matrix</h1>
        <p>Error loading content analysis</p>
      </div>
      <div style={{ padding: '2rem' }}>
        <div style={{ 
          border: '2px solid #fecaca', 
          borderRadius: '8px', 
          padding: '2rem',
          backgroundColor: '#fef2f2' 
        }}>
          <p>❌ Error: {error.message}</p>
          <p>Please try adjusting your filters or refresh the page.</p>
        </div>
      </div>
    </div>
  )

  const data = contentData || {}
  const filteredContent = data.content || []
  const metrics = data.metrics || {}
  const heatmapData = data.heatmap || {}
  const criteriaData = data.criteria || []
  const pageData = data.pages || []

  // Handle empty data case
  if (data.error || (metrics.totalPages === 0 && filters.minScore > 0)) {
    return (
      <div>
        <div className="main-header">
          <h1>📊 Content Matrix</h1>
          <p>Comprehensive content analysis with performance scoring and strategic insights</p>
        </div>

        {/* Show filters even when no data */}
        <ContentFilters filters={filters} setFilters={setFilters} data={data} />

        <div className="insights-box">
          <h2>📊 No Data Matches Current Filters</h2>
          <div style={{ 
            background: '#fef3c7', 
            borderLeft: '4px solid #f59e0b', 
            padding: '15px', 
            margin: '15px 0', 
            borderRadius: '5px' 
          }}>
            <h4 style={{ margin: 0, color: '#333' }}>⚠️ Filter Results</h4>
            <p style={{ margin: '8px 0', color: '#92400e', fontWeight: 'bold' }}>
              No pages match your current filter criteria
            </p>
            <p style={{ margin: '5px 0' }}>
              <strong>Try:</strong> Lowering the minimum score slider or selecting "All" for other filters
            </p>
          </div>
          
          <div style={{ textAlign: 'center', padding: '2rem' }}>
            <p style={{ fontSize: '1.1rem', color: '#6b7280' }}>
              Current filters: <strong>Persona:</strong> {filters.persona}, <strong>Tier:</strong> {filters.tier}, 
              <strong>Min Score:</strong> {filters.minScore}, <strong>Performance:</strong> {filters.performanceLevel}
            </p>
          </div>
        </div>
      </div>
    )
  }

  return (
    <div>
      <div className="main-header">
        <h1>📊 Content Matrix</h1>
        <p>Comprehensive content analysis with performance scoring and strategic insights</p>
      </div>

      {/* Content Analysis Filters */}
      <ContentFilters filters={filters} setFilters={setFilters} data={data} />

      {/* Performance Overview */}
      <PerformanceOverview metrics={metrics} filteredContent={filteredContent} />

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
    </div>
  )
}

function ContentFilters({ filters, setFilters, data }: any) {
  const personas = ['All', ...(data.personas || [])]
  const tiers = ['All', ...(data.tiers || [])]
  const performanceLevels = ['All', 'Excellent (≥8)', 'Good (6-8)', 'Fair (4-6)', 'Poor (&lt;4)']

  return (
    <div className="insights-box">
      <h2>🎛️ Content Analysis Filters</h2>
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: '1rem' }}>
        <div>
          <label style={{ display: 'block', marginBottom: '0.5rem', fontWeight: '600' }}>
            👥 Persona
          </label>
          <select 
            value={filters.persona}
            onChange={(e) => setFilters({...filters, persona: e.target.value})}
            style={{ 
              width: '100%', 
              padding: '0.5rem', 
              borderRadius: '4px', 
              border: '1px solid #D1D5DB'
            }}
          >
            {personas.map((persona, index) => (
              <option key={`persona-${index}-${persona}`} value={persona}>{persona}</option>
            ))}
          </select>
        </div>

        <div>
          <label style={{ display: 'block', marginBottom: '0.5rem', fontWeight: '600' }}>
            🏗️ Content Tier
          </label>
          <select 
            value={filters.tier}
            onChange={(e) => setFilters({...filters, tier: e.target.value})}
            style={{ 
              width: '100%', 
              padding: '0.5rem', 
              borderRadius: '4px', 
              border: '1px solid #D1D5DB'
            }}
          >
            {tiers.map((tier, index) => (
              <option key={`tier-${index}-${tier}`} value={tier}>{tier}</option>
            ))}
          </select>
        </div>

        <div>
          <label style={{ display: 'block', marginBottom: '0.5rem', fontWeight: '600' }}>
            📊 Min Score: {filters.minScore}
          </label>
          <input 
            type="range"
            min="0"
            max="10"
            step="0.5"
            value={filters.minScore}
            onChange={(e) => setFilters({...filters, minScore: parseFloat(e.target.value)})}
            style={{ width: '100%' }}
          />
        </div>

        <div>
          <label style={{ display: 'block', marginBottom: '0.5rem', fontWeight: '600' }}>
            ⭐ Performance Level
          </label>
          <select 
            value={filters.performanceLevel}
            onChange={(e) => setFilters({...filters, performanceLevel: e.target.value})}
            style={{ 
              width: '100%', 
              padding: '0.5rem', 
              borderRadius: '4px', 
              border: '1px solid #D1D5DB'
            }}
          >
            {performanceLevels.map((level, index) => (
              <option key={`level-${index}-${level}`} value={level}>{level}</option>
            ))}
          </select>
        </div>
      </div>
    </div>
  )
}

function PerformanceOverview({ metrics, filteredContent }: any) {
  const avgScore = metrics.avgScore || 0
  const totalPages = metrics.totalPages || 0
  const poorPerformers = metrics.poorPerformers || 0
  
  let businessImpact = "📊 Content analysis ready"
  let impactColor = "#6c757d"
  
  if (avgScore >= 8) {
    businessImpact = "🚀 Strong content performance across pages"
    impactColor = "#28a745"
  } else if (avgScore >= 6) {
    businessImpact = `⚠️ ${poorPerformers} pages need improvement`
    impactColor = "#fd7e14"
  } else if (avgScore > 0) {
    businessImpact = `🚨 ${poorPerformers} pages require attention`
    impactColor = "#dc3545"
  }

  return (
    <div className="insights-box">
      <h2>📈 Performance Overview</h2>
      
      {/* Business Impact Context */}
      <div style={{ 
        background: '#f8f9fa', 
        borderLeft: `4px solid ${impactColor}`, 
        padding: '15px', 
        margin: '15px 0', 
        borderRadius: '5px' 
      }}>
        <h4 style={{ margin: 0, color: '#333' }}>💡 Content Status</h4>
        <p style={{ margin: '8px 0', color: impactColor, fontWeight: 'bold' }}>{businessImpact}</p>
        <p style={{ margin: '5px 0' }}>
          <strong>Focus:</strong> Prioritize pages scoring below 6.0 for maximum impact
        </p>
      </div>

      {/* Performance Metrics */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: '1rem' }}>
        <div className="metric-card">
          <div className="metric-value">{avgScore.toFixed(1)}</div>
          <div className="metric-label">Average Score</div>
        </div>
        <div className="metric-card">
          <div className="metric-value">{totalPages}</div>
          <div className="metric-label">Total Pages</div>
        </div>
        <div className="metric-card">
          <div className="metric-value">{metrics.excellent || 0}</div>
          <div className="metric-label">Excellent (≥8)</div>
        </div>
        <div className="metric-card">
          <div className="metric-value">{metrics.good || 0}</div>
          <div className="metric-label">Good (6-8)</div>
        </div>
        <div className="metric-card">
          <div className="metric-value">{metrics.fair || 0}</div>
          <div className="metric-label">Fair (4-6)</div>
        </div>
        <div className="metric-card">
          <div className="metric-value">{metrics.poor || 0}</div>
          <div className="metric-label">Poor (&lt;4)</div>
        </div>
      </div>

      {/* Performance Distribution Chart */}
      {(metrics.excellent || metrics.good || metrics.fair || metrics.poor) && (
        <div style={{ marginTop: '2rem' }}>
          <PlotlyChart 
            data={[{
              type: 'pie',
              values: [metrics.excellent || 0, metrics.good || 0, metrics.fair || 0, metrics.poor || 0],
              labels: ['Excellent (≥8)', 'Good (6-8)', 'Fair (4-6)', 'Poor (&lt;4)'],
              marker: { 
                colors: ['#28a745', '#ffc107', '#fd7e14', '#dc3545']
              }
            }]}
            layout={{
              title: 'Performance Distribution',
              height: 400
            }}
          />
        </div>
      )}
    </div>
  )
}

function TierPerformanceAnalysis({ data }: any) {
  const tierData = data.tierAnalysis || []

  return (
    <div className="insights-box">
      <h2>🏗️ Tier Performance Analysis</h2>
      
      <div style={{ 
        background: '#f8f9fa', 
        borderLeft: '4px solid #10b981', 
        padding: '15px', 
        margin: '15px 0', 
        borderRadius: '5px' 
      }}>
        <h4 style={{ margin: 0, color: '#333' }}>💡 Tier Analysis</h4>
        <p style={{ margin: '8px 0' }}>
          Compare performance across content tiers to identify systematic strengths and weaknesses.
        </p>
        <p style={{ margin: '5px 0' }}>
          <strong>Focus:</strong> Tier 1 (Brand) pages should score highest as they represent your core brand.
        </p>
      </div>

      {tierData.length > 0 && (
        <div>
          {/* Tier Performance Cards */}
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(250px, 1fr))', gap: '1rem', marginBottom: '2rem' }}>
            {tierData.map((tier: any) => (
              <div key={tier.tier} className="metric-card">
                <h4>{tier.tier} - {tier.name}</h4>
                <div className="metric-value" style={{ color: tier.avgScore >= 7 ? '#28a745' : tier.avgScore >= 5 ? '#ffc107' : '#dc3545' }}>
                  {tier.avgScore.toFixed(1)}/10
                </div>
                <div className="metric-label">Average Score</div>
                <div style={{ marginTop: '1rem', fontSize: '0.9rem' }}>
                  <strong>{tier.pageCount} pages</strong> • Weight: {(tier.weight * 100).toFixed(0)}%
                </div>
              </div>
            ))}
          </div>

          {/* Tier Comparison Chart */}
          <PlotlyChart 
            data={[{
              type: 'bar',
              x: tierData.map((t: any) => t.tier),
              y: tierData.map((t: any) => t.avgScore),
              marker: { 
                color: tierData.map((t: any) => t.avgScore),
                colorscale: 'RdYlGn',
                cmin: 0,
                cmax: 10
              }
            }]}
            layout={{
              title: 'Average Score by Content Tier',
              xaxis: { title: 'Content Tier' },
              yaxis: { title: 'Average Score' },
              height: 400
            }}
          />
        </div>
      )}
    </div>
  )
}

function ContentHeatmap({ heatmapData }: any) {
  return (
    <div className="insights-box">
      <h2>🔥 Content Performance Heatmap</h2>
      
      <div style={{ 
        background: '#f8f9fa', 
        borderLeft: '4px solid #10b981', 
        padding: '15px', 
        margin: '15px 0', 
        borderRadius: '5px' 
      }}>
        <h4 style={{ margin: 0, color: '#333' }}>💡 Heatmap Analysis</h4>
        <p style={{ margin: '8px 0' }}>
          Use this heatmap to identify patterns of high and low performance.
        </p>
        <p style={{ margin: '5px 0' }}>
          <strong>Focus:</strong> Look for dark red cells to find problem areas and bright green cells for success stories.
        </p>
      </div>

      {heatmapData.matrix && (
        <div>
          <PlotlyChart 
            data={[{
              type: 'heatmap',
              z: heatmapData.matrix,
              x: heatmapData.xLabels || [],
              y: heatmapData.yLabels || [],
              colorscale: 'RdYlGn',
              zmin: 0,
              zmax: 10
            }]}
            layout={{
              title: 'Content Performance Heatmap: Tier × Criteria',
              xaxis: { title: 'Content Tier' },
              yaxis: { title: 'Criteria' },
              height: 600
            }}
          />

          {/* Heatmap Insights */}
          <div style={{ marginTop: '2rem' }}>
            <h3>🔍 Heatmap Insights</h3>
            <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '1rem' }}>
              <div className="insights-box" style={{ background: '#d4edda' }}>
                <strong>🔥 Top Performing Areas:</strong>
                {heatmapData.hotspots?.map((spot: any, idx: number) => (
                  <div key={idx}>• <strong>{spot.tier}</strong> - {spot.criteria}: {spot.score.toFixed(1)}</div>
                ))}
              </div>
              <div className="insights-box" style={{ background: '#fee2e2' }}>
                <strong>❄️ Areas Needing Attention:</strong>
                {heatmapData.coldspots?.map((spot: any, idx: number) => (
                  <div key={idx}>• <strong>{spot.tier}</strong> - {spot.criteria}: {spot.score.toFixed(1)}</div>
                ))}
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}

function CriteriaDeepDive({ criteriaData }: any) {
  return (
    <div className="insights-box">
      <h2>🎯 Criteria Deep Dive</h2>
      
      <div style={{ 
        background: '#f8f9fa', 
        borderLeft: '4px solid #10b981', 
        padding: '15px', 
        margin: '15px 0', 
        borderRadius: '5px' 
      }}>
        <h4 style={{ margin: 0, color: '#333' }}>💡 Criteria Analysis</h4>
        <p style={{ margin: '8px 0' }}>
          Understand which criteria are driving performance up or down.
        </p>
        <p style={{ margin: '5px 0' }}>
          <strong>Focus:</strong> Identify low-scoring criteria to find systemic content issues.
        </p>
      </div>

      {criteriaData.length > 0 && (
        <div>
          {/* Criteria Performance Ranking */}
          <h3>📊 Criteria Performance Ranking</h3>
          <div style={{ overflowX: 'auto' }}>
            <table style={{ width: '100%', borderCollapse: 'collapse' }}>
              <thead>
                <tr style={{ background: '#f8fafc' }}>
                  <th style={{ padding: '1rem', textAlign: 'left', border: '1px solid #D1D5DB' }}>Criteria</th>
                  <th style={{ padding: '1rem', textAlign: 'center', border: '1px solid #D1D5DB' }}>Average Score</th>
                </tr>
              </thead>
              <tbody>
                {criteriaData.map((criteria: any, idx: number) => {
                  const score = criteria.avgScore
                  const bgColor = score >= 8 ? '#d4edda' : score >= 6 ? '#fff3cd' : score >= 4 ? '#fee2e2' : '#f8d7da'
                  return (
                    <tr key={idx}>
                      <td style={{ padding: '1rem', border: '1px solid #D1D5DB' }}>{criteria.name}</td>
                      <td style={{ 
                        padding: '1rem', 
                        textAlign: 'center', 
                        border: '1px solid #D1D5DB',
                        background: bgColor,
                        fontWeight: 'bold'
                      }}>
                        {score.toFixed(1)}
                      </td>
                    </tr>
                  )
                })}
              </tbody>
            </table>
          </div>

          {/* Best and Worst Criteria */}
          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '1rem', marginTop: '2rem' }}>
            <div className="insights-box" style={{ background: '#d4edda' }}>
              <strong>🏆 Top 3 Performing Criteria:</strong>
              {criteriaData.slice(0, 3).map((criteria: any, idx: number) => (
                <div key={idx}>{idx + 1}. <strong>{criteria.name}</strong>: {criteria.avgScore.toFixed(1)}/10</div>
              ))}
            </div>
            <div className="insights-box" style={{ background: '#fee2e2' }}>
              <strong>📉 Bottom 3 Performing Criteria:</strong>
              {criteriaData.slice(-3).reverse().map((criteria: any, idx: number) => (
                <div key={idx}>{idx + 1}. <strong>{criteria.name}</strong>: {criteria.avgScore.toFixed(1)}/10</div>
              ))}
            </div>
          </div>

          {/* Criteria Distribution Chart */}
          <div style={{ marginTop: '2rem' }}>
            <PlotlyChart 
              data={[{
                type: 'bar',
                x: criteriaData.map((c: any) => c.avgScore),
                y: criteriaData.map((c: any) => c.name),
                orientation: 'h',
                marker: { 
                  color: criteriaData.map((c: any) => c.avgScore),
                  colorscale: 'RdYlGn',
                  cmin: 0,
                  cmax: 10
                }
              }]}
              layout={{
                title: 'Criteria Performance Distribution',
                xaxis: { title: 'Average Score' },
                yaxis: { title: 'Criteria' },
                height: Math.max(400, criteriaData.length * 30)
              }}
            />
          </div>
        </div>
      )}
    </div>
  )
}

function PageDrillDown({ pageData }: any) {
  const [selectedPage, setSelectedPage] = useState('')

  return (
    <div className="insights-box">
      <h2>📄 Page Drill-Down</h2>
      
      <div style={{ 
        background: '#f8f9fa', 
        borderLeft: '4px solid #10b981', 
        padding: '15px', 
        margin: '15px 0', 
        borderRadius: '5px' 
      }}>
        <h4 style={{ margin: 0, color: '#333' }}>💡 Page Analysis</h4>
        <p style={{ margin: '8px 0' }}>
          Analyze individual page performance across criteria.
        </p>
        <p style={{ margin: '5px 0' }}>
          <strong>Focus:</strong> Select a page to see its detailed scorecard.
        </p>
      </div>

      {pageData.length > 0 && (
        <div>
          {/* Page Selection */}
          <div style={{ marginBottom: '2rem' }}>
            <label style={{ display: 'block', marginBottom: '0.5rem', fontWeight: '600' }}>
              Select Page for Detailed Analysis:
            </label>
            <select 
              value={selectedPage}
              onChange={(e) => setSelectedPage(e.target.value)}
              style={{ 
                width: '100%', 
                padding: '0.5rem', 
                borderRadius: '4px', 
                border: '1px solid #D1D5DB'
              }}
            >
              <option value="">Choose a page...</option>
              {pageData.map((page: any) => (
                <option key={page.id} value={page.id}>{page.title}</option>
              ))}
            </select>
          </div>

          {/* Page Performance Summary */}
          <h3>📊 Page Performance Summary</h3>
          <div style={{ overflowX: 'auto' }}>
            <table style={{ width: '100%', borderCollapse: 'collapse' }}>
              <thead>
                <tr style={{ background: '#f8fafc' }}>
                  <th style={{ padding: '1rem', textAlign: 'left', border: '1px solid #D1D5DB' }}>Page</th>
                  <th style={{ padding: '1rem', textAlign: 'center', border: '1px solid #D1D5DB' }}>Tier</th>
                  <th style={{ padding: '1rem', textAlign: 'center', border: '1px solid #D1D5DB' }}>Score</th>
                  <th style={{ padding: '1rem', textAlign: 'center', border: '1px solid #D1D5DB' }}>Sentiment</th>
                  <th style={{ padding: '1rem', textAlign: 'center', border: '1px solid #D1D5DB' }}>Engagement</th>
                  <th style={{ padding: '1rem', textAlign: 'center', border: '1px solid #D1D5DB' }}>Conversion</th>
                  <th style={{ padding: '1rem', textAlign: 'center', border: '1px solid #D1D5DB' }}>Personas</th>
                </tr>
              </thead>
              <tbody>
                {pageData.slice(0, 10).map((page: any, idx: number) => {
                  const score = page.avgScore
                  const bgColor = score >= 8 ? '#d4edda' : score >= 6 ? '#fff3cd' : score >= 4 ? '#fee2e2' : '#f8d7da'
                  return (
                    <tr key={idx}>
                      <td style={{ padding: '1rem', border: '1px solid #D1D5DB' }}>{page.title}</td>
                      <td style={{ padding: '1rem', textAlign: 'center', border: '1px solid #D1D5DB' }}>{page.tier}</td>
                      <td style={{ 
                        padding: '1rem', 
                        textAlign: 'center', 
                        border: '1px solid #D1D5DB',
                        background: bgColor,
                        fontWeight: 'bold'
                      }}>
                        {score.toFixed(1)}
                      </td>
                      <td style={{ 
                        padding: '1rem', 
                        textAlign: 'center', 
                        border: '1px solid #D1D5DB',
                        color: (page.overall_sentiment >= 6) ? '#10b981' : (page.overall_sentiment >= 4) ? '#f59e0b' : '#ef4444'
                      }}>
                        {page.overall_sentiment ? page.overall_sentiment.toFixed(1) : 'N/A'}
                      </td>

                      <td style={{ padding: '1rem', textAlign: 'center', border: '1px solid #D1D5DB' }}>{page.personas}</td>
                    </tr>
                  )
                })}
              </tbody>
            </table>
          </div>

          {/* Selected Page Details */}
          {selectedPage && (
            <div style={{ marginTop: '2rem' }}>
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
                  <div className="insights-box">
                    <h3>🔍 Detailed Analysis: {page.title}</h3>
                    <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: '1rem', marginBottom: '2rem' }}>
                      <div className="metric-card">
                        <div className="metric-value">{page.avgScore.toFixed(1)}/10</div>
                        <div className="metric-label">Overall Score</div>
                      </div>
                      <div className="metric-card">
                        <div className="metric-value">{page.tier}</div>
                        <div className="metric-label">Content Tier</div>
                      </div>
                      <div className="metric-card">
                        <div className="metric-value">{page.personas}</div>
                        <div className="metric-label">Personas</div>
                      </div>

                      {page.url && (
                        <div className="metric-card">
                          <div className="metric-value">
                            <a href={page.url} target="_blank" rel="noopener noreferrer" style={{ color: '#3b82f6', textDecoration: 'none' }}>
                              🔗 View Page
                            </a>
                          </div>
                          <div className="metric-label">External Link</div>
                        </div>
                      )}
                    </div>
                    
                    {evidenceItems.length > 0 && (
                      <div style={{ marginTop: '1rem' }}>
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
  const personas = data.personas || []
  const contentData = data.content || []
  
  // Group content by persona for analysis
  const personaContentMap = personas.reduce((acc: any, persona: string) => {
    acc[persona] = contentData.filter((item: any) => item.personas && item.personas.includes(persona))
    return acc
  }, {})

  const getPersonaReactionAnalysis = (persona: string, content: any[]) => {
    const avgScore = content.reduce((sum: number, item: any) => sum + (item.avgScore || 0), 0) / content.length
    
    const effectivePages = content.filter((item: any) => item.effective_copy_examples)
    const trustIssues = content.filter((item: any) => item.trust_credibility_assessment?.includes('concern'))
    const informationGaps = content.filter((item: any) => item.information_gaps)
    
    return {
      avgScore,
      effectivePages,
      trustIssues,
      informationGaps,
      contentCount: content.length
    }
  }

  return (
    <div className="insights-box">
      <h2>👥 Persona-Specific Evidence Context</h2>
      
      <div style={{ 
        background: '#f8f9fa', 
        borderLeft: '4px solid #6366f1', 
        padding: '15px', 
        margin: '15px 0', 
        borderRadius: '5px' 
      }}>
        <h4 style={{ margin: 0, color: '#333' }}>💡 Persona Content Analysis</h4>
        <p style={{ margin: '8px 0' }}>
          Understand how each persona reacts to your content based on evidence from user experience data.
        </p>
        <p style={{ margin: '5px 0' }}>
          <strong>Focus:</strong> Identify content that resonates with specific personas and address persona-specific pain points.
        </p>
      </div>

      {personas.length > 0 && (
        <div className="persona-evidence-grid" style={{ display: 'grid', gap: '2rem' }}>
          {personas.map((persona: string) => {
            const personaContent = personaContentMap[persona] || []
            const analysis = getPersonaReactionAnalysis(persona, personaContent)
            
            return (
              <div key={persona} className="persona-evidence-card" style={{ 
                border: '1px solid #e2e8f0', 
                borderRadius: '12px', 
                padding: '1.5rem',
                backgroundColor: '#ffffff'
              }}>
                <div className="persona-header" style={{ marginBottom: '1.5rem' }}>
                  <h3 style={{ margin: 0, color: '#1f2937', display: 'flex', alignItems: 'center' }}>
                    👤 {persona}
                    <span style={{ 
                      marginLeft: '1rem', 
                      fontSize: '0.875rem', 
                      color: '#6b7280',
                      backgroundColor: '#f3f4f6',
                      padding: '0.25rem 0.75rem',
                      borderRadius: '9999px'
                    }}>
                      {analysis.contentCount} pages
                    </span>
                  </h3>
                </div>

                {/* Persona Performance Overview */}
                <div className="persona-metrics" style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(150px, 1fr))', gap: '1rem', marginBottom: '1.5rem' }}>
                  <div className="metric-card" style={{ textAlign: 'center' }}>
                    <div className="metric-value" style={{ 
                      color: analysis.avgScore >= 7 ? '#10b981' : analysis.avgScore >= 5 ? '#f59e0b' : '#ef4444' 
                    }}>
                      {analysis.avgScore.toFixed(1)}
                    </div>
                    <div className="metric-label">Avg Score</div>
                  </div>
                </div>

                {/* Evidence-Based Insights */}
                <div className="persona-insights" style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(300px, 1fr))', gap: '1rem' }}>
                  
                  {/* What Works for This Persona */}
                  <div className="insight-section" style={{ 
                    padding: '1rem', 
                    border: '1px solid #d1f2eb', 
                    borderRadius: '8px', 
                    backgroundColor: '#f0fdfa' 
                  }}>
                    <h4 style={{ color: '#047857', margin: '0 0 0.75rem 0' }}>✅ What Works</h4>
                    {analysis.effectivePages.length > 0 ? (
                      <div>
                        {analysis.effectivePages.slice(0, 3).map((page: any, idx: number) => (
                          <div key={idx} style={{ marginBottom: '0.75rem' }}>
                            <div style={{ fontSize: '0.875rem', fontWeight: '500' }}>
                              {page.title || 'Page'}
                            </div>
                            <div style={{ fontSize: '0.75rem', color: '#6b7280', fontStyle: 'italic' }}>
                              "{page.effective_copy_examples?.substring(0, 100) || 'Strong content performance'}..."
                            </div>
                          </div>
                        ))}
                      </div>
                    ) : (
                      <p style={{ color: '#6b7280', fontSize: '0.875rem', margin: 0 }}>
                        No specific effective examples found for this persona yet.
                      </p>
                    )}
                  </div>

                  {/* Pain Points & Trust Issues */}
                  <div className="insight-section" style={{ 
                    padding: '1rem', 
                    border: '1px solid #fecaca', 
                    borderRadius: '8px', 
                    backgroundColor: '#fef2f2' 
                  }}>
                    <h4 style={{ color: '#dc2626', margin: '0 0 0.75rem 0' }}>⚠️ Pain Points</h4>
                    {analysis.trustIssues.length > 0 || analysis.informationGaps.length > 0 ? (
                      <div>
                        {analysis.trustIssues.slice(0, 2).map((page: any, idx: number) => (
                          <div key={idx} style={{ marginBottom: '0.75rem' }}>
                            <div style={{ fontSize: '0.875rem', fontWeight: '500' }}>
                              Trust Issue: {page.title || 'Page'}
                            </div>
                            <div style={{ fontSize: '0.75rem', color: '#6b7280' }}>
                              {page.trust_credibility_assessment?.substring(0, 100) || 'Trust concerns identified'}...
                            </div>
                          </div>
                        ))}
                        {analysis.informationGaps.slice(0, 2).map((page: any, idx: number) => (
                          <div key={idx} style={{ marginBottom: '0.75rem' }}>
                            <div style={{ fontSize: '0.875rem', fontWeight: '500' }}>
                              Info Gap: {page.title || 'Page'}
                            </div>
                            <div style={{ fontSize: '0.75rem', color: '#6b7280' }}>
                              {page.information_gaps?.substring(0, 100) || 'Information gaps identified'}...
                            </div>
                          </div>
                        ))}
                      </div>
                    ) : (
                      <p style={{ color: '#6b7280', fontSize: '0.875rem', margin: 0 }}>
                        No major pain points identified for this persona.
                      </p>
                    )}
                  </div>
                </div>

                {/* Persona-Specific Recommendations */}
                <div className="persona-recommendations" style={{ 
                  marginTop: '1.5rem', 
                  padding: '1rem', 
                  backgroundColor: '#f8fafc', 
                  borderRadius: '8px' 
                }}>
                  <h4 style={{ margin: '0 0 1rem 0', color: '#374151' }}>🎯 Persona-Specific Recommendations</h4>
                  <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(250px, 1fr))', gap: '1rem' }}>
                    <div>
                      <strong style={{ color: '#059669' }}>Amplify:</strong>
                      <ul style={{ margin: '0.5rem 0', paddingLeft: '1.25rem' }}>
                        {analysis.effectivePages.length > 0 ? (
                          <li>Apply successful copy patterns from high-performing pages</li>
                        ) : (
                          <li>Test different messaging approaches for this persona</li>
                        )}
                        <li>Focus on improving content engagement and user experience</li>
                      </ul>
                    </div>
                    <div>
                      <strong style={{ color: '#dc2626' }}>Address:</strong>
                      <ul style={{ margin: '0.5rem 0', paddingLeft: '1.25rem' }}>
                        {analysis.trustIssues.length > 0 && <li>Resolve trust and credibility concerns</li>}
                        {analysis.informationGaps.length > 0 && <li>Fill information gaps that block conversions</li>}
                        <li>Optimize conversion paths for this persona</li>
                      </ul>
                    </div>
                  </div>
                </div>
              </div>
            )
          })}
        </div>
      )}

      {personas.length === 0 && (
        <div style={{ textAlign: 'center', padding: '2rem', color: '#6b7280' }}>
          <p>No persona data available for analysis.</p>
          <p>Please ensure your content data includes persona information.</p>
        </div>
      )}
    </div>
  )
}

export default ContentMatrix
