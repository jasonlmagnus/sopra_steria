import { render, screen } from '@testing-library/react'
import MetricsCard from './MetricsCard'

describe('MetricsCard', () => {
  it('applies variant based on multiplier', () => {
    const { container } = render(<MetricsCard label="Issues" value={8} multiplier={2} />)
    expect(container.querySelector('.score-card--danger')).toBeInTheDocument()
  })
})
