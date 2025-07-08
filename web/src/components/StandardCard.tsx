import React from 'react'

interface StandardCardProps {
  title?: string
  value?: string | number
  label?: string
  status?: 'excellent' | 'good' | 'warning' | 'critical' | 'default'
  variant?: 'metric' | 'content' | 'persona' | 'success'
  children?: React.ReactNode
  className?: string
  onClick?: () => void
}

export default function StandardCard({ 
  title, 
  value, 
  label, 
  status = 'default', 
  variant = 'metric',
  children, 
  className = '',
  onClick 
}: StandardCardProps) {
  const getCardClasses = () => {
    const baseClasses = ['card']
    
    // Add variant class
    if (variant !== 'metric') {
      baseClasses.push(`card--${variant}`)
    } else {
      baseClasses.push('card--metric')
    }
    
    // Add status class
    if (status !== 'default') {
      baseClasses.push(`card--${status}`)
    }
    
    // Add clickable class
    if (onClick) {
      baseClasses.push('card--clickable')
    }
    
    // Add custom classes
    if (className) {
      baseClasses.push(className)
    }
    
    return baseClasses.join(' ')
  }

  return (
    <div className={getCardClasses()} onClick={onClick}>
      {title && <h3 className="card__title">{title}</h3>}
      
      {children || (
        <div className="card__metric">
          {value && <div className="card__metric-value">{value}</div>}
          {label && <div className="card__metric-label">{label}</div>}
        </div>
      )}
    </div>
  )
} 