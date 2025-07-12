#!/usr/bin/env node

const fs = require('fs');
const path = require('path');
const InlineStyleRefactor = require('./inline_style_refactor_system');

class RefactorTester {
  constructor() {
    this.testDir = path.join(__dirname, '..', 'test-outputs', 'test_refactor');
    this.backupDir = path.join(__dirname, '..', 'backups', 'backup_before_refactor');
    this.refactor = new InlineStyleRefactor();
  }

  // Create test environment
  setup() {
    console.log('🔧 Setting up test environment...');
    
    // Create test directory
    if (fs.existsSync(this.testDir)) {
      fs.rmSync(this.testDir, { recursive: true, force: true });
    }
    fs.mkdirSync(this.testDir, { recursive: true });
    
    // Create backup directory
    if (!fs.existsSync(this.backupDir)) {
      fs.mkdirSync(this.backupDir, { recursive: true });
    }
    
    console.log('✅ Test environment ready');
  }

  // Create backup of original files
  createBackup() {
    console.log('💾 Creating backup of original files...');
    
    const pagesDir = path.join(__dirname, '..', '..', 'web', 'src', 'pages');
    const stylesDir = path.join(__dirname, '..', '..', 'web', 'src', 'styles');
    
    // Backup pages
    if (fs.existsSync(pagesDir)) {
      this.copyDirectory(pagesDir, path.join(this.backupDir, 'pages'));
    }
    
    // Backup styles
    if (fs.existsSync(stylesDir)) {
      this.copyDirectory(stylesDir, path.join(this.backupDir, 'styles'));
    }
    
    console.log('✅ Backup completed');
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

  // Test the refactor system on a single file
  testSingleFile(fileName) {
    console.log(`🧪 Testing refactor on ${fileName}...`);
    
    const originalPath = path.join(__dirname, '..', '..', 'web', 'src', 'pages', fileName);
    const testPath = path.join(this.testDir, fileName);
    
    if (!fs.existsSync(originalPath)) {
      console.error(`❌ File ${fileName} not found`);
      return false;
    }
    
    // Copy file to test directory
    fs.copyFileSync(originalPath, testPath);
    
    // Run refactor on test file
    try {
      const styles = this.refactor.extractInlineStyles(testPath);
      console.log(`   Found ${styles.length} inline styles`);
      
      // Show what would be replaced
      styles.forEach((style, index) => {
        console.log(`   ${index + 1}. Line ${style.context.lineNumber}: ${style.styleStr.substring(0, 50)}...`);
      });
      
      return true;
    } catch (error) {
      console.error(`❌ Error testing ${fileName}:`, error.message);
      return false;
    }
  }

  // Validate generated CSS classes
  validateGeneratedCSS() {
    console.log('✅ Validating generated CSS classes...');
    
    const utilsDir = path.join(__dirname, '..', '..', 'web', 'src', 'styles', 'utilities');
    
    if (!fs.existsSync(utilsDir)) {
      console.log('⚠️  Utilities directory does not exist yet');
      return false;
    }
    
    const cssFiles = fs.readdirSync(utilsDir).filter(f => f.endsWith('.css'));
    
    cssFiles.forEach(file => {
      const filePath = path.join(utilsDir, file);
      const content = fs.readFileSync(filePath, 'utf8');
      
      // Basic CSS syntax validation
      const openBraces = (content.match(/\{/g) || []).length;
      const closeBraces = (content.match(/\}/g) || []).length;
      
      if (openBraces === closeBraces) {
        console.log(`✅ ${file}: Valid CSS syntax`);
      } else {
        console.log(`❌ ${file}: Unmatched braces (${openBraces} open, ${closeBraces} close)`);
      }
    });
    
    return true;
  }

  // Dry run - show what would be changed without making changes
  dryRun() {
    console.log('🔍 Performing dry run analysis...');
    
    const pagesDir = path.join(__dirname, '..', '..', 'web', 'src', 'pages');
    const files = fs.readdirSync(pagesDir)
      .filter(file => file.endsWith('.tsx'))
      .map(file => path.join(pagesDir, file));
    
    const analysis = {
      totalFiles: files.length,
      filesWithInlineStyles: 0,
      totalInlineStyles: 0,
      replaceableStyles: 0,
      stylePatterns: new Map()
    };
    
    files.forEach(filePath => {
      const styles = this.refactor.extractInlineStyles(filePath);
      
      if (styles.length > 0) {
        analysis.filesWithInlineStyles++;
        analysis.totalInlineStyles += styles.length;
        
        // Analyze patterns
        styles.forEach(style => {
          const pattern = this.refactor.categorizeStyle(style.styleObj);
          analysis.stylePatterns.set(pattern, (analysis.stylePatterns.get(pattern) || 0) + 1);
        });
      }
    });
    
    console.log(`📊 Dry Run Results:
• Total files: ${analysis.totalFiles}
• Files with inline styles: ${analysis.filesWithInlineStyles}
• Total inline styles: ${analysis.totalInlineStyles}
• Average per file: ${(analysis.totalInlineStyles / analysis.filesWithInlineStyles).toFixed(1)}

Style Patterns:`);
    
    Array.from(analysis.stylePatterns.entries())
      .sort((a, b) => b[1] - a[1])
      .forEach(([pattern, count]) => {
        console.log(`• ${pattern}: ${count} occurrences`);
      });
    
    return analysis;
  }

  // Run comprehensive tests
  runTests() {
    console.log('🧪 Running comprehensive refactor tests...');
    
    this.setup();
    this.createBackup();
    
    // Test on worst offenders first
    const testFiles = ['Methodology.tsx', 'ContentMatrix.tsx', 'PersonaInsights.tsx'];
    
    testFiles.forEach(fileName => {
      this.testSingleFile(fileName);
    });
    
    // Dry run analysis
    const analysis = this.dryRun();
    
    // Validate existing utilities
    this.validateGeneratedCSS();
    
    return analysis;
  }

  // Restore from backup
  restore() {
    console.log('🔄 Restoring from backup...');
    
    const pagesBackup = path.join(this.backupDir, 'pages');
    const stylesBackup = path.join(this.backupDir, 'styles');
    
    if (fs.existsSync(pagesBackup)) {
      const pagesDir = path.join(__dirname, 'web', 'src', 'pages');
      fs.rmSync(pagesDir, { recursive: true, force: true });
      this.copyDirectory(pagesBackup, pagesDir);
    }
    
    if (fs.existsSync(stylesBackup)) {
      const stylesDir = path.join(__dirname, 'web', 'src', 'styles');
      fs.rmSync(stylesDir, { recursive: true, force: true });
      this.copyDirectory(stylesBackup, stylesDir);
    }
    
    console.log('✅ Restored from backup');
  }

  // Clean up test files
  cleanup() {
    if (fs.existsSync(this.testDir)) {
      fs.rmSync(this.testDir, { recursive: true, force: true });
    }
    console.log('🧹 Cleanup completed');
  }
}

// CLI interface
if (require.main === module) {
  const tester = new RefactorTester();
  
  const command = process.argv[2];
  
  switch (command) {
    case 'test':
      tester.runTests();
      break;
    case 'dry-run':
      tester.dryRun();
      break;
    case 'backup':
      tester.createBackup();
      break;
    case 'restore':
      tester.restore();
      break;
    case 'cleanup':
      tester.cleanup();
      break;
    default:
      console.log(`Usage: node test_refactor_system.js [test|dry-run|backup|restore|cleanup]
      
Commands:
• test     - Run comprehensive tests
• dry-run  - Analyze without making changes
• backup   - Create backup of current files
• restore  - Restore from backup
• cleanup  - Remove test files`);
  }
}

module.exports = RefactorTester; 