import { useState } from 'react'
import { useQuery } from '@tanstack/react-query'
import { PlotlyChart } from '../components'

const apiBase = import.meta.env.VITE_API_URL || 'http://localhost:3000'

function ContentMatrix() {
  const [filters, setFilters] = useState({
    persona: 'All',
    tier: 'All',
    minScore: 0,
    performanceLevel: 'All'
  })

  const { data: contentData, isLoading } = useQuery({
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

  if (isLoading) return <div className="main-header"><h1>📊 Content Matrix</h1><p>Loading content analysis...</p></div>

  const data = contentData || {}
  const filteredContent = data.content || []
  const metrics = data.metrics || {}
  const heatmapData = data.heatmap || {}
  const criteriaData = data.criteria || []
  const pageData = data.pages || []

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
            {personas.map(persona => (
              <option key={persona} value={persona}>{persona}</option>
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
            {tiers.map(tier => (
              <option key={tier} value={tier}>{tier}</option>
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
            {performanceLevels.map(level => (
              <option key={level} value={level}>{level}</option>
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
                
                return (
                  <div className="insights-box">
                    <h3>🔍 Detailed Analysis: {page.title}</h3>
                    <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: '1rem' }}>
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
                    </div>
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

export default ContentMatrix
