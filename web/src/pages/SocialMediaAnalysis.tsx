import { useEffect, useState } from 'react'
import { PlotlyChart } from '../components/PlotlyChart'
import { EvidenceDisplay } from '../components/EvidenceDisplay'

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
  evidence?: string
  effective_copy_examples?: string
  ineffective_copy_examples?: string
  trust_credibility_assessment?: string
  business_impact_analysis?: string
}

interface Insight {
  Category: string
  Insight: string
  Type: string
}

interface Recommendation {
  Category: string
  Recommendation: string
  Priority: string
  Impact: string
  Platform?: string
  Timeline?: string
}

function SocialMediaAnalysis() {
  const [data, setData] = useState<SocialMediaData[]>([])
  const [insights, setInsights] = useState<Insight[]>([])
  const [recommendations, setRecommendations] = useState<Recommendation[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  
  // Filters
  const [selectedPlatforms, setSelectedPlatforms] = useState<string[]>([])
  const [selectedPersonas, setSelectedPersonas] = useState<string[]>([])
  const [analysisScope, setAnalysisScope] = useState('All Data')
  const [viewMode, setViewMode] = useState('Overview')
  const [selectedPlatformForDeepDive, setSelectedPlatformForDeepDive] = useState('')

  useEffect(() => {
    fetchSocialMediaData()
  }, [])

  const fetchSocialMediaData = async () => {
    try {
      setLoading(true)
      const response = await fetch('http://localhost:3000/api/social-media')
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`)
      }
      const result = await response.json()
      
      // Use the structured data directly from the new API
      const socialMediaData = result.data || []
      setData(socialMediaData)
      
      // Use insights and recommendations from the API
      setInsights(result.insights || [])
      setRecommendations(result.recommendations || [])
      
      // Initialize filters with available data
      const platforms = result.platforms_analyzed || []
      const personas = result.personas_analyzed || []
      setSelectedPlatforms(platforms)
      setSelectedPersonas(personas)
      setSelectedPlatformForDeepDive(platforms[0] || '')
      
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to load social media data')
    } finally {
      setLoading(false)
    }
  }

  const calculateInsights = (data: any[]) => {
    const avgScore = data.reduce((sum, item) => sum + item.raw_score, 0) / data.length
    const platforms = [...new Set(data.map(d => d.platform_display))]
    const platformScores = platforms.map(platform => {
      const platformData = data.filter(d => d.platform_display === platform)
      return {
        platform,
        score: platformData.reduce((sum, item) => sum + item.raw_score, 0) / platformData.length
      }
    })
    
    const bestPlatform = platformScores.reduce((max, curr) => curr.score > max.score ? curr : max)
    const worstPlatform = platformScores.reduce((min, curr) => curr.score < min.score ? curr : min)
    
    return [
      {
        Category: 'Overall Performance',
        Insight: `Average social media score across all platforms is ${avgScore.toFixed(1)}/10`,
        Type: 'metric'
      },
      {
        Category: 'Top Performer',
        Insight: `${bestPlatform.platform} is the strongest platform with ${bestPlatform.score.toFixed(1)}/10 average score`,
        Type: 'success'
      },
      {
        Category: 'Needs Attention',
        Insight: `${worstPlatform.platform} requires review with ${worstPlatform.score.toFixed(1)}/10 average score`,
        Type: 'warning'
      }
    ]

  }

  const getFilteredData = () => {
    let filteredData = data.filter(item => 
      selectedPlatforms.includes(item.platform_display) &&
      selectedPersonas.includes(item.persona_clean)
    )

    // Apply analysis scope filter
    if (analysisScope === 'High Performers Only') {
      filteredData = filteredData.filter(item => item.raw_score >= 7)
    } else if (analysisScope === 'Problem Areas') {
      filteredData = filteredData.filter(item => item.raw_score < 5)
    } else if (analysisScope === 'Quick Wins') {
      filteredData = filteredData.filter(item => item.quick_win_flag)
    }

    return filteredData
  }

  const calculateOverallHealth = () => {
    const filteredData = getFilteredData()
    if (filteredData.length === 0) return { avgScore: 0, status: 'No Data', color: '#6B7280' }
    
    const avgScore = filteredData.reduce((sum, item) => sum + item.raw_score, 0) / filteredData.length
    
    if (avgScore >= 7) return { avgScore, status: '🟢 Healthy', color: '#10B981' }
    if (avgScore >= 5) return { avgScore, status: '🟡 Moderate', color: '#F59E0B' }
    if (avgScore >= 3) return { avgScore, status: '🟠 At Risk', color: '#F97316' }
    return { avgScore, status: '🔴 Critical', color: '#EF4444' }
  }

  const getExecutiveSummaryMetrics = () => {
    const filteredData = getFilteredData()
    const health = calculateOverallHealth()
    
    const totalPlatforms = selectedPlatforms.length
    const criticalIssues = filteredData.filter(item => item.critical_issue_flag).length
    const successCases = filteredData.filter(item => item.success_flag).length
    const quickWins = filteredData.filter(item => item.quick_win_flag).length
    
    // Find top and weakest platforms
    const platformScores = selectedPlatforms.map(platform => {
      const platformData = filteredData.filter(item => item.platform_display === platform)
      const avgScore = platformData.length > 0 
        ? platformData.reduce((sum, item) => sum + item.raw_score, 0) / platformData.length 
        : 0
      return { platform, avgScore }
    })
    
    const topPlatform = platformScores.reduce((max, curr) => curr.avgScore > max.avgScore ? curr : max, platformScores[0] || { platform: 'N/A', avgScore: 0 })
    const weakestPlatform = platformScores.reduce((min, curr) => curr.avgScore < min.avgScore ? curr : min, platformScores[0] || { platform: 'N/A', avgScore: 0 })
    
    return {
      health,
      totalPlatforms,
      criticalIssues,
      successCases,
      quickWins,
      topPlatform,
      weakestPlatform
    }
  }

  const getPlatformHealthCards = () => {
    const filteredData = getFilteredData()
    
    return selectedPlatforms.map(platform => {
      const platformData = filteredData.filter(item => item.platform_display === platform)
      const avgScore = platformData.length > 0 
        ? platformData.reduce((sum, item) => sum + item.raw_score, 0) / platformData.length 
        : 0
      
      const highPerformers = platformData.filter(item => item.raw_score >= 7).length
      const quickWins = platformData.filter(item => item.quick_win_flag).length
      
      let status, statusColor, bgColor
      if (avgScore >= 7) {
        status = '✅ Healthy'
        statusColor = '#10B981'
        bgColor = '#ECFDF5'
      } else if (avgScore >= 5) {
        status = '⚠️ Moderate'
        statusColor = '#F59E0B'
        bgColor = '#FFFBEB'
      } else if (avgScore >= 3) {
        status = '🔶 At Risk'
        statusColor = '#F97316'
        bgColor = '#FFF7ED'
      } else {
        status = '🚨 Critical'
        statusColor = '#EF4444'
        bgColor = '#FEF2F2'
      }
      
      const platformIcons: { [key: string]: string } = {
        'LinkedIn': '💼',
        'Instagram': '📸',
        'Facebook': '👥',
        'Twitter/X': '🐦'
      }
      const icon = platformIcons[platform] || '📱'
      
      return {
        platform,
        avgScore,
        status,
        statusColor,
        bgColor,
        icon,
        totalEntries: platformData.length,
        highPerformers,
        quickWins
      }
    })
  }

  const getPerformanceDistribution = () => {
    const filteredData = getFilteredData()
    
    const excellent = filteredData.filter(item => item.raw_score >= 8).length
    const good = filteredData.filter(item => item.raw_score >= 6 && item.raw_score < 8).length
    const fair = filteredData.filter(item => item.raw_score >= 4 && item.raw_score < 6).length
    const poor = filteredData.filter(item => item.raw_score < 4).length
    
    return { excellent, good, fair, poor }
  }

  const getPlatformComparisonChart = () => {
    const filteredData = getFilteredData()
    
    const platformData = selectedPlatforms.map(platform => {
      const platformItems = filteredData.filter(item => item.platform_display === platform)
      const avgScore = platformItems.length > 0 
        ? platformItems.reduce((sum, item) => sum + item.raw_score, 0) / platformItems.length 
        : 0
      
      return {
        platform,
        avgScore: Number(avgScore.toFixed(1)),
        entries: platformItems.length
      }
    })
    
    return platformData
  }

  const getPersonaPerformanceChart = () => {
    const filteredData = getFilteredData()
    
    const personaData = selectedPersonas.map(persona => {
      const personaItems = filteredData.filter(item => item.persona_clean === persona)
      const avgScore = personaItems.length > 0 
        ? personaItems.reduce((sum, item) => sum + item.raw_score, 0) / personaItems.length 
        : 0
      
      return {
        persona: persona.replace('P1 - ', '').replace('P2 - ', '').replace('P3 - ', '').replace('P4 - ', '').replace('P5 - ', ''),
        avgScore: Number(avgScore.toFixed(1)),
        entries: personaItems.length
      }
    })
    
    return personaData
  }

  const getPersonaPlatformHeatmapData = () => {
    const filteredData = getFilteredData()
    
    // Create matrix data for heatmap
    const platforms = [...new Set(filteredData.map(item => item.platform_display))]
    const personas = [...new Set(filteredData.map(item => item.persona_clean))]
    
    const matrix = personas.map(persona => {
      return platforms.map(platform => {
        const entries = filteredData.filter(item => 
          item.persona_clean === persona && item.platform_display === platform
        )
        return entries.length > 0 
          ? entries.reduce((sum, item) => sum + item.raw_score, 0) / entries.length 
          : 0
      })
    })
    
    return {
      platforms,
      personas,
      matrix
    }
  }

  const getPriorityMatrixData = () => {
    // Transform recommendations into priority matrix data
    const matrixData = recommendations.map(rec => {
      // Map priority to effort (inverse relationship)
      const effortMap: { [key: string]: number } = { 'High': 1, 'Medium': 2, 'Low': 3 }
      
      // Map expected impact to numeric value
      const impactMap: { [key: string]: number } = { 'High': 3, 'Medium': 2, 'Low': 1 }
      
      // Map timeline to size
      const timelineSize: { [key: string]: number } = {
        '0-30 days': 20,
        '1-3 months': 15,
        '1-2 months': 15,
        '3-6 months': 10
      }
      
      // Map priority to color
      const priorityColor: { [key: string]: number } = { 'High': 0, 'Medium': 0.5, 'Low': 1 }
      
      return {
        effort: effortMap[rec.Priority] || 2,
        impact: impactMap[rec.Impact] || 2,
        size: timelineSize[rec.Timeline || '1-3 months'] || 15,
        color: priorityColor[rec.Priority] || 0.5,
        label: `${rec.Platform || 'Multi-Platform'} - ${rec.Category}`
      }
    })
    
    return {
      effort: matrixData.map(d => d.effort),
      impact: matrixData.map(d => d.impact),
      size: matrixData.map(d => d.size),
      colors: matrixData.map(d => d.color),
      labels: matrixData.map(d => d.label)
    }
  }

  const getQuickWinsRecommendations = () => {
    // Filter recommendations for quick wins (low effort, high impact)
    const matrixData = getPriorityMatrixData()
    const quickWins = recommendations.filter((rec, idx) => {
      const effort = matrixData.effort[idx]
      const impact = matrixData.impact[idx]
      return effort >= 2.5 && impact >= 2.5 // Low effort, high impact
    })
    
    return quickWins.length > 0 ? quickWins : recommendations.slice(0, 3) // Fallback to first 3 recommendations
  }

  const getDetailedPlatformAnalysis = () => {
    const filteredData = getFilteredData()
    const platformData = filteredData.filter(item => item.platform_display === selectedPlatformForDeepDive)
    
    const scoreRanges = {
      'Excellent (8-10)': platformData.filter(item => item.raw_score >= 8).length,
      'Good (6-8)': platformData.filter(item => item.raw_score >= 6 && item.raw_score < 8).length,
      'Fair (4-6)': platformData.filter(item => item.raw_score >= 4 && item.raw_score < 6).length,
      'Poor (&lt;4)': platformData.filter(item => item.raw_score < 4).length
    }
    
    const personaScores = selectedPersonas.map(persona => {
      const personaData = platformData.filter(item => item.persona_clean === persona)
      const avgScore = personaData.length > 0 
        ? personaData.reduce((sum, item) => sum + item.raw_score, 0) / personaData.length 
        : 0
      
      return {
        persona,
        avgScore: Number(avgScore.toFixed(1)),
        entries: personaData.length
      }
    }).filter(item => item.entries > 0)
    
    const avgScore = platformData.length > 0 
      ? platformData.reduce((sum, item) => sum + item.raw_score, 0) / platformData.length 
      : 0
    
    const highScoringPersonas = personaScores.filter(item => item.avgScore >= 7).map(item => item.persona)
    const lowScoringPersonas = personaScores.filter(item => item.avgScore < 5).map(item => item.persona)
    const criticalIssues = platformData.filter(item => item.critical_issue_flag).length
    
    return {
      scoreRanges,
      personaScores,
      avgScore,
      highScoringPersonas,
      lowScoringPersonas,
      criticalIssues
    }
  }

  if (loading) {
    return (
      <div className="page-container">
        <div className="loading-spinner">Loading social media analysis...</div>
      </div>
    )
  }

  if (error) {
    return (
      <div className="page-container">
        <div className="error-message">
          <h2>Error Loading Social Media Data</h2>
          <p>{error}</p>
          <button onClick={fetchSocialMediaData} className="retry-button">
            Retry
          </button>
        </div>
      </div>
    )
  }

  const executiveMetrics = getExecutiveSummaryMetrics()
  const platformHealthCards = getPlatformHealthCards()
  const performanceDistribution = getPerformanceDistribution()
  const platformComparison = getPlatformComparisonChart()
  const personaPerformance = getPersonaPerformanceChart()
  const detailedAnalysis = getDetailedPlatformAnalysis()

  return (
    <div className="page-container">
      {/* Header */}
      <div className="page-header">
        <h1 className="page-title">🔍 Social Media Analysis</h1>
        <p className="page-subtitle">Cross-platform brand presence and engagement insights</p>
        <p className="page-note">📊 <strong>Live Data:</strong> Powered by unified audit data with master scoring</p>
      </div>

      {/* Critical Alert Banner */}
      {executiveMetrics.criticalIssues > 0 && (
        <div className="alert-banner warning">
          <h4>⚠️ Attention Required</h4>
          <p>Social media platforms showing low performance scores - review and optimization recommended</p>
        </div>
      )}

      {/* Executive Summary */}
      <div className="insights-box">
        <h2>📊 Executive Summary</h2>
        
        <div className="metrics-grid-6">
          {/* Overall Health */}
          <div className="metric-card">
            <h4>Overall Health</h4>
            <div className="metric-value" style={{ color: executiveMetrics.health.color }}>
              {executiveMetrics.health.avgScore.toFixed(1)}/10
            </div>
            <div className="progress-bar">
              <div 
                className="progress-fill" 
                style={{ 
                  width: `${executiveMetrics.health.avgScore * 10}%`,
                  backgroundColor: executiveMetrics.health.color
                }}
              />
            </div>
            <div className="metric-label">{executiveMetrics.health.status}</div>
          </div>

          {/* Top Platform */}
          <div className="metric-card">
            <h4>🏆 Top Platform</h4>
            <div className="metric-value">{executiveMetrics.topPlatform.platform}</div>
            <div className="metric-delta positive">{executiveMetrics.topPlatform.avgScore.toFixed(1)}/10</div>
          </div>

          {/* Weakest Platform */}
          <div className="metric-card">
            <h4>⚠️ Weakest Platform</h4>
            <div className="metric-value">{executiveMetrics.weakestPlatform.platform}</div>
            <div className="metric-delta negative">{executiveMetrics.weakestPlatform.avgScore.toFixed(1)}/10</div>
          </div>

          {/* Platform Coverage */}
          <div className="metric-card">
            <h4>📱 Platform Coverage</h4>
            <div className="metric-value">{executiveMetrics.totalPlatforms}/4</div>
            <div className="metric-delta">{Math.round((executiveMetrics.totalPlatforms / 4) * 100)}% Active</div>
          </div>

          {/* Critical Issues */}
          <div className="metric-card">
            <h4>🚨 Critical Issues</h4>
            <div className="metric-value">{executiveMetrics.criticalIssues}</div>
            <div className="metric-label">
              {executiveMetrics.criticalIssues > 0 ? 'Require Immediate Action' : 'None'}
            </div>
          </div>

          {/* Quick Wins */}
          <div className="metric-card">
            <h4>⚡ Quick Wins</h4>
            <div className="metric-value">{executiveMetrics.quickWins}</div>
            <div className="metric-label">Easy Improvements</div>
          </div>
        </div>
      </div>

      {/* Analysis Controls */}
      <div className="insights-box">
        <h2>🎯 Analysis Controls</h2>
        
        <div className="filters-grid">
          <div className="filter-group">
            <label>📱 Select Platforms</label>
            <div className="checkbox-group">
              {['LinkedIn', 'Instagram', 'Facebook', 'Twitter/X'].map(platform => (
                <label key={platform} className="checkbox-label">
                  <input
                    type="checkbox"
                    checked={selectedPlatforms.includes(platform)}
                    onChange={(e) => {
                      if (e.target.checked) {
                        setSelectedPlatforms([...selectedPlatforms, platform])
                      } else {
                        setSelectedPlatforms(selectedPlatforms.filter(p => p !== platform))
                      }
                    }}
                  />
                  {platform}
                </label>
              ))}
            </div>
          </div>

          <div className="filter-group">
            <label>👥 Select Personas</label>
            <div className="checkbox-group">
              {['P1 - C-Suite', 'P2 - Tech Leaders', 'P3 - Programme', 'P4 - Cybersecurity', 'P5 - Tech Influencers'].map(persona => (
                <label key={persona} className="checkbox-label">
                  <input
                    type="checkbox"
                    checked={selectedPersonas.includes(persona)}
                    onChange={(e) => {
                      if (e.target.checked) {
                        setSelectedPersonas([...selectedPersonas, persona])
                      } else {
                        setSelectedPersonas(selectedPersonas.filter(p => p !== persona))
                      }
                    }}
                  />
                  {persona}
                </label>
              ))}
            </div>
          </div>

          <div className="filter-group">
            <label>🌍 Analysis Scope</label>
            <select 
              value={analysisScope} 
              onChange={(e) => setAnalysisScope(e.target.value)}
              className="filter-select"
            >
              <option value="All Data">All Data</option>
              <option value="High Performers Only">High Performers Only</option>
              <option value="Problem Areas">Problem Areas</option>
              <option value="Quick Wins">Quick Wins</option>
            </select>
          </div>

          <div className="filter-group">
            <label>📊 View Mode</label>
            <div className="radio-group">
              {['Overview', 'Detailed Analysis', 'Evidence Analysis', 'Recommendations'].map(mode => (
                <label key={mode} className="radio-label">
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
      </div>

      {/* Platform Health Overview */}
      <div className="insights-box">
        <h2>📱 Platform Health Overview</h2>
        
        <div className="platform-health-grid">
          {platformHealthCards.map(card => {
            const platformData = getFilteredData().filter(item => item.platform_display === card.platform)
            const evidenceItems = platformData.slice(0, 3).map(item => ({
              type: 'evidence' as const,
              content: item.evidence || `Platform analysis for ${card.platform}: Average score ${card.avgScore.toFixed(1)}/10 with ${card.totalEntries} entries analyzed.`,
              title: 'Platform Analysis'
            }))
            
            return (
              <div 
                key={card.platform}
                className="platform-health-card"
                style={{ 
                  borderColor: card.statusColor,
                  backgroundColor: card.bgColor 
                }}
              >
                <div className="platform-icon">{card.icon}</div>
                <h4>{card.platform}</h4>
                <div className="platform-score">
                  <div className="score-value" style={{ color: card.statusColor }}>
                    {card.avgScore.toFixed(1)}/10
                  </div>
                  <div className="score-status">{card.status}</div>
                </div>
                <div className="platform-stats">
                  📊 {card.totalEntries} entries<br/>
                  🎯 {card.highPerformers} high performers<br/>
                  ⚡ {card.quickWins} quick wins
                </div>
                
                {evidenceItems.length > 0 && (
                  <div className="platform-evidence">
                    <EvidenceDisplay
                      evidence={evidenceItems}
                      title="Platform Evidence"
                      collapsible={true}
                      defaultExpanded={false}
                      maxHeight="200px"
                    />
                  </div>
                )}
              </div>
            )
          })}
        </div>
      </div>

      {/* View Mode Content */}
      {viewMode === 'Overview' && (
        <>
          {/* Platform Performance Analysis */}
          <div className="insights-box">
            <h2>📊 Platform Performance Analysis</h2>
            
            <div className="chart-grid">
              <div className="chart-container">
                <h3>Platform Comparison</h3>
                <PlotlyChart
                  data={[{
                    type: 'bar',
                    x: platformComparison.map(p => p.platform),
                    y: platformComparison.map(p => p.avgScore),
                    marker: { 
                      color: platformComparison.map(p => p.avgScore),
                      colorscale: 'RdYlGn',
                      cmin: 0,
                      cmax: 10
                    },
                    text: platformComparison.map(p => `${p.avgScore}/10`),
                    textposition: 'outside'
                  }]}
                  layout={{
                    title: 'Average Score by Platform',
                    xaxis: { title: 'Platform' },
                    yaxis: { title: 'Average Score', range: [0, 10] },
                    height: 400
                  }}
                />
              </div>

              <div className="chart-container">
                <h3>Performance Distribution</h3>
                <PlotlyChart
                  data={[{
                    type: 'pie',
                    values: [performanceDistribution.excellent, performanceDistribution.good, performanceDistribution.fair, performanceDistribution.poor],
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
            </div>
          </div>

          {/* Persona Analysis */}
          <div className="insights-box">
            <h2>👥 Persona Analysis</h2>
            
            <div className="chart-grid">
              <div className="chart-container">
                <h3>Persona-Platform Performance Heatmap</h3>
                <PlotlyChart
                  data={[{
                    type: 'heatmap',
                    x: getPersonaPlatformHeatmapData().platforms,
                    y: getPersonaPlatformHeatmapData().personas,
                    z: getPersonaPlatformHeatmapData().matrix,
                    colorscale: 'RdYlGn',
                    zmin: 0,
                    zmax: 10,
                    hoverongaps: false,
                    showscale: true,
                    colorbar: {
                      title: 'Score',
                      titleside: 'right'
                    }
                  }]}
                  layout={{
                    title: 'Persona-Platform Performance Matrix',
                    xaxis: { title: 'Platform' },
                    yaxis: { title: 'Persona' },
                    height: 400
                  }}
                />
              </div>
              
              <div className="chart-container">
                <h3>Persona Performance Summary</h3>
                <PlotlyChart
                  data={[{
                    type: 'bar',
                    x: personaPerformance.map(p => p.persona),
                    y: personaPerformance.map(p => p.avgScore),
                    marker: { 
                      color: personaPerformance.map(p => p.avgScore),
                      colorscale: 'RdYlGn',
                      cmin: 0,
                      cmax: 10
                    },
                    text: personaPerformance.map(p => `${p.avgScore}/10`),
                    textposition: 'outside'
                  }]}
                  layout={{
                    title: 'Average Score by Persona',
                    xaxis: { title: 'Persona' },
                    yaxis: { title: 'Average Score', range: [0, 10] },
                    height: 400
                  }}
                />
              </div>
            </div>
          </div>

          {/* Insights and Recommendations */}
          <div className="insights-box">
            <h2>💡 Key Insights & Recommendations</h2>
            
            <div className="insights-grid">
              <div className="insights-column">
                <h3>🔍 Key Insights</h3>
                {insights.slice(0, 5).map((insight, idx) => (
                  <div key={idx} className={`insight-item ${insight.Type}`}>
                    <strong>{insight.Category}:</strong> {insight.Insight}
                  </div>
                ))}
              </div>

              <div className="insights-column">
                <h3>🎯 Recommendations</h3>
                {recommendations.slice(0, 5).map((rec, idx) => (
                  <div key={idx} className={`recommendation-item ${rec.Priority?.toLowerCase()}`}>
                    <strong>{rec.Category}:</strong> {rec.Recommendation}
                    <div className="recommendation-meta">
                      Priority: {rec.Priority} | Impact: {rec.Impact}
                    </div>
                  </div>
                ))}
              </div>
            </div>
          </div>
        </>
      )}

      {viewMode === 'Detailed Analysis' && (
        <div className="insights-box">
          <h2>🔬 Detailed Analysis</h2>
          
          <div className="tabs">
            <div className="tab-buttons">
              <button className="tab-button active">📊 Platform Deep Dive</button>
              <button className="tab-button">📝 Content Strategy</button>
              <button className="tab-button">🎯 Performance Analytics</button>
              <button className="tab-button">⚡ Quick Wins & Actions</button>
            </div>
            
            <div className="tab-content">
              <h3>🔍 Platform-Specific Analysis</h3>
              
              <div className="filter-group">
                <label>Choose platform for deep dive:</label>
                <select 
                  value={selectedPlatformForDeepDive} 
                  onChange={(e) => setSelectedPlatformForDeepDive(e.target.value)}
                  className="filter-select"
                >
                  {selectedPlatforms.map(platform => (
                    <option key={platform} value={platform}>{platform}</option>
                  ))}
                </select>
              </div>

              <div className="analysis-grid">
                <div className="analysis-column">
                  <h4>📈 Performance Breakdown</h4>
                  <div className="score-ranges">
                    {Object.entries(detailedAnalysis.scoreRanges).map(([range, count]) => (
                      count > 0 && (
                        <div key={range} className="score-range-item">
                          <span className="range-label">{range}:</span>
                          <span className="range-count">{count}</span>
                        </div>
                      )
                    ))}
                  </div>
                </div>

                <div className="analysis-column">
                  <h4>👥 Persona Performance</h4>
                  <div className="persona-scores">
                    {detailedAnalysis.personaScores.map(persona => (
                      <div key={persona.persona} className="persona-score-item">
                        <span className="persona-name">{persona.persona}</span>
                        <span className="persona-score">{persona.avgScore}/10</span>
                        <span className="persona-entries">({persona.entries} entries)</span>
                      </div>
                    ))}
                  </div>
                </div>
              </div>

              <div className="strengths-weaknesses">
                <h4>💪 Strengths & Weaknesses</h4>
                <div className="analysis-grid">
                  <div className="analysis-column">
                    <h5>🟢 Strengths:</h5>
                    {detailedAnalysis.highScoringPersonas.length > 0 ? (
                      detailedAnalysis.highScoringPersonas.map(persona => (
                        <div key={persona}>• Strong performance with {persona}</div>
                      ))
                    ) : (
                      <div>• Identify and build on best-performing content</div>
                    )}
                    {detailedAnalysis.avgScore >= 6 && (
                      <div>• Above-average overall performance ({detailedAnalysis.avgScore.toFixed(1)}/10)</div>
                    )}
                  </div>

                  <div className="analysis-column">
                    <h5>🔴 Areas for Improvement:</h5>
                    {detailedAnalysis.lowScoringPersonas.length > 0 ? (
                      detailedAnalysis.lowScoringPersonas.map(persona => (
                        <div key={persona}>• Needs improvement with {persona}</div>
                      ))
                    ) : (
                      <div>• Continue current successful strategies</div>
                    )}
                    {detailedAnalysis.avgScore < 5 && (
                      <div>• Below-average overall performance ({detailedAnalysis.avgScore.toFixed(1)}/10)</div>
                    )}
                    {detailedAnalysis.criticalIssues > 0 && (
                      <div>• {detailedAnalysis.criticalIssues} critical issues require attention</div>
                    )}
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      )}

      {viewMode === 'Evidence Analysis' && (
        <div className="insights-box">
          <h2>🔍 Evidence Analysis & Insights</h2>
          
          <div className="evidence-sections">
            <div className="evidence-section">
              <h3>📊 Sentiment & Engagement Evidence</h3>
              <div className="evidence-grid">
                {getFilteredData().slice(0, 6).map((item, index) => (
                  <div key={index} className="evidence-card">
                    <div className="evidence-header">
                      <h4>{item.platform_display}</h4>
                      <div className="evidence-metrics">
                        <div className="metric">
                          <span className="metric-label">Sentiment:</span>
                          <span className={`metric-value ${item.sentiment_numeric >= 6 ? 'positive' : item.sentiment_numeric >= 4 ? 'neutral' : 'negative'}`}>
                            {item.sentiment_numeric}/10
                          </span>
                        </div>
                        <div className="metric">
                          <span className="metric-label">Engagement:</span>
                          <span className={`metric-value ${item.engagement_numeric >= 6 ? 'high' : item.engagement_numeric >= 4 ? 'medium' : 'low'}`}>
                            {item.engagement_numeric}/10
                          </span>
                        </div>
                      </div>
                    </div>
                    
                    <div className="evidence-content">
                      <div className="evidence-item">
                        <strong>🎯 Audience:</strong>
                        <p>{item.persona_clean}</p>
                      </div>
                      
                      <div className="evidence-item">
                        <strong>📈 Performance Evidence:</strong>
                        <p>{item.evidence}</p>
                      </div>
                      
                      <div className="evidence-item">
                        <strong>✅ What's Working:</strong>
                        <p className="effective-copy">{item.effective_copy_examples}</p>
                      </div>
                      
                      <div className="evidence-item">
                        <strong>⚠️ Areas for Improvement:</strong>
                        <p className="ineffective-copy">{item.ineffective_copy_examples}</p>
                      </div>
                      
                      <div className="evidence-item">
                        <strong>🔍 Trust Assessment:</strong>
                        <p>{item.trust_credibility_assessment}</p>
                      </div>
                      
                      <div className="evidence-item">
                        <strong>💼 Business Impact:</strong>
                        <p>{item.business_impact_analysis}</p>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            </div>

            <div className="evidence-section">
              <h3>🚀 Evidence-Based Recommendations</h3>
              <div className="evidence-recommendations">
                <div className="recommendation-category">
                  <h4>📈 High-Performing Content Patterns</h4>
                  <div className="evidence-insights">
                    {getFilteredData()
                      .filter(item => item.raw_score >= 7)
                      .map((item, index) => (
                        <div key={index} className="insight-item success">
                          <strong>{item.platform_display}:</strong> {item.effective_copy_examples}
                        </div>
                      ))}
                  </div>
                </div>
                
                <div className="recommendation-category">
                  <h4>⚡ Quick Win Opportunities</h4>
                  <div className="evidence-insights">
                    {getFilteredData()
                      .filter(item => item.quick_win_flag)
                      .map((item, index) => (
                        <div key={index} className="insight-item warning">
                          <strong>{item.platform_display}:</strong> {item.ineffective_copy_examples}
                        </div>
                      ))}
                  </div>
                </div>
                
                <div className="recommendation-category">
                  <h4>🔍 Trust & Credibility Enhancements</h4>
                  <div className="evidence-insights">
                    {getFilteredData()
                      .slice(0, 4)
                      .map((item, index) => (
                        <div key={index} className="insight-item info">
                          <strong>{item.platform_display}:</strong> {item.trust_credibility_assessment}
                        </div>
                      ))}
                  </div>
                </div>
              </div>
            </div>

            <div className="evidence-section">
              <h3>📊 Platform-Specific Evidence Summary</h3>
              <div className="platform-evidence-summary">
                {selectedPlatforms.map(platform => {
                  const platformData = getFilteredData().filter(item => item.platform_display === platform)
                  if (platformData.length === 0) return null
                  
                  const avgSentiment = platformData.reduce((sum, item) => sum + item.sentiment_numeric, 0) / platformData.length
                  const avgEngagement = platformData.reduce((sum, item) => sum + item.engagement_numeric, 0) / platformData.length
                  const avgScore = platformData.reduce((sum, item) => sum + item.raw_score, 0) / platformData.length
                  
                  return (
                    <div key={platform} className="platform-summary-card">
                      <h4>📱 {platform}</h4>
                      <div className="platform-metrics">
                        <div className="metric-row">
                          <span>📊 Overall Score:</span>
                          <span className={`score ${avgScore >= 7 ? 'high' : avgScore >= 4 ? 'medium' : 'low'}`}>
                            {avgScore.toFixed(1)}/10
                          </span>
                        </div>
                        <div className="metric-row">
                          <span>❤️ Sentiment:</span>
                          <span className={`score ${avgSentiment >= 6 ? 'positive' : avgSentiment >= 4 ? 'neutral' : 'negative'}`}>
                            {avgSentiment.toFixed(1)}/10
                          </span>
                        </div>
                        <div className="metric-row">
                          <span>🔥 Engagement:</span>
                          <span className={`score ${avgEngagement >= 6 ? 'high' : avgEngagement >= 4 ? 'medium' : 'low'}`}>
                            {avgEngagement.toFixed(1)}/10
                          </span>
                        </div>
                        <div className="metric-row">
                          <span>📈 Data Points:</span>
                          <span>{platformData.length} entries</span>
                        </div>
                      </div>
                      
                      <div className="platform-evidence-sample">
                        <h5>Key Evidence:</h5>
                        <p className="evidence-text">{platformData[0]?.evidence}</p>
                      </div>
                    </div>
                  )
                })}
              </div>
            </div>
          </div>
        </div>
      )}

      {viewMode === 'Recommendations' && (
        <>
          <div className="insights-box">
            <h2>🎯 Strategic Recommendations</h2>
            
            <div className="recommendations-grid">
              {recommendations.map((rec, idx) => (
                <div key={idx} className={`recommendation-card ${rec.Priority?.toLowerCase()}`}>
                  <div className="recommendation-header">
                    <h4>{rec.Category}</h4>
                    <div className="recommendation-badges">
                      <span className={`priority-badge ${rec.Priority?.toLowerCase()}`}>
                        {rec.Priority}
                      </span>
                      <span className="impact-badge">
                        {rec.Impact}
                      </span>
                    </div>
                  </div>
                  <p>{rec.Recommendation}</p>
                </div>
              ))}
            </div>
          </div>
          
          {/* Action Priority Matrix */}
          <div className="insights-box">
            <h2>🎯 Action Priority Matrix</h2>
            <p className="matrix-description">
              Impact vs Effort analysis for strategic prioritization
            </p>
            
            <div className="chart-container">
              <PlotlyChart
                data={[{
                  type: 'scatter',
                  x: getPriorityMatrixData().effort,
                  y: getPriorityMatrixData().impact,
                  mode: 'markers',
                  marker: {
                    size: getPriorityMatrixData().size,
                    color: getPriorityMatrixData().colors,
                    colorscale: [
                      [0, '#EF4444'],    // High priority = red
                      [0.5, '#F59E0B'],  // Medium priority = orange
                      [1, '#10B981']     // Low priority = green
                    ],
                    showscale: true,
                    colorbar: {
                      title: 'Priority Level',
                      titleside: 'right'
                    }
                  },
                  text: getPriorityMatrixData().labels,
                  textposition: 'top center',
                  hovertemplate: '<b>%{text}</b><br>' +
                                'Effort: %{x}<br>' +
                                'Impact: %{y}<br>' +
                                '<extra></extra>'
                }]}
                layout={{
                  title: 'Action Priority Matrix: Impact vs Effort',
                  xaxis: { 
                    title: 'Implementation Effort (1=High Effort, 3=Low Effort)',
                    range: [0.5, 3.5],
                    dtick: 1
                  },
                  yaxis: { 
                    title: 'Expected Impact (1=Low, 3=High)',
                    range: [0.5, 3.5],
                    dtick: 1
                  },
                  height: 500,
                  annotations: [
                    {
                      x: 3,
                      y: 3,
                      text: 'Quick Wins<br>(Low Effort, High Impact)',
                      showarrow: false,
                      font: { size: 10, color: 'green' },
                      bgcolor: 'rgba(16, 185, 129, 0.1)',
                      bordercolor: 'green'
                    },
                    {
                      x: 1,
                      y: 3,
                      text: 'Strategic Projects<br>(High Effort, High Impact)',
                      showarrow: false,
                      font: { size: 10, color: 'blue' },
                      bgcolor: 'rgba(59, 130, 246, 0.1)',
                      bordercolor: 'blue'
                    },
                    {
                      x: 3,
                      y: 1,
                      text: 'Fill-ins<br>(Low Effort, Low Impact)',
                      showarrow: false,
                      font: { size: 10, color: 'gray' },
                      bgcolor: 'rgba(156, 163, 175, 0.1)',
                      bordercolor: 'gray'
                    },
                    {
                      x: 1,
                      y: 1,
                      text: 'Questionable<br>(High Effort, Low Impact)',
                      showarrow: false,
                      font: { size: 10, color: 'red' },
                      bgcolor: 'rgba(239, 68, 68, 0.1)',
                      bordercolor: 'red'
                    }
                  ]
                }}
              />
            </div>
            
            {/* Quick Wins Section */}
            <div className="quick-wins-section">
              <h3>⚡ Recommended Quick Wins</h3>
              <div className="quick-wins-grid">
                {getQuickWinsRecommendations().map((win, idx) => (
                  <div key={idx} className="quick-win-card">
                    <h4>🎯 {win.Platform || 'Multi-Platform'} - {win.Category}</h4>
                    <p>{win.Recommendation}</p>
                    <div className="quick-win-meta">
                      <strong>Timeline:</strong> {win.Timeline || '1-3 months'} | <strong>Priority:</strong> {win.Priority}
                    </div>
                  </div>
                ))}
              </div>
            </div>
          </div>
        </>
      )}
    </div>
  )
}

export default SocialMediaAnalysis
