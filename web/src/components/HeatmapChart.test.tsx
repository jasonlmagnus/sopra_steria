import { render, screen } from '@testing-library/react'
import HeatmapChart from './HeatmapChart'

vi.mock('./', () => ({ PlotlyChart: () => <div>heatmap</div> }))

describe('HeatmapChart', () => {
  it('renders heatmap chart', () => {
    render(<HeatmapChart x={['a']} y={['b']} z={[[1]]} />)
    expect(screen.getByText('heatmap')).toBeInTheDocument()
  })
})
