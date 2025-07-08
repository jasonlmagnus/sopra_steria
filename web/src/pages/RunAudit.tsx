import { useState, useEffect, useRef } from 'react';
import { ScoreCard } from '../components/ScoreCard';

interface AuditState {
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

interface PostProcessingStatus {
  hasCSV: boolean;
  hasStrategicSummary: boolean;
  isProcessed: boolean;
}

const RunAudit: React.FC = () => {
  const [personaFile, setPersonaFile] = useState<File | null>(null);
  const [personaContent, setPersonaContent] = useState<string>('');
  const [urlsText, setUrlsText] = useState<string>('');
  const [selectedModel, setSelectedModel] = useState<'openai' | 'anthropic'>('openai');
  const [activeTab, setActiveTab] = useState<'paste' | 'upload'>('paste');
  const [auditState, setAuditState] = useState<AuditState>({
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
  const [postProcessingStatus, setPostProcessingStatus] = useState<PostProcessingStatus>({
    hasCSV: false,
    hasStrategicSummary: false,
    isProcessed: false
  });

  const logContainerRef = useRef<HTMLDivElement>(null);

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

  // Handle persona file upload
  const handlePersonaFileUpload = (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (file) {
      setPersonaFile(file);
      const reader = new FileReader();
      reader.onload = (e) => {
        const content = e.target?.result as string;
        setPersonaContent(content);
      };
      reader.readAsText(file);
    }
  };

  // Handle URL file upload
  const handleUrlFileUpload = (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (file) {
      const reader = new FileReader();
      reader.onload = (e) => {
        const content = e.target?.result as string;
        const urlRegex = /https?:\/\/[^\s|)]+/g;
        const urls = content.match(urlRegex) || [];
        setUrlsText(urls.join('\n'));
      };
      reader.readAsText(file);
    }
  };

  // Validate URLs
  const validateUrls = (text: string) => {
    const urls = text.split('\n').filter(url => url.trim());
    const validUrls = urls.filter(url => url.startsWith('http://') || url.startsWith('https://'));
    return {
      total: urls.length,
      valid: validUrls.length,
      invalid: urls.length - validUrls.length
    };
  };

  // Simulate audit execution
  const runAudit = async () => {
    if (!personaFile || !urlsText.trim()) return;

    const personaName = extractPersonaName(personaContent, personaFile.name);
    const urls = urlsText.split('\n').filter(url => url.trim());
    const validUrls = urls.filter(url => url.startsWith('http://') || url.startsWith('https://'));

    setAuditState(prev => ({
      ...prev,
      isRunning: true,
      auditComplete: false,
      currentProgress: 0,
      statusText: `Starting audit for ${personaName} using ${selectedModel.toUpperCase()}...`,
      logLines: [],
      personaName,
      totalUrls: validUrls.length,
      startTime: new Date()
    }));

    // Simulate audit process with realistic logging
    const simulateAuditProcess = () => {
      let progress = 0;
      const maxProgress = 100;
      const logMessages = [
        `🚀 Starting Brand Audit for ${personaName}`,
        `🤖 Using ${selectedModel.toUpperCase()} AI Model`,
        `📋 Processing ${validUrls.length} URLs`,
        `🔍 Initializing audit methodology...`,
        `⚙️ Loading YAML configuration...`,
        `🎯 Setting up persona context...`,
        `🌐 Beginning URL analysis...`,
        ...validUrls.map((url, index) => `📊 Analyzing URL ${index + 1}/${validUrls.length}: ${url}`),
        `📝 Generating experience reports...`,
        `🏥 Creating hygiene scorecards...`,
        `📊 Compiling audit results...`,
        `✅ Audit completed successfully!`
      ];

      let messageIndex = 0;
      const interval = setInterval(() => {
        if (messageIndex < logMessages.length) {
          const message = logMessages[messageIndex];
          setAuditState(prev => ({
            ...prev,
            currentProgress: Math.min(progress, maxProgress),
            statusText: message,
            logLines: [...prev.logLines, `[${new Date().toLocaleTimeString()}] ${message}`]
          }));
          
          messageIndex++;
          progress += (100 / logMessages.length);
        } else {
          clearInterval(interval);
          setAuditState(prev => ({
            ...prev,
            isRunning: false,
            auditComplete: true,
            currentProgress: 100,
            statusText: 'Audit completed successfully!',
            completedPersonaName: personaName
          }));
        }
      }, 1000 + Math.random() * 2000); // Random delay between 1-3 seconds
    };

    simulateAuditProcess();
  };

  // Stop audit
  const stopAudit = () => {
    setAuditState(prev => ({
      ...prev,
      isRunning: false,
      auditComplete: false,
      currentProgress: 0,
      statusText: 'Audit stopped by user',
      logLines: [...prev.logLines, `[${new Date().toLocaleTimeString()}] 🛑 Audit stopped by user`]
    }));
  };

  // Process audit results
  const processAuditResults = async () => {
    setAuditState(prev => ({ ...prev, isProcessing: true }));

    const processingSteps = [
      '📦 Importing post-processor...',
      '🏗️ Initializing processor...',
      '✅ Validating audit output...',
      '🏷️ Classifying page tiers...',
      '📊 Processing backfill data...',
      '📋 Generating strategic summary...',
      '🗄️ Adding to unified database...',
      '🔄 Refreshing dashboard cache...',
      '🎉 Successfully added to database!'
    ];

    let stepIndex = 0;
    const interval = setInterval(() => {
      if (stepIndex < processingSteps.length) {
        setAuditState(prev => ({
          ...prev,
          statusText: processingSteps[stepIndex],
          currentProgress: ((stepIndex + 1) / processingSteps.length) * 100
        }));
        stepIndex++;
      } else {
        clearInterval(interval);
        setAuditState(prev => ({ ...prev, isProcessing: false }));
        setPostProcessingStatus({
          hasCSV: true,
          hasStrategicSummary: true,
          isProcessed: true
        });
      }
    }, 1500);
  };

  // Reset audit state
  const resetAudit = () => {
    setAuditState({
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
    setPostProcessingStatus({
      hasCSV: false,
      hasStrategicSummary: false,
      isProcessed: false
    });
  };

  // Auto-scroll log container
  useEffect(() => {
    if (logContainerRef.current) {
      logContainerRef.current.scrollTop = logContainerRef.current.scrollHeight;
    }
  }, [auditState.logLines]);

  const urlValidation = validateUrls(urlsText);
  const canRunAudit = personaFile && urlsText.trim() && !auditState.isRunning;

  return (
    <div className="page-container">
      <div className="main-header">
        <h1>🚀 Run Brand Audit</h1>
        <p>Launch new audits with YAML-driven methodology and dual AI provider support</p>
      </div>

      {/* Running Audit Warning */}
      {auditState.isRunning && (
        <div className="warning-banner">
          <h3>⚠️ Audit Currently Running</h3>
          <p>Please wait for the current audit to complete or stop it below.</p>
          <button className="stop-button" onClick={stopAudit}>
            🛑 Stop Current Audit
          </button>
        </div>
      )}

      {!auditState.isRunning && !auditState.auditComplete && (
        <>
          {/* Introduction */}
          <div className="section">
            <h2>🎯 Launch New Brand Audit</h2>
            <p>
              Upload a persona file and provide URLs to analyze. The audit will generate <strong>raw analysis files</strong>:
            </p>
            <ul>
              <li><strong>Experience Reports</strong> - Persona-specific user journey analysis (markdown)</li>
              <li><strong>Hygiene Scorecards</strong> - Detailed criteria-based evaluations (markdown)</li>
            </ul>
            <p>
              After completion, use <strong>"ADD TO DATABASE"</strong> to process these into dashboard-ready data:
            </p>
            <ul>
              <li><strong>Strategic Summary</strong> - Executive insights and recommendations</li>
              <li><strong>Structured CSV/Parquet</strong> - Dashboard-compatible datasets</li>
              <li><strong>Tier Classifications</strong> - Business importance rankings</li>
            </ul>
          </div>

          {/* Configuration */}
          <div className="audit-config">
            <div className="config-section">
              <div className="step-header">
                <h3>📋 Step 1: Upload Persona File</h3>
              </div>
              
              <div className="file-upload">
                <input
                  type="file"
                  accept=".md"
                  onChange={handlePersonaFileUpload}
                  disabled={auditState.isRunning}
                />
                <p>Choose your persona markdown file</p>
              </div>
              
              {personaFile && (
                <div className="file-success">
                  <p>✅ Persona file loaded: {personaFile.name}</p>
                  <p>Detected persona: <strong>{extractPersonaName(personaContent, personaFile.name)}</strong></p>
                </div>
              )}

              <div className="step-header">
                <h3>🤖 Step 1.5: Select AI Model</h3>
              </div>
              
              <div className="model-selection">
                <label>
                  <input
                    type="radio"
                    value="openai"
                    checked={selectedModel === 'openai'}
                    onChange={(e) => setSelectedModel(e.target.value as 'openai')}
                    disabled={auditState.isRunning}
                  />
                  🔥 OpenAI GPT-4.1-Mini (Cost Effective)
                </label>
                <label>
                  <input
                    type="radio"
                    value="anthropic"
                    checked={selectedModel === 'anthropic'}
                    onChange={(e) => setSelectedModel(e.target.value as 'anthropic')}
                    disabled={auditState.isRunning}
                  />
                  🧠 Anthropic Claude-3-Opus (Premium Quality)
                </label>
              </div>
              
              {selectedModel === 'openai' && (
                <div className="model-info cost-effective">
                  💰 <strong>Cost Effective Choice</strong> - GPT-4.1-Mini offers excellent quality at lower cost
                </div>
              )}
              
              {selectedModel === 'anthropic' && (
                <div className="model-info premium">
                  💎 <strong>Premium Choice</strong> - Claude-3-Opus provides highest quality but at higher cost
                </div>
              )}
            </div>

            <div className="config-section">
              <div className="step-header">
                <h3>🌐 Step 2: Provide URLs to Audit</h3>
              </div>
              
              <div className="url-input-tabs">
                <button 
                  className={`tab-button ${activeTab === 'paste' ? 'active' : ''}`}
                  onClick={() => setActiveTab('paste')}
                >
                  Paste URLs
                </button>
                <button 
                  className={`tab-button ${activeTab === 'upload' ? 'active' : ''}`}
                  onClick={() => setActiveTab('upload')}
                >
                  Upload File
                </button>
              </div>
              
              {activeTab === 'paste' && (
                <div className="url-paste">
                  <textarea
                    value={urlsText}
                    onChange={(e) => setUrlsText(e.target.value)}
                    placeholder="https://example.com&#10;https://example.com/about&#10;https://example.com/services"
                    rows={8}
                    disabled={auditState.isRunning}
                  />
                  <p>Enter one URL per line</p>
                </div>
              )}
              
              {activeTab === 'upload' && (
                <div className="url-upload">
                  <input
                    type="file"
                    accept=".txt,.md"
                    onChange={handleUrlFileUpload}
                    disabled={auditState.isRunning}
                  />
                  <p>Upload a .txt or .md file with URLs</p>
                </div>
              )}
            </div>
          </div>

          {/* URL Validation */}
          {urlsText && (
            <div className="url-validation">
              <div className="validation-metrics">
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
                {urlValidation.invalid > 0 && (
                  <ScoreCard 
                    label="Invalid URLs" 
                    value={urlValidation.invalid.toString()} 
                    variant="warning"
                  />
                )}
                {urlValidation.invalid === 0 && (
                  <ScoreCard 
                    label="Status" 
                    value="✅ All Valid" 
                    variant="success"
                  />
                )}
              </div>
            </div>
          )}

          {/* Run Audit Button */}
          <div className="run-audit-section">
            <button 
              className="run-audit-button"
              onClick={runAudit}
              disabled={!canRunAudit}
            >
              🚀 Run Brand Audit
            </button>
          </div>
        </>
      )}

      {/* Audit Progress */}
      {auditState.isRunning && (
        <div className="audit-progress">
          <h2>🔄 Audit in Progress - Using {selectedModel.toUpperCase()}</h2>
          
          <div className="progress-section">
            <div className="progress-bar">
              <div 
                className="progress-fill" 
                style={{ width: `${auditState.currentProgress}%` }}
              />
            </div>
            <p className="progress-text">{auditState.statusText}</p>
          </div>
          
          <div className="audit-log">
            <h3>📋 Live Audit Log</h3>
            <div className="log-container" ref={logContainerRef}>
              {auditState.logLines.map((line, index) => (
                <div key={index} className="log-line">{line}</div>
              ))}
            </div>
          </div>
        </div>
      )}

      {/* Post-Audit Processing */}
      {auditState.auditComplete && !auditState.isRunning && (
        <div className="post-audit">
          <h2>🎯 Audit Complete - Next Steps</h2>
          
          <div className="completion-banner">
            <h3>✅ Audit Complete: {auditState.completedPersonaName}</h3>
            <p>Raw audit files have been generated successfully.</p>
          </div>
          
          <div className="next-steps">
            <div className="steps-info">
              <h4>What happens when you click "ADD TO DATABASE":</h4>
              <ol>
                <li>🏷️ <strong>Tier Classification</strong> - URLs classified into business importance tiers</li>
                <li>📊 <strong>Data Processing</strong> - Convert markdown reports to structured CSV/Parquet</li>
                <li>📋 <strong>Strategic Summary</strong> - Generate executive-level insights and recommendations</li>
                <li>🗄️ <strong>Database Integration</strong> - Add to unified multi-persona dataset</li>
                <li>🔄 <strong>Dashboard Update</strong> - New data becomes available across all dashboard pages</li>
              </ol>
            </div>
            
            <div className="processing-status">
              <h4>Processing Status:</h4>
              {postProcessingStatus.isProcessed ? (
                <div className="status-success">
                  <p>✅ Already processed</p>
                  <p>Data is ready for dashboard</p>
                </div>
              ) : (
                <div className="status-pending">
                  <p>⏳ Raw files only</p>
                  <p>Needs processing for dashboard</p>
                </div>
              )}
            </div>
          </div>
          
          <div className="action-buttons">
            <button 
              className="process-button"
              onClick={processAuditResults}
              disabled={auditState.isProcessing || postProcessingStatus.isProcessed}
            >
              {auditState.isProcessing ? '🔄 Processing...' : '🗄️ ADD TO DATABASE'}
            </button>
            
            {postProcessingStatus.isProcessed && (
              <div className="completion-actions">
                <button className="nav-button secondary">
                  🏠 Go to Dashboard Home
                </button>
                <button className="nav-button primary" onClick={resetAudit}>
                  🚀 Run Another Audit
                </button>
              </div>
            )}
          </div>
        </div>
      )}

      {/* Processing Progress */}
      {auditState.isProcessing && (
        <div className="processing-progress">
          <h2>🔄 Processing Audit Results...</h2>
          <div className="progress-section">
            <div className="progress-bar">
              <div 
                className="progress-fill" 
                style={{ width: `${auditState.currentProgress}%` }}
              />
            </div>
            <p className="progress-text">{auditState.statusText}</p>
          </div>
        </div>
      )}
    </div>
  );
};

export default RunAudit;
