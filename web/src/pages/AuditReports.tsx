import React from 'react'
import { useQuery } from '@tanstack/react-query'

function AuditReports() {
  const { data, isLoading } = useQuery({
    queryKey: ['reports'],
    queryFn: async () => {
      const res = await fetch('http://localhost:3000/api/reports')
      if (!res.ok) throw new Error('Failed to fetch reports')
      return res.json()
    }
  })

  if (isLoading) {
    return <p>Loading...</p>
  }

  return (
    <div>
      <h2>Audit Reports</h2>
      <ul>
        {data?.reports.map((r: string) => (
          <li key={r}>
            <a href={`http://localhost:3000/api/reports/${r}`}>{r}</a>
          </li>
        ))}
      </ul>
    </div>
  )
}

export default AuditReports;
