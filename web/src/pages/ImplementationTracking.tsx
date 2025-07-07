import React from 'react'
import { BarChart, Bar, XAxis, YAxis, Tooltip } from 'recharts'

interface Item {
  status: string
  progress: number
  team: string
  name: string
}

const sampleData: Record<string, Omit<Item, 'name'>> = {
  'Homepage Messaging': { status: 'completed', progress: 100, team: 'Marketing' },
  'Navigation UX': { status: 'in_progress', progress: 65, team: 'UX Team' },
  'Visual Brand Elements': { status: 'in_progress', progress: 30, team: 'Design' },
  'Social Media Consistency': { status: 'not_started', progress: 0, team: 'Social' },
  'Page Performance': { status: 'completed', progress: 100, team: 'Tech' }
}

function ImplementationTracking() {
  const items: Item[] = Object.entries(sampleData).map(([name, d]) => ({
    name,
    ...d
  }))

  const totalItems = items.length
  const completed = items.filter(i => i.status === 'completed').length
  const inProgress = items.filter(i => i.status === 'in_progress').length
  const avgProgress = items.reduce((sum, i) => sum + i.progress, 0) / totalItems
  const completionRate = (completed / totalItems) * 100

  return (
    <div>
      <h2>Implementation Tracking</h2>
      <div style={{ display: 'flex', gap: '1rem', marginBottom: '1rem' }}>
        <div>
          <strong>{totalItems}</strong>
          <div>Total Items</div>
        </div>
        <div>
          <strong>{completionRate.toFixed(1)}%</strong>
          <div>Completion Rate</div>
        </div>
        <div>
          <strong>{avgProgress.toFixed(1)}%</strong>
          <div>Avg Progress</div>
        </div>
        <div>
          <strong>{inProgress}</strong>
          <div>In Progress</div>
        </div>
      </div>

      <BarChart width={600} height={300} data={items} style={{ marginBottom: '1rem' }}>
        <XAxis dataKey="name" hide={true} />
        <YAxis />
        <Tooltip />
        <Bar dataKey="progress" fill="#3d4a6b" />
      </BarChart>

      <table>
        <thead>
          <tr>
            <th>Initiative</th>
            <th>Status</th>
            <th>Progress</th>
            <th>Team</th>
          </tr>
        </thead>
        <tbody>
          {items.map(item => (
            <tr key={item.name}>
              <td>{item.name}</td>
              <td>{item.status.replace('_', ' ')}</td>
              <td>{item.progress}%</td>
              <td>{item.team}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  )
}

export default ImplementationTracking
