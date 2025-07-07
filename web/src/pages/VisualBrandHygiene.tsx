import React, { useEffect, useState } from 'react'
import { PieChart, Pie, Tooltip, Cell } from 'recharts'

interface Counts {
  [key: string]: number
}

const colors = ['#3d4a6b', '#dc3545', '#8884d8']

function VisualBrandHygiene() {
  const [counts, setCounts] = useState<Counts>({})

  useEffect(() => {
    fetch('http://localhost:3000/api/brand-hygiene')
      .then((res) => res.json())
      .then((data) => setCounts(data))
      .catch(() => setCounts({}))
  }, [])

  const data = Object.entries(counts).map(([name, value]) => ({ name, value }))

  return (
    <div>
      <h2>Visual Brand Hygiene</h2>
      <PieChart width={400} height={300}>
        <Pie dataKey="value" data={data} cx="50%" cy="50%" outerRadius={100}>
          {data.map((entry, index) => (
            <Cell key={`cell-${index}`} fill={colors[index % colors.length]} />
          ))}
        </Pie>
        <Tooltip />
      </PieChart>
    </div>
  )
}

export default VisualBrandHygiene;
