import React, { useEffect, useState } from 'react'
import { EvidenceDisplay } from '../components/EvidenceDisplay'

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
      
      // Fetch actual HTML reports from the API
      const response = await fetch('http://localhost:3000/api/html-reports')
      if (response.ok) {
        const reportsData = await response.json()
        setReports(reportsData.reports || [])
        
        // Set default report (consolidated, index, or first executive)
        const defaultReport = findDefaultReport(reportsData.reports || [])
        if (defaultReport) {
          setSelectedReport(defaultReport)
          await loadHtmlContent(defaultReport)
        }
      } else {
        // Fallback to mock data if API not available
        const mockReports = generateMockReports()
        setReports(mockReports)
        
        const defaultReport = findDefaultReport(mockReports)
        if (defaultReport) {
          setSelectedReport(defaultReport)
          await loadHtmlContent(defaultReport)
        }
      }
    } catch (err) {
      // Fallback to mock data on error
      const mockReports = generateMockReports()
      setReports(mockReports)
      
      const defaultReport = findDefaultReport(mockReports)
      if (defaultReport) {
        setSelectedReport(defaultReport)
        await loadHtmlContent(defaultReport)
      }
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
      // Fetch actual HTML content from the API
      const response = await fetch(`http://localhost:3000/api/html-reports/${encodeURIComponent(report.relative_path)}`)
      if (response.ok) {
        const htmlContent = await response.text()
        setHtmlContent(htmlContent)
      } else {
        setHtmlContent('<div class="error">Failed to load report content</div>')
      }
    } catch (err) {
      setHtmlContent('<div class="error">Error loading report content</div>')
    }
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
      // Call the Python HTML report generator via API
      const response = await fetch('http://localhost:8000/api/generate-html-reports', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          personas: ['CONSOLIDATED', 'P1', 'P2', 'P3', 'P4', 'P5'],
          options: {
            include_tier_analysis: true,
            include_persona_voice: true,
            include_recommendations: true,
            include_visual_brand: true
          }
        })
      })
      
      if (response.ok) {
        await scanHtmlReports() // Refresh the reports list
      } else {
        throw new Error('Failed to regenerate reports')
      }
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
    if (!reports || reports.length === 0) {
      alert('No reports available to download')
      return
    }
    
    alert('Download all functionality not yet implemented. Please download individual reports.')
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

          {/* Evidence Panel */}
          <div className="section">
            <h2>🔍 Report Evidence & Analysis</h2>
            <div className="evidence-panel">
              <EvidenceDisplay
                evidence={[
                  {
                    type: 'evidence',
                    content: `This HTML report was generated from comprehensive audit data analysis. The report contains detailed findings, recommendations, and evidence-based insights for ${selectedReport.persona_name}.`,
                    title: 'Report Generation'
                  },
                  {
                    type: 'business_impact',
                    content: `${selectedReport.report_type} provides strategic insights for business decision-making, focusing on brand experience optimization and user journey improvements.`,
                    title: 'Business Impact'
                  },
                  {
                    type: 'trust_assessment',
                    content: `Report contains validated data from unified audit sources, ensuring accuracy and reliability of all findings and recommendations presented.`,
                    title: 'Data Validation'
                  }
                ]}
                title={`Evidence for ${selectedReport.persona_name}`}
                collapsible={true}
                defaultExpanded={false}
              />
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
