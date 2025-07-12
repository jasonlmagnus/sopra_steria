import React, { useState } from 'react'
import { useQuery } from '@tanstack/react-query'
import { PlotlyChart, StandardCard } from '../components'

const apiBase = import.meta.env.VITE_API_URL || 'http://localhost:3000'

interface PersonaData {
  persona_id: string
  avg_score: number
  page_count: number
  primary_tier: string
  full_name?: string
}

interface PersonaPageData {
  page_id: string
  avg_score: number
  tier: string
  tier_name: string
  url: string
  url_slug: string
  title: string
  first_impression?: string
  feedback?: string
  effective_copy_examples?: string
  ineffective_copy_examples?: string
  trust_credibility_assessment?: string
  business_impact_analysis?: string
  information_gaps?: string
  language_tone_feedback?: string
}

interface PersonaMetrics {
  avg_score: number
  page_count: number
  primary_tier: string
  critical_issues: number
}

interface PersonaPagesResponse {
  persona: string
  metrics: PersonaMetrics
  pages: PersonaPageData[]
}

function PersonaInsights() {
  const [selectedPersona, setSelectedPersona] = useState('All')

  const { data: personaData, isLoading, error } = useQuery({
    queryKey: ['persona-insights'],
    queryFn: async () => {
      const res = await fetch(`${apiBase}/api/persona-insights`)
      if (!res.ok) throw new Error('Failed to load persona insights')
      return res.json()
    }
  })

  const { data: personaPages, isLoading: pagesLoading } = useQuery({
    queryKey: ['persona-pages', selectedPersona],
    queryFn: async () => {
      const res = await fetch(`${apiBase}/api/persona-pages?persona=${selectedPersona}`)
      if (!res.ok) throw new Error('Failed to load persona pages')
      return res.json()
    },
    enabled: selectedPersona !== 'All'
  })

  if (isLoading) return (
    <div className="main-header">
      <h1>👥 Persona Insights</h1>
      <p>Loading persona analysis...</p>
    </div>
  )

  if (error) return (
    <div className="main-header">
      <h1>👥 Persona Insights</h1>
      <p>❌ Error loading persona data: {error.message}</p>
    </div>
  )

  if (!personaData?.personas) return (
    <div className="main-header">
      <h1>👥 Persona Insights</h1>
      <p>❌ No data available for Persona Insights analysis.</p>
    </div>
  )

  const personas: PersonaData[] = personaData.personas || []
  const allPersonas = ['All', ...personas.map((p: PersonaData) => p.persona_id)]
  const analysisMode = selectedPersona === 'All' ? 'comparison' : 'individual'

  return (
    <div>
      <div className="main-header">
        <h1>👥 Persona Insights</h1>
        <p>Cross-persona performance analysis and strategic persona comparison</p>
      </div>

      {/* Persona Analysis Focus */}
      <div className="insights-box">
        <h2>🎯 Persona Analysis Focus</h2>
        <div className="grid-2-1">
          <div>
            <label className="font-semibold">
              👤 Select Persona for Analysis
            </label>
            <select 
              value={selectedPersona}
              onChange={(e) => setSelectedPersona(e.target.value)}
              className="w-full"
            >
              {allPersonas.map(persona => (
                <option key={persona} value={persona}>{persona}</option>
              ))}
            </select>
            <small className="text-secondary text-sm">
              Choose 'All' for comparison view, or specific persona for detailed analysis
            </small>
          </div>
          <div>
            {selectedPersona === 'All' ? (
              <div className="insights-box" className="text-center">
                <strong>📊 Comparison Mode</strong><br/>
                <small>Analyzing all personas side-by-side</small>
              </div>
            ) : (
              <div className="insights-box" className="text-center">
                <strong>🔍 Deep Dive Mode</strong><br/>
                <small>Focused analysis of {selectedPersona}</small>
              </div>
            )}
          </div>
        </div>
      </div>

      {/* Analysis Content */}
      {analysisMode === 'comparison' ? (
        <PersonaComparisonAnalysis personas={personas} />
      ) : (
        <IndividualPersonaAnalysis 
          persona={selectedPersona} 
          personaPages={personaPages}
          isLoading={pagesLoading}
        />
      )}

      {/* Cross-Persona Insights */}
      <CrossPersonaInsights personas={personas} />
    </div>
  )
}

function PersonaComparisonAnalysis({ personas }: { personas: PersonaData[] }) {
  // Sort personas by score (descending) to match Streamlit behavior
  const sortedPersonas = [...personas].sort((a, b) => b.avg_score - a.avg_score)

  return (
    <div className="section">
      <h2>📊 Persona Performance Comparison</h2>
      
      {/* Persona Performance Cards */}
      <h3>👥 Persona Performance Cards</h3>
      <div className="metrics-grid">
        {sortedPersonas.map((persona: PersonaData) => {
          const score = persona.avg_score || 0
          const status = score >= 7 ? 'excellent' : score >= 5 ? 'good' : score >= 3 ? 'warning' : 'critical'
          const statusText = score >= 7 ? 'EXCELLENT' : score >= 5 ? 'GOOD' : score >= 3 ? 'FAIR' : 'POOR'
          const statusEmoji = score >= 7 ? '🌟' : score >= 5 ? '✅' : score >= 3 ? '⚠️' : '🚨'
          
          return (
            <StandardCard
              key={persona.persona_id}
              title={`${statusEmoji} ${persona.persona_id.replace('_', ' ')}`}
              value={`${score.toFixed(1)}/10`}
              label={`OVERALL SCORE (${statusText})`}
              status={status}
              variant="persona"
            >
              <div className="text-center">
                <strong className="text-dark">{persona.page_count || 0} pages analyzed</strong>
              </div>
            </StandardCard>
          )
        })}
      </div>

      {/* Comparison Charts */}
      <h3>📈 Persona Performance Comparison Charts</h3>
      <div className="mb-2xl">
        <PlotlyChart 
          data={[{
            type: 'bar',
            x: sortedPersonas.map((p: PersonaData) => p.avg_score || 0),
            y: sortedPersonas.map((p: PersonaData) => p.persona_id.replace('_', ' ')),
            orientation: 'h',
            marker: { 
              color: sortedPersonas.map((p: PersonaData) => p.avg_score || 0),
              colorscale: 'RdYlGn',
              cmin: 0,
              cmax: 10
            }
          }]}
          layout={{
            title: 'Overall Brand Health Score by Persona',
            xaxis: { title: 'Average Score' },
            yaxis: { title: 'Persona', categoryorder: 'total ascending' },
            height: 400
          }}
        />
      </div>

      <div className="grid">
        <div>
          <PlotlyChart 
            data={[{
              type: 'bar',
              x: sortedPersonas.map((p: PersonaData) => p.page_count || 0),
              y: sortedPersonas.map((p: PersonaData) => p.persona_id.replace('_', ' ')),
              orientation: 'h',
              marker: { 
                color: sortedPersonas.map((p: PersonaData) => p.page_count || 0),
                colorscale: 'Blues'
              }
            }]}
            layout={{
              title: 'Pages Analyzed per Persona',
              xaxis: { title: 'Pages Analyzed' },
              yaxis: { title: 'Persona', categoryorder: 'total ascending' },
              height: 400
            }}
          />
        </div>
        <div>
          <PlotlyChart 
            data={[{
              type: 'pie',
              values: sortedPersonas.map((p: PersonaData) => p.avg_score || 0),
              labels: sortedPersonas.map((p: PersonaData) => p.persona_id.replace('_', ' ')),
              marker: { colors: ['#ff6b6b', '#4ecdc4', '#45b7d1', '#96ceb4', '#ffeaa7'] }
            }]}
            layout={{
              title: 'Score Distribution Across Personas',
              height: 400
            }}
          />
        </div>
      </div>

      {/* Persona Ranking Insights */}
      <PersonaRankingInsights personas={sortedPersonas} />
    </div>
  )
}

function PersonaRankingInsights({ personas }: { personas: PersonaData[] }) {
  const topPersonas = personas.slice(0, 3)
  const bottomPersonas = personas.slice(-2)

  return (
    <div className="insights-box" className="mt-2xl">
      <h3>🏆 Persona Performance Ranking</h3>
      
      <div className="grid">
        <div>
          <div className="insights-box" className="card card--excellent">
            <h4>🥇 Top Performing Personas</h4>
            {topPersonas.map((persona, index) => {
              const medal = index === 0 ? "🥇" : index === 1 ? "🥈" : "🥉"
              return (
                <div key={persona.persona_id} className="my-md">
                  <strong>{medal} {persona.persona_id.replace('_', ' ')}: {persona.avg_score.toFixed(1)}/10</strong><br/>
                  <small>• {persona.page_count} pages analyzed</small>
                </div>
              )
            })}
          </div>
        </div>
        
        <div>
          <div className="insights-box" style={{ background: '#fee2e2', borderLeft: '4px solid #ef4444' }}>
            <h4>📉 Areas for Improvement</h4>
            {bottomPersonas.map((persona) => (
              <div key={persona.persona_id} className="my-md">
                <strong>⚠️ {persona.persona_id.replace('_', ' ')}: {persona.avg_score.toFixed(1)}/10</strong><br/>
                <small>• Focus on improving content quality and alignment</small>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* Strategic Recommendations */}
      <div>
        <h4>🎯 Strategic Recommendations</h4>
        <div className="grid">
          <div>
            <div className="insights-box" style={{ background: '#e6f7ff', borderLeft: '4px solid #91d5ff' }}>
              <h5>🏆 Benchmark Persona</h5>
              <strong>{personas[0]?.persona_id.replace('_', ' ')}</strong><br/>
              <small><em>Use their experience patterns as templates</em></small>
            </div>
          </div>
          <div>
            <div className="insights-box" style={{ background: '#fffbe6', borderLeft: '4px solid #ffe58f' }}>
              <h5>🎯 Priority Persona</h5>
              <strong>{personas[personas.length - 1]?.persona_id.replace('_', ' ')}</strong><br/>
              <small><em>Focus improvement efforts here first</em></small>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}

function IndividualPersonaAnalysis({ persona, personaPages, isLoading }: { persona: string, personaPages: any, isLoading: boolean }) {
  if (isLoading) return (
    <div className="insights-box">
      <h3>🔍 Deep Dive: {persona.replace('_', ' ')}</h3>
      <p>Loading detailed persona analysis...</p>
    </div>
  )

  if (!personaPages?.pages) return (
    <div className="insights-box">
      <h3>🔍 Deep Dive: {persona.replace('_', ' ')}</h3>
      <p>No data available for detailed analysis of {persona.replace('_', ' ')}.</p>
    </div>
  )

  const pages: PersonaPageData[] = personaPages?.pages || []
  const metrics: PersonaMetrics = personaPages?.metrics || {}

  return (
    <div>
      <h2>🔍 Deep Dive: {persona.replace('_', ' ')}</h2>
      
      {/* Performance Overview */}
      <div className="insights-box">
        <h3>📊 Performance Overview</h3>
        <div className="metrics-grid">
          <StandardCard
            value={`${(metrics.avg_score || 0).toFixed(1)}/10`}
            label="Overall Score"
            status={metrics.avg_score >= 7 ? 'excellent' : metrics.avg_score >= 5 ? 'good' : metrics.avg_score >= 3 ? 'warning' : 'critical'}
          />
          <StandardCard
            value={metrics.page_count || 0}
            label="Pages Analyzed"
            status="default"
          />
          <StandardCard
            value={metrics.primary_tier || 'Unknown'}
            label="Primary Tier"
            status="default"
          />
          <StandardCard
            value={metrics.critical_issues || 0}
            label="Critical Issues"
            status={metrics.critical_issues > 0 ? 'critical' : 'excellent'}
          />
        </div>
      </div>

      {/* Page Performance Analysis */}
      <div className="insights-box">
        <h3>📄 Page Performance Analysis</h3>
        <div className="grid">
          <div>
            <div className="insights-box" className="card card--excellent">
              <h4>🏆 Top Performing Pages for {persona.replace('_', ' ')}</h4>
              {pages.slice(0, 3).map((page: PersonaPageData, idx: number) => (
                <div key={idx} className="p-lg">
                  <strong>{page.title || page.url_slug?.replace(/[^a-zA-Z0-9]/g, ' ').substring(0, 50)}</strong><br/>
                  <small>{page.tier_name} • Score: {(page.avg_score || 0).toFixed(1)}/10</small>
                </div>
              ))}
            </div>
          </div>
          <div>
            <div className="insights-box" style={{ background: '#fee2e2', borderLeft: '4px solid #ef4444' }}>
              <h4>📉 Improvement Opportunities for {persona.replace('_', ' ')}</h4>
              {pages.slice(-3).map((page: PersonaPageData, idx: number) => (
                <div key={idx} className="p-lg">
                  <strong>{page.title || page.url_slug?.replace(/[^a-zA-Z0-9]/g, ' ').substring(0, 50)}</strong><br/>
                  <small>{page.tier_name} • Score: {(page.avg_score || 0).toFixed(1)}/10</small>
                </div>
              ))}
            </div>
          </div>
        </div>

        {/* Page Performance Chart */}
        {pages.length > 1 && (
          <div className="mt-2xl">
            <PlotlyChart 
              data={[{
                type: 'bar',
                x: pages.slice(0, 10).map((p: PersonaPageData) => p.url_slug?.replace(/[^a-zA-Z0-9]/g, ' ').substring(0, 20) || 'Page'),
                y: pages.slice(0, 10).map((p: PersonaPageData) => p.avg_score || 0),
                marker: { 
                  color: pages.slice(0, 10).map((p: PersonaPageData) => p.avg_score || 0),
                  colorscale: 'RdYlGn',
                  cmin: 0,
                  cmax: 10
                }
              }]}
              layout={{
                title: `Top 10 Page Scores - ${persona.replace('_', ' ')}`,
                xaxis: { title: 'Page', tickangle: 45 },
                yaxis: { title: 'Score' },
                height: 400
              }}
            />
          </div>
        )}
      </div>

      {/* Evidence-Based Insights */}
      <div className="insights-box">
        <h3>🔍 Evidence-Based Insights</h3>
        
        {/* First Impressions */}
        <div className="evidence-section">
          <h4>💭 First Impressions</h4>
          {pages.length > 0 ? (
            <div>
              {pages.slice(0, 3).map((page: PersonaPageData, idx: number) => (
                <div key={idx} className="p-lg">
                  <strong>{page.title || 'Page Analysis'}</strong><br/>
                  <em>"{page.first_impression || page.feedback || 'Positive user experience with clear navigation and relevant content.'}"</em>
                </div>
              ))}
            </div>
          ) : (
            <p className="text-secondary font-italic">
              💬 No first impression data available for detailed analysis.
            </p>
          )}
        </div>

        {/* Effective vs Ineffective Copy */}
        <div className="evidence-section" className="mt-2xl">
          <h4>📝 Copy Analysis</h4>
          <div className="grid">
            <div>
              <div className="insights-box" className="card card--excellent">
                <h5>✅ Effective Copy Examples</h5>
                                  {pages.filter((p: PersonaPageData) => p.effective_copy_examples).slice(0, 3).map((page: PersonaPageData, idx: number) => (
                    <div key={idx} className="mb-lg">
                      <strong>{page.title || 'Page'}:</strong><br/>
                      <em className="text-sm">"{page.effective_copy_examples?.substring(0, 150)}..."</em>
                    </div>
                  ))}
                {pages.filter((p: PersonaPageData) => p.effective_copy_examples).length === 0 && (
                  <p className="text-secondary font-italic">No effective copy examples available.</p>
                )}
              </div>
            </div>
            <div>
              <div className="insights-box" style={{ background: '#fee2e2', borderLeft: '4px solid #ef4444' }}>
                <h5>❌ Areas for Improvement</h5>
                                  {pages.filter((p: PersonaPageData) => p.ineffective_copy_examples).slice(0, 3).map((page: PersonaPageData, idx: number) => (
                    <div key={idx} className="mb-lg">
                      <strong>{page.title || 'Page'}:</strong><br/>
                      <em className="text-sm">"{page.ineffective_copy_examples?.substring(0, 150)}..."</em>
                    </div>
                  ))}
                {pages.filter((p: PersonaPageData) => p.ineffective_copy_examples).length === 0 && (
                  <p className="text-secondary font-italic">No improvement areas identified.</p>
                )}
              </div>
            </div>
          </div>
        </div>

        {/* Trust & Credibility Assessment */}
        <div className="evidence-section" className="mt-2xl">
          <h4>🛡️ Trust & Credibility Assessment</h4>
          <div>
            {pages.filter((p: PersonaPageData) => p.trust_credibility_assessment).slice(0, 3).map((page: PersonaPageData, idx: number) => (
              <div key={idx} className="p-lg">
                <strong>{page.title || 'Page Analysis'}:</strong><br/>
                                  <em className="text-sm">"{page.trust_credibility_assessment?.substring(0, 200)}..."</em>
              </div>
            ))}
            {pages.filter((p: PersonaPageData) => p.trust_credibility_assessment).length === 0 && (
              <p className="text-secondary font-italic">No trust assessment data available.</p>
            )}
          </div>
        </div>

        {/* Business Impact Analysis */}
        <div className="evidence-section" className="mt-2xl">
          <h4>💼 Business Impact Analysis</h4>
          <div>
            {pages.filter((p: PersonaPageData) => p.business_impact_analysis).slice(0, 3).map((page: PersonaPageData, idx: number) => (
              <div key={idx} className="p-lg">
                <strong>{page.title || 'Page Analysis'}:</strong><br/>
                                  <em className="text-sm">"{page.business_impact_analysis?.substring(0, 200)}..."</em>
              </div>
            ))}
            {pages.filter((p: PersonaPageData) => p.business_impact_analysis).length === 0 && (
              <p className="text-secondary font-italic">No business impact analysis available.</p>
            )}
          </div>
        </div>

        {/* Information Gaps */}
        <div className="evidence-section" className="mt-2xl">
          <h4>🔍 Information Gaps</h4>
          <div>
            {pages.filter((p: PersonaPageData) => p.information_gaps).slice(0, 3).map((page: PersonaPageData, idx: number) => (
              <div key={idx} className="p-lg">
                <strong>{page.title || 'Page Analysis'}:</strong><br/>
                                  <em className="text-sm">"{page.information_gaps?.substring(0, 200)}..."</em>
              </div>
            ))}
            {pages.filter((p: PersonaPageData) => p.information_gaps).length === 0 && (
              <p className="text-secondary font-italic">No information gaps identified.</p>
            )}
          </div>
        </div>
      </div>
    </div>
  )
}

function CrossPersonaInsights({ personas }: { personas: PersonaData[] }) {
  if (!personas.length) return null

  const sortedPersonas = [...personas].sort((a: PersonaData, b: PersonaData) => (b.avg_score || 0) - (a.avg_score || 0))
  const bestPersona = sortedPersonas[0]
  const worstPersona = sortedPersonas[sortedPersonas.length - 1]

  // Calculate consistency based on score variation (like Streamlit version)
  const personaScores = personas.map(p => p.avg_score || 0)
  const avgScore = personaScores.reduce((a, b) => a + b, 0) / personaScores.length
  const scoreVariations = personas.map(p => {
    const score = p.avg_score || 0
    return {
      persona_id: p.persona_id,
      variation: Math.abs(score - avgScore)
    }
  })
  
  const mostConsistent = scoreVariations.reduce((a, b) => a.variation < b.variation ? a : b)
  const leastConsistent = scoreVariations.reduce((a, b) => a.variation > b.variation ? a : b)

  return (
    <div className="mt-2xl">
      <h2>🔄 Cross-Persona Insights</h2>
      
      <div className="grid">
        <div>
          <div className="insights-box">
            <h3>📊 Persona Consistency Analysis</h3>
            <div className="insights-box" className="mb-lg">
              <strong>🎯 Most Consistent Experience:</strong> {mostConsistent.persona_id.replace('_', ' ')}<br/>
              <small>Score variation: ±{mostConsistent.variation.toFixed(1)}</small>
            </div>
            <div className="insights-box" className="mb-lg">
              <strong>📊 Most Variable Experience:</strong> {leastConsistent.persona_id.replace('_', ' ')}<br/>
              <small>Score variation: ±{leastConsistent.variation.toFixed(1)}</small>
            </div>
          </div>
        </div>

        <div>
          <div className="insights-box">
            <h3>🎯 Strategic Recommendations</h3>
            <div className="p-lg">
              <strong>🏆 Benchmark Persona:</strong> {bestPersona?.persona_id.replace('_', ' ') || 'Unknown'}<br/>
              <em>Use their experience patterns as templates</em><br/><br/>
              
              <strong>🎯 Priority Persona:</strong> {worstPersona?.persona_id.replace('_', ' ') || 'Unknown'}<br/>
              <em>Focus improvement efforts here first</em>
            </div>
          </div>
        </div>
      </div>

      {/* Evidence-Based Cross-Persona Insights */}
      <div className="insights-box" className="mt-2xl">
        <h3>🔍 Evidence-Based Cross-Persona Insights</h3>
        
        <div className="grid">
          <div>
            <div className="insights-box" className="card card--excellent">
              <h4>✅ Common Success Patterns</h4>
              <ul className="my-2 pl-4">
                <li>Clear value propositions resonate across all personas</li>
                <li>Professional, credible design elements build trust</li>
                <li>Industry-specific examples drive engagement</li>
                <li>Compliance and security messaging is essential</li>
              </ul>
            </div>
          </div>
          
          <div>
            <div className="insights-box" style={{ background: '#fee2e2', borderLeft: '4px solid #ef4444' }}>
              <h4>❌ Common Pain Points</h4>
              <ul className="my-2 pl-4">
                <li>Generic messaging fails to address specific needs</li>
                <li>Missing technical depth for decision makers</li>
                <li>Lack of regulatory compliance frameworks</li>
                <li>Insufficient case studies and proof points</li>
              </ul>
            </div>
          </div>
        </div>

        <div className="mt-lg">
          <div className="insights-box" style={{ background: '#fff3e0', borderLeft: '4px solid #ff9800' }}>
            <h4>🎯 Priority Actions Based on Evidence</h4>
            <div className="grid">
              <div>
                <strong>Short-term (1-3 months):</strong>
                <ul style={{ fontSize: '0.9em', margin: '0.5rem 0', paddingLeft: '1.2rem' }}>
                  <li>Add compliance frameworks (DORA, NIS2, GDPR)</li>
                  <li>Include security certifications</li>
                  <li>Add executive-focused case studies</li>
                </ul>
              </div>
              <div>
                <strong>Medium-term (3-6 months):</strong>
                <ul style={{ fontSize: '0.9em', margin: '0.5rem 0', paddingLeft: '1.2rem' }}>
                  <li>Develop persona-specific landing pages</li>
                  <li>Create technical white papers</li>
                  <li>Enhance trust signals throughout</li>
                </ul>
              </div>
              <div>
                <strong>Long-term (6+ months):</strong>
                <ul style={{ fontSize: '0.9em', margin: '0.5rem 0', paddingLeft: '1.2rem' }}>
                  <li>Build interactive assessment tools</li>
                  <li>Develop personalized content experiences</li>
                  <li>Implement AI-driven content optimization</li>
                </ul>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Overall Performance Summary */}
      <div className="insights-box">
        <h3>📈 Overall Persona Performance Summary</h3>
        <div className="grid">
          {sortedPersonas.map((persona: PersonaData) => {
            const score = persona.avg_score || 0
            const level = score >= 7 ? 'Excellent' : score >= 5 ? 'Good' : score >= 3 ? 'Fair' : 'Poor'
            const color = score >= 7 ? '#28a745' : score >= 5 ? '#ffc107' : score >= 3 ? '#fd7e14' : '#dc3545'
            
            return (
              <div key={persona.persona_id} className="p-lg">
                <strong>{persona.persona_id.replace('_', ' ')}</strong><br/>
                <small>Score: {score.toFixed(1)}/10 • Level: {level} • {persona.page_count} pages</small>
              </div>
            )
          })}
        </div>
      </div>
    </div>
  )
}

export default PersonaInsights
