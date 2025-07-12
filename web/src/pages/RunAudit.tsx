import { useState, useEffect, useRef, useCallback } from 'react';
import { Banner, PageContainer, StandardCard } from '../components';
import '../styles/pages/RunAudit.css';

interface AuditState {
  sessionId: string | null;
  isRunning: boolean;
  isProcessing: boolean;
  auditComplete: boolean;
  currentProgress: number;
  statusText: string;
  logLines: string[];
  personaName: string;
  completedPersonaName: string;
  totalUrls: number;
  startTime: Date | null;
}

interface ProcessingState {
  status: 'not_started' | 'running' | 'completed' | 'failed';
  progress: number;
  message: string;
}

const RunAudit: React.FC = () => {
  const [personaFile, setPersonaFile] = useState<File | null>(null);
  const [personaContent, setPersonaContent] = useState<string>('');
  const [urlsText, setUrlsText] = useState<string>('');
  const [selectedModel, setSelectedModel] = useState<'openai' | 'anthropic'>('openai');
  const [activeTab, setActiveTab] = useState<'paste' | 'upload'>('paste');
  const [isPolling, setIsPolling] = useState(false);
  
  const [auditState, setAuditState] = useState<AuditState>({
    sessionId: null,
    isRunning: false,
    isProcessing: false,
    auditComplete: false,
    currentProgress: 0,
    statusText: '',
    logLines: [],
    personaName: '',
    completedPersonaName: '',
    totalUrls: 0,
    startTime: null
  });

  const [processingState, setProcessingState] = useState<ProcessingState>({
    status: 'not_started',
    progress: 0,
    message: ''
  });

  const logContainerRef = useRef<HTMLDivElement>(null);
  const pollingIntervalRef = useRef<NodeJS.Timeout | null>(null);

  // Extract persona name from content
  const extractPersonaName = (content: string, filename?: string): string => {
    const lines = content.trim().split('\n');
    if (lines.length > 0) {
      const firstLine = lines[0].trim();
      if (firstLine.startsWith('Persona Brief:')) {
        return firstLine.replace('Persona Brief:', '').trim();
      }
      if (firstLine && !firstLine.startsWith('#')) {
        return firstLine;
      }
    }
    
    const match = content.match(/P\d+/) || (filename && filename.match(/P\d+/));
    return match ? match[0] : 'default_persona';
  };

  // Handle persona file upload with enhanced UX
  const handlePersonaFileUpload = (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (file) {
      if (!file.name.endsWith('.md')) {
        alert('Please upload a .md (Markdown) file');
        return;
      }
      
      setPersonaFile(file);
      const reader = new FileReader();
      reader.onload = (e) => {
        const content = e.target?.result as string;
        setPersonaContent(content);
      };
      reader.readAsText(file);
    }
  };

  // Handle URL file upload with validation
  const handleUrlFileUpload = (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (file) {
      const reader = new FileReader();
      reader.onload = (e) => {
        const content = e.target?.result as string;
        const urlRegex = /https?:\/\/[^\s|)]+/g;
        const urls = content.match(urlRegex) || [];
        if (urls.length > 0) {
          setUrlsText(urls.join('\n'));
        } else {
          alert('No valid URLs found in the file');
        }
      };
      reader.readAsText(file);
    }
  };

  // Validate URLs with detailed feedback
  const validateUrls = (text: string) => {
    const urls = text.split('\n').filter(url => url.trim());
    const validUrls = urls.filter(url => url.startsWith('http://') || url.startsWith('https://'));
    const invalidUrls = urls.filter(url => !url.startsWith('http://') && !url.startsWith('https://'));
    
    return {
      total: urls.length,
      valid: validUrls.length,
      invalid: invalidUrls.length,
      validUrls,
      invalidUrls
    };
  };

  // Poll for audit status
  const pollAuditStatus = useCallback(async (sessionId: string) => {
    try {
        const response = await fetch(`http://localhost:3000/api/audit/status/${sessionId}`);
      if (response.ok) {
        const data = await response.json();
        
        setAuditState(prev => ({
          ...prev,
          currentProgress: data.progress,
          statusText: data.message,
          logLines: data.logs || [],
          isRunning: data.status === 'running' || data.status === 'initializing',
          auditComplete: data.status === 'completed',
          completedPersonaName: data.completed_persona || prev.completedPersonaName
        }));

        // Stop polling if audit is complete or failed
        if (data.status === 'completed' || data.status === 'failed' || data.status === 'stopped') {
          setIsPolling(false);
          if (pollingIntervalRef.current) {
            clearInterval(pollingIntervalRef.current);
            pollingIntervalRef.current = null;
          }
        }
      }
    } catch (error) {
      console.error('Error polling audit status:', error);
    }
  }, []);

  // Poll for processing status
  const pollProcessingStatus = useCallback(async (sessionId: string) => {
    try {
        const response = await fetch(`http://localhost:8000/api/audit/processing-status/${sessionId}`);
      if (response.ok) {
        const data = await response.json();
        
        setProcessingState({
          status: data.processing_status,
          progress: data.processing_progress,
          message: data.processing_message
        });

        setAuditState(prev => ({
          ...prev,
          isProcessing: data.processing_status === 'running'
        }));

        // Stop polling if processing is complete
        if (data.processing_status === 'completed' || data.processing_status === 'failed') {
          setIsPolling(false);
          if (pollingIntervalRef.current) {
            clearInterval(pollingIntervalRef.current);
            pollingIntervalRef.current = null;
          }
        }
      }
    } catch (error) {
      console.error('Error polling processing status:', error);
    }
  }, []);

  // Start polling
  useEffect(() => {
    if (isPolling && auditState.sessionId) {
      pollingIntervalRef.current = setInterval(() => {
        if (auditState.isProcessing) {
          pollProcessingStatus(auditState.sessionId!);
        } else {
          pollAuditStatus(auditState.sessionId!);
        }
      }, 1000);

      return () => {
        if (pollingIntervalRef.current) {
          clearInterval(pollingIntervalRef.current);
          pollingIntervalRef.current = null;
        }
      };
    }
  }, [isPolling, auditState.sessionId, auditState.isProcessing, pollAuditStatus, pollProcessingStatus]);

  // Run audit with real API integration
  const runAudit = async () => {
    if (!personaFile || !urlsText.trim()) return;

    const personaName = extractPersonaName(personaContent, personaFile.name);
    const urlValidation = validateUrls(urlsText);
    
    if (urlValidation.valid === 0) {
      alert('No valid URLs found. Please provide at least one valid HTTP/HTTPS URL.');
      return;
    }

    try {
      const response = await fetch('http://localhost:3000/api/audit/run', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          persona_content: personaContent,
          persona_filename: personaFile.name,
          urls: urlValidation.validUrls,
          model_provider: selectedModel
        })
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || 'Failed to start audit');
      }

      const data = await response.json();
      
      setAuditState(prev => ({
        ...prev,
        sessionId: data.session_id,
        isRunning: true,
        auditComplete: false,
        currentProgress: 0,
        statusText: `Starting audit for ${personaName} using ${selectedModel.toUpperCase()}...`,
        logLines: [],
        personaName,
        totalUrls: data.total_urls,
        startTime: new Date()
      }));

      setIsPolling(true);

    } catch (error) {
      console.error('Error starting audit:', error);
      alert(`Failed to start audit: ${error}`);
    }
  };

  // Stop audit
  const stopAudit = async () => {
    if (!auditState.sessionId) return;

    try {
      const response = await fetch(`http://localhost:3000/api/audit/stop/${auditState.sessionId}`, {
        method: 'POST'
      });

      if (response.ok) {
        setAuditState(prev => ({
          ...prev,
          isRunning: false,
          auditComplete: false,
          statusText: '🛑 Audit stopped by user'
        }));
        setIsPolling(false);
      }
    } catch (error) {
      console.error('Error stopping audit:', error);
    }
  };

  // Process audit results
  const processAuditResults = async () => {
    if (!auditState.sessionId || !auditState.completedPersonaName) return;

    try {
      const response = await fetch('http://localhost:3000/api/audit/process', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          session_id: auditState.sessionId,
          persona_name: auditState.completedPersonaName
        })
      });

      if (response.ok) {
        setAuditState(prev => ({ ...prev, isProcessing: true }));
        setProcessingState({
          status: 'running',
          progress: 0,
          message: 'Starting post-processing...'
        });
        setIsPolling(true);
      }
    } catch (error) {
      console.error('Error starting processing:', error);
      alert(`Failed to start processing: ${error}`);
    }
  };

  // Reset audit state
  const resetAudit = () => {
    setAuditState({
      sessionId: null,
      isRunning: false,
      isProcessing: false,
      auditComplete: false,
      currentProgress: 0,
      statusText: '',
      logLines: [],
      personaName: '',
      completedPersonaName: '',
      totalUrls: 0,
      startTime: null
    });
    setProcessingState({
      status: 'not_started',
      progress: 0,
      message: ''
    });
    setIsPolling(false);
  };

  // Auto-scroll log container
  useEffect(() => {
    if (logContainerRef.current) {
      logContainerRef.current.scrollTop = logContainerRef.current.scrollHeight;
    }
  }, [auditState.logLines]);

  const urlValidation = validateUrls(urlsText);
  const canRunAudit = personaFile && urlsText.trim() && urlValidation.valid > 0 && !auditState.isRunning;

  return (
    <PageContainer title="🚀 Run New Audit">
      <div className="container--layout">
        {/* Left Column: Configuration */}
        <div className="container--layout">
          <div className="container--section">
            <h2 className="heading--section">🎯 Audit Process Overview</h2>
            <div className="container--layout">
              <div className="container--card container--form">
                <div className="number--display">1</div>
                <div className="container--workflow">
                  <h3 className="heading--card">📋 Upload Persona</h3>
                  <p className="text--body">Define your target audience with a comprehensive persona file</p>
                  <ul>
                    <li>Markdown format (.md)</li>
                    <li>Detailed persona characteristics</li>
                    <li>Business context and goals</li>
                  </ul>
                </div>
              </div>
              
              <div className="container--card container--model">
                <div className="number--display">2</div>
                <div className="container--workflow">
                  <h3 className="heading--card">🤖 Select AI Model</h3>
                  <p className="text--body">Choose between cost-effective and premium analysis</p>
                  <ul>
                    <li>OpenAI GPT-4.1-Mini (Cost effective)</li>
                    <li>Anthropic Claude-3-Opus (Premium)</li>
                    <li>Real-time model switching</li>
                  </ul>
                </div>
              </div>
              
              <div className="container--card container--urls">
                <div className="number--display">3</div>
                <div className="container--workflow">
                  <h3 className="heading--card">🌐 Provide URLs</h3>
                  <p className="text--body">Submit URLs for comprehensive brand analysis</p>
                  <ul>
                    <li>Multiple input methods</li>
                    <li>Automatic validation</li>
                    <li>Bulk URL processing</li>
                  </ul>
                </div>
              </div>
              
              <div className="container--card container--analysis">
                <div className="number--display">4</div>
                <div className="container--workflow">
                  <h3 className="heading--card">📊 Deep Analysis</h3>
                  <p className="text--body">AI-powered evaluation across 50+ criteria</p>
                  <ul>
                    <li>Experience reports</li>
                    <li>Hygiene scorecards</li>
                    <li>Strategic recommendations</li>
                  </ul>
                </div>
              </div>
            </div>
          </div>

          {/* Configuration Section */}
          <div className="container--section">
            <h2 className="heading--section">⚙️ Audit Configuration</h2>
            
            <div className="container--layout">
              {/* Persona Upload */}
              <div className="container--card container--section">
                <div className="container--layout">
                  <h3 className="heading--card">📋 Step 1: Upload Persona File</h3>
                  <div className="text--display">Required</div>
                </div>
                
                <div className="container--form">
                  <input
                    type="file"
                    id="persona-file"
                    accept=".md"
                    onChange={handlePersonaFileUpload}
                    disabled={auditState.isRunning}
                    className="input--file"
                  />
                  <label htmlFor="persona-file" className="label--upload">
                    <div className="icon--ui">📁</div>
                    <div className="container--content">
                      <span className="text--display">Choose Persona File</span>
                      <span className="text--body">Drag & drop or click to browse (.md files)</span>
                    </div>
                  </label>
                </div>
                
                {personaFile && (
                  <div className="container--section">
                    <div className="icon--ui">✅</div>
                    <Banner
                      message={
                        <>
                          <p className="text--body"><strong>File loaded:</strong> {personaFile.name}</p>
                          <p className="text--body"><strong>Detected persona:</strong> {extractPersonaName(personaContent, personaFile.name)}</p>
                          <p className="text--body"><strong>File size:</strong> {(personaFile.size / 1024).toFixed(1)} KB</p>
                        </>
                      }
                    />
                  </div>
                )}
              </div>

              {/* Model Selection */}
              <div className="container--card container--section">
                <div className="container--layout">
                  <h3 className="heading--card">🤖 Step 2: Select AI Model</h3>
                  <div className="text--display">Choose Wisely</div>
                </div>
                
                <div className="container--form">
                  <div className={`container--card ${selectedModel === 'openai' ? 'selected' : ''}`}>
                    <input
                      type="radio"
                      id="openai"
                      value="openai"
                      checked={selectedModel === 'openai'}
                      onChange={(e) => setSelectedModel(e.target.value as 'openai')}
                      disabled={auditState.isRunning}
                    />
                    <label htmlFor="openai" className="label--option">
                      <div className="icon--ui">🔥</div>
                      <div className="container--content">
                        <h4 className="heading--card">OpenAI GPT-4.1-Mini</h4>
                        <p className="text--body">Cost-effective choice with excellent quality</p>
                        <div className="container--section">
                          <span className="text--display badge--cost">Low Cost</span>
                          <span className="text--display badge--speed">Fast</span>
                          <span className="text--display badge--quality">High Quality</span>
                        </div>
                      </div>
                    </label>
                  </div>
                  
                  <div className={`container--card ${selectedModel === 'anthropic' ? 'selected' : ''}`}>
                    <input
                      type="radio"
                      id="anthropic"
                      value="anthropic"
                      checked={selectedModel === 'anthropic'}
                      onChange={(e) => setSelectedModel(e.target.value as 'anthropic')}
                      disabled={auditState.isRunning}
                    />
                    <label htmlFor="anthropic" className="label--option">
                      <div className="icon--ui">🧠</div>
                      <div className="container--content">
                        <h4 className="heading--card">Anthropic Claude-3-Opus</h4>
                        <p className="text--body">Premium choice for highest quality analysis</p>
                        <div className="container--section">
                          <span className="text--display badge--premium">Premium</span>
                          <span className="text--display badge--deep">Deep Analysis</span>
                          <span className="text--display badge--quality">Superior Quality</span>
                        </div>
                      </div>
                    </label>
                  </div>
                </div>
              </div>
            </div>

            {/* URL Input Section */}
            <div className="container--section container--section">
              <div className="container--layout">
                <h3 className="heading--card">🌐 Step 3: Provide URLs to Audit</h3>
                <div className="text--display">Multiple Methods</div>
              </div>
              
              <div className="container--form">
                <div className="tabs">
                  <button 
                    className={`tabs__button ${activeTab === 'paste' ? 'tabs__button--active' : ''}`}
                    onClick={() => setActiveTab('paste')}
                  >
                    ✏️ Paste URLs
                  </button>
                  <button 
                    className={`tabs__button ${activeTab === 'upload' ? 'tabs__button--active' : ''}`}
                    onClick={() => setActiveTab('upload')}
                  >
                    📁 Upload File
                  </button>
                </div>
                
                <div className="container--content">
                  {activeTab === 'paste' && (
                    <div className="container--form">
                      <textarea
                        value={urlsText}
                        onChange={(e) => setUrlsText(e.target.value)}
                        placeholder="https://example.com&#10;https://example.com/about&#10;https://example.com/services&#10;https://example.com/contact"
                        rows={8}
                        disabled={auditState.isRunning}
                        className="textarea--input"
                      />
                      <div className="container--section">
                        <span className="icon--help">💡</span>
                        <span>Enter one URL per line. Both HTTP and HTTPS URLs are supported.</span>
                      </div>
                    </div>
                  )}
                  
                  {activeTab === 'upload' && (
                    <div className="container--form">
                      <div className="container--form">
                        <input
                          type="file"
                          id="url-file"
                          accept=".txt,.md"
                          onChange={handleUrlFileUpload}
                          disabled={auditState.isRunning}
                          className="input--file"
                        />
                        <label htmlFor="url-file" className="label--upload">
                          <div className="icon--ui">📄</div>
                          <div className="container--content">
                            <span className="text--display">Upload URL File</span>
                            <span className="text--body">TXT or MD files containing URLs</span>
                          </div>
                        </label>
                      </div>
                    </div>
                  )}
                </div>
              </div>
            </div>

            {/* URL Validation */}
            {urlsText && (
              <div className="url-validation">
                <h4 className="validation-title">🔍 URL Validation Results</h4>
                <div className="validation-grid">
                  <StandardCard 
                    label="Total URLs" 
                    value={urlValidation.total.toString()} 
                    status="default"
                  />
                  <StandardCard 
                    label="Valid URLs" 
                    value={urlValidation.valid.toString()} 
                    status="good"
                  />
                  {urlValidation.invalid > 0 ? (
                    <StandardCard 
                      label="Invalid URLs" 
                      value={urlValidation.invalid.toString()} 
                      status="warning"
                    />
                  ) : (
                    <StandardCard 
                      label="Status" 
                      value="✅ All Valid" 
                      status="good"
                    />
                  )}
                  <StandardCard 
                    label="Ready to Audit" 
                    value={canRunAudit ? "✅ Yes" : "❌ No"} 
                    status={canRunAudit ? "good" : "warning"}
                  />
                </div>
                
                {urlValidation.invalid > 0 && (
                  <div className="container--form">
                    <h5>⚠️ Invalid URLs Found:</h5>
                    <ul>
                      {urlValidation.invalidUrls.slice(0, 5).map((url, index) => (
                        <li key={index}>{url}</li>
                      ))}
                      {urlValidation.invalidUrls.length > 5 && (
                        <li>... and {urlValidation.invalidUrls.length - 5} more</li>
                      )}
                    </ul>
                  </div>
                )}
              </div>
            )}

            {/* Launch Section */}
            <div className="container--workflow">
              <div className="container--section">
                <h4>🚀 Ready to Launch</h4>
                <div className="container--actions">
                  <div className="container--card">
                    <span className="text--summary-label">Persona:</span>
                    <span className="text--summary-value">
                      {personaFile ? extractPersonaName(personaContent, personaFile.name) : 'Not selected'}
                    </span>
                  </div>
                  <div className="container--card">
                    <span className="text--summary-label">AI Model:</span>
                    <span className="text--summary-value">{selectedModel.toUpperCase()}</span>
                  </div>
                  <div className="container--card">
                    <span className="text--summary-label">URLs:</span>
                    <span className="text--summary-value">{urlValidation.valid} valid URLs</span>
                  </div>
                  <div className="container--card">
                    <span className="text--summary-label">Estimated Time:</span>
                    <span className="text--summary-value">{Math.ceil(urlValidation.valid * 1.5)} minutes</span>
                  </div>
                </div>
              </div>
              
              <button 
                className={`button--launch ${canRunAudit ? 'ready' : 'disabled'}`}
                onClick={runAudit}
                disabled={!canRunAudit}
              >
                <div className="icon--ui">🚀</div>
                <div className="container--content">
                  <span className="text--launch-title">Launch Brand Audit</span>
                  <span className="text--launch-subtitle">
                    {!canRunAudit ? 'Complete configuration above' : 'Begin comprehensive analysis'}
                  </span>
                </div>
              </button>
            </div>
          </div>
        </div>

        {/* Right Column: Status & Logs */}
        <div className="container--layout">
          <div className="container--section">
            <h2 className="heading--section">📊 Audit Status & Logs</h2>
            {/* Running Audit Warning */}
            {auditState.isRunning && (
              <Banner
                type="warning"
                message={
                  <div className="container--layout">
                    <div className="icon--ui">⚠️</div>
                    <div className="container--content">
                      <h3 className="heading--subsection">Audit Currently Running</h3>
                      <p className="text--body">Persona: <strong>{auditState.personaName}</strong> • Model: <strong>{selectedModel.toUpperCase()}</strong></p>
                      <p className="text--body">Please wait for completion or stop the current audit below.</p>
                    </div>
                    <button className="button--action" onClick={stopAudit}>
                      🛑 Stop Audit
                    </button>
                  </div>
                }
              />
            )}

            {!auditState.isRunning && !auditState.auditComplete && !auditState.isProcessing && (
              <>
                {/* Audit Progress */}
                <div className="container--card">
                  <div className="container--workflow">
                    <h2>🔄 Audit in Progress</h2>
                    <div className="container--workflow">
                      <span>Using {selectedModel.toUpperCase()}</span>
                      <span>•</span>
                      <span>Persona: {auditState.personaName}</span>
                      <span>•</span>
                      <span>{auditState.totalUrls} URLs</span>
                    </div>
                  </div>
                  
                  <div className="container--workflow">
                    <div className="container--workflow">
                      <svg viewBox="0 0 100 100" className="progress-svg">
                        <circle
                          cx="50"
                          cy="50"
                          r="45"
                          fill="none"
                          stroke="#e5e5e5"
                          strokeWidth="8"
                        />
                        <circle
                          cx="50"
                          cy="50"
                          r="45"
                          fill="none"
                          stroke="#10b981"
                          strokeWidth="8"
                          strokeLinecap="round"
                          strokeDasharray={`${auditState.currentProgress * 2.83} 283`}
                          style={{ transition: 'stroke-dasharray 0.5s ease' }}
                        />
                      </svg>
                      <div className="container--workflow">
                        <span className="text--percentage">{auditState.currentProgress}%</span>
                        <span className="text--progress-label">Complete</span>
                      </div>
                    </div>
                    
                    <div className="container--workflow">
                      <div className="container--workflow">
                        <div className="icon--ui">🎯</div>
                        <div className="text--display">{auditState.statusText}</div>
                      </div>
                      
                      <div className="container--workflow">
                        <div className="container--card">
                          <span className="text--stat-label">Elapsed Time:</span>
                          <span className="text--stat-value">
                            {auditState.startTime ? 
                              Math.floor((Date.now() - auditState.startTime.getTime()) / 1000 / 60) : 0
                            } minutes
                          </span>
                        </div>
                        <div className="container--card">
                          <span className="text--stat-label">URLs Processed:</span>
                          <span className="text--stat-value">{Math.floor((auditState.currentProgress / 100) * auditState.totalUrls)}/{auditState.totalUrls}</span>
                        </div>
                      </div>
                    </div>
                  </div>
                  
                  <div className="container--card">
                    <div className="container--log-header">
                      <h3>📋 Live Audit Log</h3>
                      <div className="container--actions">
                        <span className="text--log-status">🟢 Live</span>
                      </div>
                    </div>
                    <div className="container--log-content" ref={logContainerRef}>
                      {auditState.logLines.length > 0 ? (
                        auditState.logLines.map((line, index) => (
                          <div key={index} className="container--log-line">{line}</div>
                        ))
                      ) : (
                        <div className="container--log-empty">Waiting for audit logs...</div>
                      )}
                    </div>
                  </div>
                </div>
              </>
            )}

            {/* Post-Audit Processing */}
            {auditState.auditComplete && !auditState.isRunning && !auditState.isProcessing && (
              <Banner
                type="success"
                message={
                  <div>
                    <div className="text-center">
                      <span className="text-5xl">🎉</span>
                      <h2 className="heading--section">✅ Audit Complete!</h2>
                      <p>Raw audit files generated successfully for <strong>{auditState.completedPersonaName}</strong></p>
                    </div>
                    
                    <div className="container--actions">
                      <div className="container--content">
                        <h3 className="heading--subsection">🎯 What's Next?</h3>
                        <div className="container--actions">
                          <div className="container--card">
                            <div className="journey--flow">🏷️</div>
                            <div className="container--content">
                              <h4>Tier Classification</h4>
                              <p>URLs classified into business importance tiers</p>
                            </div>
                          </div>
                          <div className="container--card">
                            <div className="journey--flow">📊</div>
                            <div className="container--content">
                              <h4>Data Processing</h4>
                              <p>Convert markdown reports to structured CSV/Parquet</p>
                            </div>
                          </div>
                          <div className="container--card">
                            <div className="journey--flow">📋</div>
                            <div className="container--content">
                              <h4>Strategic Summary</h4>
                              <p>Generate executive-level insights and recommendations</p>
                            </div>
                          </div>
                          <div className="container--card">
                            <div className="journey--flow">🗄️</div>
                            <div className="container--content">
                              <h4>Database Integration</h4>
                              <p>Add to unified multi-persona dataset</p>
                            </div>
                          </div>
                        </div>
                      </div>
                      
                      <div className="container--card">
                        <h4 className="heading--subsection">📊 Processing Status</h4>
                        <div className="container--card">
                          {processingState.status === 'completed' ? (
                            <div className="container--status-success">
                              <div className="icon--ui">✅</div>
                              <div className="text--display">
                                <p><strong>Already processed</strong></p>
                                <p>Data is ready for dashboard</p>
                              </div>
                            </div>
                          ) : (
                            <div className="container--status-pending">
                              <div className="icon--ui">⏳</div>
                              <div className="text--display">
                                <p><strong>Raw files only</strong></p>
                                <p>Needs processing for dashboard</p>
                              </div>
                            </div>
                          )}
                        </div>
                      </div>
                    </div>
                    
                    <div className="container--actions">
                      <button 
                        className={`process-button ${processingState.status === 'completed' ? 'completed' : ''}`}
                        onClick={processAuditResults}
                        disabled={processingState.status === 'completed' || processingState.status === 'running'}
                      >
                        <div className="button--action">
                          {processingState.status === 'completed' ? '✅' : '🗄️'}
                        </div>
                        <div className="container--content">
                          <span className="text--button-title">
                            {processingState.status === 'completed' ? 'Processing Complete' : 'Add to Database'}
                          </span>
                          <span className="text--button-subtitle">
                            {processingState.status === 'completed' 
                              ? 'Data ready for dashboard' 
                              : 'Process and integrate audit results'}
                          </span>
                        </div>
                      </button>
                      
                      {processingState.status === 'completed' && (
                        <div className="container--actions">
                          <button className="button--nav button--secondary">
                            <span className="button--action">🏠</span>
                            <span>Dashboard Home</span>
                          </button>
                          <button className="button--nav button--action" onClick={resetAudit}>
                            <span className="button--action">🚀</span>
                            <span>Run Another Audit</span>
                          </button>
                        </div>
                      )}
                    </div>
                  </div>
                }
              />
            )}

            {/* Processing Progress */}
            {auditState.isProcessing && (
              <div className="container--workflow">
                <div className="container--workflow">
                  <h2>🔄 Processing Audit Results</h2>
                  <p>Converting raw audit files into dashboard-ready data...</p>
                </div>
                
                <div className="container--workflow">
                  <div className="container--workflow">
                    <div className={`container--card ${processingState.progress >= 20 ? 'completed' : processingState.progress >= 10 ? 'active' : ''}`}>
                      <div className="number--display">1</div>
                      <div className="text--display">Import</div>
                    </div>
                    <div className={`container--card ${processingState.progress >= 40 ? 'completed' : processingState.progress >= 30 ? 'active' : ''}`}>
                      <div className="number--display">2</div>
                      <div className="text--display">Classify</div>
                    </div>
                    <div className={`container--card ${processingState.progress >= 60 ? 'completed' : processingState.progress >= 50 ? 'active' : ''}`}>
                      <div className="number--display">3</div>
                      <div className="text--display">Process</div>
                    </div>
                    <div className={`container--card ${processingState.progress >= 80 ? 'completed' : processingState.progress >= 70 ? 'active' : ''}`}>
                      <div className="number--display">4</div>
                      <div className="text--display">Summarize</div>
                    </div>
                    <div className={`container--card ${processingState.progress >= 100 ? 'completed' : processingState.progress >= 90 ? 'active' : ''}`}>
                      <div className="number--display">5</div>
                      <div className="text--display">Integrate</div>
                    </div>
                  </div>
                  
                  <div className="container--workflow">
                    <div 
                      className="container--workflow" 
                      style={{ width: `${processingState.progress}%` }}
                    />
                  </div>
                  
                  <div className="container--card">
                    <div className="text--display">{processingState.message}</div>
                    <div className="text--display">{processingState.progress}%</div>
                  </div>
                </div>
              </div>
            )}
          </div>
        </div>
      </div>
    </PageContainer>
  );
};

export default RunAudit;
