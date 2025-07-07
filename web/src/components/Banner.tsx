import React from 'react'

export interface BannerProps {
  message: string
  variant?: 'info' | 'success' | 'warning' | 'danger'
}

export default function Banner({ message, variant = 'info' }: BannerProps) {
  return <div className={`banner banner--${variant}`}>{message}</div>
}
