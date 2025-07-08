import React, { useEffect, useState } from 'react'
import { PlotlyChart } from '../components/PlotlyChart'

interface PersonaProfile {
  id: string
  name: string
  content: string
  sections: ProfileSection[]
}

interface ProfileSection {
  title: string
  content: string
}

interface JourneyStep {
  step_number: number
  step_name: string
  persona_reaction: string
  gap_severity: number
  quick_fixes: string[]
}

interface JourneyData {
  steps: JourneyStep[]
  persona_id: string
  persona_name: string
}

interface PerformanceData {
  page_id: string
  url: string
  title: string
  avg_score: number
  tier_name: string
  effective_copy_examples?: string
  ineffective_copy_examples?: string
  business_impact_analysis?: string
}

interface VoiceStats {
  populated: number
  total: number
  percentage: number
}

const PERSONA_NAMES: Record<string, string> = {
  'P1': 'The Benelux Strategic Business Leader (C-Suite Executive)',
  'P2': 'The BENELUX Technology Innovation Leader',
  'P3': 'The Benelux Transformation Programme Leader',
  'P4': 'The Benelux Cybersecurity Decision Maker',
  'P5': 'The Technical Influencer'
}

function PersonaViewer() {
  const [personas, setPersonas] = useState<string[]>([])
  const [selectedPersona, setSelectedPersona] = useState<string>('')
  const [profile, setProfile] = useState<PersonaProfile | null>(null)
  const [journey, setJourney] = useState<JourneyData | null>(null)
  const [performance, setPerformance] = useState<PerformanceData[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [activeTab, setActiveTab] = useState('profile')
  const [selectedTiers, setSelectedTiers] = useState<string[]>([])

  useEffect(() => {
    fetchPersonas()
  }, [])

  useEffect(() => {
    if (selectedPersona) {
      fetchPersonaData(selectedPersona)
    }
  }, [selectedPersona])

  const fetchPersonas = async () => {
    try {
      setLoading(true)
      // Mock persona data - in real app would fetch from API
      const mockPersonas = ['P1', 'P2', 'P3', 'P4', 'P5']
      setPersonas(mockPersonas)
      if (mockPersonas.length > 0) {
        setSelectedPersona(mockPersonas[0])
      }
    } catch (err) {
      setError('Failed to load personas')
    } finally {
      setLoading(false)
    }
  }

  const fetchPersonaData = async (personaId: string) => {
    try {
      setLoading(true)
      
      // Mock profile data
      const mockProfile: PersonaProfile = {
        id: personaId,
        name: PERSONA_NAMES[personaId] || `Business Professional ${personaId}`,
        content: generateMockProfileContent(personaId),
        sections: generateMockProfileSections(personaId)
      }
      
      // Mock journey data
      const mockJourney: JourneyData = {
        steps: generateMockJourneySteps(personaId),
        persona_id: personaId,
        persona_name: PERSONA_NAMES[personaId] || personaId
      }
      
      // Mock performance data
      const mockPerformance: PerformanceData[] = generateMockPerformanceData(personaId)
      
      setProfile(mockProfile)
      setJourney(mockJourney)
      setPerformance(mockPerformance)
      
      // Initialize tier selection
      const availableTiers = [...new Set(mockPerformance.map(p => p.tier_name))]
      setSelectedTiers(availableTiers)
      
    } catch (err) {
      setError('Failed to load persona data')
    } finally {
      setLoading(false)
    }
  }

  const generateMockProfileContent = (personaId: string) => {
    const profiles = {
      'P1': 'Strategic business leader focused on digital transformation, ROI, and competitive advantage. Seeks proven solutions with measurable business impact.',
      'P2': 'Technology innovation leader driving digital transformation initiatives. Balances cutting-edge technology with practical business applications.',
      'P3': 'Transformation programme leader managing large-scale organizational change. Focuses on change management, stakeholder alignment, and measurable outcomes.',
      'P4': 'Cybersecurity decision maker responsible for organizational security strategy. Prioritizes risk management, compliance, and threat protection.',
      'P5': 'Technical influencer with deep expertise in specific technology domains. Influences technical decisions and evaluates solution architectures.'
    }
    return profiles[personaId] || 'Business professional with strategic decision-making responsibilities.'
  }

  const generateMockProfileSections = (personaId: string): ProfileSection[] => {
    return [
      {
        title: 'Role & Responsibilities',
        content: `Primary decision maker for ${personaId === 'P1' ? 'strategic business initiatives' : personaId === 'P2' ? 'technology innovation' : personaId === 'P3' ? 'transformation programmes' : personaId === 'P4' ? 'cybersecurity strategy' : 'technical architecture'}. Manages budget allocation and vendor relationships.`
      },
      {
        title: 'Key Priorities',
        content: `Focuses on ${personaId === 'P1' ? 'business growth and competitive advantage' : personaId === 'P2' ? 'innovation and digital transformation' : personaId === 'P3' ? 'change management and stakeholder alignment' : personaId === 'P4' ? 'risk management and compliance' : 'technical excellence and solution architecture'}.`
      },
      {
        title: 'Pain Points',
        content: `Challenges include ${personaId === 'P1' ? 'proving ROI and managing stakeholder expectations' : personaId === 'P2' ? 'balancing innovation with practical implementation' : personaId === 'P3' ? 'managing resistance to change' : personaId === 'P4' ? 'staying ahead of emerging threats' : 'evaluating vendor capabilities and technical fit'}.`
      },
      {
        title: 'Success Metrics',
        content: `Measured by ${personaId === 'P1' ? 'revenue growth and operational efficiency' : personaId === 'P2' ? 'successful technology implementations' : personaId === 'P3' ? 'transformation programme success rates' : personaId === 'P4' ? 'security incident reduction' : 'technical solution performance and adoption'}.`
      }
    ]
  }

  const generateMockJourneySteps = (personaId: string): JourneyStep[] => {
    const reactions = {
      'P1': [
        'Seeks strategic alignment, concerned about generic messaging',
        'Appreciates calm leadership tone, wants concrete outcomes',
        'Strong alignment with compliance and security goals',
        'Values strategic advantage framing of regulations',
        'Appreciates local presence, frustrated by lack of digital options'
      ],
      'P2': [
        'Reassured by scale and tech focus, wants proof beyond messaging',
        'High relevance to transformation agenda, seeks compliance mention',
        'High relevance for balancing innovation and compliance',
        'Appreciates topical coverage and practical guidance',
        'Likes low-friction language, wants role-specific context'
      ],
      'P3': [
        'Looks for outcome-focused messaging, ROI indicators',
        'Strong alignment with goals, wants success metrics',
        'Measurable outcomes, trusted partner positioning',
        'High-value thought leadership, compliance + innovation narrative',
        'Values partnership emphasis, needs easier contact methods'
      ],
      'P4': [
        'Limited security-specific messaging, feels disconnected',
        'Mixed clarity - poetic tone may obscure practical offerings',
        'Very high relevance for regulatory alignment',
        'Demonstrates thought leadership and regulatory fluency',
        'Comfortable with expert access, wants specialist routing'
      ],
      'P5': [
        'Curious but cautious, wants technical depth',
        'Confidence builds, appreciates technical depth',
        'Reassured by technical depth and delivery capability',
        'Validated and informed, recognizes expertise',
        'Ready to engage, appreciates local presence'
      ]
    }

    const severities = {
      'P1': [3, 2, 1, 2, 4],
      'P2': [2, 3, 2, 2, 3],
      'P3': [3, 2, 2, 1, 3],
      'P4': [3, 2, 2, 1, 2],
      'P5': [2, 1, 1, 1, 2]
    }

    const stepNames = [
      'Step 1: Homepage (Awareness)',
      'Step 2: Service Pages (Consideration)',
      'Step 3: Proof Points (Validation)',
      'Step 4: Thought Leadership (Education)',
      'Step 5: Contact (Conversion)'
    ]

    const quickFixes = [
      [
        'Sharpen value proposition with specific domains',
        'Add prominent CTA button',
        'Include persona-guided navigation',
        'Surface EU trust credentials in hero section'
      ],
      [
        'Add bullet points or sidebar summary',
        'Include compliance and regulatory mentions',
        'Surface case study teasers',
        'Balance inspirational tone with practical deliverables'
      ],
      [
        'Add visual summary with key stats upfront',
        'Include quantified outcomes in case studies',
        'Add filtering by industry/use case',
        'Strengthen proof points with metrics'
      ],
      [
        'Add author credentials and publication dates',
        'Include related articles suggestions',
        'Add social sharing and engagement features',
        'Create downloadable resources'
      ],
      [
        'Add online scheduling/contact form',
        'Include role-specific contact routing',
        'Add local office information',
        'Create specialist team pages'
      ]
    ]

    return stepNames.map((name, index) => ({
      step_number: index + 1,
      step_name: name,
      persona_reaction: reactions[personaId]?.[index] || 'Standard persona reaction',
      gap_severity: severities[personaId]?.[index] || 2,
      quick_fixes: quickFixes[index] || []
    }))
  }

  const generateMockPerformanceData = (personaId: string): PerformanceData[] => {
    const baseScore = personaId === 'P1' ? 7.2 : personaId === 'P2' ? 6.8 : personaId === 'P3' ? 7.5 : personaId === 'P4' ? 6.5 : 7.0
    const pages = [
      { id: 'homepage', title: 'Homepage', tier: 'Tier 1' },
      { id: 'services', title: 'Services Overview', tier: 'Tier 1' },
      { id: 'about', title: 'About Us', tier: 'Tier 2' },
      { id: 'case-studies', title: 'Case Studies', tier: 'Tier 2' },
      { id: 'contact', title: 'Contact', tier: 'Tier 3' },
      { id: 'blog', title: 'Blog', tier: 'Tier 3' }
    ]

    return pages.map(page => ({
      page_id: page.id,
      url: `https://soprasteria.be/${page.id}`,
      title: page.title,
      avg_score: baseScore + (Math.random() - 0.5) * 2,
      tier_name: page.tier,
      effective_copy_examples: Math.random() > 0.3 ? `Effective messaging example for ${page.title}` : undefined,
      ineffective_copy_examples: Math.random() > 0.5 ? `Area for improvement in ${page.title}` : undefined,
      business_impact_analysis: Math.random() > 0.4 ? `Business impact analysis for ${page.title}` : undefined
    }))
  }

  const calculateOverallScore = () => {
    if (performance.length === 0) return 0
    return performance.reduce((sum, p) => sum + p.avg_score, 0) / performance.length
  }

  const getCriticalIssuesCount = () => {
    return performance.filter(p => p.avg_score < 4.0).length
  }

  const getAverageGapSeverity = () => {
    if (!journey) return 0
    return journey.steps.reduce((sum, step) => sum + step.gap_severity, 0) / journey.steps.length
  }

  const getFilteredPerformanceData = () => {
    if (selectedTiers.length === 0) return performance
    return performance.filter(p => selectedTiers.includes(p.tier_name))
  }

  const getVoiceStats = () => {
    const filteredData = getFilteredPerformanceData()
    const voiceColumns = ['effective_copy_examples', 'ineffective_copy_examples', 'business_impact_analysis']
    
    return voiceColumns.reduce((stats, col) => {
      const populated = filteredData.filter(p => p[col as keyof PerformanceData] !== undefined).length
      const total = filteredData.length
      stats[col] = {
        populated,
        total,
        percentage: total > 0 ? (populated / total) * 100 : 0
      }
      return stats
    }, {} as Record<string, VoiceStats>)
  }

  const getScoreDistributionData = () => {
    const scores = getFilteredPerformanceData().map(p => p.avg_score)
    return [{
      x: scores,
      type: 'histogram' as const,
      nbinsx: 20,
      marker: { color: '#E85A4F' }
    }]
  }

  const getJourneyFlowData = () => {
    if (!journey) return []
    
    const stepNames = journey.steps.map(step => step.step_name.replace('Step ', '').replace(': ', ':\\n'))
    const gapScores = journey.steps.map(step => step.gap_severity)
    const colors = gapScores.map(score => score <= 2 ? '#10B981' : score <= 3 ? '#F59E0B' : '#EF4444')
    
    return [{
      x: journey.steps.map((_, index) => index),
      y: gapScores,
      mode: 'lines+markers+text' as const,
      text: gapScores.map(score => `Gap: ${score}/5`),
      textposition: 'top center' as const,
      line: { color: '#E85A4F', width: 3 },
      marker: { size: 15, color: colors, line: { width: 2, color: 'white' } },
      name: 'Journey Flow',
      hovertemplate: '<b>%{text}</b><br>Step: %{x}<br>Severity: %{y}/5<extra></extra>'
    }]
  }

  const getJourneyFlowLayout = () => {
    if (!journey) return {}
    
    const stepNames = journey.steps.map(step => step.step_name.replace('Step ', '').replace(': ', ':\\n'))
    
    return {
      title: 'Journey Gap Severity by Step',
      xaxis: {
        title: 'Journey Steps',
        tickmode: 'array',
        tickvals: journey.steps.map((_, index) => index),
        ticktext: stepNames.map(name => name.includes(':') ? name.split(':')[1].trim() : name)
      },
      yaxis: {
        title: 'Gap Severity (1=Low, 5=High)',
        range: [0, 5]
      },
      height: 400,
      showlegend: false
    }
  }

  if (loading) {
    return (
      <div className="page-container">
        <div className="loading-spinner">Loading Persona Analysis...</div>
      </div>
    )
  }

  if (error) {
    return (
      <div className="page-container">
        <div className="error-message">{error}</div>
      </div>
    )
  }

  return (
    <div className="page-container">
      {/* Header */}
      <div className="main-header">
        <h1>👤 Persona Viewer</h1>
        <p>In-depth persona analysis with voice profiling and content alignment insights</p>
      </div>

      {/* Persona Selection */}
      <div className="section">
        <h2>🎯 Select Persona for Analysis</h2>
        
        <div className="persona-selection">
          <div className="selection-controls">
            <select 
              value={selectedPersona} 
              onChange={(e) => setSelectedPersona(e.target.value)}
              className="persona-selector"
            >
              {personas.map(persona => (
                <option key={persona} value={persona}>
                  {persona} - {PERSONA_NAMES[persona] || 'Business Professional'}
                </option>
              ))}
            </select>
            <div className="persona-count">
              📊 <strong>{personas.length}</strong> personas available for analysis
            </div>
          </div>
        </div>
      </div>

      {selectedPersona && profile && (
        <>
          {/* Persona Overview */}
          <div className="section">
            <div className="persona-overview">
              <div className="persona-card">
                <h3>{profile.name}</h3>
                <p><strong>ID:</strong> {selectedPersona}</p>
              </div>
              
              <div className="overview-metrics">
                <div className="metric-card">
                  <h4>Overall Score</h4>
                  <div className="metric-value">{calculateOverallScore().toFixed(1)}/10</div>
                  <div className="metric-label">Average brand health score</div>
                </div>
                
                <div className="metric-card">
                  <h4>Pages Analyzed</h4>
                  <div className="metric-value">{performance.length}</div>
                  <div className="metric-label">Website pages analyzed</div>
                </div>
                
                <div className="metric-card">
                  <h4>Critical Issues</h4>
                  <div className="metric-value">{getCriticalIssuesCount()}</div>
                  <div className="metric-label">Pages with scores &lt; 4.0</div>
                </div>
              </div>
            </div>
          </div>

          {/* Navigation Tabs */}
          <div className="section">
            <div className="tabs">
              <div className="tab-buttons">
                <button 
                  className={`tab-button ${activeTab === 'profile' ? 'active' : ''}`}
                  onClick={() => setActiveTab('profile')}
                >
                  📋 Profile
                </button>
                <button 
                  className={`tab-button ${activeTab === 'journey' ? 'active' : ''}`}
                  onClick={() => setActiveTab('journey')}
                >
                  🗺️ Journey
                </button>
                <button 
                  className={`tab-button ${activeTab === 'performance' ? 'active' : ''}`}
                  onClick={() => setActiveTab('performance')}
                >
                  📊 Performance
                </button>
                <button 
                  className={`tab-button ${activeTab === 'voice' ? 'active' : ''}`}
                  onClick={() => setActiveTab('voice')}
                >
                  🗣️ Voice
                </button>
              </div>

              <div className="tab-content">
                {activeTab === 'profile' && (
                  <div className="profile-tab">
                    <h2>🎯 Persona Profile</h2>
                    
                    <div className="profile-overview">
                      <div className="profile-summary">
                        <h3>Overview</h3>
                        <p>{profile.content}</p>
                      </div>
                    </div>

                    <div className="profile-sections">
                      {profile.sections.map((section, index) => (
                        <div key={index} className="profile-section">
                          <h4>📋 {section.title}</h4>
                          <div className="section-content">
                            <p>{section.content}</p>
                          </div>
                        </div>
                      ))}
                    </div>
                  </div>
                )}

                {activeTab === 'journey' && journey && (
                  <div className="journey-tab">
                    <h2>🗺️ Journey Analysis</h2>
                    
                    <div className="journey-overview">
                      <div className="journey-info">
                        <p><strong>Analyzing journey for:</strong> {journey.persona_name}</p>
                      </div>
                      
                      <div className="journey-metric">
                        <h4>Avg Gap Severity</h4>
                        <div className="metric-value">{getAverageGapSeverity().toFixed(1)}/5</div>
                        <div className="metric-label">Average friction across all steps</div>
                      </div>
                    </div>

                    <div className="journey-visualization">
                      <h3>📊 Journey Flow & Gap Analysis</h3>
                      <PlotlyChart 
                        data={getJourneyFlowData()}
                        layout={getJourneyFlowLayout()}
                      />
                    </div>

                    <div className="journey-steps">
                      <h3>🔍 Step-by-Step Analysis</h3>
                      
                      {journey.steps.map((step, index) => {
                        const severityLevel = step.gap_severity <= 2 ? 'low' : step.gap_severity <= 3 ? 'medium' : 'high'
                        const severityText = step.gap_severity <= 2 ? 'Low' : step.gap_severity <= 3 ? 'Medium' : 'High'
                        
                        return (
                          <div key={index} className={`journey-step ${severityLevel}`}>
                            <div className="step-header">
                              <h4>📍 {step.step_name}</h4>
                              <div className={`severity-badge ${severityLevel}`}>
                                Severity: {step.gap_severity}/5 - {severityText}
                              </div>
                            </div>
                            
                            <div className="step-content">
                              <div className="step-details">
                                <div className="persona-reaction">
                                  <h5>👤 Persona Reaction:</h5>
                                  <p>{step.persona_reaction}</p>
                                </div>
                                
                                <div className="quick-fixes">
                                  <h5>🔧 Quick Fixes:</h5>
                                  <ul>
                                    {step.quick_fixes.map((fix, fixIndex) => (
                                      <li key={fixIndex}>{fix}</li>
                                    ))}
                                  </ul>
                                </div>
                              </div>
                              
                              <div className="severity-indicator">
                                <h5>Gap Severity</h5>
                                <div className="severity-score">{step.gap_severity}/5</div>
                                <div className="severity-label">{severityText} Priority</div>
                              </div>
                            </div>
                          </div>
                        )
                      })}
                    </div>

                    <div className="journey-insights">
                      <h3>💡 Key Insights</h3>
                      
                      <div className="insights-grid">
                        <div className="insight-column">
                          <h4>🔴 Highest Friction Points:</h4>
                          {journey.steps.filter(step => step.gap_severity >= 3).map((step, index) => (
                            <div key={index} className="friction-point high">
                              <strong>{step.step_name}</strong> (Severity: {step.gap_severity}/5)
                            </div>
                          ))}
                          {journey.steps.filter(step => step.gap_severity >= 3).length === 0 && (
                            <div className="friction-point success">No high-friction points identified!</div>
                          )}
                        </div>
                        
                        <div className="insight-column">
                          <h4>🟢 Strongest Steps:</h4>
                          {journey.steps.filter(step => step.gap_severity <= 2).map((step, index) => (
                            <div key={index} className="friction-point low">
                              <strong>{step.step_name}</strong> (Severity: {step.gap_severity}/5)
                            </div>
                          ))}
                          {journey.steps.filter(step => step.gap_severity <= 2).length === 0 && (
                            <div className="friction-point warning">No particularly strong steps identified</div>
                          )}
                        </div>
                      </div>
                    </div>
                  </div>
                )}

                {activeTab === 'performance' && (
                  <div className="performance-tab">
                    <h2>📊 Performance Analytics</h2>
                    
                    <div className="performance-overview">
                      <h3>📈 Score Distribution</h3>
                      <PlotlyChart 
                        data={getScoreDistributionData()}
                        layout={{
                          title: 'Distribution of Page Scores',
                          xaxis: { title: 'Average Score' },
                          yaxis: { title: 'Number of Pages' },
                          height: 400
                        }}
                      />
                    </div>

                    <div className="performance-data">
                      <h3>📋 Raw Performance Data</h3>
                      <div className="data-table">
                        <table>
                          <thead>
                            <tr>
                              <th>Page</th>
                              <th>URL</th>
                              <th>Score</th>
                              <th>Tier</th>
                            </tr>
                          </thead>
                          <tbody>
                            {performance.map((page, index) => (
                              <tr key={index}>
                                <td>{page.title}</td>
                                <td>{page.url}</td>
                                <td>{page.avg_score.toFixed(1)}/10</td>
                                <td>{page.tier_name}</td>
                              </tr>
                            ))}
                          </tbody>
                        </table>
                      </div>
                    </div>
                  </div>
                )}

                {activeTab === 'voice' && (
                  <div className="voice-tab">
                    <h2>🗣️ Persona Voice Analysis</h2>
                    
                    <div className="voice-overview">
                      <h3>📊 Voice Data Overview</h3>
                      
                      <div className="voice-metrics">
                        {(() => {
                          const voiceStats = getVoiceStats()
                          return (
                            <>
                              <div className="voice-metric">
                                <h4>Effective Examples</h4>
                                <div className="metric-value">
                                  {voiceStats.effective_copy_examples?.populated || 0}/
                                  {voiceStats.effective_copy_examples?.total || 0}
                                </div>
                                <div className="metric-percentage">
                                  {(voiceStats.effective_copy_examples?.percentage || 0).toFixed(1)}%
                                </div>
                                <div className="metric-label">Pages with effective copy examples</div>
                              </div>
                              
                              <div className="voice-metric">
                                <h4>Issues Identified</h4>
                                <div className="metric-value">
                                  {voiceStats.ineffective_copy_examples?.populated || 0}/
                                  {voiceStats.ineffective_copy_examples?.total || 0}
                                </div>
                                <div className="metric-percentage">
                                  {(voiceStats.ineffective_copy_examples?.percentage || 0).toFixed(1)}%
                                </div>
                                <div className="metric-label">Pages with ineffective copy examples</div>
                              </div>
                              
                              <div className="voice-metric">
                                <h4>Strategic Analysis</h4>
                                <div className="metric-value">
                                  {voiceStats.business_impact_analysis?.populated || 0}/
                                  {voiceStats.business_impact_analysis?.total || 0}
                                </div>
                                <div className="metric-percentage">
                                  {(voiceStats.business_impact_analysis?.percentage || 0).toFixed(1)}%
                                </div>
                                <div className="metric-label">Pages with business impact analysis</div>
                              </div>
                            </>
                          )
                        })()}
                      </div>
                    </div>

                    <div className="voice-filters">
                      <h3>🎯 Voice Analysis Filters</h3>
                      
                      <div className="filter-controls">
                        <div className="tier-filter">
                          <label>🏷️ Filter by Content Tier:</label>
                          <div className="tier-checkboxes">
                            {[...new Set(performance.map(p => p.tier_name))].map(tier => (
                              <label key={tier} className="checkbox-label">
                                <input
                                  type="checkbox"
                                  checked={selectedTiers.includes(tier)}
                                  onChange={(e) => {
                                    if (e.target.checked) {
                                      setSelectedTiers([...selectedTiers, tier])
                                    } else {
                                      setSelectedTiers(selectedTiers.filter(t => t !== tier))
                                    }
                                  }}
                                />
                                {tier}
                              </label>
                            ))}
                          </div>
                        </div>
                        
                        <div className="tier-distribution">
                          <h4>Tier Distribution:</h4>
                          {[...new Set(performance.map(p => p.tier_name))].map(tier => {
                            const count = performance.filter(p => p.tier_name === tier).length
                            return (
                              <div key={tier} className="tier-count">
                                <strong>{tier}:</strong> {count} entries
                              </div>
                            )
                          })}
                        </div>
                      </div>
                    </div>

                    <div className="voice-analysis">
                      <h3>🔍 Voice Analysis Results</h3>
                      <div className="analysis-info">
                        📊 Analyzing {getFilteredPerformanceData().length} entries from {selectedTiers.length} tier(s)
                      </div>
                      
                      <div className="voice-examples">
                        {getFilteredPerformanceData()
                          .filter(p => p.effective_copy_examples || p.ineffective_copy_examples || p.business_impact_analysis)
                          .map((page, index) => (
                            <div key={index} className="voice-example">
                              <h4>{page.title}</h4>
                              <div className="example-content">
                                {page.effective_copy_examples && (
                                  <div className="effective-example">
                                    <h5>✅ Effective Copy:</h5>
                                    <p>{page.effective_copy_examples}</p>
                                  </div>
                                )}
                                {page.ineffective_copy_examples && (
                                  <div className="ineffective-example">
                                    <h5>❌ Areas for Improvement:</h5>
                                    <p>{page.ineffective_copy_examples}</p>
                                  </div>
                                )}
                                {page.business_impact_analysis && (
                                  <div className="business-impact">
                                    <h5>📈 Business Impact:</h5>
                                    <p>{page.business_impact_analysis}</p>
                                  </div>
                                )}
                              </div>
                            </div>
                          ))}
                      </div>
                    </div>
                  </div>
                )}
              </div>
            </div>
          </div>
        </>
      )}
    </div>
  )
}

export default PersonaViewer
