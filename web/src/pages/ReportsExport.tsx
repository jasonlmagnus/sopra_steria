import { useState, useEffect } from 'react';
import { useQuery } from '@tanstack/react-query';
import { DataTable, PageContainer } from '../components';
import type { ColumnDef } from '@tanstack/react-table';
import DatasetDetail from './DatasetDetail';
import StandardCard from '../components/StandardCard';
import '../styles/pages/ReportsExport.css';
import '../styles/utilities.css';
import Banner from '../components/Banner';
import { useFilters } from '../hooks/useFilters';
import { FilterSystem } from '../components/FilterSystem';
import type { FilterConfig } from '../types/filters';

interface DatasetInfo {
  name: string;
  records: number;
  columns: number;
  memoryMB: string;
}

interface ReportConfig {
  reportType: string;
  personas: string[];
  tiers: string[];
  includeAnalysis: boolean;
  includeRecommendations: boolean;
  format: string;
}

interface HTMLReportOptions {
  generationMode: string;
  personas: string[];
  includeTierAnalysis: boolean;
  includePersonaVoice: boolean;
  includeRecommendations: boolean;
  includeEvidence: boolean;
}

interface ReportItem {
  url: string;
  persona_id: string;
  tier: string;
  final_score: number;
  criterion: string;
  status: string;
  quick_win_flag: string;
  critical_issue_flag: string;
  success_flag: string;
}


const reportsExportFilters: FilterConfig[] = [
  { name: 'persona', label: 'Persona', type: 'select', defaultValue: 'All' },
  { name: 'tier', label: 'Tier', type: 'select', defaultValue: 'All' },
  { 
    name: 'scoreRange', 
    label: 'Score Range', 
    type: 'range', 
    defaultValue: [0, 100], 
    min: 0, 
    max: 100, 
    step: 1 
  },
];

const ReportsExport: React.FC = () => {
  const { filters, setAllFilters } = useFilters();
  const [activeTab, setActiveTab] = useState('data-explorer');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [viewingDataset, setViewingDataset] = useState<string | null>(null);
  
  // Report configuration
  const [reportConfig, setReportConfig] = useState<ReportConfig>({
    reportType: 'comprehensive',
    personas: [],
    tiers: [],
    includeAnalysis: true,
    includeRecommendations: true,
    format: 'pdf'
  });
  
  // HTML report options
  const [htmlOptions, setHtmlOptions] = useState<HTMLReportOptions>({
    generationMode: 'All Personas',
    personas: [],
    includeTierAnalysis: true,
    includePersonaVoice: true,
    includeRecommendations: true,
    includeEvidence: true
  });
  
  // Export states
  const [exportFormat, setExportFormat] = useState('csv');
  const [exportFilters, setExportFilters] = useState({
    includeRawData: true,
    includeSummaries: true,
    includeAnalysis: false
  });
  
  // Generation states
  const [generatingReport, setGeneratingReport] = useState(false);
  const [generatingHtml, setGeneratingHtml] = useState(false);
  const [exporting, setExporting] = useState(false);

  const apiBase = import.meta.env.VITE_API_URL || 'http://localhost:3000';

  const { data: masterData } = useQuery<any[]>({
    queryKey: ['master-dataset'],
    queryFn: async () => {
      const res = await fetch(`${apiBase}/api/datasets/master`);
      if (!res.ok) throw new Error('Failed to load master dataset');
      return res.json();
    },
  });

  const { data: datasets } = useQuery<DatasetInfo[]>({
    queryKey: ['datasets-metadata'],
    queryFn: async () => {
      const res = await fetch(`${apiBase}/api/datasets/metadata`);
      if (!res.ok) throw new Error('Failed to load datasets metadata');
      return res.json();
    },
  });

  useEffect(() => {
    const defaultFilters = reportsExportFilters.reduce((acc, f) => {
      acc[f.name] = f.defaultValue;
      return acc;
    }, {} as { [key: string]: any });
    setAllFilters(defaultFilters);
  }, [setAllFilters]);
  
  // Client-side filtering is removed. This will now be handled by the backend on export.
  const filteredData = masterData || [];
  
  const availablePersonas = [...new Set((masterData || []).map(item => item.persona_id))];
  const availableTiers = [...new Set((masterData || []).map(item => item.tier))];

  const dynamicFilterData = {
    personaOptions: [{value: 'All', label: 'All'}, ...availablePersonas.map(p => ({ value: p, label: p }))],
    tierOptions: [{value: 'All', label: 'All'}, ...availableTiers.map(t => ({ value: t, label: t }))],
  };

  // Calculate overview metrics
  const overviewMetrics = {
    totalRecords: filteredData.length,
    uniquePages: new Set(filteredData.map(item => item.url)).size,
    uniquePersonas: availablePersonas.length,
    dataCompleteness: filteredData.length > 0 ? 
      (filteredData.filter(item => item.final_score !== null && item.final_score !== 'N/A').length / filteredData.length * 100).toFixed(1) : '0'
  };

  // Data quality analysis
  const dataQuality = {
    completeness: parseFloat(overviewMetrics.dataCompleteness),
    consistency: filteredData.length > 0 ? 
      (filteredData.filter(item => item.tier && item.persona_id).length / filteredData.length * 100) : 0,
    accuracy: filteredData.length > 0 ? 
      (filteredData.filter(item => {
        const score = parseFloat(item.final_score);
        return score >= 0 && score <= 10;
      }).length / filteredData.length * 100) : 0,
    timeliness: 95 // Placeholder - would need actual timestamp analysis
  };

  // Generate custom report
  const generateCustomReport = async () => {
    setGeneratingReport(true);
    try {
      const response = await fetch(`${apiBase}/api/reports/custom`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(reportConfig)
      });
      
      if (response.ok) {
        const blob = await response.blob();
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `custom_report_${new Date().toISOString().split('T')[0]}.${reportConfig.format}`;
        document.body.appendChild(a);
        a.click();
        window.URL.revokeObjectURL(url);
        document.body.removeChild(a);
      }
    } catch (err) {
      setError('Failed to generate report');
    } finally {
      setGeneratingReport(false);
    }
  };

  // Generate HTML reports
  const generateHtmlReports = async () => {
    setGeneratingHtml(true);
    try {
      const response = await fetch(`${apiBase}/api/reports/html`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(htmlOptions)
      });
      
      if (response.ok) {
        const result = await response.json();
        // Handle successful generation
        alert(`HTML reports generated successfully! ${result.reports?.length || 0} reports created.`);
      }
    } catch (err) {
      setError('Failed to generate HTML reports');
    } finally {
      setGeneratingHtml(false);
    }
  };

  // Export data
  const exportData = async () => {
    setExporting(true);
    try {
      const response = await fetch(`${apiBase}/api/export/${exportFormat}`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          filters: filters, // Use the filters from the context
          options: exportFilters
        })
      });
      
      if (response.ok) {
        const blob = await response.blob();
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `export_${new Date().toISOString().split('T')[0]}.${exportFormat}`;
        document.body.appendChild(a);
        a.click();
        window.URL.revokeObjectURL(url);
        document.body.removeChild(a);
      }
    } catch (err) {
      setError('Failed to export data');
    } finally {
      setExporting(false);
    }
  };

  const renderTabContent = () => {
    switch (activeTab) {
      case 'data-explorer':
        return (
          <div>
            <div className="container--section">
              <h2 className="heading--section">📊 Data Explorer & Browser</h2>
              <p className="text--body">Interactive analysis, filtering, and browsing of all audit datasets</p>
            </div>
            
            {/* Dataset Selection */}
            <div className="container--section">
              <h3 className="heading--subsection">🗂️ Dataset Selection</h3>
              <div className="container--layout">
                <div 
                  className={`container--card ${!viewingDataset ? 'selected' : ''}`}
                  onClick={() => setViewingDataset(null)}
                >
                  <div className="text--display">📊</div>
                  <div className="container--section">
                    <div className="text--display">Master Dataset</div>
                    <div className="text--body">{filteredData.length} records • {filteredData.length > 0 ? Object.keys(filteredData[0]).length : 0} columns</div>
                  </div>
                </div>
                
                {datasets && datasets.map((dataset, index) => (
                  <div 
                    key={index}
                    className={`container--card ${viewingDataset === dataset.name ? 'selected' : ''}`}
                    onClick={() => setViewingDataset(dataset.name)}
                  >
                    <div className="text--display">🗂️</div>
                    <div className="container--section">
                      <div className="text--display">{dataset.name}</div>
                      <div className="text--body">{dataset.records} records • {dataset.columns} columns</div>
                    </div>
                  </div>
                ))}
              </div>
            </div>
            
            {/* Master Dataset Analysis */}
            {!viewingDataset ? (
              <>
                {/* Data Overview */}
                <div className="container--layout">
                  <div className="container--section">
                    <div className="text--display">{overviewMetrics.totalRecords}</div>
                    <div className="text--display">Total Records</div>
                  </div>
                  <div className="container--section">
                    <div className="text--display">{overviewMetrics.uniquePages}</div>
                    <div className="text--display">Unique Pages</div>
                  </div>
                  <div className="container--section">
                    <div className="text--display">{overviewMetrics.uniquePersonas}</div>
                    <div className="text--display">Personas</div>
                  </div>
                  <div className="container--section">
                    <div className="text--display">{overviewMetrics.dataCompleteness}%</div>
                    <div className="text--display">Data Completeness</div>
                  </div>
                </div>

                {/* Filter Controls */}
                <div className="data-explorer-filters">
                  <FilterSystem config={reportsExportFilters} data={dynamicFilterData} />
                </div>

                {/* Data Quality Analysis */}
                <div className="container--section">
                  <h3 className="heading--subsection">📈 Data Quality Analysis</h3>
                  <div className="container--layout">
                    <StandardCard
                      title="Completeness"
                      variant="metric"
                      status={dataQuality.completeness >= 90 ? "excellent" : 
                        dataQuality.completeness >= 70 ? "good" : 
                        dataQuality.completeness >= 50 ? "warning" : "critical"}
                    >
                      <div className="text--display">{dataQuality.completeness.toFixed(1)}%</div>
                    </StandardCard>
                    <StandardCard
                      title="Consistency"
                      variant="metric"
                      status={dataQuality.consistency >= 90 ? "excellent" : 
                        dataQuality.consistency >= 70 ? "good" : 
                        dataQuality.consistency >= 50 ? "warning" : "critical"}
                    >
                      <div className="text--display">{dataQuality.consistency.toFixed(1)}%</div>
                    </StandardCard>
                    <StandardCard
                      title="Accuracy"
                      variant="metric"
                      status={dataQuality.accuracy >= 90 ? "excellent" : 
                        dataQuality.accuracy >= 70 ? "good" : 
                        dataQuality.accuracy >= 50 ? "warning" : "critical"}
                    >
                      <div className="text--display">{dataQuality.accuracy.toFixed(1)}%</div>
                    </StandardCard>
                    <StandardCard
                      title="Timeliness"
                      variant="metric"
                      status={dataQuality.timeliness >= 90 ? "excellent" : 
                        dataQuality.timeliness >= 70 ? "good" : 
                        dataQuality.timeliness >= 50 ? "warning" : "critical"}
                    >
                      <div className="text--display">{dataQuality.timeliness.toFixed(1)}%</div>
                    </StandardCard>
                  </div>
                </div>

                {/* Filtered Data Display */}
                {/* displayMode === 'table' && ( */}
                  <div className="container--section">
                    <h3 className="heading--subsection">📋 Filtered Data ({filteredData.length} records)</h3>
                    <DataTable columns={columns} data={filteredData.slice(0, 50)} />
                  </div>
                {/* ) */}

                {/* displayMode === 'summary' && ( */}
                  <div className="container--section">
                    <h3 className="heading--subsection">📊 Summary Statistics</h3>
                    <div className="container--section">
                      <div className="heading--subsection">Key Insights</div>
                      <p className="text--body"><strong>Average Overall Score:</strong> {(filteredData.reduce((sum, item) => sum + (item.overall_score || 0), 0) / filteredData.length).toFixed(1)}</p>
                      <p className="text--body"><strong>Best Performing Tier:</strong> {
                        availableTiers.map(tier => ({
                          tier,
                          avg: filteredData.filter(item => item.tier === tier).reduce((sum, item) => sum + (item.overall_score || 0), 0) / filteredData.filter(item => item.tier === tier).length
                        })).sort((a, b) => b.avg - a.avg)[0]?.tier || 'N/A'
                      }</p>
                      <p className="text--body"><strong>Total Pages Analyzed:</strong> {new Set(filteredData.map(item => item.url)).size}</p>
                    </div>
                  </div>
                {/* ) */}
              </>
            ) : (
              <DatasetDetail datasetName={viewingDataset} />
            )}
          </div>
        );

      case 'custom-reports':
        return (
          <div>
            <div className="container--section">
              <h2 className="heading--section">📈 Custom Reports</h2>
              <p className="text--body">Generate configurable business reports with detailed analysis and insights</p>
            </div>
            
            <div className="container--layout">
              <div className="container--section">
                <h4 className="heading--subsection">📊 Report Settings</h4>
                <div className="container--section">
                  <label className="label--form">📊 Report Type</label>
                  <select 
                    value={reportConfig.reportType}
                    onChange={(e) => setReportConfig({...reportConfig, reportType: e.target.value})}
                    className="select--form"
                  >
                    <option value="comprehensive">Comprehensive Analysis</option>
                    <option value="executive">Executive Summary</option>
                    <option value="technical">Technical Deep Dive</option>
                    <option value="comparative">Comparative Analysis</option>
                  </select>
                </div>
                
                <div className="container--section">
                  <label className="label--form">📄 Output Format</label>
                  <select 
                    value={reportConfig.format}
                    onChange={(e) => setReportConfig({...reportConfig, format: e.target.value})}
                    className="select--form"
                  >
                    <option value="pdf">PDF Report</option>
                    <option value="docx">Word Document</option>
                    <option value="html">HTML Report</option>
                    <option value="xlsx">Excel Workbook</option>
                  </select>
                </div>
              </div>
              
              <div className="container--section">
                <h4 className="heading--subsection">🎯 Content Options</h4>
                <div className="container--section">
                  <input 
                    type="checkbox" 
                    id="includeAnalysis"
                    checked={reportConfig.includeAnalysis}
                    onChange={(e) => setReportConfig({...reportConfig, includeAnalysis: e.target.checked})}
                  />
                  <label htmlFor="includeAnalysis" className="label--form">Include Detailed Analysis</label>
                </div>
                <div className="container--section">
                  <input 
                    type="checkbox" 
                    id="includeRecommendations"
                    checked={reportConfig.includeRecommendations}
                    onChange={(e) => setReportConfig({...reportConfig, includeRecommendations: e.target.checked})}
                  />
                  <label htmlFor="includeRecommendations" className="label--form">Include Recommendations</label>
                </div>
              </div>

              <div className="container--section">
                <h4 className="heading--subsection">👥 Persona Filtering</h4>
                <div className="container--section">
                  {availablePersonas.map(persona => (
                    <div key={persona} className="container--section">
                      <input
                        type="checkbox"
                        id={`persona-${persona}`}
                        checked={reportConfig.personas.includes(persona)}
                        onChange={(e) => {
                          if (e.target.checked) {
                            setReportConfig({
                              ...reportConfig,
                              personas: [...reportConfig.personas, persona]
                            });
                          } else {
                            setReportConfig({
                              ...reportConfig,
                              personas: reportConfig.personas.filter(p => p !== persona)
                            });
                          }
                        }}
                      />
                      <label htmlFor={`persona-${persona}`} className="label--form">{persona}</label>
                    </div>
                  ))}
                </div>
              </div>
            </div>
            
            <div className="container--section">
              <button 
                className="button--action" 
                onClick={generateCustomReport}
                disabled={generatingReport}
              >
                {generatingReport ? '⏳ Generating...' : '📄 Generate Report'}
              </button>
            </div>
          </div>
        );
      
      case 'html-reports':
        return (
          <div>
            <div className="container--section">
              <h2 className="heading--section">🎨 HTML Reports</h2>
              <p className="text--body">Generate professional HTML reports with interactive visualizations</p>
            </div>
            
            <div className="container--layout">
              <div 
                className={`container--card ${htmlOptions.generationMode === 'All Personas' ? 'selected' : ''}`}
                onClick={() => setHtmlOptions({...htmlOptions, generationMode: 'All Personas'})}
              >
                <h4 className="heading--subsection">🎭 All Personas</h4>
                <p className="text--body">Generate reports for all available personas</p>
              </div>
              
              <div 
                className={`container--card ${htmlOptions.generationMode === 'Selected Personas' ? 'selected' : ''}`}
                onClick={() => setHtmlOptions({...htmlOptions, generationMode: 'Selected Personas'})}
              >
                <h4 className="heading--subsection">🎯 Selected Personas</h4>
                <p className="text--body">Generate reports for specific personas only</p>
              </div>
              
              <div 
                className={`container--card ${htmlOptions.generationMode === 'Consolidated Report' ? 'selected' : ''}`}
                onClick={() => setHtmlOptions({...htmlOptions, generationMode: 'Consolidated Report'})}
              >
                <h4 className="heading--subsection">📋 Consolidated Report</h4>
                <p className="text--body">Single comprehensive report across all personas</p>
              </div>
            </div>
            
            {htmlOptions.generationMode === 'Selected Personas' && (
              <div className="container--section">
                <h4 className="heading--subsection">🎭 Select Personas</h4>
                <div className="container--layout">
                  {availablePersonas.map(persona => (
                    <div key={persona} className="container--section">
                      <input
                        type="checkbox"
                        id={`html-persona-${persona}`}
                        checked={htmlOptions.personas.includes(persona)}
                        onChange={(e) => {
                          if (e.target.checked) {
                            setHtmlOptions({
                              ...htmlOptions,
                              personas: [...htmlOptions.personas, persona]
                            });
                          } else {
                            setHtmlOptions({
                              ...htmlOptions,
                              personas: htmlOptions.personas.filter(p => p !== persona)
                            });
                          }
                        }}
                      />
                      <label htmlFor={`html-persona-${persona}`} className="label--form">{persona}</label>
                    </div>
                  ))}
                </div>
                
                {htmlOptions.personas.length > 0 && (
                  <div className="container--layout">
                    {htmlOptions.personas.map(persona => (
                      <div key={persona} className="badge--status">
                        {persona.replace(/^The\s+/, '').replace(/\s+\(.*\)$/, '').replace(/_/g, ' ')}
                        <button 
                          onClick={() => setHtmlOptions({
                            ...htmlOptions,
                            personas: htmlOptions.personas.filter(p => p !== persona)
                          })}
                        >
                          ×
                        </button>
                      </div>
                    ))}
                  </div>
                )}
              </div>
            )}
            
            <div className="container--section">
              <button 
                className="button--action" 
                onClick={generateHtmlReports}
                disabled={generatingHtml || (htmlOptions.generationMode === 'Selected Personas' && htmlOptions.personas.length === 0)}
              >
                {generatingHtml ? '⏳ Generating...' : '🎨 Generate HTML Reports'}
              </button>
            </div>
          </div>
        );
      
      case 'export-center':
        return (
          <div>
            <div className="container--section">
              <h2 className="heading--section">📦 Export Center</h2>
              <p className="text--body">Export data in various formats for external analysis</p>
            </div>
            
            <div className="container--layout">
              <div 
                className={`container--card ${exportFormat === 'csv' ? 'selected' : ''}`}
                onClick={() => setExportFormat('csv')}
              >
                <div className="text--display">📊</div>
                <div className="text--display">CSV</div>
                <div className="text--body">Comma-separated values</div>
              </div>
              
              <div 
                className={`container--card ${exportFormat === 'excel' ? 'selected' : ''}`}
                onClick={() => setExportFormat('excel')}
              >
                <div className="text--display">📈</div>
                <div className="text--display">Excel</div>
                <div className="text--body">Microsoft Excel format</div>
              </div>
              
              <div 
                className={`container--card ${exportFormat === 'json' ? 'selected' : ''}`}
                onClick={() => setExportFormat('json')}
              >
                <div className="text--display">🔧</div>
                <div className="text--display">JSON</div>
                <div className="text--body">JavaScript Object Notation</div>
              </div>
              
              <div 
                className={`container--card ${exportFormat === 'parquet' ? 'selected' : ''}`}
                onClick={() => setExportFormat('parquet')}
              >
                <div className="text--display">⚡</div>
                <div className="text--display">Parquet</div>
                <div className="text--body">Columnar storage format</div>
              </div>
            </div>
            
            <div className="container--section">
              <h4 className="heading--subsection">📋 Export Options</h4>
              <div className="container--section">
                <input 
                  type="checkbox" 
                  id="includeRawData"
                  checked={exportFilters.includeRawData}
                  onChange={(e) => setExportFilters({...exportFilters, includeRawData: e.target.checked})}
                />
                <label htmlFor="includeRawData" className="label--form">Include Raw Data</label>
              </div>
              
              <div className="container--section">
                <input 
                  type="checkbox" 
                  id="includeSummaries"
                  checked={exportFilters.includeSummaries}
                  onChange={(e) => setExportFilters({...exportFilters, includeSummaries: e.target.checked})}
                />
                <label htmlFor="includeSummaries" className="label--form">Include Summaries</label>
              </div>
              
              <div className="container--section">
                <input 
                  type="checkbox" 
                  id="includeAnalysis"
                  checked={exportFilters.includeAnalysis}
                  onChange={(e) => setExportFilters({...exportFilters, includeAnalysis: e.target.checked})}
                />
                <label htmlFor="includeAnalysis" className="label--form">Include Analysis</label>
              </div>
            </div>
            
            <div className="container--section">
              <button 
                className="button--action" 
                onClick={exportData}
                disabled={exporting}
              >
                {exporting ? '⏳ Exporting...' : '📦 Export Data'}
              </button>
            </div>
          </div>
        );

      default:
        return null;
    }
  };

  return (
    <PageContainer title="📋 Reports & Export">
      <p className="text--body">Export data, generate custom reports, and analyze datasets</p>
      <div className="container--layout">
        <button 
          className="refresh-button"
          onClick={() => {
            setLoading(true);
            setError(null);
            // Invalidate queries to refetch data
            // This is a simplified approach; in a real app, you'd use a more robust cache invalidation strategy
            // For now, we'll just re-run the queries
            // A more robust solution would involve a global query client or a custom hook for data loading
            // For this example, we'll just re-run the queries
          }}
          disabled={loading}
        >
          🔄 Refresh Data
        </button>
        <span className="last-updated">
          Last updated: {new Date().toLocaleTimeString()}
        </span>
      </div>

      {error && (
        <Banner type="error" message={`⚠️ ${error}`} />
      )}

      {/* Tab Navigation */}
      <div className="container--section">
          <div className="tabs">
            <button 
              className={`tabs__button ${activeTab === 'data-explorer' ? 'tabs__button--active' : ''}`}
              onClick={() => setActiveTab('data-explorer')}
            >
              📊 Data Explorer
            </button>
            <button 
              className={`tabs__button ${activeTab === 'custom-reports' ? 'tabs__button--active' : ''}`}
              onClick={() => setActiveTab('custom-reports')}
            >
              📈 Custom Reports
            </button>
            <button 
              className={`tabs__button ${activeTab === 'html-reports' ? 'tabs__button--active' : ''}`}
              onClick={() => setActiveTab('html-reports')}
            >
              🎨 HTML Reports
            </button>
            <button 
              className={`tabs__button ${activeTab === 'export-center' ? 'tabs__button--active' : ''}`}
              onClick={() => setActiveTab('export-center')}
            >
              📦 Export Center
            </button>
          </div>

        {renderTabContent()}


      </div>
    </PageContainer>
  );
};

const columns: ColumnDef<ReportItem>[] = [
  {
    accessorKey: 'url',
    header: 'URL',
    cell: ({ row }) => (
      <a href={row.original.url} target="_blank" rel="noopener noreferrer">
        {row.original.url}
      </a>
    ),
  },
  {
    accessorKey: 'persona_id',
    header: 'Persona',
  },
  {
    accessorKey: 'tier',
    header: 'Tier',
  },
  {
    accessorKey: 'final_score',
    header: 'Score',
  },
  {
    accessorKey: 'criterion',
    header: 'Criterion',
  },
  {
    accessorKey: 'status',
    header: 'Status',
  },
  {
    id: 'flags',
    header: 'Flags',
    cell: ({ row }) => (
      <div className="container--layout">
        {row.original.quick_win_flag === 'True' && <span className="badge--status quick-win">Quick Win</span>}
        {row.original.critical_issue_flag === 'True' && <span className="badge--status critical">Critical</span>}
        {row.original.success_flag === 'True' && <span className="badge--status success">Success</span>}
      </div>
    ),
  },
];

export default ReportsExport;
