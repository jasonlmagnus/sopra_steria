import { useQuery } from '@tanstack/react-query'
import React from 'react'
import PageContainer from '../components/PageContainer'

const apiBase = import.meta.env.VITE_API_URL || 'http://localhost:3000'

function GapAnalysis() {
  const { data, isLoading, error } = useQuery({
    queryKey: ['gap-analysis'],
    queryFn: async () => {
      const res = await fetch(`${apiBase}/api/gap-analysis`)
      if (!res.ok) throw new Error('Failed to load gap analysis')
      return res.json()
    }
  })

  if (isLoading) return <p>Loading gap analysis...</p>
  if (error) return <p>Error loading gap analysis</p>

  const items = data?.items || []

  return (
    <PageContainer title="Gap Analysis">
      <ul>
        {items.map((it: string, idx: number) => (
          <li key={idx}>{it}</li>
        ))}
      </ul>
    </PageContainer>
  )
}

export default GapAnalysis
