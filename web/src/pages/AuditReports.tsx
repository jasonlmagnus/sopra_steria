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

function AuditReports() {
  const [reports, setReports] = useState<HtmlReport[]>([])
  const [selectedReport, setSelectedReport] = useState<HtmlReport | null>(null)
  const [loading, setLoading] = useState(true)
  const [htmlContent, setHtmlContent] = useState<string>('')
  const [regenerating, setRegenerating] = useState(false)

  useEffect(() => {
    scanHtmlReports()
  }, [])

  const scanHtmlReports = async () => {
    try {
      setLoading(true)
      
      // Try to fetch from API first
      const response = await fetch('http://localhost:3000/api/html-reports')
      let reportsData: HtmlReport[] = []
      
      if (response.ok) {
        const data = await response.json()
        reportsData = data.reports || []
      } else {
        // Fallback to mock data that matches actual html_reports structure
        reportsData = generateMockReports()
      }
      
      setReports(reportsData)
      
      // Auto-select default report (consolidated, index, or first executive)
      const defaultReport = findDefaultReport(reportsData)
      if (defaultReport) {
        setSelectedReport(defaultReport)
        await loadHtmlContent(defaultReport)
      }
      
    } catch (err) {
      console.error('Error scanning HTML reports:', err)
      // Fallback to mock data
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
    // Priority 1: Index report (main landing page)
    let defaultReport = reports.find(r => r.file_name.toLowerCase().includes('index'))
    
    // Priority 2: Consolidated report
    if (!defaultReport) {
      defaultReport = reports.find(r => r.file_name.toLowerCase().includes('consolidated'))
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
      // Try to fetch actual HTML content
      const response = await fetch(`http://localhost:3000/api/html-reports/${report.relative_path}`)
      if (response.ok) {
        const content = await response.text()
        setHtmlContent(content)
      } else {
        // Fallback to placeholder content
        setHtmlContent(`
          <div style="padding: 2rem; font-family: Arial, sans-serif;">
            <h1>📄 ${report.persona_name} - ${report.report_type}</h1>
            <p><strong>Report:</strong> ${report.file_name}</p>
            <p><strong>Size:</strong> ${report.size}</p>
            <p><strong>Modified:</strong> ${report.modified}</p>
            <hr style="margin: 2rem 0;">
            <p>This is a placeholder for the actual HTML report content. The report would normally be loaded from:</p>
            <code>${report.file_path}</code>
            <p style="margin-top: 2rem; color: #666;">
              In a real deployment, this would display the comprehensive brand experience report generated by the HTML report generator.
            </p>
          </div>
        `)
      }
    } catch (err) {
      console.error('Error loading HTML content:', err)
      setHtmlContent(`
        <div style="padding: 2rem; color: #666; font-family: Arial, sans-serif;">
          <h2>⚠️ Error Loading Report</h2>
          <p>Could not load the HTML report: ${report.file_name}</p>
          <p>Path: ${report.file_path}</p>
        </div>
      `)
    }
  }

  const handleReportSelection = async (event: React.ChangeEvent<HTMLSelectElement>) => {
    const selectedValue = event.target.value
    
    // Skip category headers
    if (selectedValue.startsWith('---')) return
    
    // Find the selected report
    const report = reports.find(r => 
      `${r.persona_name} - ${r.report_type}` === selectedValue
    )
    
    if (report) {
      setSelectedReport(report)
      await loadHtmlContent(report)
    }
  }

  const handleRegenerateReports = async () => {
    setRegenerating(true)
    try {
      const response = await fetch('http://localhost:3000/api/regenerate-reports', { method: 'POST' })
      if (response.ok) {
        // Refresh the reports list
        await scanHtmlReports()
        alert('✅ Reports regenerated successfully!')
      } else {
        alert('❌ Failed to regenerate reports. Check the logs for details.')
      }
    } catch (err) {
      console.error('Error regenerating reports:', err)
      alert('❌ Error regenerating reports. Please try again.')
    } finally {
      setRegenerating(false)
    }
  }

  const handleDownloadReport = () => {
    if (!selectedReport) return
    
    // Create download link for the selected report
    const link = document.createElement('a')
          link.href = `http://localhost:3000/api/html-reports/${selectedReport.relative_path}`
    link.download = selectedReport.file_name
    document.body.appendChild(link)
    link.click()
    document.body.removeChild(link)
  }

  const handleDownloadAll = async () => {
    try {
      const response = await fetch('http://localhost:3000/api/download-all-reports')
      if (response.ok) {
        const blob = await response.blob()
        const url = window.URL.createObjectURL(blob)
        const link = document.createElement('a')
        link.href = url
        link.download = `sopra_brand_reports_${new Date().toISOString().slice(0, 10)}.zip`
        document.body.appendChild(link)
        link.click()
        document.body.removeChild(link)
        window.URL.revokeObjectURL(url)
      } else {
        alert('❌ Failed to download reports archive')
      }
    } catch (err) {
      console.error('Error downloading all reports:', err)
      alert('❌ Error downloading reports archive')
    }
  }

  const createReportOptions = (): { options: string[], defaultIndex: number } => {
    const options: string[] = []
    let defaultIndex = 0
    let currentIndex = 0
    
    // Group reports by category
    const reportsByCategory = reports.reduce((acc, report) => {
      if (!acc[report.category]) acc[report.category] = []
      acc[report.category].push(report)
      return acc
    }, {} as Record<string, HtmlReport[]>)
    
    // Add category sections
    Object.entries(reportsByCategory).forEach(([category, categoryReports]) => {
      options.push(`--- ${category} Reports ---`)
      currentIndex++
      
      categoryReports.forEach(report => {
        const displayName = `${report.persona_name} - ${report.report_type}`
        options.push(displayName)
        
        // Set default to consolidated or index report
        if (selectedReport && 
            report.file_name === selectedReport.file_name && 
            report.persona_name === selectedReport.persona_name) {
          defaultIndex = currentIndex
        }
        
        currentIndex++
      })
    })
    
    return { options, defaultIndex }
  }

  if (loading) {
    return (
      <div className="page-container">
        <div className="loading-state">
          <div className="loading-spinner"></div>
          <p>Loading audit reports...</p>
        </div>
      </div>
    )
  }

  const executiveReports = reports.filter(r => r.category === 'Executive')
  const personaReports = reports.filter(r => r.category === 'Persona')
  const { options, defaultIndex } = createReportOptions()

  return (
    <div className="page-container">
      {/* Header - matching Streamlit style */}
      <div className="main-header">
        <h1>📄 Audit Reports</h1>
        <p>Access and manage comprehensive audit reports and documentation</p>
      </div>

      {/* Warning if no reports */}
      {reports.length === 0 && (
        <div className="section">
          <div className="alert alert--warning">
            <strong>⚠️ No audit reports found</strong> in the `html_reports/` directory.
          </div>
        </div>
      )}

      {/* Metrics - Clean 3-column layout */}
      {reports.length > 0 && (
        <div className="section">
          <div className="metrics-grid" style={{ gridTemplateColumns: 'repeat(3, 1fr)', gap: '1rem' }}>
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
      )}

      {/* Action buttons */}
      <div className="section">
        <div style={{ display: 'flex', gap: '1rem', marginBottom: '1rem' }}>
          <button 
            onClick={handleRegenerateReports}
            disabled={regenerating}
            className="action-button secondary"
            style={{ flex: 1 }}
          >
            {regenerating ? '🔄 Regenerating...' : '🔄 Regenerate All'}
          </button>
          <button 
            onClick={handleDownloadAll}
            className="action-button secondary"
            style={{ flex: 1 }}
          >
            📦 Download All
          </button>
        </div>
      </div>

      {/* Report selector */}
      {reports.length > 0 && (
        <div className="section">
          <label htmlFor="report-select" style={{ display: 'block', marginBottom: '0.5rem', fontWeight: '600' }}>
            🔍 Select Report to View:
          </label>
          <select 
            id="report-select"
            onChange={handleReportSelection}
            defaultValue={options[defaultIndex]}
            style={{ 
              width: '100%',
              padding: '0.75rem',
              fontSize: '1rem',
              border: '1px solid var(--border-color)',
              borderRadius: 'var(--border-radius)',
              background: 'var(--background)'
            }}
          >
            {options.map((option, index) => (
              <option 
                key={index} 
                value={option}
                disabled={option.startsWith('---')}
                style={{ 
                  fontWeight: option.startsWith('---') ? 'bold' : 'normal',
                  backgroundColor: option.startsWith('---') ? '#f0f0f0' : 'white'
                }}
              >
                {option}
              </option>
            ))}
          </select>
        </div>
      )}

      {/* Report content */}
      {selectedReport && (
        <>
          {/* Compact report details - one line */}
          <div className="section">
            <div style={{ 
              display: 'flex', 
              justifyContent: 'space-between', 
              alignItems: 'center',
              padding: '1rem',
              background: 'var(--background-secondary)',
              borderRadius: 'var(--border-radius)',
              marginBottom: '1rem'
            }}>
              <div style={{ fontSize: '0.9rem' }}>
                <strong>📋 {selectedReport.persona_name} - {selectedReport.report_type}</strong>
                <span style={{ margin: '0 0.5rem', color: '#666' }}>•</span>
                <span>📁 {selectedReport.file_name}</span>
                <span style={{ margin: '0 0.5rem', color: '#666' }}>•</span>
                <span>📏 {selectedReport.size}</span>
                <span style={{ margin: '0 0.5rem', color: '#666' }}>•</span>
                <span>🕒 {selectedReport.modified}</span>
              </div>
              <button 
                onClick={handleDownloadReport}
                className="action-button secondary"
                style={{ padding: '0.5rem 1rem', fontSize: '0.875rem' }}
              >
                ⬇️ Download Report
              </button>
            </div>
          </div>

          {/* Report content title */}
          <div className="section">
            <h2 style={{ marginBottom: '1rem' }}>📄 Report Content</h2>
            
            {/* HTML viewer - 800px height matching Streamlit */}
            <div style={{ 
              border: '1px solid var(--border-color)', 
              borderRadius: 'var(--border-radius)',
              overflow: 'hidden'
            }}>
              <iframe
                srcDoc={htmlContent}
                style={{
                  width: '100%',
                  height: '800px',
                  border: 'none'
                }}
                title={`${selectedReport.persona_name} - ${selectedReport.report_type}`}
              />
            </div>
          </div>

          {/* Compact technical details expander */}
          <details style={{ marginTop: '1rem', padding: '1rem', background: 'var(--background-secondary)', borderRadius: 'var(--border-radius)' }}>
            <summary style={{ cursor: 'pointer', fontWeight: '600' }}>
              🔧 Technical Details
            </summary>
            <div style={{ marginTop: '1rem', display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '1rem' }}>
              <div>
                <strong>Path:</strong> <code>{selectedReport.relative_path}</code><br/>
                <strong>Category:</strong> {selectedReport.category}
              </div>
              <div>
                <strong>Type:</strong> {selectedReport.report_type}<br/>
                <strong>Size:</strong> {selectedReport.size}
              </div>
            </div>
          </details>
        </>
      )}

      {/* Compact help */}
      <details style={{ marginTop: '2rem', padding: '1rem', background: 'var(--background-secondary)', borderRadius: 'var(--border-radius)' }}>
        <summary style={{ cursor: 'pointer', fontWeight: '600' }}>
          ℹ️ Quick Help
        </summary>
        <div style={{ marginTop: '1rem', fontSize: '0.9rem', color: '#666' }}>
          <p><strong>Quick Usage:</strong> Page auto-loads the main report → Use dropdown to switch reports → Download individual or bulk reports</p>
          <p><strong>Features:</strong> Auto-loading default report • In-dashboard viewing • No new windows • ZIP downloads • Auto-regeneration from latest data</p>
        </div>
      </details>
    </div>
  )
}

export default AuditReports
