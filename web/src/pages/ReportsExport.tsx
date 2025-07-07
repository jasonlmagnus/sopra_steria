import React, { useEffect, useState } from 'react'

function ReportsExport() {
  const [reports, setReports] = useState<string[]>([])

  useEffect(() => {
    fetch('http://localhost:3000/api/reports')
      .then((res) => res.json())
      .then((data) => setReports(data.reports || []))
      .catch(() => setReports([]))
  }, [])

  return (
    <div>
      <h2>Reports Export</h2>
      <p>Available reports:</p>
      <ul>
        {reports.map((r) => (
          <li key={r}>
            <a href={`http://localhost:3000/api/reports/${r}`} target="_blank" rel="noreferrer">
              {r}
            </a>
          </li>
        ))}
      </ul>
    </div>
  )
}

export default ReportsExport;
