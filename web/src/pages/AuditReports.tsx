import React, { useEffect, useState } from 'react'

interface HtmlReport {
  file_path: string
  file_name: string
  persona_name: string
  report_type: string
  category: 'Executive' | 'Persona' | 'Other'
  size: string
  modified: string
  relative_path: string
}

interface ReportOptions {
  [category: string]: Array<{
    display_name: string
    report: HtmlReport
  }>
}

function AuditReports() {
  const [reports, setReports] = useState<HtmlReport[]>([])
  const [selectedReport, setSelectedReport] = useState<HtmlReport | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [htmlContent, setHtmlContent] = useState<string>('')
  const [regenerating, setRegenerating] = useState(false)

  useEffect(() => {
    scanHtmlReports()
  }, [])

  const scanHtmlReports = async () => {
    try {
      setLoading(true)
      setError(null)
      
      // Mock HTML reports data - in real app would scan html_reports directory
      const mockReports = generateMockReports()
      setReports(mockReports)
      
      // Set default report (consolidated, index, or first executive)
      const defaultReport = findDefaultReport(mockReports)
      if (defaultReport) {
        setSelectedReport(defaultReport)
        await loadHtmlContent(defaultReport)
      }
    } catch (err) {
      setError('Failed to scan HTML reports')
    } finally {
      setLoading(false)
    }
  }

  const generateMockReports = (): HtmlReport[] => {
    return [
      {
        file_path: 'html_reports/index.html',
        file_name: 'index.html',
        persona_name: 'Index/Root',
        report_type: 'Strategic Analysis',
        category: 'Executive',
        size: '19.2 KB',
        modified: '2024-01-15 14:30',
        relative_path: 'index.html'
      },
      {
        file_path: 'html_reports/sopra_brand_audit_1.html',
        file_name: 'sopra_brand_audit_1.html',
        persona_name: 'Index/Root',
        report_type: 'Strategic Analysis',
        category: 'Executive',
        size: '52.1 KB',
        modified: '2024-01-15 14:35',
        relative_path: 'sopra_brand_audit_1.html'
      },
      {
        file_path: 'html_reports/Consolidated_Brand_Report/consolidated_brand_experience_report.html',
        file_name: 'consolidated_brand_experience_report.html',
        persona_name: 'Consolidated Brand Report',
        report_type: 'Consolidated Report',
        category: 'Executive',
        size: '156.7 KB',
        modified: '2024-01-15 14:40',
        relative_path: 'Consolidated_Brand_Report/consolidated_brand_experience_report.html'
      },
      {
        file_path: 'html_reports/The_Technical_Influencer/brand_experience_report.html',
        file_name: 'brand_experience_report.html',
        persona_name: 'The Technical Influencer',
        report_type: 'Persona Report',
        category: 'Persona',
        size: '89.3 KB',
        modified: '2024-01-15 14:25',
        relative_path: 'The_Technical_Influencer/brand_experience_report.html'
      },
      {
        file_path: 'html_reports/The_Benelux_Cybersecurity_Decision_Maker/brand_experience_report.html',
        file_name: 'brand_experience_report.html',
        persona_name: 'The Benelux Cybersecurity Decision Maker',
        report_type: 'Persona Report',
        category: 'Persona',
        size: '92.1 KB',
        modified: '2024-01-15 14:26',
        relative_path: 'The_Benelux_Cybersecurity_Decision_Maker/brand_experience_report.html'
      },
      {
        file_path: 'html_reports/The_Benelux_Strategic_Business_Leader_C-Suite_Executive/brand_experience_report.html',
        file_name: 'brand_experience_report.html',
        persona_name: 'The Benelux Strategic Business Leader (C-Suite Executive)',
        report_type: 'Persona Report',
        category: 'Persona',
        size: '88.7 KB',
        modified: '2024-01-15 14:27',
        relative_path: 'The_Benelux_Strategic_Business_Leader_C-Suite_Executive/brand_experience_report.html'
      },
      {
        file_path: 'html_reports/The_Benelux_Transformation_Programme_Leader/brand_experience_report.html',
        file_name: 'brand_experience_report.html',
        persona_name: 'The Benelux Transformation Programme Leader',
        report_type: 'Persona Report',
        category: 'Persona',
        size: '91.5 KB',
        modified: '2024-01-15 14:28',
        relative_path: 'The_Benelux_Transformation_Programme_Leader/brand_experience_report.html'
      },
      {
        file_path: 'html_reports/The_BENELUX_Technology_Innovation_Leader/brand_experience_report.html',
        file_name: 'brand_experience_report.html',
        persona_name: 'The BENELUX Technology Innovation Leader',
        report_type: 'Persona Report',
        category: 'Persona',
        size: '87.9 KB',
        modified: '2024-01-15 14:29',
        relative_path: 'The_BENELUX_Technology_Innovation_Leader/brand_experience_report.html'
      }
    ]
  }

  const findDefaultReport = (reports: HtmlReport[]): HtmlReport | null => {
    // Priority 1: Consolidated report
    let defaultReport = reports.find(r => r.file_name.toLowerCase().includes('consolidated'))
    
    // Priority 2: Index report
    if (!defaultReport) {
      defaultReport = reports.find(r => r.file_name.toLowerCase().includes('index'))
    }
    
    // Priority 3: First executive report
    if (!defaultReport) {
      const executiveReports = reports.filter(r => r.category === 'Executive')
      if (executiveReports.length > 0) {
        defaultReport = executiveReports[0]
      }
    }
    
    // Priority 4: Any report
    if (!defaultReport && reports.length > 0) {
      defaultReport = reports[0]
    }
    
    return defaultReport || null
  }

  const loadHtmlContent = async (report: HtmlReport) => {
    try {
      // In real app, would fetch actual HTML content from the file
      const mockHtmlContent = generateMockHtmlContent(report)
      setHtmlContent(mockHtmlContent)
    } catch (err) {
      setError('Failed to load HTML content')
    }
  }

  const generateMockHtmlContent = (report: HtmlReport): string => {
    const baseContent = `
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>${report.persona_name} - ${report.report_type}</title>
        <style>
            body {
                font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Roboto', 'Oxygen', 'Ubuntu', 'Cantarell', 'Fira Sans', 'Droid Sans', 'Helvetica Neue', sans-serif;
                line-height: 1.6;
                color: #333;
                max-width: 1200px;
                margin: 0 auto;
                padding: 20px;
                background: #f8fafc;
            }
            .header {
                background: linear-gradient(135deg, #4D1D82, #8b1d82);
                color: white;
                padding: 2rem;
                border-radius: 12px;
                margin-bottom: 2rem;
                text-align: center;
            }
            .header h1 {
                margin: 0;
                font-size: 2.5rem;
                font-weight: 700;
            }
            .header p {
                margin: 0.5rem 0 0 0;
                font-size: 1.1rem;
                opacity: 0.9;
            }
            .section {
                background: white;
                padding: 2rem;
                border-radius: 12px;
                margin-bottom: 2rem;
                box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            }
            .section h2 {
                color: #4D1D82;
                border-bottom: 2px solid #4D1D82;
                padding-bottom: 0.5rem;
                margin-bottom: 1.5rem;
            }
            .metrics-grid {
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
                gap: 1.5rem;
                margin: 1.5rem 0;
            }
            .metric-card {
                background: linear-gradient(135deg, #f8fafc, #e2e8f0);
                padding: 1.5rem;
                border-radius: 8px;
                text-align: center;
                border: 1px solid #e2e8f0;
            }
            .metric-value {
                font-size: 2rem;
                font-weight: bold;
                color: #4D1D82;
                margin-bottom: 0.5rem;
            }
            .metric-label {
                color: #64748b;
                font-size: 0.9rem;
                font-weight: 500;
            }
            .navigation-links {
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
                gap: 1rem;
                margin: 2rem 0;
            }
            .nav-link {
                background: white;
                border: 2px solid #e2e8f0;
                border-radius: 8px;
                padding: 1.5rem;
                text-decoration: none;
                color: #4D1D82;
                transition: all 0.3s ease;
                display: block;
            }
            .nav-link:hover {
                border-color: #4D1D82;
                background: #f8fafc;
                transform: translateY(-2px);
                box-shadow: 0 4px 8px rgba(0,0,0,0.1);
            }
            .nav-link h3 {
                margin: 0 0 0.5rem 0;
                font-size: 1.2rem;
            }
            .nav-link p {
                margin: 0;
                color: #64748b;
                font-size: 0.9rem;
            }
            .chart-placeholder {
                background: #f1f5f9;
                border: 2px dashed #cbd5e1;
                border-radius: 8px;
                padding: 3rem;
                text-align: center;
                margin: 1.5rem 0;
                color: #64748b;
            }
            .recommendations {
                background: #fef3c7;
                border-left: 4px solid #f59e0b;
                padding: 1.5rem;
                border-radius: 8px;
                margin: 1.5rem 0;
            }
            .recommendations h3 {
                color: #92400e;
                margin-top: 0;
            }
            .recommendations ul {
                margin: 0;
                padding-left: 1.5rem;
            }
            .recommendations li {
                margin-bottom: 0.5rem;
                color: #78350f;
            }
            .footer {
                text-align: center;
                color: #64748b;
                font-size: 0.9rem;
                margin-top: 3rem;
                padding-top: 2rem;
                border-top: 1px solid #e2e8f0;
            }
        </style>
    </head>
    <body>
        <div class="header">
            <h1>📊 ${report.persona_name}</h1>
            <p>${report.report_type} - Brand Experience Analysis</p>
        </div>
    `

    if (report.report_type === 'Strategic Analysis' && report.file_name.includes('index')) {
      return baseContent + `
        <div class="section">
            <h2>🎯 Available Reports</h2>
            <p>This is the main index page for all brand audit reports. Select from the available persona-specific reports and executive summaries below.</p>
            
            <div class="navigation-links">
                <a href="consolidated_brand_experience_report.html" class="nav-link">
                    <h3>📋 Consolidated Brand Report</h3>
                    <p>Comprehensive analysis across all personas and touchpoints</p>
                </a>
                <a href="The_Technical_Influencer/brand_experience_report.html" class="nav-link">
                    <h3>🔧 The Technical Influencer</h3>
                    <p>Persona-specific brand experience analysis</p>
                </a>
                <a href="The_Benelux_Cybersecurity_Decision_Maker/brand_experience_report.html" class="nav-link">
                    <h3>🛡️ The Benelux Cybersecurity Decision Maker</h3>
                    <p>Persona-specific brand experience analysis</p>
                </a>
                <a href="The_Benelux_Strategic_Business_Leader_C-Suite_Executive/brand_experience_report.html" class="nav-link">
                    <h3>👔 The Benelux Strategic Business Leader</h3>
                    <p>C-Suite Executive persona analysis</p>
                </a>
                <a href="The_Benelux_Transformation_Programme_Leader/brand_experience_report.html" class="nav-link">
                    <h3>🚀 The Benelux Transformation Programme Leader</h3>
                    <p>Persona-specific brand experience analysis</p>
                </a>
                <a href="The_BENELUX_Technology_Innovation_Leader/brand_experience_report.html" class="nav-link">
                    <h3>💡 The BENELUX Technology Innovation Leader</h3>
                    <p>Persona-specific brand experience analysis</p>
                </a>
            </div>
        </div>

        <div class="section">
            <h2>📊 Quick Stats</h2>
            <div class="metrics-grid">
                <div class="metric-card">
                    <div class="metric-value">6</div>
                    <div class="metric-label">Persona Reports</div>
                </div>
                <div class="metric-card">
                    <div class="metric-value">2</div>
                    <div class="metric-label">Executive Reports</div>
                </div>
                <div class="metric-card">
                    <div class="metric-value">547</div>
                    <div class="metric-label">Total Pages Analyzed</div>
                </div>
                <div class="metric-card">
                    <div class="metric-value">7.2</div>
                    <div class="metric-label">Average Brand Score</div>
                </div>
            </div>
        </div>

        <div class="footer">
            <p>Generated by Sopra Steria Brand Health Command Center</p>
            <p>Report generated on ${new Date().toLocaleDateString()}</p>
        </div>
    </body>
    </html>
    `
    }

    // For persona reports and consolidated reports
    return baseContent + `
        <div class="section">
            <h2>📊 Executive Summary</h2>
            <div class="metrics-grid">
                <div class="metric-card">
                    <div class="metric-value">7.${Math.floor(Math.random() * 9)}</div>
                    <div class="metric-label">Overall Brand Score</div>
                </div>
                <div class="metric-card">
                    <div class="metric-value">${Math.floor(Math.random() * 50) + 30}</div>
                    <div class="metric-label">Pages Analyzed</div>
                </div>
                <div class="metric-card">
                    <div class="metric-value">${Math.floor(Math.random() * 20) + 65}%</div>
                    <div class="metric-label">Success Rate</div>
                </div>
                <div class="metric-card">
                    <div class="metric-value">${Math.floor(Math.random() * 15) + 5}</div>
                    <div class="metric-label">Critical Issues</div>
                </div>
            </div>
        </div>

        <div class="section">
            <h2>🎯 Key Findings</h2>
            <div class="chart-placeholder">
                <h3>📈 Brand Performance Chart</h3>
                <p>Interactive charts would be displayed here showing brand performance across different criteria</p>
            </div>
            
            <div class="recommendations">
                <h3>💡 Priority Recommendations</h3>
                <ul>
                    <li>Improve brand messaging consistency across all touchpoints</li>
                    <li>Enhance visual identity implementation on key pages</li>
                    <li>Strengthen trust signals and credibility indicators</li>
                    <li>Optimize user experience flows for better conversion</li>
                    <li>Implement comprehensive social proof elements</li>
                </ul>
            </div>
        </div>

        <div class="section">
            <h2>📋 Detailed Analysis</h2>
            <p>This section would contain detailed analysis of brand performance across multiple dimensions including:</p>
            <ul>
                <li><strong>Brand Positioning:</strong> How well the brand message is communicated</li>
                <li><strong>Visual Identity:</strong> Consistency of visual elements and design</li>
                <li><strong>User Experience:</strong> Navigation, usability, and conversion optimization</li>
                <li><strong>Content Quality:</strong> Relevance, clarity, and engagement of content</li>
                <li><strong>Trust & Credibility:</strong> Social proof, testimonials, and trust signals</li>
                <li><strong>Technical Performance:</strong> Site speed, mobile optimization, and accessibility</li>
            </ul>
            
            <div class="chart-placeholder">
                <h3>📊 Performance Breakdown</h3>
                <p>Detailed performance metrics and comparative analysis would be displayed here</p>
            </div>
        </div>

        <div class="section">
            <h2>🚀 Implementation Roadmap</h2>
            <div class="chart-placeholder">
                <h3>📅 Timeline View</h3>
                <p>Implementation timeline with priorities and milestones would be displayed here</p>
            </div>
        </div>

        <div class="footer">
            <p>Generated by Sopra Steria Brand Health Command Center</p>
            <p>Report generated on ${new Date().toLocaleDateString()} for ${report.persona_name}</p>
        </div>
    </body>
    </html>
    `
  }

  const handleReportSelection = async (event: React.ChangeEvent<HTMLSelectElement>) => {
    const selectedValue = event.target.value
    if (selectedValue && !selectedValue.startsWith('---')) {
      const report = reports.find(r => {
        const displayName = `${r.persona_name} - ${r.report_type}`
        return displayName === selectedValue
      })
      if (report) {
        setSelectedReport(report)
        await loadHtmlContent(report)
      }
    }
  }

  const handleRegenerateReports = async () => {
    setRegenerating(true)
    try {
      // Mock regeneration - in real app would call API
      await new Promise(resolve => setTimeout(resolve, 2000))
      await scanHtmlReports()
    } catch (err) {
      setError('Failed to regenerate reports')
    } finally {
      setRegenerating(false)
    }
  }

  const handleDownloadReport = () => {
    if (selectedReport && htmlContent) {
      const blob = new Blob([htmlContent], { type: 'text/html' })
      const url = URL.createObjectURL(blob)
      const a = document.createElement('a')
      a.href = url
      a.download = selectedReport.file_name
      document.body.appendChild(a)
      a.click()
      document.body.removeChild(a)
      URL.revokeObjectURL(url)
    }
  }

  const handleDownloadAll = () => {
    // Mock download all functionality
    const timestamp = new Date().toISOString().replace(/[:.]/g, '-').slice(0, 19)
    const filename = `sopra_brand_reports_${timestamp}.zip`
    
    // In real app, would create actual ZIP file
    const mockZipContent = 'Mock ZIP file content with all reports'
    const blob = new Blob([mockZipContent], { type: 'application/zip' })
    const url = URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = filename
    document.body.appendChild(a)
    a.click()
    document.body.removeChild(a)
    URL.revokeObjectURL(url)
  }

  const createReportOptions = (): { options: string[], defaultIndex: number } => {
    const reportOptions: ReportOptions = {}
    
    // Group reports by category
    reports.forEach(report => {
      const category = report.category
      if (!reportOptions[category]) {
        reportOptions[category] = []
      }
      
      const displayName = `${report.persona_name} - ${report.report_type}`
      reportOptions[category].push({ display_name: displayName, report })
    })

    // Create flattened list for select
    const allOptions: string[] = []
    let defaultIndex = 0
    let currentIndex = 0

    Object.entries(reportOptions).forEach(([category, categoryReports]) => {
      allOptions.push(`--- ${category} Reports ---`)
      currentIndex += 1
      
      categoryReports.forEach(({ display_name, report }) => {
        allOptions.push(display_name)
        // Set consolidated report or index as default
        if (report.file_name.toLowerCase().includes('consolidated') || 
            report.file_name.toLowerCase().includes('index') || 
            report.category === 'Executive') {
          defaultIndex = currentIndex
        }
        currentIndex += 1
      })
    })

    // If no specific default found, use first actual report
    if (defaultIndex === 0 && allOptions.length > 1) {
      defaultIndex = 1
    }

    return { options: allOptions, defaultIndex }
  }

  if (loading) {
    return (
      <div className="page-container">
        <div className="main-header">
          <h1>📄 Audit Reports</h1>
          <p>Access and manage comprehensive audit reports and documentation.</p>
        </div>
        <div className="loading-state">
          <div className="loading-spinner"></div>
          <p>Scanning HTML reports...</p>
        </div>
      </div>
    )
  }

  if (error) {
    return (
      <div className="page-container">
        <div className="main-header">
          <h1>📄 Audit Reports</h1>
          <p>Access and manage comprehensive audit reports and documentation.</p>
        </div>
        <div className="error-state">
          <div className="error-message">
            <h2>⚠️ Error Loading Reports</h2>
            <p>{error}</p>
            <button onClick={scanHtmlReports} className="retry-button">
              🔄 Retry
            </button>
          </div>
        </div>
      </div>
    )
  }

  if (reports.length === 0) {
    return (
      <div className="page-container">
        <div className="main-header">
          <h1>📄 Audit Reports</h1>
          <p>Access and manage comprehensive audit reports and documentation.</p>
        </div>
        <div className="section">
          <div className="warning-message">
            <h2>⚠️ No audit reports found in the html_reports/ directory</h2>
            <p>Generate reports using the Reports Export page or run the HTML Report Generator.</p>
            <button 
              onClick={handleRegenerateReports} 
              disabled={regenerating}
              className="generate-button"
            >
              {regenerating ? '🔄 Generating Reports...' : '🔄 Generate Reports'}
            </button>
          </div>
        </div>
      </div>
    )
  }

  // Calculate metrics
  const executiveReports = reports.filter(r => r.category === 'Executive')
  const personaReports = reports.filter(r => r.category === 'Persona')
  const { options, defaultIndex } = createReportOptions()

  return (
    <div className="page-container">
      {/* Header */}
      <div className="main-header">
        <h1>📄 Audit Reports</h1>
        <p>Access and manage comprehensive audit reports and documentation.</p>
      </div>

      {/* Quick Metrics */}
      <div className="section">
        <div className="metrics-grid">
          <div className="metric-card">
            <div className="metric-value">{reports.length}</div>
            <div className="metric-label">📄 Total Reports</div>
          </div>
          <div className="metric-card">
            <div className="metric-value">{personaReports.length}</div>
            <div className="metric-label">👥 Persona Reports</div>
          </div>
          <div className="metric-card">
            <div className="metric-value">{executiveReports.length}</div>
            <div className="metric-label">🎯 Executive Reports</div>
          </div>
        </div>
      </div>

      {/* Action Buttons */}
      <div className="section">
        <div className="action-buttons">
          <button 
            onClick={handleRegenerateReports} 
            disabled={regenerating}
            className="action-button secondary"
          >
            {regenerating ? '🔄 Regenerating...' : '🔄 Regenerate All'}
          </button>
          <button 
            onClick={handleDownloadAll}
            className="action-button secondary"
          >
            📦 Download All
          </button>
        </div>
      </div>

      {/* Report Selector */}
      <div className="section">
        <div className="report-selector">
          <label htmlFor="report-select">🔍 Select Report to View:</label>
          <select 
            id="report-select"
            onChange={handleReportSelection}
            defaultValue={options[defaultIndex]}
            className="report-select"
          >
            {options.map((option, index) => (
              <option 
                key={index} 
                value={option}
                disabled={option.startsWith('---')}
                className={option.startsWith('---') ? 'option-header' : ''}
              >
                {option}
              </option>
            ))}
          </select>
        </div>
      </div>

      {/* Report Details and Content */}
      {selectedReport && (
        <>
          <div className="section">
            <div className="report-details">
              <div className="report-info">
                <strong>📋 {selectedReport.persona_name} - {selectedReport.report_type}</strong>
                <span className="separator">•</span>
                <span>📁 {selectedReport.file_name}</span>
                <span className="separator">•</span>
                <span>📏 {selectedReport.size}</span>
                <span className="separator">•</span>
                <span>🕒 {selectedReport.modified}</span>
              </div>
              <div className="report-actions">
                <button 
                  onClick={handleDownloadReport}
                  className="download-button"
                >
                  ⬇️ Download Report
                </button>
              </div>
            </div>
          </div>

          <div className="section">
            <h2>📄 Report Content</h2>
            <div className="html-viewer">
              {htmlContent && (
                <iframe
                  srcDoc={htmlContent}
                  style={{
                    width: '100%',
                    height: '800px',
                    border: '1px solid var(--border-color)',
                    borderRadius: 'var(--border-radius)'
                  }}
                  title={`${selectedReport.persona_name} - ${selectedReport.report_type}`}
                />
              )}
            </div>
          </div>

          {/* Technical Details */}
          <details className="technical-details">
            <summary>🔧 Technical Details</summary>
            <div className="details-grid">
              <div className="detail-item">
                <strong>Path:</strong> <code>{selectedReport.relative_path}</code>
              </div>
              <div className="detail-item">
                <strong>Category:</strong> {selectedReport.category}
              </div>
              <div className="detail-item">
                <strong>Type:</strong> {selectedReport.report_type}
              </div>
              <div className="detail-item">
                <strong>Size:</strong> {selectedReport.size}
              </div>
            </div>
          </details>
        </>
      )}
    </div>
  )
}

export default AuditReports
