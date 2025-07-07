import { render, screen } from '@testing-library/react'
import { PageContainer } from './PageContainer'

describe('PageContainer', () => {
  it('renders title and children', () => {
    render(
      <PageContainer title="Page Title">
        <p>Content</p>
      </PageContainer>
    )
    expect(screen.getByText('Page Title')).toBeInTheDocument()
    expect(screen.getByText('Content')).toBeInTheDocument()
  })
})
