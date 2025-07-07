import React from 'react'
import Plot from 'react-plotly.js'

export interface PlotlyChartProps {
  data: Partial<any>[]
  layout?: Partial<any>
  config?: Partial<any>
  onSelected?: (event: any) => void
}

export function PlotlyChart({ data, layout, config, onSelected }: PlotlyChartProps) {
  return (
    <Plot data={data} layout={layout} config={config} onSelected={onSelected} style={{ width: '100%' }} />
  )
}

export default PlotlyChart
