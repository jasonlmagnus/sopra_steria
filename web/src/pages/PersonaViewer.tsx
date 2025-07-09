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
  first_impression?: string
  language_tone_feedback?: string
  overall_sentiment?: string

  conversion_likelihood?: string
  raw_score?: number
  url_slug?: string
}

interface VoiceStats {
  total_entries: number
  effective_copy_examples: {
    populated: number
    total: number
    percentage: number
  }
  ineffective_copy_examples: {
    populated: number
    total: number
    percentage: number
  }
  business_impact_analysis: {
    populated: number
    total: number
    percentage: number
  }
}

interface VoiceExample {
  type: 'quoted_copy' | 'persona_insight'
  quote: string
  analysis: string
}

interface VoiceAnalysisPage {
  page_title: string
  url: string
  tier_name: string
  avg_score: number
  examples: VoiceExample[]
}

interface BusinessInsight {
  type: 'strategic_insight'
  content: string
}

interface BusinessAnalysisPage {
  page_title: string
  url: string
  tier_name: string
  avg_score: number
  insights: BusinessInsight[]
}

interface VoicePatterns {
  themes: Record<string, number>
  sentiment: {
    positive: number
    negative: number
  }
}

interface CopyReadyQuotes {
  positive: string[]
  negative: string[]
  strategic: string[]
}

interface AdvancedVoiceAnalysis {
  persona_id: string
  persona_name: string
  voice_stats: VoiceStats
  effective_analysis: {
    pages: VoiceAnalysisPage[]
    total_examples: number
  }
  ineffective_analysis: {
    pages: VoiceAnalysisPage[]
    total_examples: number
  }
  business_impact: {
    pages: BusinessAnalysisPage[]
    total_insights: number
  }
  voice_patterns: VoicePatterns
  copy_ready_quotes: CopyReadyQuotes
  analysis_type: string
  tier_filter?: string
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
  const [advancedVoiceAnalysis, setAdvancedVoiceAnalysis] = useState<AdvancedVoiceAnalysis | null>(null)
  const [voiceAnalysisLoading, setVoiceAnalysisLoading] = useState(false)
  const [searchTerm, setSearchTerm] = useState('')
  const [searchTermIssues, setSearchTermIssues] = useState('')
  const [selectedQuoteType, setSelectedQuoteType] = useState('positive')

  useEffect(() => {
    fetchPersonas()
    fetchAuditData()
  }, [])

  useEffect(() => {
    if (selectedPersona) {
      fetchPersonaData(selectedPersona)
      fetchAdvancedVoiceAnalysis()
    }
  }, [selectedPersona])

  useEffect(() => {
    if (selectedPersona) {
      fetchAdvancedVoiceAnalysis()
    }
  }, [selectedTiers])

  const fetchPersonas = async () => {
    try {
      setLoading(true)
      // Get available personas from the API
      const response = await fetch('http://localhost:3000/api/personas')
      if (response.ok) {
        const data = await response.json()
        const personaIds = data.personas || []
        setPersonas(personaIds)
        if (personaIds.length > 0) {
          setSelectedPersona(personaIds[0])
        }
      } else {
        setError('Failed to load personas')
      }
    } catch (err) {
      setError('Failed to load personas')
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
        setError('Failed to load persona profile')
        return
      }

      // Load journey data
      let journeyData: JourneyData | null = null
      try {
        const journeyRes = await fetch(`http://localhost:3000/api/persona-journeys/${personaId}`)
        if (journeyRes.ok) {
          const j = await journeyRes.json()
          journeyData = { ...j, persona_id: personaId, persona_name: personaProfile.name }
        }
      } catch (journeyErr) {
        console.error('Failed to load persona journey', journeyErr)
      }

      // Load performance data
      let performanceData: PerformanceData[] = []
      try {
        const perfRes = await fetch('http://localhost:3000/api/persona-insights')
        if (perfRes.ok) {
          const perfJson = await perfRes.json()
          const personaItem = (perfJson.personas || []).find((p: any) => p.persona_id === personaId)
          if (personaItem) performanceData = personaItem.pages
        }
      } catch (perfErr) {
        console.error('Failed to load performance data', perfErr)
      }

      setProfile(personaProfile)
      if (journeyData) setJourney(journeyData)
      setPerformance(performanceData)

      // Initialize tier selection
      const availableTiers = [...new Set(performanceData.map(p => p.tier_name))]
      setSelectedTiers(availableTiers)
      
    } catch (err) {
      setError('Failed to load persona data')
    } finally {
      setLoading(false)
    }
  }

  const fetchAdvancedVoiceAnalysis = async () => {
    if (!selectedPersona) return
    
    setVoiceAnalysisLoading(true)
    try {
      const tierFilter = selectedTiers.length > 0 ? selectedTiers.join(',') : undefined
      const params = new URLSearchParams({
        analysis_type: 'comprehensive'
      })
      
      if (tierFilter) {
        params.append('tier_filter', tierFilter)
      }
      
      const response = await fetch(`http://localhost:8000/api/persona/${selectedPersona}/voice-analysis?${params}`)
      if (!response.ok) {
        throw new Error('Failed to fetch voice analysis')
      }
      
      const analysis = await response.json()
      setAdvancedVoiceAnalysis(analysis)
    } catch (error) {
      console.error('Error fetching advanced voice analysis:', error)
    } finally {
      setVoiceAnalysisLoading(false)
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
                    <h2>🗣️ Advanced Persona Voice Analysis</h2>
                    
                    {voiceAnalysisLoading ? (
                      <div className="loading-state">
                        <p>🔄 Loading advanced voice analysis...</p>
                      </div>
                    ) : advancedVoiceAnalysis ? (
                      <>
                        {/* Voice Data Overview */}
                        <div className="voice-overview">
                          <h3>📊 Voice Data Overview</h3>
                          
                          <div className="voice-metrics">
                            <div className="voice-metric">
                              <h4>Effective Examples</h4>
                              <div className="metric-value">
                                {advancedVoiceAnalysis.voice_stats.effective_copy_examples.populated}/
                                {advancedVoiceAnalysis.voice_stats.effective_copy_examples.total}
                              </div>
                              <div className="metric-percentage">
                                {advancedVoiceAnalysis.voice_stats.effective_copy_examples.percentage.toFixed(1)}%
                              </div>
                              <div className="metric-label">Pages with effective copy examples</div>
                            </div>
                            
                            <div className="voice-metric">
                              <h4>Issues Identified</h4>
                              <div className="metric-value">
                                {advancedVoiceAnalysis.voice_stats.ineffective_copy_examples.populated}/
                                {advancedVoiceAnalysis.voice_stats.ineffective_copy_examples.total}
                              </div>
                              <div className="metric-percentage">
                                {advancedVoiceAnalysis.voice_stats.ineffective_copy_examples.percentage.toFixed(1)}%
                              </div>
                              <div className="metric-label">Pages with ineffective copy examples</div>
                            </div>
                            
                            <div className="voice-metric">
                              <h4>Business Impact</h4>
                              <div className="metric-value">
                                {advancedVoiceAnalysis.voice_stats.business_impact_analysis.populated}/
                                {advancedVoiceAnalysis.voice_stats.business_impact_analysis.total}
                              </div>
                              <div className="metric-percentage">
                                {advancedVoiceAnalysis.voice_stats.business_impact_analysis.percentage.toFixed(1)}%
                              </div>
                              <div className="metric-label">Pages with business impact analysis</div>
                            </div>
                          </div>
                        </div>

                        {/* Voice Patterns & Themes */}
                        <div className="voice-patterns">
                          <h3>🎯 Voice Patterns & Themes</h3>
                          
                          <div className="patterns-grid">
                            <div className="themes-analysis">
                              <h4>🔍 Key Themes</h4>
                              <div className="themes-list">
                                {Object.entries(advancedVoiceAnalysis.voice_patterns.themes).map(([theme, count]) => (
                                  <div key={theme} className="theme-item">
                                    <span className="theme-name">{theme}</span>
                                    <span className="theme-count">{count}</span>
                                  </div>
                                ))}
                              </div>
                            </div>
                            
                            <div className="sentiment-analysis">
                              <h4>💭 Sentiment Analysis</h4>
                              <div className="sentiment-metrics">
                                <div className="sentiment-item positive">
                                  <span className="sentiment-label">Positive Indicators</span>
                                  <span className="sentiment-count">{advancedVoiceAnalysis.voice_patterns.sentiment.positive}</span>
                                </div>
                                <div className="sentiment-item negative">
                                  <span className="sentiment-label">Negative Indicators</span>
                                  <span className="sentiment-count">{advancedVoiceAnalysis.voice_patterns.sentiment.negative}</span>
                                </div>
                              </div>
                            </div>
                          </div>
                        </div>

                        {/* Copy-Ready Quotes */}
                        <div className="copy-ready-quotes">
                          <h3>📝 Copy-Ready Persona Quotes</h3>
                          
                          <div className="quote-controls">
                            <select 
                              value={selectedQuoteType} 
                              onChange={(e) => setSelectedQuoteType(e.target.value)}
                              className="quote-type-selector"
                            >
                              <option value="positive">✅ Positive Quotes</option>
                              <option value="negative">❌ Negative Quotes</option>
                              <option value="strategic">🎯 Strategic Quotes</option>
                            </select>
                          </div>
                          
                          <div className="quotes-list">
                            {advancedVoiceAnalysis.copy_ready_quotes[selectedQuoteType as keyof CopyReadyQuotes].map((quote, index) => (
                              <div key={index} className={`quote-item ${selectedQuoteType}`}>
                                <p>"{quote}"</p>
                                <button 
                                  onClick={() => navigator.clipboard.writeText(quote)}
                                  className="copy-button"
                                >
                                  📋 Copy
                                </button>
                              </div>
                            ))}
                          </div>
                        </div>

                        {/* Advanced Voice Examples */}
                        <div className="advanced-voice-examples">
                          <h3>📝 Advanced Voice Examples</h3>
                          
                          <div className="voice-search">
                            <input
                              type="text"
                              placeholder="Search effective examples..."
                              value={searchTerm}
                              onChange={(e) => setSearchTerm(e.target.value)}
                              className="search-input"
                            />
                          </div>
                          
                          <div className="voice-examples-grid">
                            <div className="voice-examples-column">
                              <h4>✅ Effective Copy Examples ({advancedVoiceAnalysis.effective_analysis.total_examples})</h4>
                              {advancedVoiceAnalysis.effective_analysis.pages
                                .filter(page => 
                                  searchTerm === '' || 
                                  page.page_title.toLowerCase().includes(searchTerm.toLowerCase()) ||
                                  page.examples.some(ex => 
                                    ex.quote.toLowerCase().includes(searchTerm.toLowerCase()) ||
                                    ex.analysis.toLowerCase().includes(searchTerm.toLowerCase())
                                  )
                                )
                                .map((page, pageIndex) => (
                                <div key={pageIndex} className="voice-page-section">
                                  <h5>{page.page_title}</h5>
                                  <div className="page-meta">
                                    <span className="tier-badge">{page.tier_name}</span>
                                    <span className="score-badge">{page.avg_score.toFixed(1)}/10</span>
                                  </div>
                                  {page.examples.map((example, exIndex) => (
                                    <div key={exIndex} className={`voice-example ${example.type}`}>
                                      {example.quote && (
                                        <div className="example-quote">"{example.quote}"</div>
                                      )}
                                      <div className="example-analysis">{example.analysis}</div>
                                    </div>
                                  ))}
                                </div>
                              ))}
                            </div>
                            
                            <div className="voice-examples-column">
                              <h4>❌ Ineffective Copy Examples ({advancedVoiceAnalysis.ineffective_analysis.total_examples})</h4>
                              
                              <div className="voice-search">
                                <input
                                  type="text"
                                  placeholder="Search ineffective examples..."
                                  value={searchTermIssues}
                                  onChange={(e) => setSearchTermIssues(e.target.value)}
                                  className="search-input"
                                />
                              </div>
                              
                              {advancedVoiceAnalysis.ineffective_analysis.pages
                                .filter(page => 
                                  searchTermIssues === '' || 
                                  page.page_title.toLowerCase().includes(searchTermIssues.toLowerCase()) ||
                                  page.examples.some(ex => 
                                    ex.quote.toLowerCase().includes(searchTermIssues.toLowerCase()) ||
                                    ex.analysis.toLowerCase().includes(searchTermIssues.toLowerCase())
                                  )
                                )
                                .map((page, pageIndex) => (
                                <div key={pageIndex} className="voice-page-section">
                                  <h5>{page.page_title}</h5>
                                  <div className="page-meta">
                                    <span className="tier-badge">{page.tier_name}</span>
                                    <span className="score-badge">{page.avg_score.toFixed(1)}/10</span>
                                  </div>
                                  {page.examples.map((example, exIndex) => (
                                    <div key={exIndex} className={`voice-example ${example.type}`}>
                                      {example.quote && (
                                        <div className="example-quote">"{example.quote}"</div>
                                      )}
                                      <div className="example-analysis">{example.analysis}</div>
                                    </div>
                                  ))}
                                </div>
                              ))}
                            </div>
                          </div>
                        </div>

                        {/* Business Impact Analysis */}
                        <div className="business-impact-analysis">
                          <h3>📊 Strategic Business Impact Analysis</h3>
                          
                          <div className="business-insights">
                            <div className="insights-header">
                              <h4>🎯 Strategic Insights ({advancedVoiceAnalysis.business_impact.total_insights})</h4>
                            </div>
                            
                            {advancedVoiceAnalysis.business_impact.pages.map((page, pageIndex) => (
                              <div key={pageIndex} className="business-page-section">
                                <h5>{page.page_title}</h5>
                                <div className="page-meta">
                                  <span className="tier-badge">{page.tier_name}</span>
                                  <span className="score-badge">{page.avg_score.toFixed(1)}/10</span>
                                </div>
                                {page.insights.map((insight, insightIndex) => (
                                  <div key={insightIndex} className="business-insight">
                                    <div className="insight-content">{insight.content}</div>
                                  </div>
                                ))}
                              </div>
                            ))}
                          </div>
                        </div>
                      </>
                    ) : (
                      <div className="voice-fallback">
                        <p>🔄 Click to load advanced voice analysis...</p>
                        <button onClick={fetchAdvancedVoiceAnalysis} className="load-button">
                          Load Advanced Analysis
                        </button>
                      </div>
                    )}
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
                            'first_impression',
                            'language_tone_feedback',
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
                                type: 'first_impression',
                                content: 'The site feels corporate and professional but does not immediately communicate cybersecurity leadership or specialized expertise. The layout is clear but lacks security-specific messaging that would immediately resonate with a CISO.',
                                title: 'First Impression'
                              },
                              {
                                type: 'language_tone_feedback',
                                content: 'The tone is professional and corporate but somewhat generic. For cybersecurity executives, the language should be more precise, technical, and focused on risk management and compliance frameworks.',
                                title: 'Language & Tone Analysis'
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
                              },
                              {
                                type: 'business_impact',
                                content: 'The content addresses digital transformation broadly but lacks specific business impact metrics or KPIs that would help cybersecurity executives justify investment in security initiatives.',
                                title: 'Business Impact Analysis'
                              },
                              {
                                type: 'information_gaps',
                                content: 'Missing: specific compliance frameworks (DORA, NIS2, GDPR), cybersecurity certifications, case studies with quantifiable security outcomes, and regulatory expertise demonstrations.',
                                title: 'Information Gaps'
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
