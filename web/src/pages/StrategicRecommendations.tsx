import { useState, useEffect } from 'react'
import { useQuery } from '@tanstack/react-query'
import { EvidenceDisplay, EvidenceBrowser } from '../components/EvidenceDisplay'
import { PlotlyChart } from '../components/PlotlyChart'

const apiBase = import.meta.env.VITE_API_URL || 'http://localhost:3000'

interface StrategicRecommendation {
  id: string
  category: string
  title: string
  description: string
  priority: 'High' | 'Medium' | 'Low'
  impact: 'High' | 'Medium' | 'Low'
  effort: 'High' | 'Medium' | 'Low'
  timeframe: 'Immediate' | 'Short-term' | 'Medium-term' | 'Long-term'
  evidence: string[]
  affectedPages: string[]
  personas: string[]
  businessValue: string
  implementation: string[]
  risks: string[]
}

interface AggregatedEvidence {
  category: string
  evidenceCount: number
  strongEvidence: string[]
  improvementAreas: string[]
  businessImpact: string[]
  trustIssues: string[]
}

function StrategicRecommendations() {
  const [selectedCategory, setSelectedCategory] = useState('All')
  const [selectedPriority, setSelectedPriority] = useState('All')
  const [selectedTimeframe, setSelectedTimeframe] = useState('All')
  const [viewMode, setViewMode] = useState('recommendations')

  const { data: auditData, isLoading: auditLoading } = useQuery({
    queryKey: ['audit-data'],
    queryFn: async () => {
      const res = await fetch(`${apiBase}/api/audit-data`)
      if (!res.ok) throw new Error('Failed to load audit data')
      return res.json()
    }
  })

  const { data: recommendationsData, isLoading: recLoading } = useQuery({
    queryKey: ['strategic-recommendations'],
    queryFn: async () => {
      const res = await fetch(`${apiBase}/api/strategic-recommendations`)
      if (!res.ok) {
        // Return mock data if API not available
        return generateMockRecommendations()
      }
      return res.json()
    }
  })

  const generateMockRecommendations = (): StrategicRecommendation[] => {
    return [
      {
        id: 'content-optimization',
        category: 'Content Strategy',
        title: 'Optimize Content for Cybersecurity Decision Makers',
        description: 'Enhance content messaging to better address cybersecurity concerns and compliance requirements across key pages.',
        priority: 'High',
        impact: 'High',
        effort: 'Medium',
        timeframe: 'Short-term',
        evidence: [
          'Multiple pages lack explicit cybersecurity messaging',
          'Generic corporate language fails to address specific security concerns',
          'Missing compliance and certification information'
        ],
        affectedPages: ['Homepage', 'Services', 'About Us', 'Industries'],
        personas: ['The Benelux Cybersecurity Decision Maker', 'The Technical Influencer'],
        businessValue: 'Improved conversion rates for cybersecurity-focused prospects and enhanced credibility in security markets',
        implementation: [
          'Audit current content for security-specific messaging',
          'Develop cybersecurity-focused content templates',
          'Add compliance certifications and security credentials',
          'Create security-focused case studies and testimonials'
        ],
        risks: ['Resource allocation', 'Content consistency challenges']
      },
      {
        id: 'trust-signals',
        category: 'Trust & Credibility',
        title: 'Strengthen Trust Signals Across Platform',
        description: 'Implement comprehensive trust signals including certifications, testimonials, and social proof to build credibility.',
        priority: 'High',
        impact: 'High',
        effort: 'Low',
        timeframe: 'Immediate',
        evidence: [
          'Missing security certifications on key pages',
          'Limited client testimonials and case studies',
          'Insufficient social proof elements'
        ],
        affectedPages: ['Homepage', 'Services', 'Case Studies'],
        personas: ['The Benelux Strategic Business Leader', 'The Benelux Cybersecurity Decision Maker'],
        businessValue: 'Increased user confidence and higher conversion rates through enhanced credibility',
        implementation: [
          'Add security certifications and compliance badges',
          'Implement client testimonial sections',
          'Display industry awards and recognition',
          'Add social proof elements (client logos, case studies)'
        ],
        risks: ['Verification of claims', 'Maintenance of current information']
      },
      {
        id: 'user-experience',
        category: 'User Experience',
        title: 'Improve Navigation and Information Architecture',
        description: 'Streamline user journey and improve findability of key information for different persona types.',
        priority: 'Medium',
        impact: 'Medium',
        effort: 'High',
        timeframe: 'Medium-term',
        evidence: [
          'Complex navigation structure creates friction',
          'Key information difficult to locate',
          'Poor mobile experience on several pages'
        ],
        affectedPages: ['Navigation', 'Services', 'Solutions', 'Contact'],
        personas: ['All Personas'],
        businessValue: 'Reduced bounce rates and improved user engagement leading to higher conversion',
        implementation: [
          'Conduct user journey mapping',
          'Simplify navigation structure',
          'Implement persona-based content paths',
          'Optimize mobile experience'
        ],
        risks: ['User confusion during transition', 'SEO impact from URL changes']
      }
    ]
  }

  const aggregateEvidence = (auditData: any[]): AggregatedEvidence[] => {
    if (!auditData || auditData.length === 0) return []

    const categories = ['Content Strategy', 'Trust & Credibility', 'User Experience', 'Technical Performance']
    
    return categories.map(category => {
      const relevantData = auditData.filter(item => 
        item.category === category || 
        (category === 'Content Strategy' && item.effective_copy_examples) ||
        (category === 'Trust & Credibility' && item.trust_credibility_assessment) ||
        (category === 'User Experience' && item.information_gaps)
      )

      const strongEvidence = relevantData
        .filter(item => item.effective_copy_examples)
        .map(item => item.effective_copy_examples)
        .filter(Boolean)

      const improvementAreas = relevantData
        .filter(item => item.ineffective_copy_examples)
        .map(item => item.ineffective_copy_examples)
        .filter(Boolean)

      const businessImpact = relevantData
        .filter(item => item.business_impact_analysis)
        .map(item => item.business_impact_analysis)
        .filter(Boolean)

      const trustIssues = relevantData
        .filter(item => item.trust_credibility_assessment)
        .map(item => item.trust_credibility_assessment)
        .filter(Boolean)

      return {
        category,
        evidenceCount: relevantData.length,
        strongEvidence,
        improvementAreas,
        businessImpact,
        trustIssues
      }
    })
  }

  const getFilteredRecommendations = () => {
    if (!recommendationsData) return []

    return recommendationsData.filter((rec: StrategicRecommendation) => {
      if (selectedCategory !== 'All' && rec.category !== selectedCategory) return false
      if (selectedPriority !== 'All' && rec.priority !== selectedPriority) return false
      if (selectedTimeframe !== 'All' && rec.timeframe !== selectedTimeframe) return false
      return true
    })
  }

  const getPriorityImpactMatrix = () => {
    if (!recommendationsData) return []

    const matrix = recommendationsData.map((rec: StrategicRecommendation) => ({
      x: rec.impact === 'High' ? 3 : rec.impact === 'Medium' ? 2 : 1,
      y: rec.priority === 'High' ? 3 : rec.priority === 'Medium' ? 2 : 1,
      text: rec.title,
      mode: 'markers+text',
      textposition: 'middle center',
      marker: {
        size: rec.effort === 'High' ? 20 : rec.effort === 'Medium' ? 15 : 10,
        color: rec.timeframe === 'Immediate' ? '#dc3545' : 
               rec.timeframe === 'Short-term' ? '#fd7e14' :
               rec.timeframe === 'Medium-term' ? '#ffc107' : '#28a745'
      }
    }))

    return matrix
  }

  const isLoading = auditLoading || recLoading

  if (isLoading) {
    return (
      <div className="page-container">
        <div className="main-header">
          <h1>🎯 Strategic Recommendations</h1>
          <p>Loading strategic analysis...</p>
        </div>
      </div>
    )
  }

  const filteredRecommendations = getFilteredRecommendations()
  const aggregatedEvidence = aggregateEvidence(auditData || [])
  const priorityMatrix = getPriorityImpactMatrix()

  return (
    <div className="page-container">
      {/* Header */}
      <div className="main-header">
        <h1>🎯 Strategic Recommendations</h1>
        <p>Evidence-based strategic recommendations for brand optimization and business growth</p>
      </div>

      {/* Executive Summary */}
      <div className="insights-box">
        <h2>📊 Executive Summary</h2>
        <div className="summary-grid" style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: '1rem' }}>
          <div className="metric-card">
            <div className="metric-value">{recommendationsData?.length || 0}</div>
            <div className="metric-label">Total Recommendations</div>
          </div>
          <div className="metric-card">
            <div className="metric-value">
              {recommendationsData?.filter((r: StrategicRecommendation) => r.priority === 'High').length || 0}
            </div>
            <div className="metric-label">High Priority</div>
          </div>
          <div className="metric-card">
            <div className="metric-value">
              {recommendationsData?.filter((r: StrategicRecommendation) => r.timeframe === 'Immediate').length || 0}
            </div>
            <div className="metric-label">Immediate Actions</div>
          </div>
          <div className="metric-card">
            <div className="metric-value">{aggregatedEvidence.length}</div>
            <div className="metric-label">Evidence Categories</div>
          </div>
        </div>
      </div>

      {/* Filters */}
      <div className="insights-box">
        <h2>🎛️ Filters</h2>
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: '1rem' }}>
          <div>
            <label style={{ display: 'block', marginBottom: '0.5rem', fontWeight: '600' }}>
              Category
            </label>
            <select 
              value={selectedCategory}
              onChange={(e) => setSelectedCategory(e.target.value)}
              style={{ width: '100%', padding: '0.5rem', borderRadius: '4px', border: '1px solid #D1D5DB' }}
            >
              <option value="All">All Categories</option>
              <option value="Content Strategy">Content Strategy</option>
              <option value="Trust & Credibility">Trust & Credibility</option>
              <option value="User Experience">User Experience</option>
              <option value="Technical Performance">Technical Performance</option>
            </select>
          </div>

          <div>
            <label style={{ display: 'block', marginBottom: '0.5rem', fontWeight: '600' }}>
              Priority
            </label>
            <select 
              value={selectedPriority}
              onChange={(e) => setSelectedPriority(e.target.value)}
              style={{ width: '100%', padding: '0.5rem', borderRadius: '4px', border: '1px solid #D1D5DB' }}
            >
              <option value="All">All Priorities</option>
              <option value="High">High Priority</option>
              <option value="Medium">Medium Priority</option>
              <option value="Low">Low Priority</option>
            </select>
          </div>

          <div>
            <label style={{ display: 'block', marginBottom: '0.5rem', fontWeight: '600' }}>
              Timeframe
            </label>
            <select 
              value={selectedTimeframe}
              onChange={(e) => setSelectedTimeframe(e.target.value)}
              style={{ width: '100%', padding: '0.5rem', borderRadius: '4px', border: '1px solid #D1D5DB' }}
            >
              <option value="All">All Timeframes</option>
              <option value="Immediate">Immediate</option>
              <option value="Short-term">Short-term</option>
              <option value="Medium-term">Medium-term</option>
              <option value="Long-term">Long-term</option>
            </select>
          </div>

          <div>
            <label style={{ display: 'block', marginBottom: '0.5rem', fontWeight: '600' }}>
              View Mode
            </label>
            <select 
              value={viewMode}
              onChange={(e) => setViewMode(e.target.value)}
              style={{ width: '100%', padding: '0.5rem', borderRadius: '4px', border: '1px solid #D1D5DB' }}
            >
              <option value="recommendations">Recommendations</option>
              <option value="evidence">Evidence Analysis</option>
              <option value="matrix">Priority Matrix</option>
            </select>
          </div>
        </div>
      </div>

      {/* Content based on view mode */}
      {viewMode === 'recommendations' && (
        <div className="insights-box">
          <h2>📋 Strategic Recommendations</h2>
          <div className="recommendations-grid" style={{ display: 'grid', gap: '1.5rem' }}>
            {filteredRecommendations.map((rec: StrategicRecommendation) => (
              <div key={rec.id} className="recommendation-card" style={{ 
                border: '1px solid #D1D5DB', 
                borderRadius: '8px', 
                padding: '1.5rem',
                backgroundColor: rec.priority === 'High' ? '#fef2f2' : rec.priority === 'Medium' ? '#fffbeb' : '#f0fdf4'
              }}>
                <div className="recommendation-header" style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'start', marginBottom: '1rem' }}>
                  <h3 style={{ margin: 0, color: '#1f2937' }}>{rec.title}</h3>
                  <div className="recommendation-badges" style={{ display: 'flex', gap: '0.5rem' }}>
                    <span className={`badge priority-${rec.priority.toLowerCase()}`} style={{ 
                      padding: '0.25rem 0.5rem', 
                      borderRadius: '4px', 
                      fontSize: '0.75rem',
                      fontWeight: '600',
                      backgroundColor: rec.priority === 'High' ? '#dc3545' : rec.priority === 'Medium' ? '#fd7e14' : '#28a745',
                      color: 'white'
                    }}>
                      {rec.priority} Priority
                    </span>
                    <span className="badge timeframe" style={{ 
                      padding: '0.25rem 0.5rem', 
                      borderRadius: '4px', 
                      fontSize: '0.75rem',
                      fontWeight: '600',
                      backgroundColor: '#6c757d',
                      color: 'white'
                    }}>
                      {rec.timeframe}
                    </span>
                  </div>
                </div>

                <p style={{ color: '#4b5563', marginBottom: '1rem' }}>{rec.description}</p>

                <div className="recommendation-metrics" style={{ display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)', gap: '1rem', marginBottom: '1rem' }}>
                  <div className="metric">
                    <strong>Impact:</strong> {rec.impact}
                  </div>
                  <div className="metric">
                    <strong>Effort:</strong> {rec.effort}
                  </div>
                  <div className="metric">
                    <strong>Category:</strong> {rec.category}
                  </div>
                </div>

                <div className="recommendation-details" style={{ marginBottom: '1rem' }}>
                  <h4>💼 Business Value</h4>
                  <p style={{ color: '#4b5563' }}>{rec.businessValue}</p>
                </div>

                <div className="recommendation-evidence" style={{ marginBottom: '1rem' }}>
                  <EvidenceDisplay
                    evidence={rec.evidence.map(e => ({ type: 'evidence' as const, content: e }))}
                    title="Supporting Evidence"
                    collapsible={true}
                    defaultExpanded={false}
                  />
                </div>

                <div className="recommendation-implementation">
                  <h4>🔧 Implementation Steps</h4>
                  <ul style={{ paddingLeft: '1.5rem' }}>
                    {rec.implementation.map((step, idx) => (
                      <li key={idx} style={{ marginBottom: '0.5rem' }}>{step}</li>
                    ))}
                  </ul>
                </div>

                {rec.risks.length > 0 && (
                  <div className="recommendation-risks" style={{ marginTop: '1rem' }}>
                    <h4>⚠️ Risks & Considerations</h4>
                    <ul style={{ paddingLeft: '1.5rem' }}>
                      {rec.risks.map((risk, idx) => (
                        <li key={idx} style={{ marginBottom: '0.5rem', color: '#dc3545' }}>{risk}</li>
                      ))}
                    </ul>
                  </div>
                )}
              </div>
            ))}
          </div>
        </div>
      )}

      {viewMode === 'evidence' && (
        <div className="insights-box">
          <h2>🔍 Evidence Analysis</h2>
          {auditData && auditData.length > 0 ? (
            <EvidenceBrowser
              data={auditData}
              evidenceColumns={[
                'evidence',
                'effective_copy_examples',
                'ineffective_copy_examples',
                'trust_credibility_assessment',
                'business_impact_analysis',
                'information_gaps'
              ]}
            />
          ) : (
            <div className="no-evidence">
              <p>No audit data available for evidence analysis.</p>
            </div>
          )}
        </div>
      )}

      {viewMode === 'matrix' && (
        <div className="insights-box">
          <h2>📊 Priority Impact Matrix</h2>
          <div className="matrix-container">
            <PlotlyChart
              data={priorityMatrix}
              layout={{
                title: 'Recommendations by Priority vs Impact',
                xaxis: { 
                  title: 'Impact',
                  tickvals: [1, 2, 3],
                  ticktext: ['Low', 'Medium', 'High']
                },
                yaxis: { 
                  title: 'Priority',
                  tickvals: [1, 2, 3],
                  ticktext: ['Low', 'Medium', 'High']
                },
                height: 500
              }}
            />
          </div>
          <div className="matrix-legend" style={{ marginTop: '1rem' }}>
            <h4>Legend:</h4>
            <p><strong>Size:</strong> Implementation effort (larger = more effort)</p>
            <p><strong>Color:</strong> Timeframe (Red = Immediate, Orange = Short-term, Yellow = Medium-term, Green = Long-term)</p>
          </div>
        </div>
      )}
    </div>
  )
}

export default StrategicRecommendations 