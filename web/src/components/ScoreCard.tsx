import React from 'react'

export interface ScoreCardProps {
  label: string
  value: React.ReactNode
}

export function ScoreCard({ label, value }: ScoreCardProps) {
  return (
    <div className="score-card">
      <strong>{value}</strong>
      <div>{label}</div>
    </div>
  )
}

export default ScoreCard
