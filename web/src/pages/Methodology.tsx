import { useState } from 'react'
import { useQuery } from '@tanstack/react-query'
import { Banner, ExpandableCard, PageContainer } from '../components'

const apiBase = import.meta.env.VITE_API_URL || 'http://localhost:3000'

function Methodology() {
  const [activeTab, setActiveTab] = useState('overview')

  const { data: methodologyData, isLoading, error } = useQuery({
    queryKey: ['methodology'],
    queryFn: async () => {
      const res = await fetch(`${apiBase}/api/methodology`)
      if (!res.ok) throw new Error('Failed to load methodology')
      return res.json()
    }
  })

  if (isLoading) return (
    <PageContainer title="🔬 Methodology">
      <p>Loading methodology...</p>
    </PageContainer>
  )
  if (error) return (
    <PageContainer title="🔬 Methodology">
      <p>Error loading methodology data</p>
    </PageContainer>
  )

  const data = methodologyData || {} as any

  const tabs = [
    { id: 'overview', label: 'Overview' },
    { id: 'scoring', label: 'Scoring Framework' },
    { id: 'classification', label: 'Page Classification' },
    { id: 'criteria', label: 'Tier Criteria' },
    { id: 'standards', label: 'Brand Standards' },
    { id: 'controls', label: 'Quality Controls' }
  ]

  const renderOverview = () => (
    <div className="container--content">
      <h2 className="heading--section">Brand Health Audit Methodology</h2>
      
      <div className="container--section">
        <h4 className="heading--card">{data.metadata?.name || 'Brand Audit Methodology'}</h4>
        <p className="text--body"><strong>Version:</strong> {data.metadata?.version || 'N/A'} | <strong>Updated:</strong> {data.metadata?.updated || 'N/A'}</p>
        <p className="text--body"><strong>Corporate Tagline:</strong> "{data.metadata?.tagline || 'The world is how we shape it'}"</p>
        <p className="text--body">{data.metadata?.description || ''}</p>
      </div>

      <div className="container--section">
        <h4 className="heading--card">Brand Score Calculation</h4>
        <p className="text--body"><strong>Formula:</strong> <code>{data.calculation?.formula || ''}</code></p>
        <ul>
          <li><strong>Onsite Weight:</strong> {(data.calculation?.onsite_weight || 0.7) * 100}% (Your website and digital properties)</li>
          <li><strong>Offsite Weight:</strong> {(data.calculation?.offsite_weight || 0.3) * 100}% (Third-party platforms and reviews)</li>
          <li><strong>Crisis Impact:</strong> Can reduce overall score by up to 70%</li>
        </ul>
      </div>

      <div className="container--section">
        <h4 className="heading--card">Crisis Impact Multipliers</h4>
        <p className="text--body">Reputation issues can significantly impact your overall brand health score:</p>
        <div className="spacing--sm">
          {Object.entries(data.calculation?.crisis_multipliers || {}).map(([crisis, multiplier]) => {
            const mult = multiplier as number
            const reduction = (1 - mult) * 100
            const color = mult === 1.0 ? '#28a745' : mult >= 0.9 ? '#fd7e14' : '#dc3545'
            return (
              <div key={crisis} style={{ borderLeft: `4px solid ${color}`, padding: '10px', margin: '5px 0', background: '#f8f9fa' }}>
                <strong>{crisis.replace('_', ' ').replace(/\b\w/g, l => l.toUpperCase())}:</strong> {mult} multiplier 
                {reduction > 0 ? ` (${reduction.toFixed(0)}% reduction)` : ' (no reduction)'}
              </div>
            )
          })}
        </div>
      </div>

      <div className="container--section">
        <h4 className="heading--card">Audit Process</h4>
        <p className="text--body">The brand health audit follows a structured 5-stage process:</p>
        <ol>
          <li><strong>Page Classification:</strong> Categorize content into Tier 1 (Brand), Tier 2 (Value Prop), or Tier 3 (Functional)</li>
          <li><strong>Criteria Assessment:</strong> Apply tier-specific scoring criteria with appropriate brand/performance weightings</li>
          <li><strong>Evidence Collection:</strong> Gather verbatim quotes and specific examples to support all scores</li>
          <li><strong>Brand Consistency Check:</strong> Validate messaging hierarchy, visual identity, and approved content usage</li>
          <li><strong>Strategic Recommendations:</strong> Prioritize improvements by impact, effort, and urgency</li>
        </ol>
      </div>
    </div>
  )

  const renderScoring = () => (
    <div>
      <h2>Scoring Framework</h2>
      
      <div className="container--content">
        <h4>Scoring Scale</h4>
        <p>All criteria are scored on a <strong>{data.scoring?.scale?.min || 0}-{data.scoring?.scale?.max || 10} scale</strong> with mandatory evidence requirements.</p>
      </div>

      <h3>Score Interpretation</h3>
      {Object.entries(data.scoring?.descriptors || {}).map(([range, details]) => {
        const det = details as any
        const colorMap: any = {
          'red': '#fee',
          'orange': '#fff3cd',
          'yellow': '#fff3cd',
          'green': '#d4edda',
          'dark-green': '#d4edda'
        }
        const borderMap: any = {
          'red': '#dc3545',
          'orange': '#fd7e14',
          'yellow': '#ffc107',
          'green': '#28a745',
          'dark-green': '#155724'
        }
        return (
          <div key={range} style={{ 
            padding: '15px', 
            margin: '10px 0', 
            borderRadius: '5px',
            background: colorMap[det.color] || '#f8f9fa',
            borderLeft: `4px solid ${borderMap[det.color] || '#6c757d'}`
          }}>
            <h5 className="mb-xs">{range}: {det.label}</h5>
            <p className="margin-0"><strong>Status:</strong> {det.status}</p>
          </div>
        )
      })}

      <h3>Evidence Requirements</h3>
      <div className="container--content">
        <h4>Mandatory Evidence Standards</h4>
        <p>All scores must be supported by specific evidence from the audited content:</p>
      </div>

      <div className="spacing--sm">
        <h5>High Scores (≥7)</h5>
        <p><strong>Requirement:</strong> {data.evidence?.high_scores?.requirement || ''}</p>
        <p><strong>Penalty:</strong> {data.evidence?.high_scores?.penalty || ''}</p>
      </div>

      <div className="spacing--sm">
        <h5>Low Scores (≤4)</h5>
        <p><strong>Requirement:</strong> {data.evidence?.low_scores?.requirement || ''}</p>
        <p><strong>Penalty:</strong> {data.evidence?.low_scores?.penalty || ''}</p>
      </div>
    </div>
  )

  const renderClassification = () => (
    <div>
      <h2>Page Classification System</h2>
      
      <div className="container--content">
        <h4>Three-Tier Classification</h4>
        <p>Every page is classified into one of three tiers, each with different brand/performance weightings and criteria:</p>
      </div>

      {Object.entries(data.classification?.onsite || {}).map(([tierKey, tierData]) => {
        const tier = tierData as any
        return (
          <Banner
            key={tierKey}
            message={
              <>
                <h4>{tierKey.replace('_', ' ').replace(/\b\w/g, l => l.toUpperCase())}: {tier.name}</h4>
                <div className="container--grid">
                  <div>
                    <strong>Weight in Onsite:</strong> {(tier.weight_in_onsite * 100).toFixed(0)}%
                  </div>
                  <div>
                    <strong>Brand Focus:</strong> {tier.brand_percentage}%
                  </div>
                  <div>
                    <strong>Performance Focus:</strong> {tier.performance_percentage}%
                  </div>
                </div>
                
                <div className="container--grid">
                  <div>
                    <h5>Triggers</h5>
                    <ul>
                      {tier.triggers?.map((trigger: any, idx: number) => (
                        <li key={idx}>{trigger}</li>
                      ))}
                    </ul>
                  </div>
                  <div>
                    <h5>Examples</h5>
                    <ul>
                      {tier.examples?.map((example: any, idx: number) => (
                        <li key={idx}>{example}</li>
                      ))}
                    </ul>
                  </div>
                </div>
              </>
            }
          />
        )
      })}

      <h3>Offsite Channel Classification</h3>
      {Object.entries(data.classification?.offsite || {}).map(([channelKey, channelData]) => {
        const channel = channelData as any
        return (
          <div key={channelKey} className="container--content">
            <h5>{channel.name}</h5>
            <p><strong>Weight in Offsite:</strong> {(channel.weight_in_offsite * 100).toFixed(0)}%</p>
            <p><strong>Brand Focus:</strong> {channel.brand_percentage}%</p>
            {channel.authenticity_percentage && (
              <p><strong>Authenticity Focus:</strong> {channel.authenticity_percentage}%</p>
            )}
            {channel.sentiment_percentage && (
              <p><strong>Sentiment Focus:</strong> {channel.sentiment_percentage}%</p>
            )}
            <p><strong>Examples:</strong> {channel.examples?.join(', ')}</p>
          </div>
        )
      })}
    </div>
  )

  const renderCriteria = () => (
    <div>
      <h2>Tier-Specific Criteria</h2>
      
      {Object.entries(data.criteria || {}).map(([tierKey, tierCriteria]) => {
        const tier = tierCriteria as any
        const tierName = tierKey.replace('_', ' ').replace(/\b\w/g, l => l.toUpperCase())
        
        return (
          <div key={tierKey}>
            <h3>{tierName} Criteria</h3>
            
            {/* Brand Criteria */}
            {tier.brand_criteria && (
              <div>
                <h4>Brand Criteria:</h4>
                {Object.entries(tier.brand_criteria).map(([criterionKey, criterionData]) => {
                  const criterion = criterionData as any
                  return (
                    <ExpandableCard 
                      key={criterionKey} 
                      title={`${criterionKey.replace('_', ' ').replace(/\b\w/g, l => l.toUpperCase())} (${criterion.weight}%)`}
                    >
                      <div className="spacing--sm">
                        <p><strong>Description:</strong> {criterion.description}</p>
                        <p><strong>Requirements:</strong></p>
                        <ul>
                          {criterion.requirements?.map((req: string, idx: number) => (
                            <li key={idx}>{req}</li>
                          ))}
                        </ul>
                      </div>
                    </ExpandableCard>
                  )
                })}
              </div>
            )}
            
            {/* Performance Criteria */}
            {tier.performance_criteria && (
              <div>
                <h4>Performance Criteria:</h4>
                {Object.entries(tier.performance_criteria).map(([criterionKey, criterionData]) => {
                  const criterion = criterionData as any
                  return (
                    <ExpandableCard 
                      key={criterionKey} 
                      title={`${criterionKey.replace('_', ' ').replace(/\b\w/g, l => l.toUpperCase())} (${criterion.weight}%)`}
                    >
                      <div className="spacing--sm">
                        <p><strong>Description:</strong> {criterion.description}</p>
                        <p><strong>Requirements:</strong></p>
                        <ul>
                          {criterion.requirements?.map((req: string, idx: number) => (
                            <li key={idx}>{req}</li>
                          ))}
                        </ul>
                      </div>
                    </ExpandableCard>
                  )
                })}
              </div>
            )}
            
            <hr className="my-2xl" />
          </div>
        )
      })}
    </div>
  )

  const renderStandards = () => (
    <div>
      <h2>Brand Standards</h2>
      
      <h3>Messaging Hierarchy</h3>
      {Object.entries(data.standards?.messaging_hierarchy || {}).map(([levelKey, levelData]) => {
        const level = levelData as any
        return (
          <ExpandableCard key={levelKey} title={`${level.level}: ${level.name}`}>
            <div className="spacing--sm">
              <p><strong>Description:</strong> {level.description}</p>
              <p><strong>Examples:</strong></p>
              <ul>
                {level.examples?.map((ex: string, idx: number) => (
                  <li key={idx}>{ex}</li>
                ))}
              </ul>
            </div>
          </ExpandableCard>
        )
      })}

      <h3>Approved Content</h3>
      {Object.entries(data.standards?.approved_content || {}).map(([contentKey, contentData]) => {
        const content = contentData as any
        return (
          <ExpandableCard key={contentKey} title={contentKey.replace(/_/g, ' ')}>
            <div className="spacing--sm">
              <p><strong>Description:</strong> {content.description}</p>
              <p><strong>Approved Sources:</strong></p>
              <ul>
                {content.approved_sources?.map((source: string, idx: number) => (
                  <li key={idx}>{source}</li>
                ))}
              </ul>
              {content.usage_guidelines && (
                <>
                  <p><strong>Usage Guidelines:</strong></p>
                  <ul>
                    {content.usage_guidelines?.map((guide: string, idx: number) => (
                      <li key={idx}>{guide}</li>
                    ))}
                  </ul>
                </>
              )}
            </div>
          </ExpandableCard>
        )
      })}

      <h3>Visual Identity</h3>
      {Object.entries(data.standards?.visual_identity || {}).map(([elementKey, elementData]) => {
        const element = elementData as any
        return (
          <ExpandableCard key={elementKey} title={element.name}>
            <div className="spacing--sm">
              <p><strong>Description:</strong> {element.description}</p>
              <p><strong>Guidelines:</strong></p>
              <ul>
                {element.guidelines?.map((guide: string, idx: number) => (
                  <li key={idx}>{guide}</li>
                ))}
              </ul>
            </div>
          </ExpandableCard>
        )
      })}
    </div>
  )

  const renderControls = () => (
    <div>
      <h2>Quality Controls & Validation</h2>
      
      <h3>Hard Gating Rules (Non-Negotiable)</h3>
      <div className="container--content">
        <h4>Critical Quality Gates</h4>
        <p>These rules automatically trigger score penalties and cannot be overridden:</p>
      </div>

      {Object.entries(data.gating_rules || {}).map(([ruleKey, ruleData]) => {
        const severityColors: { [key: string]: string } = {
          'CRITICAL': '#dc3545',
          'HIGH': '#fd7e14',
          'MEDIUM': '#ffc107'
        }
        const rule = ruleData as any
        const color = severityColors[rule.severity] || '#6c757d'
        
        return (
          <div key={ruleKey} style={{ borderLeft: `4px solid ${color}`, padding: '15px', margin: '10px 0', background: '#f8f9fa' }}>
            <h5 className="mb-xs">{rule.severity} - {ruleKey.replace('_', ' ').replace(/\b\w/g, l => l.toUpperCase())}</h5>
            <p><strong>Trigger:</strong> {rule.trigger}</p>
            <p><strong>Penalty:</strong> {rule.penalty}</p>
          </div>
        )
      })}

      <h3>Copy Quality Penalties</h3>
      {Object.entries(data.quality_penalties || {}).map(([penaltyKey, penaltyData]) => {
        const penalty = penaltyData as any
        return (
          <div key={penaltyKey} className="container--content" style={{ padding: '10px', margin: '5px 0' }}>
            <h5>{penaltyKey.replace('_', ' ').replace(/\b\w/g, l => l.toUpperCase())}: {penalty.points} points</h5>
            {penalty.example && (
              <p><strong>Example:</strong> {penalty.example}</p>
            )}
            {penalty.examples && (
              <div>
                <p><strong>Examples:</strong></p>
                <ul>
                  {penalty.examples.map((ex: string, idx: number) => (
                    <li key={idx}>{ex}</li>
                  ))}
                </ul>
              </div>
            )}
          </div>
        )
      })}

            <h3>Validation Flags</h3>
      {Object.entries(data.validation_flags || {}).map(([flagCategory, flags]) => (
        <div key={flagCategory}>
          <h4>{flagCategory.replace(/\b\w/g, l => l.toUpperCase())} Flags:</h4>
          {Object.entries(flags as any).map(([flagKey, flagData]) => {
            const flag = flagData as any
            return (
              <p key={flagKey}>
                • <strong>{flagKey.replace('_', ' ').replace(/\b\w/g, l => l.toUpperCase())}:</strong> {flag.penalty as string}
              </p>
            )
          })}
        </div>
      ))}

      <h3>Scoring Examples</h3>
      {Object.entries(data.examples || {}).map(([exampleKey, exampleData]) => {
        const example = exampleData as any
        const score = example.score || 0
        const scoreColor = score >= 8 ? '#28a745' : score <= 4 ? '#dc3545' : '#ffc107'
        
        return (
          <ExpandableCard 
            key={exampleKey} 
            title={`${exampleKey.replace('_', ' ').replace(/\b\w/g, l => l.toUpperCase())} (Score: ${score}/10)`}
          >
            <div className="spacing--sm">
              <div style={{ borderLeft: `4px solid ${scoreColor}`, padding: '10px', background: '#f8f9fa' }}>
                <p><strong>Example Text:</strong></p>
                <blockquote>"{example.text}"</blockquote>
              </div>
              
              {example.why_good && example.why_good.length > 0 && (
                <div>
                  <p><strong>Why this scores well:</strong></p>
                  <ul>
                    {example.why_good.map((reason: string, idx: number) => (
                      <li key={idx}>{reason}</li>
                    ))}
                  </ul>
                </div>
              )}
              
              {example.why_bad && example.why_bad.length > 0 && (
                <div>
                  <p><strong>Why this scores poorly:</strong></p>
                  <ul>
                    {example.why_bad.map((reason: string, idx: number) => (
                      <li key={idx}>{reason}</li>
                    ))}
                  </ul>
                </div>
              )}
            </div>
          </ExpandableCard>
        )
      })}
    </div>
  )

  const renderTabContent = () => {
    switch (activeTab) {
      case 'overview': return renderOverview()
      case 'scoring': return renderScoring()
      case 'classification': return renderClassification()
      case 'criteria': return renderCriteria()
      case 'standards': return renderStandards()
      case 'controls': return renderControls()
      default: return <div />
    }
  }

  return (
    <PageContainer title="🔬 Methodology">
      <div className="container--layout">
        {/* Tab Navigation */}
        <div className="container--section">
          <div className="tabs">
            {tabs.map(tab => (
              <button
                key={tab.id}
                className={`tabs__button ${activeTab === tab.id ? 'tabs__button--active' : ''}`}
                onClick={() => setActiveTab(tab.id)}
              >
                {tab.label}
              </button>
            ))}
          </div>
        </div>

        {/* Tab Content */}
        <div className="container--section">
          {renderTabContent()}
        </div>
      </div>
    </PageContainer>
  )
}

export default Methodology
