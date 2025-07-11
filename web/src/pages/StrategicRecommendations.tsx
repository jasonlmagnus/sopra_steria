import { useState } from 'react'
import { useQuery } from '@tanstack/react-query'
import { EvidenceDisplay } from '../components/EvidenceDisplay'
import { PlotlyChart } from '../components/PlotlyChart'
import StandardCard from '../components/StandardCard'
// Import unified dashboard styles
import '../styles/dashboard.css'

const apiBase = import.meta.env.VITE_API_URL || 'http://localhost:8000'

interface StrategicIntelligence {
  executiveSummary: {
    totalRecommendations: number
    highImpactOpportunities: number
    pipelineRisk: number
    competitiveGaps: number
    quickWinValue: number
    strategicInvestmentROI: number
  }
  strategicThemes: Array<{
    id: string
    title: string
    description: string
    currentScore: number
    targetScore: number
    businessImpact: 'High' | 'Medium' | 'Low'
    affectedPages: number
    revenueImpact: number
    competitiveRisk: 'High' | 'Medium' | 'Low'
    keyInsights: string[]
    soWhat: string
  }>
  businessImpact: {
    revenueOpportunity: number
    conversionUplift: number
    competitiveAdvantage: string[]
    brandEquityRisk: number
  }
  recommendations: Array<{
    id: string
    title: string
    description: string
    businessImpact: 'High' | 'Medium' | 'Low'
    implementationEffort: 'High' | 'Medium' | 'Low'
    timeline: string
    revenueImpact: number
    conversionUplift: number
    competitiveAdvantage: string
    tier: string
    persona: string
    currentScore: number
    targetScore: number
    evidence: string
    soWhat: string
    implementationSteps: string[]
    success_metrics: string[]
  }>
  tierAnalysis: Record<string, {
    pages: number
    averageScore: number
    businessPriority: 'Strategic' | 'Tactical' | 'Operational'
    criticalIssues: number
    quickWins: number
    successStories: number
    revenueImpact: number
  }>
  competitiveContext: {
    overallPosition: 'Above Average' | 'Below Average'
    benchmarkScore: number
    currentScore: number
    competitiveGap: number
    advantages: string[]
    vulnerabilities: string[]
    marketOpportunity: string
  }
  implementationRoadmap: Array<{
    phase: string
    focus: string
    recommendations: string[]
    expectedImpact: number
    keyMilestones: string[]
  }>
}

// Add fallback data structure for basic recommendations
interface BasicRecommendation {
  id: string
  title: string
  description: string
  category: string
  impact_score: number
  urgency_score: number
  timeline: string
  priority_score: number
  page_id: string
  persona: string
  url: string
  evidence: string
  source: string
}

function StrategicRecommendations() {
  const [selectedTier, setSelectedTier] = useState('All')
  const [selectedBusinessImpact, setSelectedBusinessImpact] = useState('All')
  const [selectedTimeline, setSelectedTimeline] = useState('All')
  const [viewMode, setViewMode] = useState('executive')
  const [fallbackMode, setFallbackMode] = useState(false)

  // Primary data source - strategic intelligence
  const { data: strategicData, isLoading: strategicLoading, error: strategicError } = useQuery({
    queryKey: ['strategic-intelligence', selectedTier, selectedBusinessImpact, selectedTimeline],
    queryFn: async () => {
      const params = new URLSearchParams()
      if (selectedTier !== 'All') params.append('tier', selectedTier)
      if (selectedBusinessImpact !== 'All') params.append('business_impact', selectedBusinessImpact)
      if (selectedTimeline !== 'All') params.append('timeline', selectedTimeline)
      
      const res = await fetch(`${apiBase}/strategic-intelligence?${params.toString()}`)
      if (!res.ok) throw new Error('Failed to load strategic intelligence')
      return await res.json() as StrategicIntelligence
    },
    retry: 1, // Only retry once before falling back
    retryDelay: 1000
  })

  // Fallback data source - basic recommendations from unified dataset
  const { data: fallbackData, isLoading: fallbackLoading } = useQuery({
    queryKey: ['basic-recommendations', selectedTier, selectedTimeline],
    queryFn: async () => {
      const params = new URLSearchParams()
      if (selectedTier !== 'All') params.append('tier', selectedTier)
      if (selectedTimeline !== 'All') params.append('timeline', selectedTimeline)
      
      const res = await fetch(`${apiBase}/full-recommendations?${params.toString()}`)
      if (!res.ok) throw new Error('Failed to load basic recommendations')
      const data = await res.json()
      return data.recommendations as BasicRecommendation[]
    },
    enabled: !!strategicError // Only run if strategic intelligence fails
  })

  // Determine which data to use
  const isUsingFallback = !!strategicError && !fallbackLoading
  const isLoading = strategicLoading || (strategicError && fallbackLoading)
  const hasData = strategicData || fallbackData

  const formatCurrency = (amount: number): string => {
    if (amount >= 1000000) {
      return `$${(amount / 1000000).toFixed(1)}M`
    } else if (amount >= 1000) {
      return `$${(amount / 1000).toFixed(0)}K`
    } else {
      return `$${amount.toFixed(0)}`
    }
  }

  const getImpactColor = (impact: 'High' | 'Medium' | 'Low'): string => {
    switch (impact) {
      case 'High': return '#dc3545'
      case 'Medium': return '#fd7e14'
      case 'Low': return '#28a745'
      default: return '#6c757d'
    }
  }

  const getRiskColor = (risk: 'High' | 'Medium' | 'Low'): string => {
    switch (risk) {
      case 'High': return '#dc3545'
      case 'Medium': return '#ffc107'
      case 'Low': return '#28a745'
      default: return '#6c757d'
    }
  }

  const getBusinessImpactMatrix = () => {
    if (!strategicData?.recommendations) return []

    return strategicData.recommendations.map((rec) => ({
      x: rec.implementationEffort === 'High' ? 3 : rec.implementationEffort === 'Medium' ? 2 : 1,
      y: rec.businessImpact === 'High' ? 3 : rec.businessImpact === 'Medium' ? 2 : 1,
      text: rec.title.replace('Quick Win: ', '').replace('CRITICAL: ', ''),
      mode: 'markers+text',
      textposition: 'middle center',
      marker: {
        size: rec.revenueImpact / 50000, // Scale marker size by revenue impact
        color: rec.timeline.includes('0-7') ? '#dc3545' : 
               rec.timeline.includes('0-30') ? '#fd7e14' :
               rec.timeline.includes('30-90') ? '#ffc107' : '#28a745',
        opacity: 0.7
      }
    }))
  }

  if (isLoading) {
    return (
      <div className="page-container">
        <div className="main-header">
          <h1 className="page-title">🎯 Strategic Intelligence</h1>
          <p className="page-subtitle">Loading strategic analysis...</p>
        </div>
        <div className="loading-state">
          <div className="loading-spinner"></div>
          <p>Analyzing brand health data...</p>
        </div>
      </div>
    )
  }

  if (!hasData) {
    return (
      <div className="page-container">
        <div className="main-header">
          <h1 className="page-title">🎯 Strategic Intelligence</h1>
          <p className="page-subtitle">Strategic recommendations and action plans for brand improvement</p>
        </div>
        
        <div className="alert alert--error">
          <h2>⚠️ Error Loading Recommendations</h2>
          <p>Failed to load strategic recommendations</p>
          <p><strong>Troubleshooting:</strong></p>
          <ul>
            <li>Ensure FastAPI server is running on port 8000</li>
            <li>Check that audit data has been processed</li>
            <li>Verify network connectivity</li>
          </ul>
          <button 
            className="btn btn--primary"
            onClick={() => window.location.reload()}
          >
            🔄 Retry
          </button>
        </div>
      </div>
    )
  }

  // Render fallback view if using basic recommendations
  if (isUsingFallback && fallbackData) {
    return (
      <div className="page-container">
        <div className="main-header">
          <h1 className="page-title">🎯 Strategic Recommendations</h1>
          <p className="page-subtitle">Basic recommendations from audit data (Limited Mode)</p>
        </div>

        <div className="alert alert--warning">
          <p><strong>Limited Mode:</strong> Using basic recommendations data. For full strategic intelligence, ensure FastAPI server is running.</p>
        </div>

        <FallbackRecommendationsView 
          recommendations={fallbackData}
          selectedTier={selectedTier}
          selectedTimeline={selectedTimeline}
          setSelectedTier={setSelectedTier}
          setSelectedTimeline={setSelectedTimeline}
        />
      </div>
    )
  }

  // Type guard for strategicData
  if (!strategicData) {
    return null // This shouldn't happen due to earlier checks, but satisfies TypeScript
  }

  return (
    <div className="page-container">
      {/* Header with proper styling */}
      <div className="main-header">
        <h1 className="page-title">🎯 Strategic Intelligence</h1>
        <p className="page-subtitle">Business-focused strategic recommendations with ROI impact and competitive context</p>
      </div>

      {/* Executive Summary - Always visible */}
      <div className="insights-box">
        <h2 className="insights-box__title">📊 Executive Summary</h2>
        <div className="metrics-grid">
          <StandardCard
            title="Pipeline Risk"
            variant="metric"
            status="critical"
          >
            <div className="metric-value">{formatCurrency(strategicData.executiveSummary.pipelineRisk)}</div>
            <div className="metric-description">Annual revenue at risk from brand health issues</div>
          </StandardCard>

          <StandardCard
            title="Quick Win Value"
            variant="metric"
            status="excellent"
          >
            <div className="metric-value">{formatCurrency(strategicData.executiveSummary.quickWinValue)}</div>
            <div className="metric-description">Immediate revenue opportunity from low-effort fixes</div>
          </StandardCard>

          <StandardCard
            title="Strategic Investment ROI"
            variant="metric"
            status="good"
          >
            <div className="metric-value">{formatCurrency(strategicData.executiveSummary.strategicInvestmentROI)}</div>
            <div className="metric-description">Expected 30% ROI on strategic brand investments</div>
          </StandardCard>

          <StandardCard
            title="Competitive Gaps"
            variant="metric"
            status="warning"
          >
            <div className="metric-value">{strategicData.executiveSummary.competitiveGaps}</div>
            <div className="metric-description">Critical issues creating competitive vulnerability</div>
          </StandardCard>
        </div>

        {/* Competitive Context */}
        <div className="insights-box" style={{ marginTop: '2rem' }}>
          <h3>🏆 Competitive Position</h3>
          <div className="grid grid--2">
            <div>
              <div style={{ display: 'flex', alignItems: 'center', gap: '1rem', marginBottom: '1rem' }}>
                <span className="metric-value" style={{ 
                  color: strategicData.competitiveContext.overallPosition === 'Above Average' ? 'var(--status-excellent)' : 'var(--status-critical)'
                }}>
                  {strategicData.competitiveContext.currentScore.toFixed(1)}/10
                </span>
                <span className="text-secondary">vs {strategicData.competitiveContext.benchmarkScore}/10 industry average</span>
              </div>
              <div className="progress-bar">
                <div 
                  className="progress-fill"
                  style={{ 
                    width: `${(strategicData.competitiveContext.currentScore / 10) * 100}%`,
                    backgroundColor: strategicData.competitiveContext.overallPosition === 'Above Average' ? 'var(--status-excellent)' : 'var(--status-critical)'
                  }}
                />
              </div>
            </div>
            <div>
              <p className="font-semibold" style={{ 
                color: strategicData.competitiveContext.overallPosition === 'Above Average' ? 'var(--status-excellent)' : 'var(--status-critical)'
              }}>
                {strategicData.competitiveContext.overallPosition}
              </p>
              <p className="text-secondary text-sm">
                {strategicData.competitiveContext.marketOpportunity}
              </p>
            </div>
          </div>
        </div>
      </div>

      {/* Filters */}
      <div className="insights-box">
        <h2 className="insights-box__title">🎛️ Strategic Focus</h2>
        <div className="filter-controls">
          <div className="filter-group">
            <label className="filter-label">Content Tier</label>
            <select 
              value={selectedTier}
              onChange={(e) => setSelectedTier(e.target.value)}
              className="filter-select"
            >
              <option value="All">All Tiers</option>
              <option value="Tier 1">Tier 1 (Strategic)</option>
              <option value="Tier 2">Tier 2 (Tactical)</option>
              <option value="Tier 3">Tier 3 (Operational)</option>
            </select>
          </div>

          <div className="filter-group">
            <label className="filter-label">Business Impact</label>
            <select 
              value={selectedBusinessImpact}
              onChange={(e) => setSelectedBusinessImpact(e.target.value)}
              className="filter-select"
            >
              <option value="All">All Impact Levels</option>
              <option value="High">High Impact</option>
              <option value="Medium">Medium Impact</option>
              <option value="Low">Low Impact</option>
            </select>
          </div>

          <div className="filter-group">
            <label className="filter-label">Timeline</label>
            <select 
              value={selectedTimeline}
              onChange={(e) => setSelectedTimeline(e.target.value)}
              className="filter-select"
            >
              <option value="All">All Timelines</option>
              <option value="0-7 days">Immediate (0-7 days)</option>
              <option value="0-30 days">Short-term (0-30 days)</option>
              <option value="30-90 days">Medium-term (30-90 days)</option>
              <option value="90+ days">Long-term (90+ days)</option>
            </select>
          </div>

          <div className="filter-group">
            <label className="filter-label">View Mode</label>
            <select 
              value={viewMode}
              onChange={(e) => setViewMode(e.target.value)}
              className="filter-select"
            >
              <option value="executive">Executive Summary</option>
              <option value="themes">Strategic Themes</option>
              <option value="recommendations">Action Items</option>
              <option value="roadmap">Implementation Roadmap</option>
              <option value="matrix">Business Impact Matrix</option>
            </select>
          </div>
        </div>
      </div>

      {/* Strategic Themes */}
      {viewMode === 'themes' && (
        <div className="insights-box">
          <h2>🧠 Strategic Themes</h2>
          <div style={{ display: 'grid', gap: '1.5rem' }}>
            {strategicData.strategicThemes.map((theme) => (
              <div key={theme.id} className="theme-card" style={{ 
                border: '1px solid #dee2e6', 
                borderRadius: '8px', 
                padding: '1.5rem',
                backgroundColor: '#fff'
              }}>
                <div className="theme-header" style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'start', marginBottom: '1rem' }}>
                  <h3 style={{ margin: 0 }}>{theme.title}</h3>
                  <div className="theme-badges" style={{ display: 'flex', gap: '0.5rem' }}>
                    <span className="badge" style={{ 
                      padding: '0.25rem 0.5rem', 
                      borderRadius: '4px', 
                      fontSize: '0.75rem',
                      fontWeight: '600',
                      backgroundColor: getImpactColor(theme.businessImpact),
                      color: 'white'
                    }}>
                      {theme.businessImpact} Impact
                    </span>
                    <span className="badge" style={{ 
                      padding: '0.25rem 0.5rem', 
                      borderRadius: '4px', 
                      fontSize: '0.75rem',
                      fontWeight: '600',
                      backgroundColor: getRiskColor(theme.competitiveRisk),
                      color: 'white'
                    }}>
                      {theme.competitiveRisk} Risk
                    </span>
                  </div>
                </div>

                <p style={{ color: '#4b5563', marginBottom: '1rem' }}>{theme.description}</p>

                <div className="grid grid--auto-150 gap-md" style={{ marginBottom: '1rem' }}>
                  <StandardCard
                    title="Current Score"
                    variant="metric"
                    status={theme.currentScore >= 8 ? "excellent" : theme.currentScore >= 6 ? "good" : "warning"}
                  >
                    <div className="metric-value">{theme.currentScore.toFixed(1)}/10</div>
                  </StandardCard>
                  <StandardCard
                    title="Target Score"
                    variant="metric"
                    status="excellent"
                  >
                    <div className="metric-value">{theme.targetScore.toFixed(1)}/10</div>
                  </StandardCard>
                  <StandardCard
                    title="Pages Affected"
                    variant="metric"
                    status="good"
                  >
                    <div className="metric-value">{theme.affectedPages}</div>
                  </StandardCard>
                  <StandardCard
                    title="Revenue Impact"
                    variant="metric"
                    status="critical"
                  >
                    <div className="metric-value">{formatCurrency(theme.revenueImpact)}</div>
                  </StandardCard>
                </div>

                <div className="theme-insights" style={{ marginBottom: '1rem' }}>
                  <h4>Key Insights</h4>
                  <ul style={{ paddingLeft: '1.5rem' }}>
                    {theme.keyInsights.map((insight, idx) => (
                      <li key={idx} style={{ marginBottom: '0.5rem' }}>{insight}</li>
                    ))}
                  </ul>
                </div>

                <div className="theme-so-what" style={{ padding: '1rem', backgroundColor: '#f8f9fa', borderRadius: '6px', border: '1px solid #dee2e6' }}>
                  <h4 style={{ color: '#007bff', marginBottom: '0.5rem' }}>💡 So What?</h4>
                  <p style={{ margin: 0, fontWeight: '600' }}>{theme.soWhat}</p>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Recommendations */}
      {viewMode === 'recommendations' && (
        <div className="insights-box">
          <h2>📋 Strategic Action Items</h2>
          <div style={{ display: 'grid', gap: '1.5rem' }}>
            {strategicData.recommendations.map((rec) => (
              <div key={rec.id} className="recommendation-card" style={{ 
                border: '1px solid #dee2e6', 
                borderRadius: '8px', 
                padding: '1.5rem',
                backgroundColor: rec.businessImpact === 'High' ? '#fef2f2' : rec.businessImpact === 'Medium' ? '#fffbeb' : '#f0fdf4'
              }}>
                <div className="recommendation-header" style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'start', marginBottom: '1rem' }}>
                  <h3 style={{ margin: 0 }}>{rec.title}</h3>
                  <div className="recommendation-badges" style={{ display: 'flex', gap: '0.5rem' }}>
                    <span className="badge" style={{ 
                      padding: '0.25rem 0.5rem', 
                      borderRadius: '4px', 
                      fontSize: '0.75rem',
                      fontWeight: '600',
                      backgroundColor: getImpactColor(rec.businessImpact),
                      color: 'white'
                    }}>
                      {rec.businessImpact} Impact
                    </span>
                    <span className="badge" style={{ 
                      padding: '0.25rem 0.5rem', 
                      borderRadius: '4px', 
                      fontSize: '0.75rem',
                      fontWeight: '600',
                      backgroundColor: '#6c757d',
                      color: 'white'
                    }}>
                      {rec.timeline}
                    </span>
                  </div>
                </div>

                <p style={{ color: '#4b5563', marginBottom: '1rem' }}>{rec.description}</p>

                <div className="grid grid--auto-150 gap-md" style={{ marginBottom: '1rem' }}>
                  <StandardCard
                    title="Revenue Impact"
                    variant="metric"
                    status="excellent"
                  >
                    <div className="metric-value">{formatCurrency(rec.revenueImpact)}</div>
                  </StandardCard>
                  <StandardCard
                    title="Conversion Uplift"
                    variant="metric"
                    status="good"
                  >
                    <div className="metric-value">+{rec.conversionUplift}%</div>
                  </StandardCard>
                  <StandardCard
                    title="Current Score"
                    variant="metric"
                    status={rec.currentScore >= 8 ? "excellent" : rec.currentScore >= 6 ? "good" : "warning"}
                  >
                    <div className="metric-value">{rec.currentScore.toFixed(1)}/10</div>
                  </StandardCard>
                  <StandardCard
                    title="Implementation Effort"
                    variant="metric"
                    status={rec.implementationEffort === "Low" ? "excellent" : rec.implementationEffort === "Medium" ? "warning" : "critical"}
                  >
                    <div className="metric-value">{rec.implementationEffort}</div>
                  </StandardCard>
                </div>

                <div className="recommendation-so-what" style={{ padding: '1rem', backgroundColor: '#f8f9fa', borderRadius: '6px', border: '1px solid #dee2e6', marginBottom: '1rem' }}>
                  <h4 style={{ color: '#007bff', marginBottom: '0.5rem' }}>💡 So What?</h4>
                  <p style={{ margin: 0, fontWeight: '600' }}>{rec.soWhat}</p>
                </div>

                <div className="recommendation-evidence" style={{ marginBottom: '1rem' }}>
                  <EvidenceDisplay
                    evidence={[{ type: 'evidence' as const, content: rec.evidence }]}
                    title="Supporting Evidence"
                    collapsible={true}
                    defaultExpanded={false}
                  />
                </div>

                <div className="recommendation-implementation">
                  <h4>🔧 Implementation Steps</h4>
                  <ol style={{ paddingLeft: '1.5rem' }}>
                    {rec.implementationSteps.map((step, idx) => (
                      <li key={idx} style={{ marginBottom: '0.5rem' }}>{step}</li>
                    ))}
                  </ol>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Implementation Roadmap */}
      {viewMode === 'roadmap' && (
        <div className="insights-box">
          <h2>🗺️ Implementation Roadmap</h2>
          <div style={{ display: 'grid', gap: '1.5rem' }}>
            {strategicData.implementationRoadmap.map((phase, idx) => (
              <div key={idx} className="roadmap-phase" style={{ 
                border: '1px solid #dee2e6', 
                borderRadius: '8px', 
                padding: '1.5rem',
                backgroundColor: '#fff'
              }}>
                <div className="phase-header" style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'start', marginBottom: '1rem' }}>
                  <h3 style={{ margin: 0 }}>{phase.phase}</h3>
                  <div style={{ fontSize: '1.5rem', fontWeight: 'bold', color: '#28a745' }}>
                    {formatCurrency(phase.expectedImpact)}
                  </div>
                </div>
                <p style={{ color: '#4b5563', marginBottom: '1rem' }}>{phase.focus}</p>
                
                <div className="phase-recommendations" style={{ marginBottom: '1rem' }}>
                  <h4>📋 Key Recommendations</h4>
                  <ul style={{ paddingLeft: '1.5rem' }}>
                    {phase.recommendations.map((rec, recIdx) => (
                      <li key={recIdx} style={{ marginBottom: '0.5rem' }}>{rec}</li>
                    ))}
                  </ul>
                </div>

                <div className="phase-milestones">
                  <h4>🎯 Key Milestones</h4>
                  <ul style={{ paddingLeft: '1.5rem' }}>
                    {phase.keyMilestones.map((milestone, milestoneIdx) => (
                      <li key={milestoneIdx} style={{ marginBottom: '0.5rem' }}>{milestone}</li>
                    ))}
                  </ul>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Business Impact Matrix */}
      {viewMode === 'matrix' && (
        <div className="insights-box">
          <h2>📊 Business Impact Matrix</h2>
          <div className="matrix-container">
            <PlotlyChart
              data={getBusinessImpactMatrix()}
              layout={{
                title: 'Business Impact vs Implementation Effort',
                xaxis: { 
                  title: 'Implementation Effort',
                  tickvals: [1, 2, 3],
                  ticktext: ['Low', 'Medium', 'High']
                },
                yaxis: { 
                  title: 'Business Impact',
                  tickvals: [1, 2, 3],
                  ticktext: ['Low', 'Medium', 'High']
                },
                height: 600,
                annotations: [
                  {
                    x: 1,
                    y: 3,
                    text: 'Quick Wins<br>(High Impact, Low Effort)',
                    showarrow: false,
                    xanchor: 'center',
                    yanchor: 'middle',
                    bgcolor: 'rgba(40, 167, 69, 0.1)',
                    bordercolor: '#28a745',
                    borderwidth: 2
                  },
                  {
                    x: 3,
                    y: 3,
                    text: 'Strategic Projects<br>(High Impact, High Effort)',
                    showarrow: false,
                    xanchor: 'center',
                    yanchor: 'middle',
                    bgcolor: 'rgba(0, 123, 255, 0.1)',
                    bordercolor: '#007bff',
                    borderwidth: 2
                  }
                ]
              }}
            />
          </div>
          <div className="matrix-legend" style={{ marginTop: '1rem' }}>
            <h4>Legend:</h4>
            <p><strong>Size:</strong> Revenue impact (larger = higher revenue potential)</p>
            <p><strong>Color:</strong> Timeline (Red = Immediate, Orange = Short-term, Yellow = Medium-term, Green = Long-term)</p>
          </div>
        </div>
      )}

      {/* Tier Analysis */}
      {viewMode === 'executive' && (
        <div className="insights-box">
          <h2>📈 Tier-Level Intelligence</h2>
          <div style={{ display: 'grid', gap: '1.5rem' }}>
            {Object.entries(strategicData.tierAnalysis).map(([tier, data]) => (
              <div key={tier} className="tier-card" style={{ 
                border: '1px solid #dee2e6', 
                borderRadius: '8px', 
                padding: '1.5rem',
                backgroundColor: data.businessPriority === 'Strategic' ? '#f8f9fa' : 
                                 data.businessPriority === 'Tactical' ? '#fff8e1' : '#f0fdf4'
              }}>
                <div className="tier-header" style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'start', marginBottom: '1rem' }}>
                  <h3 style={{ margin: 0 }}>{tier}</h3>
                  <span className="badge" style={{ 
                    padding: '0.25rem 0.5rem', 
                    borderRadius: '4px', 
                    fontSize: '0.75rem',
                    fontWeight: '600',
                    backgroundColor: data.businessPriority === 'Strategic' ? '#007bff' : 
                                     data.businessPriority === 'Tactical' ? '#fd7e14' : '#28a745',
                    color: 'white'
                  }}>
                    {data.businessPriority}
                  </span>
                </div>

                <div className="grid grid--auto-120 gap-md">
                  <StandardCard
                    title="Average Score"
                    variant="metric"
                    status={data.averageScore >= 8 ? "excellent" : data.averageScore >= 6 ? "good" : "warning"}
                  >
                    <div className="metric-value">{data.averageScore.toFixed(1)}/10</div>
                  </StandardCard>
                  <StandardCard
                    title="Total Pages"
                    variant="metric"
                    status="good"
                  >
                    <div className="metric-value">{data.pages}</div>
                  </StandardCard>
                  <StandardCard
                    title="Critical Issues"
                    variant="metric"
                    status={data.criticalIssues === 0 ? "excellent" : data.criticalIssues <= 2 ? "warning" : "critical"}
                  >
                    <div className="metric-value">{data.criticalIssues}</div>
                  </StandardCard>
                  <StandardCard
                    title="Quick Wins"
                    variant="metric"
                    status="excellent"
                  >
                    <div className="metric-value">{data.quickWins}</div>
                  </StandardCard>
                  <StandardCard
                    title="Revenue Impact"
                    variant="metric"
                    status="warning"
                  >
                    <div className="metric-value">{formatCurrency(data.revenueImpact)}</div>
                  </StandardCard>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  )
}

// Fallback component for basic recommendations
function FallbackRecommendationsView({ 
  recommendations, 
  selectedTier, 
  selectedTimeline, 
  setSelectedTier, 
  setSelectedTimeline 
}: {
  recommendations: BasicRecommendation[]
  selectedTier: string
  selectedTimeline: string
  setSelectedTier: (tier: string) => void
  setSelectedTimeline: (timeline: string) => void
}) {
  // Filter recommendations
  const filteredRecs = recommendations.filter(rec => {
    if (selectedTier !== 'All' && !rec.page_id.includes(selectedTier.toLowerCase())) return false
    if (selectedTimeline !== 'All' && rec.timeline !== selectedTimeline) return false
    return true
  })

  const getImpactColor = (score: number): string => {
    if (score >= 8) return 'var(--status-critical)'
    if (score >= 6) return 'var(--status-warning)'
    return 'var(--status-excellent)'
  }

  const getPriorityIcon = (score: number): string => {
    if (score >= 8) return '🔴'
    if (score >= 6) return '🟡'
    return '🟢'
  }

  return (
    <>
      {/* Basic Filters */}
      <div className="insights-box">
        <h2 className="insights-box__title">🎛️ Filters</h2>
        <div className="filter-controls">
          <div className="filter-group">
            <label className="filter-label">Content Tier</label>
            <select 
              value={selectedTier}
              onChange={(e) => setSelectedTier(e.target.value)}
              className="filter-select"
            >
              <option value="All">All Tiers</option>
              <option value="Tier 1">Tier 1</option>
              <option value="Tier 2">Tier 2</option>
              <option value="Tier 3">Tier 3</option>
            </select>
          </div>

          <div className="filter-group">
            <label className="filter-label">Timeline</label>
            <select 
              value={selectedTimeline}
              onChange={(e) => setSelectedTimeline(e.target.value)}
              className="filter-select"
            >
              <option value="All">All Timelines</option>
              <option value="0-7 days">Immediate (0-7 days)</option>
              <option value="0-30 days">Short-term (0-30 days)</option>
              <option value="30-90 days">Medium-term (30-90 days)</option>
              <option value="90+ days">Long-term (90+ days)</option>
            </select>
          </div>
        </div>
      </div>

      {/* Summary Metrics */}
      <div className="insights-box">
        <h2 className="insights-box__title">📊 Recommendations Summary</h2>
        <div className="metrics-grid">
          <StandardCard
            title="Total Recommendations"
            variant="metric"
            status="good"
          >
            <div className="metric-value">{filteredRecs.length}</div>
          </StandardCard>

          <StandardCard
            title="High Priority"
            variant="metric"
            status="critical"
          >
            <div className="metric-value">{filteredRecs.filter(r => r.priority_score >= 8).length}</div>
          </StandardCard>

          <StandardCard
            title="Quick Wins"
            variant="metric"
            status="excellent"
          >
            <div className="metric-value">{filteredRecs.filter(r => r.timeline === '0-30 days').length}</div>
          </StandardCard>

          <StandardCard
            title="Average Impact"
            variant="metric"
            status="warning"
          >
            <div className="metric-value">{(filteredRecs.reduce((sum, r) => sum + r.impact_score, 0) / filteredRecs.length || 0).toFixed(1)}/10</div>
          </StandardCard>
        </div>
      </div>

      {/* Recommendations List */}
      <div className="insights-box">
        <h2 className="insights-box__title">📋 Recommendations ({filteredRecs.length})</h2>
        <div className="section">
          {filteredRecs.map((rec) => (
            <div key={rec.id} className="card" style={{ marginBottom: '1.5rem' }}>
              <div className="card-header">
                <h3 style={{ margin: 0, display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                  {getPriorityIcon(rec.priority_score)}
                  {rec.title}
                </h3>
                <div style={{ display: 'flex', gap: '0.5rem' }}>
                  <span 
                    className="badge"
                    style={{ 
                      backgroundColor: getImpactColor(rec.impact_score),
                      color: 'white'
                    }}
                  >
                    Impact: {rec.impact_score}/10
                  </span>
                  <span className="badge" style={{ backgroundColor: 'var(--secondary-color)', color: 'white' }}>
                    {rec.timeline}
                  </span>
                  <span className="badge" style={{ backgroundColor: 'var(--primary-color)', color: 'white' }}>
                    {rec.category}
                  </span>
                </div>
              </div>
              
              <div style={{ padding: '1rem' }}>
                <p style={{ color: 'var(--text-secondary)', marginBottom: '1rem' }}>{rec.description}</p>
                
                <div className="metrics-grid" style={{ marginBottom: '1rem' }}>
                  <StandardCard
                    title="Priority Score"
                    variant="metric"
                    status={rec.priority_score >= 8 ? "critical" : rec.priority_score >= 6 ? "warning" : "good"}
                  >
                    <div className="metric-value">{rec.priority_score.toFixed(1)}/10</div>
                  </StandardCard>
                  
                  <StandardCard
                    title="Urgency"
                    variant="metric"
                    status="warning"
                  >
                    <div className="metric-value">{rec.urgency_score}/10</div>
                  </StandardCard>
                  
                  <StandardCard
                    title="Persona"
                    variant="metric"
                    status="good"
                  >
                    <div className="metric-value text-sm">{rec.persona}</div>
                  </StandardCard>
                  
                  <StandardCard
                    title="Source"
                    variant="metric"
                    status="good"
                  >
                    <div className="metric-value text-sm">{rec.source}</div>
                  </StandardCard>
                </div>

                {rec.url && (
                  <div style={{ marginBottom: '1rem' }}>
                    <strong>🔗 Page URL:</strong>
                    <br />
                    <a href={rec.url} target="_blank" rel="noopener noreferrer" style={{ color: 'var(--primary-color)' }}>
                      {rec.url}
                    </a>
                  </div>
                )}

                {rec.evidence && rec.evidence.length > 20 && (
                  <div>
                    <EvidenceDisplay
                      evidence={[{ type: 'evidence' as const, content: rec.evidence }]}
                      title="Supporting Evidence"
                      collapsible={true}
                      defaultExpanded={false}
                    />
                  </div>
                )}
              </div>
            </div>
          ))}
        </div>
      </div>
    </>
  )
}

export default StrategicRecommendations 