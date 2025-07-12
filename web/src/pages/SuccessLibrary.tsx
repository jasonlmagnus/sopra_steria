import { useEffect } from 'react';
import { useQuery } from '@tanstack/react-query';
import { useFilters } from '../hooks/useFilters';
import { Banner, BarChart, PieChart, StandardCard, PageContainer } from '../components';
import { FilterSystem } from '../components/FilterSystem';
import type { FilterConfig } from '../types/filters';
import '../styles/dashboard.css';
import '../styles/utilities.css';

const apiBase = import.meta.env.VITE_API_URL || 'http://localhost:3000'

interface SuccessStory {
  id: string;
  title: string;
  score: number;
  tier: string;
  persona: string;
  url: string;
  percentile: number;
  sentiment: string;
  engagement: string;
  conversion: string;
  effectiveExamples: string;
  ineffectiveExamples: string;
  trustAssessment: string;
  businessImpact: string;
  evidence: string;
  personaQuotes: string[];
}

interface PatternData {
  tier: string;
  avgScore: number;
  count: number;
}

interface EvidenceItem {
  type: string;
  content: string;
  pageTitle: string;
  score: number;
}

interface ReplicationTemplate {
  tier: string;
  avgScore: number;
  keyElements: string[];
}

interface SuccessLibraryData {
  successStories: SuccessStory[];
  overview: {
    totalPages: number;
    successPages: number;
    successRate: number;
    avgScore: number;
    excellent: number;
    veryGood: number;
    good: number;
  };
  patternData: PatternData[];
  evidenceItems: EvidenceItem[];
  replicationTemplates: ReplicationTemplate[];
  personas: string[];
  tiers: string[];
}

const successLibraryFilters: FilterConfig[] = [
  { name: 'persona', label: '👤 Persona Focus', type: 'select', defaultValue: 'All' },
  { name: 'tier', label: '🏗️ Content Tier', type: 'select', defaultValue: 'All' },
  {
    name: 'successThreshold',
    label: '⭐ Success Threshold',
    type: 'range',
    defaultValue: 7.5,
    min: 5.0,
    max: 10.0,
    step: 0.1,
  },
  {
    name: 'maxStories',
    label: '📊 Max Success Stories',
    type: 'range',
    defaultValue: 10,
    min: 5,
    max: 50,
    step: 1,
  },
  {
    name: 'evidenceType',
    label: '🔍 Evidence Type',
    type: 'select',
    defaultValue: 'All',
    options: [
      { value: 'All', label: 'All' },
      { value: 'Effective Copy', label: 'Effective Copy' },
      { value: 'Ineffective Copy', label: 'Ineffective Copy' },
      { value: 'Trust Signal', label: 'Trust Signal' },
    ],
  },
  { name: 'searchTerm', label: '🔎 Search Term', type: 'text', defaultValue: '' },
];


const SuccessLibrary: React.FC = () => {
  const { filters, setAllFilters } = useFilters();

  useEffect(() => {
    const defaultFilters = successLibraryFilters.reduce((acc, f) => {
      acc[f.name] = f.defaultValue;
      return acc;
    }, {} as { [key: string]: any });
    setAllFilters(defaultFilters);
  }, [setAllFilters]);
  
  // Fetch success library data
  const { data: successData, isLoading, error } = useQuery<SuccessLibraryData>({
    queryKey: ['success-library', filters],
    queryFn: async () => {
      const params = new URLSearchParams(filters);
      const response = await fetch(`${apiBase}/api/success-library?${params}`);
      if (!response.ok) throw new Error('Failed to fetch success library data');
      return response.json();
    },
    enabled: Object.keys(filters).length > 0,
    staleTime: 5 * 60 * 1000,
  });

  const successStories = successData?.successStories || [];
  const overview = successData?.overview || {
    totalPages: 0,
    successPages: 0,
    successRate: 0,
    avgScore: 0,
    excellent: 0,
    veryGood: 0,
    good: 0
  };
  const patternData = successData?.patternData || [];
  const evidenceItems = successData?.evidenceItems || [];
  const replicationTemplates = successData?.replicationTemplates || [];
  
  const availablePersonas = successData?.personas ? 
    [{ value: 'All', label: 'All Personas' }, ...successData.personas.map((p: string) => ({ value: p, label: p }))]
    : [{ value: 'All', label: 'All Personas' }];

  const availableTiers = successData?.tiers ?
    [{ value: 'All', label: 'All Tiers' }, ...successData.tiers.map((t: string) => ({ value: t, label: t }))]
    : [{ value: 'All', label: 'All Tiers' }];

  const dynamicFilterData = {
    personaOptions: availablePersonas,
    tierOptions: availableTiers,
  };

  const scoreDistributionScores = successStories.map(s => s.score);

  const tierSuccessCounts = patternData.map(p => p.count);
  const tierSuccessLabels = patternData.map(p => p.tier);

  const getExcellenceLevel = (score: number) => {
    if (score >= 9.0) return { level: '🏆 EXCELLENT', class: 'success-excellent' };
    if (score >= 8.0) return { level: '⭐ VERY GOOD', class: 'success-good' };
    if (score >= 7.5) return { level: '✅ GOOD', class: 'success-card' };
    return { level: '📈 IMPROVING', class: 'success-improving' };
  };

  const getSentimentColor = (sentiment: string) => {
    switch (sentiment) {
      case 'Positive': return '🟢';
      case 'Neutral': return '🟡';
      case 'Negative': return '🔴';
      default: return '⚪';
    }
  };

  const getEngagementColor = (engagement: string) => {
    switch (engagement) {
      case 'High': return '🟢';
      case 'Medium': return '🟡';
      case 'Low': return '🔴';
      default: return '⚪';
    }
  };

  const getConversionColor = (conversion: string) => {
    switch (conversion) {
      case 'High': return '🟢';
      case 'Medium': return '🟡';
      case 'Low': return '🔴';
      default: return '⚪';
    }
  };

  if (isLoading) {
    return (
      <div className="container--content">
        <div className="loading--state">🔄 Loading Success Library...</div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="container--content">
        <Banner
          type="error"
          message={`❌ Error loading success library data: ${error.message}`}
        />
      </div>
    );
  }

  return (
    <PageContainer title="🌟 Success Library">
      <p className="text--body">Best practice examples and high-performing content showcase</p>

      {/* Success Analysis Controls */}
      <FilterSystem config={successLibraryFilters} data={dynamicFilterData} />

      {/* Success Overview */}
      <div className="container--section">
        <h2 className="heading--section">📊 Success Overview</h2>
        
        {overview.successPages === 0 ? (
          <Banner
            type="warning"
            message={
              <>
                <p className="text--body">⚠️ No success stories match the selected criteria.</p>
                <p className="text--body">Try adjusting the success threshold or filters.</p>
              </>
            }
          />
        ) : (
          <>
            <div className="container--layout">
              <StandardCard 
                label="Total Pages" 
                value={overview.totalPages.toString()} 
                variant="metric"
              />
              <StandardCard 
                label="Success Pages" 
                value={overview.successPages.toString()} 
                variant="success"
              />
              <StandardCard 
                label="Success Rate" 
                value={`${overview.successRate.toFixed(1)}%`} 
                variant="success"
              />
              <StandardCard 
                label="Avg Success Score" 
                value={`${overview.avgScore.toFixed(1)}/10`} 
                variant="success"
              />
            </div>

            <div className="container--layout">
              <Banner
                message={
                  <>
                    <div className="text--display">🏆 {overview.excellent}</div>
                    <div className="text--display">Excellent (≥9.0)</div>
                  </>
                }
              />
              <Banner
                message={
                  <>
                    <div className="text--display">⭐ {overview.veryGood}</div>
                    <div className="text--display">Very Good (8.0-9.0)</div>
                  </>
                }
              />
              <div className="container--section">
                <div className="text--display">✅ {overview.good}</div>
                <div className="text--display">Good (7.5-8.0)</div>
              </div>
            </div>

            {successStories.length > 0 && (
              <div className="container--grid">
                <BarChart
                  x={scoreDistributionScores}
                  y={Array.from({ length: scoreDistributionScores.length }, (_, i) => i + 1)}
                  title="Success Score Distribution"
                />
                {patternData.length > 0 && (
                  <PieChart
                    values={tierSuccessCounts}
                    labels={tierSuccessLabels}
                    title="Success Stories by Content Tier"
                  />
                )}
              </div>
            )}
          </>
        )}
      </div>

      {/* Detailed Success Stories */}
      <div className="container--section">
        <h2>🏆 Detailed Success Stories</h2>
        
        {successStories.length === 0 ? (
          <Banner
            type="info"
            message={
              <>
                <p>🎉 No success stories found above {filters.successThreshold.toFixed(1)} with current filters.</p>
                <p>Try lowering the success threshold or adjusting your filters.</p>
              </>
            }
          />
        ) : (
          <Banner
            type="success"
            message={
              <>
                🎉 Found {successStories.length} success stories above {filters.successThreshold.toFixed(1)}
                
                {successStories.map((story, index) => {
                  const excellence = getExcellenceLevel(story.score);
                  return (
                    <div key={story.id} className="container--card">
                      <div className="story-header">
                        <h3>#{index + 1} - {story.title}</h3>
                        <div className={`excellence-badge ${excellence.class}`}>
                          {excellence.level}
                        </div>
                      </div>

                      <div className="container--grid container--grid spacing--sm">
                        <StandardCard
                          title="Success Score"
                          variant="metric"
                          status={story.score >= 9 ? "excellent" : story.score >= 8 ? "good" : "warning"}
                        >
                          <div className="text--display">{story.score.toFixed(1)}/10</div>
                        </StandardCard>
                        <StandardCard
                          title="Content Tier"
                          variant="metric"
                          status="good"
                        >
                          <div className="text--display">{story.tier}</div>
                        </StandardCard>
                        <StandardCard
                          title="Persona"
                          variant="metric"
                          status="good"
                        >
                          <div className="text--display">{story.persona}</div>
                        </StandardCard>
                        <StandardCard
                          title="Percentile"
                          variant="metric"
                          status="excellent"
                        >
                          <div className="text--display">{story.percentile}th</div>
                        </StandardCard>
                      </div>

                      <div className="evidence--content">
                        <h4>📋 Success Evidence & Analysis</h4>
                        
                        <div className="container--grid container--grid spacing--sm">
                          <StandardCard
                            title={`${getSentimentColor(story.sentiment)} Score`}
                            variant="metric"
                            status={story.score >= 9 ? "excellent" : story.score >= 8 ? "good" : "warning"}
                          >
                            <div className="text--display">{story.score.toFixed(1)}/10</div>
                          </StandardCard>
                          <StandardCard
                            title={`${getEngagementColor(story.engagement)} Tier`}
                            variant="metric"
                            status="good"
                          >
                            <div className="text--display">{story.tier}</div>
                          </StandardCard>
                          <StandardCard
                            title={`${getConversionColor(story.conversion)} Percentile`}
                            variant="metric"
                            status="excellent"
                          >
                            <div className="text--display">{story.percentile}th</div>
                          </StandardCard>
                        </div>

                        <div className="container--grid">
                          <div className="evidence--content badge--status">
                            <h5>✅ What's Working Exceptionally Well:</h5>
                            <div className="evidence--content">
                              {story.personaQuotes.length > 0 && (
                                <div className="persona--content">
                                  <h6>💬 Persona Voice:</h6>
                                  {story.personaQuotes.map((quote, i) => (
                                    <div key={i} className="persona--content">
                                      <em>"{quote}"</em>
                                    </div>
                                  ))}
                                </div>
                              )}
                              {story.effectiveExamples && (
                                <div className="container--misc">
                                  <h6>📋 Full Success Analysis:</h6>
                                  <p><em>{story.effectiveExamples}</em></p>
                                </div>
                              )}
                            </div>
                          </div>
                          
                          <Banner
                            type="warning"
                            message={
                              <>
                                <h5>⚠️ Areas for Enhancement:</h5>
                                <div className="evidence--content">
                                  <p><em>{story.ineffectiveExamples || 'Even successful pages can be further optimized'}</em></p>
                                </div>
                              </>
                            }
                          />
                        </div>

                        {story.trustAssessment && (
                          <div className="container--misc">
                            <h5>🔒 Trust & Credibility Strengths:</h5>
                            <p>{story.trustAssessment}</p>
                          </div>
                        )}

                        {story.businessImpact && (
                          <div className="container--misc">
                            <h5>💼 Business Impact & Value:</h5>
                            <p>{story.businessImpact}</p>
                          </div>
                        )}

                        {story.evidence && (
                          <div className="evidence--content">
                            <h5>🔍 Additional Success Factors:</h5>
                            <p>{story.evidence}</p>
                          </div>
                        )}

                        <div className="story-url">
                          <strong>🔗 URL:</strong> <a href={story.url} target="_blank" rel="noopener noreferrer">{story.url}</a>
                        </div>

                        <div className="button-group">
                          <button className="button button--secondary">📋 Create Template</button>
                          <button className="button button--secondary">🔍 Analyze Pattern</button>
                          <button className="button button--secondary">📊 Compare Similar</button>
                        </div>
                      </div>
                    </div>
                  );
                })}
              </>
            }
          />
        )}
      </div>

      {/* Success Pattern Analysis */}
      <div className="container--section">
        <h2 className="heading--section">🔍 Success Pattern Analysis</h2>
        
        {patternData.length === 0 ? (
          <Banner
            type="info"
            message={<p className="text--body">📊 No pattern data available for the selected criteria.</p>}
          />
        ) : (
          <div className="container--layout">
            <h3 className="heading--subsection">🏗️ Success Patterns by Content Tier</h3>
            <div className="container--layout">
              {patternData.map((pattern) => (
                <div key={pattern.tier} className="container--section">
                  <h4 className="heading--subsection">🏗️ {pattern.tier} Content Pattern</h4>
                  <p className="text--body">Average Success Score: <span className="text--display">{pattern.avgScore.toFixed(1)}/10</span></p>
                  <p className="text--body">Success Stories: <span className="text--display">{pattern.count}</span> pages</p>
                  <span className="text--display">Tier Pattern</span>
                </div>
              ))}
            </div>
          </div>
        )}
      </div>

      {/* Evidence Browser */}
      <div className="container--section">
        <h2 className="heading--section">🔍 Evidence Browser</h2>
        
        <div className="container--layout">
          <div className="container--section">
            <label className="label--form">📋 Evidence Type</label>
            <select value={filters.evidenceType} onChange={(e) => setAllFilters({ ...filters, evidenceType: e.target.value })} className="select--form">
              <option value="All">All</option>
              <option value="Copy Examples">Copy Examples</option>
              <option value="Design Elements">Design Elements</option>
              <option value="User Feedback">User Feedback</option>
              <option value="Performance Data">Performance Data</option>
              <option value="Trust Assessment">Trust Assessment</option>
            </select>
          </div>
          
          <div className="container--section">
            <label className="label--form">🔍 Search Evidence</label>
            <input
              type="text"
              value={filters.searchTerm}
              onChange={(e) => setAllFilters({ ...filters, searchTerm: e.target.value })}
              placeholder="Search for specific words or phrases..."
              className="input--form"
            />
          </div>
        </div>

        <div className="container--section">
          <h3 className="heading--subsection">📋 Evidence Results</h3>
          {evidenceItems.length > 0 ? (
            evidenceItems.map((item, index) => (
              <div key={index} className="container--section">
                <div className="container--section">
                  <h4 className="heading--subsection">📋 {item.pageTitle} - Score: <span className="text--display">{item.score.toFixed(1)}</span></h4>
                </div>
                <div className="container--section">
                  <strong className="text--display">{item.type}:</strong>
                  <div className="container--layout">
                    <span className="text--body">{item.content}</span>
                    <div className="button--action" style={{ display: 'inline-block', marginLeft: '1rem' }}>📋 Copy</div>
                  </div>
                </div>
              </div>
            ))
          ) : (
            <p className="text--body">🔍 No evidence found matching the selected criteria. Try adjusting the filters.</p>
          )}
        </div>
      </div>

      {/* Success Replication Guide */}
      <div className="container--section">
        <h2 className="heading--section">🔄 Success Replication Guide</h2>
        
        <div className="container--section">
          <h3 className="heading--subsection">📋 Replication Templates</h3>
          <div className="container--layout">
            {replicationTemplates.map((template) => (
              <div key={template.tier} className="card">
                <h3 className="heading--card">Replication Template: {template.tier} (Avg Score: {template.avgScore.toFixed(1)})</h3>
                <p className="text--body">Key elements for success in this tier:</p>
                <ul>
                  {template.keyElements.map((element, i) => (
                    <li key={i}>{element}</li>
                  ))}
                </ul>
                <div className="button-group" style={{ marginTop: '1rem' }}>
                  <button className="button button--secondary">📋 Create Template</button>
                  <button className="button button--secondary">🔍 Analyze Pattern</button>
                  <button className="button button--secondary">📊 Compare Similar</button>
                </div>
              </div>
            ))}
          </div>
        </div>

        <div className="container--section">
          <h3 className="heading--subsection">✅ Success Checklist</h3>
          <div className="container--section">
            <h4 className="heading--subsection">🎯 Essential Success Criteria</h4>
            <div className="container--layout">
              <div className="text--body">☐ <strong>Clear Value Proposition</strong> (Target: 8.5/10)</div>
              <div className="text--body">☐ <strong>Strong Headlines</strong> (Target: 8.3/10)</div>
              <div className="text--body">☐ <strong>Compelling Content</strong> (Target: 8.7/10)</div>
              <div className="text--body">☐ <strong>Trust Signals</strong> (Target: 8.4/10)</div>
              <div className="text--body">☐ <strong>Clear Call-to-Action</strong> (Target: 8.1/10)</div>
            </div>
            <div className="container--section">
              <h4 className="heading--subsection">📋 How to Use This Checklist</h4>
              <ol className="text--body">
                <li>Review each criteria for your content</li>
                <li>Score your content against each criteria</li>
                <li>Focus on criteria below the target scores</li>
                <li>Use success story examples as inspiration</li>
                <li>Test and iterate based on results</li>
              </ol>
            </div>
          </div>
        </div>

        <div className="container--section">
          <h3 className="heading--subsection">🗺️ Implementation Roadmap</h3>
          <div className="container--layout">
            <Banner
              type="success"
              className="container--card container--section"
              message={
                <>
                  <h4 className="text--display">Phase 1: Analysis (Week 1)</h4>
                  <ul className="text--body">
                    <li>Analyze top 3 success stories in detail</li>
                    <li>Identify common patterns and elements</li>
                    <li>Document key success criteria</li>
                    <li>Create pattern templates</li>
                  </ul>
                </>
              }
            />
            <Banner
              type="warning"
              className="container--card container--section"
              message={
                <>
                  <h4 className="text--display">Phase 2: Planning (Week 2)</h4>
                  <ul className="text--body">
                    <li>Select content for pattern application</li>
                    <li>Prioritize by potential impact</li>
                    <li>Create implementation timeline</li>
                    <li>Assign responsibilities</li>
                  </ul>
                </>
              }
            />
            <div className="container--card layout--utility container--section">
              <h4 className="text--display text-info">Phase 3: Implementation (Weeks 3-4)</h4>
              <ul className="text--body">
                <li>Apply success patterns to selected content</li>
                <li>Test new content variations</li>
                <li>Monitor performance metrics</li>
                <li>Iterate based on results</li>
              </ul>
            </div>
            <div className="container--card layout--utility container--section">
              <h4 className="text--display text-purple">Phase 4: Optimization (Week 5+)</h4>
              <ul className="text--body">
                <li>Analyze results and performance</li>
                <li>Refine patterns based on data</li>
                <li>Scale successful implementations</li>
                <li>Update success library</li>
              </ul>
            </div>
          </div>
        </div>
      </div>
    </PageContainer>
  );
};

export default SuccessLibrary;
