const fs = require('fs');
const path = require('path');

// Configuration
const PAGES_DIR = '../../web/src/pages';
const OUTPUT_FILE = 'element_patterns_analysis.json';

// Element types to analyze
const ELEMENT_TYPES = ['div', 'span', 'p', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'button', 'label', 'input', 'select'];

function extractElementClasses(content) {
  const patterns = {};
  
  ELEMENT_TYPES.forEach(elementType => {
    patterns[elementType] = new Set();
    
    // Match JSX elements with className
    const regex = new RegExp(`<${elementType}[^>]*className=["']([^"']+)["'][^>]*>`, 'g');
    let match;
    
    while ((match = regex.exec(content)) !== null) {
      const classes = match[1].split(' ').filter(cls => cls.trim());
      classes.forEach(cls => patterns[elementType].add(cls));
    }
    
    // Also match elements with multiple className patterns
    const multiClassRegex = new RegExp(`<${elementType}[^>]*className=\\{[^}]+\\}[^>]*>`, 'g');
    while ((match = multiClassRegex.exec(content)) !== null) {
      // Extract class names from template literals or concatenations
      const classMatch = match[0].match(/className=\{([^}]+)\}/);
      if (classMatch) {
        const classContent = classMatch[1];
        // Look for string literals, template literals, or concatenations
        const stringMatches = classContent.match(/['"`]([^'"`]+)['"`]/g);
        if (stringMatches) {
          stringMatches.forEach(str => {
            const cleanStr = str.replace(/['"`]/g, '');
            const classes = cleanStr.split(' ').filter(cls => cls.trim());
            classes.forEach(cls => patterns[elementType].add(cls));
          });
        }
      }
    }
  });
  
  return patterns;
}

function analyzePages() {
  const pagesDir = path.resolve(__dirname, PAGES_DIR);
  const files = fs.readdirSync(pagesDir).filter(file => file.endsWith('.tsx'));
  
  const analysis = {
    summary: {
      totalFiles: files.length,
      totalElementClasses: 0,
      elementTypeBreakdown: {}
    },
    files: {},
    patterns: {}
  };
  
  // Initialize patterns for each element type
  ELEMENT_TYPES.forEach(type => {
    analysis.patterns[type] = new Set();
    analysis.summary.elementTypeBreakdown[type] = 0;
  });
  
  files.forEach(file => {
    const filePath = path.join(pagesDir, file);
    const content = fs.readFileSync(filePath, 'utf8');
    const filePatterns = extractElementClasses(content);
    
    analysis.files[file] = {
      elementCounts: {},
      classes: {}
    };
    
    ELEMENT_TYPES.forEach(type => {
      const classes = Array.from(filePatterns[type]);
      analysis.files[file].elementCounts[type] = classes.length;
      analysis.files[file].classes[type] = classes;
      
      // Add to global patterns
      classes.forEach(cls => analysis.patterns[type].add(cls));
      analysis.summary.elementTypeBreakdown[type] += classes.length;
      analysis.summary.totalElementClasses += classes.length;
    });
  });
  
  // Convert sets to arrays for JSON serialization
  ELEMENT_TYPES.forEach(type => {
    analysis.patterns[type] = Array.from(analysis.patterns[type]).sort();
  });
  
  return analysis;
}

function generateReport(analysis) {
  console.log('🔍 ELEMENT PATTERN ANALYSIS REPORT');
  console.log('=====================================\n');
  
  console.log('📊 SUMMARY:');
  console.log(`• Total Files Analyzed: ${analysis.summary.totalFiles}`);
  console.log(`• Total Element Classes: ${analysis.summary.totalElementClasses}\n`);
  
  console.log('📋 ELEMENT TYPE BREAKDOWN:');
  ELEMENT_TYPES.forEach(type => {
    const count = analysis.summary.elementTypeBreakdown[type];
    const uniqueCount = analysis.patterns[type].length;
    console.log(`• ${type.toUpperCase()}: ${count} total classes, ${uniqueCount} unique patterns`);
  });
  
  console.log('\n🎯 TOP ELEMENT TYPES BY CLASS COUNT:');
  const sortedTypes = ELEMENT_TYPES.sort((a, b) => 
    analysis.summary.elementTypeBreakdown[b] - analysis.summary.elementTypeBreakdown[a]
  );
  
  sortedTypes.slice(0, 5).forEach(type => {
    const count = analysis.summary.elementTypeBreakdown[type];
    const uniqueCount = analysis.patterns[type].length;
    console.log(`• ${type.toUpperCase()}: ${count} classes (${uniqueCount} unique)`);
  });
  
  console.log('\n📁 FILE BREAKDOWN:');
  Object.entries(analysis.files).forEach(([file, data]) => {
    const totalClasses = Object.values(data.elementCounts).reduce((sum, count) => sum + count, 0);
    console.log(`• ${file}: ${totalClasses} total element classes`);
  });
  
  console.log('\n🔧 RECOMMENDED STANDARDIZATION:');
  console.log('Based on the analysis, here are the recommended core patterns:');
  
  ELEMENT_TYPES.forEach(type => {
    const uniqueCount = analysis.patterns[type].length;
    if (uniqueCount > 5) {
      const targetCount = Math.min(20, Math.ceil(uniqueCount * 0.1));
      console.log(`• ${type.toUpperCase()}: ${uniqueCount} → ${targetCount} core patterns`);
    }
  });
  
  return analysis;
}

// Main execution
try {
  console.log('🔍 Starting element pattern analysis...\n');
  
  const analysis = analyzePages();
  const report = generateReport(analysis);
  
  // Save detailed analysis to JSON
  const outputPath = path.join(__dirname, OUTPUT_FILE);
  fs.writeFileSync(outputPath, JSON.stringify(report, null, 2));
  
  console.log(`\n💾 Detailed analysis saved to: ${OUTPUT_FILE}`);
  console.log('\n✅ Analysis complete!');
  
} catch (error) {
  console.error('❌ Error during analysis:', error.message);
  process.exit(1);
} 