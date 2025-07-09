import { useState } from 'react'
import { useQuery } from '@tanstack/react-query'
import { EvidenceDisplay } from '../components/EvidenceDisplay'
import { PlotlyChart } from '../components/PlotlyChart'

const apiBase = import.meta.env.VITE_API_URL || 'http://localhost:3000'

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

function StrategicRecommendations() {
  const [selectedTier, setSelectedTier] = useState('All')
  const [selectedBusinessImpact, setSelectedBusinessImpact] = useState('All')
  const [selectedTimeline, setSelectedTimeline] = useState('All')
  const [viewMode, setViewMode] = useState('executive')

  const { data: strategicData, isLoading: strategicLoading } = useQuery({
    queryKey: ['strategic-intelligence', selectedTier, selectedBusinessImpact, selectedTimeline],
    queryFn: async () => {
      const params = new URLSearchParams()
      if (selectedTier !== 'All') params.append('tier', selectedTier)
      if (selectedBusinessImpact !== 'All') params.append('business_impact', selectedBusinessImpact)
      if (selectedTimeline !== 'All') params.append('timeline', selectedTimeline)
      
      const res = await fetch(`${apiBase}/api/strategic-intelligence?${params.toString()}`)
      if (!res.ok) throw new Error('Failed to load strategic intelligence')
      return await res.json() as StrategicIntelligence
    }
  })

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

  if (strategicLoading) {
    return (
      <div className="page-container">
        <div className="main-header">
          <h1>🎯 Strategic Intelligence</h1>
          <p>Loading business-focused strategic analysis...</p>
        </div>
      </div>
    )
  }

  if (!strategicData) {
    return (
      <div className="page-container">
        <div className="main-header">
          <h1>🎯 Strategic Intelligence</h1>
          <p>No strategic data available</p>
        </div>
      </div>
    )
  }

  return (
    <div className="page-container">
      {/* Header */}
      <div className="main-header">
        <h1>🎯 Strategic Intelligence</h1>
        <p>Business-focused strategic recommendations with ROI impact and competitive context</p>
      </div>

      {/* Executive Summary - Always visible */}
      <div className="insights-box" style={{ backgroundColor: '#f8f9fa', border: '2px solid #007bff' }}>
        <h2>📊 Executive Summary</h2>
        <div className="summary-grid" style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(250px, 1fr))', gap: '1.5rem' }}>
          <div className="metric-card" style={{ backgroundColor: '#fff', padding: '1.5rem', borderRadius: '8px', border: '1px solid #dee2e6' }}>
            <div className="metric-value" style={{ fontSize: '2rem', fontWeight: 'bold', color: '#dc3545' }}>
              {formatCurrency(strategicData.executiveSummary.pipelineRisk)}
            </div>
            <div className="metric-label" style={{ color: '#6c757d' }}>Pipeline Risk</div>
            <div className="metric-description" style={{ fontSize: '0.875rem', color: '#6c757d', marginTop: '0.5rem' }}>
              Annual revenue at risk from brand health issues
            </div>
          </div>

          <div className="metric-card" style={{ backgroundColor: '#fff', padding: '1.5rem', borderRadius: '8px', border: '1px solid #dee2e6' }}>
            <div className="metric-value" style={{ fontSize: '2rem', fontWeight: 'bold', color: '#28a745' }}>
              {formatCurrency(strategicData.executiveSummary.quickWinValue)}
            </div>
            <div className="metric-label" style={{ color: '#6c757d' }}>Quick Win Value</div>
            <div className="metric-description" style={{ fontSize: '0.875rem', color: '#6c757d', marginTop: '0.5rem' }}>
              Immediate revenue opportunity from low-effort fixes
            </div>
          </div>

          <div className="metric-card" style={{ backgroundColor: '#fff', padding: '1.5rem', borderRadius: '8px', border: '1px solid #dee2e6' }}>
            <div className="metric-value" style={{ fontSize: '2rem', fontWeight: 'bold', color: '#007bff' }}>
              {formatCurrency(strategicData.executiveSummary.strategicInvestmentROI)}
            </div>
            <div className="metric-label" style={{ color: '#6c757d' }}>Strategic Investment ROI</div>
            <div className="metric-description" style={{ fontSize: '0.875rem', color: '#6c757d', marginTop: '0.5rem' }}>
              Expected 30% ROI on strategic brand investments
            </div>
          </div>

          <div className="metric-card" style={{ backgroundColor: '#fff', padding: '1.5rem', borderRadius: '8px', border: '1px solid #dee2e6' }}>
            <div className="metric-value" style={{ fontSize: '2rem', fontWeight: 'bold', color: '#fd7e14' }}>
              {strategicData.executiveSummary.competitiveGaps}
            </div>
            <div className="metric-label" style={{ color: '#6c757d' }}>Competitive Gaps</div>
            <div className="metric-description" style={{ fontSize: '0.875rem', color: '#6c757d', marginTop: '0.5rem' }}>
              Critical issues creating competitive vulnerability
            </div>
          </div>
        </div>

        {/* Competitive Context */}
        <div className="competitive-context" style={{ marginTop: '2rem', padding: '1.5rem', backgroundColor: '#fff', borderRadius: '8px', border: '1px solid #dee2e6' }}>
          <h3>🏆 Competitive Position</h3>
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(300px, 1fr))', gap: '1.5rem' }}>
            <div>
              <div style={{ display: 'flex', alignItems: 'center', gap: '1rem', marginBottom: '1rem' }}>
                <span style={{ fontSize: '1.5rem', fontWeight: 'bold', color: strategicData.competitiveContext.overallPosition === 'Above Average' ? '#28a745' : '#dc3545' }}>
                  {strategicData.competitiveContext.currentScore.toFixed(1)}/10
                </span>
                <span style={{ color: '#6c757d' }}>vs {strategicData.competitiveContext.benchmarkScore}/10 industry average</span>
              </div>
              <div style={{ 
                width: '100%', 
                height: '8px', 
                backgroundColor: '#e9ecef', 
                borderRadius: '4px',
                overflow: 'hidden'
              }}>
                <div style={{ 
                  width: `${(strategicData.competitiveContext.currentScore / 10) * 100}%`,
                  height: '100%',
                  backgroundColor: strategicData.competitiveContext.overallPosition === 'Above Average' ? '#28a745' : '#dc3545'
                }} />
              </div>
            </div>
            <div>
              <p style={{ fontWeight: 'bold', color: strategicData.competitiveContext.overallPosition === 'Above Average' ? '#28a745' : '#dc3545' }}>
                {strategicData.competitiveContext.overallPosition}
              </p>
              <p style={{ color: '#6c757d', fontSize: '0.875rem' }}>
                {strategicData.competitiveContext.marketOpportunity}
              </p>
            </div>
          </div>
        </div>
      </div>

      {/* Filters */}
      <div className="insights-box">
        <h2>🎛️ Strategic Focus</h2>
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: '1rem' }}>
          <div>
            <label style={{ display: 'block', marginBottom: '0.5rem', fontWeight: '600' }}>
              Content Tier
            </label>
            <select 
              value={selectedTier}
              onChange={(e) => setSelectedTier(e.target.value)}
              style={{ width: '100%', padding: '0.5rem', borderRadius: '4px', border: '1px solid #D1D5DB' }}
            >
              <option value="All">All Tiers</option>
              <option value="Tier 1">Tier 1 (Strategic)</option>
              <option value="Tier 2">Tier 2 (Tactical)</option>
              <option value="Tier 3">Tier 3 (Operational)</option>
            </select>
          </div>

          <div>
            <label style={{ display: 'block', marginBottom: '0.5rem', fontWeight: '600' }}>
              Business Impact
            </label>
            <select 
              value={selectedBusinessImpact}
              onChange={(e) => setSelectedBusinessImpact(e.target.value)}
              style={{ width: '100%', padding: '0.5rem', borderRadius: '4px', border: '1px solid #D1D5DB' }}
            >
              <option value="All">All Impact Levels</option>
              <option value="High">High Impact</option>
              <option value="Medium">Medium Impact</option>
              <option value="Low">Low Impact</option>
            </select>
          </div>

          <div>
            <label style={{ display: 'block', marginBottom: '0.5rem', fontWeight: '600' }}>
              Timeline
            </label>
            <select 
              value={selectedTimeline}
              onChange={(e) => setSelectedTimeline(e.target.value)}
              style={{ width: '100%', padding: '0.5rem', borderRadius: '4px', border: '1px solid #D1D5DB' }}
            >
              <option value="All">All Timelines</option>
              <option value="0-7 days">Immediate (0-7 days)</option>
              <option value="0-30 days">Short-term (0-30 days)</option>
              <option value="30-90 days">Medium-term (30-90 days)</option>
              <option value="90+ days">Long-term (90+ days)</option>
            </select>
          </div>

          <div>
            <label style={{ display: 'block', marginBottom: '0.5rem', fontWeight: '600' }}>
              View Mode
            </label>
            <select 
              value={viewMode}
              onChange={(e) => setViewMode(e.target.value)}
              style={{ width: '100%', padding: '0.5rem', borderRadius: '4px', border: '1px solid #D1D5DB' }}
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

                <div className="theme-metrics" style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(150px, 1fr))', gap: '1rem', marginBottom: '1rem' }}>
                  <div className="metric">
                    <div style={{ fontSize: '1.5rem', fontWeight: 'bold', color: '#007bff' }}>
                      {theme.currentScore.toFixed(1)}/10
                    </div>
                    <div style={{ fontSize: '0.875rem', color: '#6c757d' }}>Current Score</div>
                  </div>
                  <div className="metric">
                    <div style={{ fontSize: '1.5rem', fontWeight: 'bold', color: '#28a745' }}>
                      {theme.targetScore.toFixed(1)}/10
                    </div>
                    <div style={{ fontSize: '0.875rem', color: '#6c757d' }}>Target Score</div>
                  </div>
                  <div className="metric">
                    <div style={{ fontSize: '1.5rem', fontWeight: 'bold', color: '#fd7e14' }}>
                      {theme.affectedPages}
                    </div>
                    <div style={{ fontSize: '0.875rem', color: '#6c757d' }}>Pages Affected</div>
                  </div>
                  <div className="metric">
                    <div style={{ fontSize: '1.5rem', fontWeight: 'bold', color: '#dc3545' }}>
                      {formatCurrency(theme.revenueImpact)}
                    </div>
                    <div style={{ fontSize: '0.875rem', color: '#6c757d' }}>Revenue Impact</div>
                  </div>
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

                <div className="recommendation-metrics" style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(150px, 1fr))', gap: '1rem', marginBottom: '1rem' }}>
                  <div className="metric">
                    <div style={{ fontSize: '1.5rem', fontWeight: 'bold', color: '#28a745' }}>
                      {formatCurrency(rec.revenueImpact)}
                    </div>
                    <div style={{ fontSize: '0.875rem', color: '#6c757d' }}>Revenue Impact</div>
                  </div>
                  <div className="metric">
                    <div style={{ fontSize: '1.5rem', fontWeight: 'bold', color: '#007bff' }}>
                      +{rec.conversionUplift}%
                    </div>
                    <div style={{ fontSize: '0.875rem', color: '#6c757d' }}>Conversion Uplift</div>
                  </div>
                  <div className="metric">
                    <div style={{ fontSize: '1.5rem', fontWeight: 'bold', color: '#fd7e14' }}>
                      {rec.currentScore.toFixed(1)}/10
                    </div>
                    <div style={{ fontSize: '0.875rem', color: '#6c757d' }}>Current Score</div>
                  </div>
                  <div className="metric">
                    <div style={{ fontSize: '1.5rem', fontWeight: 'bold', color: '#dc3545' }}>
                      {rec.implementationEffort}
                    </div>
                    <div style={{ fontSize: '0.875rem', color: '#6c757d' }}>Implementation Effort</div>
                  </div>
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

                <div className="tier-metrics" style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(120px, 1fr))', gap: '1rem' }}>
                  <div className="metric">
                    <div style={{ fontSize: '1.5rem', fontWeight: 'bold', color: '#007bff' }}>
                      {data.averageScore.toFixed(1)}/10
                    </div>
                    <div style={{ fontSize: '0.875rem', color: '#6c757d' }}>Average Score</div>
                  </div>
                  <div className="metric">
                    <div style={{ fontSize: '1.5rem', fontWeight: 'bold', color: '#6c757d' }}>
                      {data.pages}
                    </div>
                    <div style={{ fontSize: '0.875rem', color: '#6c757d' }}>Total Pages</div>
                  </div>
                  <div className="metric">
                    <div style={{ fontSize: '1.5rem', fontWeight: 'bold', color: '#dc3545' }}>
                      {data.criticalIssues}
                    </div>
                    <div style={{ fontSize: '0.875rem', color: '#6c757d' }}>Critical Issues</div>
                  </div>
                  <div className="metric">
                    <div style={{ fontSize: '1.5rem', fontWeight: 'bold', color: '#28a745' }}>
                      {data.quickWins}
                    </div>
                    <div style={{ fontSize: '0.875rem', color: '#6c757d' }}>Quick Wins</div>
                  </div>
                  <div className="metric">
                    <div style={{ fontSize: '1.5rem', fontWeight: 'bold', color: '#fd7e14' }}>
                      {formatCurrency(data.revenueImpact)}
                    </div>
                    <div style={{ fontSize: '0.875rem', color: '#6c757d' }}>Revenue Impact</div>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  )
}

export default StrategicRecommendations 