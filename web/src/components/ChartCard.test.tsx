import { render, screen } from '@testing-library/react'
import { ChartCard } from './ChartCard'

describe('ChartCard', () => {
  it('shows title and children', () => {
    render(
      <ChartCard title="My Chart">
        <span>chart here</span>
      </ChartCard>
    )
    expect(screen.getByText('My Chart')).toBeInTheDocument()
    expect(screen.getByText('chart here')).toBeInTheDocument()
  })
})
