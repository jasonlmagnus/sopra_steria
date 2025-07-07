import React from 'react'

export interface ScoreCardProps {
  label: string
  value: React.ReactNode
  /**
   * Optional visual style variant. Used for performance based
   * colour coding similar to the Streamlit dashboards.
   */
  variant?: 'default' | 'success' | 'warning' | 'danger'
}

export function ScoreCard({ label, value, variant = 'default' }: ScoreCardProps) {
  return (
    <div className={`score-card score-card--${variant}`}>
      <strong>{value}</strong>
      <div>{label}</div>
    </div>
  )
}

export default ScoreCard
