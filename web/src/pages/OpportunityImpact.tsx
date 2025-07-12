import { useState, useEffect } from 'react'
import { useQuery } from '@tanstack/react-query'
import { Banner, BarChart, PageContainer, PageHeader } from '../components'
import { EvidenceDisplay } from '../components/EvidenceDisplay'
import { useFilters } from '../hooks/useFilters'
import { FilterSystem } from '../components/FilterSystem'
import type { FilterConfig } from '../types/filters'

const apiBase = import.meta.env.VITE_API_URL || 'http://localhost:3000'

const opportunityImpactFilters: FilterConfig[] = [
  {
    name: 'impactThreshold',
    label: '💥 Min Impact Score',
    type: 'range',
    defaultValue: 5.0,
    min: 0,
    max: 10,
    step: 0.5,
  },
  {
    name: 'effortLevel',
    label: '⚡ Effort Level',
    type: 'select',
    defaultValue: 'All',
    options: [
      { value: 'All', label: 'All' },
      { value: 'Low', label: 'Low' },
      { value: 'Medium', label: 'Medium' },
      { value: 'High', label: 'High' },
    ],
  },
  {
    name: 'priorityLevel',
    label: '🎯 Priority Level',
    type: 'select',
    defaultValue: 'All',
    options: [
      { value: 'All', label: 'All' },
      { value: 'Urgent', label: 'Urgent' },
      { value: 'High', label: 'High' },
      { value: 'Medium', label: 'Medium' },
      { value: 'Low', label: 'Low' },
    ],
  },
  {
    name: 'contentTier',
    label: '🏗️ Content Tier',
    type: 'select',
    defaultValue: 'All',
  },
  {
    name: 'maxOpportunities',
    label: '📈 Max Opportunities',
    type: 'range',
    defaultValue: 15,
    min: 5,
    max: 50,
    step: 5,
  },
];

function OpportunityImpact() {
  const { filters, setAllFilters } = useFilters();

  useEffect(() => {
    const defaultFilters = opportunityImpactFilters.reduce((acc, filter) => {
      acc[filter.name] = filter.defaultValue;
      return acc;
    }, {} as { [key: string]: any });
    setAllFilters(defaultFilters);
  }, [setAllFilters]);

  const { data: opportunityData, isLoading, error } = useQuery({
    queryKey: ['opportunity-impact', filters],
    queryFn: async () => {
      const params = new URLSearchParams(filters)
      const res = await fetch(`${apiBase}/api/opportunity-impact?${params}`)
      if (!res.ok) throw new Error('Failed to load opportunity impact data')
      return res.json()
    },
    enabled: Object.keys(filters).length > 0, // Only run query when filters are set
  })

  if (isLoading) return (
    <div className="container--layout">
      <PageHeader
        title="💡 Opportunity & Impact"
        description="Loading impact analysis..."
      />
      <div className="container--section text--display">
        <Banner message={<p className="text--body">🔄 Updating filters...</p>} />
      </div>
    </div>
  )

  if (error) return (
    <div className="container--layout">
      <PageHeader
        title="💡 Opportunity & Impact"
        description="Error loading impact analysis"
      />
      <div className="container--section">
        <Banner
          type="error"
          message={
            <>
              <p className="text--body">❌ Error: {error.message}</p>
              <p className="text--body">Please try adjusting your filters or refresh the page.</p>
            </>
          }
        />
      </div>
    </div>
  )

  const data = opportunityData || {};
  data.contentTierOptions = (data.tiers || []).map((t: string) => ({ value: t, label: t }));
  data.contentTierOptions.unshift({ value: 'All', label: 'All Tiers' });
  const opportunities = data.opportunities || []
  const aiRecommendations = data.aiRecommendations || []
  const criteriaAnalysis = data.criteriaAnalysis || {}

  // Handle empty data case
  if (data.error || (opportunities.length === 0 && filters.impactThreshold > 0)) {
    return (
      <PageContainer title="💡 Opportunity & Impact">
        <PageHeader 
          title="💡 Opportunity & Impact"
          description="Which gaps matter most and what should we do?"
        />

        {/* Show controls even when no data */}
        <ImpactCalculationExplainer />
        <FilterSystem config={opportunityImpactFilters} data={data} />

        <div className="container--section">
          <h2 className="heading--section">📊 No Opportunities Match Current Filters</h2>
          <Banner
            type="warning"
            message={
              <>
                <h4 className="reset-text">⚠️ Filter Results</h4>
                <p className="text--emphasis">
                  No opportunities match your current filter criteria
                </p>
                <p className="my-xs">
                  <strong>Try:</strong> Lowering the impact threshold slider or selecting "All" for other filters
                </p>
              </>
            }
          />
          
          <div className="container--section text--display">
            <p className="text--body-large text-gray-600">
              Current filters: <strong>Impact Threshold:</strong> {filters.impactThreshold}, <strong>Effort:</strong> {filters.effortLevel}, 
              <strong>Priority:</strong> {filters.priorityLevel}, <strong>Tier:</strong> {filters.contentTier}
            </p>
          </div>
        </div>
      </PageContainer>
    )
  }

  return (
    <PageContainer title="💡 Opportunity & Impact">
      <PageHeader 
        title="💡 Opportunity & Impact"
        description="Which gaps matter most and what should we do?"
      />

      {/* Impact Calculation Explanation */}
      <ImpactCalculationExplainer />

      {/* Opportunity Analysis Controls */}
      <FilterSystem config={opportunityImpactFilters} data={data} />

      {/* Impact Overview */}
      <ImpactOverview opportunities={opportunities} />

      {/* Prioritized Opportunities */}
      <PrioritizedOpportunities opportunities={opportunities} />

      {/* AI Strategic Recommendations */}
      <AIStrategicRecommendations aiRecommendations={aiRecommendations} data={data} />

      {/* Criteria Deep Dive Analysis */}
      <CriteriaDeepDive criteriaAnalysis={criteriaAnalysis} />

      {/* Action Roadmap */}
      <ActionRoadmap opportunities={opportunities} />
    </PageContainer>
  )
}

function ImpactCalculationExplainer() {
  const [expanded, setExpanded] = useState(false)

  return (
    <div className="container--section">
      <div 
        className="container--layout"
        onClick={() => setExpanded(!expanded)}
      >
        <h3 className="heading--subsection">📊 How Impact is Calculated</h3>
        <span className="text--body">{expanded ? '▼' : '▶'}</span>
      </div>
      
      {expanded && (
        <div className="container--section">
          <div className="container--layout">
            <strong>Impact Score Formula:</strong><br/>
            <code>Impact = (10 - Current Score) × Tier Weight</code>
          </div>
          
          <div className="spacing--sm">
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

          <div className="spacing--sm">
            <strong>Examples:</strong>
            <ul>
              <li>Page scoring 3/10 in Tier 2: Impact = (10-3) × 0.5 = <strong>3.5</strong></li>
              <li>Page scoring 6/10 in Tier 1: Impact = (10-6) × 0.3 = <strong>1.2</strong></li>
              <li>Page scoring 4/10 in Tier 3: Impact = (10-4) × 0.2 = <strong>1.2</strong></li>
            </ul>
          </div>

          <div className="spacing--sm">
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

function ImpactOverview({ opportunities }: any) {
  const totalOpportunities = opportunities.length
  const totalImpact = opportunities.reduce((sum: number, opp: any) => sum + (opp.potentialImpact || 0), 0)
  const avgImpact = totalOpportunities > 0 ? totalImpact / totalOpportunities : 0
  const urgentOpportunities = opportunities.filter((opp: any) => (opp.potentialImpact || 0) >= 9.0).length

  const impactScores = opportunities.map((opp: any) => opp.potentialImpact || 0);

  return (
    <div className="container--section">
      <h2 className="heading--section">📊 Impact Overview</h2>
      
      <div className="container--layout">
        <div className="container--section">
          <div className="text--display">{totalOpportunities}</div>
          <div className="text--display">Total Opportunities</div>
        </div>
        <div className="container--section">
          <div className="text--display">{totalImpact.toFixed(1)}</div>
          <div className="text--display">Total Impact Potential</div>
        </div>
        <div className="container--section">
          <div className="text--display">{avgImpact.toFixed(1)}</div>
          <div className="text--display">Average Impact Score</div>
        </div>
        <div className="container--section">
          <div className="text--display">{urgentOpportunities}</div>
          <div className="text--display">Urgent Opportunities</div>
        </div>
      </div>

      {/* Impact Distribution Chart */}
      {opportunities.length > 0 && (
        <div className="container--section">
          <BarChart
            x={impactScores}
            y={Array.from({ length: impactScores.length }, (_, i) => i + 1)}
            title="Impact Score Distribution"
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
    <div className="container--section">
      <h2 className="heading--section">🎯 Prioritized Improvement Opportunities</h2>
      
      {/* Tier Summary */}
      <h3 className="heading--subsection">Opportunities by Content Tier</h3>
      {Object.entries(tierGroups).map(([tier, opps]: [string, any]) => {
        const avgImpact = opps.reduce((sum: number, opp: any) => sum + (opp.potentialImpact || 0), 0) / opps.length
        const avgScore = opps.reduce((sum: number, opp: any) => sum + (opp.currentScore || 0), 0) / opps.length
        
        return (
          <div key={tier} className="container--section">
            <strong className="text--body">{tier}:</strong> {opps.length} opps | Avg Impact: {avgImpact.toFixed(1)}/10 | Avg Score: {avgScore.toFixed(1)}/10
          </div>
        )
      })}

      {/* Individual Opportunities */}
      <h3 className="heading--subsection">Prioritized Improvement Opportunities</h3>
      
      {opportunities.length === 0 ? (
        <div className="text--display">
          <p className="text--body">📊 No opportunities identified. Try adjusting the filters.</p>
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
  let priorityLabel = "💡 MEDIUM"
  
  if (impact >= 9.0) {
    priorityLabel = "🚨 URGENT"
  } else if (impact >= 7.0) {
    priorityLabel = "🔥 HIGH"
  }

  const title = `#${rank} - ${pageTitle} (${priorityLabel})`

  const evidenceItems = [
    {
      type: 'effective_copy' as const,
      content: opportunity.effectiveExamples || 'No specific effective examples identified',
      title: "What's Working Well"
    },
    {
      type: 'ineffective_copy' as const,
      content: opportunity.ineffectiveExamples || 'No specific ineffective examples identified',
      title: "What's Not Working"
    }
  ];

  return (
    <div className="container--section">
      <div 
        className="container--layout"
        onClick={onToggle}
      >
        <h4 className="heading--subsection margin-0">{title}</h4>
        <span className="text--body">{expanded ? '▼' : '▶'}</span>
      </div>

      {expanded && (
        <div className="container--layout">
          {/* Metrics Row */}
          <div className="container--layout">
            <div className="container--section">
              <div className="text--display">{currentScore.toFixed(1)}/10</div>
              <div className="text--display">Current Score</div>
            </div>
            <div className="container--section">
              <div className="text--display">{impact.toFixed(1)}/10</div>
              <div className="text--display">Potential Impact</div>
            </div>
            <div className="container--section">
              <div className="text--display">{effort}</div>
              <div className="text--display">Effort Level</div>
            </div>
            <div className="container--section">
              <div className="text--display">+{(impact - currentScore).toFixed(1)}</div>
              <div className="text--display">Improvement Potential</div>
            </div>
          </div>

          {/* Recommendation */}
          <div className="container--section">
            <h4 className="heading--subsection">💡 Recommended Action</h4>
            <div className="container--layout">
              <strong className="text--body">Action:</strong> {opportunity.recommendation || 'Improve page performance based on identified gaps'}
            </div>
          </div>

          {/* Supporting Evidence */}
          <EvidenceDisplay evidence={evidenceItems} title="Supporting Evidence & Analysis" />
        </div>
      )}
    </div>
  )
}

function AIStrategicRecommendations({ aiRecommendations, data }: any) {
  return (
    <div className="container--section">
      <h2 className="heading--section">🤖 AI Strategic Recommendations</h2>
      
      {aiRecommendations.length > 0 ? (
        <div>
          <div className="container--section">
            <p className="text--body">🎯 Generated {aiRecommendations.length} strategic recommendations</p>
          </div>
          
          {aiRecommendations.map((rec: string, index: number) => (
            <div key={index} className="container--section">
              <h4 className="heading--subsection">🤖 AI Recommendation #{index + 1}</h4>
              <p className="text--body">{rec}</p>
            </div>
          ))}
        </div>
      ) : (
        <div className="text--body">
          <p className="text--body">🤖 AI strategic recommendations not available. Executive summary may need to be regenerated.</p>
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
    <div className="container--section">
      <h3 className="heading--subsection">🔍 AI Pattern Analysis</h3>
      
      {patterns.length > 0 ? (
        patterns.map((insight: string, index: number) => (
          <div key={index} className="container--layout">
            <p className="text--body">{insight}</p>
          </div>
        ))
      ) : (
        <div className="text--body">
          <p className="text--body">📊 Pattern analysis not available for current dataset.</p>
        </div>
      )}
    </div>
  )
}

function CriteriaDeepDive({ criteriaAnalysis }: any) {
  const criteria = criteriaAnalysis.criteria || []
  const correlations = criteriaAnalysis.correlations || []

  return (
    <div className="container--section">
      <h2 className="heading--section">🎯 Criteria Deep Dive Analysis</h2>
      
      {criteria.length > 0 ? (
        <div>
          {/* Bottom 5 Criteria */}
          <div className="container--section">
            <strong className="text--body">🎯 Biggest Improvement Opportunities (Bottom 5 Criteria)</strong>
          </div>

          {criteria.slice(0, 5).map((criterion: any, index: number) => {
            const improvementPotential = 10 - criterion.score
            return (
              <div key={index} className="container--layout">
                <strong className="text--body">#{index + 1} - {criterion.name}</strong><br/>
                Current Score: {criterion.score.toFixed(1)}/10 | Improvement Potential: +{improvementPotential.toFixed(1)}
              </div>
            )
          })}

          {/* Criteria Performance Chart */}
          <div className="container--section">
            <BarChart
              orientation="h"
              x={criteria.map((c: any) => c.score)}
              y={criteria.map((c: any) => c.name)}
              title="Criteria Performance (Worst to Best)"
            />
          </div>

          {/* Correlation Analysis */}
          {correlations.length > 0 && (
            <div className="container--section">
              <h3 className="heading--subsection">🔗 Criteria Correlation Analysis</h3>
              
              <div className="spacing--sm">
                <h4>🔗 Strong Correlations (|r| &gt; 0.5)</h4>
                
                {correlations.slice(0, 5).map((corr: any, index: number) => {
                  const corrType = corr.correlation > 0 ? "Positive" : "Negative"
                  const corrStrength = Math.abs(corr.correlation) > 0.7 ? "Strong" : "Moderate"
                  
                  return (
                    <div key={index} className="spacing--sm">
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
        <div className="text--body">
          📊 Criteria data not available for deep dive analysis.
        </div>
      )}
    </div>
  )
}

function ActionRoadmap({ opportunities }: any) {
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
    <div className="container--content">
      <h2>🗺️ Action Roadmap</h2>
      
      <div className="container--grid">
        {/* Quick Wins */}
        <div className="spacing--sm">
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
            <div className="text--body text--emphasis">
              💡 +{quickWins.length - 3} more quick wins available
            </div>
          )}
        </div>

        {/* Fill-ins */}
        <div className="spacing--sm">
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
            <div className="text--body text--emphasis">
              💡 +{fillIns.length - 3} more fill-ins available
            </div>
          )}
        </div>

        {/* Major Projects */}
        <div className="spacing--sm">
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
            <div className="text--body text--emphasis">
              💡 +{majorProjects.length - 3} more major projects available
            </div>
          )}
        </div>
      </div>

      {/* Implementation Timeline */}
      <div className="spacing--sm">
        <h3>📅 Suggested Implementation Timeline</h3>
        <div className="spacing--sm">
          <div><strong>Phase 1 (Weeks 1-2):</strong> Execute top 3 Quick Wins</div>
          <div><strong>Phase 2 (Weeks 3-6):</strong> Start 1-2 Major Projects, continue with Fill-ins</div>
          <div><strong>Phase 3 (Weeks 7-12):</strong> Complete Major Projects, optimize based on results</div>
        </div>
      </div>
    </div>
  )
}

export default OpportunityImpact
