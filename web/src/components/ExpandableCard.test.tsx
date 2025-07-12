import { render, screen, fireEvent } from '@testing-library/react'
import ExpandableCard from './ExpandableCard'

describe('ExpandableCard', () => {
  it('expands and collapses content', () => {
    render(
      <ExpandableCard title="Test">
        <span>inner</span>
      </ExpandableCard>
    )
    // Content should be in the document but not visible
    expect(screen.getByText('inner')).toBeInTheDocument()
    
    // Click to expand
    fireEvent.click(screen.getByText(/Test/))
    expect(screen.getByText('inner')).toBeInTheDocument()

    // Click to collapse
    fireEvent.click(screen.getByText(/Test/))
    expect(screen.getByText('inner')).toBeInTheDocument()
  })
})
