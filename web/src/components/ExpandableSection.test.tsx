import { render, screen, fireEvent } from '@testing-library/react'
import ExpandableSection from './ExpandableSection'

describe('ExpandableSection', () => {
  it('toggles content visibility', () => {
    render(
      <ExpandableSection title="Test">
        <span>content</span>
      </ExpandableSection>
    )
    expect(screen.queryByText('content')).not.toBeInTheDocument()
    fireEvent.click(screen.getByText(/Test/))
    expect(screen.getByText('content')).toBeInTheDocument()
  })
})
