import { render, screen, waitFor } from '@testing-library/react'
import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import GapAnalysis from './GapAnalysis'
import { vi } from 'vitest'

const client = new QueryClient()

global.fetch = vi.fn(() =>
  Promise.resolve({
    ok: true,
    json: () => Promise.resolve({ items: ['gap1', 'gap2'] })
  })
) as any

describe('GapAnalysis', () => {
  it('displays gap items from API', async () => {
    render(
      <QueryClientProvider client={client}>
        <GapAnalysis />
      </QueryClientProvider>
    )
    await waitFor(() => expect(screen.getByText('gap1')).toBeInTheDocument())
    expect(screen.getByText('gap2')).toBeInTheDocument()
  })
})
