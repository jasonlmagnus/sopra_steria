const fs = require('fs');
const path = require('path');

// Function to extract CSS class names from CSS files
function extractCSSClasses(cssContent) {
  const classes = new Set();
  
  // Match CSS class selectors (.class-name)
  const classRegex = /\.([a-zA-Z0-9_-]+(?:--[a-zA-Z0-9_-]+)*)/g;
  let match;
  
  while ((match = classRegex.exec(cssContent)) !== null) {
    classes.add(match[1]);
  }
  
  return Array.from(classes);
}

// Function to extract class names used in React files
function extractReactClasses(reactContent) {
  const classes = new Set();
  
  // Match className patterns
  const patterns = [
    /className="([^"]+)"/g,
    /className={\`([^`]+)\`}/g,
    /className=\{([^}]+)\}/g
  ];
  
  patterns.forEach(pattern => {
    let match;
    while ((match = pattern.exec(reactContent)) !== null) {
      // Split by spaces and filter out variables/expressions
      const classNames = match[1].split(/\s+/).filter(cls => 
        cls && 
        !cls.includes('${') && 
        !cls.includes('?') && 
        !cls.includes(':') &&
        !cls.match(/^[0-9]+$/) &&
        cls !== '===' &&
        cls !== '||' &&
        cls !== '>' &&
        cls !== '<'
      );
      
      classNames.forEach(cls => classes.add(cls));
    }
  });
  
  return Array.from(classes);
}

// Function to analyze a CSS file
function analyzeCSSFile(filePath) {
  try {
    const content = fs.readFileSync(filePath, 'utf8');
    const classes = extractCSSClasses(content);
    const fileSize = fs.statSync(filePath).size;
    
    return {
      path: filePath,
      classes: classes,
      classCount: classes.length,
      fileSize: fileSize,
      lines: content.split('\n').length
    };
  } catch (error) {
    console.error(`Error reading ${filePath}:`, error.message);
    return null;
  }
}

// Function to analyze React files
function analyzeReactFiles() {
  const reactDir = 'web/src/pages';
  const usedClasses = new Set();
  
  try {
    const files = fs.readdirSync(reactDir).filter(file => file.endsWith('.tsx'));
    
    files.forEach(file => {
      const filePath = path.join(reactDir, file);
      const content = fs.readFileSync(filePath, 'utf8');
      const classes = extractReactClasses(content);
      
      classes.forEach(cls => usedClasses.add(cls));
    });
    
    return Array.from(usedClasses);
  } catch (error) {
    console.error('Error analyzing React files:', error.message);
    return [];
  }
}

// Main analysis function
function analyzeCSS() {
  console.log('🔍 CSS REDUNDANCY ANALYSIS');
  console.log('==========================\n');
  
  // Get all CSS files
  const cssFiles = [
    'web/src/styles/dashboard.css',
    'web/src/styles/utilities/elements.css',
    'web/src/styles/utilities/layout.css',
    'web/src/styles/utilities/text.css',
    'web/src/styles/utilities/spacing.css',
    'web/src/styles/utilities/combinations.css',
    'web/src/styles/utilities/colors.css',
    'web/src/styles/utilities/borders.css',
    'web/src/styles/components/voice-analysis.css',
    'web/src/styles/components/button.css',
    'web/src/styles/components/card.css',
    'web/src/styles/components/quote-display.css',
    'web/src/styles/components/slider.css',
    'web/src/styles/components/visual-brand-hygiene.css',
    'web/src/styles/components/badge.css',
    'web/src/styles/pages/ReportsExport.css',
    'web/src/styles/pages/RunAudit.css'
  ];
  
  // Analyze each CSS file
  const cssAnalysis = [];
  let totalCSSClasses = 0;
  let totalFileSize = 0;
  
  cssFiles.forEach(file => {
    if (fs.existsSync(file)) {
      const analysis = analyzeCSSFile(file);
      if (analysis) {
        cssAnalysis.push(analysis);
        totalCSSClasses += analysis.classCount;
        totalFileSize += analysis.fileSize;
      }
    }
  });
  
  // Get classes used in React files
  const usedClasses = analyzeReactFiles();
  const usedClassesSet = new Set(usedClasses);
  
  // Find orphaned classes
  const allCSSClasses = new Set();
  const orphanedClasses = [];
  
  cssAnalysis.forEach(file => {
    file.classes.forEach(cls => {
      allCSSClasses.add(cls);
      if (!usedClassesSet.has(cls)) {
        orphanedClasses.push({
          class: cls,
          file: path.basename(file.path)
        });
      }
    });
  });
  
  // Calculate redundancy
  const redundancyPercentage = (orphanedClasses.length / totalCSSClasses) * 100;
  
  console.log('📊 SUMMARY STATISTICS:');
  console.log('======================');
  console.log(`Total CSS files analyzed: ${cssAnalysis.length}`);
  console.log(`Total CSS classes defined: ${totalCSSClasses}`);
  console.log(`Total CSS file size: ${(totalFileSize / 1024).toFixed(1)} KB`);
  console.log(`Classes used in React: ${usedClasses.length}`);
  console.log(`Orphaned classes: ${orphanedClasses.length}`);
  console.log(`Redundancy percentage: ${redundancyPercentage.toFixed(1)}%`);
  
  console.log('\n📁 FILE BREAKDOWN:');
  console.log('==================');
  cssAnalysis.forEach(file => {
    const orphanedInFile = orphanedClasses.filter(o => o.file === path.basename(file.path)).length;
    const redundancyInFile = (orphanedInFile / file.classCount) * 100;
    
    console.log(`${path.basename(file.path)}:`);
    console.log(`  Classes: ${file.classCount}`);
    console.log(`  Orphaned: ${orphanedInFile} (${redundancyInFile.toFixed(1)}%)`);
    console.log(`  Size: ${(file.fileSize / 1024).toFixed(1)} KB`);
    console.log(`  Lines: ${file.lines}`);
    console.log('');
  });
  
  console.log('🗑️  TOP 50 ORPHANED CLASSES:');
  console.log('=============================');
  const orphanedByFile = {};
  orphanedClasses.forEach(o => {
    if (!orphanedByFile[o.file]) orphanedByFile[o.file] = [];
    orphanedByFile[o.file].push(o.class);
  });
  
  Object.entries(orphanedByFile).forEach(([file, classes]) => {
    console.log(`\n${file} (${classes.length} orphaned):`);
    classes.slice(0, 20).forEach(cls => {
      console.log(`  - .${cls}`);
    });
    if (classes.length > 20) {
      console.log(`  ... and ${classes.length - 20} more`);
    }
  });
  
  console.log('\n💡 CONSOLIDATION IMPACT:');
  console.log('========================');
  console.log('After consolidating React classes, we now have:');
  console.log(`- ${orphanedClasses.length} orphaned CSS rules (${redundancyPercentage.toFixed(1)}% of total)`);
  console.log(`- Potential savings: ${(totalFileSize * redundancyPercentage / 100 / 1024).toFixed(1)} KB`);
  console.log(`- Files that need cleanup: ${Object.keys(orphanedByFile).length}`);
  
  if (redundancyPercentage > 30) {
    console.log('\n🚨 HIGH REDUNDANCY DETECTED!');
    console.log('Recommendation: Clean up orphaned CSS rules to reduce bundle size.');
  } else if (redundancyPercentage > 15) {
    console.log('\n⚠️  MODERATE REDUNDANCY');
    console.log('Recommendation: Consider cleaning up major orphaned rules.');
  } else {
    console.log('\n✅ LOW REDUNDANCY');
    console.log('CSS is relatively clean after consolidation.');
  }
  
  // Save detailed report
  const report = {
    summary: {
      totalCSSFiles: cssAnalysis.length,
      totalCSSClasses: totalCSSClasses,
      totalFileSize: totalFileSize,
      usedClasses: usedClasses.length,
      orphanedClasses: orphanedClasses.length,
      redundancyPercentage: redundancyPercentage
    },
    files: cssAnalysis,
    orphanedClasses: orphanedClasses,
    usedClasses: usedClasses
  };
  
  fs.writeFileSync('refactor/scripts/css_redundancy_report.json', JSON.stringify(report, null, 2));
  console.log('\n💾 Detailed report saved to: refactor/scripts/css_redundancy_report.json');
}

// Run the analysis
analyzeCSS(); 