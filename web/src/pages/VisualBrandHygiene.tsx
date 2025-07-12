import { useEffect, useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import { Banner, BarChart, HeatmapChart, PlotlyChart, StandardCard, DataTable, PageContainer, PageHeader } from '../components';
import { EvidenceBrowser } from '../components/EvidenceDisplay';
import { createColumnHelper } from '@tanstack/react-table';
import { useFilters } from '../hooks/useFilters';
import { FilterSystem } from '../components/FilterSystem';
import type { FilterConfig } from '../types/filters';

interface BrandData {
  url: string
  page_type: string
  final_score: number
  logo_compliance: number
  color_palette: number
  typography: number
  layout_structure: number
  image_quality: number
  brand_messaging: number
  gating_penalties: number
  key_violations: string
  domain: string
  page_name: string
  tier_number: string
  tier_name: string
  region: string
}

interface PriorityItem {
  page: string
  page_type: string
  current_score: number
  business_impact: number
  implementation_effort: number
  roi_score: number
  priority_quadrant: string
  priority_color: string
  recommendations: string[]
  time_estimate: string
  cost_estimate: string
  potential_improvement: number
  issues: string
}

interface BrandColor {
  hex: string
  name: string
  description: string
  cmyk: string
}

const PRIMARY_COLORS: BrandColor[] = [
  { hex: '#4D1D82', name: 'Dark Purple', description: 'Primary brand color', cmyk: 'CMYK: 89/100/06/01' },
  { hex: '#8b1d82', name: 'Light Purple', description: 'Secondary brand color', cmyk: 'CMYK: 56/100/00/00' },
  { hex: '#cf022b', name: 'Red', description: 'Accent color', cmyk: 'CMYK: 10/100/95/00' },
  { hex: '#ef7d00', name: 'Orange', description: 'Accent color', cmyk: 'CMYK: 00/60/100/00' }
]

const SECONDARY_COLORS: BrandColor[] = [
  { hex: '#007ac2', name: 'Dark Blue', description: 'Supporting color', cmyk: '' },
  { hex: '#32abd0', name: 'Light Blue', description: 'Supporting color', cmyk: '' },
  { hex: '#00a188', name: 'Dark Green', description: 'Success states', cmyk: '' },
  { hex: '#95c11f', name: 'Light Green', description: 'Success states', cmyk: '' },
  { hex: '#ea5599', name: 'Pink', description: 'Highlight color', cmyk: '' },
  { hex: '#f7b90c', name: 'Yellow', description: 'Warning states', cmyk: '' }
]

const visualBrandFilters: FilterConfig[] = [
  {
    name: 'persona',
    label: 'Filter by Persona',
    type: 'select',
    defaultValue: 'All',
    options: [
      { value: 'All', label: 'All Personas' },
      { value: 'P1', label: 'The Benelux Cybersecurity Decision Maker' },
      { value: 'P2', label: 'The Benelux Strategic Business Leader' },
      { value: 'P3', label: 'The Benelux Transformation Programme Leader' },
      { value: 'P4', label: 'The Technical Influencer' },
      { value: 'P5', label: 'The BENELUX Technology Innovation Leader' },
    ],
  },
];

function VisualBrandHygiene() {
  const { filters, setAllFilters } = useFilters();

  useEffect(() => {
    const defaultFilters = visualBrandFilters.reduce((acc, f) => {
      acc[f.name] = f.defaultValue;
      return acc;
    }, {} as { [key: string]: any });
    setAllFilters(defaultFilters);
  }, [setAllFilters]);

  const { data, isLoading, error } = useQuery<BrandData[]>({
    queryKey: ['brand-hygiene', filters],
    queryFn: async () => {
      const params = new URLSearchParams(filters);
      const res = await fetch(`http://localhost:3000/api/brand-hygiene?${params.toString()}`);
      if (!res.ok) throw new Error('Failed to load brand hygiene data');
      return res.json();
    },
    enabled: Object.keys(filters).length > 0,
  });
  
  // Create table columns for DataTable
  const columnHelper = createColumnHelper<BrandData>()
  
  const tableColumns = [
    columnHelper.accessor('url', {
      header: 'Page',
      cell: (info) => info.getValue()?.replace('https://www.', '') || 'N/A'
    }),
    columnHelper.accessor('page_type', {
      header: 'Type',
      cell: (info) => info.getValue() || 'N/A'
    }),
    columnHelper.accessor('logo_compliance', {
      header: 'Logo',
      cell: (info) => info.getValue()?.toFixed(1) || '0.0'
    }),
    columnHelper.accessor('color_palette', {
      header: 'Color',
      cell: (info) => info.getValue()?.toFixed(1) || '0.0'
    }),
    columnHelper.accessor('typography', {
      header: 'Typography',
      cell: (info) => info.getValue()?.toFixed(1) || '0.0'
    }),
    columnHelper.accessor('layout_structure', {
      header: 'Layout',
      cell: (info) => info.getValue()?.toFixed(1) || '0.0'
    }),
    columnHelper.accessor('image_quality', {
      header: 'Images',
      cell: (info) => info.getValue()?.toFixed(1) || '0.0'
    }),
    columnHelper.accessor('brand_messaging', {
      header: 'Messaging',
      cell: (info) => info.getValue()?.toFixed(1) || '0.0'
    }),
    columnHelper.accessor('final_score', {
      header: 'Final Score',
      cell: (info) => info.getValue()?.toFixed(1) || '0.0'
    }),
    columnHelper.accessor('key_violations', {
      header: 'Key Violations',
      cell: (info) => {
        const violations = info.getValue() || ''
        return violations.length > 50 ? violations.substring(0, 50) + '...' : violations
      }
    })
  ]
  const [auditData, setAuditData] = useState<any[]>([])

  useEffect(() => {
    fetchAuditData()
  }, [])

  const fetchAuditData = async () => {
    try {
      // Fetch audit data with evidence for brand analysis via Node.js API
      const response = await fetch('http://localhost:3000/api/brand-hygiene')
      if (response.ok) {
        const data = await response.json()
        setAuditData(data)
      }
    } catch (err) {
      console.error('Failed to fetch audit data:', err)
      // Set empty array as fallback
      setAuditData([])
    }
  }

  const calculateOverallMetrics = () => {
    if (!data || data.length === 0) return { totalPages: 0, avgScore: 0, topPerformers: 0, complianceRate: 0 }
    
    const totalPages = data.length
    const avgScore = data.reduce((sum, item) => sum + item.final_score, 0) / totalPages
    const topPerformers = data.filter(item => item.final_score >= 8.5).length
    const complianceRate = (data.filter(item => item.final_score >= 8.0).length / totalPages) * 100
    
    return { totalPages, avgScore, topPerformers, complianceRate }
  }

  const getCriteriaAverages = () => {
    if (!data || data.length === 0) return {}
    
    const criteria = ['logo_compliance', 'color_palette', 'typography', 'layout_structure', 'image_quality', 'brand_messaging']
    return criteria.reduce((acc, criterion) => {
      acc[criterion] = data.reduce((sum, item) => {
        const value = item[criterion as keyof BrandData]
        return sum + (typeof value === 'number' ? value : 0)
      }, 0) / data.length
      return acc
    }, {} as Record<string, number>)
  }

  const getHeatmapData = () => {
    if (!data) return { x: [], y: [], z: [] };
    const tiers = [...new Set(data.map(item => item.tier_name))]
    const domains = [...new Set(data.map(item => item.domain))]
    
    const heatmapMatrix = tiers.map(tier => 
      domains.map(domain => {
        const items = data.filter(item => item.tier_name === tier && item.domain === domain)
        return items.length > 0 ? items.reduce((sum, item) => sum + item.final_score, 0) / items.length : 0
      })
    )
    
    return {
      z: heatmapMatrix,
      x: domains,
      y: tiers,
    }
  }

  const getRadarData = () => {
    const criteriaAvg = getCriteriaAverages()
    const criteriaLabels = ['Logo Compliance', 'Color Palette', 'Typography', 'Layout Structure', 'Image Quality', 'Brand Messaging']
    const criteriaKeys = ['logo_compliance', 'color_palette', 'typography', 'layout_structure', 'image_quality', 'brand_messaging']
    
    return {
      r: criteriaKeys.map(key => criteriaAvg[key] || 0),
      theta: criteriaLabels,
    }
  }

  const getTierAnalysisData = () => {
    if (!data) return { x: [], y: [] };
    const tierStats = data.reduce((acc, item) => {
      if (!acc[item.tier_name]) {
        acc[item.tier_name] = { scores: [], count: 0 }
      }
      acc[item.tier_name].scores.push(item.final_score)
      acc[item.tier_name].count++
      return acc
    }, {} as Record<string, { scores: number[], count: number }>)
    
    const tiers = Object.keys(tierStats)
    const avgScores = tiers.map(tier => {
      const scores = tierStats[tier].scores
      return scores.reduce((sum, score) => sum + score, 0) / scores.length
    })
    
    return {
      x: tiers,
      y: avgScores,
    }
  }

  const getRegionalAnalysisData = () => {
    if (!data) return { x: [], y: [] };
    const regionStats = data.reduce((acc, item) => {
      if (!acc[item.region]) {
        acc[item.region] = { scores: [], count: 0 }
      }
      acc[item.region].scores.push(item.final_score)
      acc[item.region].count++
      return acc
    }, {} as Record<string, { scores: number[], count: number }>)
    
    const regions = Object.keys(regionStats)
    const avgScores = regions.map(region => {
      const scores = regionStats[region].scores
      return scores.reduce((sum, score) => sum + score, 0) / scores.length
    })
    
    return {
      x: regions,
      y: avgScores,
    }
  }

  const generatePriorityData = (): PriorityItem[] => {
    if (!data) return [];
    return data.map(item => {
      const score = item.final_score || 0
      const violations = item.key_violations || ''
      const pageUrl = item.url?.replace('https://www.', '') || 'Unknown Page'
      const pageType = item.page_type || ''
      
      // Calculate Business Impact (0-10 scale) - Enhanced scoring from Streamlit
      let businessImpact = 9.0
      if (score < 6.0) {
        businessImpact = 9.0  // Critical - major brand damage
      } else if (score < 7.5) {
        businessImpact = 7.0  // High - significant improvement potential
      } else if (score < 8.5) {
        businessImpact = 5.0  // Medium - moderate improvement
      } else {
        businessImpact = 2.0  // Low - minor optimization
      }
      
      // Boost impact for strategic pages
      if (pageType.includes('Tier 1') || pageUrl.includes('homepage')) {
        businessImpact = Math.min(10.0, businessImpact + 2.0)
      } else if (pageType.includes('Tier 2')) {
        businessImpact = Math.min(10.0, businessImpact + 1.0)
      }
      
      // Calculate Implementation Effort (0-10 scale) - Enhanced from Streamlit
      const baseEffort = 3.0
      let implementationEffort = baseEffort
      
      if (violations.includes('Major') || violations.includes('Critical')) {
        implementationEffort = 8.0  // High effort - major restructuring
      } else if (violations.includes('Moderate') || violations.includes('Multiple')) {
        implementationEffort = 6.0  // Medium effort - several changes
      } else if (violations.includes('Minor') || violations.includes('Simple')) {
        implementationEffort = 3.0  // Low effort - quick fixes
      } else {
        // Estimate based on score gap
        const scoreGap = 10.0 - score
        implementationEffort = Math.min(8.0, baseEffort + (scoreGap * 0.8))
      }
      
      // Calculate ROI Score (Impact/Effort ratio)
      const roiScore = businessImpact / Math.max(implementationEffort, 1.0)
      
      // Determine priority quadrant (matches Streamlit logic)
      let priorityQuadrant = '❌ DON\'T DO'
      let priorityColor = '#EF4444'
      
      if (businessImpact >= 7.0 && implementationEffort <= 5.0) {
        priorityQuadrant = '🚀 DO FIRST'
        priorityColor = '#22C55E'
      } else if (businessImpact >= 7.0 && implementationEffort > 5.0) {
        priorityQuadrant = '📅 SCHEDULE'
        priorityColor = '#F59E0B'
      } else if (businessImpact < 7.0 && implementationEffort <= 5.0) {
        priorityQuadrant = '⚡ QUICK WIN'
        priorityColor = '#3B82F6'
      }
      
      // Generate specific recommendations (enhanced from Streamlit)
      const recommendations = []
      if (score < 6.0) {
        recommendations.push('🔴 URGENT: Complete brand compliance review')
      }
      if (violations.includes('Logo')) {
        recommendations.push('🎨 Update logo placement and sizing')
      }
      if (violations.includes('Color')) {
        recommendations.push('🌈 Implement brand color palette')
      }
      if (violations.includes('Typography')) {
        recommendations.push('📝 Apply brand typography standards')
      }
      if (violations.includes('Layout')) {
        recommendations.push('📐 Restructure page layout')
      }
      if (violations.includes('Image')) {
        recommendations.push('🖼️ Replace non-compliant imagery')
      }
      if (violations.includes('Messaging')) {
        recommendations.push('💬 Revise brand messaging')
      }
      if (recommendations.length === 0) {
        recommendations.push('✨ Minor brand consistency improvements')
      }
      
      // Estimate time and cost (matches Streamlit logic)
      let timeEstimate = '1-2 days'
      let costEstimate = '€500-1,500'
      if (implementationEffort <= 3.0) {
        timeEstimate = '1-2 days'
        costEstimate = '€500-1,500'
      } else if (implementationEffort <= 6.0) {
        timeEstimate = '1-2 weeks'
        costEstimate = '€2,000-5,000'
      } else {
        timeEstimate = '2-4 weeks'
        costEstimate = '€5,000-15,000'
      }
      
      return {
        page: pageUrl,
        page_type: pageType,
        current_score: score,
        business_impact: businessImpact,
        implementation_effort: implementationEffort,
        roi_score: roiScore,
        priority_quadrant: priorityQuadrant,
        priority_color: priorityColor,
        recommendations,
        time_estimate: timeEstimate,
        cost_estimate: costEstimate,
        potential_improvement: Math.min(2.5, (10.0 - score) * 0.7),
        issues: violations.length > 150 ? violations.substring(0, 150) + '...' : violations
      }
    })
  }

  const getPriorityMatrixData = () => {
    const priorityData = generatePriorityData()
    
    return priorityData.map(item => ({
      type: 'scatter' as const,
      mode: 'markers+text' as const,
      x: [item.implementation_effort],
      y: [item.business_impact],
      text: [item.page.length > 15 ? item.page.substring(0, 15) + '...' : item.page],
      textposition: 'top center' as const,
      marker: {
        size: item.current_score * 3,
        color: item.priority_color,
        opacity: 0.7,
        line: { width: 2, color: 'white' }
      },
      name: item.priority_quadrant,
      hovertemplate: `<b>${item.page}</b><br>Business Impact: ${item.business_impact.toFixed(1)}<br>Implementation Effort: ${item.implementation_effort.toFixed(1)}<br>Current Score: ${item.current_score.toFixed(1)}<extra></extra>`
    }))
  }

  if (isLoading) {
    return (
      <div className="container--layout">
        <Banner
          message={
            <div className="text-center">
              <div className="loader--state"></div>
              <p className="text--body">Loading visual brand hygiene analysis...</p>
            </div>
          }
        />
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
              <p className="text--body">{error.message}</p>
              <button onClick={() => window.location.reload()} className="button--primary">
                🔄 Retry
              </button>
            </>
          }
        />
      </div>
    );
  }

  const { totalPages, avgScore, topPerformers, complianceRate } = calculateOverallMetrics();
  const [activeTab, setActiveTab] = useState('criteria');

  return (
    <PageContainer title="🎨 Visual Brand Hygiene">
      <PageHeader
        title="🎨 Visual Brand Hygiene"
        description="Detailed analysis of visual brand consistency and user experience"
      />
      <p className="text--body">
        Comprehensive analysis of brand consistency across digital properties.
      </p>

      {/* Key Metrics */}
      <div className="grid--layout-4-col">
        <StandardCard title="Total Pages Audited" value={totalPages} />
        <StandardCard title="Average Brand Score" value={`${avgScore.toFixed(1)} / 10`} />
        <StandardCard title="Top Performers (Score > 8.5)" value={topPerformers} />
        <StandardCard title="Compliance Rate (Score > 8.0)" value={`${complianceRate.toFixed(0)}%`} />
      </div>

      {/* Main Analysis Tabs */}
      <div className="container--section">
        <div className="tabs">
            <button 
              className={`tabs__button ${activeTab === 'criteria' ? 'tabs__button--active' : ''}`}
              onClick={() => setActiveTab('criteria')}
            >
              📊 Criteria Performance
            </button>
            <button 
              className={`tabs__button ${activeTab === 'tier' ? 'tabs__button--active' : ''}`}
              onClick={() => setActiveTab('tier')}
            >
              🏢 Tier Analysis
            </button>
            <button 
              className={`tabs__button ${activeTab === 'regional' ? 'tabs__button--active' : ''}`}
              onClick={() => setActiveTab('regional')}
            >
              🌍 Regional Consistency
            </button>
            <button 
              className={`tabs__button ${activeTab === 'priority' ? 'tabs__button--active' : ''}`}
              onClick={() => setActiveTab('priority')}
            >
              🔧 Fix Prioritization
            </button>
            <button 
              className={`tabs__button ${activeTab === 'standards' ? 'tabs__button--active' : ''}`}
              onClick={() => setActiveTab('standards')}
            >
              📖 Brand Standards
            </button>
            <button 
              className={`tabs__button ${activeTab === 'evidence' ? 'tabs__button--active' : ''}`}
              onClick={() => setActiveTab('evidence')}
            >
              🔍 Evidence Examples
            </button>
        </div>

        <div className="tabs--content">
          {/* Criteria Performance Tab */}
          {activeTab === 'criteria' && (
            <div className="grid--layout-2-col">
              <StandardCard title="Overall Criteria Performance">
                <BarChart
                  x={getRadarData().theta}
                  y={getRadarData().r}
                  title="Brand Criteria Radar"
                />
              </StandardCard>
              <StandardCard title="Performance Heatmap (Tier vs. Domain)">
                <HeatmapChart
                  x={getHeatmapData().x}
                  y={getHeatmapData().y}
                  z={getHeatmapData().z}
                  title="Tier vs. Domain Heatmap"
                />
              </StandardCard>
              <div className="card--data table-container">
                <h3 className="heading--card">Detailed Criteria Scores</h3>
                <DataTable columns={tableColumns} data={data || []} />
              </div>
            </div>
          )}

          {/* Tier Analysis Tab */}
          {activeTab === 'tier' && (
            <div className="grid--layout-1-col">
              <StandardCard title="Average Score by Content Tier">
                <BarChart
                  x={getTierAnalysisData().x}
                  y={getTierAnalysisData().y}
                  title="Tier Performance"
                />
              </StandardCard>
            </div>
          )}

          {/* Regional Consistency Tab */}
          {activeTab === 'regional' && (
            <div className="grid--layout-1-col">
              <StandardCard title="Brand Score by Region">
                <BarChart
                  x={getRegionalAnalysisData().x}
                  y={getRegionalAnalysisData().y}
                  title="Regional Performance"
                />
              </StandardCard>
            </div>
          )}

          {/* Fix Prioritization Tab */}
          {activeTab === 'priority' && (
            <div className="grid--layout-1-col">
              <StandardCard title="Fix Prioritization Matrix (ROI vs. Effort)">
                <PlotlyChart data={getPriorityMatrixData()} layout={{ title: 'Prioritization Matrix' }} />
              </StandardCard>
            </div>
          )}

          {/* Brand Standards Tab */}
          {activeTab === 'standards' && (
            <div className="container--content">
              <h2 className="heading--section">📖 Brand Standards Reference</h2>
              <div>
                <h3 className="heading--subsection">Primary Brand Colors</h3>
                <div className="grid--layout-4-col">
                  {PRIMARY_COLORS.map(color => (
                    <StandardCard key={color.hex} title={color.name} variant="metric">
                      <div style={{ background: color.hex, height: '50px', width: '100%', borderRadius: 'var(--border-radius)' }} />
                      <p>{color.hex}</p>
                      <p>{color.cmyk}</p>
                    </StandardCard>
                  ))}
                </div>
              </div>
              <div>
                <h3 className="heading--subsection">Secondary Brand Colors</h3>
                <div className="grid--layout-3-col">
                  {SECONDARY_COLORS.map(color => (
                    <StandardCard key={color.hex} title={color.name} variant="metric">
                      <div style={{ background: color.hex, height: '50px', width: '100%', borderRadius: 'var(--border-radius)' }} />
                      <p>{color.hex}</p>
                    </StandardCard>
                  ))}
                </div>
              </div>
              <div>
                <h3 className="heading--subsection">Typography Guidelines</h3>
                <div className="card--typography">
                  <p><strong>H1 (Page Title):</strong> Font Family: var(--font-serif), Font Size: var(--font-size-h1)</p>
                  <p><strong>H2 (Section):</strong> Font Family: var(--font-serif), Font Size: var(--font-size-h2)</p>
                  <p><strong>Body:</strong> Font Family: var(--font-primary), Font Size: var(--font-size-base)</p>
                </div>
              </div>
            </div>
          )}

          {activeTab === 'evidence' && (
            <div className="container--content">
              <h2 className="heading--section">🔍 Evidence Examples & Trust Signals</h2>
              <FilterSystem config={visualBrandFilters} data={{}} />
              <EvidenceBrowser 
                data={auditData} // This seems to be from a different fetch, leaving as is for now
                evidenceColumns={['key_violations', 'brand_messaging']}
              />
            </div>
          )}
        </div>
      </div>

      {/* Export Options */}
      <div className="container--section">
        <h2 className="heading--section">Export & Reporting</h2>
        <div className="button-group">
          <button className="button button--success" onClick={() => alert('Full brand hygiene report exported!')}>
            📊 Export Full Report
          </button>
          <button className="button button--secondary" onClick={() => alert('Executive summary generated!')}>
            📄 Generate Summary
          </button>
          <button className="button button--secondary" onClick={() => alert('Re-audit scheduled!')}>
            🔄 Schedule Re-Audit
          </button>
        </div>
      </div>

      {/* Sidebar Quick Insights - matches Streamlit version */}
      <div className="sidebar-insights">
        <div className="container--card">
          <h3>Quick Insights</h3>
          
          {data && data.length > 0 && (
            <>
              <Banner
                type="success"
                message={
                  <div className="d-flex align-items-center">
                    <div className="insight-icon">🌟</div>
                    <div className="container--content">
                      <strong>Top Performer:</strong>
                      <p>{data.reduce((prev, current) => (prev.final_score > current.final_score) ? prev : current).page_name}</p>
                    </div>
                  </div>
                }
              />
              <Banner
                type="warning"
                message={
                  <div className="d-flex align-items-center">
                    <div className="insight-icon">🔧</div>
                    <div className="container--content">
                      <strong>Biggest Improvement Opportunity:</strong>
                      <p>{data.reduce((prev, current) => (prev.final_score < current.final_score) ? prev : current).page_name}</p>
                    </div>
                  </div>
                }
              />
            </>
          )}
          
          <div className="quick-stats">
            <h4>Quick Stats</h4>
            {data && data.length > 0 && (
              <div className="grid--layout-3-col">
                <StandardCard 
                  title="Avg Logo Score" 
                  value={`${(data.reduce((sum, item) => sum + item.logo_compliance, 0) / data.length).toFixed(1)}/10`} 
                />
                <StandardCard 
                  title="Avg Color Score" 
                  value={`${(data.reduce((sum, item) => sum + item.color_palette, 0) / data.length).toFixed(1)}/10`} 
                />
                <StandardCard 
                  title="Avg Typography" 
                  value={`${(data.reduce((sum, item) => sum + item.typography, 0) / data.length).toFixed(1)}/10`} 
                />
              </div>
            )}
          </div>
        </div>
      </div>
    </PageContainer>
  );
}

export default VisualBrandHygiene;
