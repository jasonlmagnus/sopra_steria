import { useQuery } from '@tanstack/react-query';
import { useEffect } from 'react';
import { ExpandableCard, PageContainer, PageHeader } from '../components';
import PagesList from './PagesList';
import { useFilters } from '../hooks/useFilters';
import { FilterSystem } from '../components/FilterSystem';
import type { FilterConfig } from '../types/filters';

const apiBase = import.meta.env.VITE_API_URL || 'http://localhost:3000';

const dashboardFilters: FilterConfig[] = [
  {
    name: 'tier',
    label: 'Focus on Content Tier:',
    type: 'select',
    defaultValue: 'All Tiers',
    options: [
      { value: 'All Tiers', label: 'All Tiers' },
      { value: 'Tier 1 (Strategic)', label: 'Tier 1 (Strategic)' },
      { value: 'Tier 2 (Tactical)', label: 'Tier 2 (Tactical)' },
      { value: 'Tier 3 (Operational)', label: 'Tier 3 (Operational)' },
    ],
  },
];

function ExecutiveDashboard() {
  const { filters, setAllFilters } = useFilters();

  useEffect(() => {
    const defaultFilters = dashboardFilters.reduce((acc, f) => {
      acc[f.name] = f.defaultValue;
      return acc;
    }, {} as { [key: string]: any });
    setAllFilters(defaultFilters);
  }, [setAllFilters]);
  
  const { data, isLoading, error } = useQuery({
    queryKey: ['summary'],
    queryFn: async () => {
      const res = await fetch(`${apiBase}/api/summary`)
      if (!res.ok) throw new Error('Failed to load summary')
      return res.json()
    }
  })

  const { data: oppData } = useQuery({
    queryKey: ['opportunities'],
    queryFn: async () => {
      const res = await fetch(`${apiBase}/api/opportunities?limit=3`)
      if (!res.ok) throw new Error('Failed to load opportunities')
      return res.json()
    }
  })

  const { data: strategicData } = useQuery({
    queryKey: ['strategic-assessment', filters.tier],
    queryFn: async () => {
      const tierParam = filters.tier && filters.tier !== 'All Tiers' ? `?tier=${encodeURIComponent(filters.tier)}` : '';
      const res = await fetch(`${apiBase}/api/strategic-assessment${tierParam}`);
      if (!res.ok) throw new Error('Failed to load strategic assessment');
      return res.json();
    },
    enabled: !!filters.tier,
  });

  const { data: successData } = useQuery({
    queryKey: ['success-stories'],
    queryFn: async () => {
      const res = await fetch(`${apiBase}/api/success-stories?limit=5&min_score=7.5`)
      if (!res.ok) throw new Error('Failed to load success stories')
      return res.json()
    }
  })

  if (isLoading) return (
    <div className="container--layout">
      <PageHeader
        title="🎯 Brand Health Command Center"
        description="Loading brand health metrics..."
      />
    </div>
  )
  if (error) return (
    <div className="container--layout">
      <PageHeader
        title="🎯 Brand Health Command Center"
        description="Error loading dashboard data"
      />
    </div>
  )

  const brand = data?.brand_health || {}
  const metrics = data?.key_metrics || {}
  const sentiment = data?.sentiment || {}
  const conversion = data?.conversion || {}
  const recs = Array.isArray(data?.recommendations) ? data.recommendations : []
  const opps = Array.isArray(oppData?.opportunities) ? oppData.opportunities : []
  const successStories = Array.isArray(successData?.success_stories) ? successData.success_stories : []

  // Use real strategic assessment data when available
  const getDistinctivenessScore = () => {
    if (strategicData?.distinctiveness?.score !== undefined) {
      return strategicData.distinctiveness.score
    }
    // Fallback calculation if API fails
    const baseScore = (brand.raw_score || 0) * 0.6 + (sentiment.net_sentiment || 0) * 0.4
    return Math.min(Math.max(baseScore, 0), 10)
  }

  const getResonanceScore = () => {
    if (strategicData?.resonance?.net_sentiment !== undefined) {
      return strategicData.resonance.net_sentiment / 10
    }
    // Fallback: use existing sentiment data converted to 0-10 scale
    return Math.max((sentiment.net_sentiment || 0) / 10, 0)
  }

  const getConversionScore = () => {
    if (strategicData?.conversion?.score !== undefined) {
      return strategicData.conversion.score
    }
    // Fallback: use existing conversion data
    return conversion.raw_score || 0
  }

  const getScoreStatus = (score: number) => {
    if (score >= 7.0) return "HIGH"
    if (score >= 4.0) return "MODERATE"
    return "LOW"
  }

  return (
    <PageContainer title="🎯 Brand Health Command Center">
      <PageHeader
        title="🎯 Brand Health Command Center"
        description="30-second strategic marketing decision engine for executives"
      />

      {/* Brand Health Overview */}
      <h2 className="heading--section">Brand Health Overview</h2>
      <div className="container--layout">
        <div className={`container--section ${brand.raw_score < 4 ? 'critical' : brand.raw_score < 6 ? 'warning' : brand.raw_score < 8 ? 'fair' : ''}`}>
          <div className={`text--display ${brand.raw_score < 4 ? 'status-critical' : brand.raw_score < 6 ? 'status-fair' : brand.raw_score < 8 ? 'status-good' : 'status-excellent'}`}>
            {brand.raw_score || 0}/10
          </div>
          <div className="text--display">Overall Brand Health - {brand.status || 'Unknown'}</div>
        </div>

        <div className={`container--section text--display > 0 ? 'critical' : ''}`}>
          <div className="text--display">{metrics.critical_issues || 0}</div>
          <div className="text--display">Critical Issues</div>
        </div>

        <div className="container--section">
          <div className="text--display">{metrics.quick_wins || 0}</div>
          <div className="text--display">Quick Wins</div>
        </div>

        <div className="container--section">
          <div className="text--display">{metrics.success_pages || 0}</div>
          <div className="text--display">Success Pages</div>
        </div>
      </div>

      {/* Strategic Focus */}
      <h3 className="heading--subsection">🎯 Strategic Focus</h3>
      <FilterSystem config={dashboardFilters} data={{}} />
      
      {/* Strategic Brand Assessment */}
      <h2 className="heading--section">Strategic Brand Assessment</h2>
      <div className="container--layout">
        
        {/* Are we distinct? */}
        <div className="container--section">
          <h4 className="heading--subsection">Are we distinct?</h4>
          {(() => {
            const score = getDistinctivenessScore()
            const status = getScoreStatus(score)
            
            return (
              <div className="text--display">
                <div className="text--display text--emphasis">{score.toFixed(1)}/10</div>
                <div className="text--body text--emphasis">{status}</div>
                <div className="text--body" style={{ marginTop: '0.5rem' }}>
                  <strong>How we measure:</strong><br/>
                  First impression uniqueness (40%)<br/>
                  Brand visibility (30%)<br/>
                  Distinctive language tone (30%)
                </div>
              </div>
            )
          })()}
        </div>

        {/* Are we resonating? */}
        <div className="container--section">
          <h4 className="heading--subsection">Are we resonating?</h4>
          {(() => {
            const score = getResonanceScore()
            const status = getScoreStatus(score)
            
            return (
              <div className="container--layout text--display">
                <div className="text--display text--emphasis">{score.toFixed(1)}/10</div>
                <div className="text--body text--emphasis">{status}</div>
                <div className="text--body text--body" style={{ marginTop: '0.5rem' }}>
                  <strong>How we measure:</strong><br/>
                  User sentiment scores (50%)<br/>
                  Content engagement (30%)<br/>
                  Success rate (20%)
                </div>
              </div>
            )
          })()}
        </div>

        {/* Are we converting? */}
        <div className="container--section">
          <h4 className="heading--subsection">Are we converting?</h4>
          {(() => {
            const score = getConversionScore()
            const status = getScoreStatus(score)
            
            return (
              <div className="container--layout text--display">
                <div className="text--display text--emphasis">{score.toFixed(1)}/10</div>
                <div className="text--body text--emphasis">{status}</div>
                <div className="text--body text--body" style={{ marginTop: '0.5rem' }}>
                  <strong>How we measure:</strong><br/>
                  Conversion likelihood (50%)<br/>
                  Trust & credibility (30%)<br/>
                  Performance metrics (20%)
                </div>
              </div>
            )
          })()}
        </div>
      </div>

      {/* Top 3 Improvement Opportunities */}
      <h2 className="heading--section">🎯 Top 3 Improvement Opportunities</h2>
      <p className="text--body text--body">*For comprehensive analysis, visit the **Opportunity & Impact** tab*</p>
      
      {opps.length > 0 ? (
        <div className="container--section">
          {opps.map((opp: any) => (
            <ExpandableCard key={opp.id} title={`${(opp.priority_score || 0).toFixed(1)}/10 Priority - ${opp.title}`}>
              <p className="text--body">{opp.description}</p>
              <div className="text--body" style={{ marginTop: '1rem' }}>
                <strong>Page:</strong> {opp.page_id}<br/>
                <strong>Persona:</strong> {opp.persona}<br/>
                <strong>Evidence:</strong> <span className="text-gray-600 italic">{opp.evidence}</span>
              </div>
            </ExpandableCard>
          ))}
        </div>
      ) : (
        <p className="text--body">No improvement opportunities found.</p>
      )}

      {/* Top 5 Success Stories */}
      <h2 className="heading--section">🏆 Top 5 Success Stories</h2>
      <p className="text--body text--body">*For comprehensive analysis, visit the **Success Library** tab*</p>
      
      {successStories.length > 0 ? (
        <div className="container--section">
          {successStories.map((story: any) => (
            <ExpandableCard key={story.id} title={`${story.score.toFixed(1)}/10 - ${story.page_id}`}>
              <p className="text--body">{story.description}</p>
              <div className="text--body" style={{ marginTop: '1rem' }}>
                <strong>Persona:</strong> {story.persona}<br/>
                <strong>URL:</strong> <a href={story.url} target="_blank" rel="noopener noreferrer">{story.url}</a>
              </div>
            </ExpandableCard>
          ))}
        </div>
      ) : (
        <p className="text--body">No success stories found.</p>
      )}

      {/* Strategic Recommendations */}
      {recs.length > 0 && (
        <div className="container--section">
          <h2 className="heading--section">💡 Strategic Recommendations</h2>
          <p className="text--body text--body">*AI-generated action priorities based on current brand health*</p>
          
          <div className="container--section">
            {recs.map((rec: any, i: number) => (
              <div key={i} className="container--section">
                <div className="container--layout">
                  <div className="container--layout">
                    <strong>{i + 1}.</strong> {rec}
                  </div>
                  <div className="container--layout">
                    {rec.toLowerCase().includes('critical pages') || rec.toLowerCase().includes('scoring below') ? (
                      <button className="button--action">🔍 View Critical Pages</button>
                    ) : rec.toLowerCase().includes('quick wins') || rec.toLowerCase().includes('immediate impact') ? (
                      <button className="button--action">⚡ See Quick Wins</button>
                    ) : rec.toLowerCase().includes('persona') ? (
                      <button className="button--action">👥 Analyze Persona</button>
                    ) : rec.toLowerCase().includes('improvements') || rec.toLowerCase().includes('opportunities') ? (
                      <button className="button--action">💡 Get Action Plan</button>
                    ) : (
                      <button className="button--action">📊 Explore Analysis</button>
                    )}
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Page Performance Overview */}
      <h2 className="heading--section">📄 Page Performance Overview</h2>
      <p className="text--body text--body">*Quick visual overview of brand scores across all audited pages*</p>
      
      <div className="container--section">
        <PagesList />
      </div>

      {/* Deep-Dive Analysis Navigation */}
      <h2 className="heading--section">🧭 Deep-Dive Analysis</h2>
      <p className="text--body"><strong>Need more details?</strong> Visit these specialized tabs for comprehensive analysis:</p>
      
      <div className="container--layout">
        <div className="container--layout">
          <strong>📊 Analysis Tabs:</strong>
          <ul className="text--body">
            <li>• <strong>👥 Persona Insights</strong> - How different personas experience your brand</li>
            <li>• <strong>📊 Content Matrix</strong> - Detailed performance by content type and tier</li>
          </ul>
        </div>
        
        <div className="container--layout">
          <strong>🎯 Action Tabs:</strong>
          <ul className="text--body">
            <li>• <strong>💡 Opportunity & Impact</strong> - Comprehensive improvement roadmap</li>
            <li>• <strong>🌟 Success Library</strong> - Pattern analysis and replication guides</li>
          </ul>
        </div>
        
        <div className="container--layout">
          <strong>📋 Data & Tools:</strong>
          <ul className="text--body">
            <li>• <strong>📋 Reports & Export</strong> - Custom reports and data exports</li>
            <li>• <strong>🚀 Run Audit</strong> - Generate fresh audit data</li>
          </ul>
        </div>
      </div>
    </PageContainer>
  )
}

export default ExecutiveDashboard
