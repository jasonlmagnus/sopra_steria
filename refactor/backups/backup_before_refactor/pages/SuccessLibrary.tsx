import { useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import { useFilters } from '../context/FilterContext';
import { ScoreCard } from '../components/ScoreCard';
import { PlotlyChart } from '../components/PlotlyChart';
import StandardCard from '../components/StandardCard';

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

const SuccessLibrary: React.FC = () => {
  const filters = useFilters();
  
  // Success Library specific filters
  const [successThreshold, setSuccessThreshold] = useState(7.5);
  const [maxStories, setMaxStories] = useState(10);
  const [evidenceType, setEvidenceType] = useState('All');
  const [searchTerm, setSearchTerm] = useState('');

  // Fetch success library data
  const { data: successData, isLoading, error } = useQuery<SuccessLibraryData>({
    queryKey: ['success-library', filters.persona, filters.tier, successThreshold, maxStories, evidenceType, searchTerm],
    queryFn: async () => {
      const params = new URLSearchParams({
        successThreshold: successThreshold.toString(),
        persona: filters.persona || 'All',
        tier: filters.tier || 'All', 
        maxStories: maxStories.toString(),
        evidenceType: evidenceType,
        searchTerm: searchTerm
      });
      
      const response = await fetch(`${apiBase}/api/success-library?${params}`);
      
      if (!response.ok) {
        throw new Error('Failed to fetch success library data');
      }
      
      return response.json();
    },
    staleTime: 5 * 60 * 1000, // Cache for 5 minutes
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
  const availablePersonas = successData?.personas || ['All'];
  const availableTiers = successData?.tiers || ['All'];

  const scoreDistributionData = [
    {
      x: successStories.map(s => s.score),
      type: 'histogram',
      nbinsx: 20,
      marker: { color: '#10b981' }
    }
  ];

  const scoreDistributionLayout = {
    title: 'Success Score Distribution',
    xaxis: { title: 'Score' },
    yaxis: { title: 'Count' },
    height: 300
  };

  const tierSuccessData = [
    {
      values: patternData.map(p => p.count),
      labels: patternData.map(p => p.tier),
      type: 'pie'
    }
  ];

  const tierSuccessLayout = {
    title: 'Success Stories by Content Tier',
    height: 300
  };

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
      <div className="page-container">
        <div className="loading-spinner">🔄 Loading Success Library...</div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="page-container">
        <div className="error-message">
          ❌ Error loading success library data: {error.message}
        </div>
      </div>
    );
  }

  return (
    <div className="page-container">
      <div className="main-header">
        <h1>🌟 Success Library</h1>
        <p>Best practice examples and high-performing content showcase</p>
      </div>

      {/* Success Analysis Controls */}
      <div className="section">
        <h2>🎛️ Success Analysis Controls</h2>
        <div className="controls-grid">
          <div className="control-group">
            <label>⭐ Success Threshold</label>
            <input
              type="range"
              min="5.0"
              max="10.0"
              step="0.1"
              value={successThreshold}
              onChange={(e) => setSuccessThreshold(parseFloat(e.target.value))}
            />
            <span>{successThreshold.toFixed(1)}</span>
          </div>
          
          <div className="control-group">
            <label>👤 Persona Focus</label>
            <select 
              value={filters.persona || 'All'} 
              onChange={(e) => filters.setPersona(e.target.value === 'All' ? '' : e.target.value)}
            >
              {availablePersonas.map((persona, index) => (
                <option key={`persona-${index}-${persona}`} value={persona}>{persona}</option>
              ))}
            </select>
          </div>
          
          <div className="control-group">
            <label>🏗️ Content Tier</label>
            <select 
              value={filters.tier || 'All'} 
              onChange={(e) => filters.setTier(e.target.value === 'All' ? '' : e.target.value)}
            >
              {availableTiers.map((tier, index) => (
                <option key={`tier-${index}-${tier}`} value={tier}>{tier}</option>
              ))}
            </select>
          </div>
          
          <div className="control-group">
            <label>📊 Max Success Stories</label>
            <input
              type="number"
              min="5"
              max="50"
              value={maxStories}
              onChange={(e) => setMaxStories(parseInt(e.target.value))}
            />
          </div>
        </div>
      </div>

      {/* Success Overview */}
      <div className="section">
        <h2>📊 Success Overview</h2>
        
        {overview.successPages === 0 ? (
          <div className="empty-state">
            <p>⚠️ No success stories match the selected criteria.</p>
            <p>Try adjusting the success threshold or filters.</p>
          </div>
        ) : (
          <>
            <div className="metrics-grid">
              <ScoreCard 
                label="Total Pages" 
                value={overview.totalPages.toString()} 
                variant="default"
              />
              <ScoreCard 
                label="Success Pages" 
                value={overview.successPages.toString()} 
                variant="success"
              />
              <ScoreCard 
                label="Success Rate" 
                value={`${overview.successRate.toFixed(1)}%`} 
                variant="success"
              />
              <ScoreCard 
                label="Avg Success Score" 
                value={`${overview.avgScore.toFixed(1)}/10`} 
                variant="success"
              />
            </div>

            <div className="success-distribution">
              <div className="success-card success-excellent">
                <div className="metric-value">🏆 {overview.excellent}</div>
                <div className="metric-label">Excellent (≥9.0)</div>
              </div>
              <div className="success-card success-good">
                <div className="metric-value">⭐ {overview.veryGood}</div>
                <div className="metric-label">Very Good (8.0-9.0)</div>
              </div>
              <div className="success-card">
                <div className="metric-value">✅ {overview.good}</div>
                <div className="metric-label">Good (7.5-8.0)</div>
              </div>
            </div>

            {successStories.length > 0 && (
              <div className="charts-grid">
                <PlotlyChart data={scoreDistributionData} layout={scoreDistributionLayout} />
                {patternData.length > 0 && (
                  <PlotlyChart data={tierSuccessData} layout={tierSuccessLayout} />
                )}
              </div>
            )}
          </>
        )}
      </div>

      {/* Detailed Success Stories */}
      <div className="section">
        <h2>🏆 Detailed Success Stories</h2>
        
        {successStories.length === 0 ? (
          <div className="empty-state">
            <p>🎉 No success stories found above {successThreshold.toFixed(1)} with current filters.</p>
            <p>Try lowering the success threshold or adjusting your filters.</p>
          </div>
        ) : (
          <div className="success-stories">
            <div className="success-summary">
              🎉 Found {successStories.length} success stories above {successThreshold.toFixed(1)}
            </div>
            
            {successStories.map((story, index) => {
              const excellence = getExcellenceLevel(story.score);
              return (
                <div key={story.id} className="success-story-card">
                  <div className="story-header">
                    <h3>#{index + 1} - {story.title}</h3>
                    <div className={`excellence-badge ${excellence.class}`}>
                      {excellence.level}
                    </div>
                  </div>

                  <div className="grid grid--cols-4 gap-sm">
                    <StandardCard
                      title="Success Score"
                      variant="metric"
                      status={story.score >= 9 ? "excellent" : story.score >= 8 ? "good" : "warning"}
                    >
                      <div className="metric-value">{story.score.toFixed(1)}/10</div>
                    </StandardCard>
                    <StandardCard
                      title="Content Tier"
                      variant="metric"
                      status="good"
                    >
                      <div className="metric-value">{story.tier}</div>
                    </StandardCard>
                    <StandardCard
                      title="Persona"
                      variant="metric"
                      status="good"
                    >
                      <div className="metric-value">{story.persona}</div>
                    </StandardCard>
                    <StandardCard
                      title="Percentile"
                      variant="metric"
                      status="excellent"
                    >
                      <div className="metric-value">{story.percentile}th</div>
                    </StandardCard>
                  </div>

                  <div className="story-evidence">
                    <h4>📋 Success Evidence & Analysis</h4>
                    
                    <div className="grid grid--cols-3 gap-sm">
                      <StandardCard
                        title={`${getSentimentColor(story.sentiment)} Score`}
                        variant="metric"
                        status={story.score >= 9 ? "excellent" : story.score >= 8 ? "good" : "warning"}
                      >
                        <div className="metric-value">{story.score.toFixed(1)}/10</div>
                      </StandardCard>
                      <StandardCard
                        title={`${getEngagementColor(story.engagement)} Tier`}
                        variant="metric"
                        status="good"
                      >
                        <div className="metric-value">{story.tier}</div>
                      </StandardCard>
                      <StandardCard
                        title={`${getConversionColor(story.conversion)} Percentile`}
                        variant="metric"
                        status="excellent"
                      >
                        <div className="metric-value">{story.percentile}th</div>
                      </StandardCard>
                    </div>

                    <div className="evidence-grid">
                      <div className="evidence-section positive">
                        <h5>✅ What's Working Exceptionally Well:</h5>
                        <div className="evidence-content">
                          {story.personaQuotes.length > 0 && (
                            <div className="persona-quotes">
                              <h6>💬 Persona Voice:</h6>
                              {story.personaQuotes.map((quote, i) => (
                                <div key={i} className="persona-quote">
                                  <em>"{quote}"</em>
                                </div>
                              ))}
                            </div>
                          )}
                          {story.effectiveExamples && (
                            <div className="full-analysis">
                              <h6>📋 Full Success Analysis:</h6>
                              <p><em>{story.effectiveExamples}</em></p>
                            </div>
                          )}
                        </div>
                      </div>
                      
                      <div className="evidence-section warning">
                        <h5>⚠️ Areas for Enhancement:</h5>
                        <div className="evidence-content">
                          <p><em>{story.ineffectiveExamples || 'Even successful pages can be further optimized'}</em></p>
                        </div>
                      </div>
                    </div>

                    {story.trustAssessment && (
                      <div className="trust-assessment">
                        <h5>🔒 Trust & Credibility Strengths:</h5>
                        <p>{story.trustAssessment}</p>
                      </div>
                    )}

                    {story.businessImpact && (
                      <div className="business-impact">
                        <h5>💼 Business Impact & Value:</h5>
                        <p>{story.businessImpact}</p>
                      </div>
                    )}

                    {story.evidence && (
                      <div className="general-evidence">
                        <h5>🔍 Additional Success Factors:</h5>
                        <p>{story.evidence}</p>
                      </div>
                    )}

                    <div className="story-url">
                      <strong>🔗 URL:</strong> <a href={story.url} target="_blank" rel="noopener noreferrer">{story.url}</a>
                    </div>

                    <div className="action-buttons">
                      <button className="action-button">📋 Create Template</button>
                      <button className="action-button">🔍 Analyze Pattern</button>
                      <button className="action-button">📊 Compare Similar</button>
                    </div>
                  </div>
                </div>
              );
            })}
          </div>
        )}
      </div>

      {/* Success Pattern Analysis */}
      <div className="section">
        <h2>🔍 Success Pattern Analysis</h2>
        
        {patternData.length === 0 ? (
          <div className="empty-state">
            <p>📊 No pattern data available for the selected criteria.</p>
          </div>
        ) : (
          <div className="pattern-analysis">
            <h3>🏗️ Success Patterns by Content Tier</h3>
            <div className="pattern-cards">
              {patternData.map((pattern) => (
                <div key={pattern.tier} className="pattern-card">
                  <h4>🏗️ {pattern.tier} Content Pattern</h4>
                  <p>Average Success Score: {pattern.avgScore.toFixed(1)}/10</p>
                  <p>Success Stories: {pattern.count} pages</p>
                  <span className="pattern-tag">Tier Pattern</span>
                </div>
              ))}
            </div>
          </div>
        )}
      </div>

      {/* Evidence Browser */}
      <div className="section">
        <h2>🔍 Evidence Browser</h2>
        
        <div className="evidence-controls">
          <div className="control-group">
            <label>📋 Evidence Type</label>
            <select value={evidenceType} onChange={(e) => setEvidenceType(e.target.value)}>
              <option value="All">All</option>
              <option value="Copy Examples">Copy Examples</option>
              <option value="Design Elements">Design Elements</option>
              <option value="User Feedback">User Feedback</option>
              <option value="Performance Data">Performance Data</option>
              <option value="Trust Assessment">Trust Assessment</option>
            </select>
          </div>
          
          <div className="control-group">
            <label>🔍 Search Evidence</label>
            <input
              type="text"
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              placeholder="Search for specific words or phrases..."
            />
          </div>
        </div>

        <div className="evidence-results">
          <h3>📋 Evidence Results</h3>
          {evidenceItems.length > 0 ? (
            evidenceItems.map((item, index) => (
              <div key={index} className="evidence-item">
                <div className="evidence-header">
                  <h4>📋 {item.pageTitle} - Score: {item.score.toFixed(1)}</h4>
                </div>
                <div className="evidence-section">
                  <strong>{item.type}:</strong>
                  <div className="copy-example">
                    {item.content}
                    <div className="copy-button">📋 Copy</div>
                  </div>
                </div>
              </div>
            ))
          ) : (
            <p>🔍 No evidence found matching the selected criteria. Try adjusting the filters.</p>
          )}
        </div>
      </div>

      {/* Success Replication Guide */}
      <div className="section">
        <h2>🔄 Success Replication Guide</h2>
        
        <div className="replication-templates">
          <h3>📋 Replication Templates</h3>
          {replicationTemplates.map((template) => (
            <div key={template.tier} className="pattern-card">
              <h4>📋 {template.tier} Success Template</h4>
              <p><strong>Average Success Score:</strong> {template.avgScore.toFixed(1)}/10</p>
              
              <h5>Key Elements to Replicate:</h5>
              <ul>
                {template.keyElements.map((element, index) => (
                  <li key={index}>✅ {element}</li>
                ))}
              </ul>
              
              <button className="apply-button">📋 Use This Template</button>
            </div>
          ))}
        </div>

        <div className="success-checklist">
          <h3>✅ Success Checklist</h3>
          <div className="pattern-card">
            <h4>🎯 Essential Success Criteria</h4>
            <div className="checklist-items">
              <div className="checklist-item">☐ <strong>Clear Value Proposition</strong> (Target: 8.5/10)</div>
              <div className="checklist-item">☐ <strong>Strong Headlines</strong> (Target: 8.3/10)</div>
              <div className="checklist-item">☐ <strong>Compelling Content</strong> (Target: 8.7/10)</div>
              <div className="checklist-item">☐ <strong>Trust Signals</strong> (Target: 8.4/10)</div>
              <div className="checklist-item">☐ <strong>Clear Call-to-Action</strong> (Target: 8.1/10)</div>
            </div>
            
            <div className="checklist-guide">
              <h4>📋 How to Use This Checklist</h4>
              <ol>
                <li>Review each criteria for your content</li>
                <li>Score your content against each criteria</li>
                <li>Focus on criteria below the target scores</li>
                <li>Use success story examples as inspiration</li>
                <li>Test and iterate based on results</li>
              </ol>
            </div>
          </div>
        </div>

        <div className="implementation-roadmap">
          <h3>🗺️ Implementation Roadmap</h3>
          <div className="roadmap-phases">
            <div className="phase-card" style={{ borderLeftColor: '#10b981' }}>
              <h4 style={{ color: '#10b981' }}>Phase 1: Analysis (Week 1)</h4>
              <ul>
                <li>Analyze top 3 success stories in detail</li>
                <li>Identify common patterns and elements</li>
                <li>Document key success criteria</li>
                <li>Create pattern templates</li>
              </ul>
            </div>
            
            <div className="phase-card" style={{ borderLeftColor: '#f59e0b' }}>
              <h4 style={{ color: '#f59e0b' }}>Phase 2: Planning (Week 2)</h4>
              <ul>
                <li>Select content for pattern application</li>
                <li>Prioritize by potential impact</li>
                <li>Create implementation timeline</li>
                <li>Assign responsibilities</li>
              </ul>
            </div>
            
            <div className="phase-card" style={{ borderLeftColor: '#0ea5e9' }}>
              <h4 style={{ color: '#0ea5e9' }}>Phase 3: Implementation (Weeks 3-4)</h4>
              <ul>
                <li>Apply success patterns to selected content</li>
                <li>Test new content variations</li>
                <li>Monitor performance metrics</li>
                <li>Iterate based on results</li>
              </ul>
            </div>
            
            <div className="phase-card" style={{ borderLeftColor: '#8b5cf6' }}>
              <h4 style={{ color: '#8b5cf6' }}>Phase 4: Optimization (Week 5+)</h4>
              <ul>
                <li>Analyze results and performance</li>
                <li>Refine patterns based on data</li>
                <li>Scale successful implementations</li>
                <li>Update success library</li>
              </ul>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default SuccessLibrary;
