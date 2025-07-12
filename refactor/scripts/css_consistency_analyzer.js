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

class CSCConsistencyAnalyzer {
  constructor() {
    this.pagesDir = path.join(__dirname, '..', '..', 'web', 'src', 'pages');
    this.stylesDir = path.join(__dirname, '..', '..', 'web', 'src', 'styles');
    
    // Analysis data
    this.cssClasses = new Map(); // className -> {files: [], count: 0, elements: []}
    this.elementClasses = new Map(); // elementType -> {classes: [], files: []}
    this.orphanedClasses = new Set(); // CSS classes not used in any file
    this.missingStyles = new Map(); // elementType -> {files: [], suggestedClasses: []}
  }

  // Extract CSS classes from a file
  extractCSSClasses(filePath) {
    const content = fs.readFileSync(filePath, 'utf8');
    const fileName = path.basename(filePath);
    
    const classNameRegex = /className="([^"]*)"/g;
    const elementClassMap = new Map(); // element -> classes[]
    let match;
    
    while ((match = classNameRegex.exec(content)) !== null) {
      const classList = match[1].split(' ').filter(c => c.trim());
      const elementContext = this.extractElementContext(content, match.index);
      
      classList.forEach(c => {
        const className = c.trim();
        if (className) {
          // Track class usage
          if (!this.cssClasses.has(className)) {
            this.cssClasses.set(className, { files: [], count: 0, elements: [] });
          }
          const classData = this.cssClasses.get(className);
          if (!classData.files.includes(fileName)) {
            classData.files.push(fileName);
          }
          classData.count++;
          if (!classData.elements.includes(elementContext)) {
            classData.elements.push(elementContext);
          }
          
          // Track element-class relationships
          if (!elementClassMap.has(elementContext)) {
            elementClassMap.set(elementContext, []);
          }
          elementClassMap.get(elementContext).push(className);
        }
      });
    }
    
    // Track element-class patterns
    elementClassMap.forEach((classes, element) => {
      if (!this.elementClasses.has(element)) {
        this.elementClasses.set(element, { classes: [], files: [] });
      }
      const elementData = this.elementClasses.get(element);
      classes.forEach(cls => {
        if (!elementData.classes.includes(cls)) {
          elementData.classes.push(cls);
        }
      });
      if (!elementData.files.includes(fileName)) {
        elementData.files.push(fileName);
      }
    });
    
    return elementClassMap;
  }

  // Extract element context
  extractElementContext(content, index) {
    // Look backwards to find the opening tag
    const beforeContent = content.substring(0, index);
    const lines = beforeContent.split('\n');
    const currentLine = lines[lines.length - 1];
    
    const elementMatch = currentLine.match(/<(\w+)/);
    return elementMatch ? elementMatch[1] : 'unknown';
  }

  // Find elements without className
  findUnstyledElements(filePath) {
    const content = fs.readFileSync(filePath, 'utf8');
    const fileName = path.basename(filePath);
    
    // Find elements that might need styling
    const elementRegex = /<(\w+)(?![^>]*className=)[^>]*>/g;
    const unstyledElements = new Map(); // elementType -> count
    let match;
    
    while ((match = elementRegex.exec(content)) !== null) {
      const elementType = match[1];
      const fullTag = match[0];
      
      // Skip self-closing tags and elements that shouldn't be styled
      if (['img', 'br', 'hr', 'input', 'textarea', 'select', 'button'].includes(elementType)) {
        continue;
      }
      
      // Skip elements that already have inline styles
      if (fullTag.includes('style=')) {
        continue;
      }
      
      if (!unstyledElements.has(elementType)) {
        unstyledElements.set(elementType, 0);
      }
      unstyledElements.set(elementType, unstyledElements.get(elementType) + 1);
    }
    
    return unstyledElements;
  }

  // Load existing CSS classes
  loadExistingCSSClasses() {
    const cssFiles = this.findCSSFiles();
    
    cssFiles.forEach(cssFile => {
      const content = fs.readFileSync(cssFile, 'utf8');
      const classRegex = /\.([a-zA-Z][a-zA-Z0-9_-]*)\s*\{/g;
      let match;
      
      while ((match = classRegex.exec(content)) !== null) {
        const className = match[1];
        this.orphanedClasses.add(className);
      }
    });
  }

  // Find CSS files
  findCSSFiles() {
    const cssFiles = [];
    
    if (fs.existsSync(this.stylesDir)) {
      this.walkDirectory(this.stylesDir, (filePath) => {
        if (filePath.endsWith('.css')) {
          cssFiles.push(filePath);
        }
      });
    }
    
    return cssFiles;
  }

  // Walk directory recursively
  walkDirectory(dir, callback) {
    const entries = fs.readdirSync(dir, { withFileTypes: true });
    
    entries.forEach(entry => {
      const fullPath = path.join(dir, entry.name);
      if (entry.isDirectory()) {
        this.walkDirectory(fullPath, callback);
      } else {
        callback(fullPath);
      }
    });
  }

  // Analyze all files
  analyzeAllFiles() {
    console.log(`${colors.bold}${colors.cyan}🔍 Analyzing CSS consistency and missing styles...${colors.reset}`);
    
    // Load existing CSS classes first
    this.loadExistingCSSClasses();
    
    const files = fs.readdirSync(this.pagesDir)
      .filter(file => file.endsWith('.tsx'))
      .map(file => path.join(this.pagesDir, file));
    
    files.forEach(filePath => {
      const fileName = path.basename(filePath);
      console.log(`  📄 Analyzing ${fileName}...`);
      
      // Extract CSS classes
      this.extractCSSClasses(filePath);
      
      // Find unstyled elements
      const unstyledElements = this.findUnstyledElements(filePath);
      unstyledElements.forEach((count, elementType) => {
        if (!this.missingStyles.has(elementType)) {
          this.missingStyles.set(elementType, { files: [], count: 0, suggestedClasses: [] });
        }
        const missingData = this.missingStyles.get(elementType);
        if (!missingData.files.includes(fileName)) {
          missingData.files.push(fileName);
        }
        missingData.count += count;
      });
    });
    
    // Remove used classes from orphaned set
    this.cssClasses.forEach((data, className) => {
      this.orphanedClasses.delete(className);
    });
  }

  // Generate consistency report
  generateConsistencyReport() {
    console.log(`\n${colors.bold}${colors.cyan}
╔══════════════════════════════════════════════════════════════════════════════════════╗
║                    🎨 CSS CONSISTENCY ANALYSIS REPORT 🎨                           ║
╚══════════════════════════════════════════════════════════════════════════════════════╝${colors.reset}`);

    // CSS class usage analysis
    console.log(`\n${colors.bold}📊 CSS CLASS USAGE ANALYSIS:${colors.reset}`);
    const sortedClasses = Array.from(this.cssClasses.entries())
      .sort((a, b) => b[1].count - a[1].count);

    console.log(`\n${colors.bold}Most Used Classes:${colors.reset}`);
    sortedClasses.slice(0, 10).forEach(([className, data]) => {
      console.log(`   ${className}: ${data.count} uses across ${data.files.length} files`);
      console.log(`     └── Elements: ${data.elements.join(', ')}`);
    });

    // Inconsistent element styling
    console.log(`\n${colors.bold}🎯 INCONSISTENT ELEMENT STYLING:${colors.reset}`);
    const inconsistentElements = Array.from(this.elementClasses.entries())
      .filter(([element, data]) => data.files.length > 1 && data.classes.length > 3)
      .sort((a, b) => b[1].classes.length - a[1].classes.length);

    inconsistentElements.forEach(([element, data]) => {
      console.log(`\n${colors.bold}<${element}>:${colors.reset} ${data.classes.length} different classes across ${data.files.length} files`);
      console.log(`   Files: ${data.files.join(', ')}`);
      console.log(`   Classes: ${data.classes.join(', ')}`);
    });

    // Missing styles analysis
    console.log(`\n${colors.bold}❌ MISSING STYLES:${colors.reset}`);
    const sortedMissing = Array.from(this.missingStyles.entries())
      .sort((a, b) => b[1].count - a[1].count);

    if (sortedMissing.length === 0) {
      console.log(`${colors.green}✅ No unstyled elements found!${colors.reset}`);
    } else {
      sortedMissing.forEach(([element, data]) => {
        console.log(`\n${colors.bold}<${element}>:${colors.reset} ${data.count} unstyled instances across ${data.files.length} files`);
        console.log(`   Files: ${data.files.join(', ')}`);
        
        // Suggest classes based on element type
        const suggestions = this.suggestClassesForElement(element);
        if (suggestions.length > 0) {
          console.log(`   Suggested classes: ${suggestions.join(', ')}`);
        }
      });
    }

    // Orphaned CSS classes
    console.log(`\n${colors.bold}👻 ORPHANED CSS CLASSES:${colors.reset}`);
    const orphanedArray = Array.from(this.orphanedClasses);
    
    if (orphanedArray.length === 0) {
      console.log(`${colors.green}✅ No orphaned CSS classes found!${colors.reset}`);
    } else {
      console.log(`${colors.yellow}Found ${orphanedArray.length} orphaned classes:${colors.reset}`);
      orphanedArray.slice(0, 20).forEach(className => {
        console.log(`   • ${className}`);
      });
      if (orphanedArray.length > 20) {
        console.log(`   ... and ${orphanedArray.length - 20} more`);
      }
    }

    // Consistency recommendations
    this.generateConsistencyRecommendations(inconsistentElements, sortedMissing);
  }

  // Suggest classes for element type
  suggestClassesForElement(elementType) {
    const suggestions = {
      'div': ['container', 'section', 'card', 'grid', 'flex'],
      'h1': ['title', 'heading', 'main-title'],
      'h2': ['subtitle', 'heading', 'section-title'],
      'h3': ['heading', 'subsection-title'],
      'h4': ['heading', 'small-title'],
      'p': ['text', 'paragraph', 'description'],
      'span': ['text', 'label', 'badge'],
      'button': ['btn', 'button', 'action-button'],
      'a': ['link', 'nav-link'],
      'ul': ['list', 'nav-list'],
      'li': ['list-item', 'nav-item'],
      'table': ['table', 'data-table'],
      'tr': ['table-row'],
      'td': ['table-cell'],
      'th': ['table-header']
    };
    
    return suggestions[elementType] || ['content', 'element'];
  }

  // Generate consistency recommendations
  generateConsistencyRecommendations(inconsistentElements, missingStyles) {
    console.log(`\n${colors.bold}💡 CONSISTENCY RECOMMENDATIONS:${colors.reset}`);
    
    if (inconsistentElements.length > 0) {
      console.log(`\n${colors.yellow}🔥 HIGH PRIORITY - Standardize element styling:${colors.reset}`);
      inconsistentElements.slice(0, 5).forEach(([element, data]) => {
        console.log(`   • <${element}>: Create standard classes (currently using ${data.classes.length} different classes)`);
      });
    }

    if (missingStyles.length > 0) {
      console.log(`\n${colors.cyan}📋 STYLING GAPS:${colors.reset}`);
      missingStyles.slice(0, 5).forEach(([element, data]) => {
        console.log(`   • <${element}>: Add consistent styling (${data.count} unstyled instances)`);
      });
    }

    console.log(`\n${colors.green}✅ NEXT STEPS:${colors.reset}`);
    console.log('1. Create element-specific base classes');
    console.log('2. Standardize class naming conventions');
    console.log('3. Remove orphaned CSS classes');
    console.log('4. Create component-specific style modules');
    console.log('5. Implement design system tokens');
  }

  // Run the analysis
  run() {
    this.analyzeAllFiles();
    this.generateConsistencyReport();
  }
}

// CLI interface
if (require.main === module) {
  const analyzer = new CSCConsistencyAnalyzer();
  analyzer.run();
}

module.exports = CSCConsistencyAnalyzer; 