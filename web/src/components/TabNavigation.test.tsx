import { render, screen, fireEvent } from '@testing-library/react'
import TabNavigation from './TabNavigation'

describe('TabNavigation', () => {
  it('switches tabs', () => {
    render(
      <TabNavigation
        tabs={[
          { label: 'A', content: <span>A content</span> },
          { label: 'B', content: <span>B content</span> }
        ]}
      />
    )
    expect(screen.getByText('A content')).toBeInTheDocument()
    fireEvent.click(screen.getByText('B'))
    expect(screen.getByText('B content')).toBeInTheDocument()
  })
})
