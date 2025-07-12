import React, { useEffect, useState, useCallback } from 'react'
import { Banner, ExpandableCard } from '../components'

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

  const scanHtmlReports = useCallback(async () => {
    try {
      setLoading(true)
      
      const response = await fetch('http://localhost:3000/api/html-reports')
      let reportsData: HtmlReport[] = []
      
      if (response.ok) {
        const data = await response.json()
        reportsData = data.reports || []
      } else {
        reportsData = generateMockReports()
      }
      
      setReports(reportsData)
      
      const defaultReport = findDefaultReport(reportsData)
      if (defaultReport) {
        setSelectedReport(defaultReport)
        await loadHtmlContent(defaultReport)
      }
      
    } catch (err) {
      console.error('Error scanning HTML reports:', err)
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
  }, [])

  useEffect(() => {
    scanHtmlReports()
  }, [scanHtmlReports])

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
    ]
  }

  const findDefaultReport = (reports: HtmlReport[]): HtmlReport | null => {
    let defaultReport = reports.find(r => r.file_name.toLowerCase().includes('index'))
    if (!defaultReport) {
      defaultReport = reports.find(r => r.file_name.toLowerCase().includes('consolidated'))
    }
    if (!defaultReport) {
      defaultReport = reports.filter(r => r.category === 'Executive')[0]
    }
    if (!defaultReport && reports.length > 0) {
      defaultReport = reports[0]
    }
    return defaultReport || null
  }

  const loadHtmlContent = async (report: HtmlReport) => {
    try {
      const response = await fetch(`http://localhost:3000/api/html-reports/${report.relative_path}`)
      if (response.ok) {
        setHtmlContent(await response.text())
      } else {
        setHtmlContent(`
          <div style="padding: 2rem; font-family: Arial, sans-serif;">
            <h1>📄 ${report.persona_name} - ${report.report_type}</h1>
            <p>Could not load report content. This is a placeholder.</p>
          </div>
        `)
      }
    } catch (err) {
      console.error('Error loading HTML content:', err)
      setHtmlContent(`
        <div style="padding: 2rem; color: #666; font-family: Arial, sans-serif;">
          <h2>⚠️ Error Loading Report</h2>
        </div>
      `)
    }
  }

  const handleReportSelection = async (event: React.ChangeEvent<HTMLSelectElement>) => {
    const selectedValue = event.target.value
    if (selectedValue.startsWith('---')) return
    const report = reports.find(r => `${r.persona_name} - ${r.report_type}` === selectedValue)
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
        await scanHtmlReports()
        alert('✅ Reports regenerated successfully!')
      } else {
        alert('❌ Failed to regenerate reports.')
      }
    } catch (err) {
      console.error('Error regenerating reports:', err)
      alert('❌ Error regenerating reports.')
    } finally {
      setRegenerating(false)
    }
  }

  const handleDownloadReport = () => {
    if (!selectedReport) return
    const blob = new Blob([htmlContent], { type: 'text/html' })
    const link = document.createElement('a')
    link.href = URL.createObjectURL(blob)
    link.download = selectedReport.file_name
    document.body.appendChild(link)
    link.click()
    document.body.removeChild(link)
  }

  const handleDownloadAll = async () => {
    const response = await fetch('http://localhost:3000/api/download-all-reports')
    if (response.ok) {
      const blob = await response.blob()
      const link = document.createElement('a')
      link.href = URL.createObjectURL(blob)
      link.download = 'sopra_steria_brand_reports.zip'
      document.body.appendChild(link)
      link.click()
      document.body.removeChild(link)
    } else {
      alert('Failed to download all reports.')
    }
  }

  const createReportOptions = (): { options: (JSX.Element | null)[], defaultIndex: number } => {
    const categories: { [key: string]: HtmlReport[] } = {
      Executive: [],
      Persona: [],
      Other: []
    }
    reports.forEach(r => {
      categories[r.category] = [...(categories[r.category] || []), r]
    })

    let defaultIndex = 0
    let currentIndex = 0
    const options = Object.entries(categories).flatMap(([category, reports]) => {
      if (reports.length === 0) return []
      const reportOptions = reports.map(r => {
        const value = `${r.persona_name} - ${r.report_type}`
        if (selectedReport && value === `${selectedReport.persona_name} - ${selectedReport.report_type}`) {
          defaultIndex = currentIndex + 1
        }
        currentIndex++
        return <option key={value} value={value}>{value}</option>
      })
      currentIndex++
      return [
        <option key={category} disabled value={`---${category}---`}>{`--- ${category} ---`}</option>,
        ...reportOptions
      ]
    })
    return { options, defaultIndex }
  }

  const { options, defaultIndex } = createReportOptions()

  return (
    <div className="flex h-screen bg-gray-100">
      <div className="w-1/4 bg-gray-50 p-4 flex flex-col border-r border-gray-200">
        <h1 className="text-2xl font-bold mb-4">📄 Audit Reports</h1>
        
        <div className="mb-4">
          <label htmlFor="report-select" className="block text-sm font-medium text-gray-700 mb-1">Select Report</label>
          <select
            id="report-select"
            className="select--form"
            onChange={handleReportSelection}
            value={selectedReport ? `${selectedReport.persona_name} - ${selectedReport.report_type}` : ''}
          >
            {options}
          </select>
        </div>

        <button
          onClick={handleRegenerateReports}
          className="button--action mb-4"
          disabled={regenerating}
        >
          {regenerating ? '🔄 Regenerating...' : '🔄 Regenerate All'}
        </button>

        <button
          onClick={handleDownloadReport}
          className="button--action"
          disabled={!selectedReport}
        >
          Download Selected Report
        </button>

        <ExpandableCard title="Advanced Export">
          <div className="flex flex-col space-y-2">
            <button
              onClick={handleDownloadAll}
              className="button--secondary"
            >
              Download All Reports as ZIP
            </button>
            <Banner type="info" message="This may take a few moments to process."/>
          </div>
        </ExpandableCard>

        <div style={{ marginTop: 'auto' }}>
          <ExpandableCard title="ℹ️ Quick Help">
            <div className="text--body-sm space-y-2">
              <p><strong>Quick Usage:</strong> Page auto-loads the main report → Use dropdown to switch reports → Download individual or bulk reports.</p>
              <p><strong>Features:</strong> Auto-loading default report • In-dashboard viewing • No new windows • ZIP downloads • Auto-regeneration from latest data.</p>
            </div>
          </ExpandableCard>
        </div>
      </div>

      <div className="flex-grow p-4 bg-white border-l border-gray-200">
        {loading ? (
          <div className="flex items-center justify-center h-full">
            <div className="text-center">
              <div className="text-2xl">Loading Report...</div>
              <div className="text-gray-500">Please wait while the report is being loaded.</div>
            </div>
          </div>
        ) : (
          <>
            <div className="flex justify-between items-center mb-4">
              <h2 className="text-xl font-bold">{selectedReport?.persona_name} - {selectedReport?.report_type}</h2>
              <div className="flex items-center space-x-2">
                <a href={`http://localhost:3000/api/html-reports/${selectedReport?.relative_path}`} target="_blank" rel="noopener noreferrer" className="button--secondary">
                  Open in New Tab
                </a>
              </div>
            </div>

            <ExpandableCard title="Technical Details">
              <div className="p-2 mt-2 border rounded-md bg-gray-50 text-xs">
                <strong>File Path:</strong> {selectedReport?.file_path}<br/>
                <strong>Relative Path:</strong> {selectedReport?.relative_path}<br/>
                <strong>Size:</strong> {selectedReport?.size}
              </div>
            </ExpandableCard>

            <iframe 
              srcDoc={htmlContent} 
              title="Audit Report" 
              className="w-full h-full border rounded-md"
              style={{ minHeight: '80vh' }}
            />
          </>
        )}
      </div>
    </div>
  )
}

export default AuditReports
