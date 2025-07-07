import { render, screen } from '@testing-library/react'
import { ScoreCard } from './ScoreCard'

describe('ScoreCard', () => {
  it('renders label and value', () => {
    render(<ScoreCard label="Test" value={42} />)
    expect(screen.getByText('Test')).toBeInTheDocument()
    expect(screen.getByText('42')).toBeInTheDocument()
  })

  it('shows progress when provided', () => {
    render(<ScoreCard label="Progress" value="50%" progress={50} />)
    const progress = screen.getByTestId('progress') as HTMLProgressElement
    expect(progress).toBeInTheDocument()
    expect(progress.value).toBe(50)
  })
})
