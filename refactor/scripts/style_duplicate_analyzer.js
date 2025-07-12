#!/usr/bin/env node

const fs = require('fs');
const path = require('path');

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

class StyleDuplicateAnalyzer {
  constructor() {
    this.pagesDir = path.join(__dirname, '..', '..', 'web', 'src', 'pages');
    this.stylesDir = path.join(__dirname, '..', '..', 'web', 'src', 'styles');
    
    // Style analysis data
    this.allInlineStyles = new Map(); // styleHash -> {files: [], style: {}, count: 0}
    this.stylePatterns = new Map(); // pattern -> {files: [], styles: [], count: 0}
    this.cssClasses = new Map(); // className -> {files: [], count: 0}
    this.elementStyles = new Map(); // elementType -> {styles: [], files: []}
  }

  // Extract all inline styles from a file
  extractInlineStyles(filePath) {
    const content = fs.readFileSync(filePath, 'utf8');
    const fileName = path.basename(filePath);
    
    const inlineStyleRegex = /style=\{\{([^}]+)\}\}/g;
    const styles = [];
    let match;
    
    while ((match = inlineStyleRegex.exec(content)) !== null) {
      const styleStr = match[1];
      const fullMatch = match[0];
      const startIndex = match.index;
      
      try {
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
      } catch (error) {
        console.warn(`${colors.yellow}WARNING: Could not parse style in ${fileName}: ${styleStr}${colors.reset}`);
      }
    }
    
    return styles;
  }

  // Parse style object from string
  parseStyleObject(styleStr) {
    const styleObj = {};
    const cleanStr = styleStr.replace(/\s+/g, ' ').trim();
    const properties = this.splitStyleProperties(cleanStr);
    
    properties.forEach(prop => {
      const [key, value] = this.parseStyleProperty(prop);
      if (key && value) {
        styleObj[key] = value;
      }
    });
    
    return styleObj;
  }

  // Smart property splitting
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
    
    // Skip dynamic/conditional styles
    if (value.includes('${') || value.includes('?') || value.includes('===')) {
      return [null, null];
    }
    
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
    
    return require('crypto').createHash('md5')
      .update(JSON.stringify(sortedObj))
      .digest('hex')
      .substring(0, 8);
  }

  // Extract context around the style
  extractContext(content, index) {
    const lines = content.split('\n');
    let currentIndex = 0;
    
    for (let i = 0; i < lines.length; i++) {
      const lineLength = lines[i].length + 1;
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

  // Extract element context
  extractElementContext(line) {
    const elementMatch = line.match(/<(\w+)/);
    return elementMatch ? elementMatch[1] : 'unknown';
  }

  // Extract CSS classes from a file
  extractCSSClasses(filePath) {
    const content = fs.readFileSync(filePath, 'utf8');
    const fileName = path.basename(filePath);
    
    const classNameRegex = /className="([^"]*)"/g;
    const classes = new Set();
    let match;
    
    while ((match = classNameRegex.exec(content)) !== null) {
      const classList = match[1].split(' ').filter(c => c.trim());
      classList.forEach(c => {
        const className = c.trim();
        if (className) {
          classes.add(className);
          
          // Track class usage across files
          if (!this.cssClasses.has(className)) {
            this.cssClasses.set(className, { files: [], count: 0 });
          }
          const classData = this.cssClasses.get(className);
          if (!classData.files.includes(fileName)) {
            classData.files.push(fileName);
          }
          classData.count++;
        }
      });
    }
    
    return Array.from(classes);
  }

  // Categorize style by pattern
  categorizeStyle(styleObj) {
    const keys = Object.keys(styleObj).sort();
    
    if (keys.includes('display') && keys.includes('justifyContent') && keys.includes('alignItems')) {
      return 'flexbox-layout';
    }
    if (keys.includes('margin') || keys.includes('padding')) {
      return 'spacing';
    }
    if (keys.includes('color') || keys.includes('backgroundColor')) {
      return 'colors';
    }
    if (keys.includes('fontSize') || keys.includes('fontWeight') || keys.includes('textAlign')) {
      return 'typography';
    }
    if (keys.includes('border') || keys.includes('borderRadius')) {
      return 'borders';
    }
    if (keys.includes('width') || keys.includes('height')) {
      return 'sizing';
    }
    if (keys.includes('position') || keys.includes('top') || keys.includes('left')) {
      return 'positioning';
    }
    
    return 'other';
  }

  // Analyze all files
  analyzeAllFiles() {
    console.log(`${colors.bold}${colors.cyan}🔍 Analyzing style duplicates and patterns...${colors.reset}`);
    
    const files = fs.readdirSync(this.pagesDir)
      .filter(file => file.endsWith('.tsx'))
      .map(file => path.join(this.pagesDir, file));
    
    files.forEach(filePath => {
      const fileName = path.basename(filePath);
      console.log(`  📄 Analyzing ${fileName}...`);
      
      // Extract inline styles
      const styles = this.extractInlineStyles(filePath);
      styles.forEach(style => {
        const hash = style.styleHash;
        
        if (!this.allInlineStyles.has(hash)) {
          this.allInlineStyles.set(hash, {
            files: [],
            style: style.styleObj,
            count: 0,
            examples: []
          });
        }
        
        const styleData = this.allInlineStyles.get(hash);
        if (!styleData.files.includes(fileName)) {
          styleData.files.push(fileName);
        }
        styleData.count++;
        styleData.examples.push({
          file: fileName,
          line: style.context.lineNumber,
          element: style.context.elementContext
        });
        
        // Track by pattern
        const pattern = this.categorizeStyle(style.styleObj);
        if (!this.stylePatterns.has(pattern)) {
          this.stylePatterns.set(pattern, { files: [], styles: [], count: 0 });
        }
        
        const patternData = this.stylePatterns.get(pattern);
        if (!patternData.files.includes(fileName)) {
          patternData.files.push(fileName);
        }
        patternData.styles.push(style.styleObj);
        patternData.count++;
        
        // Track by element type
        const elementType = style.context.elementContext;
        if (!this.elementStyles.has(elementType)) {
          this.elementStyles.set(elementType, { styles: [], files: [] });
        }
        
        const elementData = this.elementStyles.get(elementType);
        elementData.styles.push(style.styleObj);
        if (!elementData.files.includes(fileName)) {
          elementData.files.push(fileName);
        }
      });
      
      // Extract CSS classes
      this.extractCSSClasses(filePath);
    });
  }

  // Generate duplicate analysis report
  generateDuplicateReport() {
    console.log(`\n${colors.bold}${colors.cyan}
╔══════════════════════════════════════════════════════════════════════════════════════╗
║                    🔄 STYLE DUPLICATE ANALYSIS REPORT 🔄                           ║
╚══════════════════════════════════════════════════════════════════════════════════════╝${colors.reset}`);

    // Find exact duplicates
    const duplicates = Array.from(this.allInlineStyles.entries())
      .filter(([hash, data]) => data.files.length > 1)
      .sort((a, b) => b[1].count - a[1].count);

    console.log(`\n${colors.bold}🎯 EXACT STYLE DUPLICATES (${duplicates.length} found):${colors.reset}`);
    
    if (duplicates.length === 0) {
      console.log(`${colors.green}✅ No exact style duplicates found!${colors.reset}`);
    } else {
      duplicates.forEach(([hash, data], index) => {
        console.log(`\n${colors.bold}${index + 1}. Style used in ${data.files.length} files (${data.count} total instances):${colors.reset}`);
        console.log(`   Style: ${JSON.stringify(data.style)}`);
        console.log(`   Files: ${data.files.join(', ')}`);
        data.examples.slice(0, 3).forEach(example => {
          console.log(`   └── ${example.file}:${example.line} (${example.element})`);
        });
      });
    }

    // Pattern analysis
    console.log(`\n${colors.bold}📊 STYLE PATTERN ANALYSIS:${colors.reset}`);
    const sortedPatterns = Array.from(this.stylePatterns.entries())
      .sort((a, b) => b[1].count - a[1].count);

    sortedPatterns.forEach(([pattern, data]) => {
      console.log(`\n${colors.bold}${pattern.toUpperCase()}:${colors.reset} ${data.count} instances across ${data.files.length} files`);
      console.log(`   Files: ${data.files.join(', ')}`);
      
      // Show most common properties in this pattern
      const propertyCounts = {};
      data.styles.forEach(style => {
        Object.keys(style).forEach(prop => {
          propertyCounts[prop] = (propertyCounts[prop] || 0) + 1;
        });
      });
      
      const topProperties = Object.entries(propertyCounts)
        .sort((a, b) => b[1] - a[1])
        .slice(0, 5);
      
      console.log(`   Top properties: ${topProperties.map(([prop, count]) => `${prop}(${count})`).join(', ')}`);
    });

    // Element-specific analysis
    console.log(`\n${colors.bold}🏷️  ELEMENT-SPECIFIC STYLING:${colors.reset}`);
    const sortedElements = Array.from(this.elementStyles.entries())
      .sort((a, b) => b[1].styles.length - a[1].styles.length);

    sortedElements.forEach(([element, data]) => {
      if (data.styles.length > 1) {
        console.log(`\n${colors.bold}<${element}>:${colors.reset} ${data.styles.length} styles across ${data.files.length} files`);
        console.log(`   Files: ${data.files.join(', ')}`);
        
        // Find common properties for this element
        const propertyCounts = {};
        data.styles.forEach(style => {
          Object.keys(style).forEach(prop => {
            propertyCounts[prop] = (propertyCounts[prop] || 0) + 1;
          });
        });
        
        const commonProperties = Object.entries(propertyCounts)
          .filter(([prop, count]) => count > 1)
          .sort((a, b) => b[1] - a[1]);
        
        if (commonProperties.length > 0) {
          console.log(`   Common properties: ${commonProperties.map(([prop, count]) => `${prop}(${count})`).join(', ')}`);
        }
      }
    });

    // CSS class usage analysis
    console.log(`\n${colors.bold}🎨 CSS CLASS USAGE ANALYSIS:${colors.reset}`);
    const multiFileClasses = Array.from(this.cssClasses.entries())
      .filter(([className, data]) => data.files.length > 1)
      .sort((a, b) => b[1].count - a[1].count);

    console.log(`\n${colors.bold}Shared CSS Classes (${multiFileClasses.length} found):${colors.reset}`);
    multiFileClasses.slice(0, 10).forEach(([className, data]) => {
      console.log(`   ${className}: used ${data.count} times in ${data.files.length} files`);
    });

    // Recommendations
    this.generateRecommendations(duplicates, sortedPatterns);
  }

  // Generate recommendations
  generateRecommendations(duplicates, patterns) {
    console.log(`\n${colors.bold}💡 STREAMLINING RECOMMENDATIONS:${colors.reset}`);
    
    if (duplicates.length > 0) {
      console.log(`\n${colors.yellow}🔥 HIGH PRIORITY - Create utility classes for:${colors.reset}`);
      duplicates.slice(0, 5).forEach(([hash, data]) => {
        const styleStr = Object.entries(data.style)
          .map(([k, v]) => `${k}: ${v}`)
          .join('; ');
        console.log(`   • ${styleStr} (used in ${data.files.length} files)`);
      });
    }

    console.log(`\n${colors.cyan}📋 PATTERN-BASED RECOMMENDATIONS:${colors.reset}`);
    patterns.forEach(([pattern, data]) => {
      if (data.count > 5) {
        console.log(`   • Create ${pattern} utility classes (${data.count} instances)`);
      }
    });

    console.log(`\n${colors.green}✅ NEXT STEPS:${colors.reset}`);
    console.log('1. Create utility classes for exact duplicates');
    console.log('2. Standardize common patterns (flexbox, spacing, colors)');
    console.log('3. Create element-specific base styles');
    console.log('4. Audit CSS class usage for consistency');
    console.log('5. Consider creating component-specific style modules');
  }

  // Run the analysis
  run() {
    this.analyzeAllFiles();
    this.generateDuplicateReport();
  }
}

// CLI interface
if (require.main === module) {
  const analyzer = new StyleDuplicateAnalyzer();
  analyzer.run();
}

module.exports = StyleDuplicateAnalyzer; 