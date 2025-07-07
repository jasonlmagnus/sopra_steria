import React from 'react'
import { useQuery } from '@tanstack/react-query'
import { TabNavigation } from '../components'

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

  const tabs = [
    {
      label: 'Overview',
      content: <p>{data?.metadata?.description}</p>
    },
    {
      label: 'Formula',
      content: formula ? <p><strong>Score Formula:</strong> {formula}</p> : null
    },
    {
      label: 'Descriptors',
      content: (
        <ul>
          {Object.entries(descriptors).map(([range, details]: any) => (
            <li key={range}>
              {range}: {details.label} ({details.status})
            </li>
          ))}
        </ul>
      )
    },
    {
      label: 'Onsite Tiers',
      content: <pre>{JSON.stringify(data?.classification?.onsite, null, 2)}</pre>
    },
    {
      label: 'Offsite Channels',
      content: <pre>{JSON.stringify(data?.classification?.offsite, null, 2)}</pre>
    },
    {
      label: 'Multipliers',
      content: <pre>{JSON.stringify(data?.calculation?.crisis_multipliers, null, 2)}</pre>
    }
  ]

  return (
    <div>
      <h2>Methodology</h2>
      <TabNavigation tabs={tabs} />
    </div>
  )
}

export default Methodology
