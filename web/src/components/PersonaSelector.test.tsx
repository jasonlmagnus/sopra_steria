import { render, screen, fireEvent } from '@testing-library/react'
import PersonaSelector from './PersonaSelector'

describe('PersonaSelector', () => {
  const personas = ['CEO', 'CTO']
  it('shows mode indicator', () => {
    const onChange = vi.fn()
    render(<PersonaSelector personas={personas} selected="" onChange={onChange} />)
    expect(screen.getByTestId('mode-indicator').textContent).toMatch('Comparison')
    fireEvent.change(screen.getByRole('combobox'), { target: { value: 'CEO' } })
    expect(onChange).toHaveBeenCalledWith('CEO')
  })
})
