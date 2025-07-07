import React from 'react'

export interface PageContainerProps {
  title: string
  children: React.ReactNode
}

export function PageContainer({ title, children }: PageContainerProps) {
  return (
    <div className="page-container">
      <h2>{title}</h2>
      {children}
    </div>
  )
}

export default PageContainer
