import { useState, useEffect } from 'react'
import { Routes, Route, Link } from 'react-router-dom'
import DatasetList from './pages/DatasetList'
import DatasetDetail from './pages/DatasetDetail'
import PagesList from './pages/PagesList'
import Recommendations from './pages/Recommendations'
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
import ImplementationTracking from './pages/ImplementationTracking'
import AuditReports from './pages/AuditReports'
import ExecutiveDashboard from './pages/ExecutiveDashboard'
import reactLogo from './assets/react.svg'
import viteLogo from '/vite.svg'
import './App.css'

function App() {
  const [count, setCount] = useState(0)
  const [apiMessage, setApiMessage] = useState('')

  useEffect(() => {
    fetch('http://localhost:3000/api/hello')
      .then((res) => res.json())
      .then((data) => setApiMessage(data.message))
      .catch(() => setApiMessage('Error fetching API'))
  }, [])

  return (
    <>
      <nav>
        <Link to="/">Home</Link> |{' '}
        <Link to="/executive-dashboard">Executive Dashboard</Link> |{' '}
        <Link to="/datasets">Datasets</Link> |{' '}
        <Link to="/pages">Pages</Link> |{' '}
        <Link to="/recommendations">Recommendations</Link> |{' '}
        <Link to="/methodology">Methodology</Link> |{' '}
        <Link to="/persona-insights">Persona Insights</Link> |{' '}
        <Link to="/content-matrix">Content Matrix</Link> |{' '}
        <Link to="/opportunity-impact">Opportunity Impact</Link> |{' '}
        <Link to="/success-library">Success Library</Link> |{' '}
        <Link to="/reports-export">Reports Export</Link> |{' '}
        <Link to="/run-audit">Run Audit</Link> |{' '}
        <Link to="/social-media-analysis">Social Media Analysis</Link> |{' '}
        <Link to="/persona-viewer">Persona Viewer</Link> |{' '}
        <Link to="/visual-brand-hygiene">Visual Brand Hygiene</Link> |{' '}
        <Link to="/implementation-tracking">Implementation Tracking</Link> |{' '}
        <Link to="/audit-reports">Audit Reports</Link>
      </nav>
      <Routes>
        <Route
          path="/"
          element={(
            <div>
              <div>
                <a href="https://vite.dev" target="_blank">
                  <img src={viteLogo} className="logo" alt="Vite logo" />
                </a>
                <a href="https://react.dev" target="_blank">
                  <img src={reactLogo} className="logo react" alt="React logo" />
                </a>
              </div>
              <h1>Vite + React</h1>
              <div className="card">
                <button onClick={() => setCount((count) => count + 1)}>
                  count is {count}
                </button>
                <p>
                  Edit <code>src/App.tsx</code> and save to test HMR
                </p>
              </div>
              <p>{apiMessage}</p>
              <p className="read-the-docs">
                Click on the Vite and React logos to learn more
              </p>
            </div>
          )}
        />
        <Route path="/executive-dashboard" element={<ExecutiveDashboard />} />
        <Route path="/datasets" element={<DatasetList />} />
        <Route path="/datasets/:name" element={<DatasetDetail />} />
        <Route path="/pages" element={<PagesList />} />
        <Route path="/recommendations" element={<Recommendations />} />
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
        <Route path="/implementation-tracking" element={<ImplementationTracking />} />
        <Route path="/audit-reports" element={<AuditReports />} />
      </Routes>
    </>
  )
}

export default App
