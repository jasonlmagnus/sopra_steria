import { PlotlyChart } from './PlotlyChart'

export interface HeatmapChartProps {
  x: string[]
  y: string[]
  z: number[][]
  title?: string
}

export function HeatmapChart({ x, y, z, title }: HeatmapChartProps) {
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
      layout={{ 
        title,
        height: 300, 
        xaxis: { title: 'Persona' }, 
        yaxis: { title: 'Tier' } 
      }}
    />
  )
}

export default HeatmapChart 