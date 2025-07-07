import { Routes, Route, Link } from 'react-router-dom'
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
import StrategicRecommendations from './pages/StrategicRecommendations'
import ImplementationTracking from './pages/ImplementationTracking'
import AuditReports from './pages/AuditReports'
import './App.css'

function App() {
  return (
    <div className="main">
      <div className="block-container">
        <nav className="main-header">
          <h1>🎯 Brand Health Command Center</h1>
          <p>30-second strategic marketing decision engine for executives</p>
          <div className="nav-links">
            <Link to="/">🎯 Executive Dashboard</Link> |{' '}
            <Link to="/methodology">🔬 Methodology</Link> |{' '}
            <Link to="/persona-insights">👥 Persona Insights</Link> |{' '}
            <Link to="/content-matrix">📊 Content Matrix</Link> |{' '}
            <Link to="/opportunity-impact">💡 Opportunity Impact</Link> |{' '}
            <Link to="/success-library">🌟 Success Library</Link> |{' '}
            <Link to="/reports-export">📋 Reports Export</Link> |{' '}
            <Link to="/run-audit">🚀 Run Audit</Link> |{' '}
            <Link to="/social-media-analysis">🔍 Social Media Analysis</Link> |{' '}
            <Link to="/persona-viewer">👤 Persona Viewer</Link> |{' '}
            <Link to="/visual-brand-hygiene">🎨 Visual Brand Hygiene</Link> |{' '}
            <Link to="/strategic-recommendations">🎯 Strategic Recommendations</Link> |{' '}
            <Link to="/implementation-tracking">📈 Implementation Tracking</Link> |{' '}
            <Link to="/audit-reports">📄 Audit Reports</Link>
          </div>
        </nav>
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
