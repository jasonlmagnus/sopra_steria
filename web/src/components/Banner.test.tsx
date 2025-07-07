import { render, screen } from '@testing-library/react'
import Banner from './Banner'

describe('Banner', () => {
  it('renders message', () => {
    render(<Banner message="Hello" />)
    expect(screen.getByText('Hello')).toBeInTheDocument()
  })
})
