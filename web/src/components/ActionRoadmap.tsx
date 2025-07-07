import React from 'react'
import { PlotlyChart } from './'

export interface RoadmapItem {
  phase: string
  category: string
  count: number
  color: string
}

export interface ActionRoadmapProps {
  data: RoadmapItem[]
}

export function ActionRoadmap({ data }: ActionRoadmapProps) {
  return (
    <PlotlyChart
      data={[{
        x: data.map(d => d.phase),
        y: data.map(d => d.count),
        type: 'bar',
        marker: { color: data.map(d => d.color) },
        text: data.map(d => d.category)
      }]}
      layout={{ height: 400, xaxis: { title: 'Phase' }, yaxis: { title: 'Opportunities' } }}
    />
  )
}

export default ActionRoadmap
