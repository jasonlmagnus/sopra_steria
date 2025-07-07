import { render, screen } from '@testing-library/react'
import { FilterBar } from './FilterBar'

describe('FilterBar', () => {
  it('renders children', () => {
    render(
      <FilterBar>
        <button>child</button>
      </FilterBar>
    )
    expect(screen.getByText('child')).toBeInTheDocument()
  })
})
