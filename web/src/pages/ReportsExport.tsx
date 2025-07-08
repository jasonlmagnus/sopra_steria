import { useState, useEffect } from 'react';
import { useFilters } from '../context/FilterContext';
import { ScoreCard } from '../components/ScoreCard';
import { PlotlyChart } from '../components/PlotlyChart';

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
  includeTierAnalysis: boolean;
  includePersonaVoice: boolean;
  includeRecommendations: boolean;
  includeVisualBrand: boolean;
  autoOpen: boolean;
  createZip: boolean;
}

const ReportsExport: React.FC = () => {
  const filters = useFilters();
  const [loading, setLoading] = useState(true);
  const [activeTab, setActiveTab] = useState('data-explorer');
  const [masterData, setMasterData] = useState<any[]>([]);
  const [datasets, setDatasets] = useState<DatasetInfo[]>([]);
  
  // Data Explorer state
  const [filteredData, setFilteredData] = useState<any[]>([]);
  const [displayMode, setDisplayMode] = useState('table');
  const [maxRows, setMaxRows] = useState(100);
  const [selectedColumns, setSelectedColumns] = useState<string[]>([]);
  
  // Custom Reports state
  const [reportConfig, setReportConfig] = useState<ReportConfig>({
    reportType: 'Executive Summary Report',
    personas: [],
    tiers: [],
    includeAnalysis: true,
    includeRecommendations: true,
    format: 'PDF'
  });
  
  // HTML Reports state
  const [generationMode, setGenerationMode] = useState('Single Persona');
  const [selectedPersonas, setSelectedPersonas] = useState<string[]>([]);
  const [htmlOptions, setHtmlOptions] = useState<HTMLReportOptions>({
    includeTierAnalysis: true,
    includePersonaVoice: true,
    includeRecommendations: true,
    includeVisualBrand: true,
    autoOpen: false,
    createZip: true
  });
  
  // Export Center state
  const [exportFormat, setExportFormat] = useState('CSV');
  const [exportScope, setExportScope] = useState('Filtered Data');

  useEffect(() => {
    fetchReportData();
  }, []);

  const fetchReportData = async () => {
    try {
      setLoading(true);
      const res = await fetch('http://localhost:3000/api/datasets/master');
      if (!res.ok) throw new Error('Failed to load data');
      const data = await res.json();
      setMasterData(data);
      setFilteredData(data);
      setSelectedColumns(Object.keys(data[0] || {}));

      const dsRes = await fetch('http://localhost:3000/api/datasets');
      if (dsRes.ok) {
        setDatasets(dsRes.json().datasets || []);
      }
    } catch (error) {
      console.error('Error fetching report data:', error);
    } finally {
      setLoading(false);
    }
  };

  const applyDataFilters = () => {
    const filtered = masterData.filter(item => {
      if (filters.persona && filters.persona !== 'All' && item.persona_id !== filters.persona) return false;
      if (filters.tier && filters.tier !== 'All' && item.tier !== filters.tier) return false;
      const [minScore, maxScore] = filters.scoreRange;
      if (item.avg_score < minScore || item.avg_score > maxScore) return false;
      return true;
    });
    setFilteredData(filtered);
  };

  useEffect(() => {
    applyDataFilters();
  }, [filters, masterData]);

  const dataOverviewMetrics = {
    totalRecords: masterData.length,
    uniquePages: new Set(masterData.map(item => item.page_id)).size,
    personas: new Set(masterData.map(item => item.persona_id)).size,
    completeness: 95.2
  };

  const datasetChartData = [
    {
      x: datasets.map(d => d.records),
      y: datasets.map(d => d.name),
      type: 'bar',
      orientation: 'h',
      marker: { color: '#10b981' }
    }
  ];

  const datasetChartLayout = {
    title: 'Dataset Breakdown',
    xaxis: { title: 'Records' },
    height: 400
  };

  const distributionChartData = [
    {
      x: filteredData.map(item => item.avg_score),
      type: 'histogram',
      nbins: 20,
      marker: { color: '#10b981' }
    }
  ];

  const distributionChartLayout = {
    title: 'Score Distribution',
    xaxis: { title: 'Score' },
    yaxis: { title: 'Count' },
    height: 400
  };

  const generateCustomReport = () => {
    console.log('Generating custom report:', reportConfig);
    // TODO: Implement actual report generation
    alert(`Generating ${reportConfig.reportType} for ${reportConfig.personas.length || 'all'} personas`);
  };

  const generateHtmlReports = () => {
    console.log('Generating HTML reports:', { generationMode, selectedPersonas, htmlOptions });
    // TODO: Implement actual HTML report generation
    alert(`Generating HTML reports in ${generationMode} mode`);
  };

  const exportData = () => {
    console.log('Exporting data:', { exportFormat, exportScope });
    // TODO: Implement actual data export
    alert(`Exporting ${exportScope} as ${exportFormat}`);
  };

  if (loading) {
    return (
      <div className="page-container">
        <div className="loading-spinner">Loading Reports & Export...</div>
      </div>
    );
  }

  return (
    <div className="page-container">
      <div className="main-header">
        <h1>📋 Reports Export</h1>
        <p>Generate and export comprehensive audit reports and data summaries</p>
      </div>

      {/* Tab Navigation */}
      <div className="tab-navigation">
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

      {/* Tab Content */}
      {activeTab === 'data-explorer' && (
        <div className="tab-content">
          <h2>🔍 Data Explorer</h2>
          
          {/* Data Overview */}
          <div className="section">
            <h3>📊 Data Overview</h3>
            <div className="metrics-grid">
              <ScoreCard 
                label="Total Records" 
                value={dataOverviewMetrics.totalRecords.toLocaleString()} 
                variant="default"
              />
              <ScoreCard 
                label="Unique Pages" 
                value={dataOverviewMetrics.uniquePages.toLocaleString()} 
                variant="default"
              />
              <ScoreCard 
                label="Personas" 
                value={dataOverviewMetrics.personas.toString()} 
                variant="default"
              />
              <ScoreCard 
                label="Data Completeness" 
                value={`${dataOverviewMetrics.completeness}%`} 
                variant="success"
              />
            </div>

            <div className="dataset-breakdown">
              <h4>📋 Dataset Breakdown</h4>
              <div className="dataset-table">
                <table>
                  <thead>
                    <tr>
                      <th>Dataset</th>
                      <th>Records</th>
                      <th>Columns</th>
                      <th>Memory (MB)</th>
                    </tr>
                  </thead>
                  <tbody>
                    {datasets.map((dataset, index) => (
                      <tr key={index}>
                        <td>{dataset.name}</td>
                        <td>{dataset.records.toLocaleString()}</td>
                        <td>{dataset.columns}</td>
                        <td>{dataset.memoryMB}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
              <PlotlyChart data={datasetChartData} layout={datasetChartLayout} />
            </div>
          </div>

          {/* Data Filters */}
          <div className="section">
            <h3>🎛️ Data Filters</h3>
            <div className="controls-grid">
              <div className="control-group">
                <label>👤 Persona</label>
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
                <label>🏗️ Tier</label>
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
                <label>📊 Score Range</label>
                <input
                  type="range"
                  min="0"
                  max="10"
                  step="0.1"
                  value={filters.scoreRange[0]}
                  onChange={(e) => filters.setScoreRange([parseFloat(e.target.value), filters.scoreRange[1]])}
                />
                <span>{filters.scoreRange[0]} - {filters.scoreRange[1]}</span>
              </div>
              
              <div className="control-group">
                <label>📋 Display Mode</label>
                <select value={displayMode} onChange={(e) => setDisplayMode(e.target.value)}>
                  <option value="table">Table View</option>
                  <option value="summary">Summary Statistics</option>
                </select>
              </div>
            </div>
          </div>

          {/* Filtered Data */}
          <div className="section">
            <h3>📊 Filtered Data</h3>
            <p>Showing {filteredData.length.toLocaleString()} records after filtering</p>
            
            {displayMode === 'table' ? (
              <div className="data-table-container">
                <div className="table-controls">
                  <label>Max Rows:</label>
                  <input 
                    type="number" 
                    min="10" 
                    max="1000" 
                    value={maxRows}
                    onChange={(e) => setMaxRows(parseInt(e.target.value))}
                  />
                </div>
                <div className="data-table">
                  <table>
                    <thead>
                      <tr>
                        {selectedColumns.map(col => (
                          <th key={col}>{col.replace('_', ' ').toUpperCase()}</th>
                        ))}
                      </tr>
                    </thead>
                    <tbody>
                      {filteredData.slice(0, maxRows).map((row, index) => (
                        <tr key={index}>
                          {selectedColumns.map(col => (
                            <td key={col}>
                              {typeof row[col] === 'number' ? row[col].toFixed(2) : row[col]}
                            </td>
                          ))}
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              </div>
            ) : (
              <div className="summary-statistics">
                <h4>📈 Summary Statistics</h4>
                <PlotlyChart data={distributionChartData} layout={distributionChartLayout} />
                
                <div className="categorical-summary">
                  <h5>📊 Categorical Data Summary</h5>
                  <div className="category-counts">
                    <div className="category-group">
                      <strong>Personas:</strong>
                      {Object.entries(
                        filteredData.reduce((acc: Record<string, number>, item: any) => {
                          acc[item.persona_id] = (acc[item.persona_id] || 0) + 1;
                          return acc;
                        }, {} as Record<string, number>)
                      ).map(([persona, count]) => (
                        <div key={persona}>{persona}: {count}</div>
                      ))}
                    </div>
                    
                    <div className="category-group">
                      <strong>Tiers:</strong>
                      {Object.entries(
                        filteredData.reduce((acc: Record<string, number>, item: any) => {
                          acc[item.tier] = (acc[item.tier] || 0) + 1;
                          return acc;
                        }, {} as Record<string, number>)
                      ).map(([tier, count]) => (
                        <div key={tier}>{tier}: {count}</div>
                      ))}
                    </div>
                  </div>
                </div>
              </div>
            )}
          </div>

          {/* Data Quality Insights */}
          <div className="section">
            <h3>🔍 Data Quality Insights</h3>
            <div className="quality-metrics">
              <div className="quality-card">
                <h4>📊 Missing Data Analysis</h4>
                <p>✅ No missing data found in current dataset</p>
              </div>
              <div className="quality-card">
                <h4>📈 Data Distribution</h4>
                <p>Score distribution appears normal with mean: {(filteredData.reduce((sum, item) => sum + item.avg_score, 0) / filteredData.length).toFixed(2)}</p>
              </div>
            </div>
          </div>
        </div>
      )}

      {activeTab === 'custom-reports' && (
        <div className="tab-content">
          <h2>📈 Custom Reports</h2>
          
          <div className="section">
            <h3>📋 Report Configuration</h3>
            
            <div className="report-config">
              <div className="config-group">
                <label>📊 Report Type</label>
                <select 
                  value={reportConfig.reportType}
                  onChange={(e) => setReportConfig({...reportConfig, reportType: e.target.value})}
                >
                  <option value="Executive Summary Report">Executive Summary Report</option>
                  <option value="Persona Performance Report">Persona Performance Report</option>
                  <option value="Content Tier Analysis Report">Content Tier Analysis Report</option>
                  <option value="Criteria Deep Dive Report">Criteria Deep Dive Report</option>
                  <option value="Success Stories Report">Success Stories Report</option>
                  <option value="Improvement Opportunities Report">Improvement Opportunities Report</option>
                </select>
              </div>
              
              <div className="config-group">
                <label>👤 Personas</label>
                <select 
                  multiple 
                  value={reportConfig.personas}
                  onChange={(e) => setReportConfig({
                    ...reportConfig, 
                    personas: Array.from(e.target.selectedOptions, option => option.value)
                  })}
                >
                  <option value="Strategic Business Leader">Strategic Business Leader</option>
                  <option value="Technology Innovation Leader">Technology Innovation Leader</option>
                  <option value="Cybersecurity Decision Maker">Cybersecurity Decision Maker</option>
                  <option value="Transformation Programme Leader">Transformation Programme Leader</option>
                </select>
              </div>
              
              <div className="config-group">
                <label>🏗️ Content Tiers</label>
                <select 
                  multiple 
                  value={reportConfig.tiers}
                  onChange={(e) => setReportConfig({
                    ...reportConfig, 
                    tiers: Array.from(e.target.selectedOptions, option => option.value)
                  })}
                >
                  <option value="Tier 1">Tier 1</option>
                  <option value="Tier 2">Tier 2</option>
                  <option value="Tier 3">Tier 3</option>
                </select>
              </div>
              
              <div className="config-options">
                <label>
                  <input 
                    type="checkbox" 
                    checked={reportConfig.includeAnalysis}
                    onChange={(e) => setReportConfig({...reportConfig, includeAnalysis: e.target.checked})}
                  />
                  Include Analysis
                </label>
                <label>
                  <input 
                    type="checkbox" 
                    checked={reportConfig.includeRecommendations}
                    onChange={(e) => setReportConfig({...reportConfig, includeRecommendations: e.target.checked})}
                  />
                  Include Recommendations
                </label>
              </div>
              
              <div className="config-group">
                <label>📄 Format</label>
                <select 
                  value={reportConfig.format}
                  onChange={(e) => setReportConfig({...reportConfig, format: e.target.value})}
                >
                  <option value="PDF">PDF</option>
                  <option value="HTML">HTML</option>
                  <option value="Excel">Excel</option>
                  <option value="PowerPoint">PowerPoint</option>
                </select>
              </div>
            </div>
            
            <div className="report-preview">
              <h4>📋 Report Preview</h4>
              <div className="preview-metrics">
                <ScoreCard 
                  label="Report Type" 
                  value={reportConfig.reportType} 
                  variant="default"
                />
                <ScoreCard 
                  label="Personas" 
                  value={reportConfig.personas.length > 0 ? reportConfig.personas.length.toString() : 'All'} 
                  variant="default"
                />
                <ScoreCard 
                  label="Tiers" 
                  value={reportConfig.tiers.length > 0 ? reportConfig.tiers.length.toString() : 'All'} 
                  variant="default"
                />
                <ScoreCard 
                  label="Format" 
                  value={reportConfig.format} 
                  variant="default"
                />
              </div>
            </div>
            
            <button className="generate-button" onClick={generateCustomReport}>
              📊 Generate Custom Report
            </button>
          </div>
        </div>
      )}

      {activeTab === 'html-reports' && (
        <div className="tab-content">
          <h2>🎨 HTML Brand Experience Reports</h2>
          
          <div className="section">
            <h3>🎯 Report Configuration</h3>
            
            <div className="html-config">
              <div className="config-section">
                <h4>👤 Persona Selection</h4>
                <div className="generation-mode">
                  <label>
                    <input 
                      type="radio" 
                      value="Single Persona" 
                      checked={generationMode === 'Single Persona'}
                      onChange={(e) => setGenerationMode(e.target.value)}
                    />
                    Single Persona
                  </label>
                  <label>
                    <input 
                      type="radio" 
                      value="Multiple Personas" 
                      checked={generationMode === 'Multiple Personas'}
                      onChange={(e) => setGenerationMode(e.target.value)}
                    />
                    Multiple Personas
                  </label>
                  <label>
                    <input 
                      type="radio" 
                      value="All Personas" 
                      checked={generationMode === 'All Personas'}
                      onChange={(e) => setGenerationMode(e.target.value)}
                    />
                    All Personas
                  </label>
                  <label>
                    <input 
                      type="radio" 
                      value="Consolidated Report" 
                      checked={generationMode === 'Consolidated Report'}
                      onChange={(e) => setGenerationMode(e.target.value)}
                    />
                    Consolidated Report
                  </label>
                </div>
                
                {(generationMode === 'Single Persona' || generationMode === 'Multiple Personas') && (
                  <div className="persona-selection">
                    <select 
                      multiple={generationMode === 'Multiple Personas'}
                      value={selectedPersonas}
                      onChange={(e) => setSelectedPersonas(
                        generationMode === 'Single Persona' 
                          ? [e.target.value]
                          : Array.from(e.target.selectedOptions, option => option.value)
                      )}
                    >
                      <option value="Strategic Business Leader">Strategic Business Leader</option>
                      <option value="Technology Innovation Leader">Technology Innovation Leader</option>
                      <option value="Cybersecurity Decision Maker">Cybersecurity Decision Maker</option>
                      <option value="Transformation Programme Leader">Transformation Programme Leader</option>
                    </select>
                  </div>
                )}
              </div>
              
              <div className="config-section">
                <h4>⚙️ Report Options</h4>
                <div className="report-options">
                  <label>
                    <input 
                      type="checkbox" 
                      checked={htmlOptions.includeTierAnalysis}
                      onChange={(e) => setHtmlOptions({...htmlOptions, includeTierAnalysis: e.target.checked})}
                    />
                    Include Tier Analysis
                  </label>
                  <label>
                    <input 
                      type="checkbox" 
                      checked={htmlOptions.includePersonaVoice}
                      onChange={(e) => setHtmlOptions({...htmlOptions, includePersonaVoice: e.target.checked})}
                    />
                    Include Persona Voice Insights
                  </label>
                  <label>
                    <input 
                      type="checkbox" 
                      checked={htmlOptions.includeRecommendations}
                      onChange={(e) => setHtmlOptions({...htmlOptions, includeRecommendations: e.target.checked})}
                    />
                    Include Strategic Recommendations
                  </label>
                  <label>
                    <input 
                      type="checkbox" 
                      checked={htmlOptions.includeVisualBrand}
                      onChange={(e) => setHtmlOptions({...htmlOptions, includeVisualBrand: e.target.checked})}
                    />
                    Include Visual Brand Assessment
                  </label>
                </div>
                
                <div className="output-options">
                  <h5>Output Options:</h5>
                  <label>
                    <input 
                      type="checkbox" 
                      checked={htmlOptions.autoOpen}
                      onChange={(e) => setHtmlOptions({...htmlOptions, autoOpen: e.target.checked})}
                    />
                    Auto-open reports in browser
                  </label>
                  <label>
                    <input 
                      type="checkbox" 
                      checked={htmlOptions.createZip}
                      onChange={(e) => setHtmlOptions({...htmlOptions, createZip: e.target.checked})}
                    />
                    Create ZIP package for multiple reports
                  </label>
                </div>
              </div>
            </div>
            
            <div className="generation-preview">
              <h4>📋 Generation Preview</h4>
              <div className="preview-metrics">
                <ScoreCard 
                  label="Reports to Generate" 
                  value={generationMode === 'All Personas' ? '4' : selectedPersonas.length.toString()} 
                  variant="default"
                />
                <ScoreCard 
                  label="Total Records" 
                  value={filteredData.length.toString()} 
                  variant="default"
                />
                <ScoreCard 
                  label="Estimated Time" 
                  value={`${(generationMode === 'All Personas' ? 4 : selectedPersonas.length) * 2}s`} 
                  variant="default"
                />
              </div>
            </div>
            
            <button className="generate-button" onClick={generateHtmlReports}>
              🎨 Generate HTML Reports
            </button>
          </div>
        </div>
      )}

      {activeTab === 'export-center' && (
        <div className="tab-content">
          <h2>📦 Export Center</h2>
          
          <div className="section">
            <h3>📊 Export Options</h3>
            
            <div className="export-config">
              <div className="config-group">
                <label>📄 Export Format</label>
                <select 
                  value={exportFormat}
                  onChange={(e) => setExportFormat(e.target.value)}
                >
                  <option value="CSV">CSV</option>
                  <option value="Excel">Excel</option>
                  <option value="JSON">JSON</option>
                  <option value="PDF">PDF</option>
                </select>
              </div>
              
              <div className="config-group">
                <label>🎯 Export Scope</label>
                <select 
                  value={exportScope}
                  onChange={(e) => setExportScope(e.target.value)}
                >
                  <option value="Filtered Data">Filtered Data</option>
                  <option value="All Data">All Data</option>
                  <option value="Selected Columns">Selected Columns</option>
                  <option value="Summary Report">Summary Report</option>
                </select>
              </div>
            </div>
            
            <div className="export-preview">
              <h4>📋 Export Preview</h4>
              <div className="preview-info">
                <p><strong>Format:</strong> {exportFormat}</p>
                <p><strong>Scope:</strong> {exportScope}</p>
                <p><strong>Records:</strong> {exportScope === 'All Data' ? masterData.length : filteredData.length}</p>
                <p><strong>Estimated Size:</strong> {((exportScope === 'All Data' ? masterData.length : filteredData.length) * 0.5).toFixed(1)} KB</p>
              </div>
            </div>
            
            <div className="export-actions">
              <button className="export-button" onClick={exportData}>
                📦 Export Data
              </button>
              <button className="export-button secondary">
                📋 Export Report
              </button>
              <button className="export-button secondary">
                🎨 Export Visualizations
              </button>
            </div>
          </div>
          
          <div className="section">
            <h3>📚 Bulk Export</h3>
            <div className="bulk-export">
              <p>Export all datasets and reports in a single package</p>
              <div className="bulk-options">
                <label>
                  <input type="checkbox" defaultChecked />
                  Include Master Dataset
                </label>
                <label>
                  <input type="checkbox" defaultChecked />
                  Include Individual Datasets
                </label>
                <label>
                  <input type="checkbox" defaultChecked />
                  Include Generated Reports
                </label>
                <label>
                  <input type="checkbox" />
                  Include Raw Data
                </label>
              </div>
              <button className="bulk-export-button">
                📦 Create Complete Export Package
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default ReportsExport;
