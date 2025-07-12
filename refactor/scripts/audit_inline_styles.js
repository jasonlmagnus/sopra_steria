#!/usr/bin/env node

const fs = require('fs');
const path = require('path');

// ANSI color codes for better output
const colors = {
  red: '\x1b[31m',
  green: '\x1b[32m',
  yellow: '\x1b[33m',
  blue: '\x1b[34m',
  magenta: '\x1b[35m',
  cyan: '\x1b[36m',
  white: '\x1b[37m',
  reset: '\x1b[0m',
  bold: '\x1b[1m'
};

function countInlineStyles(content) {
  // Match style={{...}} patterns
  const inlineStyleRegex = /style=\{\{[^}]*\}\}/g;
  const matches = content.match(inlineStyleRegex) || [];
  return matches.length;
}

function countCSSClasses(content) {
  // Match className="..." patterns
  const classNameRegex = /className="[^"]*"/g;
  const matches = content.match(classNameRegex) || [];
  return matches.length;
}

function extractUniqueClasses(content) {
  // Extract unique class names
  const classNameRegex = /className="([^"]*)"/g;
  const classes = new Set();
  let match;
  
  while ((match = classNameRegex.exec(content)) !== null) {
    const classList = match[1].split(' ').filter(c => c.trim());
    classList.forEach(c => classes.add(c.trim()));
  }
  
  return Array.from(classes);
}

function getFileSize(filePath) {
  const stats = fs.statSync(filePath);
  return (stats.size / 1024).toFixed(1); // KB
}

function getLineCount(content) {
  return content.split('\n').length;
}

function auditPage(filePath) {
  const content = fs.readFileSync(filePath, 'utf8');
  const fileName = path.basename(filePath);
  
  const inlineStyles = countInlineStyles(content);
  const cssClasses = countCSSClasses(content);
  const uniqueClasses = extractUniqueClasses(content);
  const fileSize = getFileSize(filePath);
  const lineCount = getLineCount(content);
  
  const total = inlineStyles + cssClasses;
  const inlinePercentage = total > 0 ? ((inlineStyles / total) * 100).toFixed(1) : 0;
  const cssPercentage = total > 0 ? ((cssClasses / total) * 100).toFixed(1) : 0;
  
  // Determine severity
  let severity = 'GOOD';
  let severityColor = colors.green;
  
  if (inlinePercentage > 70) {
    severity = 'CRITICAL';
    severityColor = colors.red;
  } else if (inlinePercentage > 50) {
    severity = 'BAD';
    severityColor = colors.yellow;
  } else if (inlinePercentage > 30) {
    severity = 'WARNING';
    severityColor = colors.yellow;
  }
  
  return {
    fileName,
    filePath,
    inlineStyles,
    cssClasses,
    uniqueClasses,
    total,
    inlinePercentage: parseFloat(inlinePercentage),
    cssPercentage: parseFloat(cssPercentage),
    severity,
    severityColor,
    fileSize,
    lineCount
  };
}

function generateReport() {
  const pagesDir = path.join(__dirname, '..', '..', 'web', 'src', 'pages');
  
  if (!fs.existsSync(pagesDir)) {
    console.error(`${colors.red}ERROR: Pages directory not found at ${pagesDir}${colors.reset}`);
    return;
  }
  
  const files = fs.readdirSync(pagesDir)
    .filter(file => file.endsWith('.tsx'))
    .map(file => path.join(pagesDir, file));
  
  if (files.length === 0) {
    console.error(`${colors.red}ERROR: No .tsx files found in ${pagesDir}${colors.reset}`);
    return;
  }
  
  const results = files.map(auditPage);
  
  // Sort by inline percentage (worst first)
  results.sort((a, b) => b.inlinePercentage - a.inlinePercentage);
  
  console.log(`${colors.bold}${colors.cyan}
╔══════════════════════════════════════════════════════════════════════════════════════╗
║                           🚨 INLINE STYLES AUDIT REPORT 🚨                          ║
╚══════════════════════════════════════════════════════════════════════════════════════╝${colors.reset}

${colors.bold}📊 SUMMARY:${colors.reset}
• Total Pages Analyzed: ${colors.bold}${results.length}${colors.reset}
• Total Inline Styles: ${colors.bold}${results.reduce((sum, r) => sum + r.inlineStyles, 0)}${colors.reset}
• Total CSS Classes: ${colors.bold}${results.reduce((sum, r) => sum + r.cssClasses, 0)}${colors.reset}
• Average Inline %: ${colors.bold}${(results.reduce((sum, r) => sum + r.inlinePercentage, 0) / results.length).toFixed(1)}%${colors.reset}

${colors.bold}🔥 SEVERITY BREAKDOWN:${colors.reset}`);

  const severityCounts = results.reduce((acc, r) => {
    acc[r.severity] = (acc[r.severity] || 0) + 1;
    return acc;
  }, {});

  Object.entries(severityCounts).forEach(([severity, count]) => {
    const color = severity === 'CRITICAL' ? colors.red : 
                  severity === 'BAD' ? colors.yellow :
                  severity === 'WARNING' ? colors.yellow : colors.green;
    console.log(`• ${color}${severity}: ${count} pages${colors.reset}`);
  });

  console.log(`\n${colors.bold}📋 DETAILED BREAKDOWN:${colors.reset}`);
  console.log('─'.repeat(120));
  console.log(`${colors.bold}FILE NAME${' '.repeat(35)}│ SIZE  │ LINES │ INLINE │ CSS   │ INLINE% │ STATUS${colors.reset}`);
  console.log('─'.repeat(120));
  
  results.forEach(result => {
    const nameCol = result.fileName.padEnd(40);
    const sizeCol = `${result.fileSize}KB`.padEnd(6);
    const linesCol = result.lineCount.toString().padEnd(6);
    const inlineCol = result.inlineStyles.toString().padEnd(7);
    const cssCol = result.cssClasses.toString().padEnd(6);
    const percentCol = `${result.inlinePercentage}%`.padEnd(8);
    
    console.log(`${nameCol}│ ${sizeCol}│ ${linesCol}│ ${inlineCol}│ ${cssCol}│ ${percentCol}│ ${result.severityColor}${result.severity}${colors.reset}`);
  });
  
  console.log('─'.repeat(120));
  
  // Top offenders
  console.log(`\n${colors.bold}🚨 TOP 5 WORST OFFENDERS:${colors.reset}`);
  results.slice(0, 5).forEach((result, index) => {
    console.log(`${colors.bold}${index + 1}. ${result.fileName}${colors.reset}`);
    console.log(`   └── ${colors.red}${result.inlineStyles} inline styles${colors.reset} (${result.inlinePercentage}%) vs ${colors.green}${result.cssClasses} CSS classes${colors.reset} (${result.cssPercentage}%)`);
    console.log(`   └── File size: ${result.fileSize}KB, ${result.lineCount} lines`);
    console.log(`   └── Unique CSS classes used: ${result.uniqueClasses.length > 0 ? result.uniqueClasses.join(', ') : 'NONE'}`);
    console.log('');
  });
  
  // Best practices
  const goodPages = results.filter(r => r.severity === 'GOOD');
  if (goodPages.length > 0) {
    console.log(`${colors.bold}✅ PAGES FOLLOWING BEST PRACTICES:${colors.reset}`);
    goodPages.forEach(result => {
      console.log(`${colors.green}• ${result.fileName}${colors.reset} - ${result.inlinePercentage}% inline styles`);
    });
  }
  
  // Recommendations
  console.log(`\n${colors.bold}💡 RECOMMENDATIONS:${colors.reset}`);
  
  const criticalPages = results.filter(r => r.severity === 'CRITICAL').length;
  const badPages = results.filter(r => r.severity === 'BAD').length;
  const warningPages = results.filter(r => r.severity === 'WARNING').length;
  
  if (criticalPages > 0) {
    console.log(`${colors.red}🔥 CRITICAL:${colors.reset} ${criticalPages} pages have >70% inline styles - IMMEDIATE REFACTOR REQUIRED`);
  }
  
  if (badPages > 0) {
    console.log(`${colors.yellow}⚠️  BAD:${colors.reset} ${badPages} pages have >50% inline styles - Should be refactored`);
  }
  
  if (warningPages > 0) {
    console.log(`${colors.yellow}⚠️  WARNING:${colors.reset} ${warningPages} pages have >30% inline styles - Consider refactoring`);
  }
  
  console.log(`\n${colors.bold}📋 NEXT STEPS:${colors.reset}`);
  console.log('1. Create utility classes for common inline patterns');
  console.log('2. Convert repeated inline styles to CSS classes');
  console.log('3. Use CSS variables for consistent spacing/colors');
  console.log('4. Add linting rules to prevent new inline styles');
  console.log('5. Migrate critical pages first, then work down the list');
  
  // Generate CSV for further analysis
  const csvContent = [
    'File,Size(KB),Lines,InlineStyles,CSSClasses,InlinePercent,Severity',
    ...results.map(r => `${r.fileName},${r.fileSize},${r.lineCount},${r.inlineStyles},${r.cssClasses},${r.inlinePercentage},${r.severity}`)
  ].join('\n');
  
  fs.writeFileSync('inline_styles_audit.csv', csvContent);
  console.log(`\n${colors.green}📊 Detailed CSV report saved to: inline_styles_audit.csv${colors.reset}`);
}

// Run the audit
generateReport(); 