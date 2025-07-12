import { useEffect, useState } from 'react'
import { useQuery } from '@tanstack/react-query';
import { PlotlyChart, StandardCard, Banner, DataTable, BarChart, EvidenceBrowser, PageContainer } from '../components'
import type { ColumnDef } from '@tanstack/react-table'
import { useFilters } from '../hooks/useFilters';
import { FilterSystem } from '../components/FilterSystem';
import type { FilterConfig } from '../types/filters';

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

const personaViewerFilters: FilterConfig[] = [
  { name: 'persona', label: 'Select Persona', type: 'select', defaultValue: '' },
  { name: 'tiers', label: 'Filter by Content Tier', type: 'multiselect', defaultValue: [] },
];

function PersonaViewer() {
  const { filters, setFilter } = useFilters();
  const [activeTab, setActiveTab] = useState('profile');

  // Fetch available personas for the dropdown
  const { data: personasData } = useQuery({
    queryKey: ['personas'],
    queryFn: async () => {
      const res = await fetch('http://localhost:3000/api/personas');
      if (!res.ok) throw new Error('Failed to load personas');
      const data = await res.json();
      // Set the first persona as default when the list loads
      if (data.personas && data.personas.length > 0 && !filters.persona) {
        setFilter('persona', data.personas[0]);
      }
      return data.personas || [];
    },
  });

  // Fetch all data for the selected persona
  const { data, isLoading, error } = useQuery({
    queryKey: ['persona-viewer', filters.persona, filters.tiers],
    queryFn: async () => {
      if (!filters.persona) return null;
      const params = new URLSearchParams({ tiers: filters.tiers.join(',') });
      const res = await fetch(`http://localhost:3000/api/persona-viewer/${filters.persona}?${params.toString()}`);
      if (!res.ok) throw new Error('Failed to load persona data');
      return res.json();
    },
    enabled: !!filters.persona, // Only fetch when a persona is selected
  });

  const { profile, journey, performance, audit } = (data || {}) as {
    profile: PersonaProfile | null;
    journey: JourneyData | null;
    performance: PerformanceData[] | null;
    audit: any[] | null;
  };

  const journeySteps = journey?.steps || [];
  const performanceData = performance || [];
  const auditData = audit || [];

  // Create dynamic options for the filter system
  const dynamicFilterData = {
    personaOptions: (personasData || []).map((p: string) => ({ value: p, label: PERSONA_NAMES[p] || p })),
    tiersOptions: performanceData ? [...new Set(performanceData.map((p: PerformanceData) => p.tier_name))].map(t => ({ value: t, label: t })) : [],
  };
  
  // Initialize tier selection
  useEffect(() => {
    if (performanceData) {
      const availableTiers = [...new Set(performanceData.map((p: PerformanceData) => p.tier_name))]
      setFilter('tiers', availableTiers)
    }
  }, [performanceData, setFilter])

  // Initialize persona selection
  useEffect(() => {
    if (personasData && personasData.length > 0 && !filters.persona) {
      setFilter('persona', personasData[0])
    }
  }, [personasData, filters.persona])

  // Initialize active tab
  useEffect(() => {
    setActiveTab('profile')
  }, [])

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
    performanceData?.forEach(page => {
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
    performanceData?.forEach(page => {
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
    const scores = performanceData?.map(item => item.avg_score) || []
    return {
      x: scores,
      y: Array.from({ length: scores.length }, (_, i) => i + 1),
    }
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

  if (isLoading) {
    return (
      <PageContainer title="👤 Persona Viewer">
        <p className="text--body">Loading persona data...</p>
      </PageContainer>
    )
  }

  if (error) {
    return (
      <PageContainer title="👤 Persona Viewer">
        <p className="text--body">Error: {error.message}</p>
      </PageContainer>
    )
  }

  if (!profile) {
    return (
      <PageContainer title="👤 Persona Viewer">
        <p className="text--body">No persona data available for the selected persona.</p>
      </PageContainer>
    )
  }

  return (
    <PageContainer title="👤 Persona Viewer">
      <FilterSystem config={personaViewerFilters} data={dynamicFilterData} />
      {/* Header */}
      <p className="text--body">In-depth persona analysis with voice profiling and content alignment insights</p>

      {/* Persona Selection */}
      <div className="container--section">
        <h2 className="heading--section">🎯 Select Persona for Analysis</h2>
        
        <div className="persona--content">
          <div className="container--layout">
            <select 
              value={filters.persona} 
              onChange={(e) => setFilter('persona', e.target.value)}
              className="select--form"
            >
              {personasData?.map((persona: string) => (
                <option key={persona} value={persona}>
                  {persona} - {PERSONA_NAMES[persona] || 'Business Professional'}
                </option>
              ))}
            </select>
            <div className="persona--content">
              <span className="text--display">📊 <strong>{personasData?.length || 0}</strong> personas available for analysis</span>
            </div>
          </div>
        </div>
      </div>

      {profile && (
        <>
          {/* Persona Overview */}
          <div className="container--section">
            <div className="persona--content">
              <div className="container--card">
                <h3 className="heading--card">{profile.name}</h3>
                <p className="text--body"><strong>ID:</strong> {filters.persona}</p>
              </div>
              
              <div className="container--layout">
                <StandardCard
                  title="Overall Score"
                  variant="metric"
                  status={((performanceData.reduce((sum: number, item: PerformanceData) => sum + item.avg_score, 0) || 0) / (performanceData.length || 1)) >= 8 ? "excellent" : ((performanceData.reduce((sum: number, item: PerformanceData) => sum + item.avg_score, 0) || 0) / (performanceData.length || 1)) >= 6 ? "good" : "critical"}
                >
                  <div className="text--display">{(performanceData.reduce((sum, item: PerformanceData) => sum + item.avg_score, 0) || 0) / (performanceData.length || 1) || 0}/10</div>
                  <div className="text--body">Average brand health score</div>
                </StandardCard>
                
                <StandardCard
                  title="Pages Analyzed"
                  variant="metric"
                  status="good"
                >
                  <div className="text--display">{(performanceData.length || 0)}</div>
                  <div className="text--body">Website pages analyzed</div>
                </StandardCard>
                
                <StandardCard
                  title="Critical Issues"
                  variant="metric"
                  status={(performanceData.filter((p: PerformanceData) => p.avg_score < 4.0).length || 0) === 0 ? "excellent" : (performanceData.filter((p: PerformanceData) => p.avg_score < 4.0).length || 0) <= 2 ? "warning" : "critical"}
                >
                  <div className="text--display">{(performanceData.filter((p: PerformanceData) => p.avg_score < 4.0).length || 0)}</div>
                  <div className="text--body">Pages with scores &lt; 4.0</div>
                </StandardCard>
              </div>
            </div>
          </div>

          {/* Navigation Tabs */}
          <div className="container--section">
            <div className="tabs">
                <button 
                  className={`tabs__button ${activeTab === 'profile' ? 'tabs__button--active' : ''}`}
                  onClick={() => setActiveTab('profile')}
                >
                  📋 Profile
                </button>
                <button 
                  className={`tabs__button ${activeTab === 'journey' ? 'tabs__button--active' : ''}`}
                  onClick={() => setActiveTab('journey')}
                >
                  🗺️ Journey
                </button>
                <button 
                  className={`tabs__button ${activeTab === 'performance' ? 'tabs__button--active' : ''}`}
                  onClick={() => setActiveTab('performance')}
                >
                  📊 Performance
                </button>
                <button 
                  className={`tabs__button ${activeTab === 'voice' ? 'tabs__button--active' : ''}`}
                  onClick={() => setActiveTab('voice')}
                >
                  🗣️ Voice
                </button>
                <button 
                  className={`tabs__button ${activeTab === 'evidence' ? 'tabs__button--active' : ''}`}
                  onClick={() => setActiveTab('evidence')}
                >
                  🔍 Evidence
                </button>

              <div className="tab--interface">
                {activeTab === 'profile' && (
                  <div className="tab--interface">
                    <h2 className="heading--section">🎯 Persona Profile</h2>
                    
                    <div className="container--content">
                      <div className="container--content">
                        <h3 className="heading--subsection">Overview</h3>
                        <p className="text--body">{profile.content}</p>
                      </div>
                    </div>

                    <div className="container--content">
                      {profile.sections.map((section, index) => (
                        <div key={index} className="container--card">
                          <div 
                            className="container--layout"
                            onClick={() => {
                              if(profile?.sections) {
                                  const updatedSections = [...profile.sections];
                                  updatedSections[index].isCollapsed = !updatedSections[index].isCollapsed;
                                  // This is a local UI state change, so it's ok to not use the filter context.
                                  // A more robust solution might involve a local reducer.
                              }
                            }}
                          >
                            <h4 className="heading--card">📋 {section.title}</h4>
                            <span className="collapse-icon">
                              {profile?.sections?.[index]?.isCollapsed ? '▼' : '▲'}
                            </span>
                          </div>
                          {!profile?.sections?.[index]?.isCollapsed && (
                            <div className="container--content">
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
                  <div className="tab--interface">
                    <h2 className="heading--section">🗺️ Journey Analysis</h2>
                    
                    <div className="journey--flow">
                      <div className="journey--flow">
                        <p className="text--body"><strong>Analyzing journey for:</strong> {profile?.name}</p>
                      </div>
                      
                      <div className="container--section">
                        <h4 className="heading--card">Avg Gap Severity</h4>
                        <div className="text--display">{journeySteps.reduce((sum: number, step: JourneyStep) => sum + step.gap_severity, 0) / (journeySteps.length || 1) || 0}/5</div>
                        <div className="text--body">Average friction across all steps</div>
                      </div>
                    </div>

                    <div className="journey--flow">
                      <h3 className="heading--subsection">📊 Journey Flow & Gap Analysis</h3>
                      <PlotlyChart 
                        data={getJourneyFlowData()}
                        layout={getJourneyFlowLayout()}
                      />
                    </div>

                    <div className="journey--flow">
                      <h3 className="heading--subsection">🔍 Step-by-Step Analysis</h3>
                      
                      {journey.steps.map((step, index) => {
                        const severityLevel = step.gap_severity <= 2 ? 'low' : step.gap_severity <= 3 ? 'medium' : 'high'
                        const severityText = step.gap_severity <= 2 ? 'Low' : step.gap_severity <= 3 ? 'Medium' : 'High'
                        
                        return (
                          <div key={index} className={`journey-step ${severityLevel}`}>
                            <div className="journey--flow">
                              <h4>📍 {step.step_name}</h4>
                              <div className={`severity-badge ${severityLevel}`}>
                                Severity: {step.gap_severity}/5 - {severityText}
                              </div>
                            </div>
                            
                            <div className="container--content">
                              <div className="journey--flow">
                                <div className="persona--content">
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

                    <div className="journey--flow">
                      <h3 className="heading--subsection">💡 Key Insights</h3>
                      
                      <div className="container--grid">
                        <div className="insight-column">
                          <h4>🔴 Highest Friction Points:</h4>
                          {journey.steps.filter(step => step.gap_severity >= 3).map((step, index) => (
                            <div key={index} className="friction-point badge--status">
                              <strong>{step.step_name}</strong> (Severity: {step.gap_severity}/5)
                            </div>
                          ))}
                          {journey.steps.filter(step => step.gap_severity >= 3).length === 0 && (
                            <Banner message="No high-friction points identified!" />
                          )}
                        </div>
                        
                        <div className="insight-column">
                          <h4>🟢 Strongest Steps:</h4>
                          {journey.steps.filter(step => step.gap_severity <= 2).map((step, index) => (
                            <div key={index} className="friction-point badge--status">
                              <strong>{step.step_name}</strong> (Severity: {step.gap_severity}/5)
                            </div>
                          ))}
                          {journey.steps.filter(step => step.gap_severity <= 2).length === 0 && (
                            <Banner message="No particularly strong steps identified" />
                          )}
                        </div>
                      </div>
                    </div>
                  </div>
                )}

                {activeTab === 'performance' && (
                  <div className="tab--interface">
                    <h2 className="heading--section">📊 Performance Analytics</h2>
                    
                    <div className="performance-overview">
                      <h3 className="heading--subsection">📈 Score Distribution</h3>
                      <BarChart 
                        x={getScoreDistributionData().x}
                        y={getScoreDistributionData().y}
                        title="Distribution of Page Scores"
                      />
                    </div>

                    <div className="performance-data">
                      <h3 className="heading--subsection">📋 Raw Performance Data</h3>
                      <DataTable columns={columns} data={performanceData} />
                      
                      <div className="performance-summary">
                        <h4 className="heading--subsection">📊 Performance Summary</h4>
                        <div className="container--grid container--grid spacing--sm">
                          <StandardCard
                            title="Total Pages"
                            variant="metric"
                            status="good"
                          >
                            <div className="text--display">{(performanceData.length || 0)}</div>
                          </StandardCard>
                          <StandardCard
                            title="Average Score"
                            variant="metric"
                            status={((performanceData.reduce((sum: number, item: PerformanceData) => sum + item.avg_score, 0) || 0) / (performanceData.length || 1)) >= 8 ? "excellent" : ((performanceData.reduce((sum: number, item: PerformanceData) => sum + item.avg_score, 0) || 0) / (performanceData.length || 1)) >= 6 ? "good" : "critical"}
                          >
                            <div className="text--display">{(performanceData.reduce((sum, item: PerformanceData) => sum + item.avg_score, 0) || 0) / (performanceData.length || 1) || 0}/10</div>
                          </StandardCard>
                          <StandardCard
                            title="Critical Issues"
                            variant="metric"
                            status={(performanceData.filter((p: PerformanceData) => p.avg_score < 4.0).length || 0) === 0 ? "excellent" : (performanceData.filter((p: PerformanceData) => p.avg_score < 4.0).length || 0) <= 2 ? "warning" : "critical"}
                          >
                            <div className="text--display">{(performanceData.filter((p: PerformanceData) => p.avg_score < 4.0).length || 0)}</div>
                          </StandardCard>
                          <StandardCard
                            title="Success Stories"
                            variant="metric"
                            status="excellent"
                          >
                            <div className="text--display">{(performanceData.filter((p: PerformanceData) => p.avg_score >= 8).length || 0)}</div>
                          </StandardCard>
                        </div>
                      </div>
                    </div>
                  </div>
                )}

                {activeTab === 'voice' && (
                  <div className="tab--interface">
                    <h2 className="heading--section">🗣️ Advanced Persona Voice Analysis</h2>
                    
                    {performanceData?.length > 0 ? (
                      <>
                        {/* Voice Data Overview */}
                        <div className="voice--analysis">
                          <h3 className="heading--subsection">📊 Voice Data Overview</h3>
                          
                          <div className="container--grid container--grid spacing--sm">
                            <StandardCard
                              title="Effective Examples"
                              variant="metric"
                              status="good"
                            >
                              <div className="text--display">
                                {(
                                (performanceData.filter((item: PerformanceData) => item.effective_copy_examples && item.effective_copy_examples.trim().length > 0).length || 0) /
                                (performanceData.length || 1) * 100
                                ).toFixed(1)}%
                              </div>
                              <div className="text--display">Pages with effective copy examples</div>
                            </StandardCard>
                            
                            <StandardCard
                              title="Issues Identified"
                              variant="metric"
                              status="warning"
                            >
                              <div className="text--display">
                                {(
                                (performanceData.filter((item: PerformanceData) => item.ineffective_copy_examples && item.ineffective_copy_examples.trim().length > 0).length || 0) /
                                (performanceData.length || 1) * 100
                                ).toFixed(1)}%
                              </div>
                              <div className="text--display">Pages with ineffective copy examples</div>
                            </StandardCard>
                            
                            <StandardCard
                              title="Strategic Analysis"
                              variant="metric"
                              status="excellent"
                            >
                              <div className="text--display">
                                {(
                                (performanceData.filter((item: PerformanceData) => item.business_impact_analysis && item.business_impact_analysis.trim().length > 0).length || 0) /
                                (performanceData.length || 1) * 100
                                ).toFixed(1)}%
                              </div>
                              <div className="text--display">Pages with business impact analysis</div>
                            </StandardCard>
                          </div>
                        </div>

                        {/* Voice Analysis Filters */}
                        <div className="filter--controls">
                          <h3 className="heading--subsection">🎯 Voice Analysis Filters</h3>
                          
                          <div className="filter--controls">
                            <div className="filter--controls">
                              <label>🏷️ Filter by Content Tier:</label>
                              <div className="tier-selection">
                                {[...new Set(performanceData?.map((p: PerformanceData) => p.tier_name))].map(tier => (
                                  <label key={tier} className="tier-checkbox">
                                    <input
                                      type="checkbox"
                                      checked={filters.tiers?.includes(tier)}
                                      onChange={(e) => {
                                        if (e.target.checked) {
                                          setFilter('tiers', [...(filters.tiers || []), tier])
                                        } else {
                                          setFilter('tiers', (filters.tiers || []).filter((t: string) => t !== tier))
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
                              {[...new Set(performanceData?.map((p: PerformanceData) => p.tier_name))].map(tier => {
                                const count = performanceData?.filter((p: PerformanceData) => p.tier_name === tier).length || 0
                                return (
                                  <div key={tier} className="tier-count">
                                    <strong>{tier}:</strong> {count} entries
                                  </div>
                                )
                              })}
                            </div>
                          </div>
                          
                          <div className="filter--controls">
                            📊 Analyzing {performanceData?.filter((item: PerformanceData) => filters.tiers?.includes(item.tier_name)).length || 0} entries from {filters.tiers?.length || 0} tier(s)
                          </div>
                        </div>

                        {/* Voice Patterns & Insights */}
                        <div className="voice--analysis">
                          <h3 className="heading--subsection">🎯 Voice Patterns & Insights</h3>
                          
                          <div className="container--grid">
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
                              <div className="container--grid container--grid spacing--sm">
                                <StandardCard
                                  title="Positive Signals"
                                  variant="metric"
                                  status="excellent"
                                >
                                  <div className="text--display">{getVoiceSentiment().positive}</div>
                                </StandardCard>
                                <StandardCard
                                  title="Concern Signals"
                                  variant="metric"
                                  status="warning"
                                >
                                  <div className="text--display">{getVoiceSentiment().negative}</div>
                                </StandardCard>
                              </div>
                            </div>
                          </div>
                        </div>

                        {/* Copy-Ready Quotes */}
                        <div className="voice--analysis">
                          <h3 className="heading--subsection">📋 Copy-Ready Persona Quotes</h3>
                          <p className="text--body"><em>Ready-to-use persona voice quotes for presentations and reports</em></p>
                          
                          <div className="voice--analysis">
                            <select 
                              value={filters.quoteType} 
                              onChange={(e) => setFilter('quoteType', e.target.value)}
                              className="quote-type-selector"
                            >
                              <option value="positive">✅ Positive Reactions</option>
                              <option value="negative">❌ Critical Feedback</option>
                              <option value="strategic">🎯 Strategic Insights</option>
                            </select>
                          </div>
                          
                          <div className="voice--analysis">
                            {filters.quoteType === 'positive' && 
                              performanceData
                                ?.filter((page: PerformanceData) => page.effective_copy_examples)
                                .slice(0, 3)
                                .map((page: PerformanceData, index) => {
                                  const examples = processVoiceExamples(page.effective_copy_examples || '')
                                  const quote = examples.find(ex => ex.quote)?.quote || examples[0]?.analysis
                                  
                                  return quote ? (
                                    <div key={index} className="voice--analysis badge--status">
                                      <p><strong>Quote #{index + 1}:</strong></p>
                                      <p>"{quote}"</p>
                                      <button 
                                        onClick={() => navigator.clipboard.writeText(quote)}
                                        className="button button--secondary button--sm"
                                      >
                                        📋 Copy Quote
                                      </button>
                                    </div>
                                  ) : null
                                })
                            }
                            
                            {filters.quoteType === 'negative' && 
                              performanceData
                                ?.filter((page: PerformanceData) => page.ineffective_copy_examples)
                                .slice(0, 3)
                                .map((page: PerformanceData, index) => {
                                  const examples = processVoiceExamples(page.ineffective_copy_examples || '')
                                  const quote = examples.find(ex => ex.quote)?.quote || examples[0]?.analysis
                                  
                                  return quote ? (
                                    <div key={index} className="voice--analysis badge--status">
                                      <p><strong>Quote #{index + 1}:</strong></p>
                                      <p>"{quote}"</p>
                                      <button 
                                        onClick={() => navigator.clipboard.writeText(quote)}
                                        className="button button--secondary button--sm"
                                      >
                                        📋 Copy Quote
                                      </button>
                                    </div>
                                  ) : null
                                })
                            }
                            
                            {filters.quoteType === 'strategic' && 
                              performanceData
                                ?.filter((page: PerformanceData) => page.business_impact_analysis)
                                .slice(0, 3)
                                .map((page: PerformanceData, index) => {
                                  const segments = page.business_impact_analysis?.split(' | ')
                                    .map(seg => seg.trim())
                                    .filter(seg => seg.length > 30) || []
                                  const quote = segments[0]
                                  
                                  return quote ? (
                                    <div key={index} className="voice--analysis badge--status">
                                      <p><strong>Quote #{index + 1}:</strong></p>
                                      <p>"{quote}"</p>
                                      <button 
                                        onClick={() => navigator.clipboard.writeText(quote)}
                                        className="button button--secondary button--sm"
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
                        <div className="voice--analysis">
                          <h3 className="heading--subsection">✅ What's Working Well</h3>
                          <p className="text--body"><em>Persona reactions to effective copy and messaging</em></p>
                          
                          <div className="voice--analysis">
                            <input
                              type="text"
                              placeholder="🔍 Search effective examples..."
                              value={filters.searchTerm || ''}
                              onChange={(e) => setFilter('searchTerm', e.target.value)}
                              className="search-input"
                            />
                          </div>
                          
                          {performanceData?.length > 0 && (
                            <div className="voice--analysis">
                              {performanceData
                                ?.filter((page: PerformanceData) => 
                                  page.effective_copy_examples && 
                                  page.effective_copy_examples.trim().length > 10 &&
                                  (filters.searchTerm === '' || 
                                   page.title?.toLowerCase().includes(filters.searchTerm.toLowerCase()) ||
                                   page.effective_copy_examples.toLowerCase().includes(filters.searchTerm.toLowerCase()))
                                )
                                .slice(0, 5)
                                .map((page: PerformanceData, pageIndex) => {
                                  const pageTitle = createFriendlyPageTitle(page.page_id, page.url)
                                  const examples = processVoiceExamples(page.effective_copy_examples || '')
                                  
                                  return (
                                    <div key={pageIndex} className="voice--analysis">
                                      <h5>✅ {pageTitle} ({page.tier_name})</h5>
                                      <div className="page-meta">
                                        <span className="badge badge--primary">{page.avg_score.toFixed(1)}/10</span>
                                      </div>
                                      
                                      {examples.map((example, exIndex) => (
                                        <div key={exIndex} className="voice--analysis badge--status">
                                          {example.quote ? (
                                            <div className="voice--analysis">
                                              <div className="voice--analysis">📝 Copy Example: "{example.quote}"</div>
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
                        <div className="voice--analysis">
                          <h3 className="heading--subsection">❌ What's Not Working</h3>
                          <p className="text--body"><em>Persona feedback on problematic copy and messaging</em></p>
                          
                          <div className="voice--analysis">
                            <input
                              type="text"
                              placeholder="🔍 Search issues..."
                              value={filters.searchTermIssues || ''}
                              onChange={(e) => setFilter('searchTermIssues', e.target.value)}
                              className="search-input"
                            />
                          </div>
                          
                          {performanceData?.length > 0 && (
                            <div className="voice--analysis">
                              {performanceData
                                ?.filter((page: PerformanceData) => 
                                  page.ineffective_copy_examples && 
                                  page.ineffective_copy_examples.trim().length > 10 &&
                                  (filters.searchTermIssues === '' || 
                                   page.title?.toLowerCase().includes(filters.searchTermIssues.toLowerCase()) ||
                                   page.ineffective_copy_examples.toLowerCase().includes(filters.searchTermIssues.toLowerCase()))
                                )
                                .slice(0, 5)
                                .map((page: PerformanceData, pageIndex) => {
                                  const pageTitle = createFriendlyPageTitle(page.page_id, page.url)
                                  const examples = processVoiceExamples(page.ineffective_copy_examples || '')
                                  
                                  return (
                                    <div key={pageIndex} className="voice--analysis">
                                      <h5>❌ {pageTitle} ({page.tier_name})</h5>
                                      <div className="page-meta">
                                        <span className="badge badge--primary">{page.avg_score.toFixed(1)}/10</span>
                                      </div>
                                      
                                      {examples.map((example, exIndex) => (
                                        <div key={exIndex} className="voice--analysis badge--status">
                                          {example.quote ? (
                                            <div className="voice--analysis">
                                              <div className="voice--analysis">📝 Problematic Copy: "{example.quote}"</div>
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
                        <div className="voice--analysis">
                          <h3 className="heading--subsection">💼 Strategic Business Impact</h3>
                          <p className="text--body"><em>High-level persona analysis and recommendations</em></p>
                          
                          {performanceData?.length > 0 && (
                            <div className="container--misc">
                              {performanceData
                                ?.filter((page: PerformanceData) => 
                                  page.business_impact_analysis && 
                                  page.business_impact_analysis.trim().length > 5
                                )
                                .slice(0, 5)
                                .map((page: PerformanceData, pageIndex) => {
                                  const pageTitle = createFriendlyPageTitle(page.page_id, page.url)
                                  const segments = page.business_impact_analysis?.split(' | ')
                                    .map(seg => seg.trim())
                                    .filter(seg => seg.length > 0) || []
                                  
                                  return (
                                    <div key={pageIndex} className="container--misc">
                                      <h5>💼 {pageTitle} ({page.tier_name})</h5>
                                      <div className="page-meta">
                                        <span className="badge badge--primary">{page.avg_score.toFixed(1)}/10</span>
                                      </div>
                                      
                                      {segments.map((segment, segIndex) => (
                                        <div key={segIndex} className="container--misc">
                                          <div className="container--content">💼 Strategic Insight: {segment}</div>
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
                      <div className="voice--analysis">
                        <p className="text--body">📝 No voice analysis data available for this persona</p>
                      </div>
                    )}
                  </div>
                )}

                {activeTab === 'evidence' && (
                  <div className="evidence--content">
                    <h2 className="heading--section">🔍 Evidence & Analysis</h2>
                    
                    <div className="evidence--content">
                      <p className="text--body">Detailed audit evidence and AI analysis for <strong>{profile?.name}</strong></p>
                    </div>

                    {auditData?.length > 0 ? (
                      <div className="evidence--content">
                        <div className="evidence--content">
                          <h3 className="heading--subsection">📊 Evidence Analysis Overview</h3>
                          <p className="text--body">Detailed audit evidence and AI analysis for <strong>{profile?.name}</strong></p>
                          
                          <div className="evidence--content">
                            <div className="container--card">
                              <strong>Total Evidence Items:</strong> {auditData.filter((row: any) => {
                                const personaName = PERSONA_NAMES[filters.persona] || filters.persona
                                return row.persona_id === personaName || row.persona_id === filters.persona
                              }).length}
                            </div>
                            <div className="container--card">
                              <strong>Pages Analyzed:</strong> {[...new Set(auditData.filter((row: any) => {
                                const personaName = PERSONA_NAMES[filters.persona] || filters.persona
                                return row.persona_id === personaName || row.persona_id === filters.persona
                              }).map((row: any) => row.page_id))].length}
                            </div>
                          </div>
                        </div>
                        
                        <EvidenceBrowser
                          data={auditData.filter((row: any) => {
                            const personaName = PERSONA_NAMES[filters.persona] || filters.persona
                            return row.persona_id === personaName || row.persona_id === filters.persona
                          }) || []}
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
                      <div className="evidence--content">
                        <h3 className="heading--subsection">📊 Evidence Analysis</h3>
                        <p className="text--body">No audit data available for <strong>{profile?.name}</strong></p>
                        <p className="text--body">Please ensure the audit has been run and data is available.</p>
                      </div>
                    )}
                  </div>
                )}
              </div>
            </div>
          </div>
        </>
      )}
    </PageContainer>
  )
}

const columns: ColumnDef<PerformanceData>[] = [
  {
    accessorKey: 'title',
    header: 'Page',
    cell: ({ row }) => createFriendlyPageTitle(row.original.page_id, row.original.url),
  },
  {
    accessorKey: 'url',
    header: 'URL',
    cell: ({ row }) => <a href={row.original.url} target="_blank" rel="noopener noreferrer" className="link--external">{createFriendlyPageTitle(row.original.page_id, row.original.url)}</a>,
  },
  {
    accessorKey: 'avg_score',
    header: 'Score',
    cell: ({ row }) => (
      <span className={`badge ${
        row.original.avg_score >= 8 ? 'badge--success' :
        row.original.avg_score >= 6 ? 'badge--primary' :
        row.original.avg_score >= 4 ? 'badge--warning' : 'badge--error'
      }`}>
        {row.original.avg_score.toFixed(1)}/10
      </span>
    ),
  },
  {
    accessorKey: 'tier_name',
    header: 'Content Tier',
    cell: ({ row }) => <span className="badge badge--default">{row.original.tier_name}</span>,
  },
  {
    accessorKey: 'overall_sentiment',
    header: 'Sentiment',
    cell: ({ row }) => row.original.overall_sentiment || 'N/A',
  },
  {
    id: 'actions',
    header: 'Actions',
    cell: ({ row }) => (
      <div className="button--action">
        {row.original.avg_score < 4 && (
          <span className="badge--status badge--status">Critical</span>
        )}
        {row.original.avg_score >= 8 && (
          <span className="badge--status badge--status">Success</span>
        )}
      </div>
    ),
  },
];

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

export default PersonaViewer
