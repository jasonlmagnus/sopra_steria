const fs = require('fs');
const path = require('path');

// CONSOLIDATION MAPPING: Map all variations to core patterns
const consolidationMapping = {
  // CONTAINERS (84 classes → 8 core patterns)
  'container--content': [
    'chart-container', 'container--content', 'container--input-content', 'container--option-content',
    'container--button-content', 'container--launch-text', 'container--upload-text', 'container--warning-text',
    'container--step-content', 'container--next-steps-info', 'page-container', 'content-box', 'section-content'
  ],
  'container--section': [
    'container--section', 'container--header', 'container--insight', 'container--metric', 'container--stats',
    'container--summary', 'container--features', 'container--help', 'container--validation', 'section'
  ],
  'container--card': [
    'container--card', 'container--option', 'container--stat', 'container--status', 'container--step',
    'container--summary-item', 'container--processing', 'container--progress', 'container--log'
  ],
  'container--layout': [
    'container--page', 'container--grid', 'container--flex', 'container--flex-between', 'container--flex-end',
    'container--flex-gap-sm', 'container--tabs', 'container--padding', 'container--overflow'
  ],
  'container--form': [
    'container--input', 'container--upload', 'container--paste', 'container--options', 'container--validation-grid',
    'container--upload-section', 'container--invalid'
  ],
  'container--feedback': [
    'container--alert', 'container--warning', 'container--success', 'container--loading', 'container--celebration',
    'container--animation', 'container--post-audit'
  ],
  'container--workflow': [
    'container--process', 'container--launch', 'container--progress-header', 'container--progress-meta',
    'container--progress-viz', 'container--progress-circle', 'container--progress-text', 'container--progress-details',
    'container--progress-status', 'container--progress-stats', 'container--processing-header', 'container--processing-progress',
    'container--processing-steps', 'container--processing-viz', 'container--processing-bar', 'container--processing-fill'
  ],
  'container--actions': [
    'container--actions', 'container--completion-actions', 'container--log-controls', 'container--next-steps',
    'container--steps-grid', 'container--summary-items'
  ],

  // GRIDS (13 classes → 1 core pattern)
  'container--grid': [
    'grid', 'grid--auto-200', 'grid--cols-2', 'grid--cols-3', 'grid--cols-4', 'charts-grid',
    'evidence-grid', 'executive-summary-grid', 'insights-grid', 'metrics-grid', 'patterns-grid',
    'persona-evidence-grid', 'grid-gap-2xl'
  ],

  // SPACING (15 classes → 2 core patterns)
  'spacing--margin': [
    'mb-2', 'mb-3', 'mb-4', 'mb-5', 'mb-lg', 'mb-xl', 'mt-1', 'mt-2xl', 'mt-3', 'mt-4', 'mt-5', 'mt-lg'
  ],
  'spacing--gap': [
    'gap-sm', 'gap-md', 'flex-gap-sm'
  ],

  // TEXT (24 classes → 3 core patterns)
  'text--body': [
    'text--body', 'text--body-secondary', 'text--body-small', 'text--caption', 'text-sm', 'text-muted',
    'text-secondary', 'text-primary'
  ],
  'text--emphasis': [
    'font-bold', 'font-medium', 'font-semibold', 'font-italic'
  ],
  'text--display': [
    'text--metric', 'text--label', 'text--status', 'text--status-message', 'text--status-percentage',
    'text--step-label', 'text--badge', 'text--center', 'text-center', 'text-blue-600'
  ],

  // BADGES (9 classes → 1 core pattern)
  'badge--status': [
    'badge', 'badge--primary', 'badge--critical', 'badge--excellent', 'badge--priority-high',
    'badge--priority-medium', 'badge--priority-low', 'badge--${insight.Type', 'badge--${platform.Status_Color'
  ],

  // CARDS (15 classes → 1 core pattern)
  'card--content': [
    'card', 'card--content', 'card--metric', 'card-header', 'card__content', 'card__title',
    'evidence-card', 'insight-card', 'insight-cards', 'metric-card', 'persona-evidence-card',
    'phase-card', 'recommendation-card', 'sidebar-card', 'success-story-card'
  ],

  // BUTTONS (4 classes → 1 core pattern)
  'button--action': [
    'action-buttons', 'button--primary', 'icon--button', 'tab-buttons'
  ],

  // ALERTS (17 classes → 1 core pattern)
  'alert--message': [
    'alert', 'alert--error', 'alert--warning', 'bg-error-light', 'bg-success-light', 'border-l-success',
    'border-l-warning', 'error', 'error-message', 'icon--success', 'icon--warning', 'success',
    'success-excellent', 'success-good', 'success-stories', 'success-summary', 'warning'
  ],

  // METRICS (7 classes → 1 core pattern)
  'metric--display': [
    'metric-value', 'metric-label', 'metric-percentage', 'metric--highlight', 'metric-display',
    '${metrics.critical_issues', 'insight-metric'
  ],

  // EVIDENCE (17 classes → 1 core pattern)
  'evidence--content': [
    'evidence-content', 'evidence-header', 'evidence-item', 'evidence-section', 'evidence-sections',
    'evidence-tab', 'evidence-browser', 'evidence-controls', 'evidence-examples', 'evidence-overview',
    'evidence-samples', 'evidence-score', 'evidence-stats', 'brand-evidence-examples', 'general-evidence',
    'no-evidence', 'story-evidence'
  ],

  // PERSONAS (10 classes → 1 core pattern)
  'persona--content': [
    'persona-selection', 'persona-overview', 'persona-header', 'persona-insights', 'persona-recommendations',
    'persona-count', 'persona-filter', 'persona-quote', 'persona-quotes', 'persona-reaction'
  ],

  // TABS (12 classes → 1 core pattern)
  'tab--interface': [
    'tabs', 'tab-content', 'criteria-tab', 'journey-tab', 'performance-tab', 'priority-tab',
    'profile-tab', 'regional-tab', 'standards-tab', 'tier-tab', 'voice-tab', 'data-table'
  ],

  // FILTERS (7 classes → 1 core pattern)
  'filter--controls': [
    'filter-controls', 'filter-bar', 'filter-control', 'filter-group', 'filter-info', 'filter-row', 'voice-filters'
  ],

  // LOADING (2 classes → 1 core pattern)
  'loading--state': [
    'loading-spinner', 'loading-state'
  ],

  // JOURNEY (9 classes → 1 core pattern)
  'journey--flow': [
    'journey-overview', 'journey-info', 'journey-insights', 'journey-steps', 'journey-visualization',
    'step-header', 'step-details', 'icon--step', 'number--step'
  ],

  // VOICE (14 classes → 1 core pattern)
  'voice--analysis': [
    'voice-overview', 'voice-patterns', 'voice-search', 'voice-example', 'voice-examples-display',
    'voice-page-section', 'voice-analysis-section', 'voice-fallback', 'copy-ready-quotes',
    'quote-controls', 'quote-item', 'quotes-list', 'example-quote', 'example-with-quote'
  ],

  // COLORS (4 classes → utility classes - keep as is)
  'bg-light': ['bg-blue-50', 'bg-gray-100'],
  'border-accent': ['border-l-info', 'border-l-purple'],

  // ICONS (consolidated from various icon-- patterns)
  'icon--ui': [
    'icon--hero', 'icon--launch', 'icon--model', 'icon--status', 'icon--upload', 'icon--success', 'icon--warning'
  ],

  // NUMBERS (consolidated from various number-- patterns)
  'number--display': [
    'number--process', 'number--step'
  ]
};

// Function to create replacement mapping
function createReplacementMapping() {
  const replacements = {};
  
  Object.entries(consolidationMapping).forEach(([corePattern, variations]) => {
    variations.forEach(variation => {
      replacements[variation] = corePattern;
    });
  });
  
  return replacements;
}

// Function to apply consolidation to files
function consolidateClasses(filePath) {
  try {
    let content = fs.readFileSync(filePath, 'utf8');
    const replacements = createReplacementMapping();
    let replacementCount = 0;
    
    // Replace each variation with its core pattern
    Object.entries(replacements).forEach(([oldClass, newClass]) => {
      // Skip if it's already a core pattern
      if (oldClass === newClass) return;
      
      // Match className patterns
      const patterns = [
        new RegExp(`className="([^"]*\\s)?${oldClass.replace(/[.*+?^${}()|[\]\\]/g, '\\$&')}(\\s[^"]*)?"`,'g'),
        new RegExp(`className={\`([^\`]*\\s)?${oldClass.replace(/[.*+?^${}()|[\]\\]/g, '\\$&')}(\\s[^\`]*)?`,'g'),
        new RegExp(`className={\`${oldClass.replace(/[.*+?^${}()|[\]\\]/g, '\\$&')}\`}`,'g'),
        new RegExp(`className="${oldClass.replace(/[.*+?^${}()|[\]\\]/g, '\\$&')}"`,'g')
      ];
      
      patterns.forEach(pattern => {
        const matches = content.match(pattern);
        if (matches) {
          content = content.replace(pattern, (match) => {
            replacementCount++;
            return match.replace(oldClass, newClass);
          });
        }
      });
    });
    
    // Write the updated content back to the file
    if (replacementCount > 0) {
      fs.writeFileSync(filePath, content, 'utf8');
      console.log(`✅ ${path.basename(filePath)}: ${replacementCount} consolidations made`);
    } else {
      console.log(`⚪ ${path.basename(filePath)}: No consolidations needed`);
    }
    
    return replacementCount;
  } catch (error) {
    console.error(`❌ Error processing ${filePath}:`, error.message);
    return 0;
  }
}

// Main execution
const targetFiles = [
  'web/src/pages/RunAudit.tsx',
  'web/src/pages/PersonaViewer.tsx',
  'web/src/pages/SocialMediaAnalysis.tsx',
  'web/src/pages/VisualBrandHygiene.tsx',
  'web/src/pages/ContentMatrix.tsx',
  'web/src/pages/StrategicRecommendations.tsx',
  'web/src/pages/SuccessLibrary.tsx',
  'web/src/pages/ReportsExport.tsx',
  'web/src/pages/ExecutiveDashboard.tsx',
  'web/src/pages/OpportunityImpact.tsx',
  'web/src/pages/AuditReports.tsx',
  'web/src/pages/Methodology.tsx',
  'web/src/pages/PersonaInsights.tsx'
];

console.log('🔄 Starting class consolidation...\n');
console.log('CONSOLIDATION STRATEGY:');
console.log('======================');

const corePatterns = Object.keys(consolidationMapping);
console.log(`Consolidating ${Object.values(consolidationMapping).flat().length} classes into ${corePatterns.length} core patterns:`);
corePatterns.forEach((pattern, index) => {
  console.log(`${index + 1}. ${pattern}`);
});

console.log('\n🎯 PROCESSING FILES:\n');

let totalConsolidations = 0;
const processedFiles = [];

targetFiles.forEach(filePath => {
  if (fs.existsSync(filePath)) {
    const consolidations = consolidateClasses(filePath);
    totalConsolidations += consolidations;
    processedFiles.push({ file: path.basename(filePath), consolidations });
  } else {
    console.log(`⚠️  File not found: ${filePath}`);
  }
});

console.log('\n📊 CONSOLIDATION SUMMARY:');
console.log('=========================');
processedFiles.forEach(({ file, consolidations }) => {
  console.log(`${file}: ${consolidations} consolidations`);
});
console.log(`\n🎯 Total consolidations made: ${totalConsolidations}`);
console.log(`\n✅ Class consolidation complete!`);
console.log(`\nExpected result: Reduced from 400 unique patterns to ~${corePatterns.length} core patterns`); 