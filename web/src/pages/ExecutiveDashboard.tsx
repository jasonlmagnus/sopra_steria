import { useQuery } from '@tanstack/react-query'
import React from 'react'

const apiBase = import.meta.env.VITE_API_URL || 'http://localhost:3000'

function ExecutiveDashboard() {
  const { data, isLoading, error } = useQuery({
    queryKey: ['summary'],
    queryFn: async () => {
      const res = await fetch(`${apiBase}/api/summary`)
      if (!res.ok) throw new Error('Failed to load summary')
      return res.json()
    }
  })

  if (isLoading) return <p>Loading summary...</p>
  if (error) return <p>Error loading summary</p>

  const brand = data?.brand_health || {}
  const metrics = data?.key_metrics || {}
  const recs = Array.isArray(data?.recommendations) ? data.recommendations : []

  return (
    <div>
      <h2>Executive Dashboard</h2>
      <p>
        Brand Health: <strong>{brand.raw_score}</strong> {brand.emoji}
      </p>
      <ul>
        <li>Total Pages: {metrics.total_pages}</li>
        <li>Critical Issues: {metrics.critical_issues}</li>
        <li>Quick Wins: {metrics.quick_wins}</li>
        <li>Success Pages: {metrics.success_pages}</li>
      </ul>
      <h3>Top Recommendations</h3>
      <ul>
        {recs.map((r: string, idx: number) => (
          <li key={idx}>{r}</li>
        ))}
      </ul>
    </div>
  )
}

export default ExecutiveDashboard
