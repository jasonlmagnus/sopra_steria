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

export function StandardCard({ 
  title, 
  value, 
  label, 
  status = 'default', 
  variant = 'metric',
  children, 
  className = '',
  onClick 
}: StandardCardProps) {
  const getStatusClass = () => {
    switch (status) {
      case 'excellent': return 'status-excellent'
      case 'good': return 'status-good'
      case 'warning': return 'status-warning'
      case 'critical': return 'status-critical'
      default: return ''
    }
  }

  const cardClass = `metric-card ${variant === 'persona' ? 'persona-card' : ''} ${getStatusClass()} ${className}`

  return (
    <div className={cardClass} onClick={onClick} style={{ cursor: onClick ? 'pointer' : 'default' }}>
      {title && <h4 className="card-title">{title}</h4>}
      
      {value && (
        <div className="metric-display">
          <div className="metric-value">{value}</div>
          {label && <div className="metric-label">{label}</div>}
        </div>
      )}
      
      {children}
    </div>
  )
}

export default StandardCard 