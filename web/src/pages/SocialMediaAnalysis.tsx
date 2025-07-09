import React, { useState, useEffect } from 'react'

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
      <div className="social-media-analysis">
        <div className="loading">
          <div className="spinner"></div>
          <p>Loading social media analysis...</p>
        </div>
      </div>
    )
  }

  if (error) {
    return (
      <div className="social-media-analysis">
        <div className="error">
          <h2>❌ Error Loading Data</h2>
          <p>{error}</p>
          <button onClick={loadSocialMediaData} className="retry-button">
            🔄 Retry
          </button>
        </div>
      </div>
    )
  }

  if (!data || data.error) {
    return (
      <div className="social-media-analysis">
        <div className="no-data">
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
    <div className="social-media-analysis">
      {/* Header Section */}
      <div className="header-card">
        <h1 style={{ color: '#2C3E50', fontFamily: 'Crimson Text, serif', margin: 0 }}>
          🔍 Social Media Analysis
        </h1>
        <p style={{ color: '#6B7280', margin: '0.5rem 0 0 0' }}>
          Cross-platform brand presence and engagement insights
        </p>
        <p style={{ color: '#E85A4F', margin: '0.25rem 0 0 0', fontSize: '0.9rem' }}>
          📊 <strong>Live Data:</strong> Powered by unified audit data with master scoring
        </p>
      </div>

      {/* Executive Summary */}
      <div className="executive-summary">
        <h2>📊 Executive Summary</h2>
        
        {/* Critical Alert Banner */}
        {twitterCritical && (
          <div style={{
            border: '1px solid #F59E0B',
            borderRadius: '8px',
            padding: '1rem',
            marginBottom: '1rem',
            background: '#FFFBEB',
            borderLeft: '4px solid #F59E0B'
          }}>
            <h4 style={{ margin: 0, color: '#92400E' }}>⚠️ Attention Required</h4>
            <p style={{ margin: '0.5rem 0 0 0', color: '#78350F' }}>
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
      <div className="analysis-controls">
        <h2>🎯 Analysis Controls</h2>
        <div className="controls-grid">
          <div className="control-group">
            <label>📱 Select Platforms</label>
            <select 
              multiple 
              value={selectedPlatforms}
              onChange={(e) => setSelectedPlatforms(Array.from(e.target.selectedOptions, option => option.value))}
            >
              {(data.platforms_analyzed || []).map(platform => (
                <option key={platform} value={platform}>{platform}</option>
              ))}
            </select>
          </div>
          
          <div className="control-group">
            <label>👥 Select Personas</label>
            <select 
              multiple 
              value={selectedPersonas}
              onChange={(e) => setSelectedPersonas(Array.from(e.target.selectedOptions, option => option.value))}
            >
              {(data.personas_analyzed || []).map(persona => (
                <option key={persona} value={persona}>{persona}</option>
              ))}
            </select>
          </div>
          
          <div className="control-group">
            <label>🌍 Analysis Scope</label>
            <select value={analysisScope} onChange={(e) => setAnalysisScope(e.target.value)}>
              <option>All Data</option>
              <option>High Performers Only</option>
              <option>Problem Areas</option>
              <option>Quick Wins</option>
            </select>
          </div>
          
          <div className="control-group">
            <label>📊 View Mode</label>
            <div className="radio-group">
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
        
        <button 
          onClick={handleFilterChange}
          className="apply-filters-btn"
          style={{
            background: '#3B82F6',
            color: 'white',
            border: 'none',
            padding: '0.5rem 1rem',
            borderRadius: '4px',
            marginTop: '1rem'
          }}
        >
          🔄 Apply Filters
        </button>
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
    <div className="metric-card" style={{ textAlign: 'center', padding: '1rem', border: '1px solid #E5E7EB', borderRadius: '8px', background: 'white' }}>
      <h4 style={{ margin: 0, color: '#374151' }}>Overall Health</h4>
      <div style={{ fontSize: '2rem', fontWeight: 'bold', color: healthInfo.color, margin: '0.5rem 0' }}>
        {score.toFixed(1)}/10
      </div>
      <div style={{ background: '#F3F4F6', borderRadius: '10px', height: '10px', margin: '0.5rem 0' }}>
        <div 
          style={{ 
            background: healthInfo.color, 
            width: `${score * 10}%`, 
            height: '100%', 
            borderRadius: '10px' 
          }}
        />
      </div>
      <div style={{ fontSize: '0.8rem', color: '#6B7280' }}>{healthInfo.status}</div>
    </div>
  )
}

function TopPlatformCard({ platformMetrics }: { platformMetrics: PlatformMetrics[] }) {
  const topPlatform = platformMetrics.reduce((prev, current) => 
    prev.Average_Score > current.Average_Score ? prev : current
  )
  
  return (
    <div className="metric-card">
      <h4>🏆 Top Platform</h4>
      <div className="metric-value">{topPlatform.Platform}</div>
      <div className="metric-delta positive">{topPlatform.Average_Score.toFixed(1)}/10</div>
    </div>
  )
}

function WeakestPlatformCard({ platformMetrics }: { platformMetrics: PlatformMetrics[] }) {
  const weakestPlatform = platformMetrics.reduce((prev, current) => 
    prev.Average_Score < current.Average_Score ? prev : current
  )
  
  return (
    <div className="metric-card">
      <h4>⚠️ Weakest Platform</h4>
      <div className="metric-value">{weakestPlatform.Platform}</div>
      <div className="metric-delta negative">{weakestPlatform.Average_Score.toFixed(1)}/10</div>
    </div>
  )
}

function PlatformCoverageCard({ platformMetrics }: { platformMetrics: PlatformMetrics[] }) {
  const totalExpected = 4 // LinkedIn, Instagram, Facebook, Twitter/X
  const coveragePct = (platformMetrics.length / totalExpected) * 100
  
  return (
    <div className="metric-card">
      <h4>📱 Platform Coverage</h4>
      <div className="metric-value">{platformMetrics.length}/{totalExpected}</div>
      <div className="metric-delta">{coveragePct.toFixed(0)}% Active</div>
    </div>
  )
}

function CriticalIssuesCard({ data }: { data: SocialMediaData[] }) {
  const criticalCount = data.filter(item => item.critical_issue_flag).length
  
  return (
    <div className="metric-card">
      <h4>🚨 Critical Issues</h4>
      <div className="metric-value">{criticalCount}</div>
      <div className="metric-delta">
        {criticalCount > 0 ? "Require Immediate Action" : "None"}
      </div>
    </div>
  )
}

function QuickWinsCard({ data }: { data: SocialMediaData[] }) {
  const quickWins = data.filter(item => item.quick_win_flag).length
  
  return (
    <div className="metric-card">
      <h4>⚡ Quick Wins</h4>
      <div className="metric-value">{quickWins}</div>
      <div className="metric-delta">Easy Improvements</div>
    </div>
  )
}

function PlatformHealthOverview({ platformMetrics }: { platformMetrics: PlatformMetrics[] }) {
  return (
    <div className="platform-health-overview">
      <h2>🏥 Platform Health Overview</h2>
      <div className="platform-cards">
        {platformMetrics.map(platform => (
          <div key={platform.Platform} className="platform-card">
            <h3>{platform.Platform}</h3>
            <div className="platform-score">{platform.Average_Score.toFixed(1)}/10</div>
            <div className={`platform-status ${platform.Status_Color}`}>{platform.Status}</div>
            <div className="platform-details">
              <div>Total Entries: {platform.Total_Entries}</div>
              <div>High Performers: {platform.High_Performers}</div>
              <div>Critical Issues: {platform.Critical_Issues}</div>
              <div>Quick Wins: {platform.Quick_Wins}</div>
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
    <div className="platform-performance">
      <h2>📊 Platform Performance Analysis</h2>
      <div className="performance-summary">
        <p>Analyzed {data.length} entries across {platformMetrics.length} platforms</p>
        <div className="performance-breakdown">
          {platformMetrics.map(platform => (
            <div key={platform.Platform} className="platform-summary">
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
    <div className="persona-analysis">
      <h2>👥 Persona Analysis</h2>
      <div className="persona-summary">
        {Object.entries(personaPerformance).map(([persona, stats]) => (
          <div key={persona} className="persona-item">
            <strong>{persona}:</strong> {(stats.total / stats.count).toFixed(1)}/10 
            (based on {stats.count} entries)
          </div>
        ))}
      </div>
      
      {personaPlatformMatrix.length > 0 && (
        <div className="persona-platform-matrix">
          <h3>🎯 Persona-Platform Matrix</h3>
          <div className="matrix-grid">
            {personaPlatformMatrix.map((item, index) => (
              <div key={index} className="matrix-cell">
                <div className="matrix-label">{item.persona} × {item.platform}</div>
                <div className="matrix-score">{item.score.toFixed(1)}/10</div>
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
    <div className="insights-recommendations">
      <h2>💡 Insights & Recommendations</h2>
      
      <div className="insights-section">
        <h3>🔍 Key Insights</h3>
        {insights.map((insight, index) => (
          <div key={index} className={`insight-card ${insight.Type}`}>
            <h4>{insight.Category}</h4>
            <p>{insight.Insight}</p>
          </div>
        ))}
      </div>
      
      <div className="recommendations-section">
        <h3>🎯 Recommendations</h3>
        {recommendations.map((rec, index) => (
          <div key={index} className={`recommendation-card ${rec.Priority.toLowerCase()}`}>
            <h4>{rec.Platform} - {rec.Category}</h4>
            <p>{rec.Recommendation}</p>
            <div className="rec-details">
              <span>Priority: {rec.Priority}</span>
              <span>Impact: {rec.Impact}</span>
              <span>Timeline: {rec.Timeline}</span>
            </div>
          </div>
        ))}
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
    <div className="detailed-analysis">
      <h2>🔬 Detailed Analysis</h2>
      
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
    <div className="platform-deep-dive">
      <h3>🔍 Platform-Specific Analysis</h3>
      {platformMetrics.map(platform => {
        const platformData = data.filter(item => item.platform_display === platform.Platform)
        return (
          <div key={platform.Platform} className="platform-analysis-card">
            <h4>{platform.Platform} Detailed Analysis</h4>
            <div className="platform-stats">
              <div>Average Score: {platform.Average_Score.toFixed(1)}/10</div>
              <div>Total Entries: {platform.Total_Entries}</div>
              <div>Score Range: {platform.Score_Range}</div>
              <div>Status: {platform.Status}</div>
            </div>
            <div className="platform-content">
              <h5>Sample Content:</h5>
              {platformData.slice(0, 3).map((item, index) => (
                <div key={index} className="content-sample">
                  <div><strong>Score:</strong> {item.raw_score.toFixed(1)}/10</div>
                  <div><strong>URL:</strong> {item.url}</div>
                  {item.effective_copy_examples && (
                    <div><strong>Effective Examples:</strong> {item.effective_copy_examples.substring(0, 200)}...</div>
                  )}
                </div>
              ))}
            </div>
          </div>
        )
      })}
    </div>
  )
}

function ContentStrategyAnalysis({ data }: { data: SocialMediaData[] }) {
  return (
    <div className="content-strategy">
      <h3>📝 Content Strategy Analysis</h3>
      <div className="strategy-insights">
        <h4>📈 Content Performance by Platform</h4>
        {Object.entries(data.reduce((acc, item) => {
          if (!acc[item.platform_display]) {
            acc[item.platform_display] = []
          }
          acc[item.platform_display].push(item)
          return acc
        }, {} as Record<string, SocialMediaData[]>)).map(([platform, items]) => (
          <div key={platform} className="platform-content-analysis">
            <h5>{platform}</h5>
            <div>Average Engagement: {(items.reduce((sum, item) => sum + item.engagement_numeric, 0) / items.length).toFixed(2)}</div>
            <div>Average Sentiment: {(items.reduce((sum, item) => sum + item.sentiment_numeric, 0) / items.length).toFixed(2)}</div>
            <div>Content Volume: {items.length} pieces analyzed</div>
          </div>
        ))}
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
    <div className="performance-analytics">
      <h3>🎯 Performance Analytics</h3>
      <div className="analytics-overview">
        <div className="analytics-metrics">
          <div className="metric-card">
            <h5>📊 Total Entries</h5>
            <div className="metric-value">{overallStats.totalEntries}</div>
          </div>
          <div className="metric-card">
            <h5>📈 Average Score</h5>
            <div className="metric-value">{overallStats.avgScore.toFixed(1)}/10</div>
          </div>
          <div className="metric-card">
            <h5>🚨 Critical Issues</h5>
            <div className="metric-value">{overallStats.criticalIssues}</div>
          </div>
          <div className="metric-card">
            <h5>⚡ Quick Wins</h5>
            <div className="metric-value">{overallStats.quickWins}</div>
          </div>
        </div>
        
        <div className="platform-analytics">
          <h4>📊 Platform Performance Breakdown</h4>
          <table className="analytics-table">
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
                  <td>{platform.Platform}</td>
                  <td>{platform.Average_Score.toFixed(1)}</td>
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
    <div className="quick-wins-analysis">
      <h3>⚡ Quick Wins & Immediate Actions</h3>
      
      {quickWins.length > 0 && (
        <div className="quick-wins-section">
          <h4>🎯 Identified Quick Wins ({quickWins.length})</h4>
          <div className="quick-wins-grid">
            {quickWins.slice(0, 5).map((item, index) => (
              <div key={index} className="quick-win-card success">
                <h5>{item.platform_display} → {item.persona_clean}</h5>
                <p>Current Score: {item.raw_score.toFixed(1)}/10</p>
                <div className="win-details">
                  <strong>Opportunity:</strong> Optimization potential identified
                </div>
                {item.effective_copy_examples && (
                  <div className="examples">
                    <strong>Focus Areas:</strong> {item.effective_copy_examples.substring(0, 100)}...
                  </div>
                )}
              </div>
            ))}
          </div>
        </div>
      )}

      {criticalIssues.length > 0 && (
        <div className="critical-actions-section">
          <h4>🚨 Critical Actions Required ({criticalIssues.length})</h4>
          <div className="critical-issues-grid">
            {criticalIssues.slice(0, 3).map((item, index) => (
              <div key={index} className="critical-issue-card error">
                <h5>{item.platform_display} → {item.persona_clean}</h5>
                <p>Current Score: {item.raw_score.toFixed(1)}/10</p>
                <div className="issue-details">
                  <strong>Action Required:</strong> Immediate content review and optimization
                </div>
                {item.ineffective_copy_examples && (
                  <div className="examples">
                    <strong>Issues:</strong> {item.ineffective_copy_examples.substring(0, 100)}...
                  </div>
                )}
              </div>
            ))}
          </div>
        </div>
      )}

      <div className="action-summary">
        <h4>📋 Action Summary</h4>
        <div className="action-stats">
          <div>Quick Wins Available: {quickWins.length}</div>
          <div>Critical Issues: {criticalIssues.length}</div>
          <div>Success Cases to Replicate: {data.filter(item => item.success_flag).length}</div>
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
    <div className="action-priority-matrix">
      <h2>🎯 Action Priority Matrix</h2>
      
      <div className="priority-sections">
        {highPriority.length > 0 && (
          <div className="priority-section high">
            <h3>🔴 High Priority ({highPriority.length})</h3>
            {highPriority.map((rec, index) => (
              <div key={index} className="priority-item">
                <h4>{rec.Platform} - {rec.Category}</h4>
                <p>{rec.Recommendation}</p>
                <div className="priority-meta">
                  Impact: {rec.Impact} | Timeline: {rec.Timeline}
                </div>
              </div>
            ))}
          </div>
        )}

        {mediumPriority.length > 0 && (
          <div className="priority-section medium">
            <h3>🟡 Medium Priority ({mediumPriority.length})</h3>
            {mediumPriority.map((rec, index) => (
              <div key={index} className="priority-item">
                <h4>{rec.Platform} - {rec.Category}</h4>
                <p>{rec.Recommendation}</p>
                <div className="priority-meta">
                  Impact: {rec.Impact} | Timeline: {rec.Timeline}
                </div>
              </div>
            ))}
          </div>
        )}

        {lowPriority.length > 0 && (
          <div className="priority-section low">
            <h3>🟢 Low Priority ({lowPriority.length})</h3>
            {lowPriority.map((rec, index) => (
              <div key={index} className="priority-item">
                <h4>{rec.Platform} - {rec.Category}</h4>
                <p>{rec.Recommendation}</p>
                <div className="priority-meta">
                  Impact: {rec.Impact} | Timeline: {rec.Timeline}
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  )
}
