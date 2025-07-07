import { useState, useEffect } from 'react'
import { Routes, Route, Link } from 'react-router-dom'
import DatasetList from './pages/DatasetList'
import DatasetDetail from './pages/DatasetDetail'
import PagesList from './pages/PagesList'
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
        <Link to="/datasets">Datasets</Link> |{' '}
        <Link to="/pages">Pages</Link>
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
        <Route path="/datasets" element={<DatasetList />} />
        <Route path="/datasets/:name" element={<DatasetDetail />} />
        <Route path="/pages" element={<PagesList />} />
      </Routes>
    </>
  )
}

export default App
