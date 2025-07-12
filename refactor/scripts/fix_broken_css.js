#!/usr/bin/env node

const fs = require('fs');
const path = require('path');

// ANSI colors
const colors = {
  red: '\x1b[31m',
  green: '\x1b[32m',
  yellow: '\x1b[33m',
  cyan: '\x1b[36m',
  reset: '\x1b[0m',
  bold: '\x1b[1m'
};

function fixCSSFile(filePath) {
  const content = fs.readFileSync(filePath, 'utf8');
  const fileName = path.basename(filePath);
  
  console.log(`${colors.cyan}🔧 Fixing ${fileName}...${colors.reset}`);
  
  let fixedContent = content;
  let fixCount = 0;
  
  // Fix 1: Remove quotes around CSS values
  fixedContent = fixedContent.replace(/:\s*['"]([^'"]*)['"]\s*;/g, (match, value) => {
    fixCount++;
    return `: ${value};`;
  });
  
  // Fix 2: Remove invalid CSS rules with JavaScript syntax
  const lines = fixedContent.split('\n');
  const validLines = [];
  
  lines.forEach(line => {
    // Skip lines with JavaScript syntax
    if (line.includes('===') || 
        line.includes('?') || 
        line.includes('${') ||
        line.includes('strategicData') ||
        line.includes('bgColor') ||
        line.includes('color.hex')) {
      console.log(`${colors.yellow}  ❌ Removing invalid CSS: ${line.trim().substring(0, 50)}...${colors.reset}`);
      fixCount++;
      return;
    }
    
    // Skip malformed class names
    if (line.includes('--') && line.includes('---')) {
      console.log(`${colors.yellow}  ❌ Removing malformed class: ${line.trim().substring(0, 50)}...${colors.reset}`);
      fixCount++;
      return;
    }
    
    validLines.push(line);
  });
  
  fixedContent = validLines.join('\n');
  
  // Fix 3: Clean up class names with weird characters
  fixedContent = fixedContent.replace(/\.-+/g, '.');
  
  // Write back if changes were made
  if (fixCount > 0) {
    fs.writeFileSync(filePath, fixedContent);
    console.log(`${colors.green}  ✅ Fixed ${fixCount} issues in ${fileName}${colors.reset}`);
  } else {
    console.log(`${colors.green}  ✅ ${fileName} was already clean${colors.reset}`);
  }
  
  return fixCount;
}

function fixAllCSSFiles() {
  console.log(`${colors.bold}${colors.cyan}🔧 Fixing Broken CSS Files...${colors.reset}`);
  
  const utilsDir = path.join(__dirname, '..', '..', 'web', 'src', 'styles', 'utilities');
  
  if (!fs.existsSync(utilsDir)) {
    console.log(`${colors.red}❌ Utilities directory not found: ${utilsDir}${colors.reset}`);
    return;
  }
  
  const cssFiles = fs.readdirSync(utilsDir)
    .filter(file => file.endsWith('.css'))
    .map(file => path.join(utilsDir, file));
  
  let totalFixes = 0;
  
  cssFiles.forEach(filePath => {
    totalFixes += fixCSSFile(filePath);
  });
  
  console.log(`\n${colors.bold}${colors.green}✅ CSS Fix Complete!${colors.reset}`);
  console.log(`${colors.cyan}📊 Total fixes applied: ${totalFixes}${colors.reset}`);
  console.log(`${colors.yellow}🔄 Refresh your app to see the visual fixes!${colors.reset}`);
}

// Run the fix
if (require.main === module) {
  fixAllCSSFiles();
}

module.exports = { fixAllCSSFiles, fixCSSFile }; 