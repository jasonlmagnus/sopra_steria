import { useState, useEffect } from 'react';
import DatasetDetail from './DatasetDetail';
import StandardCard from '../components/StandardCard';
import '../styles/pages/ReportsExport.css';

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

const ReportsExport: React.FC = () => {
  const [activeTab, setActiveTab] = useState('data-explorer');
  const [loading, setLoading] = useState(false);
  const [masterData, setMasterData] = useState<any[]>([]);
  const [datasets, setDatasets] = useState<DatasetInfo[]>([]);
  const [error, setError] = useState<string | null>(null);
  const [viewingDataset, setViewingDataset] = useState<string | null>(null);
  
  // Filter states
  const [personaFilter, setPersonaFilter] = useState('All');
  const [tierFilter, setTierFilter] = useState('All');
  const [scoreRange, setScoreRange] = useState([0, 100]);
  const [displayMode, setDisplayMode] = useState('table');
  
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

  // Data loading
  useEffect(() => {
    loadData();
  }, []);

  const loadData = async () => {
    setLoading(true);
    setError(null);
    
    try {
      // Load master dataset
      const masterResponse = await fetch(`${apiBase}/api/datasets/master`);
      if (masterResponse.ok) {
        const masterData = await masterResponse.json();
        setMasterData(masterData);
      }
      
      // Load datasets metadata
      const datasetsResponse = await fetch(`${apiBase}/api/datasets/metadata`);
      if (datasetsResponse.ok) {
        const datasetsData = await datasetsResponse.json();
        setDatasets(datasetsData);
      }
    } catch (err) {
      setError('Failed to load data');
      console.error('Error loading data:', err);
    } finally {
      setLoading(false);
    }
  };

  const refreshData = () => {
    loadData();
  };

  // Get available personas and tiers
  const availablePersonas = [...new Set(masterData.map(item => item.persona_id))];
  const availableTiers = [...new Set(masterData.map(item => item.tier))];

  // Filter data based on current filters
  const filteredData = masterData.filter(item => {
    if (personaFilter !== 'All' && item.persona_id !== personaFilter) return false;
    if (tierFilter !== 'All' && item.tier !== tierFilter) return false;
    const score = parseFloat(item.final_score) || 0;
    if (score < scoreRange[0] || score > scoreRange[1]) return false;
    return true;
  });

  // Calculate overview metrics
  const overviewMetrics = {
    totalRecords: masterData.length,
    uniquePages: new Set(masterData.map(item => item.url)).size,
    uniquePersonas: availablePersonas.length,
    dataCompleteness: masterData.length > 0 ? 
      (masterData.filter(item => item.final_score !== null && item.final_score !== 'N/A').length / masterData.length * 100).toFixed(1) : '0'
  };

  // Data quality analysis
  const dataQuality = {
    completeness: parseFloat(overviewMetrics.dataCompleteness),
    consistency: masterData.length > 0 ? 
      (masterData.filter(item => item.tier && item.persona_id).length / masterData.length * 100) : 0,
    accuracy: masterData.length > 0 ? 
      (masterData.filter(item => {
        const score = parseFloat(item.final_score);
        return score >= 0 && score <= 10;
      }).length / masterData.length * 100) : 0,
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
          filters: { personaFilter, tierFilter, scoreRange },
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

  return (
    <div className="page-container reports-export-container">
      <div className="main-header">
        <h1>📋 Reports & Export</h1>
        <p>Generate and export comprehensive audit reports and data summaries</p>
        <div className="header-actions">
          <button 
            className="refresh-button"
            onClick={refreshData}
            disabled={loading}
          >
            🔄 Refresh Data
          </button>
          <span className="last-updated">
            Last updated: {new Date().toLocaleTimeString()}
          </span>
        </div>
      </div>

      {error && (
        <div className="error-state">
          ⚠️ {error}
        </div>
      )}

      {/* Tab Navigation */}
      <div className="tabs">
                  <div className="tab-buttons">
            <button 
              className={`tab-button ${activeTab === 'data-explorer' ? 'active' : ''}`}
              onClick={() => setActiveTab('data-explorer')}
            >
              📊 Data Explorer
            </button>
            <button 
              className={`tab-button ${activeTab === 'custom-reports' ? 'active' : ''}`}
              onClick={() => setActiveTab('custom-reports')}
            >
              📈 Custom Reports
            </button>
            <button 
              className={`tab-button ${activeTab === 'html-reports' ? 'active' : ''}`}
              onClick={() => setActiveTab('html-reports')}
            >
              🎨 HTML Reports
            </button>
            <button 
              className={`tab-button ${activeTab === 'export-center' ? 'active' : ''}`}
              onClick={() => setActiveTab('export-center')}
            >
              📦 Export Center
            </button>
          </div>

        <div className="tab-content">
          {/* Data Explorer Tab */}
          {activeTab === 'data-explorer' && (
            <div>
              <div className="section-header">
                <h2>📊 Data Explorer & Browser</h2>
                <p>Interactive analysis, filtering, and browsing of all audit datasets</p>
              </div>
              
              {/* Dataset Selection */}
              <div className="section">
                <h3>🗂️ Dataset Selection</h3>
                <div className="dataset-selector">
                  <div 
                    className={`dataset-option ${!viewingDataset ? 'selected' : ''}`}
                    onClick={() => setViewingDataset(null)}
                  >
                    <div className="dataset-icon">📊</div>
                    <div className="dataset-details">
                      <div className="dataset-name">Master Dataset</div>
                      <div className="dataset-meta">{masterData.length} records • {masterData.length > 0 ? Object.keys(masterData[0]).length : 0} columns</div>
                    </div>
                  </div>
                  
                  {datasets.map((dataset, index) => (
                    <div 
                      key={index}
                      className={`dataset-option ${viewingDataset === dataset.name ? 'selected' : ''}`}
                      onClick={() => setViewingDataset(dataset.name)}
                    >
                      <div className="dataset-icon">🗂️</div>
                      <div className="dataset-details">
                        <div className="dataset-name">{dataset.name}</div>
                        <div className="dataset-meta">{dataset.records} records • {dataset.columns} columns</div>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
              
              {/* Master Dataset Analysis */}
              {!viewingDataset ? (
                <>
                  {/* Data Overview */}
                  <div className="data-overview">
                <div className="overview-metric">
                  <div className="metric-value">{overviewMetrics.totalRecords}</div>
                  <div className="metric-label">Total Records</div>
                </div>
                <div className="overview-metric">
                  <div className="metric-value">{overviewMetrics.uniquePages}</div>
                  <div className="metric-label">Unique Pages</div>
                </div>
                <div className="overview-metric">
                  <div className="metric-value">{overviewMetrics.uniquePersonas}</div>
                  <div className="metric-label">Personas</div>
                </div>
                <div className="overview-metric">
                  <div className="metric-value">{overviewMetrics.dataCompleteness}%</div>
                  <div className="metric-label">Data Completeness</div>
                </div>
              </div>

              {/* Filter Controls */}
              <div className="filter-controls">
                <div className="filter-group">
                  <label>👤 Persona</label>
                  <select 
                    value={personaFilter} 
                    onChange={(e) => setPersonaFilter(e.target.value)}
                  >
                    <option value="All">All Personas</option>
                    {availablePersonas.map(persona => (
                      <option key={persona} value={persona}>{persona}</option>
                    ))}
                  </select>
                </div>
                
                <div className="filter-group">
                  <label>🏢 Tier</label>
                  <select 
                    value={tierFilter} 
                    onChange={(e) => setTierFilter(e.target.value)}
                  >
                    <option value="All">All Tiers</option>
                    {availableTiers.map(tier => (
                      <option key={tier} value={tier}>{tier}</option>
                    ))}
                  </select>
                </div>
                
                <div className="filter-group">
                  <label>📊 Score Range: {scoreRange[0]} - {scoreRange[1]}</label>
                  <input
                    type="range"
                    min="0"
                    max="100"
                    value={scoreRange[0]}
                    onChange={(e) => setScoreRange([parseInt(e.target.value), scoreRange[1]])}
                  />
                  <input
                    type="range"
                    min="0"
                    max="100"
                    value={scoreRange[1]}
                    onChange={(e) => setScoreRange([scoreRange[0], parseInt(e.target.value)])}
                  />
                </div>
                
                <div className="filter-group">
                  <label>👁️ Display Mode</label>
                  <select 
                    value={displayMode} 
                    onChange={(e) => setDisplayMode(e.target.value)}
                  >
                    <option value="table">Table View</option>
                    <option value="summary">Summary Statistics</option>
                    <option value="chart">Chart View</option>
                  </select>
                </div>
              </div>

              {/* Data Quality Analysis */}
              <div className="data-quality">
                <h3>📈 Data Quality Analysis</h3>
                <div className="grid grid--cols-4 gap-md">
                  <StandardCard
                    title="Completeness"
                    variant="metric"
                    status={dataQuality.completeness >= 90 ? "excellent" : 
                      dataQuality.completeness >= 70 ? "good" : 
                      dataQuality.completeness >= 50 ? "warning" : "critical"}
                  >
                    <div className="metric-value">{dataQuality.completeness.toFixed(1)}%</div>
                  </StandardCard>
                  <StandardCard
                    title="Consistency"
                    variant="metric"
                    status={dataQuality.consistency >= 90 ? "excellent" : 
                      dataQuality.consistency >= 70 ? "good" : 
                      dataQuality.consistency >= 50 ? "warning" : "critical"}
                  >
                    <div className="metric-value">{dataQuality.consistency.toFixed(1)}%</div>
                  </StandardCard>
                  <StandardCard
                    title="Accuracy"
                    variant="metric"
                    status={dataQuality.accuracy >= 90 ? "excellent" : 
                      dataQuality.accuracy >= 70 ? "good" : 
                      dataQuality.accuracy >= 50 ? "warning" : "critical"}
                  >
                    <div className="metric-value">{dataQuality.accuracy.toFixed(1)}%</div>
                  </StandardCard>
                  <StandardCard
                    title="Timeliness"
                    variant="metric"
                    status={dataQuality.timeliness >= 90 ? "excellent" : 
                      dataQuality.timeliness >= 70 ? "good" : 
                      dataQuality.timeliness >= 50 ? "warning" : "critical"}
                  >
                    <div className="metric-value">{dataQuality.timeliness.toFixed(1)}%</div>
                  </StandardCard>
                </div>
              </div>

              {/* Filtered Data Display */}
              {displayMode === 'table' && (
                <div className="section">
                  <h3>📋 Filtered Data ({filteredData.length} records)</h3>
                  <div className="data-table-container">
                    <table className="data-table">
                      <thead>
                        <tr>
                          <th>URL</th>
                          <th>Persona</th>
                          <th>Tier</th>
                          <th>Score</th>
                          <th>Criterion</th>
                          <th>Status</th>
                          <th>Flags</th>
                        </tr>
                      </thead>
                      <tbody>
                        {filteredData.slice(0, 50).map((item, index) => (
                          <tr key={index}>
                            <td className="url-cell">
                              <a href={item.url} target="_blank" rel="noopener noreferrer">
                                {item.url}
                              </a>
                            </td>
                            <td>{item.persona_id}</td>
                            <td>{item.tier_name || item.tier}</td>
                            <td>{item.final_score || 'N/A'}</td>
                            <td>{item.criterion_code || 'N/A'}</td>
                            <td>
                              <span className={`descriptor ${item.descriptor?.toLowerCase()}`}>
                                {item.descriptor || 'N/A'}
                              </span>
                            </td>
                            <td>
                              <div className="flags">
                                {item.quick_win_flag === 'True' && <span className="flag quick-win">Quick Win</span>}
                                {item.critical_issue_flag === 'True' && <span className="flag critical">Critical</span>}
                                {item.success_flag === 'True' && <span className="flag success">Success</span>}
                              </div>
                            </td>
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  </div>
                  {filteredData.length > 50 && (
                    <p className="text-center text-secondary">
                      Showing first 50 of {filteredData.length} records
                    </p>
                  )}
                </div>
              )}

              {displayMode === 'summary' && (
                <div className="section">
                  <h3>📊 Summary Statistics</h3>
                  <div className="insights-box">
                    <div className="insights-box__title">Key Insights</div>
                    <p><strong>Average Overall Score:</strong> {(filteredData.reduce((sum, item) => sum + (item.overall_score || 0), 0) / filteredData.length).toFixed(1)}</p>
                    <p><strong>Best Performing Tier:</strong> {
                      availableTiers.map(tier => ({
                        tier,
                        avg: filteredData.filter(item => item.tier === tier).reduce((sum, item) => sum + (item.overall_score || 0), 0) / filteredData.filter(item => item.tier === tier).length
                      })).sort((a, b) => b.avg - a.avg)[0]?.tier || 'N/A'
                    }</p>
                    <p><strong>Total Pages Analyzed:</strong> {new Set(filteredData.map(item => item.url)).size}</p>
                  </div>
                </div>
              )}
                </>
              ) : (
                <div>
                  <h3>Dataset: {viewingDataset}</h3>
                  <DatasetDetail />
                </div>
              )}
            </div>
          )}

          {/* Custom Reports Tab */}
          {activeTab === 'custom-reports' && (
            <div>
              <div className="section-header">
                <h2>📈 Custom Reports</h2>
                <p>Generate configurable business reports with detailed analysis and insights</p>
              </div>
              
              <div className="report-config-grid">
                <div className="config-section">
                  <h4>📊 Report Settings</h4>
                  <div className="config-group">
                    <label>📊 Report Type</label>
                    <select 
                      value={reportConfig.reportType}
                      onChange={(e) => setReportConfig({...reportConfig, reportType: e.target.value})}
                    >
                      <option value="comprehensive">Comprehensive Analysis</option>
                      <option value="executive">Executive Summary</option>
                      <option value="technical">Technical Deep Dive</option>
                      <option value="comparative">Comparative Analysis</option>
                    </select>
                  </div>
                  
                  <div className="config-group">
                    <label>📄 Output Format</label>
                    <select 
                      value={reportConfig.format}
                      onChange={(e) => setReportConfig({...reportConfig, format: e.target.value})}
                    >
                      <option value="pdf">PDF Report</option>
                      <option value="docx">Word Document</option>
                      <option value="html">HTML Report</option>
                      <option value="xlsx">Excel Workbook</option>
                    </select>
                  </div>
                </div>
                
                <div className="config-section">
                  <h4>🎯 Content Options</h4>
                  <div className="checkbox-group">
                    <input 
                      type="checkbox" 
                      id="includeAnalysis"
                      checked={reportConfig.includeAnalysis}
                      onChange={(e) => setReportConfig({...reportConfig, includeAnalysis: e.target.checked})}
                    />
                    <label htmlFor="includeAnalysis">Include Detailed Analysis</label>
                  </div>
                  
                  <div className="checkbox-group">
                    <input 
                      type="checkbox" 
                      id="includeRecommendations"
                      checked={reportConfig.includeRecommendations}
                      onChange={(e) => setReportConfig({...reportConfig, includeRecommendations: e.target.checked})}
                    />
                    <label htmlFor="includeRecommendations">Include Recommendations</label>
                  </div>
                </div>
                
                <div className="config-section">
                  <h4>🎭 Persona Selection</h4>
                  <div className="multi-select">
                    {availablePersonas.map(persona => (
                      <div key={persona} className="multi-select-option">
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
                        <label htmlFor={`persona-${persona}`}>{persona}</label>
                      </div>
                    ))}
                  </div>
                </div>
              </div>
              
              <div className="action-buttons">
                <button 
                  className="action-button primary" 
                  onClick={generateCustomReport}
                  disabled={generatingReport}
                >
                  {generatingReport ? '⏳ Generating...' : '📊 Generate Report'}
                </button>
                <button 
                  className="action-button secondary"
                  onClick={() => setReportConfig({
                    reportType: 'comprehensive',
                    personas: [],
                    tiers: [],
                    includeAnalysis: true,
                    includeRecommendations: true,
                    format: 'pdf'
                  })}
                >
                  🔄 Reset Configuration
                </button>
              </div>
            </div>
          )}

          {/* HTML Reports Tab */}
          {activeTab === 'html-reports' && (
            <div>
              <div className="section-header">
                <h2>🎨 HTML Reports</h2>
                <p>Generate professional HTML reports with interactive visualizations</p>
              </div>
              
              <div className="html-report-options">
                <div 
                  className={`report-option ${htmlOptions.generationMode === 'All Personas' ? 'selected' : ''}`}
                  onClick={() => setHtmlOptions({...htmlOptions, generationMode: 'All Personas'})}
                >
                  <h4>🎭 All Personas</h4>
                  <p>Generate reports for all available personas</p>
                </div>
                
                <div 
                  className={`report-option ${htmlOptions.generationMode === 'Selected Personas' ? 'selected' : ''}`}
                  onClick={() => setHtmlOptions({...htmlOptions, generationMode: 'Selected Personas'})}
                >
                  <h4>🎯 Selected Personas</h4>
                  <p>Generate reports for specific personas only</p>
                </div>
                
                <div 
                  className={`report-option ${htmlOptions.generationMode === 'Consolidated Report' ? 'selected' : ''}`}
                  onClick={() => setHtmlOptions({...htmlOptions, generationMode: 'Consolidated Report'})}
                >
                  <h4>📋 Consolidated Report</h4>
                  <p>Single comprehensive report across all personas</p>
                </div>
              </div>
              
              {htmlOptions.generationMode === 'Selected Personas' && (
                <div className="config-section">
                  <h4>🎭 Select Personas</h4>
                  <div className="multi-select">
                    {availablePersonas.map(persona => (
                      <div key={persona} className="multi-select-option">
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
                        <label htmlFor={`html-persona-${persona}`}>{persona}</label>
                      </div>
                    ))}
                  </div>
                  
                  {htmlOptions.personas.length > 0 && (
                    <div className="selected-items">
                      {htmlOptions.personas.map(persona => (
                        <div key={persona} className="selected-item">
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
              
              <div className="action-buttons">
                <button 
                  className="action-button primary" 
                  onClick={generateHtmlReports}
                  disabled={generatingHtml || (htmlOptions.generationMode === 'Selected Personas' && htmlOptions.personas.length === 0)}
                >
                  {generatingHtml ? '⏳ Generating...' : '🎨 Generate HTML Reports'}
                </button>
              </div>
            </div>
          )}

          {/* Export Center Tab */}
          {activeTab === 'export-center' && (
            <div>
              <div className="section-header">
                <h2>📦 Export Center</h2>
                <p>Export data in various formats for external analysis</p>
              </div>
              
              <div className="export-options">
                <div 
                  className={`export-option ${exportFormat === 'csv' ? 'selected' : ''}`}
                  onClick={() => setExportFormat('csv')}
                >
                  <div className="export-icon">📊</div>
                  <div className="export-name">CSV</div>
                  <div className="export-description">Comma-separated values</div>
                </div>
                
                <div 
                  className={`export-option ${exportFormat === 'excel' ? 'selected' : ''}`}
                  onClick={() => setExportFormat('excel')}
                >
                  <div className="export-icon">📈</div>
                  <div className="export-name">Excel</div>
                  <div className="export-description">Microsoft Excel format</div>
                </div>
                
                <div 
                  className={`export-option ${exportFormat === 'json' ? 'selected' : ''}`}
                  onClick={() => setExportFormat('json')}
                >
                  <div className="export-icon">🔧</div>
                  <div className="export-name">JSON</div>
                  <div className="export-description">JavaScript Object Notation</div>
                </div>
                
                <div 
                  className={`export-option ${exportFormat === 'parquet' ? 'selected' : ''}`}
                  onClick={() => setExportFormat('parquet')}
                >
                  <div className="export-icon">⚡</div>
                  <div className="export-name">Parquet</div>
                  <div className="export-description">Columnar storage format</div>
                </div>
              </div>
              
              <div className="config-section">
                <h4>📋 Export Options</h4>
                <div className="checkbox-group">
                  <input 
                    type="checkbox" 
                    id="includeRawData"
                    checked={exportFilters.includeRawData}
                    onChange={(e) => setExportFilters({...exportFilters, includeRawData: e.target.checked})}
                  />
                  <label htmlFor="includeRawData">Include Raw Data</label>
                </div>
                
                <div className="checkbox-group">
                  <input 
                    type="checkbox" 
                    id="includeSummaries"
                    checked={exportFilters.includeSummaries}
                    onChange={(e) => setExportFilters({...exportFilters, includeSummaries: e.target.checked})}
                  />
                  <label htmlFor="includeSummaries">Include Summaries</label>
                </div>
                
                <div className="checkbox-group">
                  <input 
                    type="checkbox" 
                    id="includeAnalysis"
                    checked={exportFilters.includeAnalysis}
                    onChange={(e) => setExportFilters({...exportFilters, includeAnalysis: e.target.checked})}
                  />
                  <label htmlFor="includeAnalysis">Include Analysis</label>
                </div>
              </div>
              
              <div className="action-buttons">
                <button 
                  className="action-button primary" 
                  onClick={exportData}
                  disabled={exporting}
                >
                  {exporting ? '⏳ Exporting...' : '📦 Export Data'}
                </button>
              </div>
            </div>
          )}


        </div>
      </div>
    </div>
  );
};

export default ReportsExport;
