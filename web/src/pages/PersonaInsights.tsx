import { useState } from 'react'
import { useQuery } from '@tanstack/react-query'
import { Banner, BarChart, PieChart, StandardCard, PageContainer, PageHeader } from '../components'

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
    <PageContainer title="👥 Persona Insights">
      <PageHeader
        title="👥 Persona Insights"
        description="Loading persona analysis..."
      />
    </PageContainer>
  )

  if (error) return (
    <PageContainer title="👥 Persona Insights">
      <PageHeader
        title="👥 Persona Insights"
        description={`❌ Error loading persona data: ${error.message}`}
      />
    </PageContainer>
  )

  if (!personaData?.personas) return (
    <PageContainer title="👥 Persona Insights">
      <PageHeader
        title="👥 Persona Insights"
        description="❌ No data available for Persona Insights analysis."
      />
    </PageContainer>
  )

  const personas: PersonaData[] = personaData.personas || []
  const allPersonas = ['All', ...personas.map((p: PersonaData) => p.persona_id)]
  const analysisMode = selectedPersona === 'All' ? 'comparison' : 'individual'

  return (
    <PageContainer title="👥 Persona Insights">
      <PageHeader
        title="👥 Persona Insights"
        description="Cross-persona performance analysis and strategic persona comparison"
      />

      {/* Persona Analysis Focus */}
      <div className="container--section">
        <h2 className="heading--section">🎯 Persona Analysis Focus</h2>
        <div className="container--layout">
          <div>
            <label className="label--form">
              👤 Select Persona for Analysis
            </label>
            <select 
              value={selectedPersona}
              onChange={(e) => setSelectedPersona(e.target.value)}
              className="select--form"
            >
              {allPersonas.map(persona => (
                <option key={persona} value={persona}>{persona}</option>
              ))}
            </select>
            <small className="text--body">
              Choose 'All' for comparison view, or specific persona for detailed analysis
            </small>
          </div>
          <div>
            {selectedPersona === 'All' ? (
              <div className="container--section text--display">
                <strong className="text--body">📊 Comparison Mode</strong><br/>
                <small className="text--body">Analyzing all personas side-by-side</small>
              </div>
            ) : (
              <div className="container--section text--display">
                <strong className="text--body">🔍 Deep Dive Mode</strong><br/>
                <small className="text--body">Focused analysis of {selectedPersona}</small>
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
    </PageContainer>
  )
}

function PersonaComparisonAnalysis({ personas }: { personas: PersonaData[] }) {
  // Sort personas by score (descending) to match Streamlit behavior
  const sortedPersonas = [...personas].sort((a, b) => b.avg_score - a.avg_score)

  return (
    <div className="container--section">
      <h2 className="heading--section">📊 Persona Performance Comparison</h2>
      
      {/* Persona Performance Cards */}
      <h3 className="heading--subsection">👥 Persona Performance Cards</h3>
      <div className="container--layout">
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
              <div className="text--display">
                <strong className="text--display">{persona.page_count || 0} pages analyzed</strong>
              </div>
            </StandardCard>
          )
        })}
      </div>

      {/* Comparison Charts */}
      <h3 className="heading--subsection">📈 Persona Performance Comparison Charts</h3>
      <div className="container--section">
        <BarChart
          orientation="h"
          x={sortedPersonas.map((p: PersonaData) => p.avg_score || 0)}
          y={sortedPersonas.map((p: PersonaData) => p.persona_id.replace('_', ' '))}
          title="Overall Brand Health Score by Persona"
        />
      </div>

      <div className="container--layout">
        <div>
          <BarChart
            orientation="h"
            x={sortedPersonas.map((p: PersonaData) => p.page_count || 0)}
            y={sortedPersonas.map((p: PersonaData) => p.persona_id.replace('_', ' '))}
            title="Pages Analyzed per Persona"
          />
        </div>
        <div>
          <PieChart
            values={sortedPersonas.map((p: PersonaData) => p.avg_score || 0)}
            labels={sortedPersonas.map((p: PersonaData) => p.persona_id.replace('_', ' '))}
            title="Score Distribution Across Personas"
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
    <div className="container--section">
      <h3 className="heading--subsection">🏆 Persona Performance Ranking</h3>
      
      <div className="container--layout">
        <div>
          <div className="container--section">
            <h4 className="heading--card">🥇 Top Performing Personas</h4>
            {topPersonas.map((persona, index) => {
              const medal = index === 0 ? "🥇" : index === 1 ? "🥈" : "🥉"
              return (
                <div key={persona.persona_id} className="container--section">
                  <strong className="text--display">{medal} {persona.persona_id.replace('_', ' ')}: {persona.avg_score.toFixed(1)}/10</strong><br/>
                  <small className="text--body">• {persona.page_count} pages analyzed</small>
                </div>
              )
            })}
          </div>
        </div>
        
        <div>
          <Banner
            message={
              <>
                <h4 className="heading--card">📉 Areas for Improvement</h4>
                {bottomPersonas.map((persona) => (
                  <div key={persona.persona_id} className="container--section">
                    <strong className="text--display">⚠️ {persona.persona_id.replace('_', ' ')}: {persona.avg_score.toFixed(1)}/10</strong><br/>
                    <small className="text--body">• Focus on improving content quality and alignment</small>
                  </div>
                ))}
              </>
            }
          />
        </div>
      </div>

      {/* Strategic Recommendations */}
      <div>
        <h4 className="heading--subsection">🎯 Strategic Recommendations</h4>
        <div className="container--layout">
          <div>
            <div className="container--section">
              <h5 className="heading--card">🏆 Benchmark Persona</h5>
              <strong className="text--display">{personas[0]?.persona_id.replace('_', ' ')}</strong><br/>
              <small className="text--body"><em>Use their experience patterns as templates</em></small>
            </div>
          </div>
          <div>
            <div className="container--section">
              <h5 className="heading--card">🎯 Priority Persona</h5>
              <strong className="text--display">{personas[personas.length - 1]?.persona_id.replace('_', ' ')}</strong><br/>
              <small className="text--body"><em>Focus improvement efforts here first</em></small>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}

function IndividualPersonaAnalysis({ persona, personaPages, isLoading }: { persona: string, personaPages: any, isLoading: boolean }) {
  if (isLoading) return (
    <div className="container--section">
      <h3 className="heading--subsection">🔍 Deep Dive: {persona.replace('_', ' ')}</h3>
      <p className="text--body">Loading detailed persona analysis...</p>
    </div>
  )

  if (!personaPages?.pages) return (
    <div className="container--section">
      <h3 className="heading--subsection">🔍 Deep Dive: {persona.replace('_', ' ')}</h3>
      <p className="text--body">No data available for detailed analysis of {persona.replace('_', ' ')}.</p>
    </div>
  )

  const pages: PersonaPageData[] = personaPages?.pages || []
  const metrics: PersonaMetrics = personaPages?.metrics || {}

  return (
    <div>
      <h2 className="heading--section">🔍 Deep Dive: {persona.replace('_', ' ')}</h2>
      
      {/* Performance Overview */}
      <div className="container--section">
        <h3 className="heading--subsection">📊 Performance Overview</h3>
        <div className="container--layout">
          <StandardCard
            value={`${(metrics.avg_score || 0).toFixed(1)}/10`}
            label="Average Score"
            status={metrics.avg_score >= 7 ? 'excellent' : metrics.avg_score >= 5 ? 'good' : 'warning'}
          />
          <StandardCard
            value={`${metrics.page_count || 0}`}
            label="Pages Analyzed"
            status="good"
          />
          <StandardCard
            value={`${metrics.primary_tier || 'N/A'}`}
            label="Primary Tier"
            status="good"
          />
          <StandardCard
            value={`${metrics.critical_issues || 0}`}
            label="Critical Issues"
            status={metrics.critical_issues === 0 ? 'excellent' : metrics.critical_issues <= 2 ? 'warning' : 'critical'}
          />
        </div>
      </div>

      {/* Page-by-Page Analysis */}
      <div className="container--section">
        <h3 className="heading--subsection">📄 Page-by-Page Analysis</h3>
        <div className="container--layout">
          {pages.map((page: PersonaPageData) => (
            <StandardCard
              key={page.page_id}
              title={page.title || page.url_slug}
              value={`${page.avg_score.toFixed(1)}/10`}
              label={`${page.tier_name} (${page.tier})`}
              status={page.avg_score >= 7 ? 'excellent' : page.avg_score >= 5 ? 'good' : page.avg_score >= 3 ? 'warning' : 'critical'}
            >
              <div className="container--section">
                <p className="text--body">
                  <strong className="text--display">URL:</strong> {page.url}
                </p>
                {page.first_impression && (
                  <p className="text--body">
                    <strong className="text--display">First Impression:</strong> {page.first_impression.substring(0, 100)}...
                  </p>
                )}
              </div>
            </StandardCard>
          ))}
        </div>
      </div>
    </div>
  )
}

function CrossPersonaInsights({ personas }: { personas: PersonaData[] }) {
  const avgScore = personas.reduce((sum, p) => sum + (p.avg_score || 0), 0) / personas.length
  const totalPages = personas.reduce((sum, p) => sum + (p.page_count || 0), 0)

  return (
    <div className="container--section">
      <h2 className="heading--section">🔄 Cross-Persona Insights</h2>
      
      <div className="container--layout">
        <StandardCard
          title="Overall Brand Health"
          value={`${avgScore.toFixed(1)}/10`}
          label="Average Across All Personas"
          status={avgScore >= 7 ? 'excellent' : avgScore >= 5 ? 'good' : 'warning'}
        />
        <StandardCard
          title="Total Coverage"
          value={`${totalPages}`}
          label="Total Pages Analyzed"
          status="good"
        />
        <StandardCard
          title="Persona Diversity"
          value={`${personas.length}`}
          label="Unique Personas"
          status="excellent"
        />
      </div>

      <div className="container--section">
        <h3 className="heading--subsection">💡 Key Insights</h3>
        <div className="container--layout">
          <div className="container--section">
            <h4 className="heading--card">🎯 Strongest Persona</h4>
            <p className="text--body">
              <strong className="text--display">{personas[0]?.persona_id.replace('_', ' ')}</strong> shows the highest brand health score.
              Consider using their content patterns as templates for other personas.
            </p>
          </div>
          <div className="container--section">
            <h4 className="heading--card">⚠️ Improvement Opportunity</h4>
            <p className="text--body">
              <strong className="text--display">{personas[personas.length - 1]?.persona_id.replace('_', ' ')}</strong> has the lowest scores.
              Focus optimization efforts on their user journey and content alignment.
            </p>
          </div>
        </div>
      </div>
    </div>
  )
}

export default PersonaInsights
