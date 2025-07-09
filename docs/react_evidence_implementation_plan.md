# React Evidence Implementation Plan

**Date:** January 8, 2025  
**Purpose:** Detailed implementation plan for enhancing React pages to fully utilize evidence and persona data

## Implementation Priority Matrix

### Phase 1: Critical Evidence Enhancement (Week 1-2)
- [x] **PersonaViewer**: Add missing evidence columns 
- [ ] **EvidenceBrowser**: Enhance to handle all evidence types
- [ ] **PersonaInsights**: Add evidence-based insights

### Phase 2: Core Pages Enhancement (Week 3-4)
- [ ] **AuditReports**: Add detailed evidence display
- [ ] **VisualBrandHygiene**: Integrate evidence examples
- [ ] **Experience Data**: Add to all persona-focused pages

### Phase 3: Advanced Features (Week 5-6)
- [ ] **SocialMediaAnalysis**: Integrate evidence data
- [ ] **StrategicRecommendations**: Evidence-based recommendations
- [ ] **ContentMatrix**: Persona-specific evidence context

## Detailed Implementation Plans

### 1. PersonaViewer Enhancement

#### Current State
```typescript
// PersonaViewer.tsx - Evidence tab (lines 696-731)
{activeTab === 'evidence' && (
  <div className="evidence-tab">
    <h2>🔍 Evidence & Analysis</h2>
    <EvidenceBrowser
      data={auditData.filter(row => {
        const personaName = PERSONA_NAMES[selectedPersona] || selectedPersona
        return row.persona_id === personaName || row.persona_id === selectedPersona
      })}
      evidenceColumns={[
        'evidence',
        'effective_copy_examples',
        'ineffective_copy_examples',
        'trust_credibility_assessment',
        'business_impact_analysis',
        'information_gaps'
      ]}
    />
  </div>
)}
```

#### Required Enhancement
```typescript
// Enhanced PersonaViewer.tsx evidence tab
{activeTab === 'evidence' && (
  <div className="evidence-tab">
    <h2>🔍 Evidence & Analysis</h2>
    
    {/* Evidence Overview Metrics */}
    <div className="evidence-overview">
      <div className="metrics-grid">
        <div className="metric-card">
          <h4>Evidence Quality</h4>
          <div className="metric-value">
            {getEvidenceQualityScore().toFixed(1)}/10
          </div>
          <div className="metric-label">Average evidence completeness</div>
        </div>
        
        <div className="metric-card">
          <h4>Copy Examples</h4>
          <div className="metric-value">
            {getCopyExamplesCount().effective}/{getCopyExamplesCount().total}
          </div>
          <div className="metric-label">Effective copy examples found</div>
        </div>
        
        <div className="metric-card">
          <h4>Trust Signals</h4>
          <div className="metric-value">
            {getTrustSignalsCount()}
          </div>
          <div className="metric-label">Trust indicators identified</div>
        </div>
      </div>
    </div>

    {/* Enhanced Evidence Browser */}
    <EvidenceBrowser
      data={auditData.filter(row => {
        const personaName = PERSONA_NAMES[selectedPersona] || selectedPersona
        return row.persona_id === personaName || row.persona_id === selectedPersona
      })}
      evidenceColumns={[
        'evidence',
        'effective_copy_examples',
        'ineffective_copy_examples',
        'trust_credibility_assessment',
        'business_impact_analysis',
        'information_gaps',
        'first_impression',           // NEW
        'language_tone_feedback'      // NEW
      ]}
      showExperienceData={true}       // NEW
      groupByTier={true}             // NEW
      enableEvidence Export={true}    // NEW
    />
  </div>
)}
```

#### Additional Methods Needed
```typescript
// PersonaViewer.tsx - Add these methods
const getEvidenceQualityScore = () => {
  const filteredData = auditData.filter(row => {
    const personaName = PERSONA_NAMES[selectedPersona] || selectedPersona
    return row.persona_id === personaName || row.persona_id === selectedPersona
  })
  
  const evidenceColumns = [
    'evidence', 'effective_copy_examples', 'ineffective_copy_examples',
    'trust_credibility_assessment', 'business_impact_analysis', 'information_gaps',
    'first_impression', 'language_tone_feedback'
  ]
  
  let totalEvidence = 0
  let populatedEvidence = 0
  
  filteredData.forEach(row => {
    evidenceColumns.forEach(col => {
      totalEvidence++
      if (row[col] && row[col].trim().length > 0) {
        populatedEvidence++
      }
    })
  })
  
  return totalEvidence > 0 ? (populatedEvidence / totalEvidence) * 10 : 0
}

const getCopyExamplesCount = () => {
  const filteredData = auditData.filter(row => {
    const personaName = PERSONA_NAMES[selectedPersona] || selectedPersona
    return row.persona_id === personaName || row.persona_id === selectedPersona
  })
  
  let effective = 0
  let total = 0
  
  filteredData.forEach(row => {
    if (row.effective_copy_examples && row.effective_copy_examples.trim().length > 0) {
      effective++
    }
    if (row.effective_copy_examples || row.ineffective_copy_examples) {
      total++
    }
  })
  
  return { effective, total }
}

const getTrustSignalsCount = () => {
  const filteredData = auditData.filter(row => {
    const personaName = PERSONA_NAMES[selectedPersona] || selectedPersona
    return row.persona_id === personaName || row.persona_id === selectedPersona
  })
  
  return filteredData.filter(row => 
    row.trust_credibility_assessment && row.trust_credibility_assessment.trim().length > 0
  ).length
}
```

### 2. EvidenceBrowser Component Enhancement

#### Current State
```typescript
// EvidenceDisplay.tsx - EvidenceBrowser (lines 212-333)
const extractEvidenceFromRow = (row: any): EvidenceItem[] => {
  const evidence: EvidenceItem[] = [];
  
  evidenceColumns.forEach(column => {
    if (row[column] && typeof row[column] === 'string' && row[column].trim().length > 0) {
      let type: EvidenceItem['type'] = 'evidence';
      
      if (column.includes('effective_copy')) type = 'effective_copy';
      else if (column.includes('ineffective_copy')) type = 'ineffective_copy';
      else if (column.includes('trust')) type = 'trust_assessment';
      else if (column.includes('business_impact')) type = 'business_impact';
      else if (column.includes('information_gaps')) type = 'information_gaps';
      
      evidence.push({
        type,
        content: row[column].trim(),
        title: column.replace(/_/g, ' ').replace(/\b\w/g, (l: string) => l.toUpperCase())
      });
    }
  });
  
  return evidence;
};
```

#### Required Enhancement
```typescript
// Enhanced EvidenceDisplay.tsx
interface EvidenceItem {
  type: 'evidence' | 'effective_copy' | 'ineffective_copy' | 'trust_assessment' | 'business_impact' | 'information_gaps' | 'first_impression' | 'language_tone_feedback';
  content: string;
  title?: string;
  experienceData?: {
    sentiment: string;
    engagement: string;
    conversion: string;
  };
}

interface EvidenceBrowserProps {
  data: any[];
  evidenceColumns: string[];
  showExperienceData?: boolean;
  groupByTier?: boolean;
  enableEvidenceExport?: boolean;
  onEvidenceSelect?: (evidence: EvidenceItem[]) => void;
}

const extractEvidenceFromRow = (row: any, showExperienceData: boolean = false): EvidenceItem[] => {
  const evidence: EvidenceItem[] = [];
  
  evidenceColumns.forEach(column => {
    if (row[column] && typeof row[column] === 'string' && row[column].trim().length > 0) {
      let type: EvidenceItem['type'] = 'evidence';
      
      if (column.includes('effective_copy')) type = 'effective_copy';
      else if (column.includes('ineffective_copy')) type = 'ineffective_copy';
      else if (column.includes('trust')) type = 'trust_assessment';
      else if (column.includes('business_impact')) type = 'business_impact';
      else if (column.includes('information_gaps')) type = 'information_gaps';
      else if (column.includes('first_impression')) type = 'first_impression';
      else if (column.includes('language_tone_feedback')) type = 'language_tone_feedback';
      
      const item: EvidenceItem = {
        type,
        content: row[column].trim(),
        title: column.replace(/_/g, ' ').replace(/\b\w/g, (l: string) => l.toUpperCase())
      };
      
      if (showExperienceData) {
        item.experienceData = {
          sentiment: row.overall_sentiment || 'Unknown',
          engagement: row.engagement_level || 'Unknown',
          conversion: row.conversion_likelihood || 'Unknown'
        };
      }
      
      evidence.push(item);
    }
  });
  
  return evidence;
};

// Add new evidence type handlers
const getEvidenceIcon = (type: EvidenceItem['type']) => {
  switch (type) {
    case 'first_impression':
      return <EyeIcon className="w-4 h-4 text-purple-500" />;
    case 'language_tone_feedback':
      return <ChatBubbleIcon className="w-4 h-4 text-indigo-500" />;
    // ... existing cases
  }
};

const getEvidenceTypeLabel = (type: EvidenceItem['type']) => {
  switch (type) {
    case 'first_impression':
      return 'First Impression';
    case 'language_tone_feedback':
      return 'Language & Tone';
    // ... existing cases
  }
};
```

### 3. PersonaInsights Evidence Integration

#### Current State
```typescript
// PersonaInsights.tsx - Limited evidence usage
function PersonaComparisonAnalysis({ personas }: { personas: any[] }) {
  return (
    <div className="section">
      <h2>📊 Persona Performance Comparison</h2>
      {/* Only basic metrics shown */}
    </div>
  )
}
```

#### Required Enhancement
```typescript
// Enhanced PersonaInsights.tsx
import { EvidenceDisplay } from '../components/EvidenceDisplay'

function PersonaComparisonAnalysis({ personas }: { personas: any[] }) {
  const [evidenceData, setEvidenceData] = useState<any[]>([])
  
  useEffect(() => {
    // Load evidence data for all personas
    fetchEvidenceData()
  }, [])
  
  const fetchEvidenceData = async () => {
    try {
      const response = await fetch(`${apiBase}/api/audit-data`)
      if (response.ok) {
        const data = await response.json()
        setEvidenceData(data)
      }
    } catch (err) {
      console.error('Failed to fetch evidence data:', err)
    }
  }
  
  const getPersonaEvidenceInsights = (personaId: string) => {
    const personaData = evidenceData.filter(row => row.persona_id === personaId)
    
    const effectiveExamples = personaData
      .filter(row => row.effective_copy_examples && row.effective_copy_examples.trim().length > 0)
      .map(row => ({
        page: row.url_slug,
        example: row.effective_copy_examples,
        score: row.raw_score
      }))
    
    const trustSignals = personaData
      .filter(row => row.trust_credibility_assessment && row.trust_credibility_assessment.trim().length > 0)
      .map(row => ({
        page: row.url_slug,
        assessment: row.trust_credibility_assessment,
        score: row.raw_score
      }))
    
    return { effectiveExamples, trustSignals }
  }
  
  return (
    <div className="section">
      <h2>📊 Persona Performance Comparison</h2>
      
      {/* Existing persona cards */}
      <div className="metrics-grid">
        {personas.map((persona: any) => (
          <PersonaCard key={persona.persona_id} persona={persona} />
        ))}
      </div>
      
      {/* NEW: Evidence-Based Insights */}
      <div className="section">
        <h3>💡 Evidence-Based Insights</h3>
        
        <div className="evidence-insights-grid">
          {personas.map((persona: any) => {
            const insights = getPersonaEvidenceInsights(persona.persona_id)
            
            return (
              <div key={persona.persona_id} className="persona-evidence-card">
                <h4>{persona.persona_id.replace('_', ' ')}</h4>
                
                <div className="evidence-sections">
                  <div className="effective-examples">
                    <h5>✅ What Works</h5>
                    {insights.effectiveExamples.slice(0, 3).map((example, index) => (
                      <div key={index} className="example-item">
                        <strong>{example.page.replace('_', ' ')}</strong>
                        <p className="example-text">{example.example.substring(0, 150)}...</p>
                        <span className="score-badge">{example.score.toFixed(1)}/10</span>
                      </div>
                    ))}
                  </div>
                  
                  <div className="trust-signals">
                    <h5>🛡️ Trust Signals</h5>
                    {insights.trustSignals.slice(0, 2).map((signal, index) => (
                      <div key={index} className="trust-item">
                        <p className="trust-text">{signal.assessment.substring(0, 120)}...</p>
                        <span className="score-badge">{signal.score.toFixed(1)}/10</span>
                      </div>
                    ))}
                  </div>
                </div>
              </div>
            )
          })}
        </div>
      </div>
      
      {/* NEW: Cross-Persona Evidence Analysis */}
      <div className="section">
        <h3>🔍 Cross-Persona Evidence Analysis</h3>
        
        <div className="evidence-comparison">
          <div className="comparison-section">
            <h4>🏆 Best Performing Copy by Persona</h4>
            <div className="best-copy-grid">
              {personas.map((persona: any) => {
                const bestCopy = getBestCopyForPersona(persona.persona_id)
                return (
                  <div key={persona.persona_id} className="best-copy-card">
                    <h5>{persona.persona_id.replace('_', ' ')}</h5>
                    <div className="copy-example">
                      <p className="copy-text">{bestCopy.text}</p>
                      <div className="copy-meta">
                        <span className="page-name">{bestCopy.page}</span>
                        <span className="score">{bestCopy.score.toFixed(1)}/10</span>
                      </div>
                    </div>
                  </div>
                )
              })}
            </div>
          </div>
          
          <div className="comparison-section">
            <h4>⚠️ Common Issues Across Personas</h4>
            <div className="common-issues">
              {getCommonIssuesAcrossPersonas().map((issue, index) => (
                <div key={index} className="issue-item">
                  <h5>{issue.type}</h5>
                  <p>{issue.description}</p>
                  <div className="affected-personas">
                    Affects: {issue.affectedPersonas.join(', ')}
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}

// New helper methods
const getBestCopyForPersona = (personaId: string) => {
  const personaData = evidenceData.filter(row => row.persona_id === personaId)
  
  let bestCopy = {
    text: 'No effective copy found',
    page: '',
    score: 0
  }
  
  personaData.forEach(row => {
    if (row.effective_copy_examples && row.raw_score > bestCopy.score) {
      bestCopy = {
        text: row.effective_copy_examples.substring(0, 200),
        page: row.url_slug.replace('_', ' '),
        score: row.raw_score
      }
    }
  })
  
  return bestCopy
}

const getCommonIssuesAcrossPersonas = () => {
  const issuesByType = {}
  
  evidenceData.forEach(row => {
    if (row.ineffective_copy_examples) {
      // Analyze ineffective copy to identify common patterns
      const issues = analyzeIneffectiveCopy(row.ineffective_copy_examples)
      issues.forEach(issue => {
        if (!issuesByType[issue.type]) {
          issuesByType[issue.type] = {
            type: issue.type,
            description: issue.description,
            affectedPersonas: new Set()
          }
        }
        issuesByType[issue.type].affectedPersonas.add(row.persona_id)
      })
    }
  })
  
  return Object.values(issuesByType).map(issue => ({
    ...issue,
    affectedPersonas: Array.from(issue.affectedPersonas)
  }))
}
```

### 4. AuditReports Evidence Enhancement

#### Current State
```typescript
// AuditReports.tsx - Basic evidence display
// Currently shows limited evidence without detailed analysis
```

#### Required Enhancement
```typescript
// Enhanced AuditReports.tsx
import { EvidenceDisplay, EvidenceBrowser } from '../components/EvidenceDisplay'

function AuditReports() {
  const [evidenceView, setEvidenceView] = useState('summary') // 'summary' | 'detailed'
  const [selectedCriterion, setSelectedCriterion] = useState<string | null>(null)
  
  const renderEvidenceForCriterion = (criterion: string, data: any[]) => {
    const criterionData = data.filter(row => row.criterion_id === criterion)
    
    return (
      <div className="criterion-evidence">
        <h4>{criterion.replace('_', ' ').replace(/\b\w/g, l => l.toUpperCase())}</h4>
        
        <div className="evidence-summary">
          <div className="evidence-stats">
            <span>Score Range: {Math.min(...criterionData.map(r => r.raw_score)).toFixed(1)} - {Math.max(...criterionData.map(r => r.raw_score)).toFixed(1)}</span>
            <span>Pages: {criterionData.length}</span>
            <span>Evidence Items: {criterionData.filter(r => r.evidence).length}</span>
          </div>
        </div>
        
        <EvidenceBrowser
          data={criterionData}
          evidenceColumns={[
            'evidence',
            'effective_copy_examples',
            'ineffective_copy_examples',
            'trust_credibility_assessment',
            'business_impact_analysis'
          ]}
          showExperienceData={true}
          groupByTier={true}
        />
      </div>
    )
  }
  
  return (
    <div>
      {/* Existing audit reports content */}
      
      {/* NEW: Evidence Analysis Section */}
      <div className="section">
        <h2>🔍 Evidence Analysis</h2>
        
        <div className="evidence-controls">
          <div className="view-toggle">
            <button 
              className={`toggle-btn ${evidenceView === 'summary' ? 'active' : ''}`}
              onClick={() => setEvidenceView('summary')}
            >
              Summary View
            </button>
            <button 
              className={`toggle-btn ${evidenceView === 'detailed' ? 'active' : ''}`}
              onClick={() => setEvidenceView('detailed')}
            >
              Detailed Evidence
            </button>
          </div>
          
          <select 
            value={selectedCriterion || 'all'}
            onChange={(e) => setSelectedCriterion(e.target.value === 'all' ? null : e.target.value)}
          >
            <option value="all">All Criteria</option>
            <option value="brand_differentiation">Brand Differentiation</option>
            <option value="value_proposition_clarity">Value Proposition Clarity</option>
            <option value="corporate_positioning_alignment">Corporate Positioning</option>
            <option value="trust_credibility_signals">Trust & Credibility</option>
            <option value="calltoaction_effectiveness">Call-to-Action Effectiveness</option>
          </select>
        </div>
        
        {evidenceView === 'summary' ? (
          <div className="evidence-summary-grid">
            {getUniqueeCriteria().map(criterion => (
              <div key={criterion} className="criterion-card">
                <h4>{criterion.replace('_', ' ').replace(/\b\w/g, l => l.toUpperCase())}</h4>
                <div className="criterion-insights">
                  <div className="insight-item">
                    <strong>Best Example:</strong>
                    <p>{getBestExampleForCriterion(criterion)}</p>
                  </div>
                  <div className="insight-item">
                    <strong>Common Issue:</strong>
                    <p>{getCommonIssueForCriterion(criterion)}</p>
                  </div>
                </div>
              </div>
            ))}
          </div>
        ) : (
          <div className="detailed-evidence">
            {selectedCriterion ? 
              renderEvidenceForCriterion(selectedCriterion, auditData) :
              getUniqueCriteria().map(criterion => 
                renderEvidenceForCriterion(criterion, auditData)
              )
            }
          </div>
        )}
      </div>
    </div>
  )
}
```

## Next Steps

1. **Start with PersonaViewer Enhancement** - It has the best foundation and will show immediate impact
2. **Enhance EvidenceBrowser Component** - This will benefit all pages using evidence
3. **Add Evidence to PersonaInsights** - High-value enhancement for persona comparison
4. **Integrate Experience Data** - Add sentiment/engagement data across all pages
5. **Continue with remaining pages** - Following the priority matrix above

## Success Metrics

- **Evidence Coverage**: 100% of evidence columns utilized across relevant pages
- **Persona Context**: All evidence properly contextualized for specific personas
- **User Engagement**: Increased time spent on pages with rich evidence
- **Decision Support**: Better evidence-based insights for brand decisions

This implementation plan ensures that React pages will match and exceed the evidence utilization found in the Streamlit dashboard, providing comprehensive brand insights based on the rich unified CSV data. 