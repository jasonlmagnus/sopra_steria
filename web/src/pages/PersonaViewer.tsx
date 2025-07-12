import { useEffect, useState } from 'react'
import { PlotlyChart } from '../components/PlotlyChart'
import { EvidenceBrowser } from '../components/EvidenceDisplay'
import StandardCard from '../components/StandardCard'

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



const PERSONA_NAMES: Record<string, string> = {
  'P1': 'The Benelux Strategic Business Leader (C-Suite Executive)',
  'P2': 'The_BENELUX_Technology_Innovation_Leader',
  'P3': 'The Benelux Transformation Programme Leader',
  'P4': 'The Benelux Cybersecurity Decision Maker',
  'P5': 'The Technical Influencer'
}

// Utility function to parse markdown content into structured sections (matches Streamlit logic)
const parseMarkdownToSections = (content: string): ProfileSection[] => {
  if (!content) return []
  
  const sections: ProfileSection[] = []
  let currentSection: string | null = null
  let currentContent: string[] = []
  
  const lines = content.split('\n')
  
  for (const line of lines) {
    const lineStripped = line.trim()
    
    // Check if line is a section header (matches Streamlit logic)
    if (lineStripped && (
      lineStripped.match(/^[1-9]\.\s/) || // numbered sections
      lineStripped.startsWith('#') || // markdown headers
      (lineStripped.endsWith(':') && lineStripped.split(' ').length <= 5) // short lines ending with colon
    )) {
      // Save previous section
      if (currentSection && currentContent.length > 0) {
        sections.push({
          title: currentSection,
          content: currentContent.join('\n').trim(),
          subsections: [],
          isCollapsed: true
        })
      }
      
      // Start new section
      currentSection = lineStripped.replace(/^#+\s*/, '').replace(/:$/, '').trim()
      currentContent = []
    } else {
      if (lineStripped) { // Only add non-empty lines
        currentContent.push(line)
      }
    }
  }
  
  // Save last section
  if (currentSection && currentContent.length > 0) {
    sections.push({
      title: currentSection,
      content: currentContent.join('\n').trim(),
      subsections: [],
      isCollapsed: true
    })
  }
  
  return sections
}

// Format profile content for better display (matches Streamlit logic)
const formatProfileContent = (content: string): string => {
  const lines = content.split('\n')
  const formattedLines: string[] = []
  
  for (const line of lines) {
    const trimmedLine = line.trim()
    if (!trimmedLine) continue
    
    // Format key-value pairs
    if (trimmedLine.includes(':') && !trimmedLine.startsWith('http')) {
      const parts = trimmedLine.split(':', 2)
      if (parts.length === 2) {
        const key = parts[0].trim()
        const value = parts[1].trim()
        formattedLines.push(`**${key}:** ${value}`)
      } else {
        formattedLines.push(trimmedLine)
      }
    } else {
      formattedLines.push(trimmedLine)
    }
  }
  
  return formattedLines.join('\n\n')
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
    }
  }, [selectedPersona])

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
    const businessPopulated = filteredData.filter(item => item.business_impact_analysis && item.business_impact_analysis.trim().length > 0).length

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
      },
      business_impact_analysis: {
        populated: businessPopulated,
        total: total,
        percentage: total > 0 ? (businessPopulated / total) * 100 : 0
      }
    }
  }



  // Helper function to create friendly page titles
  const createFriendlyPageTitle = (_pageId: string, url: string): string => {
    // Always prioritize URL over page_id since page_id is often a meaningless hash
    if (url) {
      // Extract readable title from URL
      const cleanUrl = url.replace(/https?:\/\//, '').replace(/www\./, '')
      
      // Handle domain and path
      if (cleanUrl.includes('/')) {
        const domain = cleanUrl.split('/')[0]
        const path = cleanUrl.split('/').slice(1).join('/')
        
        // Create meaningful title from path
        if (path) {
          // Clean up path for readability
          const pathParts = path.split('/')
          const meaningfulParts: string[] = []
          
          for (const part of pathParts) {
            if (part && !['en', 'nl', 'be', 'com', 'www'].includes(part)) {
              // Convert dashes/underscores to spaces and capitalize
              const cleanPart = part.replace(/[-_]/g, ' ').replace(/\.(html|php|aspx?)$/, '')
              meaningfulParts.push(cleanPart.replace(/\b\w/g, l => l.toUpperCase()))
            }
          }
          
          if (meaningfulParts.length > 0) {
            return meaningfulParts.join(' > ')
          } else {
            // Fallback to domain
            return domain.replace(/\./g, ' ').replace(/[-_]/g, ' ').replace(/\b\w/g, l => l.toUpperCase())
          }
        } else {
          // Just domain
          return domain.replace(/\./g, ' ').replace(/[-_]/g, ' ').replace(/\b\w/g, l => l.toUpperCase())
        }
      } else {
        // Just domain
        return cleanUrl.replace(/\./g, ' ').replace(/[-_]/g, ' ').replace(/\b\w/g, l => l.toUpperCase())
      }
    }
    
    // Fallback if no URL
    return 'Website Page'
  }

  // Helper function to process voice examples into structured format
  const processVoiceExamples = (text: string) => {
    if (!text) return []
    
    const examples: { quote?: string; analysis: string; type: 'quoted_copy' | 'persona_insight' }[] = []
    const segments = text.split(' | ').map(seg => seg.trim()).filter(seg => seg.length > 0)
    
    for (const segment of segments) {
      // Check if this segment contains quoted copy
      const quotedCopy = segment.match(/"([^"]{10,})"/g)
      
      if (quotedCopy) {
        for (const quote of quotedCopy) {
          const cleanQuote = quote.replace(/"/g, '')
          // Extract analysis part (after the quote)
          const analysisParts = segment.split(quote)
          let analysis = ''
          if (analysisParts.length > 1) {
            analysis = analysisParts[1].trim()
            if (analysis.startsWith(':')) {
              analysis = analysis.substring(1).trim()
            }
          }
          
          examples.push({
            quote: cleanQuote,
            analysis: analysis || 'Analysis not available',
            type: 'quoted_copy'
          })
        }
      } else {
        // Pure analysis - show as persona insight
        examples.push({
          analysis: segment,
          type: 'persona_insight'
        })
      }
    }
    
    return examples
  }

  // Helper function to extract voice themes
  const getVoiceThemes = (): [string, number][] => {
    const themes: Record<string, string[]> = {
      'trust': ['trust', 'credibility', 'confidence', 'reliable'],
      'efficiency': ['efficiency', 'streamline', 'optimize', 'productivity'],
      'security': ['security', 'cybersecurity', 'risk', 'compliance'],
      'innovation': ['innovation', 'AI', 'digital', 'transformation'],
      'clarity': ['clear', 'clarity', 'understand', 'specific'],
      'value': ['value', 'ROI', 'benefit', 'outcome', 'result']
    }
    
    const themeCounts: Record<string, number> = {}
    const allVoiceData: string[] = []
    
    // Collect all voice data
    performance.forEach(page => {
      if (page.effective_copy_examples) allVoiceData.push(page.effective_copy_examples)
      if (page.ineffective_copy_examples) allVoiceData.push(page.ineffective_copy_examples)
      if (page.business_impact_analysis) allVoiceData.push(page.business_impact_analysis)
    })
    
    // Count theme occurrences
    Object.entries(themes).forEach(([themeName, keywords]) => {
      let count = 0
      allVoiceData.forEach(text => {
        const textLower = text.toLowerCase()
        keywords.forEach(keyword => {
          const regex = new RegExp(`\\b${keyword}\\b`, 'g')
          const matches = textLower.match(regex)
          if (matches) count += matches.length
        })
      })
      if (count > 0) {
        themeCounts[themeName] = count
      }
    })
    
    // Return sorted themes
    return Object.entries(themeCounts)
      .sort(([, a], [, b]) => b - a)
      .slice(0, 5)
  }

  // Helper function to get voice sentiment
  const getVoiceSentiment = () => {
    const positiveIndicators = ['good', 'excellent', 'strong', 'effective', 'clear', 'helpful', 'valuable', 'relevant']
    const negativeIndicators = ['poor', 'weak', 'unclear', 'confusing', 'generic', 'vague', 'missing', 'lacking']
    
    const allVoiceData: string[] = []
    
    // Collect all voice data
    performance.forEach(page => {
      if (page.effective_copy_examples) allVoiceData.push(page.effective_copy_examples)
      if (page.ineffective_copy_examples) allVoiceData.push(page.ineffective_copy_examples)
      if (page.business_impact_analysis) allVoiceData.push(page.business_impact_analysis)
    })
    
    let positiveCount = 0
    let negativeCount = 0
    
    allVoiceData.forEach(text => {
      const textLower = text.toLowerCase()
      
      positiveIndicators.forEach(indicator => {
        const regex = new RegExp(`\\b${indicator}\\b`, 'g')
        const matches = textLower.match(regex)
        if (matches) positiveCount += matches.length
      })
      
      negativeIndicators.forEach(indicator => {
        const regex = new RegExp(`\\b${indicator}\\b`, 'g')
        const matches = textLower.match(regex)
        if (matches) negativeCount += matches.length
      })
    })
    
    return {
      positive: positiveCount,
      negative: negativeCount
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
              
              <div className="grid grid--cols-3 gap-md">
                <StandardCard
                  title="Overall Score"
                  variant="metric"
                  status={calculateOverallScore() >= 8 ? "excellent" : calculateOverallScore() >= 6 ? "good" : "critical"}
                >
                  <div className="metric-value">{calculateOverallScore().toFixed(1)}/10</div>
                  <div className="metric-label">Average brand health score</div>
                </StandardCard>
                
                <StandardCard
                  title="Pages Analyzed"
                  variant="metric"
                  status="good"
                >
                  <div className="metric-value">{performance.length}</div>
                  <div className="metric-label">Website pages analyzed</div>
                </StandardCard>
                
                <StandardCard
                  title="Critical Issues"
                  variant="metric"
                  status={getCriticalIssuesCount() === 0 ? "excellent" : getCriticalIssuesCount() <= 2 ? "warning" : "critical"}
                >
                  <div className="metric-value">{getCriticalIssuesCount()}</div>
                  <div className="metric-label">Pages with scores &lt; 4.0</div>
                </StandardCard>
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
                            className="flex-between-center"
                          >
                            <h4>📋 {section.title}</h4>
                            <span className="collapse-icon">
                              {section.isCollapsed ? '▼' : '▲'}
                            </span>
                          </div>
                          {!section.isCollapsed && (
                            <div className="section-content">
                              <div 
                                dangerouslySetInnerHTML={{ 
                                  __html: formatProfileContent(section.content)
                                    .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
                                    .replace(/\n\n/g, '<br/><br/>')
                                    .replace(/\n/g, '<br/>')
                                }} 
                              />
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
                              <th>Sentiment</th>
                              <th>Actions</th>
                            </tr>
                          </thead>
                          <tbody>
                            {performance.map((page, index) => (
                              <tr key={index}>
                                <td>{createFriendlyPageTitle(page.page_id, page.url)}</td>
                                <td>
                                  <a href={page.url} target="_blank" rel="noopener noreferrer">
                                    {page.url.length > 50 ? `${page.url.substring(0, 50)}...` : page.url}
                                  </a>
                                </td>
                                <td>
                                  <span className={`score-badge ${
                                    page.avg_score >= 8 ? 'excellent' :
                                    page.avg_score >= 6 ? 'good' :
                                    page.avg_score >= 4 ? 'fair' : 'poor'
                                  }`}>
                                    {page.avg_score.toFixed(1)}/10
                                  </span>
                                </td>
                                <td>
                                  <span className="tier-badge">{page.tier_name}</span>
                                </td>
                                <td>{page.overall_sentiment || 'N/A'}</td>
                                <td>
                                  <div className="action-buttons">
                                    {page.avg_score < 4 && (
                                      <span className="badge badge--critical">Critical</span>
                                    )}
                                    {page.avg_score >= 8 && (
                                      <span className="badge badge--excellent">Success</span>
                                    )}
                                  </div>
                                </td>
                              </tr>
                            ))}
                          </tbody>
                        </table>
                      </div>
                      
                      <div className="performance-summary">
                        <h4>📊 Performance Summary</h4>
                        <div className="grid grid--cols-4 gap-sm">
                          <StandardCard
                            title="Total Pages"
                            variant="metric"
                            status="good"
                          >
                            <div className="metric-value">{performance.length}</div>
                          </StandardCard>
                          <StandardCard
                            title="Average Score"
                            variant="metric"
                            status={calculateOverallScore() >= 8 ? "excellent" : calculateOverallScore() >= 6 ? "good" : "critical"}
                          >
                            <div className="metric-value">{calculateOverallScore().toFixed(1)}/10</div>
                          </StandardCard>
                          <StandardCard
                            title="Critical Issues"
                            variant="metric"
                            status={getCriticalIssuesCount() === 0 ? "excellent" : getCriticalIssuesCount() <= 2 ? "warning" : "critical"}
                          >
                            <div className="metric-value">{getCriticalIssuesCount()}</div>
                          </StandardCard>
                          <StandardCard
                            title="Success Stories"
                            variant="metric"
                            status="excellent"
                          >
                            <div className="metric-value">{performance.filter(p => p.avg_score >= 8).length}</div>
                          </StandardCard>
                        </div>
                      </div>
                    </div>
                  </div>
                )}

                {activeTab === 'voice' && (
                  <div className="voice-tab">
                    <h2>🗣️ Advanced Persona Voice Analysis</h2>
                    
                    {performance.length > 0 ? (
                      <>
                        {/* Voice Data Overview */}
                        <div className="voice-overview">
                          <h3>📊 Voice Data Overview</h3>
                          
                          <div className="grid grid--cols-3 gap-md">
                            <StandardCard
                              title="Effective Examples"
                              variant="metric"
                              status="good"
                            >
                              <div className="metric-value">
                                {getVoiceStats().effective_copy_examples.populated}/
                                {getVoiceStats().effective_copy_examples.total}
                              </div>
                              <div className="metric-percentage">
                                {getVoiceStats().effective_copy_examples.percentage.toFixed(1)}%
                              </div>
                              <div className="metric-label">Pages with effective copy examples</div>
                            </StandardCard>
                            
                            <StandardCard
                              title="Issues Identified"
                              variant="metric"
                              status="warning"
                            >
                              <div className="metric-value">
                                {getVoiceStats().ineffective_copy_examples.populated}/
                                {getVoiceStats().ineffective_copy_examples.total}
                              </div>
                              <div className="metric-percentage">
                                {getVoiceStats().ineffective_copy_examples.percentage.toFixed(1)}%
                              </div>
                              <div className="metric-label">Pages with ineffective copy examples</div>
                            </StandardCard>
                            
                            <StandardCard
                              title="Strategic Analysis"
                              variant="metric"
                              status="excellent"
                            >
                              <div className="metric-value">
                                {getVoiceStats().business_impact_analysis.populated}/
                                {getVoiceStats().business_impact_analysis.total}
                              </div>
                              <div className="metric-percentage">
                                {getVoiceStats().business_impact_analysis.percentage.toFixed(1)}%
                              </div>
                              <div className="metric-label">Pages with business impact analysis</div>
                            </StandardCard>
                          </div>
                        </div>

                        {/* Voice Analysis Filters */}
                        <div className="voice-filters">
                          <h3>🎯 Voice Analysis Filters</h3>
                          
                          <div className="filter-row">
                            <div className="filter-control">
                              <label>🏷️ Filter by Content Tier:</label>
                              <div className="tier-selection">
                                {[...new Set(performance.map(p => p.tier_name))].map(tier => (
                                  <label key={tier} className="tier-checkbox">
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
                          
                          <div className="filter-info">
                            📊 Analyzing {getFilteredPerformanceData().length} entries from {selectedTiers.length} tier(s)
                          </div>
                        </div>

                        {/* Voice Patterns & Insights */}
                        <div className="voice-patterns">
                          <h3>🎯 Voice Patterns & Insights</h3>
                          
                          <div className="patterns-grid">
                            <div className="themes-analysis">
                              <h4>🏷️ Common Themes</h4>
                              <div className="themes-list">
                                {getVoiceThemes().map(([theme, count]) => (
                                  <div key={theme} className="theme-item">
                                    <span className="theme-name">{theme}</span>
                                    <span className="theme-count">{count}</span>
                                  </div>
                                ))}
                              </div>
                            </div>
                            
                            <div className="sentiment-analysis">
                              <h4>📈 Voice Sentiment</h4>
                              <div className="grid grid--cols-2 gap-md">
                                <StandardCard
                                  title="Positive Signals"
                                  variant="metric"
                                  status="excellent"
                                >
                                  <div className="metric-value">{getVoiceSentiment().positive}</div>
                                </StandardCard>
                                <StandardCard
                                  title="Concern Signals"
                                  variant="metric"
                                  status="warning"
                                >
                                  <div className="metric-value">{getVoiceSentiment().negative}</div>
                                </StandardCard>
                              </div>
                            </div>
                          </div>
                        </div>

                        {/* Copy-Ready Quotes */}
                        <div className="copy-ready-quotes">
                          <h3>📋 Copy-Ready Persona Quotes</h3>
                          <p><em>Ready-to-use persona voice quotes for presentations and reports</em></p>
                          
                          <div className="quote-controls">
                            <select 
                              value={selectedQuoteType} 
                              onChange={(e) => setSelectedQuoteType(e.target.value)}
                              className="quote-type-selector"
                            >
                              <option value="positive">✅ Positive Reactions</option>
                              <option value="negative">❌ Critical Feedback</option>
                              <option value="strategic">🎯 Strategic Insights</option>
                            </select>
                          </div>
                          
                          <div className="quotes-list">
                            {selectedQuoteType === 'positive' && 
                              performance
                                .filter(page => page.effective_copy_examples)
                                .slice(0, 3)
                                .map((page, index) => {
                                  const examples = processVoiceExamples(page.effective_copy_examples || '')
                                  const quote = examples.find(ex => ex.quote)?.quote || examples[0]?.analysis
                                  
                                  return quote ? (
                                    <div key={index} className="quote-item positive">
                                      <p><strong>Quote #{index + 1}:</strong></p>
                                      <p>"{quote}"</p>
                                      <button 
                                        onClick={() => navigator.clipboard.writeText(quote)}
                                        className="copy-button"
                                      >
                                        📋 Copy Quote
                                      </button>
                                    </div>
                                  ) : null
                                })
                            }
                            
                            {selectedQuoteType === 'negative' && 
                              performance
                                .filter(page => page.ineffective_copy_examples)
                                .slice(0, 3)
                                .map((page, index) => {
                                  const examples = processVoiceExamples(page.ineffective_copy_examples || '')
                                  const quote = examples.find(ex => ex.quote)?.quote || examples[0]?.analysis
                                  
                                  return quote ? (
                                    <div key={index} className="quote-item negative">
                                      <p><strong>Quote #{index + 1}:</strong></p>
                                      <p>"{quote}"</p>
                                      <button 
                                        onClick={() => navigator.clipboard.writeText(quote)}
                                        className="copy-button"
                                      >
                                        📋 Copy Quote
                                      </button>
                                    </div>
                                  ) : null
                                })
                            }
                            
                            {selectedQuoteType === 'strategic' && 
                              performance
                                .filter(page => page.business_impact_analysis)
                                .slice(0, 3)
                                .map((page, index) => {
                                  const segments = page.business_impact_analysis?.split(' | ')
                                    .map(seg => seg.trim())
                                    .filter(seg => seg.length > 30) || []
                                  const quote = segments[0]
                                  
                                  return quote ? (
                                    <div key={index} className="quote-item strategic">
                                      <p><strong>Quote #{index + 1}:</strong></p>
                                      <p>"{quote}"</p>
                                      <button 
                                        onClick={() => navigator.clipboard.writeText(quote)}
                                        className="copy-button"
                                      >
                                        📋 Copy Quote
                                      </button>
                                    </div>
                                  ) : null
                                })
                            }
                          </div>
                        </div>

                        {/* What's Working Well - Effective Copy Examples */}
                        <div className="voice-analysis-section">
                          <h3>✅ What's Working Well</h3>
                          <p><em>Persona reactions to effective copy and messaging</em></p>
                          
                          <div className="voice-search">
                            <input
                              type="text"
                              placeholder="🔍 Search effective examples..."
                              value={searchTerm}
                              onChange={(e) => setSearchTerm(e.target.value)}
                              className="search-input"
                            />
                          </div>
                          
                          {performance.length > 0 && (
                            <div className="voice-examples-display">
                              {performance
                                .filter(page => 
                                  page.effective_copy_examples && 
                                  page.effective_copy_examples.trim().length > 10 &&
                                  (searchTerm === '' || 
                                   page.title?.toLowerCase().includes(searchTerm.toLowerCase()) ||
                                   page.effective_copy_examples.toLowerCase().includes(searchTerm.toLowerCase()))
                                )
                                .slice(0, 5)
                                .map((page, pageIndex) => {
                                  const pageTitle = createFriendlyPageTitle(page.page_id, page.url)
                                  const examples = processVoiceExamples(page.effective_copy_examples || '')
                                  
                                  return (
                                    <div key={pageIndex} className="voice-page-section">
                                      <h5>✅ {pageTitle} ({page.tier_name})</h5>
                                      <div className="page-meta">
                                        <span className="score-badge">{page.avg_score.toFixed(1)}/10</span>
                                      </div>
                                      
                                      {examples.map((example, exIndex) => (
                                        <div key={exIndex} className="voice-example effective">
                                          {example.quote ? (
                                            <div className="example-with-quote">
                                              <div className="example-quote">📝 Copy Example: "{example.quote}"</div>
                                              <div className="example-analysis">💬 Persona Analysis: {example.analysis}</div>
                                            </div>
                                          ) : (
                                            <div className="example-insight">
                                              <div className="example-analysis">💬 Persona Insight: {example.analysis}</div>
                                            </div>
                                          )}
                                        </div>
                                      ))}
                                    </div>
                                  )
                                })}
                            </div>
                          )}
                        </div>

                        {/* What's Not Working - Ineffective Copy Examples */}
                        <div className="voice-analysis-section">
                          <h3>❌ What's Not Working</h3>
                          <p><em>Persona feedback on problematic copy and messaging</em></p>
                          
                          <div className="voice-search">
                            <input
                              type="text"
                              placeholder="🔍 Search issues..."
                              value={searchTermIssues}
                              onChange={(e) => setSearchTermIssues(e.target.value)}
                              className="search-input"
                            />
                          </div>
                          
                          {performance.length > 0 && (
                            <div className="voice-examples-display">
                              {performance
                                .filter(page => 
                                  page.ineffective_copy_examples && 
                                  page.ineffective_copy_examples.trim().length > 10 &&
                                  (searchTermIssues === '' || 
                                   page.title?.toLowerCase().includes(searchTermIssues.toLowerCase()) ||
                                   page.ineffective_copy_examples.toLowerCase().includes(searchTermIssues.toLowerCase()))
                                )
                                .slice(0, 5)
                                .map((page, pageIndex) => {
                                  const pageTitle = createFriendlyPageTitle(page.page_id, page.url)
                                  const examples = processVoiceExamples(page.ineffective_copy_examples || '')
                                  
                                  return (
                                    <div key={pageIndex} className="voice-page-section">
                                      <h5>❌ {pageTitle} ({page.tier_name})</h5>
                                      <div className="page-meta">
                                        <span className="score-badge">{page.avg_score.toFixed(1)}/10</span>
                                      </div>
                                      
                                      {examples.map((example, exIndex) => (
                                        <div key={exIndex} className="voice-example ineffective">
                                          {example.quote ? (
                                            <div className="example-with-quote">
                                              <div className="example-quote">📝 Problematic Copy: "{example.quote}"</div>
                                              <div className="example-analysis">💬 Persona Analysis: {example.analysis}</div>
                                            </div>
                                          ) : (
                                            <div className="example-insight">
                                              <div className="example-analysis">💬 Persona Concern: {example.analysis}</div>
                                            </div>
                                          )}
                                        </div>
                                      ))}
                                    </div>
                                  )
                                })}
                            </div>
                          )}
                        </div>

                        {/* Strategic Business Impact */}
                        <div className="voice-analysis-section">
                          <h3>💼 Strategic Business Impact</h3>
                          <p><em>High-level persona analysis and recommendations</em></p>
                          
                          {performance.length > 0 && (
                            <div className="business-impact-display">
                              {performance
                                .filter(page => 
                                  page.business_impact_analysis && 
                                  page.business_impact_analysis.trim().length > 5
                                )
                                .slice(0, 5)
                                .map((page, pageIndex) => {
                                  const pageTitle = createFriendlyPageTitle(page.page_id, page.url)
                                  const segments = page.business_impact_analysis?.split(' | ')
                                    .map(seg => seg.trim())
                                    .filter(seg => seg.length > 0) || []
                                  
                                  return (
                                    <div key={pageIndex} className="business-page-section">
                                      <h5>💼 {pageTitle} ({page.tier_name})</h5>
                                      <div className="page-meta">
                                        <span className="score-badge">{page.avg_score.toFixed(1)}/10</span>
                                      </div>
                                      
                                      {segments.map((segment, segIndex) => (
                                        <div key={segIndex} className="business-insight">
                                          <div className="insight-content">💼 Strategic Insight: {segment}</div>
                                        </div>
                                      ))}
                                    </div>
                                  )
                                })}
                            </div>
                          )}
                        </div>

                      </>
                    ) : (
                      <div className="voice-fallback">
                        <p>📝 No voice analysis data available for this persona</p>
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
                        <div className="evidence-overview">
                          <h3>📊 Evidence Analysis Overview</h3>
                          <p>Detailed audit evidence and AI analysis for <strong>{profile?.name}</strong></p>
                          
                          <div className="evidence-stats">
                            <div className="stat-item">
                              <strong>Total Evidence Items:</strong> {auditData.filter(row => {
                                const personaName = PERSONA_NAMES[selectedPersona] || selectedPersona
                                return row.persona_id === personaName || row.persona_id === selectedPersona
                              }).length}
                            </div>
                            <div className="stat-item">
                              <strong>Pages Analyzed:</strong> {[...new Set(auditData.filter(row => {
                                const personaName = PERSONA_NAMES[selectedPersona] || selectedPersona
                                return row.persona_id === personaName || row.persona_id === selectedPersona
                              }).map(row => row.page_id))].length}
                            </div>
                          </div>
                        </div>
                        
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
                        <h3>📊 Evidence Analysis</h3>
                        <p>No audit data available for <strong>{profile?.name}</strong></p>
                        <p>Please ensure the audit has been run and data is available.</p>
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
