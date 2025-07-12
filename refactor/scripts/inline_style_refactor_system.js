#!/usr/bin/env node

const fs = require('fs');
const path = require('path');
const crypto = require('crypto');

// ANSI color codes
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

class InlineStyleRefactor {
  constructor() {
    this.pagesDir = path.join(__dirname, 'web', 'src', 'pages');
    this.stylesDir = path.join(__dirname, 'web', 'src', 'styles');
    this.utilsDir = path.join(this.stylesDir, 'utilities');
    
    // Style pattern collectors
    this.stylePatterns = new Map();
    this.commonStyles = new Map();
    this.dynamicStyles = [];
    this.replacements = [];
    
    // CSS generation
    this.generatedClasses = new Map();
    this.utilityClasses = new Map();
    
    // Statistics
    this.stats = {
      totalInlineStyles: 0,
      replacedStyles: 0,
      generatedClasses: 0,
      filesProcessed: 0
    };
  }

  // STEP 1: Extract and analyze all inline styles
  extractInlineStyles(filePath) {
    const content = fs.readFileSync(filePath, 'utf8');
    const fileName = path.basename(filePath);
    
    // Enhanced regex to capture complete style objects
    const inlineStyleRegex = /style=\{\{([^}]+)\}\}/g;
    const styles = [];
    let match;
    
    while ((match = inlineStyleRegex.exec(content)) !== null) {
      const styleStr = match[1];
      const fullMatch = match[0];
      const startIndex = match.index;
      
      try {
        // Parse style object
        const styleObj = this.parseStyleObject(styleStr);
        const styleHash = this.generateStyleHash(styleObj);
        
        styles.push({
          fileName,
          filePath,
          styleStr,
          fullMatch,
          startIndex,
          styleObj,
          styleHash,
          context: this.extractContext(content, startIndex)
        });
        
        // Track style patterns
        this.trackStylePattern(styleObj, styleHash);
        
      } catch (error) {
        console.warn(`${colors.yellow}WARNING: Could not parse style in ${fileName}: ${styleStr}${colors.reset}`);
      }
    }
    
    return styles;
  }

  // Parse style object from string
  parseStyleObject(styleStr) {
    const styleObj = {};
    
    // Handle both single and multi-line styles
    const cleanStr = styleStr.replace(/\s+/g, ' ').trim();
    
    // Split by comma, but handle nested objects and template literals
    const properties = this.splitStyleProperties(cleanStr);
    
    properties.forEach(prop => {
      const [key, value] = this.parseStyleProperty(prop);
      if (key && value) {
        styleObj[key] = value;
      }
    });
    
    return styleObj;
  }

  // Smart property splitting that handles nested objects
  splitStyleProperties(str) {
    const properties = [];
    let current = '';
    let depth = 0;
    let inString = false;
    let stringChar = '';
    
    for (let i = 0; i < str.length; i++) {
      const char = str[i];
      
      if (!inString && (char === '"' || char === "'")) {
        inString = true;
        stringChar = char;
      } else if (inString && char === stringChar) {
        inString = false;
        stringChar = '';
      }
      
      if (!inString) {
        if (char === '{' || char === '(') depth++;
        if (char === '}' || char === ')') depth--;
        
        if (char === ',' && depth === 0) {
          properties.push(current.trim());
          current = '';
          continue;
        }
      }
      
      current += char;
    }
    
    if (current.trim()) {
      properties.push(current.trim());
    }
    
    return properties;
  }

  // Parse individual style property
  parseStyleProperty(prop) {
    const colonIndex = prop.indexOf(':');
    if (colonIndex === -1) return [null, null];
    
    const key = prop.substring(0, colonIndex).trim();
    let value = prop.substring(colonIndex + 1).trim();
    
    // Clean up the value - remove quotes and handle dynamic values
    if (value.includes('${') || value.includes('?') || value.includes('===')) {
      // Skip dynamic/conditional styles
      return [null, null];
    }
    
    // Remove quotes from CSS values
    value = value.replace(/^['"]|['"]$/g, '');
    
    return [key, value];
  }

  // Generate hash for style object
  generateStyleHash(styleObj) {
    const sortedObj = Object.keys(styleObj)
      .sort()
      .reduce((result, key) => {
        result[key] = styleObj[key];
        return result;
      }, {});
    
    return crypto.createHash('md5')
      .update(JSON.stringify(sortedObj))
      .digest('hex')
      .substring(0, 8);
  }

  // Extract context around the style
  extractContext(content, index) {
    const lines = content.split('\n');
    let currentIndex = 0;
    
    for (let i = 0; i < lines.length; i++) {
      const lineLength = lines[i].length + 1; // +1 for newline
      if (currentIndex + lineLength > index) {
        return {
          lineNumber: i + 1,
          line: lines[i],
          elementContext: this.extractElementContext(lines[i])
        };
      }
      currentIndex += lineLength;
    }
    
    return { lineNumber: 0, line: '', elementContext: 'unknown' };
  }

  // Extract element context (div, span, etc.)
  extractElementContext(line) {
    const elementMatch = line.match(/<(\w+)/);
    return elementMatch ? elementMatch[1] : 'unknown';
  }

  // Track style patterns for analysis
  trackStylePattern(styleObj, styleHash) {
    const pattern = this.categorizeStyle(styleObj);
    
    if (!this.stylePatterns.has(pattern)) {
      this.stylePatterns.set(pattern, []);
    }
    
    this.stylePatterns.get(pattern).push({
      styleObj,
      styleHash,
      count: 1
    });
    
    // Track individual style properties
    Object.entries(styleObj).forEach(([prop, value]) => {
      const key = `${prop}:${value}`;
      this.commonStyles.set(key, (this.commonStyles.get(key) || 0) + 1);
    });
  }

  // Categorize style by type
  categorizeStyle(styleObj) {
    const keys = Object.keys(styleObj);
    
    if (keys.some(k => k.includes('grid') || k.includes('Grid'))) return 'grid';
    if (keys.some(k => k.includes('flex') || k.includes('Flex'))) return 'flex';
    if (keys.some(k => k.includes('position') || k.includes('Position'))) return 'position';
    if (keys.some(k => k.includes('margin') || k.includes('padding'))) return 'spacing';
    if (keys.some(k => k.includes('color') || k.includes('Color') || k.includes('background'))) return 'color';
    if (keys.some(k => k.includes('border') || k.includes('Border'))) return 'border';
    if (keys.some(k => k.includes('font') || k.includes('Font') || k.includes('text'))) return 'typography';
    if (keys.some(k => k.includes('width') || k.includes('height') || k.includes('Width') || k.includes('Height'))) return 'sizing';
    
    return 'misc';
  }

  // STEP 2: Generate CSS classes from patterns
  generateCSSClasses() {
    console.log(`${colors.cyan}🔄 Generating CSS classes from style patterns...${colors.reset}`);
    
    // Generate utility classes for common patterns
    this.generateUtilityClasses();
    
    // Generate component-specific classes
    this.generateComponentClasses();
    
    // Generate layout classes
    this.generateLayoutClasses();
    
    console.log(`${colors.green}✅ Generated ${this.generatedClasses.size} CSS classes${colors.reset}`);
  }

  // Generate utility classes for common single-property styles
  generateUtilityClasses() {
    const utilityCategories = {
      spacing: new Map(),
      colors: new Map(),
      typography: new Map(),
      sizing: new Map(),
      borders: new Map()
    };
    
    // Categorize common styles
    for (const [styleKey, count] of this.commonStyles) {
      if (count < 2) continue; // Only generate utilities for repeated styles
      
      const [prop, value] = styleKey.split(':');
      const category = this.getUtilityCategory(prop);
      
      if (category && utilityCategories[category]) {
        utilityCategories[category].set(styleKey, count);
      }
    }
    
    // Generate utility CSS for each category
    Object.entries(utilityCategories).forEach(([category, styles]) => {
      if (styles.size > 0) {
        this.generateUtilityCategoryCSS(category, styles);
      }
    });
  }

  // Get utility category for a property
  getUtilityCategory(prop) {
    if (['margin', 'padding', 'gap', 'marginTop', 'marginBottom', 'marginLeft', 'marginRight', 'paddingTop', 'paddingBottom', 'paddingLeft', 'paddingRight'].includes(prop)) {
      return 'spacing';
    }
    if (['color', 'backgroundColor', 'borderColor', 'background'].includes(prop)) {
      return 'colors';
    }
    if (['fontSize', 'fontWeight', 'textAlign', 'lineHeight', 'fontFamily'].includes(prop)) {
      return 'typography';
    }
    if (['width', 'height', 'maxWidth', 'maxHeight', 'minWidth', 'minHeight'].includes(prop)) {
      return 'sizing';
    }
    if (['border', 'borderWidth', 'borderStyle', 'borderRadius', 'borderLeft', 'borderRight', 'borderTop', 'borderBottom'].includes(prop)) {
      return 'borders';
    }
    return null;
  }

  // Generate CSS for a utility category
  generateUtilityCategoryCSS(category, styles) {
    const cssRules = [];
    
    for (const [styleKey, count] of styles) {
      const [prop, value] = styleKey.split(':');
      const className = this.generateUtilityClassName(prop, value);
      
      // Convert camelCase to kebab-case
      const cssProp = prop.replace(/([A-Z])/g, '-$1').toLowerCase();
      
      // Clean value - remove quotes for CSS output
      const cleanValue = value.replace(/^['"]|['"]$/g, '');
      
      cssRules.push(`.${className} { ${cssProp}: ${cleanValue}; }`);
      
      // Store for replacement
      this.utilityClasses.set(styleKey, className);
      this.generatedClasses.set(className, {
        type: 'utility',
        category,
        property: prop,
        value,
        usage: count
      });
    }
    
    // Write to appropriate utility file
    this.writeUtilityCSS(category, cssRules);
  }

  // Generate utility class name
  generateUtilityClassName(prop, value) {
    const propAbbrev = this.getPropertyAbbreviation(prop);
    const valueAbbrev = this.getValueAbbreviation(value);
    
    return `${propAbbrev}-${valueAbbrev}`;
  }

  // Get property abbreviation
  getPropertyAbbreviation(prop) {
    const abbreviations = {
      'margin': 'm',
      'marginTop': 'mt',
      'marginBottom': 'mb',
      'marginLeft': 'ml',
      'marginRight': 'mr',
      'padding': 'p',
      'paddingTop': 'pt',
      'paddingBottom': 'pb',
      'paddingLeft': 'pl',
      'paddingRight': 'pr',
      'gap': 'gap',
      'backgroundColor': 'bg',
      'color': 'text',
      'borderColor': 'border',
      'fontSize': 'text',
      'fontWeight': 'font',
      'textAlign': 'text',
      'width': 'w',
      'height': 'h',
      'maxWidth': 'max-w',
      'maxHeight': 'max-h',
      'minWidth': 'min-w',
      'minHeight': 'min-h',
      'borderRadius': 'rounded',
      'border': 'border'
    };
    
    return abbreviations[prop] || prop.toLowerCase();
  }

  // Get value abbreviation
  getValueAbbreviation(value) {
    // Handle common values
    const cleanValue = value.replace(/['"]/g, '').trim();
    
    // Handle pixels, rem, em
    if (cleanValue.match(/^\d+px$/)) {
      return cleanValue.replace('px', '');
    }
    if (cleanValue.match(/^\d+rem$/)) {
      return cleanValue.replace('rem', 'r');
    }
    if (cleanValue.match(/^\d+em$/)) {
      return cleanValue.replace('em', 'e');
    }
    
    // Handle percentages
    if (cleanValue.match(/^\d+%$/)) {
      return cleanValue.replace('%', 'pct');
    }
    
    // Handle common keywords
    const keywords = {
      'center': 'center',
      'left': 'left',
      'right': 'right',
      'flex': 'flex',
      'block': 'block',
      'inline': 'inline',
      'none': 'none',
      'auto': 'auto',
      'bold': 'bold',
      'normal': 'normal',
      '#fff': 'white',
      '#ffffff': 'white',
      '#000': 'black',
      '#000000': 'black',
      'transparent': 'transparent'
    };
    
    if (keywords[cleanValue]) {
      return keywords[cleanValue];
    }
    
    // Handle hex colors
    if (cleanValue.match(/^#[0-9a-f]{3,8}$/i)) {
      return cleanValue.replace('#', 'hex-');
    }
    
    // Fallback: create safe class name
    return cleanValue.replace(/[^a-zA-Z0-9]/g, '-').toLowerCase();
  }

  // Generate component-specific classes for complex styles
  generateComponentClasses() {
    const componentStyles = new Map();
    
    // Group styles by component/pattern
    for (const [pattern, styles] of this.stylePatterns) {
      if (styles.length > 1) { // Only generate classes for repeated patterns
        const className = this.generateComponentClassName(pattern, styles);
        componentStyles.set(className, {
          pattern,
          styles,
          count: styles.length
        });
      }
    }
    
    // Generate CSS for component classes
    for (const [className, data] of componentStyles) {
      const cssRule = this.generateComponentCSS(className, data);
      this.generatedClasses.set(className, {
        type: 'component',
        pattern: data.pattern,
        usage: data.count,
        css: cssRule
      });
    }
  }

  // Generate component class name
  generateComponentClassName(pattern, styles) {
    const hash = this.generateStyleHash(styles[0].styleObj);
    return `${pattern}-${hash}`;
  }

  // Generate CSS for component class
  generateComponentCSS(className, data) {
    const styleObj = data.styles[0].styleObj;
    const properties = Object.entries(styleObj).map(([prop, value]) => {
      const cssProp = prop.replace(/([A-Z])/g, '-$1').toLowerCase();
      return `  ${cssProp}: ${value};`;
    }).join('\n');
    
    return `.${className} {\n${properties}\n}`;
  }

  // Generate layout classes for grid/flex patterns
  generateLayoutClasses() {
    const layoutPatterns = this.stylePatterns.get('grid') || [];
    const flexPatterns = this.stylePatterns.get('flex') || [];
    
    [...layoutPatterns, ...flexPatterns].forEach(pattern => {
      const className = this.generateLayoutClassName(pattern);
      this.generatedClasses.set(className, {
        type: 'layout',
        styleObj: pattern.styleObj,
        usage: pattern.count
      });
    });
  }

  // Generate layout class name
  generateLayoutClassName(pattern) {
    const styleObj = pattern.styleObj;
    
    if (styleObj.display === 'grid') {
      return `grid-${pattern.styleHash}`;
    }
    if (styleObj.display === 'flex') {
      return `flex-${pattern.styleHash}`;
    }
    
    return `layout-${pattern.styleHash}`;
  }

  // Write utility CSS to file
  writeUtilityCSS(category, cssRules) {
    const filePath = path.join(this.utilsDir, `${category}.css`);
    
    let existingContent = '';
    if (fs.existsSync(filePath)) {
      existingContent = fs.readFileSync(filePath, 'utf8');
    }
    
    // Add new rules to existing content
    const newContent = existingContent + '\n\n/* Auto-generated utility classes */\n' + cssRules.join('\n') + '\n';
    
    fs.writeFileSync(filePath, newContent);
    console.log(`${colors.green}✅ Updated ${category}.css with ${cssRules.length} utility classes${colors.reset}`);
  }

  // STEP 3: Replace inline styles with CSS classes
  replaceInlineStyles() {
    console.log(`${colors.cyan}🔄 Replacing inline styles with CSS classes...${colors.reset}`);
    
    const files = fs.readdirSync(this.pagesDir)
      .filter(file => file.endsWith('.tsx'))
      .map(file => path.join(this.pagesDir, file));
    
    files.forEach(filePath => {
      this.replaceInlineStylesInFile(filePath);
    });
    
    console.log(`${colors.green}✅ Replaced ${this.stats.replacedStyles} inline styles across ${this.stats.filesProcessed} files${colors.reset}`);
  }

  // Replace inline styles in a single file
  replaceInlineStylesInFile(filePath) {
    const content = fs.readFileSync(filePath, 'utf8');
    const styles = this.extractInlineStyles(filePath);
    
    if (styles.length === 0) return;
    
    let newContent = content;
    let replacements = 0;
    
    // Sort styles by position (reverse order to avoid index shifting)
    styles.sort((a, b) => b.startIndex - a.startIndex);
    
    styles.forEach(style => {
      const replacement = this.findBestReplacement(style);
      if (replacement) {
        newContent = newContent.substring(0, style.startIndex) + 
                    replacement + 
                    newContent.substring(style.startIndex + style.fullMatch.length);
        replacements++;
      }
    });
    
    if (replacements > 0) {
      // Add necessary imports
      newContent = this.addCSSImports(newContent, filePath);
      
      // Write back to file
      fs.writeFileSync(filePath, newContent);
      
      this.stats.replacedStyles += replacements;
      this.stats.filesProcessed++;
      
      console.log(`${colors.green}✅ ${path.basename(filePath)}: Replaced ${replacements} inline styles${colors.reset}`);
    }
  }

  // Find best CSS class replacement for an inline style
  findBestReplacement(style) {
    const { styleObj } = style;
    
    // Try to find exact utility class match
    const utilityMatch = this.findUtilityMatch(styleObj);
    if (utilityMatch) {
      return `className="${utilityMatch}"`;
    }
    
    // Try to find component class match
    const componentMatch = this.findComponentMatch(styleObj);
    if (componentMatch) {
      return `className="${componentMatch}"`;
    }
    
    // Try to decompose into multiple utility classes
    const decomposedMatch = this.decomposeToUtilities(styleObj);
    if (decomposedMatch) {
      return `className="${decomposedMatch}"`;
    }
    
    return null;
  }

  // Find utility class match
  findUtilityMatch(styleObj) {
    const classes = [];
    
    Object.entries(styleObj).forEach(([prop, value]) => {
      const styleKey = `${prop}:${value}`;
      if (this.utilityClasses.has(styleKey)) {
        classes.push(this.utilityClasses.get(styleKey));
      }
    });
    
    return classes.length > 0 ? classes.join(' ') : null;
  }

  // Find component class match
  findComponentMatch(styleObj) {
    const hash = this.generateStyleHash(styleObj);
    
    for (const [className, data] of this.generatedClasses) {
      if (data.type === 'component' && className.includes(hash)) {
        return className;
      }
    }
    
    return null;
  }

  // Decompose complex styles into multiple utility classes
  decomposeToUtilities(styleObj) {
    const classes = [];
    
    Object.entries(styleObj).forEach(([prop, value]) => {
      const styleKey = `${prop}:${value}`;
      if (this.utilityClasses.has(styleKey)) {
        classes.push(this.utilityClasses.get(styleKey));
      }
    });
    
    // Only use decomposed if we can replace most properties
    if (classes.length >= Object.keys(styleObj).length * 0.7) {
      return classes.join(' ');
    }
    
    return null;
  }

  // Add CSS imports to file
  addCSSImports(content, filePath) {
    // Check if imports already exist
    if (content.includes('import') && content.includes('.css')) {
      return content;
    }
    
    // Add import after other imports
    const importMatch = content.match(/^(import.*\n)+/m);
    if (importMatch) {
      const importsEnd = importMatch.index + importMatch[0].length;
      const beforeImports = content.substring(0, importsEnd);
      const afterImports = content.substring(importsEnd);
      
      return beforeImports + "import '../styles/utilities/spacing.css'\n" +
             "import '../styles/utilities/colors.css'\n" +
             "import '../styles/utilities/typography.css'\n" +
             "import '../styles/utilities/sizing.css'\n" +
             "import '../styles/utilities/borders.css'\n" +
             afterImports;
    }
    
    // Add at the beginning if no imports found
    return "import '../styles/utilities/spacing.css'\n" +
           "import '../styles/utilities/colors.css'\n" +
           "import '../styles/utilities/typography.css'\n" +
           "import '../styles/utilities/sizing.css'\n" +
           "import '../styles/utilities/borders.css'\n\n" +
           content;
  }

  // STEP 4: Generate comprehensive report
  generateReport() {
    console.log(`${colors.bold}${colors.cyan}
╔══════════════════════════════════════════════════════════════════════════════════════╗
║                    🔄 INLINE STYLE REFACTOR SYSTEM REPORT 🔄                        ║
╚══════════════════════════════════════════════════════════════════════════════════════╝${colors.reset}

${colors.bold}📊 REFACTORING STATISTICS:${colors.reset}
• Total Inline Styles Found: ${colors.bold}${this.stats.totalInlineStyles}${colors.reset}
• Styles Successfully Replaced: ${colors.bold}${this.stats.replacedStyles}${colors.reset}
• Generated CSS Classes: ${colors.bold}${this.stats.generatedClasses}${colors.reset}
• Files Processed: ${colors.bold}${this.stats.filesProcessed}${colors.reset}
• Success Rate: ${colors.bold}${((this.stats.replacedStyles / this.stats.totalInlineStyles) * 100).toFixed(1)}%${colors.reset}

${colors.bold}🏗️ GENERATED CLASSES BREAKDOWN:${colors.reset}`);

    const classByType = {
      utility: 0,
      component: 0,
      layout: 0
    };

    for (const [className, data] of this.generatedClasses) {
      classByType[data.type]++;
    }

    Object.entries(classByType).forEach(([type, count]) => {
      console.log(`• ${type.charAt(0).toUpperCase() + type.slice(1)} classes: ${colors.bold}${count}${colors.reset}`);
    });

    console.log(`\n${colors.bold}🎯 MOST COMMON STYLE PATTERNS:${colors.reset}`);
    const sortedPatterns = Array.from(this.stylePatterns.entries())
      .sort((a, b) => b[1].length - a[1].length)
      .slice(0, 10);

    sortedPatterns.forEach(([pattern, styles], index) => {
      console.log(`${index + 1}. ${pattern}: ${styles.length} occurrences`);
    });
  }

  // Create automatic backup before any changes
  createBackup() {
    console.log(`${colors.cyan}💾 Creating automatic backup...${colors.reset}`);
    
    const backupDir = path.join(__dirname, 'backup_before_refactor');
    const timestamp = new Date().toISOString().replace(/[:.]/g, '-');
    const timestampedBackupDir = path.join(backupDir, `refactor_${timestamp}`);
    
    // Create backup directory
    if (!fs.existsSync(timestampedBackupDir)) {
      fs.mkdirSync(timestampedBackupDir, { recursive: true });
    }
    
    // Backup pages
    const pagesDir = path.join(__dirname, 'web', 'src', 'pages');
    if (fs.existsSync(pagesDir)) {
      this.copyDirectory(pagesDir, path.join(timestampedBackupDir, 'pages'));
    }
    
    // Backup styles
    const stylesDir = path.join(__dirname, 'web', 'src', 'styles');
    if (fs.existsSync(stylesDir)) {
      this.copyDirectory(stylesDir, path.join(timestampedBackupDir, 'styles'));
    }
    
    console.log(`${colors.green}✅ Backup created at: ${timestampedBackupDir}${colors.reset}`);
    return timestampedBackupDir;
  }

  // Copy directory recursively
  copyDirectory(src, dest) {
    if (!fs.existsSync(dest)) {
      fs.mkdirSync(dest, { recursive: true });
    }
    
    const entries = fs.readdirSync(src, { withFileTypes: true });
    
    entries.forEach(entry => {
      const srcPath = path.join(src, entry.name);
      const destPath = path.join(dest, entry.name);
      
      if (entry.isDirectory()) {
        this.copyDirectory(srcPath, destPath);
      } else {
        fs.copyFileSync(srcPath, destPath);
      }
    });
  }

  // Main execution method
  async run() {
    console.log(`${colors.bold}${colors.cyan}🚀 Starting Inline Style Refactor System...${colors.reset}`);
    
    // Step 0: Create automatic backup
    const backupPath = this.createBackup();
    
    // Step 1: Analyze all inline styles
    console.log(`${colors.cyan}🔍 Step 1: Analyzing inline styles...${colors.reset}`);
    const files = fs.readdirSync(this.pagesDir)
      .filter(file => file.endsWith('.tsx'))
      .map(file => path.join(this.pagesDir, file));
    
    files.forEach(filePath => {
      const styles = this.extractInlineStyles(filePath);
      this.stats.totalInlineStyles += styles.length;
    });
    
    console.log(`${colors.green}✅ Found ${this.stats.totalInlineStyles} inline styles across ${files.length} files${colors.reset}`);
    
    // Step 2: Generate CSS classes
    this.generateCSSClasses();
    this.stats.generatedClasses = this.generatedClasses.size;
    
    // Step 3: Replace inline styles
    this.replaceInlineStyles();
    
    // Step 4: Generate report
    this.generateReport();
    
    console.log(`\n${colors.bold}${colors.green}✅ Inline Style Refactor System completed successfully!${colors.reset}`);
    console.log(`${colors.cyan}💾 Backup location: ${backupPath}${colors.reset}`);
    console.log(`${colors.yellow}⚠️  If anything goes wrong, restore with: node test_refactor_system.js restore${colors.reset}`);
  }
}

// CLI interface
if (require.main === module) {
  const refactor = new InlineStyleRefactor();
  refactor.run().catch(console.error);
}

module.exports = InlineStyleRefactor; 