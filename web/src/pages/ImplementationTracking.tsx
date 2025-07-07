import React, { useEffect, useState } from 'react'
import { BarChart, Bar, XAxis, YAxis, Tooltip } from 'recharts'

interface Item {
  status: string
  progress: number
  team: string
  name: string
}

function ImplementationTracking() {
  const [items, setItems] = useState<Item[]>([])

  useEffect(() => {
    fetch('http://localhost:3000/api/implementation-tracking')
      .then((res) => res.json())
      .then((data: Item[]) => setItems(data))
      .catch(() => setItems([]))
  }, [])

  const totalItems = items.length
  const completed = items.filter(i => i.status === 'completed').length
  const inProgress = items.filter(i => i.status === 'in_progress').length
  const avgProgress = items.reduce((sum, i) => sum + i.progress, 0) / (totalItems || 1)
  const completionRate = totalItems ? (completed / totalItems) * 100 : 0


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
