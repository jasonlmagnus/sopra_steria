import React from 'react'

export interface PageContainerProps {
  /** Optional page title. Currently unused but kept for backwards compatibility */
  title?: string
  children: React.ReactNode
}

export function PageContainer({ children }: PageContainerProps) {
  return <div className="page-container">{children}</div>
}

export default PageContainer
