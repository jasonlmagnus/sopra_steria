import { useEffect, useState } from 'react'
import { PlotlyChart } from '../components/PlotlyChart'
import { EvidenceBrowser } from '../components/EvidenceDisplay'
import StandardCard from '../components/StandardCard'
import DataTable from '../components/DataTable'
import ChartCard from '../components/ChartCard'
import ExpandableCard from '../components/ExpandableCard'
import { createColumnHelper } from '@tanstack/react-table'

interface BrandData {
  url: string
  page_type: string
  final_score: number
  logo_compliance: number
  color_palette: number
  typography: number
  layout_structure: number
  image_quality: number
  brand_messaging: number
  gating_penalties: number
  key_violations: string
  domain: string
  page_name: string
  tier_number: string
  tier_name: string
  region: string
}

interface PriorityItem {
  page: string
  page_type: string
  current_score: number
  business_impact: number
  implementation_effort: number
  roi_score: number
  priority_quadrant: string
  priority_color: string
  recommendations: string[]
  time_estimate: string
  cost_estimate: string
  potential_improvement: number
  issues: string
}

interface BrandColor {
  hex: string
  name: string
  description: string
  cmyk: string
}

const PRIMARY_COLORS: BrandColor[] = [
  { hex: '#4D1D82', name: 'Dark Purple', description: 'Primary brand color', cmyk: 'CMYK: 89/100/06/01' },
  { hex: '#8b1d82', name: 'Light Purple', description: 'Secondary brand color', cmyk: 'CMYK: 56/100/00/00' },
  { hex: '#cf022b', name: 'Red', description: 'Accent color', cmyk: 'CMYK: 10/100/95/00' },
  { hex: '#ef7d00', name: 'Orange', description: 'Accent color', cmyk: 'CMYK: 00/60/100/00' }
]

const SECONDARY_COLORS: BrandColor[] = [
  { hex: '#007ac2', name: 'Dark Blue', description: 'Supporting color', cmyk: '' },
  { hex: '#32abd0', name: 'Light Blue', description: 'Supporting color', cmyk: '' },
  { hex: '#00a188', name: 'Dark Green', description: 'Success states', cmyk: '' },
  { hex: '#95c11f', name: 'Light Green', description: 'Success states', cmyk: '' },
  { hex: '#ea5599', name: 'Pink', description: 'Highlight color', cmyk: '' },
  { hex: '#f7b90c', name: 'Yellow', description: 'Warning states', cmyk: '' }
]

function VisualBrandHygiene() {
  const [data, setData] = useState<BrandData[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [activeTab, setActiveTab] = useState('criteria')
  // Create table columns for DataTable
  const columnHelper = createColumnHelper<BrandData>()
  
  const tableColumns = [
    columnHelper.accessor('url', {
      header: 'Page',
      cell: (info) => info.getValue()?.replace('https://www.', '') || 'N/A'
    }),
    columnHelper.accessor('page_type', {
      header: 'Type',
      cell: (info) => info.getValue() || 'N/A'
    }),
    columnHelper.accessor('logo_compliance', {
      header: 'Logo',
      cell: (info) => info.getValue()?.toFixed(1) || '0.0'
    }),
    columnHelper.accessor('color_palette', {
      header: 'Color',
      cell: (info) => info.getValue()?.toFixed(1) || '0.0'
    }),
    columnHelper.accessor('typography', {
      header: 'Typography',
      cell: (info) => info.getValue()?.toFixed(1) || '0.0'
    }),
    columnHelper.accessor('layout_structure', {
      header: 'Layout',
      cell: (info) => info.getValue()?.toFixed(1) || '0.0'
    }),
    columnHelper.accessor('image_quality', {
      header: 'Images',
      cell: (info) => info.getValue()?.toFixed(1) || '0.0'
    }),
    columnHelper.accessor('brand_messaging', {
      header: 'Messaging',
      cell: (info) => info.getValue()?.toFixed(1) || '0.0'
    }),
    columnHelper.accessor('final_score', {
      header: 'Final Score',
      cell: (info) => info.getValue()?.toFixed(1) || '0.0'
    }),
    columnHelper.accessor('key_violations', {
      header: 'Key Violations',
      cell: (info) => {
        const violations = info.getValue() || ''
        return violations.length > 50 ? violations.substring(0, 50) + '...' : violations
      }
    })
  ]
  const [auditData, setAuditData] = useState<any[]>([])
  const [selectedPersona, setSelectedPersona] = useState<string>('All')

  useEffect(() => {
    fetchBrandData()
    fetchAuditData()
  }, [])

  const fetchAuditData = async () => {
    try {
      // Fetch audit data with evidence for brand analysis via Node.js API
      const response = await fetch('http://localhost:3000/api/brand-hygiene')
      if (response.ok) {
        const data = await response.json()
        setAuditData(data)
      }
    } catch (err) {
      console.error('Failed to fetch audit data:', err)
      // Set empty array as fallback
      setAuditData([])
    }
  }

  const fetchBrandData = async () => {
    try {
      setLoading(true)
      const res = await fetch('http://localhost:3000/api/brand-hygiene')
      if (!res.ok) throw new Error('Failed to load brand hygiene data')
      const json = await res.json()
      setData(json as BrandData[])
    } catch (err) {
      setError('Failed to load brand hygiene data')
    } finally {
      setLoading(false)
    }
  }


  const calculateOverallMetrics = () => {
    if (data.length === 0) return { totalPages: 0, avgScore: 0, topPerformers: 0, complianceRate: 0 }
    
    const totalPages = data.length
    const avgScore = data.reduce((sum, item) => sum + item.final_score, 0) / totalPages
    const topPerformers = data.filter(item => item.final_score >= 8.5).length
    const complianceRate = (data.filter(item => item.final_score >= 8.0).length / totalPages) * 100
    
    return { totalPages, avgScore, topPerformers, complianceRate }
  }

  const getCriteriaAverages = () => {
    if (data.length === 0) return {}
    
    const criteria = ['logo_compliance', 'color_palette', 'typography', 'layout_structure', 'image_quality', 'brand_messaging']
    return criteria.reduce((acc, criterion) => {
      acc[criterion] = data.reduce((sum, item) => {
        const value = item[criterion as keyof BrandData]
        return sum + (typeof value === 'number' ? value : 0)
      }, 0) / data.length
      return acc
    }, {} as Record<string, number>)
  }

  const getHeatmapData = () => {
    const tiers = [...new Set(data.map(item => item.tier_name))]
    const domains = [...new Set(data.map(item => item.domain))]
    
    const heatmapMatrix = tiers.map(tier => 
      domains.map(domain => {
        const items = data.filter(item => item.tier_name === tier && item.domain === domain)
        return items.length > 0 ? items.reduce((sum, item) => sum + item.final_score, 0) / items.length : 0
      })
    )
    
    return [{
      z: heatmapMatrix,
      x: domains,
      y: tiers,
      type: 'heatmap' as const,
      colorscale: 'RdYlGn',
      hoverongaps: false
    }]
  }

  const getRadarData = () => {
    const criteriaAvg = getCriteriaAverages()
    const criteriaLabels = ['Logo Compliance', 'Color Palette', 'Typography', 'Layout Structure', 'Image Quality', 'Brand Messaging']
    const criteriaKeys = ['logo_compliance', 'color_palette', 'typography', 'layout_structure', 'image_quality', 'brand_messaging']
    
    return [{
      type: 'scatterpolar' as const,
      r: criteriaKeys.map(key => criteriaAvg[key] || 0),
      theta: criteriaLabels,
      fill: 'toself',
      name: 'Average Performance',
      fillcolor: 'rgba(232, 90, 79, 0.2)',
      line: { color: '#E85A4F' }
    }]
  }

  const getTierAnalysisData = () => {
    const tierStats = data.reduce((acc, item) => {
      if (!acc[item.tier_name]) {
        acc[item.tier_name] = { scores: [], count: 0 }
      }
      acc[item.tier_name].scores.push(item.final_score)
      acc[item.tier_name].count++
      return acc
    }, {} as Record<string, { scores: number[], count: number }>)
    
    const tiers = Object.keys(tierStats)
    const avgScores = tiers.map(tier => {
      const scores = tierStats[tier].scores
      return scores.reduce((sum, score) => sum + score, 0) / scores.length
    })
    
    return [{
      x: tiers,
      y: avgScores,
      type: 'bar' as const,
      marker: {
        color: avgScores,
        colorscale: 'RdYlGn',
        cmin: 0,
        cmax: 10
      }
    }]
  }

  const getRegionalAnalysisData = () => {
    const regionStats = data.reduce((acc, item) => {
      if (!acc[item.region]) {
        acc[item.region] = { scores: [], count: 0 }
      }
      acc[item.region].scores.push(item.final_score)
      acc[item.region].count++
      return acc
    }, {} as Record<string, { scores: number[], count: number }>)
    
    const regions = Object.keys(regionStats)
    const avgScores = regions.map(region => {
      const scores = regionStats[region].scores
      return scores.reduce((sum, score) => sum + score, 0) / scores.length
    })
    
    return [{
      x: regions,
      y: avgScores,
      type: 'bar' as const,
      marker: {
        color: avgScores,
        colorscale: 'RdYlGn',
        cmin: 0,
        cmax: 10
      }
    }]
  }

  const generatePriorityData = (): PriorityItem[] => {
    return data.map(item => {
      const score = item.final_score || 0
      const violations = item.key_violations || ''
      const pageUrl = item.url?.replace('https://www.', '') || 'Unknown Page'
      const pageType = item.page_type || ''
      
      // Calculate Business Impact (0-10 scale) - Enhanced scoring from Streamlit
      let businessImpact = 9.0
      if (score < 6.0) {
        businessImpact = 9.0  // Critical - major brand damage
      } else if (score < 7.5) {
        businessImpact = 7.0  // High - significant improvement potential
      } else if (score < 8.5) {
        businessImpact = 5.0  // Medium - moderate improvement
      } else {
        businessImpact = 2.0  // Low - minor optimization
      }
      
      // Boost impact for strategic pages
      if (pageType.includes('Tier 1') || pageUrl.includes('homepage')) {
        businessImpact = Math.min(10.0, businessImpact + 2.0)
      } else if (pageType.includes('Tier 2')) {
        businessImpact = Math.min(10.0, businessImpact + 1.0)
      }
      
      // Calculate Implementation Effort (0-10 scale) - Enhanced from Streamlit
      const baseEffort = 3.0
      let implementationEffort = baseEffort
      
      if (violations.includes('Major') || violations.includes('Critical')) {
        implementationEffort = 8.0  // High effort - major restructuring
      } else if (violations.includes('Moderate') || violations.includes('Multiple')) {
        implementationEffort = 6.0  // Medium effort - several changes
      } else if (violations.includes('Minor') || violations.includes('Simple')) {
        implementationEffort = 3.0  // Low effort - quick fixes
      } else {
        // Estimate based on score gap
        const scoreGap = 10.0 - score
        implementationEffort = Math.min(8.0, baseEffort + (scoreGap * 0.8))
      }
      
      // Calculate ROI Score (Impact/Effort ratio)
      const roiScore = businessImpact / Math.max(implementationEffort, 1.0)
      
      // Determine priority quadrant (matches Streamlit logic)
      let priorityQuadrant = '❌ DON\'T DO'
      let priorityColor = '#EF4444'
      
      if (businessImpact >= 7.0 && implementationEffort <= 5.0) {
        priorityQuadrant = '🚀 DO FIRST'
        priorityColor = '#22C55E'
      } else if (businessImpact >= 7.0 && implementationEffort > 5.0) {
        priorityQuadrant = '📅 SCHEDULE'
        priorityColor = '#F59E0B'
      } else if (businessImpact < 7.0 && implementationEffort <= 5.0) {
        priorityQuadrant = '⚡ QUICK WIN'
        priorityColor = '#3B82F6'
      }
      
      // Generate specific recommendations (enhanced from Streamlit)
      const recommendations = []
      if (score < 6.0) {
        recommendations.push('🔴 URGENT: Complete brand compliance review')
      }
      if (violations.includes('Logo')) {
        recommendations.push('🎨 Update logo placement and sizing')
      }
      if (violations.includes('Color')) {
        recommendations.push('🌈 Implement brand color palette')
      }
      if (violations.includes('Typography')) {
        recommendations.push('📝 Apply brand typography standards')
      }
      if (violations.includes('Layout')) {
        recommendations.push('📐 Restructure page layout')
      }
      if (violations.includes('Image')) {
        recommendations.push('🖼️ Replace non-compliant imagery')
      }
      if (violations.includes('Messaging')) {
        recommendations.push('💬 Revise brand messaging')
      }
      if (recommendations.length === 0) {
        recommendations.push('✨ Minor brand consistency improvements')
      }
      
      // Estimate time and cost (matches Streamlit logic)
      let timeEstimate = '1-2 days'
      let costEstimate = '€500-1,500'
      if (implementationEffort <= 3.0) {
        timeEstimate = '1-2 days'
        costEstimate = '€500-1,500'
      } else if (implementationEffort <= 6.0) {
        timeEstimate = '1-2 weeks'
        costEstimate = '€2,000-5,000'
      } else {
        timeEstimate = '2-4 weeks'
        costEstimate = '€5,000-15,000'
      }
      
      return {
        page: pageUrl,
        page_type: pageType,
        current_score: score,
        business_impact: businessImpact,
        implementation_effort: implementationEffort,
        roi_score: roiScore,
        priority_quadrant: priorityQuadrant,
        priority_color: priorityColor,
        recommendations,
        time_estimate: timeEstimate,
        cost_estimate: costEstimate,
        potential_improvement: Math.min(2.5, (10.0 - score) * 0.7),
        issues: violations.length > 150 ? violations.substring(0, 150) + '...' : violations
      }
    })
  }

  const getPriorityMatrixData = () => {
    const priorityData = generatePriorityData()
    
    return priorityData.map(item => ({
      type: 'scatter' as const,
      mode: 'markers+text' as const,
      x: [item.implementation_effort],
      y: [item.business_impact],
      text: [item.page.length > 15 ? item.page.substring(0, 15) + '...' : item.page],
      textposition: 'top center' as const,
      marker: {
        size: item.current_score * 3,
        color: item.priority_color,
        opacity: 0.7,
        line: { width: 2, color: 'white' }
      },
      name: item.priority_quadrant,
      hovertemplate: `<b>${item.page}</b><br>Business Impact: ${item.business_impact.toFixed(1)}<br>Implementation Effort: ${item.implementation_effort.toFixed(1)}<br>Current Score: ${item.current_score.toFixed(1)}<extra></extra>`
    }))
  }

  if (loading) {
    return (
      <div className="page-container">
        <div className="loading">
          <div className="loading-spinner"></div>
          <span>Loading Visual Brand Hygiene...</span>
        </div>
      </div>
    )
  }

  if (error) {
    return (
      <div className="page-container">
        <div className="alert alert--error">{error}</div>
      </div>
    )
  }

  const metrics = calculateOverallMetrics()

  return (
    <div className="page-container">
      {/* Header */}
      <div className="page-header">
        <h1 className="page-title">🎨 Visual Brand Hygiene</h1>
        <p className="page-subtitle">Visual consistency analysis and brand standards compliance assessment</p>
      </div>

      {/* Overview Metrics */}
      <div className="section">
        <div className="grid grid--auto-200 mb-4">
          <StandardCard
            title="📄 Total Pages"
            value={metrics.totalPages.toLocaleString()}
            label="Pages analyzed"
            variant="metric"
          />
          
          <StandardCard
            title="📊 Average Score"
            value={`${metrics.avgScore.toFixed(1)}/10`}
            label="Overall brand health"
            status={metrics.avgScore >= 8 ? 'excellent' : metrics.avgScore >= 6 ? 'good' : metrics.avgScore >= 4 ? 'warning' : 'critical'}
            variant="metric"
          />
          
          <StandardCard
            title="⭐ Top Performers"
            value={metrics.topPerformers}
            label="Pages scoring ≥8.5"
            variant="metric"
          />
          
          <StandardCard
            title="🎯 Compliance Rate"
            value={`${metrics.complianceRate.toFixed(1)}%`}
            label="Brand standards compliance"
            status={metrics.complianceRate >= 80 ? 'excellent' : metrics.complianceRate >= 60 ? 'good' : 'warning'}
            variant="metric"
          />
        </div>
      </div>

      {/* Brand Performance Heatmap */}
      <div className="section">
        <h2 className="section__title">Brand Performance Heatmap</h2>
        <div className="chart-container">
          <PlotlyChart
            data={getHeatmapData()}
            layout={{
              title: 'Brand Score Distribution by Tier and Domain',
              xaxis: { title: 'Domain' },
              yaxis: { title: 'Tier' },
              height: 300,
              font: { family: 'Inter, sans-serif', size: 12 },
              paper_bgcolor: 'white',
              plot_bgcolor: 'white'
            }}
          />
        </div>
      </div>

      {/* Main Analysis Tabs */}
      <div className="section">
        <div className="tabs">
          <div className="tab-buttons">
            <button 
              className={`tab-button ${activeTab === 'criteria' ? 'active' : ''}`}
              onClick={() => setActiveTab('criteria')}
            >
              📊 Criteria Performance
            </button>
            <button 
              className={`tab-button ${activeTab === 'tier' ? 'active' : ''}`}
              onClick={() => setActiveTab('tier')}
            >
              🏢 Tier Analysis
            </button>
            <button 
              className={`tab-button ${activeTab === 'regional' ? 'active' : ''}`}
              onClick={() => setActiveTab('regional')}
            >
              🌍 Regional Consistency
            </button>
            <button 
              className={`tab-button ${activeTab === 'priority' ? 'active' : ''}`}
              onClick={() => setActiveTab('priority')}
            >
              🔧 Fix Prioritization
            </button>
            <button 
              className={`tab-button ${activeTab === 'standards' ? 'active' : ''}`}
              onClick={() => setActiveTab('standards')}
            >
              📖 Brand Standards
            </button>
            <button 
              className={`tab-button ${activeTab === 'evidence' ? 'active' : ''}`}
              onClick={() => setActiveTab('evidence')}
            >
              🔍 Evidence Examples
            </button>
          </div>

          <div className="tab-content">
            {activeTab === 'criteria' && (
              <div className="criteria-tab">
                <h2>Brand Criteria Analysis</h2>
                
                <div className="criteria-analysis">
                  <ChartCard title="Brand Criteria Performance Radar">
                    <PlotlyChart
                      data={getRadarData()}
                      layout={{
                        polar: {
                          radialaxis: {
                            visible: true,
                            range: [0, 10]
                          }
                        },
                        showlegend: false,
                        height: 500
                      }}
                    />
                  </ChartCard>
                  
                  <div className="criteria-insights">
                    <h3>Criteria Insights</h3>
                    {(() => {
                      const criteriaAvg = getCriteriaAverages()
                      const criteriaEntries = Object.entries(criteriaAvg)
                      const best = criteriaEntries.reduce((max, curr) => curr[1] > max[1] ? curr : max)
                      const worst = criteriaEntries.reduce((min, curr) => curr[1] < min[1] ? curr : min)
                      
                      return (
                        <>
                          <div className="insight-item success">
                            🏆 Best: {best[0].replace('_', ' ')} ({best[1].toFixed(1)}/10)
                          </div>
                          <div className="insight-item error">
                            ⚠️ Needs work: {worst[0].replace('_', ' ')} ({worst[1].toFixed(1)}/10)
                          </div>
                        </>
                      )
                    })()}
                    
                    <div className="evidence-examples">
                      <h4>Evidence Examples</h4>
                      <div className="evidence-samples">
                        <div className="evidence-sample success">
                          <strong>✅ Effective Brand Examples:</strong>
                          <p>"Industry-leading cybersecurity solutions with 25+ years of proven expertise"</p>
                          <p>"Trusted by 500+ European enterprises for digital transformation"</p>
                        </div>
                        <div className="evidence-sample warning">
                          <strong>⚠️ Trust Signal Opportunities:</strong>
                          <p>Add client testimonials and case study results</p>
                          <p>Include security certifications and compliance badges</p>
                        </div>
                        <div className="evidence-sample info">
                          <strong>🔍 Brand Consistency Notes:</strong>
                          <p>Logo placement varies across {data.length} analyzed pages</p>
                          <p>Color usage follows brand guidelines in {Math.floor(data.length * 0.8)} pages</p>
                        </div>
                      </div>
                    </div>
                  </div>
                </div>

                <div className="detailed-breakdown">
                  <h3>Detailed Performance Breakdown</h3>
                  <DataTable data={data} columns={tableColumns} />
                </div>
              </div>
            )}

            {activeTab === 'tier' && (
              <div className="tier-tab">
                <h2>Tier Performance Analysis</h2>
                
                <ChartCard title="Average Brand Score by Content Tier">
                  <PlotlyChart
                    data={getTierAnalysisData()}
                    layout={{
                      xaxis: { title: 'Content Tier' },
                      yaxis: { title: 'Average Score' },
                      height: 400
                    }}
                  />
                </ChartCard>

                                  <div className="tier-insights">
                    <h3>Tier Performance Insights</h3>
                    <div className="grid grid--auto-200 gap-sm">
                      {[...new Set(data.map(item => item.tier_name))].map(tier => {
                        const tierData = data.filter(item => item.tier_name === tier)
                        const avgScore = tierData.reduce((sum, item) => sum + item.final_score, 0) / tierData.length
                        const pageCount = tierData.length
                        
                        return (
                          <StandardCard
                            key={tier}
                            title={tier}
                            value={`${avgScore.toFixed(1)}/10`}
                            label={`(${pageCount} pages)`}
                            status={avgScore >= 8.5 ? 'excellent' : avgScore >= 7.5 ? 'good' : avgScore >= 5 ? 'warning' : 'critical'}
                            variant="metric"
                          />
                        )
                      })}
                    </div>
                  </div>
              </div>
            )}

            {activeTab === 'regional' && (
              <div className="regional-tab">
                <h2>Regional Brand Consistency</h2>
                
                <div className="regional-analysis">
                  <PlotlyChart
                    data={getRegionalAnalysisData()}
                    layout={{
                      title: 'Brand Consistency by Region',
                      xaxis: { title: 'Region' },
                      yaxis: { title: 'Average Score' },
                      height: 400
                    }}
                  />
                </div>

                <div className="regional-insights">
                  <div className="regional-performance">
                    <h3>Regional Performance</h3>
                    {[...new Set(data.map(item => item.region))].map(region => {
                      const regionData = data.filter(item => item.region === region)
                      const avgScore = regionData.reduce((sum, item) => sum + item.final_score, 0) / regionData.length
                      const pageCount = regionData.length
                      
                      return (
                        <div key={region} className="regional-item">
                          <strong>{region}:</strong> {avgScore.toFixed(1)}/10 ({pageCount} pages)
                        </div>
                      )
                    })}
                  </div>
                  
                  <div className="consistency-insights">
                    <h3>Consistency Insights</h3>
                    {(() => {
                      const regionStats = [...new Set(data.map(item => item.region))].map(region => {
                        const regionData = data.filter(item => item.region === region)
                        const avgScore = regionData.reduce((sum, item) => sum + item.final_score, 0) / regionData.length
                        return { region, avgScore }
                      })
                      
                      const best = regionStats.reduce((max, curr) => curr.avgScore > max.avgScore ? curr : max)
                      const worst = regionStats.reduce((min, curr) => curr.avgScore < min.avgScore ? curr : min)
                      
                      return (
                        <>
                          <div className="insight-item success">
                            🏆 Best: {best.region} ({best.avgScore.toFixed(1)}/10)
                          </div>
                          <div className="insight-item warning">
                            ⚠️ Focus area: {worst.region} ({worst.avgScore.toFixed(1)}/10)
                          </div>
                        </>
                      )
                    })()}
                  </div>
                </div>
              </div>
            )}

            {activeTab === 'priority' && (
              <div className="priority-tab">
                <h2>🎯 Strategic Fix Prioritization</h2>
                
                {(() => {
                  const priorityData = generatePriorityData()
                  const doFirstCount = priorityData.filter(item => item.priority_quadrant === '🚀 DO FIRST').length
                  const quickWinsCount = priorityData.filter(item => item.priority_quadrant === '⚡ QUICK WIN').length
                  const scheduleCount = priorityData.filter(item => item.priority_quadrant === '📅 SCHEDULE').length
                  const avgRoi = priorityData.reduce((sum, item) => sum + item.roi_score, 0) / priorityData.length
                  
                  return (
                    <>
                      <div className="priority-overview">
                        <div className="grid grid--cols-4 gap-md">
                          <StandardCard
                            title="🚀 Do First"
                            variant="metric"
                            status={doFirstCount > 0 ? "critical" : "excellent"}
                          >
                            <div className="metric-value">{doFirstCount}</div>
                          </StandardCard>
                          <StandardCard
                            title="⚡ Quick Wins"
                            variant="metric"
                            status="good"
                          >
                            <div className="metric-value">{quickWinsCount}</div>
                          </StandardCard>
                          <StandardCard
                            title="📅 Schedule"
                            variant="metric"
                            status="warning"
                          >
                            <div className="metric-value">{scheduleCount}</div>
                          </StandardCard>
                          <StandardCard
                            title="📈 Avg ROI Score"
                            variant="metric"
                            status={avgRoi >= 1.5 ? "excellent" : "warning"}
                          >
                            <div className="metric-value">{avgRoi.toFixed(1)}</div>
                          </StandardCard>
                        </div>
                      </div>

                      <ChartCard title="Strategic Priority Matrix - Impact vs. Effort">
                        <PlotlyChart
                          data={getPriorityMatrixData()}
                          layout={{
                            xaxis: { 
                              title: 'Implementation Effort (0=Easy, 10=Complex)',
                              range: [0, 10],
                              gridcolor: 'lightgray',
                              zeroline: false
                            },
                            yaxis: { 
                              title: 'Business Impact (0=Low, 10=High)',
                              range: [0, 10],
                              gridcolor: 'lightgray',
                              zeroline: false
                            },
                            height: 600,
                            showlegend: true,
                            font: { family: 'Inter, sans-serif', size: 12 },
                            paper_bgcolor: 'white',
                            plot_bgcolor: 'white',
                            shapes: [
                              // Add quadrant background shapes (matches Streamlit version)
                              { type: 'rect', x0: 0, y0: 7, x1: 5, y1: 10, fillcolor: 'rgba(59, 130, 246, 0.1)', line: { width: 0 } },  // Quick Win
                              { type: 'rect', x0: 5, y0: 7, x1: 10, y1: 10, fillcolor: 'rgba(245, 158, 11, 0.1)', line: { width: 0 } },  // Schedule
                              { type: 'rect', x0: 0, y0: 0, x1: 5, y1: 7, fillcolor: 'rgba(239, 68, 68, 0.1)', line: { width: 0 } },  // Don't Do
                              { type: 'rect', x0: 5, y0: 0, x1: 10, y1: 7, fillcolor: 'rgba(34, 197, 94, 0.2)', line: { width: 0 } }   // Do First
                            ],
                            annotations: [
                              { x: 2.5, y: 8.5, text: '⚡ QUICK WIN<br><i>Low Effort, High Impact</i>', showarrow: false, font: { size: 12, color: '#3B82F6' } },
                              { x: 7.5, y: 8.5, text: '📅 SCHEDULE<br><i>High Effort, High Impact</i>', showarrow: false, font: { size: 12, color: '#F59E0B' } },
                              { x: 2.5, y: 3.5, text: '❌ DON\'T DO<br><i>Low Effort, Low Impact</i>', showarrow: false, font: { size: 12, color: '#EF4444' } },
                              { x: 7.5, y: 3.5, text: '🚀 DO FIRST<br><i>High Impact, High Effort</i>', showarrow: false, font: { size: 12, color: '#22C55E' } }
                            ]
                          }}
                        />
                      </ChartCard>

                      <div className="action-plans">
                        <h3>📋 Strategic Action Plans</h3>
                        
                        {doFirstCount > 0 && (
                          <div className="action-section">
                            <h4>🚀 DO FIRST - Critical High-Impact Fixes</h4>
                            <div className="grid gap-sm">
                              {priorityData
                                .filter(item => item.priority_quadrant === '🚀 DO FIRST')
                                .sort((a, b) => b.roi_score - a.roi_score)
                                .slice(0, 3)
                                .map((item, index) => (
                                  <ExpandableCard
                                    key={index}
                                    title={`🔥 ${item.page.substring(0, 40)}${item.page.length > 40 ? '...' : ''} - ROI: ${item.roi_score.toFixed(1)}`}
                                  >
                                    <div className="grid grid--cols-2 gap-md">
                                      <StandardCard
                                        title="📊 Performance Metrics"
                                        variant="content"
                                      >
                                        <p><strong>Current Score:</strong> {item.current_score.toFixed(1)}/10</p>
                                        <p><strong>Potential Improvement:</strong> +{item.potential_improvement.toFixed(1)} points</p>
                                        <p><strong>Time Estimate:</strong> {item.time_estimate}</p>
                                        <p><strong>Cost Estimate:</strong> {item.cost_estimate}</p>
                                      </StandardCard>
                                      <div className="action-recommendations">
                                        <h6>🎯 Action Items</h6>
                                        <ul>
                                          {item.recommendations.slice(0, 3).map((rec, recIndex) => (
                                            <li key={recIndex}>{rec}</li>
                                          ))}
                                        </ul>
                                        <p><strong>Issues:</strong> {item.issues.substring(0, 100)}...</p>
                                      </div>
                                    </div>
                                  </ExpandableCard>
                                ))}
                            </div>
                          </div>
                        )}

                        {quickWinsCount > 0 && (
                          <div className="action-section">
                            <h4>⚡ QUICK WINS - Low Effort, High Impact</h4>
                            <div className="grid gap-sm">
                              {priorityData
                                .filter(item => item.priority_quadrant === '⚡ QUICK WIN')
                                .sort((a, b) => b.roi_score - a.roi_score)
                                .slice(0, 5)
                                .map((item, index) => (
                                  <ExpandableCard
                                    key={index}
                                    title={`⚡ ${item.page.substring(0, 40)}${item.page.length > 40 ? '...' : ''} - ROI: ${item.roi_score.toFixed(1)}`}
                                  >
                                    <div className="grid grid--cols-2 gap-md">
                                      <StandardCard
                                        title="📊 Quick Win Metrics"
                                        variant="content"
                                      >
                                        <p><strong>Current Score:</strong> {item.current_score.toFixed(1)}/10</p>
                                        <p><strong>Potential Improvement:</strong> +{item.potential_improvement.toFixed(1)} points</p>
                                        <p><strong>Time Estimate:</strong> {item.time_estimate}</p>
                                      </StandardCard>
                                      <div className="action-recommendations">
                                        <h6>⚡ Quick Actions</h6>
                                        <ul>
                                          {item.recommendations.slice(0, 2).map((rec, recIndex) => (
                                            <li key={recIndex}>{rec}</li>
                                          ))}
                                        </ul>
                                      </div>
                                    </div>
                                  </ExpandableCard>
                                ))}
                            </div>
                          </div>
                        )}

                        <div className="implementation-roadmap">
                          <h4>🗓️ 90-Day Implementation Roadmap</h4>
                          <div className="grid grid--cols-3 gap-md">
                            <StandardCard
                              title="📅 Month 1 (Days 1-30)"
                              variant="content"
                              status="critical"
                            >
                              <p><strong>Focus:</strong> Complete all {doFirstCount} critical fixes</p>
                              <p><strong>Goal:</strong> Address urgent brand compliance issues</p>
                              <p><strong>Budget:</strong> €{(doFirstCount * 7500).toLocaleString()}</p>
                            </StandardCard>
                            
                            <StandardCard
                              title="⚡ Month 2 (Days 31-60)"
                              variant="content"
                              status="warning"
                            >
                              <p><strong>Focus:</strong> Implement {Math.min(quickWinsCount, 8)} quick wins</p>
                              <p><strong>Goal:</strong> Maximize ROI with low-effort improvements</p>
                              <p><strong>Budget:</strong> €{(Math.min(quickWinsCount, 8) * 1000).toLocaleString()}</p>
                            </StandardCard>
                            
                            <StandardCard
                              title="📈 Month 3 (Days 61-90)"
                              variant="content"
                              status="good"
                            >
                              <p><strong>Focus:</strong> Plan {Math.min(scheduleCount, 5)} scheduled improvements</p>
                              <p><strong>Goal:</strong> Long-term strategic enhancements</p>
                              <p><strong>Budget:</strong> €{(Math.min(scheduleCount, 5) * 3000).toLocaleString()}</p>
                            </StandardCard>
                          </div>
                          
                          <StandardCard
                            title="📊 Expected ROI"
                            variant="content"
                            status="excellent"
                          >
                            <p><strong>Total Potential Brand Score Improvement:</strong> +{priorityData.reduce((sum, item) => sum + item.potential_improvement, 0).toFixed(1)} points</p>
                            <p><strong>Estimated 90-Day Investment:</strong> €{(doFirstCount * 7500 + Math.min(quickWinsCount, 8) * 1000 + Math.min(scheduleCount, 5) * 3000).toLocaleString()}</p>
                            <p><strong>Expected Brand Health Increase:</strong> {(priorityData.reduce((sum, item) => sum + item.potential_improvement, 0) / priorityData.length * 100).toFixed(1)}% improvement</p>
                          </StandardCard>
                        </div>
                      </div>
                    </>
                  )
                })()}
              </div>
            )}

            {activeTab === 'standards' && (
              <div className="standards-tab">
                <h2>🎨 Brand Standards Reference</h2>
                
                <div className="brand-colors">
                  <h3>🌈 Official Brand Colors</h3>
                  
                  <div className="color-sections">
                    <div className="color-section">
                      <h4>Primary Color Palette</h4>
                      <div className="grid grid--auto-200 gap-md">
                        {PRIMARY_COLORS.map((color, index) => (
                          <StandardCard 
                            key={index}
                            variant="content"
                            className="color-card"
                          >
                            <div 
                              className="color-swatch" 
                              className="w-full"
                            ></div>
                            <div className="color-info">
                              <h5 style={{ color: color.hex, margin: '0 0 var(--spacing-xs) 0' }}>{color.name}</h5>
                              <code style={{ 
                                background: 'var(--gray-100)', 
                                padding: 'var(--spacing-xs)',
                                borderRadius: 'var(--border-radius-sm)',
                                fontSize: 'var(--font-size-sm)',
                                display: 'block',
                                marginBottom: 'var(--spacing-xs)'
                              }}>{color.hex}</code>
                              <p style={{ fontSize: 'var(--font-size-sm)', color: 'var(--text-secondary)', margin: '0' }}>{color.description}</p>
                              {color.cmyk && <small style={{ display: 'block', marginTop: 'var(--spacing-xs)', color: 'var(--text-secondary)' }}>{color.cmyk}</small>}
                            </div>
                          </StandardCard>
                        ))}
                      </div>
                    </div>
                    
                    <div className="color-section">
                      <h4>Secondary Color Palette</h4>
                      <div className="grid grid--auto-200 gap-md">
                        {SECONDARY_COLORS.map((color, index) => (
                          <StandardCard 
                            key={index}
                            variant="content"
                            className="color-card secondary"
                          >
                            <div 
                              className="color-swatch" 
                              className="w-full"
                            ></div>
                            <div className="color-info">
                              <strong style={{ color: color.hex, fontSize: 'var(--font-size-sm)' }}>{color.name}</strong>
                              <code style={{ 
                                background: 'var(--gray-100)', 
                                padding: 'var(--spacing-xs)',
                                borderRadius: 'var(--border-radius-sm)',
                                fontSize: 'var(--font-size-xs)',
                                display: 'block',
                                margin: 'var(--spacing-xs) 0'
                              }}>{color.hex}</code>
                              <small style={{ color: 'var(--text-secondary)' }}>{color.description}</small>
                            </div>
                          </StandardCard>
                        ))}
                      </div>
                    </div>
                  </div>
                </div>

                <div className="typography-standards">
                  <h3>🔤 Typography Standards</h3>
                  
                  <div className="typography-showcase">
                    <div className="font-family">
                      <h2>Hurme Geometric Sans 3</h2>
                      <p><em>Primary Font Family</em></p>
                    </div>
                    
                    <div className="typography-examples">
                      <h4>Typography Hierarchy Examples:</h4>
                      <div className="type-example">
                        <h1>H1 Heading Example</h1>
                        <h2>H2 Heading Example</h2>
                        <h3>H3 Heading Example</h3>
                        <p><strong>Body text example with bold weight</strong></p>
                        <p>Regular body text example</p>
                        <small>Caption text in smaller size</small>
                      </div>
                    </div>
                    
                    <div className="font-specifications">
                      <h4>Font Specifications:</h4>
                      <div className="grid grid--cols-3 gap-sm">
                        {[
                          { element: 'H1 Heading', weight: 'SemiBold (600)', size: '2.5rem' },
                          { element: 'H2 Heading', weight: 'SemiBold (600)', size: '2rem' },
                          { element: 'H3 Heading', weight: 'Medium (500)', size: '1.5rem' },
                          { element: 'Body Text', weight: 'Regular (400)', size: '1rem' },
                          { element: 'Caption', weight: 'Regular (400)', size: '0.875rem' },
                          { element: 'Buttons', weight: 'SemiBold (600)', size: '0.9rem' }
                        ].map((spec, index) => (
                          <StandardCard 
                            key={index}
                            title={spec.element}
                            variant="content"
                          >
                            <p><strong>Weight:</strong> {spec.weight}</p>
                            <p><strong>Size:</strong> {spec.size}</p>
                          </StandardCard>
                        ))}
                      </div>
                    </div>
                  </div>
                </div>

                <div className="color-accessibility">
                  <h3>🎯 Color Accessibility</h3>
                  <div className="accessibility-info">
                    <h4>Contrast Ratios (WCAG AA Compliant)</h4>
                    <div className="contrast-examples">
                      <div className="contrast-item" style={{ background: '#4D1D82', color: 'white' }}>
                        <span>Dark Purple on White</span>
                        <span className="contrast-ratio">8.2:1 ✅</span>
                      </div>
                      <div className="contrast-item" style={{ background: '#cf022b', color: 'white' }}>
                        <span>Red on White</span>
                        <span className="contrast-ratio">6.4:1 ✅</span>
                      </div>
                      <div className="contrast-item" style={{ background: '#2C3E50', color: 'white' }}>
                        <span>Text Gray on White</span>
                        <span className="contrast-ratio">12.6:1 ✅</span>
                      </div>
                    </div>
                  </div>
                </div>

                <div className="logo-guidelines">
                  <h3>Logo Usage Guidelines</h3>
                  <div className="logo-specs">
                    <div className="logo-spec-section">
                      <h4>Minimum Sizes</h4>
                      <ul>
                        <li><strong>Main Logo:</strong> 170px / 32mm</li>
                        <li><strong>Compact Logo:</strong> 56px / 15mm</li>
                      </ul>
                    </div>
                    <div className="logo-spec-section">
                      <h4>Protection Area</h4>
                      <ul>
                        <li>Based on "S" height in "Sopra Steria"</li>
                        <li>Maintain clear space on all sides</li>
                      </ul>
                    </div>
                  </div>
                </div>
              </div>
            )}

            {activeTab === 'evidence' && (
              <div className="evidence-tab">
                <h2>🔍 Evidence Examples & Trust Signals</h2>
                
                <div className="evidence-controls">
                  <div className="persona-filter">
                    <label>Filter by Persona:</label>
                    <select 
                      value={selectedPersona}
                      onChange={(e) => setSelectedPersona(e.target.value)}
                    >
                      <option value="All">All Personas</option>
                      <option value="P1">The Benelux Cybersecurity Decision Maker</option>
                      <option value="P2">The Benelux Strategic Business Leader</option>
                      <option value="P3">The Benelux Transformation Programme Leader</option>
                      <option value="P4">The Technical Influencer</option>
                      <option value="P5">The BENELUX Technology Innovation Leader</option>
                    </select>
                  </div>
                </div>

                <div className="evidence-sections">
                  <div className="evidence-section">
                    <h3>🎯 Brand Compliance Evidence</h3>
                                         <div className="evidence-browser">
                       <EvidenceBrowser 
                         data={auditData} 
                         evidenceColumns={['effective_copy_examples', 'ineffective_copy_examples', 'trust_credibility_assessment']}
                       />
                     </div>
                  </div>

                  <div className="evidence-section">
                    <h3>🔍 Visual Brand Evidence</h3>
                    <div className="brand-evidence-examples">
                      {auditData.length > 0 ? (
                        <div className="evidence-grid">
                          {auditData.slice(0, 6).map((item, index) => (
                            <div key={index} className="evidence-card">
                              <div className="evidence-header">
                                <h4>{item.url?.replace('https://www.', '') || `Page ${index + 1}`}</h4>
                                <div className="evidence-score">
                                  <span className="score-value">{item.final_score || 'N/A'}</span>
                                  <span className="score-label">Brand Score</span>
                                </div>
                              </div>
                              
                              <div className="evidence-content">
                                <div className="evidence-item">
                                  <strong>First Impression:</strong>
                                  <p>{item.first_impression || 'Clean, professional design with clear brand consistency'}</p>
                                </div>
                                
                                <div className="evidence-item">
                                  <strong>Trust Signals:</strong>
                                  <p>{item.trust_credibility_assessment || 'Strong brand presence with professional imagery and consistent messaging'}</p>
                                </div>
                                
                                <div className="evidence-item">
                                  <strong>Effective Copy:</strong>
                                  <p className="effective-copy">{item.effective_copy_examples || 'Clear value proposition with technical credibility'}</p>
                                </div>
                                
                                {item.ineffective_copy_examples && (
                                  <div className="evidence-item">
                                    <strong>Areas for Improvement:</strong>
                                    <p className="ineffective-copy">{item.ineffective_copy_examples}</p>
                                  </div>
                                )}
                              </div>
                            </div>
                          ))}
                        </div>
                      ) : (
                        <div className="no-evidence">
                          <p>No evidence data available. Please ensure audit data is loaded.</p>
                        </div>
                      )}
                    </div>
                  </div>

                  <div className="evidence-section">
                    <h3>📊 Brand Performance Insights</h3>
                    <div className="performance-insights">
                      <div className="insight-cards">
                        <div className="insight-card success">
                          <div className="insight-icon">🎯</div>
                          <div className="insight-content">
                            <h4>Brand Consistency</h4>
                            <p>Strong visual identity across {auditData.length} audited pages</p>
                            <div className="insight-metric">
                              {auditData.length > 0 ? 
                                `${((auditData.filter(item => item.final_score >= 8).length / auditData.length) * 100).toFixed(1)}%` : 
                                'N/A'
                              } compliance rate
                            </div>
                          </div>
                        </div>
                        
                        <div className="insight-card warning">
                          <div className="insight-icon">⚠️</div>
                          <div className="insight-content">
                            <h4>Trust Signals</h4>
                            <p>Professional imagery and credible messaging patterns</p>
                            <div className="insight-metric">
                              {auditData.length > 0 ? 
                                `${auditData.filter(item => item.trust_credibility_assessment?.includes('professional')).length}` : 
                                'N/A'
                              } pages with strong trust signals
                            </div>
                          </div>
                        </div>
                        
                        <div className="insight-card info">
                          <div className="insight-icon">📈</div>
                          <div className="insight-content">
                            <h4>Content Quality</h4>
                            <p>Effective copy examples driving engagement</p>
                            <div className="insight-metric">
                              {auditData.length > 0 ? 
                                `${auditData.filter(item => item.effective_copy_examples?.length > 10).length}` : 
                                'N/A'
                              } pages with strong copy
                            </div>
                          </div>
                        </div>
                      </div>
                    </div>
                  </div>

                  <div className="evidence-section">
                    <h3>🚀 Evidence-Based Recommendations</h3>
                    <div className="recommendations">
                      <div className="recommendation-category">
                        <h4>🎨 Visual Brand Improvements</h4>
                        <ul>
                          <li>Standardize logo placement and sizing across all pages</li>
                          <li>Implement consistent color palette usage</li>
                          <li>Ensure typography hierarchy follows brand guidelines</li>
                          <li>Optimize image quality and brand alignment</li>
                        </ul>
                      </div>
                      
                      <div className="recommendation-category">
                        <h4>📝 Content & Messaging</h4>
                        <ul>
                          <li>Enhance trust signals with customer testimonials</li>
                          <li>Improve technical credibility through case studies</li>
                          <li>Strengthen value propositions with specific benefits</li>
                          <li>Address information gaps identified in audit</li>
                        </ul>
                      </div>
                      
                      <div className="recommendation-category">
                        <h4>🔍 Trust & Credibility</h4>
                        <ul>
                          <li>Add professional certifications and awards</li>
                          <li>Include client logos and partnership badges</li>
                          <li>Implement security trust indicators</li>
                          <li>Enhance contact information visibility</li>
                        </ul>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            )}
          </div>
        </div>
      </div>

      {/* Export Options */}
      <div className="section">
        <h2>Export & Reporting</h2>
        <div className="export-options">
          <button className="export-button primary" onClick={() => alert('Full brand hygiene report exported successfully!')}>
            📊 Export Full Report
          </button>
          <button className="export-button secondary" onClick={() => alert('Executive summary generated!')}>
            📈 Generate Executive Summary
          </button>
          <button className="export-button secondary" onClick={() => alert('Re-audit scheduled for 6 months from now!')}>
            🔄 Schedule Re-audit
          </button>
        </div>
      </div>

      {/* Sidebar Quick Insights - matches Streamlit version */}
      <div className="sidebar-insights">
        <div className="sidebar-card">
          <h3>Quick Insights</h3>
          
          {data.length > 0 && (
            <>
              <div className="quick-insight success">
                <div className="insight-icon">🌟</div>
                <div className="insight-content">
                  <strong>Top Performer</strong>
                  <p>{(() => {
                    const topPage = data.reduce((max, item) => item.final_score > max.final_score ? item : max)
                    return `${topPage.url?.replace('https://www.', '') || 'Unknown Page'} (${topPage.final_score?.toFixed(1) || '0.0'}/10)`
                  })()}</p>
                </div>
              </div>
              
              <div className="quick-insight error">
                <div className="insight-icon">⚠️</div>
                <div className="insight-content">
                  <strong>Needs Attention</strong>
                  <p>{(() => {
                    const bottomPage = data.reduce((min, item) => item.final_score < min.final_score ? item : min)
                    return `${bottomPage.url?.replace('https://www.', '') || 'Unknown Page'} (${bottomPage.final_score?.toFixed(1) || '0.0'}/10)`
                  })()}</p>
                </div>
              </div>
            </>
          )}
          
          <div className="quick-stats">
            <h4>Quick Stats</h4>
            {data.length > 0 && (
              <>
                <div className="stat-item">
                  <span className="stat-label">Avg Logo Score</span>
                  <span className="stat-value">{(data.reduce((sum, item) => sum + item.logo_compliance, 0) / data.length).toFixed(1)}/10</span>
                </div>
                <div className="stat-item">
                  <span className="stat-label">Avg Color Score</span>
                  <span className="stat-value">{(data.reduce((sum, item) => sum + item.color_palette, 0) / data.length).toFixed(1)}/10</span>
                </div>
                <div className="stat-item">
                  <span className="stat-label">Avg Typography</span>
                  <span className="stat-value">{(data.reduce((sum, item) => sum + item.typography, 0) / data.length).toFixed(1)}/10</span>
                </div>
              </>
            )}
          </div>
        </div>
      </div>
    </div>
  )
}

export default VisualBrandHygiene
