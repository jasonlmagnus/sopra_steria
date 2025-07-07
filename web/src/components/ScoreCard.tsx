import React from 'react'

export interface ScoreCardProps {
  label: string
  value: React.ReactNode
  /** Optional progress percentage for a progress indicator */
  progress?: number
  /**
   * Optional visual style variant. Used for performance based
   * colour coding similar to the Streamlit dashboards.
   */
  variant?: 'default' | 'success' | 'warning' | 'danger'
}

export function ScoreCard({ label, value, progress, variant = 'default' }: ScoreCardProps) {
  return (
    <div className={`score-card score-card--${variant}`}>
      <strong>{value}</strong>
      {typeof progress === 'number' && (
        <progress value={progress} max={100} data-testid="progress" />
      )}
      <div>{label}</div>
    </div>
  )
}

export default ScoreCard
