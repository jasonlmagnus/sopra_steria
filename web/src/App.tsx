import { Routes, Route, Link, useLocation } from 'react-router-dom'
import { useState } from 'react'
import ExecutiveDashboard from './pages/ExecutiveDashboard'
import Methodology from './pages/Methodology'
import PersonaInsights from './pages/PersonaInsights'
import ContentMatrix from './pages/ContentMatrix'
import OpportunityImpact from './pages/OpportunityImpact'
import SuccessLibrary from './pages/SuccessLibrary'
import ReportsExport from './pages/ReportsExport'
import RunAudit from './pages/RunAudit'
import SocialMediaAnalysis from './pages/SocialMediaAnalysis'
import PersonaViewer from './pages/PersonaViewer'
import VisualBrandHygiene from './pages/VisualBrandHygiene'
import StrategicRecommendations from './pages/Recommendations'
import ImplementationTracking from './pages/ImplementationTracking'
import AuditReports from './pages/AuditReports'
import './App.css'

function App() {
  const [sidebarExpanded, setSidebarExpanded] = useState(true)
  const location = useLocation()

  const navigationItems = [
    { path: '/', label: 'Executive Dashboard', icon: '🎯' },
    { path: '/methodology', label: 'Methodology', icon: '🔬' },
    { path: '/persona-insights', label: 'Persona Insights', icon: '👥' },
    { path: '/content-matrix', label: 'Content Matrix', icon: '📊' },
    { path: '/opportunity-impact', label: 'Opportunity Impact', icon: '💡' },
    { path: '/success-library', label: 'Success Library', icon: '🌟' },
    { path: '/reports-export', label: 'Reports Export', icon: '📋' },
    { path: '/run-audit', label: 'Run Audit', icon: '🚀' },
    { path: '/social-media-analysis', label: 'Social Media Analysis', icon: '🔍' },
    { path: '/persona-viewer', label: 'Persona Viewer', icon: '👤' },
    { path: '/visual-brand-hygiene', label: 'Visual Brand Hygiene', icon: '🎨' },
    { path: '/strategic-recommendations', label: 'Strategic Recommendations', icon: '🎯' },
    { path: '/implementation-tracking', label: 'Implementation Tracking', icon: '📈' },
    { path: '/audit-reports', label: 'Audit Reports', icon: '📄' }
  ]

  return (
    <div className="app-container">
      {/* Sidebar */}
      <div className={`sidebar ${sidebarExpanded ? 'expanded' : 'collapsed'}`}>
        {/* Sidebar Header */}
        <div className="sidebar-header">
          <div className="sidebar-brand">
            <h1>🎯 Brand Health Command Center</h1>
            <p>30-second strategic marketing decision engine</p>
          </div>
          <button 
            className="sidebar-toggle"
            onClick={() => setSidebarExpanded(!sidebarExpanded)}
          >
            {sidebarExpanded ? '◀' : '▶'}
          </button>
        </div>

        {/* Navigation Links */}
        <nav className="sidebar-nav">
          {navigationItems.map((item) => (
            <Link
              key={item.path}
              to={item.path}
              className={`sidebar-link ${location.pathname === item.path ? 'active' : ''}`}
            >
              <span className="sidebar-icon">{item.icon}</span>
              {sidebarExpanded && <span className="sidebar-label">{item.label}</span>}
            </Link>
          ))}
        </nav>

        {/* Sidebar Footer */}
        {sidebarExpanded && (
          <div className="sidebar-footer">
            <div className="sidebar-info">
              <h4>📊 Data Overview</h4>
              <div className="sidebar-stats">
                <div className="stat-item">
                  <span className="stat-value">247</span>
                  <span className="stat-label">Total Pages</span>
                </div>
                <div className="stat-item">
                  <span className="stat-value">1,235</span>
                  <span className="stat-label">Total Records</span>
                </div>
                <div className="stat-item">
                  <span className="stat-value">6.8/10</span>
                  <span className="stat-label">Avg Score</span>
                </div>
              </div>
            </div>
          </div>
        )}
      </div>

      {/* Main Content */}
      <div className={`main-content ${sidebarExpanded ? 'sidebar-expanded' : 'sidebar-collapsed'}`}>
        <Routes>
          <Route path="/" element={<ExecutiveDashboard />} />
          <Route path="/methodology" element={<Methodology />} />
          <Route path="/persona-insights" element={<PersonaInsights />} />
          <Route path="/content-matrix" element={<ContentMatrix />} />
          <Route path="/opportunity-impact" element={<OpportunityImpact />} />
          <Route path="/success-library" element={<SuccessLibrary />} />
          <Route path="/reports-export" element={<ReportsExport />} />
          <Route path="/run-audit" element={<RunAudit />} />
          <Route path="/social-media-analysis" element={<SocialMediaAnalysis />} />
          <Route path="/persona-viewer" element={<PersonaViewer />} />
          <Route path="/visual-brand-hygiene" element={<VisualBrandHygiene />} />
          <Route path="/strategic-recommendations" element={<StrategicRecommendations />} />
          <Route path="/implementation-tracking" element={<ImplementationTracking />} />
          <Route path="/audit-reports" element={<AuditReports />} />
        </Routes>
      </div>
    </div>
  )
}

export default App
