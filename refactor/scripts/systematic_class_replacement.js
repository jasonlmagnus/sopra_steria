const fs = require('fs');
const path = require('path');

// Define the mapping from specialized classes to standardized utility classes
const classReplacements = {
  // Hero section patterns
  'hero-content': 'container--hero',
  'hero-icon': 'icon--hero',
  'hero-stats': 'container--stats',
  'stat-item': 'container--stat',
  
  // Warning/Alert patterns
  'warning-content': 'container--warning',
  'warning-icon': 'icon--warning',
  'warning-text': 'container--warning-text',
  'success-icon': 'icon--success',
  'success-content': 'container--success',
  
  // Process patterns
  'process-number': 'number--process',
  'process-content': 'container--process',
  
  // File upload patterns
  'file-upload-area': 'container--upload',
  'upload-icon': 'icon--upload',
  'upload-text': 'container--upload-text',
  'file-upload-label': 'label--upload',
  'file-input': 'input--file',
  
  // Model selection patterns
  'model-options': 'container--options',
  'model-option': 'container--option',
  'model-icon': 'icon--model',
  'model-content': 'container--option-content',
  'model-features': 'container--features',
  'model-label': 'label--option',
  
  // URL input patterns
  'url-input-container': 'container--input',
  'url-tabs': 'container--tabs',
  'url-input-content': 'container--input-content',
  'url-paste-section': 'container--paste',
  'url-help': 'container--help',
  'url-upload-section': 'container--upload-section',
  'url-validation': 'container--validation',
  'validation-grid': 'container--validation-grid',
  'invalid-urls': 'container--invalid',
  'url-tab': 'button--tab',
  'url-textarea': 'textarea--input',
  'help-icon': 'icon--help',
  
  // Launch patterns
  'launch-section': 'container--launch',
  'launch-summary': 'container--summary',
  'summary-items': 'container--summary-items',
  'summary-item': 'container--summary-item',
  'launch-icon': 'icon--launch',
  'launch-text': 'container--launch-text',
  'launch-button': 'button--launch',
  'launch-title': 'text--launch-title',
  'launch-subtitle': 'text--launch-subtitle',
  'summary-label': 'text--summary-label',
  'summary-value': 'text--summary-value',
  
  // Progress patterns
  'audit-progress': 'container--progress',
  'progress-header': 'container--progress-header',
  'progress-meta': 'container--progress-meta',
  'progress-visualization': 'container--progress-viz',
  'progress-circle': 'container--progress-circle',
  'progress-text': 'container--progress-text',
  'progress-details': 'container--progress-details',
  'progress-status': 'container--progress-status',
  'status-icon': 'icon--status',
  'status-text': 'text--status',
  'progress-stats': 'container--progress-stats',
  'stat': 'container--stat',
  'progress-percentage': 'text--percentage',
  'progress-label': 'text--progress-label',
  'stat-label': 'text--stat-label',
  'stat-value': 'text--stat-value',
  
  // Audit log patterns
  'audit-log': 'container--log',
  'log-header': 'container--log-header',
  'log-controls': 'container--log-controls',
  'log-container': 'container--log-content',
  'log-line': 'container--log-line',
  'log-empty': 'container--log-empty',
  'log-status': 'text--log-status',
  
  // Post-audit patterns
  'post-audit': 'container--post-audit',
  'completion-celebration': 'container--celebration',
  'celebration-animation': 'container--animation',
  'next-steps-container': 'container--next-steps',
  'next-steps-info': 'container--next-steps-info',
  'steps-grid': 'container--steps-grid',
  'step-card': 'container--step',
  'step-icon': 'icon--step',
  'step-content': 'container--step-content',
  
  // Processing patterns
  'processing-status': 'container--processing',
  'status-card': 'container--status',
  'status-success': 'container--status-success',
  'status-pending': 'container--status-pending',
  'action-section': 'container--actions',
  'button-icon': 'icon--button',
  'button-content': 'container--button-content',
  'completion-actions': 'container--completion-actions',
  'processing-progress': 'container--processing-progress',
  'processing-header': 'container--processing-header',
  'processing-visualization': 'container--processing-viz',
  'processing-steps': 'container--processing-steps',
  'step-number': 'number--step',
  'step-label': 'text--step-label',
  'processing-bar': 'container--processing-bar',
  'processing-fill': 'container--processing-fill',
  'status-message': 'text--status-message',
  'status-percentage': 'text--status-percentage',
  'button-title': 'text--button-title',
  'button-subtitle': 'text--button-subtitle',
  
  // Section-specific patterns
  'persona-section': 'container--section',
  'model-section': 'container--section',
  'urls-section': 'container--section',
  
  // Navigation patterns
  'nav-button': 'button--nav',
  
  // Validation patterns
  'validation-title': 'heading--validation',
  
  // Generic specialized patterns that should be standardized
  'upload': 'container--upload',
  'model': 'container--model',
  'urls': 'container--urls',
  'analysis': 'container--analysis',
  'cost': 'badge--cost',
  'speed': 'badge--speed',
  'quality': 'badge--quality',
  'premium': 'badge--premium',
  'deep': 'badge--deep',
  'secondary': 'button--secondary',
  'primary': 'button--primary',
  'step': 'container--step'
};

// Function to replace classes in a file
function replaceClassesInFile(filePath) {
  try {
    let content = fs.readFileSync(filePath, 'utf8');
    let replacementCount = 0;
    
    // Replace each specialized class with its standardized equivalent
    for (const [oldClass, newClass] of Object.entries(classReplacements)) {
      // Match className="old-class" or className={`old-class ${...}`} patterns
      const patterns = [
        new RegExp(`className="([^"]*\\s)?${oldClass}(\\s[^"]*)?"`,'g'),
        new RegExp(`className={\`([^\`]*\\s)?${oldClass}(\\s[^\`]*)?`,'g'),
        new RegExp(`className={\`${oldClass}\`}`,'g'),
        new RegExp(`className="${oldClass}"`,'g')
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
    }
    
    // Write the updated content back to the file
    if (replacementCount > 0) {
      fs.writeFileSync(filePath, content, 'utf8');
      console.log(`✅ ${path.basename(filePath)}: ${replacementCount} class replacements made`);
    } else {
      console.log(`⚪ ${path.basename(filePath)}: No replacements needed`);
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
  'web/src/pages/Methodology.tsx'
];

console.log('🔄 Starting systematic class replacement...\n');

let totalReplacements = 0;
const processedFiles = [];

targetFiles.forEach(filePath => {
  if (fs.existsSync(filePath)) {
    const replacements = replaceClassesInFile(filePath);
    totalReplacements += replacements;
    processedFiles.push({ file: path.basename(filePath), replacements });
  } else {
    console.log(`⚠️  File not found: ${filePath}`);
  }
});

console.log('\n📊 REPLACEMENT SUMMARY:');
console.log('======================');
processedFiles.forEach(({ file, replacements }) => {
  console.log(`${file}: ${replacements} replacements`);
});
console.log(`\n🎯 Total replacements made: ${totalReplacements}`);
console.log('\n✅ Systematic class replacement complete!'); 