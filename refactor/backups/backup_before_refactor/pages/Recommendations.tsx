import React, { useEffect, useState } from 'react'
import { PlotlyChart } from '../components/PlotlyChart'

interface Recommendation {
  id: string
  title: string
  description: string
  category: string
  all_categories?: string[]
  all_evidence?: string[]
  synthesized_findings?: string[]
  impact_score: number
  urgency_score: number
  priority_score: number
  timeline: string
  page_id: string
  persona: string
  url: string
  source: string
  evidence?: string
}

interface ThematicRecommendations {
  [theme: string]: Recommendation[]
}

const THEMES = {
  'Brand & Messaging Strategy': '🏢',
  'Visual Identity & Design': '🎨',
  'User Experience & Trust': '🛡️',
  'Social Media Performance': '👥'
}

const CATEGORIES = [
  '🏢 Brand & Messaging',
  '📝 Content & Copy',
  '🎨 Visual & Design',
  '🧭 Navigation & UX',
  '🛡️ Trust & Credibility',
  '🎯 Conversion Optimization',
  '👥 Social & Engagement'
]

const TIMELINES = ['0-30 days', '30-90 days', '90+ days']

function Recommendations() {
  const [recommendations, setRecommendations] = useState<Recommendation[]>([])
  const [filteredRecommendations, setFilteredRecommendations] = useState<Recommendation[]>([])
  const [thematicRecommendations, setThematicRecommendations] = useState<ThematicRecommendations>({})
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  // Filter states
  const [categoryFilter, setCategoryFilter] = useState('All')
  const [timelineFilter, setTimelineFilter] = useState('All')
  const [impactFilter, setImpactFilter] = useState(0)
  const [urgencyFilter, setUrgencyFilter] = useState(0)

  useEffect(() => {
    fetchRecommendations()
  }, [])

  useEffect(() => {
    applyFilters()
  }, [recommendations, categoryFilter, timelineFilter, impactFilter, urgencyFilter])

  const fetchRecommendations = async () => {
    try {
      setLoading(true)
      const res = await fetch('http://localhost:3000/api/full-recommendations')
      if (!res.ok) throw new Error('Failed to load recommendations')
      const data = await res.json()
      setRecommendations(data.recommendations || [])
      setThematicRecommendations(groupByTheme(data.recommendations || []))
    } catch (err) {
      setError('Failed to load strategic recommendations')
    } finally {
      setLoading(false)
    }
  }


  const groupByTheme = (recs: Recommendation[]): ThematicRecommendations => {
    const thematic: ThematicRecommendations = {
      'Brand & Messaging Strategy': [],
      'Visual Identity & Design': [],
      'User Experience & Trust': [],
      'Social Media Performance': []
    }

    const categoryToThemeMap: Record<string, string> = {
      '🏢 Brand & Messaging': 'Brand & Messaging Strategy',
      '📝 Content & Copy': 'Brand & Messaging Strategy',
      '🎨 Visual & Design': 'Visual Identity & Design',
      '🧭 Navigation & UX': 'User Experience & Trust',
      '🛡️ Trust & Credibility': 'User Experience & Trust',
      '🎯 Conversion Optimization': 'User Experience & Trust',
      '👥 Social & Engagement': 'Social Media Performance'
    }

    recs.forEach(rec => {
      const categories = rec.all_categories || [rec.category]
      let assigned = false

      for (const cat of categories) {
        const theme = categoryToThemeMap[cat]
        if (theme) {
          thematic[theme].push(rec)
          assigned = true
          break
        }
      }

      if (!assigned) {
        // Fallback logic
        const source = rec.source.toLowerCase()
        if (source.includes('social media')) {
          thematic['Social Media Performance'].push(rec)
        } else if (source.includes('visual')) {
          thematic['Visual Identity & Design'].push(rec)
        } else {
          thematic['Brand & Messaging Strategy'].push(rec)
        }
      }
    })

    return thematic
  }

  const applyFilters = () => {
    let filtered = recommendations

    // Category filter
    if (categoryFilter !== 'All') {
      filtered = filtered.filter(rec => {
        const categories = rec.all_categories || [rec.category]
        return categories.includes(categoryFilter)
      })
    }

    // Timeline filter
    if (timelineFilter !== 'All') {
      filtered = filtered.filter(rec => rec.timeline === timelineFilter)
    }

    // Impact score filter
    filtered = filtered.filter(rec => rec.impact_score >= impactFilter)

    // Urgency score filter
    filtered = filtered.filter(rec => rec.urgency_score >= urgencyFilter)

    setFilteredRecommendations(filtered)
  }

  const getPriorityIcon = (score: number) => {
    if (score >= 8) return '🔴'
    if (score >= 6) return '🟡'
    return '🟢'
  }

  const getPriorityColor = (score: number) => {
    if (score >= 8) return 'error'
    if (score >= 6) return 'warning'
    return 'success'
  }

  const getCategoryDistributionData = () => {
    const categoryCounts = filteredRecommendations.reduce((acc, rec) => {
      acc[rec.category] = (acc[rec.category] || 0) + 1
      return acc
    }, {} as Record<string, number>)

    return [{
      type: 'pie' as const,
      labels: Object.keys(categoryCounts),
      values: Object.values(categoryCounts),
      textinfo: 'label+percent',
      textposition: 'auto'
    }]
  }

  const getTimelineDistributionData = () => {
    const timelineOrder = { '0-30 days': 0, '30-90 days': 1, '90+ days': 2 }
    const timelineCounts = filteredRecommendations.reduce((acc, rec) => {
      acc[rec.timeline] = (acc[rec.timeline] || 0) + 1
      return acc
    }, {} as Record<string, number>)

    const sortedTimelines = Object.entries(timelineCounts)
      .sort(([a], [b]) => timelineOrder[a as keyof typeof timelineOrder] - timelineOrder[b as keyof typeof timelineOrder])

    return [{
      type: 'bar' as const,
      x: sortedTimelines.map(([timeline]) => timeline),
      y: sortedTimelines.map(([, count]) => count),
      marker: {
        color: ['#EF4444', '#F59E0B', '#10B981']
      }
    }]
  }

  const getImpactUrgencyScatterData = () => {
    return [{
      type: 'scatter' as const,
      mode: 'markers+text' as const,
      x: filteredRecommendations.map(rec => rec.impact_score),
      y: filteredRecommendations.map(rec => rec.urgency_score),
      text: filteredRecommendations.map(rec => rec.title.length > 20 ? rec.title.substring(0, 20) + '...' : rec.title),
      textposition: 'top center' as const,
      marker: {
        size: filteredRecommendations.map(rec => rec.priority_score * 2),
        color: filteredRecommendations.map(rec => rec.priority_score),
        colorscale: 'RdYlGn',
        showscale: true,
        colorbar: { title: 'Priority Score' }
      },
      hovertemplate: '<b>%{text}</b><br>Impact: %{x}<br>Urgency: %{y}<br>Priority: %{marker.color:.1f}<extra></extra>'
    }]
  }

  const topThemes = Object.entries(thematicRecommendations)
    .filter(([, recs]) => recs.length > 0)
    .sort(([, a], [, b]) => b.length - a.length)
    .slice(0, 3)

  if (loading) {
    return (
      <div className="page-container">
        <div className="main-header">
          <h1>🎯 Strategic Recommendations</h1>
          <p>Strategic recommendations and action plans for brand improvement.</p>
        </div>
        <div className="loading-state">
          <div className="loading-spinner"></div>
          <p>Loading strategic recommendations...</p>
        </div>
      </div>
    )
  }

  if (error) {
    return (
      <div className="page-container">
        <div className="main-header">
          <h1>🎯 Strategic Recommendations</h1>
          <p>Strategic recommendations and action plans for brand improvement.</p>
        </div>
        <div className="error-state">
          <div className="error-message">
            <h2>⚠️ Error Loading Recommendations</h2>
            <p>{error}</p>
            <button onClick={fetchRecommendations} className="retry-button">
              🔄 Retry
            </button>
          </div>
        </div>
      </div>
    )
  }

  return (
    <div className="page-container">
      {/* Header */}
      <div className="main-header">
        <h1>🎯 Strategic Recommendations</h1>
        <p>Strategic recommendations and action plans for brand improvement.</p>
      </div>

      {/* Filters Section */}
      <div className="section">
        <h2>🎛️ Filter Recommendations</h2>
        <div className="filters-grid">
          <div className="filter-group">
            <label>Filter by Category</label>
            <select 
              value={categoryFilter} 
              onChange={(e) => setCategoryFilter(e.target.value)}
              className="filter-select"
            >
              <option value="All">All</option>
              {CATEGORIES.map(category => (
                <option key={category} value={category}>{category}</option>
              ))}
            </select>
          </div>

          <div className="filter-group">
            <label>Filter by Timeline</label>
            <select 
              value={timelineFilter} 
              onChange={(e) => setTimelineFilter(e.target.value)}
              className="filter-select"
            >
              <option value="All">All</option>
              {TIMELINES.map(timeline => (
                <option key={timeline} value={timeline}>{timeline}</option>
              ))}
            </select>
          </div>

          <div className="filter-group">
            <label>Minimum Impact Score: {impactFilter}</label>
            <input
              type="range"
              min="0"
              max="10"
              value={impactFilter}
              onChange={(e) => setImpactFilter(Number(e.target.value))}
              className="filter-slider"
            />
          </div>

          <div className="filter-group">
            <label>Minimum Urgency Score: {urgencyFilter}</label>
            <input
              type="range"
              min="0"
              max="10"
              value={urgencyFilter}
              onChange={(e) => setUrgencyFilter(Number(e.target.value))}
              className="filter-slider"
            />
          </div>
        </div>
      </div>

      {/* Thematic Strategic Insights */}
      {topThemes.length > 0 && (
        <div className="section">
          <h2>🧠 Thematic Strategic Insights</h2>
          <div className="thematic-insights">
            {topThemes.map(([theme, recs]) => (
              <div key={theme} className="theme-card">
                <h3>{THEMES[theme as keyof typeof THEMES]} {theme}</h3>
                <div className="theme-recommendations">
                  {recs.slice(0, 2).map(rec => (
                    <div key={rec.id} className="theme-rec-item">
                      <h4>{rec.title}</h4>
                      <p><strong>Supporting Evidence:</strong></p>
                      <ul>
                        {(rec.all_evidence || []).slice(0, 2).map((evidence, index) => (
                          <li key={index}><em>{evidence}</em></li>
                        ))}
                      </ul>
                    </div>
                  ))}
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Recommendation Cards */}
      <div className="section">
        <h2>📋 Detailed Recommendations</h2>
        <p className="section-subtitle">Showing {filteredRecommendations.length} recommendations</p>
        
        <div className="recommendations-list">
          {filteredRecommendations.map(rec => (
            <div key={rec.id} className="recommendation-card">
              <div className="rec-header">
                <h3>
                  {getPriorityIcon(rec.priority_score)} {rec.title}
                  <span className={`priority-badge ${getPriorityColor(rec.priority_score)}`}>
                    Priority: {rec.priority_score.toFixed(1)}
                  </span>
                </h3>
              </div>

              {rec.url && (
                <div className="rec-url">
                  <strong>🔗 Page URL:</strong> <a href={rec.url} target="_blank" rel="noopener noreferrer">{rec.url}</a>
                </div>
              )}

              <div className="rec-description">
                <strong>📋 Description:</strong>
                <p>{rec.description}</p>
              </div>

              {rec.evidence && (
                <div className="rec-evidence">
                  <strong>🔍 Evidence & Details:</strong>
                  <p>{rec.evidence}</p>
                </div>
              )}

              {rec.all_evidence && rec.all_evidence.length > 0 && (
                <div className="rec-evidence-list">
                  <strong>📊 Supporting Evidence:</strong>
                  <ul>
                    {rec.all_evidence.map((evidence, index) => (
                      <li key={index}>{evidence}</li>
                    ))}
                  </ul>
                </div>
              )}

              <div className="rec-metrics">
                <div className="metric-item">
                  <span className="metric-label">Impact</span>
                  <span className={`metric-value ${rec.impact_score >= 7 ? 'high' : 'medium'}`}>
                    {rec.impact_score}/10
                  </span>
                </div>
                <div className="metric-item">
                  <span className="metric-label">Urgency</span>
                  <span className={`metric-value ${rec.urgency_score >= 7 ? 'high' : 'medium'}`}>
                    {rec.urgency_score}/10
                  </span>
                </div>
                <div className="metric-item">
                  <span className="metric-label">Timeline</span>
                  <span className="metric-value">{rec.timeline}</span>
                </div>
                <div className="metric-item">
                  <span className="metric-label">Category</span>
                  <span className="metric-value">{rec.category}</span>
                </div>
              </div>

              <div className="rec-details">
                <div className="detail-item">
                  <strong>Persona:</strong> {rec.persona}
                </div>
                <div className="detail-item">
                  <strong>Source:</strong> {rec.source}
                </div>
                <div className="detail-item">
                  <strong>Page ID:</strong> <code>{rec.page_id}</code>
                </div>
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Resource & Timeline Planning */}
      <div className="section">
        <h2>📊 Resource & Timeline Planning</h2>
        
        <div className="planning-charts">
          <div className="chart-container">
            <h3>Recommendations by Category</h3>
            <PlotlyChart
              data={getCategoryDistributionData()}
              layout={{
                title: 'Recommendations by Category',
                height: 400,
                showlegend: true
              }}
            />
          </div>

          <div className="chart-container">
            <h3>Recommendations by Timeline</h3>
            <PlotlyChart
              data={getTimelineDistributionData()}
              layout={{
                title: 'Recommendations by Timeline',
                xaxis: { title: 'Timeline' },
                yaxis: { title: 'Count' },
                height: 400
              }}
            />
          </div>
        </div>

        <div className="chart-container full-width">
          <h3>Impact vs Urgency Analysis</h3>
          <PlotlyChart
            data={getImpactUrgencyScatterData()}
            layout={{
              title: 'Impact vs Urgency Analysis',
              xaxis: { 
                title: 'Impact Score',
                range: [0, 10]
              },
              yaxis: { 
                title: 'Urgency Score',
                range: [0, 10]
              },
              height: 500
            }}
          />
        </div>

        <div className="planning-table">
          <h3>Planning Overview</h3>
          <table>
            <thead>
              <tr>
                <th>Title</th>
                <th>Category</th>
                <th>Impact</th>
                <th>Urgency</th>
                <th>Priority</th>
                <th>Timeline</th>
              </tr>
            </thead>
            <tbody>
              {filteredRecommendations
                .sort((a, b) => b.priority_score - a.priority_score)
                .map(rec => (
                  <tr key={rec.id}>
                    <td>{rec.title}</td>
                    <td>{rec.category}</td>
                    <td>{rec.impact_score}/10</td>
                    <td>{rec.urgency_score}/10</td>
                    <td className={getPriorityColor(rec.priority_score)}>
                      {rec.priority_score.toFixed(1)}
                    </td>
                    <td>{rec.timeline}</td>
                  </tr>
                ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  )
}

export default Recommendations
