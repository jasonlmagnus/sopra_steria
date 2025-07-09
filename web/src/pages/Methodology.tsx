import React, { useState } from 'react'
import { useQuery } from '@tanstack/react-query'

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

  if (isLoading) return <div className="main-header"><h1>🔬 Methodology</h1><p>Loading methodology...</p></div>
  if (error) return <div className="main-header"><h1>🔬 Methodology</h1><p>Error loading methodology data</p></div>

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
    <div>
      <h2>Brand Health Audit Methodology</h2>
      
      <div className="insights-box">
        <h4>{data.metadata?.name || 'Brand Audit Methodology'}</h4>
        <p><strong>Version:</strong> {data.metadata?.version || 'N/A'} | <strong>Updated:</strong> {data.metadata?.updated || 'N/A'}</p>
        <p><strong>Corporate Tagline:</strong> "{data.metadata?.tagline || 'The world is how we shape it'}"</p>
        <p>{data.metadata?.description || ''}</p>
      </div>

      <div className="insights-box">
        <h4>Brand Score Calculation</h4>
        <p><strong>Formula:</strong> <code>{data.calculation?.formula || ''}</code></p>
        <ul>
          <li><strong>Onsite Weight:</strong> {(data.calculation?.onsite_weight || 0.7) * 100}% (Your website and digital properties)</li>
          <li><strong>Offsite Weight:</strong> {(data.calculation?.offsite_weight || 0.3) * 100}% (Third-party platforms and reviews)</li>
          <li><strong>Crisis Impact:</strong> Can reduce overall score by up to 70%</li>
        </ul>
      </div>

      <div className="insights-box">
        <h4>Crisis Impact Multipliers</h4>
        <p>Reputation issues can significantly impact your overall brand health score:</p>
        <div style={{ marginTop: '1rem' }}>
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

      <div className="insights-box">
        <h4>Audit Process</h4>
        <p>The brand health audit follows a structured 5-stage process:</p>
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
      
      <div className="insights-box">
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
            <h5 style={{ margin: '0 0 5px 0' }}>{range}: {det.label}</h5>
            <p style={{ margin: 0 }}><strong>Status:</strong> {det.status}</p>
          </div>
        )
      })}

      <h3>Evidence Requirements</h3>
      <div className="insights-box">
        <h4>Mandatory Evidence Standards</h4>
        <p>All scores must be supported by specific evidence from the audited content:</p>
      </div>

      <div style={{ background: '#f8fafc', padding: '1rem', borderRadius: '8px', border: '1px solid #D1D5DB', margin: '1rem 0' }}>
        <h5>High Scores (≥7)</h5>
        <p><strong>Requirement:</strong> {data.evidence?.high_scores?.requirement || ''}</p>
        <p><strong>Penalty:</strong> {data.evidence?.high_scores?.penalty || ''}</p>
      </div>

      <div style={{ background: '#f8fafc', padding: '1rem', borderRadius: '8px', border: '1px solid #D1D5DB', margin: '1rem 0' }}>
        <h5>Low Scores (≤4)</h5>
        <p><strong>Requirement:</strong> {data.evidence?.low_scores?.requirement || ''}</p>
        <p><strong>Penalty:</strong> {data.evidence?.low_scores?.penalty || ''}</p>
      </div>
    </div>
  )

  const renderClassification = () => (
    <div>
      <h2>Page Classification System</h2>
      
      <div className="insights-box">
        <h4>Three-Tier Classification</h4>
        <p>Every page is classified into one of three tiers, each with different brand/performance weightings and criteria:</p>
      </div>

      {Object.entries(data.classification?.onsite || {}).map(([tierKey, tierData]) => {
        const tier = tierData as any
        return (
          <div key={tierKey} style={{ border: '2px solid #dee2e6', padding: '20px', margin: '15px 0', borderRadius: '8px' }}>
            <h4>{tierKey.replace('_', ' ').replace(/\b\w/g, l => l.toUpperCase())}: {tier.name}</h4>
            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: '1rem', marginBottom: '1rem' }}>
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
            
            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(300px, 1fr))', gap: '1rem' }}>
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
          </div>
        )
      })}

      <h3>Offsite Channel Classification</h3>
      {Object.entries(data.classification?.offsite || {}).map(([channelKey, channelData]) => {
        const channel = channelData as any
        return (
          <div key={channelKey} style={{ border: '1px solid #dee2e6', padding: '15px', margin: '10px 0', borderRadius: '5px' }}>
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
                    <details key={criterionKey} style={{ margin: '1rem 0', padding: '0.5rem', border: '1px solid #dee2e6', borderRadius: '4px' }}>
                      <summary style={{ cursor: 'pointer', fontWeight: 'bold' }}>
                        {criterionKey.replace('_', ' ').replace(/\b\w/g, l => l.toUpperCase())} ({criterion.weight}%)
                      </summary>
                      <div style={{ marginTop: '1rem' }}>
                        <p><strong>Description:</strong> {criterion.description}</p>
                        <p><strong>Requirements:</strong></p>
                        <ul>
                          {criterion.requirements?.map((req: string, idx: number) => (
                            <li key={idx}>{req}</li>
                          ))}
                        </ul>
                      </div>
                    </details>
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
                    <details key={criterionKey} style={{ margin: '1rem 0', padding: '0.5rem', border: '1px solid #dee2e6', borderRadius: '4px' }}>
                      <summary style={{ cursor: 'pointer', fontWeight: 'bold' }}>
                        {criterionKey.replace('_', ' ').replace(/\b\w/g, l => l.toUpperCase())} ({criterion.weight}%)
                      </summary>
                      <div style={{ marginTop: '1rem' }}>
                        <p><strong>Description:</strong> {criterion.description}</p>
                        <p><strong>Requirements:</strong></p>
                        <ul>
                          {criterion.requirements?.map((req: string, idx: number) => (
                            <li key={idx}>{req}</li>
                          ))}
                        </ul>
                      </div>
                    </details>
                  )
                })}
              </div>
            )}
            
            <hr style={{ margin: '2rem 0' }} />
          </div>
        )
      })}
    </div>
  )

  const renderStandards = () => (
    <div>
      <h2>Brand Standards & Messaging</h2>
      
      <div className="insights-box">
        <h4>Brand Messaging Hierarchy</h4>
        <p>Approved messaging elements that must be used consistently across all digital properties:</p>
      </div>

      <div style={{ background: '#f8f9fa', padding: '15px', margin: '10px 0', borderRadius: '5px' }}>
        <h5>Global Corporate Positioning</h5>
        <p style={{ fontWeight: 'bold', color: '#E85A4F' }}>"{data.messaging?.corporate_hierarchy?.global || ''}"</p>
      </div>

      <div style={{ background: '#f8f9fa', padding: '15px', margin: '10px 0', borderRadius: '5px' }}>
        <h5>Regional Narrative (BENELUX)</h5>
        <p style={{ fontWeight: 'bold', color: '#2C3E50' }}>"{data.messaging?.corporate_hierarchy?.regional || ''}"</p>
      </div>

      <h3>Sub-Narratives by Domain</h3>
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(300px, 1fr))', gap: '1rem' }}>
        {Object.entries(data.messaging?.corporate_hierarchy?.sub_narratives || {}).map(([domain, narrative]) => (
          <div key={domain} style={{ border: '1px solid #dee2e6', padding: '10px', borderRadius: '5px' }}>
            <strong>{domain.replace('_', ' ').replace(/\b\w/g, l => l.toUpperCase())}:</strong><br/>
            "{narrative}"
          </div>
        ))}
      </div>

      <h3>Approved Value Propositions</h3>
      <ul>
        {data.messaging?.value_propositions?.map((prop: string, idx: number) => (
          <li key={idx}>{prop}</li>
        ))}
      </ul>

      <h3>Approved Strategic CTAs</h3>
      <ul>
        {data.messaging?.strategic_ctas?.map((cta: string, idx: number) => (
          <li key={idx}>{cta}</li>
        ))}
      </ul>

      <h3>BENELUX Market Positioning</h3>
      <ul>
        {data.messaging?.benelux_positioning?.map((position: string, idx: number) => (
          <li key={idx}>{position}</li>
        ))}
      </ul>
    </div>
  )

  const renderControls = () => (
    <div>
      <h2>Quality Controls & Validation</h2>
      
      <h3>Hard Gating Rules (Non-Negotiable)</h3>
      <div className="insights-box">
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
            <h5 style={{ margin: '0 0 5px 0', color }}>{rule.severity} - {ruleKey.replace('_', ' ').replace(/\b\w/g, l => l.toUpperCase())}</h5>
            <p><strong>Trigger:</strong> {rule.trigger}</p>
            <p><strong>Penalty:</strong> {rule.penalty}</p>
          </div>
        )
      })}

      <h3>Copy Quality Penalties</h3>
      {Object.entries(data.quality_penalties || {}).map(([penaltyKey, penaltyData]) => {
        const penalty = penaltyData as any
        return (
          <div key={penaltyKey} style={{ border: '1px solid #dee2e6', padding: '10px', margin: '5px 0', borderRadius: '5px' }}>
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
          <details key={exampleKey} style={{ margin: '1rem 0', padding: '0.5rem', border: '1px solid #dee2e6', borderRadius: '4px' }}>
            <summary style={{ cursor: 'pointer', fontWeight: 'bold' }}>
              {exampleKey.replace('_', ' ').replace(/\b\w/g, l => l.toUpperCase())} (Score: {score}/10)
            </summary>
            <div style={{ marginTop: '1rem' }}>
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
          </details>
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
      default: return renderOverview()
    }
  }

  return (
    <div>
      <div className="main-header">
        <h1>🔬 Methodology</h1>
        <p>Brand Health Command Center assessment framework and evaluation criteria</p>
      </div>

      {/* Tab Navigation */}
      <div style={{ borderBottom: '1px solid #dee2e6', marginBottom: '2rem' }}>
        <div style={{ display: 'flex', gap: '1rem', flexWrap: 'wrap' }}>
          {tabs.map(tab => (
            <button
              key={tab.id}
              onClick={() => setActiveTab(tab.id)}
              style={{
                padding: '0.75rem 1rem',
                border: 'none',
                background: activeTab === tab.id ? '#E85A4F' : 'transparent',
                color: activeTab === tab.id ? 'white' : '#2C3E50',
                borderRadius: '4px 4px 0 0',
                cursor: 'pointer',
                fontWeight: activeTab === tab.id ? '600' : '400',
                transition: 'all 0.2s'
              }}
            >
              {tab.label}
            </button>
          ))}
        </div>
      </div>

      {/* Tab Content */}
      <div>
        {renderTabContent()}
      </div>

      {/* Footer */}
      <div style={{ marginTop: '50px', padding: '20px', borderTop: '1px solid #D1D5DB', textAlign: 'center', color: '#6c757d' }}>
        <p>Brand Health Command Center - Methodology v{data.metadata?.version || '2.1'}</p>
      </div>
    </div>
  )
}

export default Methodology
