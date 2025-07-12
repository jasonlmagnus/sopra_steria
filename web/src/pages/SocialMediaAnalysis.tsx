import { useState, useEffect } from 'react'
import { useQuery } from '@tanstack/react-query';
import { Banner, DataTable, PageContainer, StandardCard } from '../components'
import { EvidenceDisplay } from '../components/EvidenceDisplay'
import { useFilters } from '../hooks/useFilters';
import { FilterSystem } from '../components/FilterSystem';
import type { FilterConfig } from '../types/filters';
import type { ColumnDef } from '@tanstack/react-table'
import '../styles/dashboard.css'

interface SocialMediaData {
  platform: string
  platform_display: string
  persona_clean: string
  raw_score: number
  engagement_numeric: number
  sentiment_numeric: number
  critical_issue_flag: boolean
  success_flag: boolean
  quick_win_flag: boolean
  url: string
  evidence: string
  effective_copy_examples: string
  ineffective_copy_examples: string
  trust_credibility_assessment: string
  business_impact_analysis: string
  tier: string
  audited_ts: string
}

interface PlatformMetrics {
  Platform: string
  Platform_Code: string
  Average_Score: number
  Score_Range: string
  Status: string
  Status_Color: string
  Total_Entries: number
  High_Performers: number
  Moderate_Performers: number
  Low_Performers: number
  Avg_Engagement: number
  Avg_Sentiment: number
  Critical_Issues: number
  Success_Cases: number
  Quick_Wins: number
}

interface Insight {
  Category: string
  Insight: string
  Type: string
}

interface Recommendation {
  Platform: string
  Priority: string
  Category: string
  Recommendation: string
  Impact: string
  Timeline: string
}

interface SocialMediaApiResponse {
  data: SocialMediaData[]
  insights: Insight[]
  recommendations: Recommendation[]
  platform_metrics: PlatformMetrics[]
  persona_platform_matrix: Array<{
    persona: string
    platform: string
    score: number
  }>
  analysis_scope: string
  total_entries: number
  platforms_analyzed: string[]
  personas_analyzed: string[]
  error?: string
}

const socialMediaFilters: FilterConfig[] = [
  { name: 'platforms', label: '📱 Select Platforms', type: 'multiselect', defaultValue: [] },
  { name: 'personas', label: '👥 Select Personas', type: 'multiselect', defaultValue: [] },
  {
    name: 'analysisScope',
    label: '⚙️ Analysis Scope',
    type: 'select',
    defaultValue: 'All Data',
    options: [
      { value: 'All Data', label: 'All Data' },
      { value: 'Success Flag', label: 'Success Flag' },
      { value: 'Critical Issue', label: 'Critical Issue' },
      { value: 'Quick Win', label: 'Quick Win' },
    ],
  },
];

export default function SocialMediaAnalysis() {
  const { filters, setAllFilters } = useFilters();
  const [viewMode, setViewMode] = useState('Overview');
  const [activeTab, setActiveTab] = useState('platform-deep-dive');

  const { data, isLoading, error } = useQuery<SocialMediaApiResponse>({
    queryKey: ['social-media', filters],
    queryFn: async () => {
      const params = new URLSearchParams();
      // Handle array values for multiselect
      if (filters.platforms && filters.platforms.length > 0) {
        params.append('platforms', filters.platforms.join(','));
      }
      if (filters.personas && filters.personas.length > 0) {
        params.append('personas', filters.personas.join(','));
      }
      if (filters.analysisScope) {
        params.append('analysis_scope', filters.analysisScope);
      }
      
      const response = await fetch(`/api/social-media?${params.toString()}`);
      if (!response.ok) throw new Error(`HTTP error! status: ${response.status}`);
      return response.json();
    },
    enabled: Object.keys(filters).length > 0,
  });
  
  useEffect(() => {
    // Initialize filters only once from the first successful data load
    if (data && (!filters.platforms || filters.platforms.length === 0)) {
      const defaultFilters = {
        platforms: data.platforms_analyzed || [],
        personas: data.personas_analyzed || [],
        analysisScope: 'All Data'
      };
      setAllFilters(defaultFilters);
    }
  }, [data, filters, setAllFilters]);

  const getHealthStatus = (score: number) => {
    if (score >= 7) return { status: "🟢 Healthy", color: "#10B981" }
    if (score >= 5) return { status: "🟡 Moderate", color: "#F59E0B" }
    if (score >= 3) return { status: "🟠 At Risk", color: "#F97316" }
    return { status: "🔴 Critical", color: "#EF4444" }
  }

  const overallAvg = (data && data.data) ? data.data.reduce((sum, item) => sum + item.raw_score, 0) / data.data.length : 0;
  const healthInfo = getHealthStatus(overallAvg);
  const twitterCritical = (data && data.data) ? data.data.some(item => item.platform === 'twitter' && item.raw_score < 2) : false;

  if (isLoading) {
    return (
      <div className="container--layout">
        <Banner message={
          <div className="text-center">
            <div className="loader--state"></div>
            <p className="text--body">Loading social media analysis...</p>
          </div>
        } />
      </div>
    );
  }

  if (error) {
    return (
      <div className="container--layout">
        <Banner
          type="error"
          message={
            <>
              <h2 className="heading--subsection">❌ Error Loading Data</h2>
              <p className="text--body">{error instanceof Error ? error.message : 'Unknown error'}</p>
              <button onClick={() => setAllFilters({})} className="button--primary">
                🔄 Retry
              </button>
            </>
          }
        />
      </div>
    );
  }

  if (!data || data.error) {
    return (
      <div className="container--layout">
        <Banner
          message={
            <>
              <h2 className="heading--subsection">📊 No Social Media Data</h2>
              <p className="text--body">{data?.error || 'No social media data available for analysis.'}</p>
            </>
          }
        />
      </div>
    );
  }

  // Create dynamic options for the filter system
  const dynamicFilterData = {
    platformsOptions: (data?.platforms_analyzed || []).map(p => ({ value: p, label: p })),
    personasOptions: (data?.personas_analyzed || []).map(p => ({ value: p, label: p })),
  };

  return (
    <PageContainer title="🔍 Social Media Analysis">
      <p className="text--body">Cross-platform brand presence and engagement insights</p>

      {/* Executive Summary */}
      <div className="container--section">
        <h2 className="heading--section">📊 Executive Summary</h2>
        
        {/* Critical Alert Banner */}
        {twitterCritical && (
          <Banner
            type="warning"
            message={
              <>
                <h4 className="heading--card">⚠️ Attention Required</h4>
                <p className="text--body">
                  Twitter/X platform showing low performance scores - review and optimization recommended
                </p>
              </>
            }
          />
        )}

        {/* Metrics Cards */}
        <div className="grid--layout-3-col">
          <StandardCard
            title="Overall Health"
            value={`${overallAvg.toFixed(1)} / 10`}
            label={healthInfo.status}
            status={healthInfo.status.includes('Healthy') ? 'excellent' : healthInfo.status.includes('Moderate') ? 'warning' : 'critical'}
          />
          <StandardCard
            title="Top Platform"
            value={data.platform_metrics.reduce((prev, current) => (prev.Average_Score > current.Average_Score) ? prev : current).Platform_Code}
            label={`Score: ${data.platform_metrics.reduce((prev, current) => (prev.Average_Score > current.Average_Score) ? prev : current).Average_Score.toFixed(1)}`}
          />
          <StandardCard
            title="Weakest Platform"
            value={data.platform_metrics.reduce((prev, current) => (prev.Average_Score < current.Average_Score) ? prev : current).Platform_Code}
            label={`Score: ${data.platform_metrics.reduce((prev, current) => (prev.Average_Score < current.Average_Score) ? prev : current).Average_Score.toFixed(1)}`}
            status="warning"
          />
          <StandardCard
            title="Platform Coverage"
            value={data.platform_metrics.length}
            label="Platforms Analyzed"
          />
          <StandardCard
            title="Critical Issues"
            value={data.data.filter(item => item.critical_issue_flag).length}
            label="High-priority flags"
            status="critical"
          />
          <StandardCard
            title="Quick Wins"
            value={data.data.filter(item => item.quick_win_flag).length}
            label="Low-effort opportunities"
            status="good"
          />
        </div>
      </div>

      {/* Analysis Controls */}
      <div className="container--section">
        <h2 className="heading--section">🎯 Analysis Controls</h2>
        <FilterSystem config={socialMediaFilters} data={dynamicFilterData} />
        <div className="container--layout-col">
            <label className="label--form">📊 View Mode</label>
            <div className="tabs">
              {['Overview', 'Detailed Analysis', 'Recommendations'].map(mode => (
                <button 
                  key={mode}
                  className={`tabs__button ${viewMode === mode ? 'tabs__button--active' : ''}`}
                  onClick={() => setViewMode(mode)}
                >
                  {mode}
                </button>
              ))}
            </div>
          </div>
      </div>

      {/* Main Content Based on View Mode */}
      {viewMode === 'Overview' && (
        <>
          <PlatformHealthOverview platformMetrics={data.platform_metrics} />
          <PlatformPerformanceAnalysis platformMetrics={data.platform_metrics} />
          <PersonaAnalysis data={data.data} />
          <InsightsAndRecommendations insights={data.insights} recommendations={data.recommendations} />
        </>
      )}

      {viewMode === 'Detailed Analysis' && (
        <DetailedAnalysisTabs 
          data={data.data} 
          platformMetrics={data.platform_metrics}
          activeTab={activeTab}
          setActiveTab={setActiveTab}
        />
      )}

      {viewMode === 'Recommendations' && (
        <>
          <InsightsAndRecommendations insights={data.insights} recommendations={data.recommendations} />
          <ActionPriorityMatrix recommendations={data.recommendations} />
        </>
      )}
    </PageContainer>
  )
}

function PlatformHealthOverview({ platformMetrics }: { platformMetrics: PlatformMetrics[] }) {
  const columns: ColumnDef<PlatformMetrics>[] = [
    { accessorKey: 'Platform', header: 'Platform' },
    { accessorKey: 'Average_Score', header: 'Avg Score' },
    { accessorKey: 'Total_Entries', header: 'Entries' },
    { accessorKey: 'Critical_Issues', header: 'Critical Issues' },
    { 
      accessorKey: 'Status', 
      header: 'Status',
      cell: info => (
        <span className="text--tag" style={{ backgroundColor: info.row.original.Status_Color }}>
          {info.getValue() as string}
        </span>
      )
    },
  ]

  return (
    <div className="container--section">
      <h2 className="heading--section">Platform Health Overview</h2>
      <DataTable columns={columns} data={platformMetrics} />
    </div>
  );
}

function PlatformPerformanceAnalysis({ platformMetrics }: { 
  platformMetrics: PlatformMetrics[] 
}) {
  return (
    <div className="container--section">
      <h2 className="heading--section">Platform Performance Analysis</h2>
      <div className="grid--layout-2-col">
        {platformMetrics.map(p => (
          <div key={p.Platform_Code} className="card--data">
            <h3 className="heading--card">{p.Platform}</h3>
            <p>Score: {p.Average_Score.toFixed(1)}</p>
            {/* Add more detailed visualizations here later */}
          </div>
        ))}
      </div>
    </div>
  );
}

function PersonaAnalysis({ data }: { 
  data: SocialMediaData[]
}) {
  const personas = [...new Set(data.map(d => d.persona_clean))];
  return (
    <div className="container--section">
      <h2 className="heading--section">Persona Analysis</h2>
      <div className="grid--layout-2-col">
        {personas.map(persona => (
          <div key={persona} className="card--data">
            <h3 className="heading--card">{persona}</h3>
            {/* Find top and bottom platforms for this persona */}
          </div>
        ))}
      </div>
    </div>
  );
}

function InsightsAndRecommendations({ insights, recommendations }: { 
  insights: Insight[],
  recommendations: Recommendation[]
}) {
  const insightItems = insights.map(i => ({ type: 'evidence' as const, content: i.Insight, title: i.Type }));
  const recommendationItems = recommendations.slice(0, 5).map(r => ({ type: 'business_impact' as const, content: r.Recommendation, title: `${r.Platform} (${r.Priority})` }));

  return (
    <div className="container--section">
      <h2 className="heading--section">Insights & Recommendations</h2>
      <div className="grid--layout-2-col">
        <EvidenceDisplay evidence={insightItems} title="Key Insights" />
        <EvidenceDisplay evidence={recommendationItems} title="Top Recommendations" />
      </div>
    </div>
  );
}


function DetailedAnalysisTabs({ data, platformMetrics, activeTab, setActiveTab }: { 
  data: SocialMediaData[], 
  platformMetrics: PlatformMetrics[],
  activeTab: string,
  setActiveTab: (tab: string) => void
}) {
  return (
    <div className="container--section">
      <h2 className="heading--section">🔬 Detailed Analysis</h2>
      
      <div className="container--tabs">
        <div className="tabs">
          {[
            { id: 'platform-deep-dive', label: '📊 Platform Deep Dive' },
            { id: 'content-strategy', label: '📝 Content Strategy' },
            { id: 'performance-analytics', label: '🎯 Performance Analytics' },
            { id: 'quick-wins', label: '⚡ Quick Wins & Actions' }
          ].map(tab => (
            <button 
              key={tab.id}
              className={`tabs__button ${activeTab === tab.id ? 'tabs__button--active' : ''}`}
              onClick={() => setActiveTab(tab.id)}
            >
              {tab.label}
            </button>
          ))}
        </div>
        
        <div className="tabs--content">
          {activeTab === 'platform-deep-dive' && (
            <PlatformDeepDive data={data} platformMetrics={platformMetrics} />
          )}
          {activeTab === 'content-strategy' && (
            <ContentStrategyAnalysis data={data} />
          )}
          {activeTab === 'performance-analytics' && (
            <PerformanceAnalytics platformMetrics={platformMetrics} />
          )}
          {activeTab === 'quick-wins' && (
            <QuickWinsAnalysis data={data} />
          )}
        </div>
      </div>
    </div>
  )
}

function PlatformDeepDive({ data, platformMetrics }: { data: SocialMediaData[], platformMetrics: PlatformMetrics[] }) {
  const [selectedPlatform, setSelectedPlatform] = useState(platformMetrics[0]?.Platform_Code || '');

  const platformData = data.filter(d => d.platform === selectedPlatform);
  const platformMetric = platformMetrics.find(p => p.Platform_Code === selectedPlatform);

  const columns: ColumnDef<SocialMediaData>[] = [
    { accessorKey: 'persona_clean', header: 'Persona' },
    { accessorKey: 'raw_score', header: 'Score' },
    { accessorKey: 'engagement_numeric', header: 'Engagement' },
    { accessorKey: 'sentiment_numeric', header: 'Sentiment' },
    { 
      id: 'flags',
      header: 'Flags',
      cell: ({row}) => (
        <>
          {row.original.critical_issue_flag && <span className="badge--error">Critical</span>}
          {row.original.success_flag && <span className="badge--success">Success</span>}
          {row.original.quick_win_flag && <span className="badge--info">Quick Win</span>}
        </>
      )
    },
  ]

  return (
    <div className="container--content">
      <h3 className="heading--subsection">Platform Deep Dive</h3>
      <select 
        value={selectedPlatform} 
        onChange={e => setSelectedPlatform(e.target.value)}
        className="select--form"
      >
        {platformMetrics.map(p => (
          <option key={p.Platform_Code} value={p.Platform_Code}>{p.Platform}</option>
        ))}
      </select>

      {platformMetric && (
        <div className="grid--layout-4-col margin--top-l">
          <StandardCard
            title="Avg Score"
            value={platformMetric.Average_Score.toFixed(1)}
            label="Score"
          />
          <StandardCard
            title="Engagement"
            value={platformMetric.Avg_Engagement.toFixed(2)}
            label="Engagement"
          />
          <StandardCard
            title="Sentiment"
            value={platformMetric.Avg_Sentiment.toFixed(2)}
            label="Sentiment"
          />
          <StandardCard
            title="Issues"
            value={platformMetric.Critical_Issues}
            label="Critical Issues"
          />
        </div>
      )}

      <DataTable columns={columns} data={platformData} />
    </div>
  );
}

function ContentStrategyAnalysis({ data }: { data: SocialMediaData[] }) {
  const [selectedPersona, setSelectedPersona] = useState('All');
  const personas = ['All', ...new Set(data.map(d => d.persona_clean))];
  const filteredData = selectedPersona === 'All' ? data : data.filter(d => d.persona_clean === selectedPersona);

  const evidenceItems = filteredData.flatMap(d => [
    d.effective_copy_examples ? { type: 'effective_copy' as const, content: d.effective_copy_examples, title: d.platform_display } : null,
    d.ineffective_copy_examples ? { type: 'ineffective_copy' as const, content: d.ineffective_copy_examples, title: d.platform_display } : null
  ]).filter((item): item is { type: 'effective_copy' | 'ineffective_copy'; content: string; title: string; } => item !== null);

  return (
    <div className="container--content">
      <h3 className="heading--subsection">Content Strategy Analysis</h3>
      <select 
        value={selectedPersona} 
        onChange={e => setSelectedPersona(e.target.value)}
        className="select--form"
      >
        {personas.map(p => <option key={p} value={p}>{p}</option>)}
      </select>

      <div className="margin--top-l">
        <EvidenceDisplay evidence={evidenceItems} />
      </div>
    </div>
  );
}

function PerformanceAnalytics({ platformMetrics }: { platformMetrics: PlatformMetrics[] }) {
  const [chartType, setChartType] = useState('score');
  
  // Chart.js data would be prepared here. For now, showing a placeholder.
  const chartData = {
    labels: platformMetrics.map(p => p.Platform_Code),
    datasets: [{
      label: 'Average Score',
      data: platformMetrics.map(p => p.Average_Score)
    }]
  };

  return (
    <div className="container--content">
      <h3 className="heading--subsection">Performance Analytics</h3>
      <div className="container--flex-row">
        <button className="button--secondary" onClick={() => setChartType('score')}>Score</button>
        <button className="button--secondary" onClick={() => setChartType('engagement')}>Engagement</button>
        <button className="button--secondary" onClick={() => setChartType('sentiment')}>Sentiment</button>
      </div>
      <div className="chart-container margin--top-l">
        {/* Placeholder for chart */}
        <p className="text--body">Chart for {chartType} will be displayed here.</p>
        <pre className="code-block">{JSON.stringify(chartData, null, 2)}</pre>
      </div>
    </div>
  );
}

function QuickWinsAnalysis({ data }: { data: SocialMediaData[] }) {
  const quickWins = data.filter(d => d.quick_win_flag);

  const columns: ColumnDef<SocialMediaData>[] = [
    { accessorKey: 'platform_display', header: 'Platform' },
    { accessorKey: 'persona_clean', header: 'Persona' },
    { accessorKey: 'evidence', header: 'Evidence' },
    { 
      accessorKey: 'url',
      header: 'URL',
      cell: info => (
        <a href={info.getValue() as string} target="_blank" rel="noopener noreferrer" className="link--external">
          View Post
        </a>
      )
    },
  ]

  return (
    <div className="container--content">
      <h3 className="heading--subsection">Quick Wins & Actions</h3>
      <p className="text--body">
        High-impact, low-effort actions to improve performance.
      </p>
      <DataTable columns={columns} data={quickWins} />
    </div>
  );
}


function ActionPriorityMatrix({ recommendations }: { recommendations: Recommendation[] }) {
  const [impactFilter, setImpactFilter] = useState('All');
  const [timelineFilter, setTimelineFilter] = useState('All');

  const filteredRecs = recommendations.filter(r => 
    (impactFilter === 'All' || r.Impact === impactFilter) &&
    (timelineFilter === 'All' || r.Timeline === timelineFilter)
  );

  const columns: ColumnDef<Recommendation>[] = [
    { accessorKey: 'Recommendation', header: 'Recommendation' },
    { accessorKey: 'Platform', header: 'Platform' },
    { 
      accessorKey: 'Priority', 
      header: 'Priority',
      cell: info => (
        <span className={`badge--priority-${(info.getValue() as string).toLowerCase()}`}>{info.getValue() as string}</span>
      )
    },
    { accessorKey: 'Impact', header: 'Impact' },
    { accessorKey: 'Timeline', header: 'Timeline' },
  ]

  return (
    <div className="container--section">
      <h2 className="heading--section">Action Priority Matrix</h2>
      <div className="container--flex-row">
        <div className="container--layout-col">
          <label className="label--form">Filter by Impact</label>
          <select value={impactFilter} onChange={e => setImpactFilter(e.target.value)} className="select--form">
            <option>All</option>
            <option>High</option>
            <option>Medium</option>
            <option>Low</option>
          </select>
        </div>
        <div className="container--layout-col">
          <label className="label--form">Filter by Timeline</label>
          <select value={timelineFilter} onChange={e => setTimelineFilter(e.target.value)} className="select--form">
            <option>All</option>
            <option>Immediate</option>
            <option>Short-Term</option>
            <option>Long-Term</option>
          </select>
        </div>
      </div>

      <DataTable columns={columns} data={filteredRecs} />
    </div>
  );
}
