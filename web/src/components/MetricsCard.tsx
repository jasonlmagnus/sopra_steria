import React from 'react'
import ScoreCard, { ScoreCardProps } from './ScoreCard'

export interface MetricsCardProps extends Omit<ScoreCardProps, 'variant'> {
  multiplier?: number
}

export function MetricsCard({ label, value, progress, multiplier = 1 }: MetricsCardProps) {
  const num = typeof value === 'number' ? value : parseFloat(String(value))
  const scaled = num * multiplier
  const variant = scaled >= 10 ? 'danger' : scaled >= 5 ? 'warning' : 'success'
  return <ScoreCard label={label} value={value} progress={progress} variant={variant} />
}

export default MetricsCard
