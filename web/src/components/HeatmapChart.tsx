import React from 'react'
import { PlotlyChart } from './'

export interface HeatmapChartProps {
  x: string[]
  y: string[]
  z: number[][]
}

export function HeatmapChart({ x, y, z }: HeatmapChartProps) {
  return (
    <PlotlyChart
      data={[{
        x,
        y,
        z,
        type: 'heatmap',
        colorscale: 'Blues',
        hovertemplate: 'Persona: %{x}<br>Tier: %{y}<br>Score: %{z}<extra></extra>'
      }]}
      layout={{ height: 300, xaxis: { title: 'Persona' }, yaxis: { title: 'Tier' } }}
    />
  )
}

export default HeatmapChart
