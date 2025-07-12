#!/usr/bin/env node
import fs from 'fs';
import path from 'path';
import { fileURLToPath } from 'url';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

// REAL CSS classes that actually exist in the codebase
const REAL_CSS_MAPPINGS = {
  // Grid System - REAL classes from grid.css
  'display: grid': 'grid',
  'grid-template-columns: repeat(1, 1fr)': 'grid grid--cols-1',
  'grid-template-columns: repeat(2, 1fr)': 'grid grid--cols-2', 
  'grid-template-columns: repeat(3, 1fr)': 'grid grid--cols-3',
  'grid-template-columns: repeat(4, 1fr)': 'grid grid--cols-4',
  'grid-template-columns: repeat(5, 1fr)': 'grid grid--cols-5',
  'grid-template-columns: repeat(6, 1fr)': 'grid grid--cols-6',
  'grid-template-columns: repeat(auto-fit, minmax(200px, 1fr))': 'grid grid--responsive-sm',
  'grid-template-columns: repeat(auto-fit, minmax(250px, 1fr))': 'grid grid--responsive-md',
  'grid-template-columns: repeat(auto-fit, minmax(300px, 1fr))': 'grid grid--responsive-lg',
  'grid-template-columns: repeat(auto-fit, minmax(400px, 1fr))': 'grid grid--responsive-xl',

  // Flexbox - REAL classes from grid.css
  'display: flex': 'flex',
  'display: flex; justify-content: center; align-items: center': 'flex flex--center',
  'display: flex; justify-content: space-between; align-items: center': 'flex flex--between',
  'display: flex; flex-direction: column': 'flex flex--column',
  'justify-content: center': 'flex--center',
  'justify-content: space-between': 'flex--between',
  'align-items: center': 'flex--center',
  'flex-direction: column': 'flex--column',

  // Gap - REAL classes from grid.css
  'gap: 0.5rem': 'gap-sm',
  'gap: 1rem': 'gap-md', 
  'gap: 1.5rem': 'gap-lg',
  'gap: 2rem': 'gap-xl',
  'gap: 8px': 'gap-sm',
  'gap: 16px': 'gap-md',
  'gap: 24px': 'gap-lg',
  'gap: 32px': 'gap-xl',

  // Spacing - REAL classes from spacing.css
  'margin-top: 0': 'mt-0',
  'margin-top: 0.25rem': 'mt-1',
  'margin-top: 0.5rem': 'mt-2',
  'margin-top: 1rem': 'mt-3',
  'margin-top: 1.5rem': 'mt-4',
  'margin-top: 2rem': 'mt-5',
  'margin-top: 4px': 'mt-1',
  'margin-top: 8px': 'mt-2',
  'margin-top: 16px': 'mt-3',
  'margin-top: 24px': 'mt-4',
  'margin-top: 32px': 'mt-5',

  'margin-bottom: 0': 'mb-0',
  'margin-bottom: 0.25rem': 'mb-1',
  'margin-bottom: 0.5rem': 'mb-2',
  'margin-bottom: 1rem': 'mb-3',
  'margin-bottom: 1.5rem': 'mb-4',
  'margin-bottom: 2rem': 'mb-5',
  'margin-bottom: 4px': 'mb-1',
  'margin-bottom: 8px': 'mb-2',
  'margin-bottom: 16px': 'mb-3',
  'margin-bottom: 24px': 'mb-4',
  'margin-bottom: 32px': 'mb-5',

  'padding: 0.25rem': 'p-1',
  'padding: 0.5rem': 'p-2',
  'padding: 1rem': 'p-3',
  'padding: 1.5rem': 'p-4',
  'padding: 4px': 'p-1',
  'padding: 8px': 'p-2',
  'padding: 16px': 'p-3',
  'padding: 24px': 'p-4',

  // Background Colors - REAL classes from colors.css
  'background-color: #E85A4F': 'bg-primary',
  'background-color: #2C3E50': 'bg-secondary',
  'background-color: #10B981': 'bg-success',
  'background-color: #F59E0B': 'bg-warning',
  'background-color: #EF4444': 'bg-error',
  'background-color: #f8fafc': 'bg-subtle',
  'background-color: #FFFFFF': 'bg-white',
  'background-color: #F9FAFB': 'bg-gray-50',
  'background-color: #F3F4F6': 'bg-gray-100',
  'background: #E85A4F': 'bg-primary',
  'background: #2C3E50': 'bg-secondary',
  'background: #10B981': 'bg-success',
  'background: #F59E0B': 'bg-warning',
  'background: #EF4444': 'bg-error',
  'background: #f8fafc': 'bg-subtle',
  'background: #FFFFFF': 'bg-white',
  'background: #F9FAFB': 'bg-gray-50',
  'background: #F3F4F6': 'bg-gray-100',

  // Text Colors - REAL classes from text.css
  'color: #111827': 'text-primary',
  'color: #4B5563': 'text-secondary',
  'color: #10B981': 'text-success',
  'color: #F59E0B': 'text-warning',
  'color: #EF4444': 'text-error',

  // Text Alignment - REAL classes from text.css
  'text-align: center': 'text-center',
  'text-align: left': 'text-left',
  'text-align: right': 'text-right',

  // Font Weight - REAL classes from text.css
  'font-weight: 400': 'font-normal',
  'font-weight: 500': 'font-medium',
  'font-weight: 600': 'font-semibold',
  'font-weight: 700': 'font-bold',
  'font-weight: bold': 'font-bold',
  'font-weight: normal': 'font-normal',

  // Font Size - REAL classes from text.css
  'font-size: 0.875rem': 'text-sm',
  'font-size: 1rem': 'text-base',
  'font-size: 1.125rem': 'text-lg',
  'font-size: 1.25rem': 'text-xl',
  'font-size: 14px': 'text-sm',
  'font-size: 16px': 'text-base',
  'font-size: 18px': 'text-lg',
  'font-size: 20px': 'text-xl',

  // Border Colors - REAL classes from colors.css
  'border-color: #E85A4F': 'border-primary',
  'border-color: #2C3E50': 'border-secondary',
  'border-color: #10B981': 'border-success',
  'border-color: #F59E0B': 'border-warning',
  'border-color: #EF4444': 'border-error',

  // Layout - REAL classes from layout.css
  'width: 100%': 'w-full',
  'height: 100%': 'h-full',
  'position: relative': 'relative',
  'position: absolute': 'absolute',
  'cursor: pointer': 'cursor-pointer',
  'display: none': 'hidden',
  'display: block': 'visible',
};

// Card patterns - REAL classes from card.css
const CARD_PATTERNS = {
  // Basic card with border-left
  'background: var(--background); border: 1px solid var(--border-color); border-radius: var(--border-radius); padding: var(--spacing-lg); border-left: 4px solid': 'card--content',
  // Metric card (centered)
  'background: var(--background); border: 1px solid var(--border-color); border-radius: var(--border-radius); padding: var(--spacing-lg); text-align: center; border-left: 4px solid': 'card--metric',
  // Persona card (centered, top border)
  'background: var(--background); border: 1px solid var(--border-color); border-radius: var(--border-radius); padding: var(--spacing-lg); text-align: center; border-top: 4px solid': 'card--persona',
  // Basic card
  'background: var(--background); border: 1px solid var(--border-color); border-radius: var(--border-radius); padding: var(--spacing-lg)': 'card',
};

// Dashboard component patterns - REAL classes from dashboard.css
const DASHBOARD_PATTERNS = {
  'background: var(--background); border: 1px solid var(--border-color); border-radius: var(--border-radius-lg); padding: var(--spacing-lg)': 'insights-box',
  'margin-bottom: var(--spacing-2xl)': 'section',
  'max-width: 1400px; margin: 0 auto; padding: var(--spacing-lg)': 'page-container',
};

function normalizeStyle(style) {
  return style.trim()
    .replace(/\s*;\s*/g, '; ')
    .replace(/\s*:\s*/g, ': ')
    .replace(/\s+/g, ' ')
    .replace(/;$/, '');
}

function findStyleMapping(styleString) {
  const normalized = normalizeStyle(styleString);
  
  // Check exact mappings first
  if (REAL_CSS_MAPPINGS[normalized]) {
    return REAL_CSS_MAPPINGS[normalized];
  }
  
  // Check card patterns
  for (const [pattern, className] of Object.entries(CARD_PATTERNS)) {
    if (normalized.includes(pattern)) {
      return className;
    }
  }
  
  // Check dashboard patterns
  for (const [pattern, className] of Object.entries(DASHBOARD_PATTERNS)) {
    if (normalized.includes(pattern)) {
      return className;
    }
  }
  
  // Check partial matches for complex styles
  const styles = normalized.split('; ');
  let classes = [];
  
  for (const style of styles) {
    if (REAL_CSS_MAPPINGS[style]) {
      classes.push(REAL_CSS_MAPPINGS[style]);
    }
  }
  
  if (classes.length > 0) {
    return classes.join(' ');
  }
  
  return null;
}

function analyzeInlineStyles(filePath) {
  const content = fs.readFileSync(filePath, 'utf8');
  const inlineStyleRegex = /style=\{\{[^}]*(?:\}(?!\})[^}]*)*\}\}/gs;
  const matches = content.match(inlineStyleRegex) || [];
  
  const results = {
    total: matches.length,
    mappable: 0,
    unmappable: 0,
    styles: []
  };
  
  matches.forEach(match => {
    const styleContent = match.replace(/style=\{\{|\}\}/g, '').trim();
    const mapping = findStyleMapping(styleContent);
    
    if (mapping) {
      results.mappable++;
      results.styles.push({
        original: match,
        styleContent,
        mapping,
        mappable: true
      });
    } else {
      results.unmappable++;
      results.styles.push({
        original: match,
        styleContent,
        mapping: null,
        mappable: false
      });
    }
  });
  
  return results;
}

function refactorFile(filePath) {
  let content = fs.readFileSync(filePath, 'utf8');
  let replacements = 0;
  
  const analysis = analyzeInlineStyles(filePath);
  
  for (const style of analysis.styles) {
    if (style.mappable) {
      // Replace the inline style with className
      const classNameReplacement = `className="${style.mapping}"`;
      content = content.replace(style.original, classNameReplacement);
      replacements++;
    }
  }
  
  fs.writeFileSync(filePath, content);
  return {
    replacements,
    total: analysis.total,
    mappable: analysis.mappable,
    unmappable: analysis.unmappable
  };
}

function main() {
  const webSrcPath = path.join(__dirname, '..', '..', 'web', 'src');
  const pagesPath = path.join(webSrcPath, 'pages');
  
  if (!fs.existsSync(pagesPath)) {
    console.error('❌ Pages directory not found:', pagesPath);
    process.exit(1);
  }
  
  const files = fs.readdirSync(pagesPath).filter(file => file.endsWith('.tsx'));
  
  if (files.length === 0) {
    console.error('❌ No .tsx files found in pages directory');
    process.exit(1);
  }
  
  console.log('🔧 REFACTORING INLINE STYLES TO REAL CSS CLASSES');
  console.log('===============================================');
  
  let totalReplacements = 0;
  let totalAnalyzed = 0;
  let totalMappable = 0;
  let totalUnmappable = 0;
  
  for (const file of files) {
    const filePath = path.join(pagesPath, file);
    console.log(`\n📄 Processing: ${file}`);
    
    const result = refactorFile(filePath);
    
    totalReplacements += result.replacements;
    totalAnalyzed += result.total;
    totalMappable += result.mappable;
    totalUnmappable += result.unmappable;
    
    console.log(`   ✅ Replaced: ${result.replacements}/${result.total} inline styles`);
    console.log(`   📊 Mappable: ${result.mappable}, Unmappable: ${result.unmappable}`);
    
    if (result.mappable > 0) {
      const percentage = ((result.mappable / result.total) * 100).toFixed(1);
      console.log(`   🎯 Success rate: ${percentage}%`);
    }
  }
  
  console.log('\n🎉 REFACTOR COMPLETE!');
  console.log('====================');
  console.log(`📊 Total inline styles found: ${totalAnalyzed}`);
  console.log(`✅ Successfully mapped: ${totalMappable}`);
  console.log(`❌ Could not map: ${totalUnmappable}`);
  console.log(`🔄 Total replacements made: ${totalReplacements}`);
  
  if (totalMappable > 0) {
    const overallPercentage = ((totalMappable / totalAnalyzed) * 100).toFixed(1);
    console.log(`🎯 Overall success rate: ${overallPercentage}%`);
  }
  
  console.log('\n🎨 All mappings use REAL CSS classes from your existing design system!');
  console.log('🔍 Check the updated files and run your dev server to see the results.');
}

if (import.meta.url === `file://${process.argv[1]}`) {
  main();
} 