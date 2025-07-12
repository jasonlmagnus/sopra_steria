import { useQuery } from '@tanstack/react-query'
import { useState } from 'react'
import PagesList from './PagesList'

const apiBase = import.meta.env.VITE_API_URL || 'http://localhost:3000'

function ExecutiveDashboard() {
  const [tierFilter, setTierFilter] = useState('All Tiers')

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
      const res = await fetch(`${apiBase}/api/opportunities?limit=3`)
      if (!res.ok) throw new Error('Failed to load opportunities')
      return res.json()
    }
  })

  const { data: strategicData } = useQuery({
    queryKey: ['strategic-assessment', tierFilter],
    queryFn: async () => {
      const tierParam = tierFilter !== 'All Tiers' ? `?tier=${encodeURIComponent(tierFilter)}` : ''
      const res = await fetch(`${apiBase}/api/strategic-assessment${tierParam}`)
      if (!res.ok) throw new Error('Failed to load strategic assessment')
      return res.json()
    }
  })

  const { data: successData } = useQuery({
    queryKey: ['success-stories'],
    queryFn: async () => {
      const res = await fetch(`${apiBase}/api/success-stories?limit=5&min_score=7.5`)
      if (!res.ok) throw new Error('Failed to load success stories')
      return res.json()
    }
  })

  if (isLoading) return <div className="main-header"><h1>🎯 Brand Health Command Center</h1><p>Loading brand health metrics...</p></div>
  if (error) return <div className="main-header"><h1>🎯 Brand Health Command Center</h1><p>Error loading dashboard data</p></div>

  const brand = data?.brand_health || {}
  const metrics = data?.key_metrics || {}
  const sentiment = data?.sentiment || {}
  const conversion = data?.conversion || {}
  const recs = Array.isArray(data?.recommendations) ? data.recommendations : []
  const opps = Array.isArray(oppData?.opportunities) ? oppData.opportunities : []
  const successStories = Array.isArray(successData?.success_stories) ? successData.success_stories : []

  // Use real strategic assessment data when available
  const getDistinctivenessScore = () => {
    if (strategicData?.distinctiveness?.score !== undefined) {
      return strategicData.distinctiveness.score
    }
    // Fallback calculation if API fails
    const baseScore = (brand.raw_score || 0) * 0.6 + (sentiment.net_sentiment || 0) * 0.4
    return Math.min(Math.max(baseScore, 0), 10)
  }

  const getResonanceScore = () => {
    if (strategicData?.resonance?.net_sentiment !== undefined) {
      return strategicData.resonance.net_sentiment / 10
    }
    // Fallback: use existing sentiment data converted to 0-10 scale
    return Math.max((sentiment.net_sentiment || 0) / 10, 0)
  }

  const getConversionScore = () => {
    if (strategicData?.conversion?.score !== undefined) {
      return strategicData.conversion.score
    }
    // Fallback: use existing conversion data
    return conversion.raw_score || 0
  }

  const getScoreColor = (score: number) => {
    if (score >= 7.0) return "#22C55E" // Green
    if (score >= 4.0) return "#F59E0B" // Amber
    return "#EF4444" // Red
  }

  const getScoreStatus = (score: number) => {
    if (score >= 7.0) return "HIGH"
    if (score >= 4.0) return "MODERATE"
    return "LOW"
  }

  return (
    <div>
      {/* Executive Header */}
      <div className="main-header">
        <h1>🎯 Brand Health Command Center</h1>
        <p>30-second strategic marketing decision engine for executives</p>
      </div>

      {/* Brand Health Overview */}
      <h2>Brand Health Overview</h2>
      <div className="grid grid--auto-200 mb-4">
        <div className={`metric-card ${brand.raw_score < 4 ? 'critical' : brand.raw_score < 6 ? 'warning' : brand.raw_score < 8 ? 'fair' : ''}`}>
          <div className={`metric-value ${brand.raw_score < 4 ? 'status-critical' : brand.raw_score < 6 ? 'status-fair' : brand.raw_score < 8 ? 'status-good' : 'status-excellent'}`}>
            {brand.raw_score || 0}/10
          </div>
          <div className="metric-label">Overall Brand Health - {brand.status || 'Unknown'}</div>
        </div>

        <div className={`metric-card ${metrics.critical_issues > 0 ? 'critical' : ''}`}>
          <div className="metric-value">{metrics.critical_issues || 0}</div>
          <div className="metric-label">Critical Issues</div>
        </div>

        <div className="metric-card">
          <div className="metric-value">{metrics.quick_wins || 0}</div>
          <div className="metric-label">Quick Wins</div>
        </div>

        <div className="metric-card">
          <div className="metric-value">{metrics.success_pages || 0}</div>
          <div className="metric-label">Success Pages</div>
        </div>
      </div>

      {/* Strategic Focus */}
      <h3>🎯 Strategic Focus</h3>
      <div className="grid grid--cols-3 gap-sm mb-4">
        <div>
          <label htmlFor="tier-filter" className="block text-sm font-medium mb-1">Focus on Content Tier:</label>
          <select 
            id="tier-filter"
            value={tierFilter} 
            onChange={(e) => setTierFilter(e.target.value)}
            className="w-full p-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
          >
            <option value="All Tiers">All Tiers</option>
            <option value="Tier 1 (Strategic)">Tier 1 (Strategic)</option>
            <option value="Tier 2 (Tactical)">Tier 2 (Tactical)</option>
            <option value="Tier 3 (Operational)">Tier 3 (Operational)</option>
          </select>
        </div>
        <div className="flex items-end">
          {tierFilter !== "All Tiers" && (
            <div className="text-sm text-blue-600 bg-blue-50 p-2 rounded">
              📊 Filtering analysis by {tierFilter}
            </div>
          )}
        </div>
      </div>

      {/* Strategic Brand Assessment */}
      <h2>Strategic Brand Assessment</h2>
      <div className="grid grid--cols-3 gap-lg mb-4">
        
        {/* Are we distinct? */}
        <div className="executive-question">
          <h4>Are we distinct?</h4>
          {(() => {
            const score = getDistinctivenessScore()
            const color = getScoreColor(score)
            const status = getScoreStatus(score)
            
            return (
              <div style={{ textAlign: 'center', padding: '1rem', background: 'rgba(255,255,255,0.05)', borderRadius: '8px', borderLeft: `4px solid ${color}` }}>
                <div style={{ fontSize: '2rem', fontWeight: 'bold', color }}>{score.toFixed(1)}/10</div>
                <div style={{ color, fontWeight: '600', margin: '0.5rem 0' }}>{status}</div>
                <div style={{ fontSize: '0.85rem', color: '#6B7280', marginTop: '0.5rem' }}>
                  <strong>How we measure:</strong><br/>
                  First impression uniqueness (40%)<br/>
                  Brand visibility (30%)<br/>
                  Distinctive language tone (30%)
                </div>
              </div>
            )
          })()}
        </div>

        {/* Are we resonating? */}
        <div className="executive-question">
          <h4>Are we resonating?</h4>
          {(() => {
            const score = getResonanceScore()
            const color = getScoreColor(score)
            const status = getScoreStatus(score)
            
            return (
              <div style={{ textAlign: 'center', padding: '1rem', background: 'rgba(255,255,255,0.05)', borderRadius: '8px', borderLeft: `4px solid ${color}` }}>
                <div style={{ fontSize: '2rem', fontWeight: 'bold', color }}>{score.toFixed(1)}/10</div>
                <div style={{ color, fontWeight: '600', margin: '0.5rem 0' }}>{status}</div>
                <div style={{ fontSize: '0.85rem', color: '#6B7280', marginTop: '0.5rem' }}>
                  <strong>How we measure:</strong><br/>
                  User sentiment scores (50%)<br/>
                  Content engagement (30%)<br/>
                  Success rate (20%)
                </div>
              </div>
            )
          })()}
        </div>

        {/* Are we converting? */}
        <div className="executive-question">
          <h4>Are we converting?</h4>
          {(() => {
            const score = getConversionScore()
            const color = getScoreColor(score)
            const status = getScoreStatus(score)
            
            return (
              <div style={{ textAlign: 'center', padding: '1rem', background: 'rgba(255,255,255,0.05)', borderRadius: '8px', borderLeft: `4px solid ${color}` }}>
                <div style={{ fontSize: '2rem', fontWeight: 'bold', color }}>{score.toFixed(1)}/10</div>
                <div style={{ color, fontWeight: '600', margin: '0.5rem 0' }}>{status}</div>
                <div style={{ fontSize: '0.85rem', color: '#6B7280', marginTop: '0.5rem' }}>
                  <strong>How we measure:</strong><br/>
                  Conversion likelihood (50%)<br/>
                  Trust & credibility (30%)<br/>
                  Performance metrics (20%)
                </div>
              </div>
            )
          })()}
        </div>
      </div>

      {/* Top 3 Improvement Opportunities */}
      <h2>🎯 Top 3 Improvement Opportunities</h2>
      <p className="text-sm text-secondary mb-3">*For comprehensive analysis, visit the **Opportunity & Impact** tab*</p>
      
      {opps.length > 0 ? (
        <div className="space-y-3 mb-4">
          {opps.map((opp: any, i: number) => (
            <details key={i} className="insights-box">
              <summary className="cursor-pointer font-semibold">
                #{i + 1} - {opp.page_title} (Impact: {opp.potential_impact})
              </summary>
              <div className="mt-3">
                <div className="grid grid--cols-3 gap-md mb-3">
                  <div className="metric-card">
                    <div className="metric-value">{opp.current_score?.toFixed(1) || 'N/A'}</div>
                    <div className="metric-label">Current Score</div>
                  </div>
                  <div className="metric-card">
                    <div className="metric-value">{opp.effort_level}</div>
                    <div className="metric-label">Effort Level</div>
                  </div>
                  <div className="metric-card">
                    <div className="metric-value">{opp.potential_impact}</div>
                    <div className="metric-label">Potential Impact</div>
                  </div>
                </div>
                
                <div className="space-y-2">
                  <div>
                    <strong>💡 Recommendation:</strong>
                    <p className="text-sm italic mt-1">{opp.recommendation}</p>
                  </div>
                  
                  {opp.evidence && opp.evidence !== opp.recommendation && (
                    <div>
                      <strong>📋 Evidence:</strong>
                      <p className="text-sm mt-1">{opp.evidence.substring(0, 200)}...</p>
                    </div>
                  )}
                </div>
                
                <p className="text-sm text-secondary mt-2">
                  *👉 For detailed action plan, visit **Opportunity & Impact** tab*
                </p>
              </div>
            </details>
          ))}
        </div>
      ) : (
        <div className="insights-box">
          <p>📈 No specific opportunities identified. Visit **Content Matrix** for detailed analysis.</p>
        </div>
      )}

      {/* Top 5 Success Stories */}
      <h2>🌟 Top 5 Success Stories</h2>
      <p className="text-sm text-secondary mb-3">*For detailed success analysis, visit the **Success Library** tab*</p>
      
      {successStories.length > 0 ? (
        <div className="space-y-3 mb-4">
          <div className="text-sm text-green-600 bg-green-50 p-2 rounded mb-3">
            🎉 Found {successStories.length} high-performing pages (score ≥ 7.7)
          </div>
          
          {successStories.map((story: any, i: number) => (
            <details key={i} className="insights-box">
              <summary className="cursor-pointer font-semibold">
                ⭐ #{i + 1} - {story.page_title} - Score: {story.raw_score?.toFixed(1)}
              </summary>
              <div className="mt-3">
                <div className="grid grid--cols-2 gap-md mb-3">
                  <div>
                    <div className="metric-card">
                      <div className="metric-value">{story.raw_score?.toFixed(1)}/10</div>
                      <div className="metric-label">Score</div>
                    </div>
                    <div className="metric-card">
                      <div className="metric-value">{story.tier}</div>
                      <div className="metric-label">Tier</div>
                    </div>
                    
                    {story.key_strengths && story.key_strengths.length > 0 && (
                      <div className="mt-3">
                        <strong>✨ Key Strengths:</strong>
                        <ul className="text-sm mt-1 space-y-1">
                          {story.key_strengths.slice(0, 2).map((strength: string, idx: number) => (
                            <li key={idx}>• {strength}</li>
                          ))}
                        </ul>
                      </div>
                    )}
                  </div>
                  
                  <div>
                    {story.evidence && story.evidence !== 'nan' && String(story.evidence).trim().length > 10 ? (
                      <div>
                        <strong>📋 Evidence:</strong>
                        <p className="text-sm mt-1 italic">
                          {String(story.evidence).length > 200 
                            ? `${String(story.evidence).substring(0, 200)}...` 
                            : String(story.evidence)
                          }
                        </p>
                      </div>
                    ) : (
                      <div>
                        <strong>📋 Evidence:</strong>
                        <p className="text-sm mt-1 italic">Evidence details available in Success Library tab</p>
                      </div>
                    )}
                  </div>
                </div>
                
                <p className="text-sm text-secondary mt-2">
                  *👉 For pattern analysis and replication guide, visit **Success Library** tab*
                </p>
              </div>
            </details>
          ))}
        </div>
      ) : (
        <div className="insights-box">
          <p>⚠️ No pages currently scoring 7.7 or above. Focus on improvement opportunities.</p>
        </div>
      )}

      {/* Strategic Recommendations */}
      {recs.length > 0 && (
        <div>
          <h2>💡 Strategic Recommendations</h2>
          <p className="text-sm text-secondary mb-3">*AI-generated action priorities based on current brand health*</p>
          
          <div className="space-y-3 mb-4">
            {recs.map((rec: any, i: number) => (
              <div key={i} className="insights-box">
                <div className="flex justify-between items-start">
                  <div className="flex-1">
                    <strong>{i + 1}.</strong> {rec}
                  </div>
                  <div className="ml-4">
                    {rec.toLowerCase().includes('critical pages') || rec.toLowerCase().includes('scoring below') ? (
                      <button className="nav-button">🔍 View Critical Pages</button>
                    ) : rec.toLowerCase().includes('quick wins') || rec.toLowerCase().includes('immediate impact') ? (
                      <button className="nav-button">⚡ See Quick Wins</button>
                    ) : rec.toLowerCase().includes('persona') ? (
                      <button className="nav-button">👥 Analyze Persona</button>
                    ) : rec.toLowerCase().includes('improvements') || rec.toLowerCase().includes('opportunities') ? (
                      <button className="nav-button">💡 Get Action Plan</button>
                    ) : (
                      <button className="nav-button">📊 Explore Analysis</button>
                    )}
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Page Performance Overview */}
      <h2>📄 Page Performance Overview</h2>
      <p className="text-sm text-secondary mb-3">*Quick visual overview of brand scores across all audited pages*</p>
      
      <div className="page-performance-section">
        <PagesList />
      </div>

      {/* Deep-Dive Analysis Navigation */}
      <h2>🧭 Deep-Dive Analysis</h2>
      <p className="mb-3"><strong>Need more details?</strong> Visit these specialized tabs for comprehensive analysis:</p>
      
      <div className="grid grid--cols-3 gap-lg mb-4">
        <div>
          <strong>📊 Analysis Tabs:</strong>
          <ul className="text-sm mt-2 space-y-1">
            <li>• <strong>👥 Persona Insights</strong> - How different personas experience your brand</li>
            <li>• <strong>📊 Content Matrix</strong> - Detailed performance by content type and tier</li>
          </ul>
        </div>
        
        <div>
          <strong>🎯 Action Tabs:</strong>
          <ul className="text-sm mt-2 space-y-1">
            <li>• <strong>💡 Opportunity & Impact</strong> - Comprehensive improvement roadmap</li>
            <li>• <strong>🌟 Success Library</strong> - Pattern analysis and replication guides</li>
          </ul>
        </div>
        
        <div>
          <strong>📋 Data & Tools:</strong>
          <ul className="text-sm mt-2 space-y-1">
            <li>• <strong>📋 Reports & Export</strong> - Custom reports and data exports</li>
            <li>• <strong>🚀 Run Audit</strong> - Generate fresh audit data</li>
          </ul>
        </div>
      </div>
    </div>
  )
}

export default ExecutiveDashboard
