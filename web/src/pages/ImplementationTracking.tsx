import React, { useEffect, useState } from 'react'
import { PlotlyChart } from '../components/PlotlyChart'

interface ImplementationItem {
  name: string
  status: 'completed' | 'in_progress' | 'not_started' | 'blocked' | 'on_hold'
  progress: number
  team: string
  priority: 'high' | 'medium' | 'low'
  start_date?: string
  target_date?: string
  completion_date?: string
  description?: string
  milestones?: Milestone[]
  blockers?: string[]
  dependencies?: string[]
}

interface Milestone {
  name: string
  status: 'completed' | 'in_progress' | 'pending'
  target_date: string
  completion_date?: string
}

interface TeamProgress {
  team: string
  total_items: number
  completed: number
  in_progress: number
  avg_progress: number
}

function ImplementationTracking() {
  const [items, setItems] = useState<ImplementationItem[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  
  // Filter states
  const [statusFilter, setStatusFilter] = useState('All')
  const [teamFilter, setTeamFilter] = useState('All')
  const [priorityFilter, setPriorityFilter] = useState('All')
  const [viewMode, setViewMode] = useState('Overview')

  useEffect(() => {
    fetchImplementationData()
  }, [])

  const fetchImplementationData = async () => {
    try {
      setLoading(true)
      // Mock enhanced implementation data - in real app would fetch from API
      const mockData = generateMockImplementationData()
      setItems(mockData)
    } catch (err) {
      setError('Failed to load implementation tracking data')
    } finally {
      setLoading(false)
    }
  }

  const generateMockImplementationData = (): ImplementationItem[] => {
    return [
      {
        name: 'Homepage Brand Messaging Overhaul',
        status: 'completed',
        progress: 100,
        team: 'Marketing',
        priority: 'high',
        start_date: '2024-01-15',
        target_date: '2024-02-15',
        completion_date: '2024-02-10',
        description: 'Complete redesign of homepage messaging to align with brand strategy',
        milestones: [
          { name: 'Messaging Strategy', status: 'completed', target_date: '2024-01-25', completion_date: '2024-01-22' },
          { name: 'Copy Development', status: 'completed', target_date: '2024-02-05', completion_date: '2024-02-03' },
          { name: 'Implementation', status: 'completed', target_date: '2024-02-15', completion_date: '2024-02-10' }
        ]
      },
      {
        name: 'Navigation UX Enhancement',
        status: 'in_progress',
        progress: 65,
        team: 'UX Team',
        priority: 'high',
        start_date: '2024-02-01',
        target_date: '2024-03-15',
        description: 'Improve navigation structure and user experience flows',
        milestones: [
          { name: 'User Research', status: 'completed', target_date: '2024-02-10', completion_date: '2024-02-08' },
          { name: 'Wireframe Design', status: 'completed', target_date: '2024-02-20', completion_date: '2024-02-18' },
          { name: 'Prototype Development', status: 'in_progress', target_date: '2024-03-01' },
          { name: 'User Testing', status: 'pending', target_date: '2024-03-10' },
          { name: 'Implementation', status: 'pending', target_date: '2024-03-15' }
        ]
      },
      {
        name: 'Visual Brand Standards Implementation',
        status: 'in_progress',
        progress: 30,
        team: 'Design',
        priority: 'medium',
        start_date: '2024-02-15',
        target_date: '2024-04-30',
        description: 'Systematic implementation of visual brand standards across all touchpoints',
        milestones: [
          { name: 'Brand Guidelines Audit', status: 'completed', target_date: '2024-02-25', completion_date: '2024-02-23' },
          { name: 'Design System Creation', status: 'in_progress', target_date: '2024-03-15' },
          { name: 'Component Library', status: 'pending', target_date: '2024-04-01' },
          { name: 'Implementation Rollout', status: 'pending', target_date: '2024-04-30' }
        ],
        blockers: ['Waiting for brand guidelines approval', 'Resource allocation pending']
      },
      {
        name: 'Social Media Consistency Initiative',
        status: 'not_started',
        progress: 0,
        team: 'Social',
        priority: 'medium',
        start_date: '2024-03-01',
        target_date: '2024-05-15',
        description: 'Establish consistent brand voice and visual identity across social platforms',
        dependencies: ['Visual Brand Standards Implementation']
      },
      {
        name: 'Page Performance Optimization',
        status: 'completed',
        progress: 100,
        team: 'Tech',
        priority: 'high',
        start_date: '2024-01-01',
        target_date: '2024-01-31',
        completion_date: '2024-01-28',
        description: 'Optimize website performance and loading speeds across all pages',
        milestones: [
          { name: 'Performance Audit', status: 'completed', target_date: '2024-01-10', completion_date: '2024-01-08' },
          { name: 'Optimization Implementation', status: 'completed', target_date: '2024-01-25', completion_date: '2024-01-22' },
          { name: 'Testing & Validation', status: 'completed', target_date: '2024-01-31', completion_date: '2024-01-28' }
        ]
      },
      {
        name: 'Trust Signal Enhancement',
        status: 'blocked',
        progress: 15,
        team: 'Marketing',
        priority: 'medium',
        start_date: '2024-02-20',
        target_date: '2024-04-01',
        description: 'Add trust signals and credibility indicators across key pages',
        blockers: ['Legal review pending', 'Client testimonial collection delayed'],
        milestones: [
          { name: 'Trust Signal Strategy', status: 'completed', target_date: '2024-02-28', completion_date: '2024-02-26' },
          { name: 'Content Collection', status: 'in_progress', target_date: '2024-03-15' },
          { name: 'Implementation', status: 'pending', target_date: '2024-04-01' }
        ]
      }
    ]
  }

  const getFilteredItems = () => {
    return items.filter(item => {
      const statusMatch = statusFilter === 'All' || item.status === statusFilter
      const teamMatch = teamFilter === 'All' || item.team === teamFilter
      const priorityMatch = priorityFilter === 'All' || item.priority === priorityFilter
      return statusMatch && teamMatch && priorityMatch
    })
  }

  const calculateMetrics = () => {
    const filteredItems = getFilteredItems()
    const total = filteredItems.length
    const completed = filteredItems.filter(item => item.status === 'completed').length
    const inProgress = filteredItems.filter(item => item.status === 'in_progress').length
    const blocked = filteredItems.filter(item => item.status === 'blocked').length
    const notStarted = filteredItems.filter(item => item.status === 'not_started').length
    const avgProgress = total > 0 ? filteredItems.reduce((sum, item) => sum + item.progress, 0) / total : 0
    const completionRate = total > 0 ? (completed / total) * 100 : 0

    return { total, completed, inProgress, blocked, notStarted, avgProgress, completionRate }
  }

  const getTeamProgress = (): TeamProgress[] => {
    const teams = [...new Set(items.map(item => item.team))]
    return teams.map(team => {
      const teamItems = items.filter(item => item.team === team)
      const total = teamItems.length
      const completed = teamItems.filter(item => item.status === 'completed').length
      const inProgress = teamItems.filter(item => item.status === 'in_progress').length
      const avgProgress = total > 0 ? teamItems.reduce((sum, item) => sum + item.progress, 0) / total : 0
      
      return { team, total_items: total, completed, in_progress: inProgress, avg_progress: avgProgress }
    })
  }

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'completed': return '✅'
      case 'in_progress': return '🔄'
      case 'blocked': return '🚫'
      case 'on_hold': return '⏸️'
      case 'not_started': return '⏳'
      default: return '❓'
    }
  }

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'completed': return '#10B981'
      case 'in_progress': return '#3B82F6'
      case 'blocked': return '#EF4444'
      case 'on_hold': return '#F59E0B'
      case 'not_started': return '#6B7280'
      default: return '#6B7280'
    }
  }

  const getPriorityColor = (priority: string) => {
    switch (priority) {
      case 'high': return '#EF4444'
      case 'medium': return '#F59E0B'
      case 'low': return '#10B981'
      default: return '#6B7280'
    }
  }

  const getProgressBarData = () => {
    const filteredItems = getFilteredItems()
    return [{
      type: 'bar' as const,
      orientation: 'h' as const,
      x: filteredItems.map(item => item.progress),
      y: filteredItems.map(item => item.name),
      marker: {
        color: filteredItems.map(item => getStatusColor(item.status))
      },
      text: filteredItems.map(item => `${item.progress}%`),
      textposition: 'auto' as const,
      hovertemplate: '<b>%{y}</b><br>Progress: %{x}%<br>Team: %{customdata}<extra></extra>',
      customdata: filteredItems.map(item => item.team)
    }]
  }

  const getStatusDistributionData = () => {
    const filteredItems = getFilteredItems()
    const statusCounts = filteredItems.reduce((acc, item) => {
      acc[item.status] = (acc[item.status] || 0) + 1
      return acc
    }, {} as Record<string, number>)

    return [{
      type: 'pie' as const,
      labels: Object.keys(statusCounts).map(status => status.replace('_', ' ').toUpperCase()),
      values: Object.values(statusCounts),
      marker: {
        colors: Object.keys(statusCounts).map(status => getStatusColor(status))
      },
      textinfo: 'label+percent',
      textposition: 'auto'
    }]
  }

  const getTeamProgressData = () => {
    const teamProgress = getTeamProgress()
    return [{
      type: 'bar' as const,
      x: teamProgress.map(team => team.team),
      y: teamProgress.map(team => team.avg_progress),
      marker: {
        color: '#3B82F6'
      },
      text: teamProgress.map(team => `${team.avg_progress.toFixed(1)}%`),
      textposition: 'auto' as const,
      hovertemplate: '<b>%{x}</b><br>Avg Progress: %{y:.1f}%<br>Total Items: %{customdata.total}<br>Completed: %{customdata.completed}<extra></extra>',
      customdata: teamProgress.map(team => ({ total: team.total_items, completed: team.completed }))
    }]
  }

  const getTimelineData = () => {
    const filteredItems = getFilteredItems().filter(item => item.target_date)
    const timelineData = filteredItems.map(item => ({
      x: [item.start_date || '2024-01-01', item.target_date!],
      y: [item.name, item.name],
      mode: 'lines+markers' as const,
      line: { color: getStatusColor(item.status), width: 8 },
      marker: { size: 10 },
      name: item.name,
      hovertemplate: '<b>%{text}</b><br>Progress: ' + item.progress + '%<br>Team: ' + item.team + '<extra></extra>',
      text: [item.name, item.name]
    }))

    return timelineData
  }

  if (loading) {
    return (
      <div className="page-container">
        <div className="main-header">
          <h1>📈 Implementation Tracking</h1>
          <p>Monitor progress on strategic initiatives and track optimization implementation.</p>
        </div>
        <div className="loading-state">
          <div className="loading-spinner"></div>
          <p>Loading implementation data...</p>
        </div>
      </div>
    )
  }

  if (error) {
    return (
      <div className="page-container">
        <div className="main-header">
          <h1>📈 Implementation Tracking</h1>
          <p>Monitor progress on strategic initiatives and track optimization implementation.</p>
        </div>
        <div className="error-state">
          <div className="error-message">
            <h2>⚠️ Error Loading Implementation Data</h2>
            <p>{error}</p>
            <button onClick={fetchImplementationData} className="retry-button">
              🔄 Retry
            </button>
          </div>
        </div>
      </div>
    )
  }

  const metrics = calculateMetrics()
  const filteredItems = getFilteredItems()

  return (
    <div className="page-container">
      {/* Header */}
      <div className="main-header">
        <h1>📈 Implementation Tracking</h1>
        <p>Monitor progress on strategic initiatives and track optimization implementation.</p>
      </div>

      {/* Filters and View Mode */}
      <div className="section">
        <h2>🎛️ View Controls</h2>
        <div className="filters-grid">
          <div className="filter-group">
            <label>View Mode</label>
            <select 
              value={viewMode} 
              onChange={(e) => setViewMode(e.target.value)}
              className="filter-select"
            >
              <option value="Overview">📊 Overview</option>
              <option value="Timeline">📅 Timeline View</option>
              <option value="Team Progress">👥 Team Progress</option>
              <option value="Detailed">📋 Detailed View</option>
            </select>
          </div>

          <div className="filter-group">
            <label>Filter by Status</label>
            <select 
              value={statusFilter} 
              onChange={(e) => setStatusFilter(e.target.value)}
              className="filter-select"
            >
              <option value="All">All</option>
              <option value="completed">✅ Completed</option>
              <option value="in_progress">🔄 In Progress</option>
              <option value="blocked">🚫 Blocked</option>
              <option value="not_started">⏳ Not Started</option>
            </select>
          </div>

          <div className="filter-group">
            <label>Filter by Team</label>
            <select 
              value={teamFilter} 
              onChange={(e) => setTeamFilter(e.target.value)}
              className="filter-select"
            >
              <option value="All">All</option>
              {[...new Set(items.map(item => item.team))].map(team => (
                <option key={team} value={team}>{team}</option>
              ))}
            </select>
          </div>

          <div className="filter-group">
            <label>Filter by Priority</label>
            <select 
              value={priorityFilter} 
              onChange={(e) => setPriorityFilter(e.target.value)}
              className="filter-select"
            >
              <option value="All">All</option>
              <option value="high">🔴 High</option>
              <option value="medium">🟡 Medium</option>
              <option value="low">🟢 Low</option>
            </select>
          </div>
        </div>
      </div>

      {/* Key Metrics */}
      <div className="section">
        <h2>📊 Implementation Overview</h2>
        <div className="metrics-grid">
          <div className="metric-card">
            <div className="metric-value">{metrics.total}</div>
            <div className="metric-label">📋 Total Initiatives</div>
          </div>
          <div className="metric-card">
            <div className="metric-value" style={{ color: '#10B981' }}>{metrics.completionRate.toFixed(1)}%</div>
            <div className="metric-label">✅ Completion Rate</div>
          </div>
          <div className="metric-card">
            <div className="metric-value" style={{ color: '#3B82F6' }}>{metrics.avgProgress.toFixed(1)}%</div>
            <div className="metric-label">📈 Average Progress</div>
          </div>
          <div className="metric-card">
            <div className="metric-value" style={{ color: '#F59E0B' }}>{metrics.inProgress}</div>
            <div className="metric-label">🔄 In Progress</div>
          </div>
        </div>
      </div>

      {/* Overview Mode */}
      {viewMode === 'Overview' && (
        <>
          <div className="section">
            <h2>📈 Progress Visualization</h2>
            <div className="charts-grid">
              <div className="chart-container">
                <h3>Progress by Initiative</h3>
                <PlotlyChart
                  data={getProgressBarData()}
                  layout={{
                    title: 'Implementation Progress',
                    xaxis: { title: 'Progress (%)', range: [0, 100] },
                    yaxis: { title: 'Initiative' },
                    height: 400,
                    margin: { l: 200, r: 50, t: 50, b: 50 }
                  }}
                />
              </div>

              <div className="chart-container">
                <h3>Status Distribution</h3>
                <PlotlyChart
                  data={getStatusDistributionData()}
                  layout={{
                    title: 'Initiative Status Distribution',
                    height: 400,
                    showlegend: true
                  }}
                />
              </div>
            </div>
          </div>

          <div className="section">
            <h2>👥 Team Performance</h2>
            <div className="chart-container">
              <PlotlyChart
                data={getTeamProgressData()}
                layout={{
                  title: 'Average Progress by Team',
                  xaxis: { title: 'Team' },
                  yaxis: { title: 'Average Progress (%)', range: [0, 100] },
                  height: 400
                }}
              />
            </div>
          </div>
        </>
      )}

      {/* Timeline Mode */}
      {viewMode === 'Timeline' && (
        <div className="section">
          <h2>📅 Timeline View</h2>
          <div className="chart-container">
        <PlotlyChart
              data={getTimelineData()}
              layout={{
                title: 'Implementation Timeline',
                xaxis: { title: 'Date', type: 'date' },
                yaxis: { title: 'Initiative' },
                height: 500,
                margin: { l: 200, r: 50, t: 50, b: 50 },
                showlegend: false
              }}
            />
          </div>
        </div>
      )}

      {/* Detailed View */}
      {(viewMode === 'Detailed' || viewMode === 'Team Progress') && (
        <div className="section">
          <h2>📋 Detailed Implementation Status</h2>
          <p className="section-subtitle">Showing {filteredItems.length} initiatives</p>
          
          <div className="implementation-list">
            {filteredItems.map(item => (
              <div key={item.name} className="implementation-card">
                <div className="impl-header">
                  <h3>
                    {getStatusIcon(item.status)} {item.name}
                    <span className={`priority-badge ${item.priority}`}>
                      {item.priority.toUpperCase()} PRIORITY
                    </span>
                  </h3>
                  <div className="impl-status">
                    <span className={`status-badge ${item.status}`}>
                      {item.status.replace('_', ' ').toUpperCase()}
                    </span>
                  </div>
                </div>

                {item.description && (
                  <div className="impl-description">
                    <strong>📋 Description:</strong>
                    <p>{item.description}</p>
                  </div>
                )}

                <div className="impl-progress">
                  <div className="progress-header">
                    <strong>📈 Progress: {item.progress}%</strong>
                  </div>
                  <div className="progress-bar">
                    <div 
                      className="progress-fill" 
                      style={{ 
                        width: `${item.progress}%`, 
                        backgroundColor: getStatusColor(item.status) 
                      }}
                    ></div>
                  </div>
                </div>

                {item.milestones && item.milestones.length > 0 && (
                  <div className="impl-milestones">
                    <strong>🎯 Milestones:</strong>
                    <div className="milestones-list">
                      {item.milestones.map((milestone, index) => (
                        <div key={index} className={`milestone-item ${milestone.status}`}>
                          <span className="milestone-status">{getStatusIcon(milestone.status)}</span>
                          <span className="milestone-name">{milestone.name}</span>
                          <span className="milestone-date">
                            {milestone.completion_date || milestone.target_date}
                          </span>
                        </div>
                      ))}
                    </div>
                  </div>
                )}

                {item.blockers && item.blockers.length > 0 && (
                  <div className="impl-blockers">
                    <strong>🚫 Blockers:</strong>
                    <ul>
                      {item.blockers.map((blocker, index) => (
                        <li key={index} className="blocker-item">{blocker}</li>
                      ))}
                    </ul>
                  </div>
                )}

                {item.dependencies && item.dependencies.length > 0 && (
                  <div className="impl-dependencies">
                    <strong>🔗 Dependencies:</strong>
                    <ul>
                      {item.dependencies.map((dep, index) => (
                        <li key={index} className="dependency-item">{dep}</li>
                      ))}
                    </ul>
                  </div>
                )}

                <div className="impl-details">
                  <div className="detail-item">
                    <strong>Team:</strong> {item.team}
                  </div>
                  <div className="detail-item">
                    <strong>Priority:</strong> 
                    <span style={{ color: getPriorityColor(item.priority) }}>
                      {item.priority.toUpperCase()}
                    </span>
                  </div>
                  {item.start_date && (
                    <div className="detail-item">
                      <strong>Start Date:</strong> {item.start_date}
                    </div>
                  )}
                  {item.target_date && (
                    <div className="detail-item">
                      <strong>Target Date:</strong> {item.target_date}
                    </div>
                  )}
                  {item.completion_date && (
                    <div className="detail-item">
                      <strong>Completed:</strong> {item.completion_date}
                    </div>
                  )}
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Action Items */}
      <div className="section">
        <h2>🚨 Action Items & Next Steps</h2>
        <div className="action-items">
          {items.filter(item => item.status === 'blocked').length > 0 && (
            <div className="action-group blocked">
              <h3>🚫 Blocked Items Requiring Attention</h3>
              {items.filter(item => item.status === 'blocked').map(item => (
                <div key={item.name} className="action-item">
                  <strong>{item.name}</strong> - {item.team}
                  {item.blockers && (
                    <ul className="blocker-list">
                      {item.blockers.map((blocker, index) => (
                        <li key={index}>{blocker}</li>
                      ))}
                    </ul>
                  )}
                </div>
              ))}
            </div>
          )}

          {items.filter(item => item.status === 'in_progress' && item.progress < 50).length > 0 && (
            <div className="action-group behind-schedule">
              <h3>⚠️ Behind Schedule</h3>
              {items.filter(item => item.status === 'in_progress' && item.progress < 50).map(item => (
                <div key={item.name} className="action-item">
                  <strong>{item.name}</strong> - {item.progress}% complete ({item.team})
                </div>
              ))}
            </div>
          )}

          {items.filter(item => item.status === 'not_started').length > 0 && (
            <div className="action-group upcoming">
              <h3>📅 Starting Soon</h3>
              {items.filter(item => item.status === 'not_started').map(item => (
                <div key={item.name} className="action-item">
                  <strong>{item.name}</strong> - Assigned to {item.team}
                  {item.start_date && <span> (Start: {item.start_date})</span>}
                </div>
              ))}
            </div>
          )}

          {items.filter(item => item.status === 'completed').length > 0 && (
            <div className="action-group completed">
              <h3>🎉 Recently Completed</h3>
              {items.filter(item => item.status === 'completed').slice(0, 3).map(item => (
                <div key={item.name} className="action-item">
                  <strong>{item.name}</strong> - {item.team}
                  {item.completion_date && <span> (Completed: {item.completion_date})</span>}
                </div>
              ))}
            </div>
          )}
        </div>
      </div>
    </div>
  )
}

export default ImplementationTracking
