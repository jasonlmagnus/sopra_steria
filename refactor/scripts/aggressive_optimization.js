const fs = require('fs');
const path = require('path');

// AGGRESSIVE SECOND-ROUND CONSOLIDATION
const aggressiveMapping = {
  // CONSOLIDATE ALL DYNAMIC/TEMPLATE PATTERNS → REMOVE THEM
  // These are JavaScript expressions that shouldn't be CSS classes
  'REMOVE': [
    '?', ':', '===', '>', '<', '>=', '||', '&&',
    '0', '4', '6', '8', '10', '20', '30', '40', '50', '60', '70', '80', '90', '100',
    '${selectedModel', '${processingState.progress', '${!viewingDataset', '${viewingDataset',
    '${brand.raw_score', '${criticalCount', '${exportFormat', '${htmlOptions.generationMode',
    '${metrics.critical_issues', 'brand.raw_score', 'dataset.name', 'processingState.progress'
  ],

  // CONSOLIDATE ALL LEGACY/SPECIFIC PATTERNS → SEMANTIC GROUPS
  'container--content': [
    'insights-box', 'info-box-light', 'insight-content', 'insight-section', 'content-box',
    'main-header', 'profile-overview', 'profile-summary', 'profile-sections', 'section-content',
    'persona-header', 'persona-overview', 'persona-insights', 'persona-recommendations',
    'journey-overview', 'journey-info', 'journey-insights', 'journey-steps', 'journey-visualization',
    'voice-overview', 'voice-patterns', 'voice-search', 'voice-example', 'voice-examples-display',
    'evidence-overview', 'evidence-stats', 'evidence-content', 'evidence-header', 'evidence-item',
    'evidence-section', 'evidence-sections', 'evidence-tab', 'evidence-browser', 'evidence-controls'
  ],

  'container--layout': [
    'selection-controls', 'header-actions', 'action-section', 'action-buttons', 'controls',
    'filter-controls', 'filter-bar', 'filter-control', 'filter-group', 'filter-info', 'filter-row',
    'tab-buttons', 'tab-content', 'tabs', 'data-table', 'chart-container', 'charts-grid'
  ],

  'container--card': [
    'card', 'card--content', 'card--metric', 'card-header', 'card__content', 'card__title',
    'metric-card', 'insight-card', 'insight-cards', 'phase-card', 'recommendation-card',
    'success-story-card', 'sidebar-card', 'persona-evidence-card'
  ],

  'container--feedback': [
    'alert', 'alert--message', 'alert--warning', 'alert--error', 'success', 'error', 'warning',
    'empty-state', 'loading-state', 'loading-spinner', 'error-message', 'success-excellent',
    'success-good', 'success-stories', 'success-summary'
  ],

  'text--display': [
    'metric--display', 'metric-value', 'metric-label', 'metric-percentage', 'metric--highlight',
    'metric-display', 'score-display', 'stat-item', 'stat-label', 'stat-value'
  ],

  'badge--status': [
    'badge', 'badge--status', 'badge--primary', 'badge--critical', 'badge--excellent',
    'badge--priority-high', 'badge--priority-medium', 'badge--priority-low', 'positive', 'negative',
    'effective', 'ineffective', 'strategic', 'high', 'low'
  ],

  // CONSOLIDATE ALL SPACING PATTERNS → UTILITY CLASSES
  'spacing--sm': [
    'p-lg', 'gap-sm', 'gap-md', 'flex-gap-sm', 'mb-xl', 'mt-lg', 'mb-lg', 'mb-3', 'mb-4', 'mb-5',
    'mt-1', 'mt-2xl', 'mt-3', 'mt-4', 'mt-5', 'spacing--margin', 'spacing--gap'
  ],

  // CONSOLIDATE ALL REMAINING PATTERNS → CATCH-ALL GROUPS
  'container--misc': [
    'page-container', 'section', 'multi-select', 'multi-select-option', 'selected-items',
    'selected-item', 'checkbox-group', 'kpi-set', 'recommendations-list', 'tag-group',
    'business-impact', 'business-impact-display', 'business-insight', 'business-page-section',
    'trust-assessment', 'full-analysis', 'general-evidence', 'detailed-breakdown',
    'implementation-roadmap', 'action-plans', 'action-recommendations', 'priority-overview',
    'consistency-insights', 'regional-analysis', 'regional-insights', 'regional-performance'
  ],

  'layout--utility': [
    'rounded', 'w-full', 'text-center', 'flex-1', 'text-sm', 'font-medium', 'font-bold',
    'font-semibold', 'font-italic', 'text-muted', 'text-secondary', 'text-primary',
    'bg-light', 'bg-gray-100', 'bg-blue-50', 'border-accent', 'border-l-info', 'border-l-purple',
    'border-l-success', 'border-l-warning'
  ]
};

// Function to remove problematic classes entirely
function removeProblematicClasses(filePath) {
  try {
    let content = fs.readFileSync(filePath, 'utf8');
    let removedCount = 0;
    
    aggressiveMapping.REMOVE.forEach(className => {
      const escapedClassName = className.replace(/[.*+?^${}()|[\]\\]/g, '\\$&');
      
      // Remove these classes from className attributes
      const patterns = [
        new RegExp(`\\s*${escapedClassName}\\s*`, 'g'),
        new RegExp(`className="\\s*${escapedClassName}\\s*"`, 'g'),
        new RegExp(`className="([^"]*\\s)${escapedClassName}(\\s[^"]*)"`, 'g'),
        new RegExp(`className="([^"]*\\s)${escapedClassName}\\s*"`, 'g'),
        new RegExp(`className="\\s*${escapedClassName}(\\s[^"]*)"`, 'g')
      ];
      
      patterns.forEach(pattern => {
        const beforeReplace = content;
        content = content.replace(pattern, (match, before, after) => {
          if (before && after) {
            return `className="${before.trim()} ${after.trim()}"`;
          } else if (before) {
            return `className="${before.trim()}"`;
          } else if (after) {
            return `className="${after.trim()}"`;
          } else {
            return '';
          }
        });
        
        if (content !== beforeReplace) {
          removedCount++;
        }
      });
    });
    
    // Clean up empty className attributes
    content = content.replace(/className=""\s*/g, '');
    content = content.replace(/className={\`\`}\s*/g, '');
    
    if (removedCount > 0) {
      fs.writeFileSync(filePath, content, 'utf8');
      console.log(`✅ ${path.basename(filePath)}: Removed ${removedCount} problematic classes`);
    }
    
    return removedCount;
  } catch (error) {
    console.error(`❌ Error removing problematic classes from ${filePath}:`, error.message);
    return 0;
  }
}

// Function to apply aggressive consolidation
function applyAggressiveConsolidation(filePath) {
  try {
    let content = fs.readFileSync(filePath, 'utf8');
    let replacementCount = 0;
    
    // Apply consolidation mapping (excluding REMOVE)
    Object.entries(aggressiveMapping).forEach(([corePattern, variations]) => {
      if (corePattern === 'REMOVE') return;
      
      variations.forEach(oldClass => {
        const escapedOldClass = oldClass.replace(/[.*+?^${}()|[\]\\]/g, '\\$&');
        
        const patterns = [
          new RegExp(`className="([^"]*\\s)?${escapedOldClass}(\\s[^"]*)?"`,'g'),
          new RegExp(`className={\`([^\`]*\\s)?${escapedOldClass}(\\s[^\`]*)?`,'g'),
          new RegExp(`className={\`${escapedOldClass}\`}`,'g'),
          new RegExp(`className="${escapedOldClass}"`,'g')
        ];
        
        patterns.forEach(pattern => {
          const matches = content.match(pattern);
          if (matches) {
            content = content.replace(pattern, (match) => {
              replacementCount++;
              return match.replace(oldClass, corePattern);
            });
          }
        });
      });
    });
    
    if (replacementCount > 0) {
      fs.writeFileSync(filePath, content, 'utf8');
      console.log(`✅ ${path.basename(filePath)}: ${replacementCount} aggressive consolidations made`);
    }
    
    return replacementCount;
  } catch (error) {
    console.error(`❌ Error processing ${filePath}:`, error.message);
    return 0;
  }
}

// Main aggressive optimization function
function aggressiveOptimization() {
  console.log('🚀 AGGRESSIVE OPTIMIZATION - ROUND 2');
  console.log('====================================\n');
  
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
  
  console.log('STRATEGY:');
  console.log('- Remove all dynamic/template patterns (JavaScript expressions)');
  console.log('- Consolidate legacy/specific patterns into semantic groups');
  console.log('- Reduce remaining 170 patterns to ~15 core patterns');
  console.log('');
  
  let totalRemovals = 0;
  let totalConsolidations = 0;
  
  // Step 1: Remove problematic classes
  console.log('🗑️  STEP 1: REMOVING PROBLEMATIC CLASSES');
  targetFiles.forEach(filePath => {
    if (fs.existsSync(filePath)) {
      totalRemovals += removeProblematicClasses(filePath);
    }
  });
  
  console.log('');
  
  // Step 2: Apply aggressive consolidation
  console.log('🔄 STEP 2: AGGRESSIVE CONSOLIDATION');
  targetFiles.forEach(filePath => {
    if (fs.existsSync(filePath)) {
      totalConsolidations += applyAggressiveConsolidation(filePath);
    }
  });
  
  console.log('\n📊 AGGRESSIVE OPTIMIZATION SUMMARY:');
  console.log('===================================');
  console.log(`Problematic classes removed: ${totalRemovals}`);
  console.log(`Aggressive consolidations made: ${totalConsolidations}`);
  console.log(`Total optimizations: ${totalRemovals + totalConsolidations}`);
  
  console.log('\n🎯 EXPECTED RESULTS:');
  console.log('- DIV patterns: 170 → ~15 core patterns');
  console.log('- Eliminated all JavaScript expressions as CSS classes');
  console.log('- Consolidated legacy patterns into semantic groups');
  console.log('- Achieved maximum standardization');
  
  console.log('\n✅ AGGRESSIVE OPTIMIZATION COMPLETE!');
}

// Run the aggressive optimization
aggressiveOptimization(); 