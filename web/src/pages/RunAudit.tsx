import React, { useState } from 'react'

function RunAudit() {
  const [url, setUrl] = useState('')
  const [status, setStatus] = useState('')

  const handleRun = async () => {
    setStatus('Running...')
    try {
      const res = await fetch('http://localhost:3000/api/run-audit', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ url })
      })
      const data = await res.json()
      setStatus(data.message)
    } catch {
      setStatus('Error starting audit')
    }
  }

  return (
    <div>
      <h2>Run Audit</h2>
      <input
        value={url}
        onChange={(e) => setUrl(e.target.value)}
        placeholder="Enter URL"
      />
      <button onClick={handleRun}>Run</button>
      {status && <p>{status}</p>}
    </div>
  );
}

export default RunAudit;
