import { render, screen } from '@testing-library/react'
import { PageContainer } from './PageContainer'

describe('PageContainer', () => {
  it('renders children', () => {
    render(
      <PageContainer title="Page Title">
        <p>Content</p>
      </PageContainer>
    )
    expect(screen.getByText('Content')).toBeInTheDocument()
  })
})
