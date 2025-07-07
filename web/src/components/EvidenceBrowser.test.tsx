import { render, screen, fireEvent } from '@testing-library/react'
import EvidenceBrowser from './EvidenceBrowser'

describe('EvidenceBrowser', () => {
  const items = [
    { title: 'A', url: 'http://a.com', score: 1 },
    { title: 'B', url: 'http://b.com', score: 2 }
  ]
  it('filters items by search text', () => {
    render(<EvidenceBrowser items={items} />)
    fireEvent.change(screen.getByPlaceholderText('Search evidence...'), { target: { value: 'B' } })
    expect(screen.queryByText('A')).toBeNull()
    expect(screen.getByText('B')).toBeInTheDocument()
  })
})
