import { useQuery } from '@tanstack/react-query'

const apiBase = import.meta.env.VITE_API_URL || 'http://localhost:3000'

function ExecutiveDashboard() {
  const { data, isLoading, error } = useQuery({
    queryKey: ['summary'],
    queryFn: async () => {
      const res = await fetch(`${apiBase}/api/summary`)
      if (!res.ok) throw new Error('Failed to load summary')
      return res.json()
    }
  })

  const { data: oppData } = useQuery({
    queryKey: ['opportunities'],
    queryFn: async () => {
      const res = await fetch(`${apiBase}/api/opportunities?limit=5`)
      if (!res.ok) throw new Error('Failed to load opportunities')
      return res.json()
    }
  })

  if (isLoading) return <div className="main-header"><h1>🎯 Executive Dashboard</h1><p>Loading brand health metrics...</p></div>
  if (error) return <div className="main-header"><h1>🎯 Executive Dashboard</h1><p>Error loading dashboard data</p></div>

  const brand = data?.brand_health || {}
  const metrics = data?.key_metrics || {}
  const sentiment = data?.sentiment || {}
  const conversion = data?.conversion || {}
  const recs = Array.isArray(data?.recommendations) ? data.recommendations : []
  const opps = Array.isArray(oppData?.opportunities) ? oppData.opportunities : []

  return (
    <div>
      {/* Executive Header */}
      <div className="main-header">
        <h1>🎯 Brand Health Command Center</h1>
        <p>30-second strategic marketing decision engine for executives</p>
      </div>

      {/* Key Metrics Row */}
      <div className="grid grid--auto-200 mb-4">
        <div className={`metric-card ${brand.raw_score < 4 ? 'critical' : brand.raw_score < 6 ? 'warning' : brand.raw_score < 8 ? 'fair' : ''}`}>
          <div className={`metric-value ${brand.raw_score < 4 ? 'status-critical' : brand.raw_score < 6 ? 'status-fair' : brand.raw_score < 8 ? 'status-good' : 'status-excellent'}`}>
            {brand.raw_score || 0} {brand.emoji || ''}
          </div>
          <div className="metric-label">Brand Health Score</div>
          <div className="so-what">{brand.status || 'Unknown'} - {brand.raw_score >= 7 ? 'Strong brand presence' : brand.raw_score >= 5 ? 'Moderate improvements needed' : 'Critical attention required'}</div>
        </div>

        <div className="metric-card">
          <div className="metric-value status-critical">{metrics.critical_issues || 0}</div>
          <div className="metric-label">Critical Issues</div>
          <div className="so-what">Pages scoring below 4.0 requiring immediate attention</div>
        </div>

        <div className="metric-card">
          <div className="metric-value status-excellent">{metrics.quick_wins || 0}</div>
          <div className="metric-label">Quick Wins</div>
          <div className="so-what">Opportunities for immediate brand impact</div>
        </div>

        <div className="metric-card">
          <div className="metric-value status-good">{metrics.total_pages || 0}</div>
          <div className="metric-label">Total Pages Audited</div>
          <div className="so-what">Comprehensive brand touchpoint analysis</div>
        </div>
      </div>

      {/* Business Impact Summary */}
      <div className="insights-box business-impact-summary">
        <h3>🎯 Executive Summary</h3>
        <p><strong>Brand Performance:</strong> Your brand scores {brand.raw_score}/10 with {metrics.critical_issues} critical issues requiring immediate attention.</p>
        <p><strong>Opportunity Pipeline:</strong> {metrics.quick_wins} quick wins identified for rapid brand improvement.</p>
        <p><strong>Sentiment Analysis:</strong> {sentiment.net_sentiment?.toFixed(1)}% net positive sentiment across digital touchpoints.</p>
        <p><strong>Conversion Readiness:</strong> {conversion.status} level with score of {conversion.raw_score?.toFixed(1)}/10.</p>
      </div>

      {/* Charts Section */}
      <div className="grid grid--auto-400 mb-4">
        <div className="insights-box">
          <h4>📊 Sentiment Breakdown</h4>
          <div className="grid grid--cols-3 text-center">
            <div>
              <div className="metric-value status-excellent text-xl">{sentiment.positive?.toFixed(1)}%</div>
              <div className="metric-label">Positive</div>
            </div>
            <div>
              <div className="metric-value text-xl text-secondary">{sentiment.neutral?.toFixed(1)}%</div>
              <div className="metric-label">Neutral</div>
            </div>
            <div>
              <div className="metric-value status-critical text-xl">{sentiment.negative?.toFixed(1)}%</div>
              <div className="metric-label">Negative</div>
            </div>
          </div>
        </div>

        <div className="insights-box">
          <h4>💡 Top Opportunities</h4>
          <div className="scrollable">
            {opps.slice(0, 5).map((opp: any, idx: number) => (
              <div key={idx} className="list-item">
                <div className="font-semibold text-sm">{opp.page_title || `Opportunity ${idx + 1}`}</div>
                <div className="text-sm text-secondary">
                  Impact: {opp.potential_impact || 'Medium'} | Effort: {opp.effort_level || 'Low'}
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* Strategic Recommendations */}
      <div className="insights-box">
        <h4>🎯 Strategic Recommendations</h4>
        <div className="grid grid--gap-sm">
          {recs.slice(0, 3).map((rec: any, idx: number) => (
            <div key={idx} className="flex flex--center">
              <span className={idx === 0 ? 'critical-badge' : 'quick-win-badge'}>
                {idx === 0 ? 'CRITICAL' : 'QUICK WIN'}
              </span>
              <span>{rec}</span>
            </div>
          ))}
        </div>
      </div>

      {/* Navigation Guidance */}
      <div className="insights-box">
        <h4>🧭 Next Steps</h4>
        <div className="grid grid--auto-200">
          <div>
            <strong>🔍 Detailed Analysis:</strong><br/>
            <small>Visit Persona Insights for audience-specific performance</small>
          </div>
          <div>
            <strong>💡 Action Planning:</strong><br/>
            <small>Check Opportunity Impact for prioritized improvements</small>
          </div>
          <div>
            <strong>🚀 Implementation:</strong><br/>
            <small>Use Run Audit to track progress and updates</small>
          </div>
        </div>
      </div>
    </div>
  )
}

export default ExecutiveDashboard
