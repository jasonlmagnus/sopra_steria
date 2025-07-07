import React, { useState } from 'react';

function RunAudit() {
  const [url, setUrl] = useState('');
  const [status, setStatus] = useState('');

  const handleRun = () => {
    setStatus(`Pretending to run audit for ${url}`);
  };

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
