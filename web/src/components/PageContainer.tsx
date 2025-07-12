import React from 'react'
import { PageHeader } from './PageHeader'

export interface PageContainerProps {
  title: string
  description?: string
  children: React.ReactNode
}

export function PageContainer({ title, description, children }: PageContainerProps) {
  return (
    <div className="page-container">
      <PageHeader title={title} description={description} />
      <div className="page-container__content">
        {children}
      </div>
    </div>
  )
}

export default PageContainer
