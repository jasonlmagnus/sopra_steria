import React, { useState, useEffect } from 'react'
import '../styles/dashboard.css'

interface SocialMediaData {
  platform: string
  platform_display: string
  persona_clean: string
  raw_score: number
  engagement_numeric: number
  sentiment_numeric: number
  critical_issue_flag: boolean
  success_flag: boolean
  quick_win_flag: boolean
  url: string
  evidence: string
  effective_copy_examples: string
  ineffective_copy_examples: string
  trust_credibility_assessment: string
  business_impact_analysis: string
  tier: string
  audited_ts: string
}

interface PlatformMetrics {
  Platform: string
  Platform_Code: string
  Average_Score: number
  Score_Range: string
  Status: string
  Status_Color: string
  Total_Entries: number
  High_Performers: number
  Moderate_Performers: number
  Low_Performers: number
  Avg_Engagement: number
  Avg_Sentiment: number
  Critical_Issues: number
  Success_Cases: number
  Quick_Wins: number
}

interface Insight {
  Category: string
  Insight: string
  Type: string
}

interface Recommendation {
  Platform: string
  Priority: string
  Category: string
  Recommendation: string
  Impact: string
  Timeline: string
}

interface SocialMediaApiResponse {
  data: SocialMediaData[]
  insights: Insight[]
  recommendations: Recommendation[]
  platform_metrics: PlatformMetrics[]
  persona_platform_matrix: Array<{
    persona: string
    platform: string
    score: number
  }>
  analysis_scope: string
  total_entries: number
  platforms_analyzed: string[]
  personas_analyzed: string[]
  error?: string
}

export default function SocialMediaAnalysis() {
  const [data, setData] = useState<SocialMediaApiResponse | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [selectedPlatforms, setSelectedPlatforms] = useState<string[]>([])
  const [selectedPersonas, setSelectedPersonas] = useState<string[]>([])
  const [analysisScope, setAnalysisScope] = useState('All Data')
  const [viewMode, setViewMode] = useState('Overview')
  const [activeTab, setActiveTab] = useState('platform-deep-dive')

  const loadSocialMediaData = async () => {
    try {
      setLoading(true)
      setError(null)

      const params = new URLSearchParams()
      if (selectedPlatforms.length > 0) {
        params.append('platforms', selectedPlatforms.join(','))
      }
      if (selectedPersonas.length > 0) {
        params.append('personas', selectedPersonas.join(','))
      }
      if (analysisScope !== 'All Data') {
        params.append('analysis_scope', analysisScope)
      }

      const response = await fetch(`/api/social-media?${params.toString()}`)
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`)
      }
      
      const result: SocialMediaApiResponse = await response.json()
      setData(result)

      // Set default filters if not set
      if (selectedPlatforms.length === 0) {
        setSelectedPlatforms(result.platforms_analyzed || [])
      }
      if (selectedPersonas.length === 0) {
        setSelectedPersonas(result.personas_analyzed || [])
      }

    } catch (err) {
      console.error('Error loading social media data:', err)
      setError(err instanceof Error ? err.message : 'Unknown error')
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    loadSocialMediaData()
  }, [analysisScope]) // Reload when scope changes

  const handleFilterChange = () => {
    loadSocialMediaData()
  }

  if (loading) {
    return (
      <div className="page-container">
        <div className="loading">
          <div className="loading-spinner"></div>
          <p>Loading social media analysis...</p>
        </div>
      </div>
    )
  }

  if (error) {
    return (
      <div className="page-container">
        <div className="alert alert--error">
          <h2>❌ Error Loading Data</h2>
          <p>{error}</p>
          <button onClick={loadSocialMediaData} className="btn btn--primary">
            🔄 Retry
          </button>
        </div>
      </div>
    )
  }

  if (!data || data.error) {
    return (
      <div className="page-container">
        <div className="empty-state">
          <h2>📊 No Social Media Data</h2>
          <p>{data?.error || 'No social media data available for analysis.'}</p>
        </div>
      </div>
    )
  }

  const getHealthStatus = (score: number) => {
    if (score >= 7) return { status: "🟢 Healthy", color: "#10B981" }
    if (score >= 5) return { status: "🟡 Moderate", color: "#F59E0B" }
    if (score >= 3) return { status: "🟠 At Risk", color: "#F97316" }
    return { status: "🔴 Critical", color: "#EF4444" }
  }

  const overallAvg = data.data.reduce((sum, item) => sum + item.raw_score, 0) / data.data.length
  const healthInfo = getHealthStatus(overallAvg)
  const twitterCritical = data.data.some(item => item.platform === 'twitter' && item.raw_score < 2)

  return (
    <div className="page-container">
      {/* Header Section */}
      <div className="main-header">
        <h1>🔍 Social Media Analysis</h1>
        <p>Cross-platform brand presence and engagement insights</p>
      </div>

      {/* Executive Summary */}
      <div className="section">
        <h2 className="section__title">📊 Executive Summary</h2>
        
        {/* Critical Alert Banner */}
        {twitterCritical && (
          <div className="alert alert--warning mb-4">
            <h4 className="mb-2">⚠️ Attention Required</h4>
            <p className="mb-0">
              Twitter/X platform showing low performance scores - review and optimization recommended
            </p>
          </div>
        )}

        {/* Metrics Cards */}
        <div className="metrics-grid">
          <OverallHealthCard score={overallAvg} healthInfo={healthInfo} />
          <TopPlatformCard platformMetrics={data.platform_metrics} />
          <WeakestPlatformCard platformMetrics={data.platform_metrics} />
          <PlatformCoverageCard platformMetrics={data.platform_metrics} />
          <CriticalIssuesCard data={data.data} />
          <QuickWinsCard data={data.data} />
        </div>
      </div>

      {/* Analysis Controls */}
      <div className="section">
        <h2 className="section__title">🎯 Analysis Controls</h2>
        <div className="filter-controls">
          <div className="filter-group">
            <label className="filter-label">📱 Select Platforms</label>
            <div className="multi-select">
              {(data.platforms_analyzed || []).map(platform => (
                <div key={platform} className="multi-select-option">
                  <input
                    type="checkbox"
                    id={`platform-${platform}`}
                    checked={selectedPlatforms.includes(platform)}
                    onChange={(e) => {
                      if (e.target.checked) {
                        setSelectedPlatforms([...selectedPlatforms, platform]);
                      } else {
                        setSelectedPlatforms(selectedPlatforms.filter(p => p !== platform));
                      }
                    }}
                  />
                  <label htmlFor={`platform-${platform}`}>{platform}</label>
                </div>
              ))}
            </div>
            {selectedPlatforms.length > 0 && (
              <div className="selected-items">
                {selectedPlatforms.map(platform => (
                  <div key={platform} className="selected-item">
                    {platform}
                    <button 
                      onClick={() => setSelectedPlatforms(selectedPlatforms.filter(p => p !== platform))}
                    >
                      ×
                    </button>
                  </div>
                ))}
              </div>
            )}
          </div>
          
          <div className="filter-group">
            <label className="filter-label">👥 Select Personas</label>
            <div className="multi-select">
              {(data.personas_analyzed || []).map(persona => (
                <div key={persona} className="multi-select-option">
                  <input
                    type="checkbox"
                    id={`persona-${persona}`}
                    checked={selectedPersonas.includes(persona)}
                    onChange={(e) => {
                      if (e.target.checked) {
                        setSelectedPersonas([...selectedPersonas, persona]);
                      } else {
                        setSelectedPersonas(selectedPersonas.filter(p => p !== persona));
                      }
                    }}
                  />
                  <label htmlFor={`persona-${persona}`}>{persona}</label>
                </div>
              ))}
            </div>
            {selectedPersonas.length > 0 && (
              <div className="selected-items">
                {selectedPersonas.map(persona => (
                  <div key={persona} className="selected-item">
                    {persona}
                    <button 
                      onClick={() => setSelectedPersonas(selectedPersonas.filter(p => p !== persona))}
                    >
                      ×
                    </button>
                  </div>
                ))}
              </div>
            )}
          </div>
          
          <div className="filter-group">
            <label className="filter-label">🌍 Analysis Scope</label>
            <select className="filter-select" value={analysisScope} onChange={(e) => setAnalysisScope(e.target.value)}>
              <option>All Data</option>
              <option>High Performers Only</option>
              <option>Problem Areas</option>
              <option>Quick Wins</option>
            </select>
          </div>
          
          <div className="filter-group">
            <label className="filter-label">📊 View Mode</label>
            <div className="checkbox-group">
              {['Overview', 'Detailed Analysis', 'Recommendations'].map(mode => (
                <label key={mode}>
                  <input 
                    type="radio" 
                    name="viewMode" 
                    value={mode}
                    checked={viewMode === mode}
                    onChange={(e) => setViewMode(e.target.value)}
                  />
                  {mode}
                </label>
              ))}
            </div>
          </div>
        </div>
        
        <div className="action-buttons">
          <button 
            onClick={handleFilterChange}
            className="action-button primary"
          >
            🔄 Apply Filters
          </button>
          <button 
            onClick={() => {
              setSelectedPlatforms(data.platforms_analyzed || []);
              setSelectedPersonas(data.personas_analyzed || []);
              setAnalysisScope('All Data');
              setViewMode('Overview');
            }}
            className="action-button secondary"
          >
            🔄 Reset Filters
          </button>
        </div>
      </div>

      {/* Main Content Based on View Mode */}
      {viewMode === 'Overview' && (
        <>
          <PlatformHealthOverview platformMetrics={data.platform_metrics} />
          <PlatformPerformanceAnalysis data={data.data} platformMetrics={data.platform_metrics} />
          <PersonaAnalysis data={data.data} personaPlatformMatrix={data.persona_platform_matrix} />
          <InsightsAndRecommendations insights={data.insights} recommendations={data.recommendations} />
        </>
      )}

      {viewMode === 'Detailed Analysis' && (
        <DetailedAnalysisTabs 
          data={data.data} 
          platformMetrics={data.platform_metrics}
          activeTab={activeTab}
          setActiveTab={setActiveTab}
        />
      )}

      {viewMode === 'Recommendations' && (
        <>
          <InsightsAndRecommendations insights={data.insights} recommendations={data.recommendations} />
          <ActionPriorityMatrix recommendations={data.recommendations} />
        </>
      )}
    </div>
  )
}

// Component functions
function OverallHealthCard({ score, healthInfo }: { score: number, healthInfo: { status: string, color: string } }) {
  return (
    <div className="metric-card">
      <h4 className="metric-label">Overall Health</h4>
      <div className="metric-value" style={{ color: healthInfo.color }}>
        {score.toFixed(1)}/10
      </div>
      <div className="bg-gray-100 rounded" style={{ height: '10px', margin: '0.5rem 0' }}>
        <div 
          className="rounded"
          style={{ 
            background: healthInfo.color, 
            width: `${score * 10}%`, 
            height: '100%'
          }}
        />
      </div>
      <div className="text-sm text-secondary">{healthInfo.status}</div>
    </div>
  )
}

function TopPlatformCard({ platformMetrics }: { platformMetrics: PlatformMetrics[] }) {
  const topPlatform = platformMetrics.reduce((prev, current) => 
    prev.Average_Score > current.Average_Score ? prev : current
  )
  
  return (
    <div className="metric-card">
      <h4 className="metric-label">🏆 Top Platform</h4>
      <div className="metric-value text-primary">{topPlatform.Platform}</div>
      <div className="badge badge--excellent">{topPlatform.Average_Score.toFixed(1)}/10</div>
    </div>
  )
}

function WeakestPlatformCard({ platformMetrics }: { platformMetrics: PlatformMetrics[] }) {
  const weakestPlatform = platformMetrics.reduce((prev, current) => 
    prev.Average_Score < current.Average_Score ? prev : current
  )
  
  return (
    <div className="metric-card">
      <h4 className="metric-label">⚠️ Weakest Platform</h4>
      <div className="metric-value text-primary">{weakestPlatform.Platform}</div>
      <div className="badge badge--critical">{weakestPlatform.Average_Score.toFixed(1)}/10</div>
    </div>
  )
}

function PlatformCoverageCard({ platformMetrics }: { platformMetrics: PlatformMetrics[] }) {
  const totalExpected = 4 // LinkedIn, Instagram, Facebook, Twitter/X
  const coveragePct = (platformMetrics.length / totalExpected) * 100
  
  return (
    <div className="metric-card">
      <h4 className="metric-label">📱 Platform Coverage</h4>
      <div className="metric-value">{platformMetrics.length}/{totalExpected}</div>
      <div className="badge badge--primary">{coveragePct.toFixed(0)}% Active</div>
    </div>
  )
}

function CriticalIssuesCard({ data }: { data: SocialMediaData[] }) {
  const criticalCount = data.filter(item => item.critical_issue_flag).length
  
  return (
    <div className="metric-card">
      <h4 className="metric-label">🚨 Critical Issues</h4>
      <div className="metric-value">{criticalCount}</div>
      <div className={`badge ${criticalCount > 0 ? 'badge--critical' : 'badge--excellent'}`}>
        {criticalCount > 0 ? "Require Immediate Action" : "None"}
      </div>
    </div>
  )
}

function QuickWinsCard({ data }: { data: SocialMediaData[] }) {
  const quickWins = data.filter(item => item.quick_win_flag).length
  
  return (
    <div className="metric-card">
      <h4 className="metric-label">⚡ Quick Wins</h4>
      <div className="metric-value">{quickWins}</div>
      <div className="badge badge--excellent">Easy Improvements</div>
    </div>
  )
}

function PlatformHealthOverview({ platformMetrics }: { platformMetrics: PlatformMetrics[] }) {
  return (
    <div className="section">
      <h2 className="section__title">🏥 Platform Health Overview</h2>
      <div className="metrics-grid">
        {platformMetrics.map(platform => (
          <div key={platform.Platform} className="card card--metric">
            <h3 className="card__title">{platform.Platform}</h3>
            <div className="metric-value">{platform.Average_Score.toFixed(1)}/10</div>
            <div className={`badge badge--${platform.Status_Color}`}>{platform.Status}</div>
            <div className="card__content mt-3">
              <div className="text-sm">Total Entries: {platform.Total_Entries}</div>
              <div className="text-sm">High Performers: {platform.High_Performers}</div>
              <div className="text-sm">Critical Issues: {platform.Critical_Issues}</div>
              <div className="text-sm">Quick Wins: {platform.Quick_Wins}</div>
            </div>
          </div>
        ))}
      </div>
    </div>
  )
}

function PlatformPerformanceAnalysis({ data, platformMetrics }: { 
  data: SocialMediaData[], 
  platformMetrics: PlatformMetrics[] 
}) {
  return (
    <div className="section">
      <h2 className="section__title">📊 Platform Performance Analysis</h2>
      <div className="insights-box">
        <p className="text-lg">Analyzed {data.length} entries across {platformMetrics.length} platforms</p>
        <div className="mt-4">
          {platformMetrics.map(platform => (
            <div key={platform.Platform} className="mb-2">
              <strong>{platform.Platform}:</strong> {platform.Average_Score.toFixed(1)}/10 
              ({platform.High_Performers} high performers, {platform.Critical_Issues} critical issues)
            </div>
          ))}
        </div>
      </div>
    </div>
  )
}

function PersonaAnalysis({ data, personaPlatformMatrix }: { 
  data: SocialMediaData[], 
  personaPlatformMatrix: Array<{persona: string, platform: string, score: number}>
}) {
  const personaPerformance = data.reduce((acc, item) => {
    if (!acc[item.persona_clean]) {
      acc[item.persona_clean] = { total: 0, count: 0 }
    }
    acc[item.persona_clean].total += item.raw_score
    acc[item.persona_clean].count += 1
    return acc
  }, {} as Record<string, {total: number, count: number}>)

  return (
    <div className="section">
      <h2 className="section__title">👥 Persona Analysis</h2>
      <div className="insights-box">
        {Object.entries(personaPerformance).map(([persona, stats]) => (
          <div key={persona} className="mb-3">
            <strong>{persona}:</strong> {(stats.total / stats.count).toFixed(1)}/10 
            <span className="text-sm text-secondary ml-2">
              (based on {stats.count} entries)
            </span>
          </div>
        ))}
      </div>
      
      {personaPlatformMatrix.length > 0 && (
        <div className="mt-5">
          <h3 className="section__subtitle">🎯 Persona-Platform Matrix</h3>
          <div className="metrics-grid">
            {personaPlatformMatrix.map((item, index) => (
              <div key={index} className="card card--metric">
                <div className="card__title text-sm">{item.persona} × {item.platform}</div>
                <div className="metric-value">{item.score.toFixed(1)}/10</div>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  )
}

function InsightsAndRecommendations({ insights, recommendations }: { 
  insights: Insight[],
  recommendations: Recommendation[]
}) {
  return (
    <div className="section">
      <h2 className="section__title">💡 Insights & Recommendations</h2>
      
      <div className="mb-5">
        <h3 className="section__subtitle">🔍 Key Insights</h3>
        <div className="metrics-grid">
          {insights.map((insight, index) => (
            <div key={index} className={`card card--content`}>
              <h4 className="card__title">{insight.Category}</h4>
              <p className="card__content">{insight.Insight}</p>
              <div className={`badge badge--${insight.Type === 'positive' ? 'excellent' : 'warning'}`}>
                {insight.Type}
              </div>
            </div>
          ))}
        </div>
      </div>
      
      <div>
        <h3 className="section__subtitle">🎯 Recommendations</h3>
        <div className="metrics-grid">
          {recommendations.map((rec, index) => (
            <div key={index} className={`card card--content`}>
              <h4 className="card__title">{rec.Platform} - {rec.Category}</h4>
              <p className="card__content">{rec.Recommendation}</p>
              <div className="mt-3">
                <span className={`badge badge--priority-${rec.Priority.toLowerCase()}`}>
                  {rec.Priority}
                </span>
                <span className="badge badge--default ml-2">
                  {rec.Impact}
                </span>
                <span className="badge badge--default ml-2">
                  {rec.Timeline}
                </span>
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  )
}

function DetailedAnalysisTabs({ data, platformMetrics, activeTab, setActiveTab }: { 
  data: SocialMediaData[], 
  platformMetrics: PlatformMetrics[],
  activeTab: string,
  setActiveTab: (tab: string) => void
}) {
  return (
    <div className="section">
      <h2 className="section__title">🔬 Detailed Analysis</h2>
      
      <div className="tabs">
        <div className="tab-buttons">
          {[
            { id: 'platform-deep-dive', label: '📊 Platform Deep Dive' },
            { id: 'content-strategy', label: '📝 Content Strategy' },
            { id: 'performance-analytics', label: '🎯 Performance Analytics' },
            { id: 'quick-wins', label: '⚡ Quick Wins & Actions' }
          ].map(tab => (
            <button 
              key={tab.id}
              className={`tab-button ${activeTab === tab.id ? 'active' : ''}`}
              onClick={() => setActiveTab(tab.id)}
            >
              {tab.label}
            </button>
          ))}
        </div>
        
        <div className="tab-content">
          {activeTab === 'platform-deep-dive' && (
            <PlatformDeepDive data={data} platformMetrics={platformMetrics} />
          )}
          {activeTab === 'content-strategy' && (
            <ContentStrategyAnalysis data={data} />
          )}
          {activeTab === 'performance-analytics' && (
            <PerformanceAnalytics data={data} platformMetrics={platformMetrics} />
          )}
          {activeTab === 'quick-wins' && (
            <QuickWinsAnalysis data={data} />
          )}
        </div>
      </div>
    </div>
  )
}

function PlatformDeepDive({ data, platformMetrics }: { data: SocialMediaData[], platformMetrics: PlatformMetrics[] }) {
  return (
    <div className="evidence-sections">
      <h3 className="section__subtitle">🔍 Platform-Specific Analysis</h3>
      {platformMetrics.map(platform => {
        const platformData = data.filter(item => item.platform_display === platform.Platform)
        return (
          <div key={platform.Platform} className="evidence-section">
            <h4>📱 {platform.Platform} Detailed Analysis</h4>
            
            {/* Platform Overview Stats */}
            <div className="insights-box mb-4">
              <div className="metrics-grid">
                <div className="metric-card">
                  <div className="metric-value">{platform.Average_Score.toFixed(1)}/10</div>
                  <div className="metric-label">Average Score</div>
                </div>
                <div className="metric-card">
                  <div className="metric-value">{platform.Total_Entries}</div>
                  <div className="metric-label">Total Entries</div>
                </div>
                <div className="metric-card">
                  <div className="metric-value">{platform.Score_Range}</div>
                  <div className="metric-label">Score Range</div>
                </div>
                <div className="metric-card">
                  <div className={`badge badge--${platform.Status_Color || 'default'}`}>
                    {platform.Status}
                  </div>
                  <div className="metric-label">Status</div>
                </div>
              </div>
            </div>

            {/* Sample Content Analysis */}
            <div className="evidence-grid">
              <h5 className="mb-3">📋 Sample Content Analysis:</h5>
              {platformData.slice(0, 3).map((item, index) => (
                <div key={index} className="evidence-card">
                  <div className="evidence-header">
                    <h4>{item.platform_display} Content #{index + 1}</h4>
                    <div className="evidence-score">
                      <span className="score-value">{item.raw_score.toFixed(1)}/10</span>
                      <span className="score-label">Score</span>
                    </div>
                  </div>
                  
                  <div className="evidence-content">
                    <div className="evidence-item">
                      <strong>🔗 URL:</strong>
                      <p>
                        <a href={item.url} target="_blank" rel="noopener noreferrer" className="text-primary">
                          {item.url}
                        </a>
                      </p>
                    </div>
                    
                    <div className="evidence-item">
                      <strong>👤 Persona:</strong>
                      <p>{item.persona_clean}</p>
                    </div>
                    
                    {item.effective_copy_examples && (
                      <div className="evidence-item">
                        <strong>✅ Effective Examples:</strong>
                        <p className="effective-copy">{item.effective_copy_examples.substring(0, 200)}...</p>
                      </div>
                    )}
                    
                    {item.ineffective_copy_examples && (
                      <div className="evidence-item">
                        <strong>⚠️ Areas for Improvement:</strong>
                        <p className="ineffective-copy">{item.ineffective_copy_examples.substring(0, 200)}...</p>
                      </div>
                    )}
                    
                    {item.trust_credibility_assessment && (
                      <div className="evidence-item">
                        <strong>🛡️ Trust Assessment:</strong>
                        <p>{item.trust_credibility_assessment.substring(0, 200)}...</p>
                      </div>
                    )}
                    
                    <div className="evidence-item">
                      <strong>🏷️ Flags:</strong>
                      <div className="mt-1">
                        {item.quick_win_flag && <span className="badge badge--excellent mr-1">Quick Win</span>}
                        {item.critical_issue_flag && <span className="badge badge--critical mr-1">Critical</span>}
                        {item.success_flag && <span className="badge badge--excellent mr-1">Success</span>}
                        {!item.quick_win_flag && !item.critical_issue_flag && !item.success_flag && (
                          <span className="badge badge--default">Standard</span>
                        )}
                      </div>
                    </div>
                  </div>
                </div>
              ))}
            </div>
            
            {platformData.length > 3 && (
              <p className="text-center text-secondary mt-3">
                Showing 3 of {platformData.length} {platform.Platform} entries
              </p>
            )}
          </div>
        )
      })}
    </div>
  )
}

function ContentStrategyAnalysis({ data }: { data: SocialMediaData[] }) {
  return (
    <div className="evidence-sections">
      <h3 className="section__subtitle">📝 Content Strategy Analysis</h3>
      <div className="evidence-section">
        <h4>📈 Content Performance by Platform</h4>
        <div className="metrics-grid">
          {Object.entries(data.reduce((acc, item) => {
            if (!acc[item.platform_display]) {
              acc[item.platform_display] = []
            }
            acc[item.platform_display].push(item)
            return acc
          }, {} as Record<string, SocialMediaData[]>)).map(([platform, items]) => (
            <div key={platform} className="card card--metric">
              <h5 className="card__title">{platform}</h5>
              <div className="card__content">
                <div className="mb-2">
                  <strong>Average Engagement:</strong> {(items.reduce((sum, item) => sum + item.engagement_numeric, 0) / items.length).toFixed(2)}
                </div>
                <div className="mb-2">
                  <strong>Average Sentiment:</strong> {(items.reduce((sum, item) => sum + item.sentiment_numeric, 0) / items.length).toFixed(2)}
                </div>
                <div className="mb-2">
                  <strong>Content Volume:</strong> {items.length} pieces analyzed
                </div>
                <div className="metric-value text-sm">
                  {((items.reduce((sum, item) => sum + item.raw_score, 0) / items.length)).toFixed(1)}/10
                </div>
                <div className="metric-label">Avg Score</div>
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  )
}

function PerformanceAnalytics({ data, platformMetrics }: { data: SocialMediaData[], platformMetrics: PlatformMetrics[] }) {
  const overallStats = {
    totalEntries: data.length,
    avgScore: data.reduce((sum, item) => sum + item.raw_score, 0) / data.length,
    criticalIssues: data.filter(item => item.critical_issue_flag).length,
    quickWins: data.filter(item => item.quick_win_flag).length,
    successCases: data.filter(item => item.success_flag).length
  }

  return (
    <div className="evidence-sections">
      <h3 className="section__subtitle">🎯 Performance Analytics</h3>
      
      <div className="evidence-section">
        <h4>📊 Overall Performance Metrics</h4>
        <div className="metrics-grid">
          <div className="metric-card">
            <div className="metric-value">{overallStats.totalEntries}</div>
            <div className="metric-label">📊 Total Entries</div>
          </div>
          <div className="metric-card">
            <div className="metric-value">{overallStats.avgScore.toFixed(1)}/10</div>
            <div className="metric-label">📈 Average Score</div>
          </div>
          <div className="metric-card">
            <div className="metric-value">{overallStats.criticalIssues}</div>
            <div className="metric-label">🚨 Critical Issues</div>
          </div>
          <div className="metric-card">
            <div className="metric-value">{overallStats.quickWins}</div>
            <div className="metric-label">⚡ Quick Wins</div>
          </div>
        </div>
      </div>
      
      <div className="evidence-section">
        <h4>📊 Platform Performance Breakdown</h4>
        <div className="chart-container">
          <table className="data-table">
            <thead>
              <tr>
                <th>Platform</th>
                <th>Avg Score</th>
                <th>High Performers</th>
                <th>Critical Issues</th>
                <th>Quick Wins</th>
              </tr>
            </thead>
            <tbody>
              {platformMetrics.map(platform => (
                <tr key={platform.Platform}>
                  <td><strong>{platform.Platform}</strong></td>
                  <td>
                    <span className={`badge ${platform.Average_Score >= 7 ? 'badge--excellent' : 
                      platform.Average_Score >= 5 ? 'badge--warning' : 'badge--critical'}`}>
                      {platform.Average_Score.toFixed(1)}
                    </span>
                  </td>
                  <td>{platform.High_Performers}</td>
                  <td>{platform.Critical_Issues}</td>
                  <td>{platform.Quick_Wins}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  )
}

function QuickWinsAnalysis({ data }: { data: SocialMediaData[] }) {
  const quickWins = data.filter(item => item.quick_win_flag)
  const criticalIssues = data.filter(item => item.critical_issue_flag)

  return (
    <div className="evidence-sections">
      <h3 className="section__subtitle">⚡ Quick Wins & Immediate Actions</h3>
      
      {quickWins.length > 0 && (
        <div className="evidence-section">
          <h4>🎯 Identified Quick Wins ({quickWins.length})</h4>
          <div className="evidence-grid">
            {quickWins.slice(0, 5).map((item, index) => (
              <div key={index} className="evidence-card">
                <div className="evidence-header">
                  <h4>{item.platform_display} → {item.persona_clean}</h4>
                  <div className="evidence-score">
                    <span className="score-value">{item.raw_score.toFixed(1)}/10</span>
                    <span className="score-label">Current Score</span>
                  </div>
                </div>
                
                <div className="evidence-content">
                  <div className="evidence-item">
                    <strong>🎯 Opportunity:</strong>
                    <p>Optimization potential identified</p>
                  </div>
                  
                  {item.effective_copy_examples && (
                    <div className="evidence-item">
                      <strong>📋 Focus Areas:</strong>
                      <p className="effective-copy">{item.effective_copy_examples.substring(0, 150)}...</p>
                    </div>
                  )}
                  
                  <div className="evidence-item">
                    <strong>🔗 URL:</strong>
                    <p>
                      <a href={item.url} target="_blank" rel="noopener noreferrer" className="text-primary">
                        {item.url}
                      </a>
                    </p>
                  </div>
                  
                  <div className="evidence-item">
                    <div className="badge badge--excellent">Quick Win Opportunity</div>
                  </div>
                </div>
              </div>
            ))}
          </div>
          
          {quickWins.length > 5 && (
            <p className="text-center text-secondary mt-3">
              Showing 5 of {quickWins.length} quick win opportunities
            </p>
          )}
        </div>
      )}

      {criticalIssues.length > 0 && (
        <div className="evidence-section">
          <h4>🚨 Critical Actions Required ({criticalIssues.length})</h4>
          <div className="evidence-grid">
            {criticalIssues.slice(0, 3).map((item, index) => (
              <div key={index} className="evidence-card">
                <div className="evidence-header">
                  <h4>{item.platform_display} → {item.persona_clean}</h4>
                  <div className="evidence-score">
                    <span className="score-value">{item.raw_score.toFixed(1)}/10</span>
                    <span className="score-label">Current Score</span>
                  </div>
                </div>
                
                <div className="evidence-content">
                  <div className="evidence-item">
                    <strong>⚠️ Action Required:</strong>
                    <p>Immediate content review and optimization</p>
                  </div>
                  
                  {item.ineffective_copy_examples && (
                    <div className="evidence-item">
                      <strong>🔍 Issues Identified:</strong>
                      <p className="ineffective-copy">{item.ineffective_copy_examples.substring(0, 150)}...</p>
                    </div>
                  )}
                  
                  <div className="evidence-item">
                    <strong>🔗 URL:</strong>
                    <p>
                      <a href={item.url} target="_blank" rel="noopener noreferrer" className="text-primary">
                        {item.url}
                      </a>
                    </p>
                  </div>
                  
                  <div className="evidence-item">
                    <div className="badge badge--critical">Critical Issue</div>
                  </div>
                </div>
              </div>
            ))}
          </div>
          
          {criticalIssues.length > 3 && (
            <p className="text-center text-secondary mt-3">
              Showing 3 of {criticalIssues.length} critical issues
            </p>
          )}
        </div>
      )}

      <div className="evidence-section">
        <h4>📋 Action Summary</h4>
        <div className="insights-box">
          <div className="metrics-grid">
            <div className="metric-card">
              <div className="metric-value">{quickWins.length}</div>
              <div className="metric-label">Quick Wins Available</div>
            </div>
            <div className="metric-card">
              <div className="metric-value">{criticalIssues.length}</div>
              <div className="metric-label">Critical Issues</div>
            </div>
            <div className="metric-card">
              <div className="metric-value">{data.filter(item => item.success_flag).length}</div>
              <div className="metric-label">Success Cases to Replicate</div>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}

function ActionPriorityMatrix({ recommendations }: { recommendations: Recommendation[] }) {
  const highPriority = recommendations.filter(rec => rec.Priority === 'High')
  const mediumPriority = recommendations.filter(rec => rec.Priority === 'Medium')
  const lowPriority = recommendations.filter(rec => rec.Priority === 'Low')

  return (
    <div className="section">
      <h2 className="section__title">🎯 Action Priority Matrix</h2>
      
      <div className="evidence-sections">
        {highPriority.length > 0 && (
          <div className="evidence-section">
            <h3>🔴 High Priority ({highPriority.length})</h3>
            <div className="evidence-grid">
              {highPriority.map((rec, index) => (
                <div key={index} className="evidence-card">
                  <div className="evidence-header">
                    <h4>{rec.Platform} - {rec.Category}</h4>
                    <div className="badge badge--priority-high">High Priority</div>
                  </div>
                  
                  <div className="evidence-content">
                    <div className="evidence-item">
                      <strong>📋 Recommendation:</strong>
                      <p>{rec.Recommendation}</p>
                    </div>
                    
                    <div className="evidence-item">
                      <strong>📊 Impact:</strong>
                      <p>{rec.Impact}</p>
                    </div>
                    
                    <div className="evidence-item">
                      <strong>⏱️ Timeline:</strong>
                      <p>{rec.Timeline}</p>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}

        {mediumPriority.length > 0 && (
          <div className="evidence-section">
            <h3>🟡 Medium Priority ({mediumPriority.length})</h3>
            <div className="evidence-grid">
              {mediumPriority.map((rec, index) => (
                <div key={index} className="evidence-card">
                  <div className="evidence-header">
                    <h4>{rec.Platform} - {rec.Category}</h4>
                    <div className="badge badge--priority-medium">Medium Priority</div>
                  </div>
                  
                  <div className="evidence-content">
                    <div className="evidence-item">
                      <strong>📋 Recommendation:</strong>
                      <p>{rec.Recommendation}</p>
                    </div>
                    
                    <div className="evidence-item">
                      <strong>📊 Impact:</strong>
                      <p>{rec.Impact}</p>
                    </div>
                    
                    <div className="evidence-item">
                      <strong>⏱️ Timeline:</strong>
                      <p>{rec.Timeline}</p>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}

        {lowPriority.length > 0 && (
          <div className="evidence-section">
            <h3>🟢 Low Priority ({lowPriority.length})</h3>
            <div className="evidence-grid">
              {lowPriority.map((rec, index) => (
                <div key={index} className="evidence-card">
                  <div className="evidence-header">
                    <h4>{rec.Platform} - {rec.Category}</h4>
                    <div className="badge badge--priority-low">Low Priority</div>
                  </div>
                  
                  <div className="evidence-content">
                    <div className="evidence-item">
                      <strong>📋 Recommendation:</strong>
                      <p>{rec.Recommendation}</p>
                    </div>
                    
                    <div className="evidence-item">
                      <strong>📊 Impact:</strong>
                      <p>{rec.Impact}</p>
                    </div>
                    
                    <div className="evidence-item">
                      <strong>⏱️ Timeline:</strong>
                      <p>{rec.Timeline}</p>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}
      </div>
    </div>
  )
}
