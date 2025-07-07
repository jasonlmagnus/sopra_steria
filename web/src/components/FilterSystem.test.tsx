import { render, screen, fireEvent } from '@testing-library/react'
import { FilterProvider } from '../context/FilterContext'
import FilterSystem from './FilterSystem'

function setup() {
  render(
    <FilterProvider>
      <FilterSystem personaOptions={['P1']} tierOptions={['T1']} />
    </FilterProvider>
  )
}

describe('FilterSystem', () => {
  it('persists selections to sessionStorage', () => {
    setup()
    const selects = screen.getAllByRole('combobox')
    fireEvent.change(selects[0], { target: { value: 'P1' } })
    expect(sessionStorage.getItem('filters')).toContain('P1')
  })
})
