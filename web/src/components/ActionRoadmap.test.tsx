import { render, screen } from '@testing-library/react'
import ActionRoadmap from './ActionRoadmap'

vi.mock('./', () => ({ PlotlyChart: () => <div>roadmap</div> }))

describe('ActionRoadmap', () => {
  it('renders roadmap chart', () => {
    render(<ActionRoadmap data={[{ phase: 'P1', category: 'A', count: 1, color: '#fff' }]} />)
    expect(screen.getByText('roadmap')).toBeInTheDocument()
  })
})
