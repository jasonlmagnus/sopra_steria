import React from 'react'
import { useQuery } from '@tanstack/react-query'

const apiBase = import.meta.env.VITE_API_URL || 'http://localhost:3000'

function Methodology() {
  const { data, isLoading, error } = useQuery({
    queryKey: ['methodology'],
    queryFn: async () => {
      const res = await fetch(`${apiBase}/api/methodology`)
      if (!res.ok) throw new Error('Failed to load methodology')
      return res.json()
    }
  })

  if (isLoading) return <p>Loading methodology...</p>
  if (error) return <p>Error loading methodology</p>

  const formula = data?.calculation?.formula
  const descriptors = data?.scoring?.descriptors || {}

  return (
    <div>
      <h2>Methodology</h2>
      {formula && (
        <p>
          <strong>Score Formula:</strong> {formula}
        </p>
      )}
      <h3>Score Descriptors</h3>
      <ul>
        {Object.entries(descriptors).map(([range, details]: any) => (
          <li key={range}>
            {range}: {details.label} ({details.status})
          </li>
        ))}
      </ul>
    </div>
  )
}

export default Methodology
