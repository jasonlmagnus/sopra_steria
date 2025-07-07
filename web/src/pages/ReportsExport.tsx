import React, { useEffect, useState } from 'react'
import { TabNavigation } from '../components'

function ReportsExport() {
  const [reports, setReports] = useState<string[]>([])

  useEffect(() => {
    fetch('http://localhost:3000/api/reports')
      .then((res) => res.json())
      .then((data) => setReports(data.reports || []))
      .catch(() => setReports([]))
  }, [])

  const tabs = [
    {
      label: 'HTML Reports',
      content: (
        <ul>
          {reports.map((r) => (
            <li key={r}>
              <a href={`http://localhost:3000/api/reports/${r}`} target="_blank" rel="noreferrer">
                {r}
              </a>
            </li>
          ))}
        </ul>
      )
    },
    {
      label: 'Audit CSV',
      content: (
        <a href="http://localhost:3000/api/download/unified_audit_data.csv" target="_blank" rel="noreferrer">
          unified_audit_data.csv
        </a>
      )
    },
    {
      label: 'Experience CSV',
      content: (
        <a href="http://localhost:3000/api/download/unified_experience_data.csv" target="_blank" rel="noreferrer">
          unified_experience_data.csv
        </a>
      )
    },
    {
      label: 'Persona Journeys',
      content: (
        <a href="http://localhost:3000/api/persona-journeys" target="_blank" rel="noreferrer">
          View Journey Files
        </a>
      )
    }
  ]

  return (
    <div>
      <h2>Reports Export</h2>
      <TabNavigation tabs={tabs} />
    </div>
  )
}

export default ReportsExport;
