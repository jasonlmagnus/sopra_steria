import { useState, useEffect } from 'react';
import { useFilters } from '../context/FilterContext';
import { ScoreCard } from '../components/ScoreCard';
import { PlotlyChart } from '../components/PlotlyChart';
// import { DataTable } from '../components/DataTable';

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

const SuccessLibrary: React.FC = () => {
  const filters = useFilters();
  const [loading, setLoading] = useState(true);
  const [successStories, setSuccessStories] = useState<SuccessStory[]>([]);
  const [patternData, setPatternData] = useState<PatternData[]>([]);
  const [evidenceItems, setEvidenceItems] = useState<EvidenceItem[]>([]);
  
  // Success Library specific filters
  const [successThreshold, setSuccessThreshold] = useState(7.5);
  const [maxStories, setMaxStories] = useState(10);
  const [evidenceType, setEvidenceType] = useState('All');
  const [searchTerm, setSearchTerm] = useState('');

  useEffect(() => {
    fetchSuccessData();
  }, [filters, successThreshold, maxStories]);

  const fetchSuccessData = async () => {
    try {
      setLoading(true);
      // TODO: Replace with actual API calls
      const mockSuccessStories: SuccessStory[] = [
        {
          id: 'story-1',
          title: 'Financial Services Excellence',
          score: 9.2,
          tier: 'Tier 1',
          persona: 'Strategic Business Leader',
          url: 'https://soprasteria.be/industries/financial-services',
          percentile: 95,
          sentiment: 'Positive',
          engagement: 'High',
          conversion: 'High',
          effectiveExamples: 'As a financial services leader, I need comprehensive digital transformation solutions that understand regulatory complexity. This page demonstrates deep sector expertise through specific case studies and compliance frameworks.',
          ineffectiveExamples: 'Some technical jargon could be simplified for C-suite consumption.',
          trustAssessment: 'Strong credibility established through industry certifications, regulatory compliance mentions, and specific client success metrics.',
          businessImpact: 'Clear ROI demonstrations with quantified outcomes: 40% operational efficiency gains, 25% cost reduction, 60% faster time-to-market.',
          evidence: 'Page includes comprehensive sector expertise, regulatory compliance framework, and quantified business outcomes.'
        },
        {
          id: 'story-2', 
          title: 'Cloud Infrastructure Platform',
          score: 8.8,
          tier: 'Tier 1',
          persona: 'Technology Innovation Leader',
          url: 'https://soprasteria.be/cloud-infrastructure-platforms',
          percentile: 88,
          sentiment: 'Positive',
          engagement: 'High',
          conversion: 'Medium',
          effectiveExamples: 'From my perspective as a technology leader, this platform approach addresses our hybrid cloud challenges with Microsoft Azure integration and enterprise-grade security.',
          ineffectiveExamples: 'Could include more technical architecture diagrams and implementation timelines.',
          trustAssessment: 'Microsoft partnership credentials and enterprise security certifications build strong technical credibility.',
          businessImpact: 'Demonstrates scalability benefits, security improvements, and operational cost optimization through cloud transformation.',
          evidence: 'Strong technical credibility with Microsoft partnership, security certifications, and architectural expertise.'
        },
        {
          id: 'story-3',
          title: 'Data Science & AI Solutions',
          score: 8.5,
          tier: 'Tier 1',
          persona: 'Cybersecurity Decision Maker',
          url: 'https://soprasteria.be/data-science-ai',
          percentile: 82,
          sentiment: 'Positive',
          engagement: 'Medium',
          conversion: 'High',
          effectiveExamples: 'This resonates with me as a security professional - AI-powered threat detection and predictive analytics for cybersecurity applications.',
          ineffectiveExamples: 'Security implications of AI implementations could be explored more thoroughly.',
          trustAssessment: 'AI ethics framework and security-first approach to data science builds trust with security-conscious buyers.',
          businessImpact: 'Quantified threat detection improvements: 75% faster incident response, 90% reduction in false positives.',
          evidence: 'Comprehensive AI ethics framework, security-first methodology, and quantified cybersecurity outcomes.'
        },
        {
          id: 'story-4',
          title: 'Digital Transformation Consulting',
          score: 8.3,
          tier: 'Tier 2',
          persona: 'Transformation Programme Leader',
          url: 'https://soprasteria.be/digital-transformation-consulting',
          percentile: 78,
          sentiment: 'Positive',
          engagement: 'Medium',
          conversion: 'Medium',
          effectiveExamples: 'As a transformation leader, I appreciate the structured approach to change management and stakeholder engagement throughout digital initiatives.',
          ineffectiveExamples: 'More specific industry vertical examples would strengthen the positioning.',
          trustAssessment: 'Change management methodology and stakeholder engagement framework demonstrate transformation expertise.',
          businessImpact: 'Clear transformation outcomes: 50% process efficiency improvement, 30% employee adoption rate increase.',
          evidence: 'Structured transformation methodology, change management expertise, and measurable business outcomes.'
        },
        {
          id: 'story-5',
          title: 'Corporate Responsibility',
          score: 8.0,
          tier: 'Tier 3',
          persona: 'Strategic Business Leader',
          url: 'https://soprasteria.com/corporate-responsibility',
          percentile: 70,
          sentiment: 'Positive',
          engagement: 'Medium',
          conversion: 'Low',
          effectiveExamples: 'My organization values sustainability and social impact - this demonstrates genuine commitment to responsible business practices.',
          ineffectiveExamples: 'Could connect sustainability initiatives more directly to business value and client outcomes.',
          trustAssessment: 'Comprehensive sustainability reporting and social impact metrics build stakeholder confidence.',
          businessImpact: 'ESG credentials support tender requirements and stakeholder expectations for responsible partnerships.',
          evidence: 'Detailed sustainability reporting, social impact metrics, and responsible business practice documentation.'
        }
      ];

      const mockPatternData: PatternData[] = [
        { tier: 'Tier 1', avgScore: 8.8, count: 15 },
        { tier: 'Tier 2', avgScore: 8.1, count: 8 },
        { tier: 'Tier 3', avgScore: 7.9, count: 5 }
      ];

      const mockEvidenceItems: EvidenceItem[] = [
        {
          type: 'Copy Examples',
          content: 'As a financial services leader, I need comprehensive digital transformation solutions that understand regulatory complexity.',
          pageTitle: 'Financial Services Excellence',
          score: 9.2
        },
        {
          type: 'Performance Data',
          content: '40% operational efficiency gains, 25% cost reduction, 60% faster time-to-market.',
          pageTitle: 'Financial Services Excellence',
          score: 9.2
        },
        {
          type: 'User Feedback',
          content: 'From my perspective as a technology leader, this platform approach addresses our hybrid cloud challenges.',
          pageTitle: 'Cloud Infrastructure Platform',
          score: 8.8
        }
      ];

      setSuccessStories(mockSuccessStories);
      setPatternData(mockPatternData);
      setEvidenceItems(mockEvidenceItems);
    } catch (error) {
      console.error('Error fetching success data:', error);
    } finally {
      setLoading(false);
    }
  };

  const filteredStories = successStories.filter(story => {
    if (story.score < successThreshold) return false;
    if (filters.persona && filters.persona !== 'All' && story.persona !== filters.persona) return false;
    if (filters.tier && filters.tier !== 'All' && story.tier !== filters.tier) return false;
    return true;
  }).slice(0, maxStories);

  const filteredEvidence = evidenceItems.filter(item => {
    if (evidenceType !== 'All' && item.type !== evidenceType) return false;
    if (searchTerm && !item.content.toLowerCase().includes(searchTerm.toLowerCase())) return false;
    return true;
  });

  const successMetrics = {
    totalPages: successStories.length,
    successPages: filteredStories.length,
    successRate: (filteredStories.length / successStories.length) * 100,
    avgScore: filteredStories.reduce((sum, story) => sum + story.score, 0) / filteredStories.length || 0,
    excellent: filteredStories.filter(s => s.score >= 9.0).length,
    veryGood: filteredStories.filter(s => s.score >= 8.0 && s.score < 9.0).length,
    good: filteredStories.filter(s => s.score >= 7.5 && s.score < 8.0).length
  };

  const scoreDistributionData = [
    {
      x: filteredStories.map(s => s.score),
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

  if (loading) {
    return (
      <div className="page-container">
        <div className="loading-spinner">Loading Success Library...</div>
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
              <option value="All">All</option>
              <option value="Strategic Business Leader">Strategic Business Leader</option>
              <option value="Technology Innovation Leader">Technology Innovation Leader</option>
              <option value="Cybersecurity Decision Maker">Cybersecurity Decision Maker</option>
              <option value="Transformation Programme Leader">Transformation Programme Leader</option>
            </select>
          </div>
          
          <div className="control-group">
            <label>🏗️ Content Tier</label>
            <select 
              value={filters.tier || 'All'} 
              onChange={(e) => filters.setTier(e.target.value === 'All' ? '' : e.target.value)}
            >
              <option value="All">All</option>
              <option value="Tier 1">Tier 1</option>
              <option value="Tier 2">Tier 2</option>
              <option value="Tier 3">Tier 3</option>
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
        <div className="metrics-grid">
          <ScoreCard 
            label="Total Pages" 
            value={successMetrics.totalPages.toString()} 
            variant="default"
          />
          <ScoreCard 
            label="Success Pages" 
            value={successMetrics.successPages.toString()} 
            variant="success"
          />
          <ScoreCard 
            label="Success Rate" 
            value={`${successMetrics.successRate.toFixed(1)}%`} 
            variant="success"
          />
          <ScoreCard 
            label="Avg Success Score" 
            value={`${successMetrics.avgScore.toFixed(1)}/10`} 
            variant="success"
          />
        </div>

        <div className="success-distribution">
          <div className="success-card success-excellent">
            <div className="metric-value">🏆 {successMetrics.excellent}</div>
            <div className="metric-label">Excellent (≥9.0)</div>
          </div>
          <div className="success-card success-good">
            <div className="metric-value">⭐ {successMetrics.veryGood}</div>
            <div className="metric-label">Very Good (8.0-9.0)</div>
          </div>
          <div className="success-card">
            <div className="metric-value">✅ {successMetrics.good}</div>
            <div className="metric-label">Good (7.5-8.0)</div>
          </div>
        </div>

        <div className="charts-grid">
          <PlotlyChart data={scoreDistributionData} layout={scoreDistributionLayout} />
          <PlotlyChart data={tierSuccessData} layout={tierSuccessLayout} />
        </div>
      </div>

      {/* Detailed Success Stories */}
      <div className="section">
        <h2>🏆 Detailed Success Stories</h2>
        <div className="success-stories">
          {filteredStories.map((story, index) => {
            const excellence = getExcellenceLevel(story.score);
            return (
              <div key={story.id} className="success-story-card">
                <div className="story-header">
                  <h3>#{index + 1} - {story.title}</h3>
                  <div className={`excellence-badge ${excellence.class}`}>
                    {excellence.level}
                  </div>
                </div>

                <div className="story-metrics">
                  <div className="metric">
                    <span className="metric-label">Success Score</span>
                    <span className="metric-value">{story.score.toFixed(1)}/10</span>
                  </div>
                  <div className="metric">
                    <span className="metric-label">Content Tier</span>
                    <span className="metric-value">{story.tier}</span>
                  </div>
                  <div className="metric">
                    <span className="metric-label">Persona</span>
                    <span className="metric-value">{story.persona}</span>
                  </div>
                  <div className="metric">
                    <span className="metric-label">Percentile</span>
                    <span className="metric-value">{story.percentile}th</span>
                  </div>
                </div>

                <div className="story-evidence">
                  <h4>📋 Success Evidence & Analysis</h4>
                  
                  <div className="experience-metrics">
                    <div className="experience-metric">
                      <span>{getSentimentColor(story.sentiment)} Sentiment: {story.sentiment}</span>
                    </div>
                    <div className="experience-metric">
                      <span>{getEngagementColor(story.engagement)} Engagement: {story.engagement}</span>
                    </div>
                    <div className="experience-metric">
                      <span>{getConversionColor(story.conversion)} Conversion: {story.conversion}</span>
                    </div>
                  </div>

                  <div className="evidence-grid">
                    <div className="evidence-section positive">
                      <h5>✅ What's Working Exceptionally Well:</h5>
                      <div className="evidence-content">
                        <p><em>"{story.effectiveExamples}"</em></p>
                      </div>
                    </div>
                    
                    <div className="evidence-section warning">
                      <h5>⚠️ Areas for Enhancement:</h5>
                      <div className="evidence-content">
                        <p><em>{story.ineffectiveExamples}</em></p>
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
      </div>

      {/* Success Pattern Analysis */}
      <div className="section">
        <h2>🔍 Success Pattern Analysis</h2>
        
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
          {filteredEvidence.length > 0 ? (
            filteredEvidence.map((item, index) => (
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
          {patternData.map((pattern) => (
            <div key={pattern.tier} className="pattern-card">
              <h4>📋 {pattern.tier} Success Template</h4>
              <p><strong>Average Success Score:</strong> {pattern.avgScore.toFixed(1)}/10</p>
              
              <h5>Key Elements to Replicate:</h5>
              <ul>
                <li>✅ Focus on high-performing criteria patterns</li>
                <li>✅ Maintain consistent messaging tone</li>
                <li>✅ Implement proven design elements</li>
                <li>✅ Apply successful content structure</li>
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
