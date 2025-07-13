import { Routes, Route, Link, useLocation } from 'react-router-dom'
import { useState } from 'react'
import ExecutiveDashboard from './pages/ExecutiveDashboard'
import ExecutiveDashboard_AntDesign_Real from './pages/ExecutiveDashboard_AntDesign_Real'
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
import StrategicRecommendations from './pages/StrategicRecommendations'
import DatasetDetail from './pages/DatasetDetail'

import AuditReports from './pages/AuditReports'
import './styles/dashboard.css'

function App() {
  const [sidebarExpanded, setSidebarExpanded] = useState(true)
  const location = useLocation()

  const navigationItems = [
    { path: '/', label: 'Executive Dashboard', icon: '��' },
    { path: '/antd-real', label: 'Ant Design Real Data', icon: '🎯🐜' },
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
    { path: '/audit-reports', label: 'Audit Reports', icon: '📄' }
  ]

  return (
    <div className="app">
      {/* Sidebar */}
      <div className={`sidebar ${sidebarExpanded ? '' : 'sidebar--collapsed'}`}>
        {/* Sidebar Header */}
        <div className="sidebar__header">
          <Link to="/" className="sidebar__logo">
            <span className="sidebar__logo-icon">🎯</span>
            <span className="sidebar__logo-text">Brand Health Command Center</span>
          </Link>
          <button 
            className="sidebar__toggle"
            onClick={() => setSidebarExpanded(!sidebarExpanded)}
          >
            {sidebarExpanded ? '◀' : '▶'}
          </button>
        </div>

        {/* Navigation Links */}
        <nav className="sidebar__nav">
          {navigationItems.map((item) => (
            <Link
              key={item.path}
              to={item.path}
              className={`sidebar__link ${location.pathname === item.path ? 'sidebar__link--active' : ''}`}
            >
              <span className="sidebar__link-icon">{item.icon}</span>
              <span className="sidebar__link-label">{item.label}</span>
            </Link>
          ))}
        </nav>
      </div>

      {/* Main Content */}
      <div className={`main-content ${sidebarExpanded ? '' : 'main-content--sidebar-collapsed'}`}>
        <Routes>
          <Route path="/" element={<ExecutiveDashboard />} />
          <Route path="/antd-real" element={<ExecutiveDashboard_AntDesign_Real />} />
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
          <Route path="/datasets/:name" element={<DatasetDetail />} />
          <Route path="/audit-reports" element={<AuditReports />} />
        </Routes>
      </div>
    </div>
  )
}

export default App
