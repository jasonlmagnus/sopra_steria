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

function copyDirectory(src, dest) {
  if (!fs.existsSync(dest)) {
    fs.mkdirSync(dest, { recursive: true });
  }
  
  const entries = fs.readdirSync(src, { withFileTypes: true });
  
  entries.forEach(entry => {
    const srcPath = path.join(src, entry.name);
    const destPath = path.join(dest, entry.name);
    
    if (entry.isDirectory()) {
      copyDirectory(srcPath, destPath);
    } else {
      fs.copyFileSync(srcPath, destPath);
    }
  });
}

function listBackups() {
  const backupDir = path.join(__dirname, '..', 'backups', 'backup_before_refactor');
  
  if (!fs.existsSync(backupDir)) {
    console.log(`${colors.yellow}No backups found.${colors.reset}`);
    return [];
  }
  
  const backups = fs.readdirSync(backupDir)
    .filter(item => fs.statSync(path.join(backupDir, item)).isDirectory())
    .sort()
    .reverse(); // Most recent first
  
  return backups;
}

function restoreFromBackup(backupName) {
      const backupPath = path.join(__dirname, '..', 'backups', 'backup_before_refactor', backupName);
  
  if (!fs.existsSync(backupPath)) {
    console.log(`${colors.red}❌ Backup not found: ${backupName}${colors.reset}`);
    return false;
  }
  
  console.log(`${colors.cyan}🔄 Restoring from backup: ${backupName}${colors.reset}`);
  
  // Restore pages
  const pagesBackup = path.join(backupPath, 'pages');
  if (fs.existsSync(pagesBackup)) {
    const pagesDir = path.join(__dirname, '..', '..', 'web', 'src', 'pages');
    if (fs.existsSync(pagesDir)) {
      fs.rmSync(pagesDir, { recursive: true, force: true });
    }
    copyDirectory(pagesBackup, pagesDir);
    console.log(`${colors.green}✅ Restored pages${colors.reset}`);
  }
  
  // Restore styles
  const stylesBackup = path.join(backupPath, 'styles');
  if (fs.existsSync(stylesBackup)) {
    const stylesDir = path.join(__dirname, '..', '..', 'web', 'src', 'styles');
    if (fs.existsSync(stylesDir)) {
      fs.rmSync(stylesDir, { recursive: true, force: true });
    }
    copyDirectory(stylesBackup, stylesDir);
    console.log(`${colors.green}✅ Restored styles${colors.reset}`);
  }
  
  console.log(`${colors.bold}${colors.green}✅ Successfully restored from backup!${colors.reset}`);
  return true;
}

// CLI interface
const command = process.argv[2];
const backupName = process.argv[3];

if (command === 'list') {
  console.log(`${colors.bold}${colors.cyan}📋 Available Backups:${colors.reset}`);
  const backups = listBackups();
  
  if (backups.length === 0) {
    console.log(`${colors.yellow}No backups found.${colors.reset}`);
  } else {
    backups.forEach((backup, index) => {
      const isRecent = index === 0;
      const marker = isRecent ? '🔥 MOST RECENT' : '';
      console.log(`${index + 1}. ${backup} ${colors.green}${marker}${colors.reset}`);
    });
    
    console.log(`\n${colors.cyan}To restore a backup: node restore_backup.js restore <backup_name>${colors.reset}`);
  }
  
} else if (command === 'restore') {
  if (!backupName) {
    console.log(`${colors.yellow}Usage: node restore_backup.js restore <backup_name>${colors.reset}`);
    console.log(`${colors.cyan}Run 'node restore_backup.js list' to see available backups.${colors.reset}`);
  } else {
    restoreFromBackup(backupName);
  }
  
} else if (command === 'latest') {
  const backups = listBackups();
  if (backups.length > 0) {
    restoreFromBackup(backups[0]);
  } else {
    console.log(`${colors.yellow}No backups available to restore.${colors.reset}`);
  }
  
} else {
  console.log(`${colors.bold}${colors.cyan}🔄 Backup Restore Tool${colors.reset}

Commands:
• ${colors.green}list${colors.reset}           - List all available backups
• ${colors.green}restore <name>${colors.reset}  - Restore from specific backup
• ${colors.green}latest${colors.reset}          - Restore from most recent backup

Examples:
node restore_backup.js list
node restore_backup.js restore refactor_2024-01-15T10-30-00-000Z
node restore_backup.js latest`);
} 