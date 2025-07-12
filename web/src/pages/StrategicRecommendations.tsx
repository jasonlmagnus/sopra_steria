import { useState } from 'react'
import { useQuery } from '@tanstack/react-query'
import { EvidenceDisplay } from '../components/EvidenceDisplay'
import { PlotlyChart } from '../components/PlotlyChart'
import StandardCard from '../components/StandardCard'
// Import unified dashboard styles
import '../styles/dashboard.css'

const apiBase = import.meta.env.VITE_API_URL || 'http://localhost:3000'

interface StrategicIntelligence {
  executiveSummary: {
    totalRecommendations: number;
    highImpactOpportunities: number;
    quickWinOpportunities: number;
    criticalIssues: number;
    overallScore: number;
  };
  strategicThemes: Array<{
    id: string;
    title: string;
    description: string;
    currentScore: number;
    targetScore: number;
    businessImpact: string;
    affectedPages: number;
    competitiveRisk: string;
    keyInsights: string[];
    soWhat: string;
  }>;
  recommendations: Array<{
    id: string;
    title: string;
    description: string;
    businessImpact: string;
    implementationEffort: string;
    timeline: string;
    tier: string;
    persona: string;
    currentScore: number;
    targetScore: number;
    evidence: string;
    soWhat: string;
    implementationSteps: string[];
    success_metrics: string[];
  }>;
  competitiveContext: {
    currentScore: number;
    benchmarkScore: number;
    marketOpportunity: string;
    vulnerabilities: string[];
    overallPosition: string;
  };
  tierAnalysis: {
    [key: string]: {
      name: string;
      avgScore: number;
      pageCount: number;
      criticalIssues: number;
      quickWins: number;
      priority: string;
      businessContext: string;
    };
  };
  implementationRoadmap: Array<{
    phase: string;
    focus: string;
    recommendations: string[];
    expectedImpact: string;
  }>;
  businessImpact: {
    optimizationPotential: number;
    improvementAreas: number;
    competitiveAdvantage: string[];
    successStories: string[];
  };
}

// Add fallback data structure for basic recommendations
interface BasicRecommendation {
  id: string
  title: string
  description: string
  impact_score: number
  urgency_score: number
  timeline: string
  priority_score: number
  page_id: string
  persona: string
  url: string
  evidence: string
}

function StrategicRecommendations() {
  const [selectedTier, setSelectedTier] = useState('All')
  const [selectedBusinessImpact, setSelectedBusinessImpact] = useState('All')
  const [selectedTimeline, setSelectedTimeline] = useState('All')
  const [viewMode, setViewMode] = useState('executive')

  // Primary data source - strategic intelligence
  const { data: strategicData, isLoading: strategicLoading, error: strategicError } = useQuery({
    queryKey: ['strategic-intelligence', selectedTier, selectedBusinessImpact, selectedTimeline],
    queryFn: async () => {
      const params = new URLSearchParams()
      if (selectedTier !== 'All') params.append('tier', selectedTier)
      if (selectedBusinessImpact !== 'All') params.append('business_impact', selectedBusinessImpact)
      if (selectedTimeline !== 'All') params.append('timeline', selectedTimeline)
      
      const res = await fetch(`${apiBase}/api/strategic-intelligence?${params.toString()}`)
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
      
      const res = await fetch(`${apiBase}/api/full-recommendations?${params.toString()}`)
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

  const getImpactColor = (impact: string): string => {
    switch (impact.toLowerCase()) {
      case 'high': return '#dc3545'
      case 'medium': return '#fd7e14'
      case 'low': return '#28a745'
      default: return '#6c757d'
    }
  }

  const getRiskColor = (risk: string): string => {
    switch (risk.toLowerCase()) {
      case 'high': return '#dc3545'
      case 'medium': return '#ffc107'
      case 'low': return '#28a745'
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
        size: rec.currentScore * 3, // Scale marker size by current score
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
        <p className="page-subtitle">Strategic recommendations with competitive context and implementation roadmap</p>
      </div>

      {/* Executive Summary - Always visible */}
      <div className="insights-box">
        <h2 className="insights-box__title">📊 Executive Summary</h2>
        <div className="metrics-grid">
          <StandardCard
            title="Total Recommendations"
            variant="metric"
            status="good"
          >
            <div className="metric-value">{strategicData.executiveSummary.totalRecommendations}</div>
            <div className="metric-description">Strategic recommendations identified</div>
          </StandardCard>

          <StandardCard
            title="High Impact Opportunities"
            variant="metric"
            status="excellent"
          >
            <div className="metric-value">{strategicData.executiveSummary.highImpactOpportunities}</div>
            <div className="metric-description">High-impact improvement opportunities</div>
          </StandardCard>

          <StandardCard
            title="Quick Win Opportunities"
            variant="metric"
            status="good"
          >
            <div className="metric-value">{strategicData.executiveSummary.quickWinOpportunities}</div>
            <div className="metric-description">Quick wins for immediate impact</div>
          </StandardCard>

          <StandardCard
            title="Critical Issues"
            variant="metric"
            status="critical"
          >
            <div className="metric-value">{strategicData.executiveSummary.criticalIssues}</div>
            <div className="metric-description">Critical issues requiring immediate attention</div>
          </StandardCard>
        </div>

        {/* Competitive Context */}
        <div className="insights-box" className="mt-2xl">
          <h3>🏆 Competitive Position</h3>
          <div className="grid grid--2">
            <div>
              <div className="flex-center">
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
          <div className="grid-gap-xl">
            {strategicData.strategicThemes.map((theme) => (
              <div key={theme.id} className="theme-card" style={{ 
                border: '1px solid #dee2e6', 
                borderRadius: '8px', 
                padding: '1.5rem',
                backgroundColor: '#fff'
              }}>
                <div className="theme-header" className="flex">
                  <h3 className="margin-0">{theme.title}</h3>
                  <div className="theme-badges" className="flex-gap-sm">
                    <span className="badge" className="font-semibold">
                      {theme.businessImpact} Impact
                    </span>
                    <span className="badge" className="font-semibold">
                      {theme.competitiveRisk} Risk
                    </span>
                  </div>
                </div>

                <p className="mb-lg">{theme.description}</p>

                <div className="grid grid--auto-150 gap-md" className="mb-lg">
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
                </div>

                <div className="theme-insights" className="mb-lg">
                  <h4>Key Insights</h4>
                  <ul className="pl-xl">
                    {theme.keyInsights.map((insight, idx) => (
                      <li key={idx} className="mb-md">{insight}</li>
                    ))}
                  </ul>
                </div>

                <div className="theme-so-what" className="p-lg">
                  <h4 style={{ color: '#007bff', marginBottom: '0.5rem' }}>💡 So What?</h4>
                  <p className="font-semibold">{theme.soWhat}</p>
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
          <div className="grid-gap-xl">
            {strategicData.recommendations.map((rec) => (
              <div key={rec.id} className="recommendation-card" style={{ 
                border: '1px solid #dee2e6', 
                borderRadius: '8px', 
                padding: '1.5rem',
                backgroundColor: rec.businessImpact === 'High' ? '#fef2f2' : rec.businessImpact === 'Medium' ? '#fffbeb' : '#f0fdf4'
              }}>
                <div className="recommendation-header" className="flex">
                  <h3 className="margin-0">{rec.title}</h3>
                  <div className="recommendation-badges" className="flex-gap-sm">
                    <span className="badge" className="font-semibold">
                      {rec.businessImpact} Impact
                    </span>
                    <span className="badge" className="font-semibold">
                      {rec.timeline}
                    </span>
                  </div>
                </div>

                <p className="mb-lg">{rec.description}</p>

                <div className="grid grid--auto-150 gap-md" className="mb-lg">
                  <StandardCard
                    title="Current Score"
                    variant="metric"
                    status={rec.currentScore >= 8 ? "excellent" : rec.currentScore >= 6 ? "good" : "warning"}
                  >
                    <div className="metric-value">{rec.currentScore.toFixed(1)}/10</div>
                  </StandardCard>
                  <StandardCard
                    title="Target Score"
                    variant="metric"
                    status="excellent"
                  >
                    <div className="metric-value">{rec.targetScore.toFixed(1)}/10</div>
                  </StandardCard>
                  <StandardCard
                    title="Implementation Effort"
                    variant="metric"
                    status={rec.implementationEffort === "Low" ? "excellent" : rec.implementationEffort === "Medium" ? "warning" : "critical"}
                  >
                    <div className="metric-value">{rec.implementationEffort}</div>
                  </StandardCard>
                  <StandardCard
                    title="Timeline"
                    variant="metric"
                    status="good"
                  >
                    <div className="metric-value">{rec.timeline}</div>
                  </StandardCard>
                </div>

                <div className="recommendation-so-what" className="mb-lg">
                  <h4 style={{ color: '#007bff', marginBottom: '0.5rem' }}>💡 So What?</h4>
                  <p className="font-semibold">{rec.soWhat}</p>
                </div>

                <div className="recommendation-evidence" className="mb-lg">
                  <EvidenceDisplay
                    evidence={[{ type: 'evidence' as const, content: rec.evidence }]}
                    title="Supporting Evidence"
                    collapsible={true}
                    defaultExpanded={false}
                  />
                </div>

                <div className="recommendation-implementation">
                  <h4>🔧 Implementation Steps</h4>
                  <ol className="pl-xl">
                    {rec.implementationSteps.map((step, idx) => (
                      <li key={idx} className="mb-md">{step}</li>
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
          <div className="grid-gap-xl">
            {strategicData.implementationRoadmap.map((phase, idx) => (
              <div key={idx} className="roadmap-phase" style={{ 
                border: '1px solid #dee2e6', 
                borderRadius: '8px', 
                padding: '1.5rem',
                backgroundColor: '#fff'
              }}>
                <div className="phase-header" className="flex">
                  <h3 className="margin-0">{phase.phase}</h3>
                  <div className="font-bold">
                    {phase.expectedImpact}
                  </div>
                </div>
                <p className="mb-lg">{phase.focus}</p>
                
                <div className="phase-recommendations" className="mb-lg">
                  <h4>📋 Key Recommendations</h4>
                  <ul className="pl-xl">
                    {phase.recommendations.map((rec, recIdx) => (
                      <li key={recIdx} className="mb-md">{rec}</li>
                    ))}
                  </ul>
                </div>

                <div className="phase-impact">
                  <h4>🎯 Expected Impact</h4>
                  <p className="font-semibold">{phase.expectedImpact}</p>
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
          <div className="matrix-legend" className="mt-lg">
            <h4>Legend:</h4>
            <p><strong>Size:</strong> Current score (larger = higher current score)</p>
            <p><strong>Color:</strong> Timeline (Red = Immediate, Orange = Short-term, Yellow = Medium-term, Green = Long-term)</p>
          </div>
        </div>
      )}

      {/* Tier Analysis */}
      {viewMode === 'executive' && (
        <div className="insights-box">
          <h2>📈 Tier-Level Intelligence</h2>
          <div className="grid-gap-xl">
            {Object.entries(strategicData.tierAnalysis).map(([tier, data]) => (
              <div key={tier} className="tier-card" style={{ 
                border: '1px solid #dee2e6', 
                borderRadius: '8px', 
                padding: '1.5rem',
                backgroundColor: '#f8f9fa'
              }}>
                <div className="tier-header" className="flex">
                  <h3 className="margin-0">{tier}</h3>
                  <span className="badge" className="font-semibold">
                    Tier Analysis
                  </span>
                </div>

                <div className="grid grid--auto-120 gap-md">
                  <StandardCard
                    title="Average Score"
                    variant="metric"
                    status={data.avgScore >= 8 ? "excellent" : data.avgScore >= 6 ? "good" : "warning"}
                  >
                    <div className="metric-value">{data.avgScore.toFixed(1)}/10</div>
                  </StandardCard>
                  <StandardCard
                    title="Page Count"
                    variant="metric"
                    status="good"
                  >
                    <div className="metric-value">{data.pageCount}</div>
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
                </div>
                
                <div className="mt-lg">
                  <p className="text-secondary">
                    <strong>Priority:</strong> {data.priority}
                  </p>
                  <p className="text-secondary">
                    <strong>Business Context:</strong> {data.businessContext}
                  </p>
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
            <div key={rec.id} className="card" className="mb-xl">
              <div className="card-header">
                <h3 className="flex-center">
                  {getPriorityIcon(rec.priority_score)}
                  {rec.title}
                </h3>
                <div className="flex-gap-sm">
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
                </div>
              </div>
              
              <div className="p-lg">
                <p className="mb-lg">{rec.description}</p>
                
                <div className="metrics-grid" className="mb-lg">
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
                    title="Page ID"
                    variant="metric"
                    status="good"
                  >
                    <div className="metric-value text-sm">{rec.page_id}</div>
                  </StandardCard>
                </div>

                {rec.url && (
                  <div className="mb-lg">
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