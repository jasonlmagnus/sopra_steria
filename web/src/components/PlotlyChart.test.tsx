import { render, screen } from '@testing-library/react'
import { PlotlyChart } from './PlotlyChart'

vi.mock('react-plotly.js', () => ({ default: () => <div>plot</div> }))

describe('PlotlyChart', () => {
  it('renders without crashing', () => {
    render(<PlotlyChart data={[]} />)
    expect(screen.getByText('plot')).toBeInTheDocument()
  })
})
