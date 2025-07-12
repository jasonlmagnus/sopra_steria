import { useState } from 'react'
import { useQuery } from '@tanstack/react-query'
import { PlotlyChart } from '../components'

const apiBase = import.meta.env.VITE_API_URL || 'http://localhost:3000'

function OpportunityImpact() {
  const [controls, setControls] = useState({
    impactThreshold: 5.0,
    effortLevel: 'All',
    priorityLevel: 'All',
    contentTier: 'All',
    maxOpportunities: 15
  })

  const { data: opportunityData, isLoading, error } = useQuery({
    queryKey: ['opportunity-impact', controls],
    queryFn: async () => {
      const params = new URLSearchParams({
        impactThreshold: controls.impactThreshold.toString(),
        effortLevel: controls.effortLevel,
        priorityLevel: controls.priorityLevel,
        contentTier: controls.contentTier,
        maxOpportunities: controls.maxOpportunities.toString()
      })
      const res = await fetch(`${apiBase}/api/opportunity-impact?${params}`)
      if (!res.ok) throw new Error('Failed to load opportunity impact data')
      return res.json()
    }
  })

  if (isLoading) return (
    <div>
      <div className="main-header">
        <h1>💡 Opportunity & Impact</h1>
        <p>Loading impact analysis...</p>
      </div>
      <div className="p-2xl text-center">
        <div className="alert">
          <p>🔄 Updating filters...</p>
        </div>
      </div>
    </div>
  )

  if (error) return (
    <div>
      <div className="main-header">
        <h1>💡 Opportunity & Impact</h1>
        <p>Error loading impact analysis</p>
      </div>
      <div className="p-2xl">
        <div className="alert">
          <p>❌ Error: {error.message}</p>
          <p>Please try adjusting your filters or refresh the page.</p>
        </div>
      </div>
    </div>
  )

  const data = opportunityData || {}
  const opportunities = data.opportunities || []
  const overview = data.overview || {}
  const aiRecommendations = data.aiRecommendations || []
  const criteriaAnalysis = data.criteriaAnalysis || {}
  const roadmap = data.roadmap || {}

  // Handle empty data case
  if (data.error || (opportunities.length === 0 && controls.impactThreshold > 0)) {
    return (
      <div>
        <div className="main-header">
          <h1>💡 Opportunity & Impact</h1>
          <p>Which gaps matter most and what should we do?</p>
        </div>

        {/* Show controls even when no data */}
        <ImpactCalculationExplainer />
        <OpportunityControls controls={controls} setControls={setControls} data={data} />

        <div className="insights-box">
          <h2>📊 No Opportunities Match Current Filters</h2>
          <div style={{ 
            background: '#fef3c7', 
            borderLeft: '4px solid #f59e0b', 
            padding: '15px', 
            margin: '15px 0', 
            borderRadius: '5px' 
          }}>
            <h4 style={{ margin: 0, color: '#333' }}>⚠️ Filter Results</h4>
            <p className="font-bold">
              No opportunities match your current filter criteria
            </p>
            <p className="my-xs">
              <strong>Try:</strong> Lowering the impact threshold slider or selecting "All" for other filters
            </p>
          </div>
          
          <div className="p-2xl text-center">
            <p style={{ fontSize: '1.1rem', color: '#6b7280' }}>
              Current filters: <strong>Impact Threshold:</strong> {controls.impactThreshold}, <strong>Effort:</strong> {controls.effortLevel}, 
              <strong>Priority:</strong> {controls.priorityLevel}, <strong>Tier:</strong> {controls.contentTier}
            </p>
          </div>
        </div>
      </div>
    )
  }

  return (
    <div>
      <div className="main-header">
        <h1>💡 Opportunity & Impact</h1>
        <p>Which gaps matter most and what should we do?</p>
      </div>

      {/* Impact Calculation Explanation */}
      <ImpactCalculationExplainer />

      {/* Opportunity Analysis Controls */}
      <OpportunityControls controls={controls} setControls={setControls} data={data} />

      {/* Impact Overview */}
      <ImpactOverview overview={overview} opportunities={opportunities} />

      {/* Prioritized Opportunities */}
      <PrioritizedOpportunities opportunities={opportunities} />

      {/* AI Strategic Recommendations */}
      <AIStrategicRecommendations aiRecommendations={aiRecommendations} data={data} />

      {/* Criteria Deep Dive Analysis */}
      <CriteriaDeepDive criteriaAnalysis={criteriaAnalysis} />

      {/* Action Roadmap */}
      <ActionRoadmap roadmap={roadmap} opportunities={opportunities} />
    </div>
  )
}

function ImpactCalculationExplainer() {
  const [expanded, setExpanded] = useState(false)

  return (
    <div className="insights-box">
      <div 
        className="flex-between-center"
        onClick={() => setExpanded(!expanded)}
      >
        <h3>📊 How Impact is Calculated</h3>
        <span>{expanded ? '▼' : '▶'}</span>
      </div>
      
      {expanded && (
        <div className="mt-lg">
          <div className="p-lg">
            <strong>Impact Score Formula:</strong><br/>
            <code>Impact = (10 - Current Score) × Tier Weight</code>
          </div>
          
          <div className="mt-lg">
            <strong>What this means:</strong>
            <ul>
              <li><strong>Current Score:</strong> The page's performance score (1-10 scale)</li>
              <li><strong>Gap Size:</strong> <code>(10 - Current Score)</code> = How much room for improvement exists</li>
              <li><strong>Tier Weight:</strong> Multiplier based on content tier importance
                <ul>
                  <li>Tier 1: 0.3x weight (supporting content)</li>
                  <li>Tier 2: 0.5x weight (important content)</li>
                  <li>Tier 3: 0.2x weight (secondary content)</li>
                </ul>
              </li>
            </ul>
          </div>

          <div className="mt-lg">
            <strong>Examples:</strong>
            <ul>
              <li>Page scoring 3/10 in Tier 2: Impact = (10-3) × 0.5 = <strong>3.5</strong></li>
              <li>Page scoring 6/10 in Tier 1: Impact = (10-6) × 0.3 = <strong>1.2</strong></li>
              <li>Page scoring 4/10 in Tier 3: Impact = (10-4) × 0.2 = <strong>1.2</strong></li>
            </ul>
          </div>

          <div className="mt-lg">
            <strong>Why this works:</strong>
            <ul>
              <li>Prioritizes pages with bigger performance gaps</li>
              <li>Weights core content more heavily than supporting content</li>
              <li>Results in scores from 0-10 representing improvement potential</li>
            </ul>
          </div>
        </div>
      )}
    </div>
  )
}

function OpportunityControls({ controls, setControls, data }: any) {
  const effortLevels = ['All', 'Low', 'Medium', 'High']
  const priorityLevels = ['All', 'Urgent', 'High', 'Medium', 'Low']
  const tiers = ['All', ...(data.tiers || [])]

  return (
    <div className="insights-box">
      <h2>🎛️ Opportunity Analysis Controls</h2>
      
      <div className="grid">
        <div>
          <label className="font-semibold">
            💥 Min Impact Score: {controls.impactThreshold}
          </label>
          <input 
            type="range"
            min="0"
            max="10"
            step="0.5"
            value={controls.impactThreshold}
            onChange={(e) => setControls({...controls, impactThreshold: parseFloat(e.target.value)})}
            className="w-full"
          />
          <small>Minimum impact score to show opportunities</small>
        </div>

        <div>
          <label className="font-semibold">
            ⚡ Effort Level
          </label>
          <select 
            value={controls.effortLevel}
            onChange={(e) => setControls({...controls, effortLevel: e.target.value})}
            className="w-full"
          >
            {effortLevels.map(level => (
              <option key={level} value={level}>{level}</option>
            ))}
          </select>
        </div>

        <div>
          <label className="font-semibold">
            🎯 Priority Level
          </label>
          <select 
            value={controls.priorityLevel}
            onChange={(e) => setControls({...controls, priorityLevel: e.target.value})}
            className="w-full"
          >
            {priorityLevels.map(level => (
              <option key={level} value={level}>{level}</option>
            ))}
          </select>
        </div>

        <div>
          <label className="font-semibold">
            🏗️ Content Tier
          </label>
          <select 
            value={controls.contentTier}
            onChange={(e) => setControls({...controls, contentTier: e.target.value})}
            className="w-full"
          >
            {tiers.map((tier, index) => (
              <option key={`tier-${index}-${tier}`} value={tier}>{tier}</option>
            ))}
          </select>
        </div>
      </div>

      <div className="grid">
        <div>
          <label className="font-semibold">
            📊 Max Opportunities
          </label>
          <input 
            type="number"
            min="5"
            max="50"
            value={controls.maxOpportunities}
            onChange={(e) => setControls({...controls, maxOpportunities: parseInt(e.target.value)})}
            className="w-full"
          />
        </div>
      </div>
    </div>
  )
}

function ImpactOverview({ overview, opportunities }: any) {
  const totalOpportunities = opportunities.length
  const totalImpact = opportunities.reduce((sum: number, opp: any) => sum + (opp.potentialImpact || 0), 0)
  const avgImpact = totalOpportunities > 0 ? totalImpact / totalOpportunities : 0
  const urgentOpportunities = opportunities.filter((opp: any) => (opp.potentialImpact || 0) >= 9.0).length

  return (
    <div className="insights-box">
      <h2>📊 Impact Overview</h2>
      
      <div className="grid">
        <div className="metric-card">
          <div className="metric-value">{totalOpportunities}</div>
          <div className="metric-label">Total Opportunities</div>
        </div>
        <div className="metric-card">
          <div className="metric-value">{totalImpact.toFixed(1)}</div>
          <div className="metric-label">Total Impact Potential</div>
        </div>
        <div className="metric-card">
          <div className="metric-value">{avgImpact.toFixed(1)}</div>
          <div className="metric-label">Average Impact Score</div>
        </div>
        <div className="metric-card">
          <div className="metric-value">{urgentOpportunities}</div>
          <div className="metric-label">Urgent Opportunities</div>
        </div>
      </div>

      {/* Impact Distribution Chart */}
      {opportunities.length > 0 && (
        <div className="mt-2xl">
          <PlotlyChart 
            data={[{
              type: 'histogram',
              x: opportunities.map((opp: any) => opp.potentialImpact || 0),
              nbinsx: 20,
              marker: { color: '#3d4a6b' }
            }]}
            layout={{
              title: 'Impact Score Distribution',
              xaxis: { title: 'Impact Score' },
              yaxis: { title: 'Number of Opportunities' },
              height: 400
            }}
          />
        </div>
      )}
    </div>
  )
}

function PrioritizedOpportunities({ opportunities }: any) {
  const [expandedCards, setExpandedCards] = useState<Set<number>>(new Set([0, 1, 2])) // Expand top 3 by default

  const toggleCard = (index: number) => {
    const newExpanded = new Set(expandedCards)
    if (newExpanded.has(index)) {
      newExpanded.delete(index)
    } else {
      newExpanded.add(index)
    }
    setExpandedCards(newExpanded)
  }

  // Group opportunities by tier
  const tierGroups = opportunities.reduce((groups: any, opp: any) => {
    const tier = opp.tier || 'Unknown'
    if (!groups[tier]) groups[tier] = []
    groups[tier].push(opp)
    return groups
  }, {})

  return (
    <div className="insights-box">
      <h2>🎯 Prioritized Improvement Opportunities</h2>
      
      {/* Tier Summary */}
      <h3>Opportunities by Content Tier</h3>
      {Object.entries(tierGroups).map(([tier, opps]: [string, any]) => {
        const avgImpact = opps.reduce((sum: number, opp: any) => sum + (opp.potentialImpact || 0), 0) / opps.length
        const avgScore = opps.reduce((sum: number, opp: any) => sum + (opp.currentScore || 0), 0) / opps.length
        
        return (
          <div key={tier} className="mb-md">
            <strong>{tier}:</strong> {opps.length} opps | Avg Impact: {avgImpact.toFixed(1)}/10 | Avg Score: {avgScore.toFixed(1)}/10
          </div>
        )
      })}

      {/* Individual Opportunities */}
      <h3 className="mt-2xl">Prioritized Improvement Opportunities</h3>
      
      {opportunities.length === 0 ? (
        <div className="text-center">
          📊 No opportunities identified. Try adjusting the filters.
        </div>
      ) : (
        opportunities.map((opp: any, index: number) => (
          <OpportunityCard 
            key={index} 
            opportunity={opp} 
            rank={index + 1}
            expanded={expandedCards.has(index)}
            onToggle={() => toggleCard(index)}
          />
        ))
      )}
    </div>
  )
}

function OpportunityCard({ opportunity, rank, expanded, onToggle }: any) {
  const impact = opportunity.potentialImpact || 0
  const currentScore = opportunity.currentScore || 0
  const effort = opportunity.effortLevel || 'Unknown'
  const pageTitle = opportunity.pageTitle || opportunity.pageId || 'Unknown Page'
  
  // Determine priority level and styling
  let priorityClass = "priority-medium"
  let priorityLabel = "💡 MEDIUM"
  
  if (impact >= 9.0) {
    priorityClass = "priority-urgent"
    priorityLabel = "🚨 URGENT"
  } else if (impact >= 7.0) {
    priorityClass = "priority-high"
    priorityLabel = "🔥 HIGH"
  }

  const title = `#${rank} - ${pageTitle} (${priorityLabel})`

  return (
    <div className="mb-lg">
      <div 
        className="flex-between-center"
        onClick={onToggle}
      >
        <h4 className="margin-0">{title}</h4>
        <span>{expanded ? '▼' : '▶'}</span>
      </div>

      {expanded && (
        <div className="p-lg">
          {/* Metrics Row */}
          <div className="grid">
            <div className="metric-card">
              <div className="metric-value">{currentScore.toFixed(1)}/10</div>
              <div className="metric-label">Current Score</div>
            </div>
            <div className="metric-card">
              <div className="metric-value">{impact.toFixed(1)}/10</div>
              <div className="metric-label">Potential Impact</div>
            </div>
            <div className="metric-card">
              <div className="metric-value">{effort}</div>
              <div className="metric-label">Effort Level</div>
            </div>
            <div className="metric-card">
              <div className="metric-value">+{(impact - currentScore).toFixed(1)}</div>
              <div className="metric-label">Improvement Potential</div>
            </div>
          </div>

          {/* Recommendation */}
          <div className="mb-lg">
            <h4>💡 Recommended Action</h4>
            <div className="p-lg">
              <strong>Action:</strong> {opportunity.recommendation || 'Improve page performance based on identified gaps'}
            </div>
          </div>

          {/* Supporting Evidence */}
          <div>
            <h4>📋 Supporting Evidence & Analysis</h4>
            
            {/* Experience Metrics */}
            <div className="grid">
              <div>
                <strong>🟢 Sentiment:</strong> {opportunity.sentiment || 'Unknown'}
              </div>
              <div>
                <strong>🟡 Engagement:</strong> {opportunity.engagement || 'Unknown'}
              </div>
              <div>
                <strong>🔴 Conversion:</strong> {opportunity.conversion || 'Unknown'}
              </div>
            </div>

            {/* Content Examples */}
            <div className="grid">
              <div className="p-lg">
                <strong>✅ What's Working Well:</strong><br/>
                {opportunity.effectiveExamples || 'No specific effective examples identified'}
              </div>
              <div className="p-lg">
                <strong>❌ What's Not Working:</strong><br/>
                {opportunity.ineffectiveExamples || 'No specific ineffective examples identified'}
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}

function AIStrategicRecommendations({ aiRecommendations, data }: any) {
  return (
    <div className="insights-box">
      <h2>🤖 AI Strategic Recommendations</h2>
      
      {aiRecommendations.length > 0 ? (
        <div>
          <div className="mb-lg">
            🎯 Generated {aiRecommendations.length} strategic recommendations
          </div>
          
          {aiRecommendations.map((rec: string, index: number) => (
            <div key={index} className="mb-lg">
              <h4>🤖 AI Recommendation #{index + 1}</h4>
              <p>{rec}</p>
            </div>
          ))}
        </div>
      ) : (
        <div className="text-muted">
          🤖 AI strategic recommendations not available. Executive summary may need to be regenerated.
        </div>
      )}

      {/* AI Pattern Analysis */}
      <AIPatternAnalysis data={data} />
    </div>
  )
}

function AIPatternAnalysis({ data }: any) {
  const patterns = data.patterns || []

  return (
    <div className="mt-2xl">
      <h3>🔍 AI Pattern Analysis</h3>
      
      {patterns.length > 0 ? (
        patterns.map((insight: string, index: number) => (
          <div key={index} className="p-lg">
            {insight}
          </div>
        ))
      ) : (
        <div className="text-muted">
          📊 Pattern analysis not available for current dataset.
        </div>
      )}
    </div>
  )
}

function CriteriaDeepDive({ criteriaAnalysis }: any) {
  const criteria = criteriaAnalysis.criteria || []
  const correlations = criteriaAnalysis.correlations || []

  return (
    <div className="insights-box">
      <h2>🎯 Criteria Deep Dive Analysis</h2>
      
      {criteria.length > 0 ? (
        <div>
          {/* Bottom 5 Criteria */}
          <div className="mb-2xl">
            <strong>🎯 Biggest Improvement Opportunities (Bottom 5 Criteria)</strong>
          </div>

          {criteria.slice(0, 5).map((criterion: any, index: number) => {
            const improvementPotential = 10 - criterion.score
            return (
              <div key={index} className="p-lg">
                <strong>#{index + 1} - {criterion.name}</strong><br/>
                Current Score: {criterion.score.toFixed(1)}/10 | Improvement Potential: +{improvementPotential.toFixed(1)}
              </div>
            )
          })}

          {/* Criteria Performance Chart */}
          <div className="mt-2xl">
            <PlotlyChart 
              data={[{
                type: 'bar',
                x: criteria.map((c: any) => c.score),
                y: criteria.map((c: any) => c.name),
                orientation: 'h',
                marker: { 
                  color: criteria.map((c: any) => c.score),
                  colorscale: 'RdYlGn',
                  cmin: 0,
                  cmax: 10
                }
              }]}
              layout={{
                title: 'Criteria Performance (Worst to Best)',
                xaxis: { title: 'Score' },
                yaxis: { title: 'Criteria' },
                height: Math.max(300, criteria.length * 25)
              }}
            />
          </div>

          {/* Correlation Analysis */}
          {correlations.length > 0 && (
            <div className="mt-2xl">
              <h3>🔗 Criteria Correlation Analysis</h3>
              
              <div className="mb-lg">
                <h4>🔗 Strong Correlations (|r| &gt; 0.5)</h4>
                
                {correlations.slice(0, 5).map((corr: any, index: number) => {
                  const corrType = corr.correlation > 0 ? "Positive" : "Negative"
                  const corrStrength = Math.abs(corr.correlation) > 0.7 ? "Strong" : "Moderate"
                  
                  return (
                    <div key={index} className="p-lg">
                      <strong>{corrStrength} {corrType} Correlation:</strong><br/>
                      {corr.criteria1} ↔ {corr.criteria2}<br/>
                      Correlation: {corr.correlation.toFixed(2)}
                    </div>
                  )
                })}
              </div>
            </div>
          )}
        </div>
      ) : (
        <div className="text-muted">
          📊 Criteria data not available for deep dive analysis.
        </div>
      )}
    </div>
  )
}

function ActionRoadmap({ roadmap, opportunities }: any) {
  // Categorize opportunities
  const quickWins = opportunities.filter((opp: any) => 
    opp.effortLevel === 'Low' && (opp.potentialImpact || 0) >= 6.0
  )
  const majorProjects = opportunities.filter((opp: any) => 
    opp.effortLevel === 'High' && (opp.potentialImpact || 0) >= 7.0
  )
  const fillIns = opportunities.filter((opp: any) => 
    opp.effortLevel === 'Medium'
  )

  return (
    <div className="insights-box">
      <h2>🗺️ Action Roadmap</h2>
      
      <div className="grid">
        {/* Quick Wins */}
        <div className="p-lg">
          <h3>⚡ Quick Wins (Low Effort, High Impact)</h3>
          <p><strong>{quickWins.length} opportunities</strong></p>
          
          {quickWins.slice(0, 3).map((opp: any, index: number) => (
            <div key={index} style={{ 
              background: 'white', 
              padding: '0.5rem', 
              borderRadius: '4px', 
              marginBottom: '0.5rem' 
            }}>
              <strong>{index + 1}. {opp.pageTitle || 'Unknown'}</strong><br/>
              Impact: {(opp.potentialImpact || 0).toFixed(1)} | Current: {(opp.currentScore || 0).toFixed(1)}
            </div>
          ))}
          
          {quickWins.length > 3 && (
            <div className="text-muted font-italic">
              💡 +{quickWins.length - 3} more quick wins available
            </div>
          )}
        </div>

        {/* Fill-ins */}
        <div className="p-lg">
          <h3>🔧 Fill-ins (Medium Effort)</h3>
          <p><strong>{fillIns.length} opportunities</strong></p>
          
          {fillIns.slice(0, 3).map((opp: any, index: number) => (
            <div key={index} style={{ 
              background: 'white', 
              padding: '0.5rem', 
              borderRadius: '4px', 
              marginBottom: '0.5rem' 
            }}>
              <strong>{index + 1}. {opp.pageTitle || 'Unknown'}</strong><br/>
              Impact: {(opp.potentialImpact || 0).toFixed(1)} | Current: {(opp.currentScore || 0).toFixed(1)}
            </div>
          ))}
          
          {fillIns.length > 3 && (
            <div className="text-muted font-italic">
              💡 +{fillIns.length - 3} more fill-ins available
            </div>
          )}
        </div>

        {/* Major Projects */}
        <div className="p-lg">
          <h3>🚀 Major Projects (High Effort, High Impact)</h3>
          <p><strong>{majorProjects.length} opportunities</strong></p>
          
          {majorProjects.slice(0, 3).map((opp: any, index: number) => (
            <div key={index} style={{ 
              background: 'white', 
              padding: '0.5rem', 
              borderRadius: '4px', 
              marginBottom: '0.5rem' 
            }}>
              <strong>{index + 1}. {opp.pageTitle || 'Unknown'}</strong><br/>
              Impact: {(opp.potentialImpact || 0).toFixed(1)} | Current: {(opp.currentScore || 0).toFixed(1)}
            </div>
          ))}
          
          {majorProjects.length > 3 && (
            <div className="text-muted font-italic">
              💡 +{majorProjects.length - 3} more major projects available
            </div>
          )}
        </div>
      </div>

      {/* Implementation Timeline */}
      <div className="mt-2xl">
        <h3>📅 Suggested Implementation Timeline</h3>
        <div className="p-lg">
          <div><strong>Phase 1 (Weeks 1-2):</strong> Execute top 3 Quick Wins</div>
          <div><strong>Phase 2 (Weeks 3-6):</strong> Start 1-2 Major Projects, continue with Fill-ins</div>
          <div><strong>Phase 3 (Weeks 7-12):</strong> Complete Major Projects, optimize based on results</div>
        </div>
      </div>
    </div>
  )
}

export default OpportunityImpact
