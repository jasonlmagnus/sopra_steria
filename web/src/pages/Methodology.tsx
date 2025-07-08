import React, { useState } from 'react'
import { useQuery } from '@tanstack/react-query'

const apiBase = import.meta.env.VITE_API_URL || 'http://localhost:3000'

// Fallback methodology data used when the API is unavailable
const defaultMethodology = {
  metadata: {
    name: 'Sopra Steria Brand Health Audit Methodology',
    version: '2.1',
    updated: '2024-12-15',
    tagline: 'The world is how we shape it',
    description:
      'Comprehensive brand health assessment framework for digital touchpoints and customer experience optimization.'
  },
  calculation: {
    formula: 'Brand Health = (Onsite × 0.7) + (Offsite × 0.3) × Crisis_Multiplier',
    onsite_weight: 0.7,
    offsite_weight: 0.3,
    crisis_multipliers: {
      no_crisis: 1.0,
      minor_issue: 0.95,
      moderate_concern: 0.85,
      major_crisis: 0.6,
      severe_crisis: 0.3
    }
  },
  scoring: {
    scale: { min: 0, max: 10 },
    descriptors: {
      '9-10': {
        label: 'Excellent',
        status: 'Best-in-class brand execution',
        color: 'dark-green'
      },
      '7-8': {
        label: 'Good',
        status: 'Strong brand presence with minor improvements',
        color: 'green'
      },
      '5-6': {
        label: 'Fair',
        status: 'Moderate brand execution needing attention',
        color: 'yellow'
      },
      '3-4': {
        label: 'Poor',
        status: 'Significant brand issues requiring immediate action',
        color: 'orange'
      },
      '0-2': {
        label: 'Critical',
        status: 'Brand crisis requiring urgent intervention',
        color: 'red'
      }
    }
  },
  evidence: {
    high_scores: {
      requirement: 'Must provide specific quotes and examples from audited content',
      penalty: 'Scores reduced by 2 points if evidence is insufficient'
    },
    low_scores: {
      requirement: 'Must document specific issues and provide improvement recommendations',
      penalty: 'Cannot assign low scores without documented evidence'
    }
  },
  classification: {
    onsite: {
      tier_1: {
        name: 'Brand Pages',
        weight_in_onsite: 0.5,
        brand_percentage: 80,
        performance_percentage: 20,
        triggers: ['Homepage', 'About Us', 'Company History', 'Leadership'],
        examples: ['Corporate overview', 'Mission/Vision', 'Company values', 'Executive profiles']
      },
      tier_2: {
        name: 'Value Proposition Pages',
        weight_in_onsite: 0.3,
        brand_percentage: 60,
        performance_percentage: 40,
        triggers: ['Services', 'Solutions', 'Industries', 'Capabilities'],
        examples: ['Service descriptions', 'Industry solutions', 'Case studies', 'Capabilities overview']
      },
      tier_3: {
        name: 'Functional Pages',
        weight_in_onsite: 0.2,
        brand_percentage: 30,
        performance_percentage: 70,
        triggers: ['Contact', 'Careers', 'News', 'Resources'],
        examples: ['Contact forms', 'Job listings', 'Press releases', 'Resource downloads']
      }
    }
  },
  messaging: {
    corporate_hierarchy: {
      global: 'The world is how we shape it',
      regional: 'Digital transformation partner for the BENELUX region',
      sub_narratives: {
        technology: 'Leading technology innovation and digital transformation',
        consulting: 'Strategic consulting for business transformation',
        services: 'End-to-end digital services and solutions'
      }
    },
    value_propositions: [
      'Digital transformation expertise',
      'Industry-specific solutions',
      'Innovation and technology leadership',
      'Trusted partnership approach'
    ],
    strategic_ctas: [
      'Transform your business',
      'Discover our solutions',
      'Partner with us',
      'Explore possibilities'
    ]
  },
  gating_rules: {
    broken_links: {
      trigger: 'Any broken internal or external links',
      penalty: 'Automatic 2-point deduction from overall score',
      severity: 'CRITICAL'
    },
    missing_corporate_messaging: {
      trigger: 'Corporate tagline or positioning not found',
      penalty: '1-point deduction from brand criteria',
      severity: 'HIGH'
    },
    poor_user_experience: {
      trigger: 'Navigation issues or poor mobile experience',
      penalty: '1-point deduction from performance criteria',
      severity: 'MEDIUM'
    }
  },
  quality_penalties: {
    grammar_errors: {
      points: -0.5,
      example: 'Spelling mistakes, grammatical errors, or typos'
    },
    inconsistent_messaging: {
      points: -1,
      example: 'Conflicting value propositions or brand messaging'
    },
    poor_content_quality: {
      points: -1.5,
      example: 'Generic content, poor writing quality, or unclear messaging'
    }
  }
}

function Methodology() {
  const [activeTab, setActiveTab] = useState('overview')

  const { data: methodologyData, isLoading } = useQuery({
    queryKey: ['methodology'],
    queryFn: async () => {
      try {
        const res = await fetch(`${apiBase}/api/methodology`)
        if (!res.ok) throw new Error('Failed to load methodology')
        return await res.json()
      } catch {
        // Use bundled fallback if API request fails
        return defaultMethodology
      }
    }
  })

  if (isLoading) return <div className="main-header"><h1>🔬 Methodology</h1><p>Loading methodology...</p></div>

  const data = methodologyData || defaultMethodology as any

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
    </div>
  )

  const renderCriteria = () => (
    <div>
      <h2>Tier Criteria</h2>
      <div className="insights-box">
        <h4>Tier-Specific Assessment Criteria</h4>
        <p>Each tier has specific criteria that reflect its role in the customer journey and brand experience.</p>
      </div>
      
      <div style={{ background: '#f8fafc', padding: '1.5rem', borderRadius: '8px', border: '1px solid #D1D5DB' }}>
        <p><strong>Note:</strong> Detailed criteria configuration is loaded from the methodology YAML file during actual audits. This includes specific weightings, requirements, and assessment guidelines for each tier.</p>
      </div>
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
        {data.messaging?.value_propositions?.map((prop, idx) => (
          <li key={idx}>{prop}</li>
        ))}
      </ul>

      <h3>Approved Strategic CTAs</h3>
      <ul>
        {data.messaging?.strategic_ctas?.map((cta, idx) => (
          <li key={idx}>{cta}</li>
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
        const severityColors = {
          'CRITICAL': '#dc3545',
          'HIGH': '#fd7e14',
          'MEDIUM': '#ffc107'
        }
        const color = severityColors[ruleData.severity] || '#6c757d'
        
        return (
          <div key={ruleKey} style={{ borderLeft: `4px solid ${color}`, padding: '15px', margin: '10px 0', background: '#f8f9fa' }}>
            <h5 style={{ margin: '0 0 5px 0', color }}>{ruleData.severity} - {ruleKey.replace('_', ' ').replace(/\b\w/g, l => l.toUpperCase())}</h5>
            <p><strong>Trigger:</strong> {ruleData.trigger}</p>
            <p><strong>Penalty:</strong> {ruleData.penalty}</p>
          </div>
        )
      })}

      <h3>Copy Quality Penalties</h3>
      {Object.entries(data.quality_penalties || {}).map(([penaltyKey, penaltyData]) => (
        <div key={penaltyKey} style={{ border: '1px solid #dee2e6', padding: '10px', margin: '5px 0', borderRadius: '5px' }}>
          <h5>{penaltyKey.replace('_', ' ').replace(/\b\w/g, l => l.toUpperCase())}: {penaltyData.points} points</h5>
          {penaltyData.example && (
            <p><strong>Example:</strong> {penaltyData.example}</p>
          )}
        </div>
      ))}
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
