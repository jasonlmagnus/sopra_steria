import { render, screen, fireEvent } from '@testing-library/react'
import FilterControls from './FilterControls'
import { FilterProvider } from '../context/FilterContext'

describe('FilterControls', () => {
  it('changes selected values', () => {
    render(
      <FilterProvider>
        <FilterControls personas={["P1"]} tiers={["T1"]} />
      </FilterProvider>
    )
    fireEvent.change(screen.getByDisplayValue('All Personas'), { target: { value: 'P1' } })
    expect((screen.getByDisplayValue('P1') as HTMLSelectElement).value).toBe('P1')
  })
})
