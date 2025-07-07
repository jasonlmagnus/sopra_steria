import { render, screen, fireEvent } from '@testing-library/react'
import ExpandableCard from './ExpandableCard'

describe('ExpandableCard', () => {
  it('expands and collapses content', () => {
    render(
      <ExpandableCard title="Test">
        <span>inner</span>
      </ExpandableCard>
    )
    expect(screen.queryByText('inner')).not.toBeInTheDocument()
    fireEvent.click(screen.getByText(/Test/))
    expect(screen.getByText('inner')).toBeInTheDocument()
  })
})
