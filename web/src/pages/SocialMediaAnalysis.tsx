import React, { useEffect, useState } from 'react'
import { BarChart, Bar, XAxis, YAxis, Tooltip } from 'recharts'

interface Row {
  Platform: string
  Region: string
  Followers: string
}

function parseFollowers(value: string) {
  return parseInt(value.replace(/,/g, ''), 10)
}

function SocialMediaAnalysis() {
  const [rows, setRows] = useState<Row[]>([])

  useEffect(() => {
    fetch('http://localhost:3000/api/social-media')
      .then((res) => res.json())
      .then((data) => setRows(data.data || []))
      .catch(() => setRows([]))
  }, [])

  const chartData = rows.map((r) => ({
    name: `${r.Platform} ${r.Region}`,
    followers: parseFollowers(r.Followers)
  }))

  return (
    <div>
      <h2>Social Media Analysis</h2>
      <BarChart width={600} height={300} data={chartData}>
        <XAxis dataKey="name" hide={true} />
        <YAxis />
        <Tooltip />
        <Bar dataKey="followers" fill="#dc3545" />
      </BarChart>
    </div>
  )
}

export default SocialMediaAnalysis;
