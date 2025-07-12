import { useEffect } from 'react';
import { useQuery } from '@tanstack/react-query';
import { Banner, PlotlyChart, StandardCard, PageContainer, PageHeader } from '../components';
import { EvidenceDisplay } from '../components/EvidenceDisplay';
import { useFilters } from '../hooks/useFilters';
import { FilterSystem } from '../components/FilterSystem';
import type { FilterConfig } from '../types/filters';
// Import unified dashboard styles
import '../styles/dashboard.css'
// Import standardized element classes
import '../styles/utilities.css'

const apiBase = import.meta.env.VITE_API_URL || 'http://localhost:3000'

interface StrategicIntelligence {
  executiveSummary: {
    totalRecommendations: number;
    highImpactOpportunities: number;
    quickWinOpportunities: number;
    criticalIssues: number;
    overallScore: number;
  };
  strategicThemes: Array<{
    id: string;
    title: string;
    description: string;
    currentScore: number;
    targetScore: number;
    businessImpact: string;
    affectedPages: number;
    competitiveRisk: string;
    keyInsights: string[];
    soWhat: string;
  }>;
  recommendations: Array<{
    id: string;
    title: string;
    description: string;
    businessImpact: string;
    implementationEffort: string;
    timeline: string;
    tier: string;
    persona: string;
    currentScore: number;
    targetScore: number;
    evidence: string;
    soWhat: string;
    implementationSteps: string[];
    success_metrics: string[];
  }>;
  competitiveContext: {
    currentScore: number;
    benchmarkScore: number;
    marketOpportunity: string;
    vulnerabilities: string[];
    overallPosition: string;
  };
  tierAnalysis: {
    [key: string]: {
      name: string;
      avgScore: number;
      pageCount: number;
      criticalIssues: number;
      quickWins: number;
      priority: string;
      businessContext: string;
    };
  };
  implementationRoadmap: Array<{
    phase: string;
    focus: string;
    recommendations: string[];
    expectedImpact: string;
  }>;
  businessImpact: {
    optimizationPotential: number;
    improvementAreas: number;
    competitiveAdvantage: string[];
    successStories: string[];
  };
}

// Add fallback data structure for basic recommendations
interface BasicRecommendation {
  id: string
  title: string
  description: string
  impact_score: number
  urgency_score: number
  timeline: string
  priority_score: number
  page_id: string
  persona: string
  url: string
  evidence: string
}

const strategicFilters: FilterConfig[] = [
  { name: 'tier', label: 'Tier', type: 'select', defaultValue: 'All' },
  {
    name: 'businessImpact',
    label: 'Business Impact',
    type: 'select',
    defaultValue: 'All',
    options: [
      { value: 'All', label: 'All Impacts' },
      { value: 'High', label: 'High' },
      { value: 'Medium', label: 'Medium' },
      { value: 'Low', label: 'Low' },
    ],
  },
  {
    name: 'timeline',
    label: 'Timeline',
    type: 'select',
    defaultValue: 'All',
    options: [
      { value: 'All', label: 'All Timelines' },
      { value: '0-7 days', label: '0-7 days' },
      { value: '0-30 days', label: '0-30 days' },
      { value: '30-90 days', label: '30-90 days' },
      { value: '90+ days', label: '90+ days' },
    ],
  },
];

function StrategicRecommendations() {
  const { filters, setAllFilters } = useFilters();

  useEffect(() => {
    const defaultFilters = strategicFilters.reduce((acc, f) => {
      acc[f.name] = f.defaultValue;
      return acc;
    }, {} as { [key: string]: any });
    setAllFilters(defaultFilters);
  }, [setAllFilters]);
  
  // Primary data source - strategic intelligence
  const { data: strategicData, isLoading: strategicLoading, error: strategicError } = useQuery({
    queryKey: ['strategic-intelligence', filters],
    queryFn: async () => {
      const params = new URLSearchParams(filters);
      const res = await fetch(`${apiBase}/api/strategic-intelligence?${params.toString()}`);
      if (!res.ok) throw new Error('Failed to load strategic intelligence');
      return await res.json() as StrategicIntelligence;
    },
    enabled: Object.keys(filters).length > 0,
    retry: 1,
    retryDelay: 1000,
  });

  // Fallback data source
  const { data: fallbackData, isLoading: fallbackLoading } = useQuery({
    queryKey: ['basic-recommendations', filters],
    queryFn: async () => {
      const params = new URLSearchParams(filters);
      const res = await fetch(`${apiBase}/api/full-recommendations?${params.toString()}`);
      if (!res.ok) throw new Error('Failed to load basic recommendations');
      const data = await res.json();
      return data.recommendations as BasicRecommendation[];
    },
    enabled: !!strategicError && Object.keys(filters).length > 0,
  });

  // Determine which data to use
  const isUsingFallback = !!strategicError && !fallbackLoading
  const isLoading = strategicLoading || (strategicError && fallbackLoading)
  const hasData = strategicData || fallbackData

  const getImpactColor = (impact: string): string => {
    switch (impact.toLowerCase()) {
      case 'high': return 'var(--color-impact-high)'
      case 'medium': return 'var(--color-impact-medium)'
      case 'low': return 'var(--color-impact-low)'
      default: return 'var(--color-impact-default)'
    }
  }

  const getBusinessImpactMatrix = () => {
    if (!strategicData?.recommendations) return []

    return strategicData.recommendations.map((rec) => ({
      x: rec.implementationEffort === 'High' ? 3 : rec.implementationEffort === 'Medium' ? 2 : 1,
      y: rec.businessImpact === 'High' ? 3 : rec.businessImpact === 'Medium' ? 2 : 1,
      text: rec.title.replace('Quick Win: ', '').replace('CRITICAL: ', ''),
      mode: 'markers+text',
      textposition: 'middle center',
      marker: {
        size: rec.currentScore * 3, // Scale marker size by current score
        color: rec.timeline.includes('0-7') ? '#dc3545' : 
               rec.timeline.includes('0-30') ? '#fd7e14' :
               rec.timeline.includes('30-90') ? '#ffc107' : '#28a745',
        opacity: 0.7
      }
    }))
  }

  if (isLoading) {
    return (
      <PageContainer title="🎯 Strategic Intelligence">
        <PageHeader
          title="🎯 Strategic Intelligence"
          description="Loading strategic analysis..."
        />
        <div className="loading--state">
          <div className="loading--state"></div>
          <p>Analyzing brand health data...</p>
        </div>
      </PageContainer>
    )
  }

  if (!hasData) {
    return (
      <PageContainer title="🎯 Strategic Intelligence">
        <PageHeader
          title="🎯 Strategic Intelligence"
          description="Strategic recommendations and action plans for brand improvement"
        />
        
        <Banner
          type="error"
          message={
            <>
              <h2 className="heading--subsection">⚠️ Error Loading Recommendations</h2>
              <p className="text--body">Failed to load strategic recommendations</p>
              <p className="text--body"><strong>Troubleshooting:</strong></p>
              <ul>
                <li>Ensure FastAPI server is running on port 8000</li>
                <li>Check that audit data has been processed</li>
                <li>Verify network connectivity</li>
              </ul>
              <button 
                className="button--action"
                onClick={() => window.location.reload()}
              >
                🔄 Retry
              </button>
            </>
          }
        />
      </PageContainer>
    )
  }

  // Render fallback view if using basic recommendations
  if (isUsingFallback && fallbackData) {
    return (
      <PageContainer title="🎯 Strategic Recommendations">
        <PageHeader
          title="🎯 Strategic Recommendations"
          description="Basic recommendations based on audit data"
        />
        <Banner
          type="warning"
          message="Displaying basic recommendations. For full strategic intelligence, please ensure the backend service is running correctly."
        />
        <FilterSystem config={strategicFilters} data={{}} />
        <FallbackRecommendationsView recommendations={fallbackData} />
      </PageContainer>
    )
  }

  // Type guard for strategicData
  if (!strategicData) {
    return null // This shouldn't happen due to earlier checks, but satisfies TypeScript
  }

  return (
    <PageContainer title="🎯 Strategic Intelligence">
      <PageHeader
        title="🎯 Strategic Intelligence"
        description="Data-driven action plans for brand improvement"
      />

      <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-6">
        <StandardCard title="Executive Summary" variant="content">
          <p className="text--body-sm text-gray-600 mb-4">Key metrics from the strategic analysis</p>
          <div className="grid grid-cols-4 gap-4 text-center">
            <div className="p-4 rounded-lg">
              <div className="text-3xl font-bold text-primary">
                {strategicData.executiveSummary.totalRecommendations}
              </div>
              <div className="text-sm text-gray-600">Total Recommendations</div>
            </div>
            <div className="p-4 rounded-lg">
              <div className="text-3xl font-bold text-green-500">
                {strategicData.executiveSummary.highImpactOpportunities}
              </div>
              <div className="text-sm text-gray-600">High-Impact</div>
            </div>
            <div className="p-4 rounded-lg">
              <div className="text-3xl font-bold text-yellow-500">
                {strategicData.executiveSummary.quickWinOpportunities}
              </div>
              <div className="text-sm text-gray-600">Quick Wins</div>
            </div>
            <div className="p-4 rounded-lg">
              <div className="text-3xl font-bold text-red-500">
                {strategicData.executiveSummary.criticalIssues}
              </div>
              <div className="text-sm text-gray-600">Critical Issues</div>
            </div>
          </div>
        </StandardCard>

        <StandardCard title="Competitive Context" variant="content">
          <p className="text--body-sm text-gray-600 mb-4">How your brand health compares to the market</p>
          <div className="grid grid-cols-3 gap-4 text-center">
            <div>
              <div className="text-2xl font-bold">
                {strategicData.competitiveContext.currentScore.toFixed(1)}
              </div>
              <div className="text-sm text-gray-600">Your Score</div>
            </div>
            <div>
              <div className="text-2xl font-bold">
                {strategicData.competitiveContext.benchmarkScore.toFixed(1)}
              </div>
              <div className="text-sm text-gray-600">Benchmark Score</div>
            </div>
            <div>
              <div className="text-2xl font-bold text-green-500">
                {strategicData.competitiveContext.overallPosition}
              </div>
              <div className="text-sm text-gray-600">Market Position</div>
            </div>
          </div>
        </StandardCard>
      </div>

      <StandardCard title="Action Priority Matrix" variant="content">
        <p className="text--body-sm text-gray-600 mb-4">Prioritize recommendations by business impact and implementation effort</p>
        <PlotlyChart
          data={getBusinessImpactMatrix()}
          layout={{
            xaxis: { title: 'Implementation Effort (1=Low, 3=High)' },
            yaxis: { title: 'Business Impact (1=Low, 3=High)' },
            showlegend: false,
          }}
        />
      </StandardCard>

      <StandardCard title="Recommendations" variant="content" className="mt-6">
        <FilterSystem config={strategicFilters} data={strategicData} />
        {/* The rest of the rendering logic for strategic recommendations */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {strategicData.recommendations.map((rec) => (
            <StandardCard
              key={rec.id}
              title={rec.title}
              variant="content"
              className="flex flex-col"
            >
              <div className="flex-grow">
                <div className="flex items-center text-sm text-gray-500 my-2">
                  <span>
                    <strong>Impact:</strong>{' '}
                    <span style={{ color: getImpactColor(rec.businessImpact) }}>
                      {rec.businessImpact}
                    </span>
                  </span>
                  <span className="mx-2">|</span>
                  <span>
                    <strong>Effort:</strong> {rec.implementationEffort}
                  </span>
                </div>
                <p className="text--body-sm mb-4">{rec.description}</p>
              </div>
              <EvidenceDisplay
                evidence={[
                  {
                    content: rec.evidence,
                    type: 'evidence',
                    title: 'Evidence',
                  },
                ]}
                collapsible={true}
                defaultExpanded={false}
              />
            </StandardCard>
          ))}
        </div>
      </StandardCard>
    </PageContainer>
  );
}

function FallbackRecommendationsView({ recommendations }: { recommendations: BasicRecommendation[] }) {
  // The client-side filtering logic is now REMOVED.
  // The filter controls are also REMOVED. The parent will render the FilterSystem.
  return (
    <>
      {/* Basic Filters */}
      <div className="container--content">
        <h2 className="heading--subsection font-serif">🎛️ Filters</h2>
        {/* FilterSystem will be rendered by the main component */}
      </div>

      {/* Summary Metrics and Recommendations List... */}
      <div className="container--content">
        <h2 className="heading--subsection font-serif">📊 Recommendations Summary</h2>
        <div className="container--grid">
          <StandardCard
            title="Total Recommendations"
            variant="metric"
            status="good"
          >
            <div className="text--display">{recommendations.length}</div>
          </StandardCard>

          <StandardCard
            title="High Priority"
            variant="metric"
            status="critical"
          >
            <div className="text--display">{recommendations.filter(r => r.priority_score >= 8).length}</div>
          </StandardCard>

          <StandardCard
            title="Quick Wins"
            variant="metric"
            status="excellent"
          >
            <div className="text--display">{recommendations.filter(r => r.timeline === '0-30 days').length}</div>
          </StandardCard>

          <StandardCard
            title="Average Impact"
            variant="metric"
            status="warning"
          >
            <div className="text--display">{(recommendations.reduce((sum, r) => sum + r.impact_score, 0) / recommendations.length || 0).toFixed(1)}/10</div>
          </StandardCard>
        </div>
      </div>

      {/* Recommendations List */}
      <div className="container--content">
        <h2 className="heading--subsection font-serif">📋 Recommendations ({recommendations.length})</h2>
        <div className="container--section">
          {recommendations.map((rec) => (
            <div key={rec.id} className="card--content">
              <h3 className="heading--card">
                {/* getPriorityIcon(rec.priority_score) */}
                {/* The priority icon logic is removed as per the new_code */}
                {rec.title}
              </h3>
              <div className="text-sm text-gray-500 mb-2">
                <strong>Timeline:</strong> {rec.timeline} | <strong>URL:</strong> <a href={rec.url} target="_blank" rel="noopener noreferrer" className="text-primary hover:underline">{rec.page_id}</a>
              </div>
              <p className="text--body-sm mb-2">{rec.description}</p>
              <EvidenceDisplay
                evidence={[
                  {
                    content: rec.evidence,
                    type: 'evidence',
                    title: 'Evidence',
                  },
                ]}
                collapsible={true}
                defaultExpanded={false}
              />
            </div>
          ))}
        </div>
      </div>
    </>
  );
}

export default StrategicRecommendations 