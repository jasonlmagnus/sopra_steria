import { useQuery } from '@tanstack/react-query'
import { BarChart, Bar, XAxis, YAxis, Tooltip } from 'recharts'

const apiBase = import.meta.env.VITE_API_URL || 'http://localhost:3000'

function PagesList() {
  const { data, isLoading, error } = useQuery({
    queryKey: ['pages'],
    queryFn: async () => {
      const res = await fetch(`${apiBase}/api/pages`)
      if (!res.ok) throw new Error('Failed to load pages')
      return res.json()
    },
  })

  if (isLoading) return <p>Loading pages...</p>
  if (error) return <p>Error loading pages</p>

  const pages = data?.pages || []

  return (
    <div>
      <h2>Pages Brand Score</h2>
      <BarChart width={600} height={300} data={pages.slice(0, 10)}>
        <XAxis dataKey="slug" hide={true} />
        <YAxis />
        <Tooltip />
        <Bar dataKey="avg_score" fill="#3d4a6b" />
      </BarChart>
    </div>
  )
}

export default PagesList
