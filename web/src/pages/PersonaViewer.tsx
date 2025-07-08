import { useEffect, useState } from 'react'
import { PlotlyChart } from '../components/PlotlyChart'
import { EvidenceDisplay, EvidenceBrowser } from '../components/EvidenceDisplay'

interface PersonaProfile {
  id: string
  name: string
  content: string
  sections: ProfileSection[]
}

interface ProfileSection {
  title: string
  content: string
  subsections?: ProfileSection[]
  isCollapsed?: boolean
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
  evidence?: string
  trust_credibility_assessment?: string
  information_gaps?: string
  raw_score?: number
  url_slug?: string
}

interface VoiceStats {
  effective_copy_examples?: {
    populated: number
    total: number
    percentage: number
  }
  ineffective_copy_examples?: {
    populated: number
    total: number
    percentage: number
  }
}

const PERSONA_NAMES: Record<string, string> = {
  'P1': 'The Benelux Strategic Business Leader (C-Suite Executive)',
  'P2': 'The BENELUX Technology Innovation Leader',
  'P3': 'The Benelux Transformation Programme Leader',
  'P4': 'The Benelux Cybersecurity Decision Maker',
  'P5': 'The Technical Influencer'
}

// Utility function to parse markdown content into structured sections
const parseMarkdownToSections = (content: string): ProfileSection[] => {
  const lines = content.split('\n')
  const sections: ProfileSection[] = []
  let currentSection: ProfileSection | null = null
  let currentContent: string[] = []

  for (const line of lines) {
    const trimmedLine = line.trim()
    
    // Check if this is a main section header (number followed by period)
    const mainSectionMatch = trimmedLine.match(/^(\d+)\.\s+(.+)$/)
    if (mainSectionMatch) {
      // Save previous section if exists
      if (currentSection) {
        currentSection.content = currentContent.join('\n').trim()
        sections.push(currentSection)
      }
      
      // Start new section
      currentSection = {
        title: mainSectionMatch[2],
        content: '',
        subsections: [],
        isCollapsed: true
      }
      currentContent = []
    } else if (currentSection) {
      currentContent.push(line)
    }
  }
  
  // Add the last section
  if (currentSection) {
    currentSection.content = currentContent.join('\n').trim()
    sections.push(currentSection)
  }
  
  return sections
}

// Utility function to extract persona name from content
const extractPersonaName = (content: string): string => {
  const lines = content.trim().split('\n')
  if (lines.length > 0) {
    const firstLine = lines[0].trim()
    if (firstLine.startsWith('Persona Brief:')) {
      return firstLine.replace('Persona Brief:', '').trim()
    }
  }
  return 'Unknown Persona'
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
  const [auditData, setAuditData] = useState<any[]>([])

  useEffect(() => {
    fetchPersonas()
    fetchAuditData()
  }, [])

  useEffect(() => {
    if (selectedPersona) {
      fetchPersonaData(selectedPersona)
    }
  }, [selectedPersona])

  const fetchPersonas = async () => {
    try {
      setLoading(true)
      // Get available personas from the API
      const response = await fetch('http://localhost:3000/api/personas')
      if (response.ok) {
        const data = await response.json()
        const personaIds = data.personas || ['P1', 'P2', 'P3', 'P4', 'P5']
        setPersonas(personaIds)
        if (personaIds.length > 0) {
          setSelectedPersona(personaIds[0])
        }
      } else {
        // Fallback to mock data
        const mockPersonas = ['P1', 'P2', 'P3', 'P4', 'P5']
        setPersonas(mockPersonas)
        if (mockPersonas.length > 0) {
          setSelectedPersona(mockPersonas[0])
        }
      }
    } catch (err) {
      // Fallback to mock data
      const mockPersonas = ['P1', 'P2', 'P3', 'P4', 'P5']
      setPersonas(mockPersonas)
      if (mockPersonas.length > 0) {
        setSelectedPersona(mockPersonas[0])
      }
    } finally {
      setLoading(false)
    }
  }

  const fetchAuditData = async () => {
    try {
      // Fetch audit data with evidence for this persona
      const response = await fetch('http://localhost:8000/api/audit-data')
      if (response.ok) {
        const data = await response.json()
        setAuditData(data)
      }
    } catch (err) {
      console.error('Failed to fetch audit data:', err)
      // Set empty array as fallback
      setAuditData([])
    }
  }

  const fetchPersonaData = async (personaId: string) => {
    try {
      setLoading(true)
      
      // Try to fetch real persona data from markdown files
      const personaResponse = await fetch(`http://localhost:3000/api/persona/${personaId}`)
      let personaProfile: PersonaProfile
      
      if (personaResponse.ok) {
        const personaData = await personaResponse.json()
        const sections = parseMarkdownToSections(personaData.content)
        const extractedName = extractPersonaName(personaData.content)
        
        personaProfile = {
          id: personaId,
          name: extractedName,
          content: sections.length > 0 ? sections[0].content.substring(0, 300) + '...' : 'No content available',
          sections: sections
        }
      } else {
        // Fallback to mock data
        personaProfile = {
          id: personaId,
          name: PERSONA_NAMES[personaId] || `Business Professional ${personaId}`,
          content: generateMockProfileContent(personaId),
          sections: generateMockProfileSections(personaId)
        }
      }
      
      // Mock journey data (would be replaced with real data)
      const mockJourney: JourneyData = {
        steps: generateMockJourneySteps(personaId),
        persona_id: personaId,
        persona_name: personaProfile.name
      }
      
      // Mock performance data (would be replaced with real data)
      const mockPerformance: PerformanceData[] = generateMockPerformanceData(personaId)
      
      setProfile(personaProfile)
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

  const toggleSection = (sectionIndex: number) => {
    if (profile) {
      const updatedSections = [...profile.sections]
      updatedSections[sectionIndex].isCollapsed = !updatedSections[sectionIndex].isCollapsed
      setProfile({
        ...profile,
        sections: updatedSections
      })
    }
  }

  const generateMockProfileContent = (personaId: string) => {
    const profiles: Record<string, string> = {
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
        content: `Primary decision maker for ${personaId === 'P1' ? 'strategic business initiatives' : personaId === 'P2' ? 'technology innovation' : personaId === 'P3' ? 'transformation programmes' : personaId === 'P4' ? 'cybersecurity strategy' : 'technical architecture'}. Manages budget allocation and vendor relationships.`,
        isCollapsed: true
      },
      {
        title: 'Key Priorities',
        content: `Focuses on ${personaId === 'P1' ? 'business growth and competitive advantage' : personaId === 'P2' ? 'innovation and digital transformation' : personaId === 'P3' ? 'change management and stakeholder alignment' : personaId === 'P4' ? 'risk management and compliance' : 'technical excellence and solution architecture'}.`,
        isCollapsed: true
      },
      {
        title: 'Pain Points',
        content: `Challenges include ${personaId === 'P1' ? 'proving ROI and managing stakeholder expectations' : personaId === 'P2' ? 'balancing innovation with practical implementation' : personaId === 'P3' ? 'managing resistance to change' : personaId === 'P4' ? 'staying ahead of emerging threats' : 'evaluating vendor capabilities and technical fit'}.`,
        isCollapsed: true
      },
      {
        title: 'Success Metrics',
        content: `Measured by ${personaId === 'P1' ? 'revenue growth and operational efficiency' : personaId === 'P2' ? 'successful technology implementations' : personaId === 'P3' ? 'transformation programme success rates' : personaId === 'P4' ? 'security incident reduction' : 'technical solution performance and adoption'}.`,
        isCollapsed: true
      }
    ]
  }

  const generateMockJourneySteps = (_personaId: string): JourneyStep[] => {
    const baseSteps = [
      { name: 'Problem Recognition', reaction: 'Identifies business challenge or opportunity', severity: 2 },
      { name: 'Research & Discovery', reaction: 'Researches potential solutions and vendors', severity: 3 },
      { name: 'Stakeholder Alignment', reaction: 'Builds consensus among key stakeholders', severity: 4 },
      { name: 'Solution Evaluation', reaction: 'Evaluates technical and business fit', severity: 3 },
      { name: 'Vendor Selection', reaction: 'Selects preferred vendor and solution', severity: 2 },
      { name: 'Implementation Planning', reaction: 'Plans deployment and change management', severity: 3 },
      { name: 'Execution & Monitoring', reaction: 'Oversees implementation and tracks progress', severity: 2 }
    ]

    return baseSteps.map((step, index) => ({
      step_number: index + 1,
      step_name: step.name,
      persona_reaction: step.reaction,
      gap_severity: step.severity,
      quick_fixes: [
        'Improve content clarity and relevance',
        'Provide better supporting evidence',
        'Enhance user experience and navigation'
      ]
    }))
  }

  const generateMockPerformanceData = (_personaId: string): PerformanceData[] => {
    const mockPages = [
      { title: 'Homepage', url: 'https://example.com/', score: 7.5, tier: 'Tier 1' },
      { title: 'Services', url: 'https://example.com/services', score: 6.8, tier: 'Tier 1' },
      { title: 'About Us', url: 'https://example.com/about', score: 8.2, tier: 'Tier 2' },
      { title: 'Contact', url: 'https://example.com/contact', score: 5.9, tier: 'Tier 2' },
      { title: 'Case Studies', url: 'https://example.com/cases', score: 7.1, tier: 'Tier 3' }
    ]

    return mockPages.map((page, index) => ({
      page_id: `page_${index + 1}`,
      url: page.url,
      title: page.title,
      avg_score: page.score,
      tier_name: page.tier,
      effective_copy_examples: 'Strong value proposition and clear call-to-action',
      ineffective_copy_examples: 'Technical jargon that may confuse users',
      business_impact_analysis: 'High potential for conversion improvement'
    }))
  }

  const calculateOverallScore = () => {
    if (performance.length === 0) return 0
    return performance.reduce((sum, item) => sum + item.avg_score, 0) / performance.length
  }

  const getCriticalIssuesCount = () => {
    return performance.filter(item => item.avg_score < 4.0).length
  }

  const getAverageGapSeverity = () => {
    if (!journey || journey.steps.length === 0) return 0
    return journey.steps.reduce((sum, step) => sum + step.gap_severity, 0) / journey.steps.length
  }

  const getFilteredPerformanceData = () => {
    return performance.filter(item => selectedTiers.includes(item.tier_name))
  }

  const getVoiceStats = () => {
    const filteredData = getFilteredPerformanceData()
    const total = filteredData.length
    const effectivePopulated = filteredData.filter(item => item.effective_copy_examples && item.effective_copy_examples.trim().length > 0).length
    const ineffectivePopulated = filteredData.filter(item => item.ineffective_copy_examples && item.ineffective_copy_examples.trim().length > 0).length

    return {
      effective_copy_examples: {
        populated: effectivePopulated,
        total: total,
        percentage: total > 0 ? (effectivePopulated / total) * 100 : 0
      },
      ineffective_copy_examples: {
        populated: ineffectivePopulated,
        total: total,
        percentage: total > 0 ? (ineffectivePopulated / total) * 100 : 0
      }
    }
  }

  const getScoreDistributionData = () => {
    const scores = performance.map(item => item.avg_score)
    return [{
      x: scores,
      type: 'histogram',
      nbinsx: 10,
      marker: { color: '#3B82F6' }
    }]
  }

  const getJourneyFlowData = () => {
    if (!journey) return []
    
    return [{
      x: journey.steps.map(step => step.step_number),
      y: journey.steps.map(step => step.gap_severity),
      type: 'scatter',
      mode: 'lines+markers',
      name: 'Gap Severity',
      line: { color: '#EF4444', width: 3 },
      marker: { size: 8, color: '#EF4444' }
    }]
  }

  const getJourneyFlowLayout = () => {
    return {
      title: 'Journey Step Gap Analysis',
      xaxis: { 
        title: 'Journey Step',
        tickmode: 'array',
        tickvals: journey?.steps.map(step => step.step_number) || [],
        ticktext: journey?.steps.map(step => step.step_name.substring(0, 15) + '...') || []
      },
      yaxis: { title: 'Gap Severity (1-5)', range: [0, 5] },
      height: 400
    }
  }

  if (loading) {
    return (
      <div className="page-container">
        <div className="main-header">
          <h1>👤 Persona Viewer</h1>
          <p>Loading persona data...</p>
        </div>
      </div>
    )
  }

  if (error) {
    return (
      <div className="page-container">
        <div className="main-header">
          <h1>👤 Persona Viewer</h1>
          <p>Error: {error}</p>
        </div>
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
                <button 
                  className={`tab-button ${activeTab === 'evidence' ? 'active' : ''}`}
                  onClick={() => setActiveTab('evidence')}
                >
                  🔍 Evidence
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
                          <div 
                            className="section-header"
                            onClick={() => toggleSection(index)}
                            style={{ cursor: 'pointer', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}
                          >
                            <h4>📋 {section.title}</h4>
                            <span className="collapse-icon">
                              {section.isCollapsed ? '▼' : '▲'}
                            </span>
                          </div>
                          {!section.isCollapsed && (
                            <div className="section-content">
                              <pre style={{ whiteSpace: 'pre-wrap', fontFamily: 'inherit' }}>
                                {section.content}
                              </pre>
                            </div>
                          )}
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
                            </>
                          )
                        })()}
                      </div>
                    </div>

                    <div className="voice-examples">
                      <h3>📝 Voice Examples</h3>
                      
                      <div className="voice-examples-grid">
                        <div className="voice-examples-column">
                          <h4>✅ Effective Copy Examples</h4>
                          {performance.filter(page => page.effective_copy_examples).map((page, index) => (
                            <div key={index} className="voice-example effective">
                              <h5>{page.title}</h5>
                              <p>{page.effective_copy_examples}</p>
                            </div>
                          ))}
                        </div>
                        
                        <div className="voice-examples-column">
                          <h4>❌ Ineffective Copy Examples</h4>
                          {performance.filter(page => page.ineffective_copy_examples).map((page, index) => (
                            <div key={index} className="voice-example ineffective">
                              <h5>{page.title}</h5>
                              <p>{page.ineffective_copy_examples}</p>
                            </div>
                          ))}
                        </div>
                      </div>
                    </div>
                  </div>
                )}

                {activeTab === 'evidence' && (
                  <div className="evidence-tab">
                    <h2>🔍 Evidence & Analysis</h2>
                    
                    <div className="evidence-overview">
                      <p>Detailed audit evidence and AI analysis for <strong>{profile?.name}</strong></p>
                    </div>

                    {auditData.length > 0 ? (
                      <div className="evidence-browser">
                        <EvidenceBrowser
                          data={auditData.filter(row => {
                            const personaName = PERSONA_NAMES[selectedPersona] || selectedPersona
                            return row.persona_id === personaName || row.persona_id === selectedPersona
                          })}
                          evidenceColumns={[
                            'evidence',
                            'effective_copy_examples',
                            'ineffective_copy_examples',
                            'trust_credibility_assessment',
                            'business_impact_analysis',
                            'information_gaps'
                          ]}
                        />
                      </div>
                    ) : (
                      <div className="no-evidence">
                        <h3>📊 Sample Evidence Display</h3>
                        <p>Audit data is being loaded. Here's how evidence will be displayed:</p>
                        
                        <div className="sample-evidence">
                          <EvidenceDisplay
                            evidence={[
                              {
                                type: 'evidence',
                                content: 'The homepage clearly positions Sopra Steria as a major European tech player with expertise in consulting, digital services, AI, and cybersecurity. However, the messaging is somewhat generic and lacks explicit emphasis on cybersecurity leadership critical to this persona.',
                                title: 'AI Analysis'
                              },
                              {
                                type: 'effective_copy',
                                content: 'Cybersecurity listed explicitly as a service offering alongside Consulting, Artificial Intelligence, and Technology Services signals recognition of cybersecurity as a core capability.',
                                title: 'Effective Copy Examples'
                              },
                              {
                                type: 'ineffective_copy',
                                content: 'The world is how we shape it - This slogan is generic and abstract; it does not communicate any specific value or differentiator related to cybersecurity, compliance, or risk management.',
                                title: 'Areas for Improvement'
                              },
                              {
                                type: 'trust_assessment',
                                content: 'The site includes corporate governance, financial reports, ethics and compliance, and data protection notices, which are positive trust signals. However, there are no explicit cybersecurity certifications visible.',
                                title: 'Trust & Credibility Assessment'
                              }
                            ]}
                            title="Sample Evidence Analysis"
                            defaultExpanded={true}
                          />
                        </div>
                      </div>
                    )}
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
