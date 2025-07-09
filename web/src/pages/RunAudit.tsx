import { useState, useEffect, useRef, useCallback } from 'react';
import { ScoreCard } from '../components/ScoreCard';
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
      const response = await fetch(`http://localhost:3000/api/audit/processing-status/${sessionId}`);
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
    <div className="run-audit-container">
      {/* Hero Header */}
      <div className="hero-header">
        <div className="hero-content">
          <div className="hero-icon">🚀</div>
          <h1 className="hero-title">Brand Audit Runner</h1>
          <p className="hero-subtitle">
            Launch sophisticated brand audits with YAML-driven methodology and dual AI provider support
          </p>
          <div className="hero-stats">
            <div className="stat-item">
              <span className="stat-number">50+</span>
              <span className="stat-label">Criteria</span>
            </div>
            <div className="stat-item">
              <span className="stat-number">2</span>
              <span className="stat-label">AI Models</span>
            </div>
            <div className="stat-item">
              <span className="stat-number">100%</span>
              <span className="stat-label">Automated</span>
            </div>
          </div>
        </div>
      </div>

      {/* Running Audit Warning */}
      {auditState.isRunning && (
        <div className="audit-warning">
          <div className="warning-content">
            <div className="warning-icon">⚠️</div>
            <div className="warning-text">
              <h3>Audit Currently Running</h3>
              <p>Persona: <strong>{auditState.personaName}</strong> • Model: <strong>{selectedModel.toUpperCase()}</strong></p>
              <p>Please wait for completion or stop the current audit below.</p>
            </div>
            <button className="stop-audit-btn" onClick={stopAudit}>
              🛑 Stop Audit
            </button>
          </div>
        </div>
      )}

      {!auditState.isRunning && !auditState.auditComplete && !auditState.isProcessing && (
        <>
          {/* Process Overview */}
          <div className="process-overview">
            <h2 className="section-title">🎯 Audit Process Overview</h2>
            <div className="process-grid">
              <div className="process-card upload">
                <div className="process-number">1</div>
                <div className="process-content">
                  <h3>📋 Upload Persona</h3>
                  <p>Define your target audience with a comprehensive persona file</p>
                  <ul>
                    <li>Markdown format (.md)</li>
                    <li>Detailed persona characteristics</li>
                    <li>Business context and goals</li>
                  </ul>
                </div>
              </div>
              
              <div className="process-card model">
                <div className="process-number">2</div>
                <div className="process-content">
                  <h3>🤖 Select AI Model</h3>
                  <p>Choose between cost-effective and premium analysis</p>
                  <ul>
                    <li>OpenAI GPT-4.1-Mini (Cost effective)</li>
                    <li>Anthropic Claude-3-Opus (Premium)</li>
                    <li>Real-time model switching</li>
                  </ul>
                </div>
              </div>
              
              <div className="process-card urls">
                <div className="process-number">3</div>
                <div className="process-content">
                  <h3>🌐 Provide URLs</h3>
                  <p>Submit URLs for comprehensive brand analysis</p>
                  <ul>
                    <li>Multiple input methods</li>
                    <li>Automatic validation</li>
                    <li>Bulk URL processing</li>
                  </ul>
                </div>
              </div>
              
              <div className="process-card analysis">
                <div className="process-number">4</div>
                <div className="process-content">
                  <h3>📊 Deep Analysis</h3>
                  <p>AI-powered evaluation across 50+ criteria</p>
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
          <div className="audit-configuration">
            <h2 className="section-title">⚙️ Audit Configuration</h2>
            
            <div className="config-grid">
              {/* Persona Upload */}
              <div className="config-section persona-section">
                <div className="section-header">
                  <h3>📋 Step 1: Upload Persona File</h3>
                  <div className="section-badge">Required</div>
                </div>
                
                <div className="file-upload-area">
                  <input
                    type="file"
                    id="persona-file"
                    accept=".md"
                    onChange={handlePersonaFileUpload}
                    disabled={auditState.isRunning}
                    className="file-input"
                  />
                  <label htmlFor="persona-file" className="file-upload-label">
                    <div className="upload-icon">📁</div>
                    <div className="upload-text">
                      <span className="upload-title">Choose Persona File</span>
                      <span className="upload-subtitle">Drag & drop or click to browse (.md files)</span>
                    </div>
                  </label>
                </div>
                
                {personaFile && (
                  <div className="file-success">
                    <div className="success-icon">✅</div>
                    <div className="success-content">
                      <p><strong>File loaded:</strong> {personaFile.name}</p>
                      <p><strong>Detected persona:</strong> {extractPersonaName(personaContent, personaFile.name)}</p>
                      <p><strong>File size:</strong> {(personaFile.size / 1024).toFixed(1)} KB</p>
                    </div>
                  </div>
                )}
              </div>

              {/* Model Selection */}
              <div className="config-section model-section">
                <div className="section-header">
                  <h3>🤖 Step 2: Select AI Model</h3>
                  <div className="section-badge">Choose Wisely</div>
                </div>
                
                <div className="model-options">
                  <div className={`model-option ${selectedModel === 'openai' ? 'selected' : ''}`}>
                    <input
                      type="radio"
                      id="openai"
                      value="openai"
                      checked={selectedModel === 'openai'}
                      onChange={(e) => setSelectedModel(e.target.value as 'openai')}
                      disabled={auditState.isRunning}
                    />
                    <label htmlFor="openai" className="model-label">
                      <div className="model-icon">🔥</div>
                      <div className="model-content">
                        <h4>OpenAI GPT-4.1-Mini</h4>
                        <p className="model-description">Cost-effective choice with excellent quality</p>
                        <div className="model-features">
                          <span className="feature-tag cost">Low Cost</span>
                          <span className="feature-tag speed">Fast</span>
                          <span className="feature-tag quality">High Quality</span>
                        </div>
                      </div>
                    </label>
                  </div>
                  
                  <div className={`model-option ${selectedModel === 'anthropic' ? 'selected' : ''}`}>
                    <input
                      type="radio"
                      id="anthropic"
                      value="anthropic"
                      checked={selectedModel === 'anthropic'}
                      onChange={(e) => setSelectedModel(e.target.value as 'anthropic')}
                      disabled={auditState.isRunning}
                    />
                    <label htmlFor="anthropic" className="model-label">
                      <div className="model-icon">🧠</div>
                      <div className="model-content">
                        <h4>Anthropic Claude-3-Opus</h4>
                        <p className="model-description">Premium choice for highest quality analysis</p>
                        <div className="model-features">
                          <span className="feature-tag premium">Premium</span>
                          <span className="feature-tag deep">Deep Analysis</span>
                          <span className="feature-tag quality">Superior Quality</span>
                        </div>
                      </div>
                    </label>
                  </div>
                </div>
              </div>
            </div>

            {/* URL Input Section */}
            <div className="config-section urls-section">
              <div className="section-header">
                <h3>🌐 Step 3: Provide URLs to Audit</h3>
                <div className="section-badge">Multiple Methods</div>
              </div>
              
              <div className="url-input-container">
                <div className="url-tabs">
                  <button 
                    className={`url-tab ${activeTab === 'paste' ? 'active' : ''}`}
                    onClick={() => setActiveTab('paste')}
                  >
                    ✏️ Paste URLs
                  </button>
                  <button 
                    className={`url-tab ${activeTab === 'upload' ? 'active' : ''}`}
                    onClick={() => setActiveTab('upload')}
                  >
                    📁 Upload File
                  </button>
                </div>
                
                <div className="url-input-content">
                  {activeTab === 'paste' && (
                    <div className="url-paste-section">
                      <textarea
                        value={urlsText}
                        onChange={(e) => setUrlsText(e.target.value)}
                        placeholder="https://example.com&#10;https://example.com/about&#10;https://example.com/services&#10;https://example.com/contact"
                        rows={8}
                        disabled={auditState.isRunning}
                        className="url-textarea"
                      />
                      <div className="url-help">
                        <span className="help-icon">💡</span>
                        <span>Enter one URL per line. Both HTTP and HTTPS URLs are supported.</span>
                      </div>
                    </div>
                  )}
                  
                  {activeTab === 'upload' && (
                    <div className="url-upload-section">
                      <div className="file-upload-area">
                        <input
                          type="file"
                          id="url-file"
                          accept=".txt,.md"
                          onChange={handleUrlFileUpload}
                          disabled={auditState.isRunning}
                          className="file-input"
                        />
                        <label htmlFor="url-file" className="file-upload-label">
                          <div className="upload-icon">📄</div>
                          <div className="upload-text">
                            <span className="upload-title">Upload URL File</span>
                            <span className="upload-subtitle">TXT or MD files containing URLs</span>
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
                  <ScoreCard 
                    label="Total URLs" 
                    value={urlValidation.total.toString()} 
                    variant="default"
                  />
                  <ScoreCard 
                    label="Valid URLs" 
                    value={urlValidation.valid.toString()} 
                    variant="success"
                  />
                  {urlValidation.invalid > 0 ? (
                    <ScoreCard 
                      label="Invalid URLs" 
                      value={urlValidation.invalid.toString()} 
                      variant="warning"
                    />
                  ) : (
                    <ScoreCard 
                      label="Status" 
                      value="✅ All Valid" 
                      variant="success"
                    />
                  )}
                  <ScoreCard 
                    label="Ready to Audit" 
                    value={canRunAudit ? "✅ Yes" : "❌ No"} 
                    variant={canRunAudit ? "success" : "warning"}
                  />
                </div>
                
                {urlValidation.invalid > 0 && (
                  <div className="invalid-urls">
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
            <div className="launch-section">
              <div className="launch-summary">
                <h4>🚀 Ready to Launch</h4>
                <div className="summary-items">
                  <div className="summary-item">
                    <span className="summary-label">Persona:</span>
                    <span className="summary-value">
                      {personaFile ? extractPersonaName(personaContent, personaFile.name) : 'Not selected'}
                    </span>
                  </div>
                  <div className="summary-item">
                    <span className="summary-label">AI Model:</span>
                    <span className="summary-value">{selectedModel.toUpperCase()}</span>
                  </div>
                  <div className="summary-item">
                    <span className="summary-label">URLs:</span>
                    <span className="summary-value">{urlValidation.valid} valid URLs</span>
                  </div>
                  <div className="summary-item">
                    <span className="summary-label">Estimated Time:</span>
                    <span className="summary-value">{Math.ceil(urlValidation.valid * 1.5)} minutes</span>
                  </div>
                </div>
              </div>
              
              <button 
                className={`launch-button ${canRunAudit ? 'ready' : 'disabled'}`}
                onClick={runAudit}
                disabled={!canRunAudit}
              >
                <div className="launch-icon">🚀</div>
                <div className="launch-text">
                  <span className="launch-title">Launch Brand Audit</span>
                  <span className="launch-subtitle">
                    {!canRunAudit ? 'Complete configuration above' : 'Begin comprehensive analysis'}
                  </span>
                </div>
              </button>
            </div>
          </div>
        </>
      )}

      {/* Audit Progress */}
      {auditState.isRunning && (
        <div className="audit-progress">
          <div className="progress-header">
            <h2>🔄 Audit in Progress</h2>
            <div className="progress-meta">
              <span>Using {selectedModel.toUpperCase()}</span>
              <span>•</span>
              <span>Persona: {auditState.personaName}</span>
              <span>•</span>
              <span>{auditState.totalUrls} URLs</span>
            </div>
          </div>
          
          <div className="progress-visualization">
            <div className="progress-circle">
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
              <div className="progress-text">
                <span className="progress-percentage">{auditState.currentProgress}%</span>
                <span className="progress-label">Complete</span>
              </div>
            </div>
            
            <div className="progress-details">
              <div className="progress-status">
                <div className="status-icon">🎯</div>
                <div className="status-text">{auditState.statusText}</div>
              </div>
              
              <div className="progress-stats">
                <div className="stat">
                  <span className="stat-label">Elapsed Time:</span>
                  <span className="stat-value">
                    {auditState.startTime ? 
                      Math.floor((Date.now() - auditState.startTime.getTime()) / 1000 / 60) : 0
                    } minutes
                  </span>
                </div>
                <div className="stat">
                  <span className="stat-label">URLs Processed:</span>
                  <span className="stat-value">{Math.floor((auditState.currentProgress / 100) * auditState.totalUrls)}/{auditState.totalUrls}</span>
                </div>
              </div>
            </div>
          </div>
          
          <div className="audit-log">
            <div className="log-header">
              <h3>📋 Live Audit Log</h3>
              <div className="log-controls">
                <span className="log-status">🟢 Live</span>
              </div>
            </div>
            <div className="log-container" ref={logContainerRef}>
              {auditState.logLines.length > 0 ? (
                auditState.logLines.map((line, index) => (
                  <div key={index} className="log-line">{line}</div>
                ))
              ) : (
                <div className="log-empty">Waiting for audit logs...</div>
              )}
            </div>
          </div>
        </div>
      )}

      {/* Post-Audit Processing */}
      {auditState.auditComplete && !auditState.isRunning && !auditState.isProcessing && (
        <div className="post-audit">
          <div className="completion-celebration">
            <div className="celebration-animation">🎉</div>
            <h2>✅ Audit Complete!</h2>
            <p>Raw audit files generated successfully for <strong>{auditState.completedPersonaName}</strong></p>
          </div>
          
          <div className="next-steps-container">
            <div className="next-steps-info">
              <h3>🎯 What's Next?</h3>
              <div className="steps-grid">
                <div className="step-card">
                  <div className="step-icon">🏷️</div>
                  <div className="step-content">
                    <h4>Tier Classification</h4>
                    <p>URLs classified into business importance tiers</p>
                  </div>
                </div>
                <div className="step-card">
                  <div className="step-icon">📊</div>
                  <div className="step-content">
                    <h4>Data Processing</h4>
                    <p>Convert markdown reports to structured CSV/Parquet</p>
                  </div>
                </div>
                <div className="step-card">
                  <div className="step-icon">📋</div>
                  <div className="step-content">
                    <h4>Strategic Summary</h4>
                    <p>Generate executive-level insights and recommendations</p>
                  </div>
                </div>
                <div className="step-card">
                  <div className="step-icon">🗄️</div>
                  <div className="step-content">
                    <h4>Database Integration</h4>
                    <p>Add to unified multi-persona dataset</p>
                  </div>
                </div>
              </div>
            </div>
            
            <div className="processing-status">
              <h4>📊 Processing Status</h4>
              <div className="status-card">
                {processingState.status === 'completed' ? (
                  <div className="status-success">
                    <div className="status-icon">✅</div>
                    <div className="status-text">
                      <p><strong>Already processed</strong></p>
                      <p>Data is ready for dashboard</p>
                    </div>
                  </div>
                ) : (
                  <div className="status-pending">
                    <div className="status-icon">⏳</div>
                    <div className="status-text">
                      <p><strong>Raw files only</strong></p>
                      <p>Needs processing for dashboard</p>
                    </div>
                  </div>
                )}
              </div>
            </div>
          </div>
          
          <div className="action-section">
            <button 
              className={`process-button ${processingState.status === 'completed' ? 'completed' : ''}`}
              onClick={processAuditResults}
              disabled={processingState.status === 'completed' || processingState.status === 'running'}
            >
              <div className="button-icon">
                {processingState.status === 'completed' ? '✅' : '🗄️'}
              </div>
              <div className="button-content">
                <span className="button-title">
                  {processingState.status === 'completed' ? 'Processing Complete' : 'Add to Database'}
                </span>
                <span className="button-subtitle">
                  {processingState.status === 'completed' 
                    ? 'Data ready for dashboard' 
                    : 'Process and integrate audit results'}
                </span>
              </div>
            </button>
            
            {processingState.status === 'completed' && (
              <div className="completion-actions">
                <button className="nav-button secondary">
                  <span className="button-icon">🏠</span>
                  <span>Dashboard Home</span>
                </button>
                <button className="nav-button primary" onClick={resetAudit}>
                  <span className="button-icon">🚀</span>
                  <span>Run Another Audit</span>
                </button>
              </div>
            )}
          </div>
        </div>
      )}

      {/* Processing Progress */}
      {auditState.isProcessing && (
        <div className="processing-progress">
          <div className="processing-header">
            <h2>🔄 Processing Audit Results</h2>
            <p>Converting raw audit files into dashboard-ready data...</p>
          </div>
          
          <div className="processing-visualization">
            <div className="processing-steps">
              <div className={`step ${processingState.progress >= 20 ? 'completed' : processingState.progress >= 10 ? 'active' : ''}`}>
                <div className="step-number">1</div>
                <div className="step-label">Import</div>
              </div>
              <div className={`step ${processingState.progress >= 40 ? 'completed' : processingState.progress >= 30 ? 'active' : ''}`}>
                <div className="step-number">2</div>
                <div className="step-label">Classify</div>
              </div>
              <div className={`step ${processingState.progress >= 60 ? 'completed' : processingState.progress >= 50 ? 'active' : ''}`}>
                <div className="step-number">3</div>
                <div className="step-label">Process</div>
              </div>
              <div className={`step ${processingState.progress >= 80 ? 'completed' : processingState.progress >= 70 ? 'active' : ''}`}>
                <div className="step-number">4</div>
                <div className="step-label">Summarize</div>
              </div>
              <div className={`step ${processingState.progress >= 100 ? 'completed' : processingState.progress >= 90 ? 'active' : ''}`}>
                <div className="step-number">5</div>
                <div className="step-label">Integrate</div>
              </div>
            </div>
            
            <div className="processing-bar">
              <div 
                className="processing-fill" 
                style={{ width: `${processingState.progress}%` }}
              />
            </div>
            
            <div className="processing-status">
              <div className="status-message">{processingState.message}</div>
              <div className="status-percentage">{processingState.progress}%</div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default RunAudit;
