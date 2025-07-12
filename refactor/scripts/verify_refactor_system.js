#!/usr/bin/env node

/**
 * Refactor System Verification Script
 * 
 * This script verifies that all refactoring components are properly organized
 * and functional within the refactor folder structure.
 */

const fs = require('fs');
const path = require('path');

// ANSI color codes for console output
const colors = {
    green: '\x1b[32m',
    red: '\x1b[31m',
    yellow: '\x1b[33m',
    blue: '\x1b[34m',
    reset: '\x1b[0m',
    bold: '\x1b[1m'
};

function log(message, color = 'reset') {
    console.log(`${colors[color]}${message}${colors.reset}`);
}

function logSection(title) {
    console.log('\n' + '='.repeat(60));
    log(title, 'bold');
    console.log('='.repeat(60));
}

function checkFile(filePath, description) {
    try {
        if (fs.existsSync(filePath)) {
            const stats = fs.statSync(filePath);
            log(`✓ ${description}`, 'green');
            log(`  Path: ${filePath}`, 'blue');
            log(`  Size: ${(stats.size / 1024).toFixed(2)} KB`, 'blue');
            return true;
        } else {
            log(`✗ ${description} - File not found`, 'red');
            log(`  Expected: ${filePath}`, 'red');
            return false;
        }
    } catch (error) {
        log(`✗ ${description} - Error checking file`, 'red');
        log(`  Error: ${error.message}`, 'red');
        return false;
    }
}

function checkDirectory(dirPath, description) {
    try {
        if (fs.existsSync(dirPath)) {
            const stats = fs.statSync(dirPath);
            if (stats.isDirectory()) {
                const files = fs.readdirSync(dirPath);
                log(`✓ ${description}`, 'green');
                log(`  Path: ${dirPath}`, 'blue');
                log(`  Files: ${files.length}`, 'blue');
                return { exists: true, fileCount: files.length };
            } else {
                log(`✗ ${description} - Not a directory`, 'red');
                return { exists: false, fileCount: 0 };
            }
        } else {
            log(`✗ ${description} - Directory not found`, 'red');
            return { exists: false, fileCount: 0 };
        }
    } catch (error) {
        log(`✗ ${description} - Error checking directory`, 'red');
        log(`  Error: ${error.message}`, 'red');
        return { exists: false, fileCount: 0 };
    }
}

function verifyScripts() {
    logSection('VERIFYING REFACTORING SCRIPTS');
    
    const scripts = [
        { path: 'refactor/scripts/inline_style_refactor_system.js', desc: 'Main refactoring orchestrator' },
        { path: 'refactor/scripts/proper_inline_style_refactor.js', desc: 'Enhanced inline style processor' },
        { path: 'refactor/scripts/fix_broken_css.js', desc: 'CSS repair utility' },
        { path: 'refactor/scripts/audit_inline_styles.js', desc: 'Inline styles auditor' },
        { path: 'refactor/scripts/test_refactor_system.js', desc: 'Testing framework' },
        { path: 'refactor/scripts/restore_backup.js', desc: 'Backup restoration utility' }
    ];
    
    let passed = 0;
    scripts.forEach(script => {
        if (checkFile(script.path, script.desc)) {
            passed++;
        }
    });
    
    log(`\nScripts: ${passed}/${scripts.length} verified`, passed === scripts.length ? 'green' : 'yellow');
    return passed === scripts.length;
}

function verifyDocumentation() {
    logSection('VERIFYING DOCUMENTATION');
    
    const docs = [
        { path: 'refactor/README.md', desc: 'Main system documentation' },
        { path: 'refactor/documentation/REFACTOR_SYSTEM_GUIDE.md', desc: 'System guide' },
        { path: 'refactor/documentation/NODE_REFACTOR_LOG.md', desc: 'Node.js refactor log' },
        { path: 'refactor/documentation/node_refactor.md', desc: 'Node.js refactor documentation' }
    ];
    
    let passed = 0;
    docs.forEach(doc => {
        if (checkFile(doc.path, doc.desc)) {
            passed++;
        }
    });
    
    log(`\nDocumentation: ${passed}/${docs.length} verified`, passed === docs.length ? 'green' : 'yellow');
    return passed === docs.length;
}

function verifyBackups() {
    logSection('VERIFYING BACKUP STRUCTURE');
    
    const backupDirs = [
        { path: 'refactor/backups/backup_before_refactor', desc: 'Main backup directory' },
        { path: 'refactor/backups/backup_before_refactor/pages', desc: 'Backup pages' },
        { path: 'refactor/backups/backup_before_refactor/styles', desc: 'Backup styles' },
        { path: 'refactor/backups/backup_before_refactor/refactor_2025-07-11T22-03-54-683Z', desc: 'Timestamped backup' }
    ];
    
    let passed = 0;
    backupDirs.forEach(dir => {
        const result = checkDirectory(dir.path, dir.desc);
        if (result.exists) {
            passed++;
        }
    });
    
    log(`\nBackups: ${passed}/${backupDirs.length} verified`, passed === backupDirs.length ? 'green' : 'yellow');
    return passed === backupDirs.length;
}

function verifyTestOutputs() {
    logSection('VERIFYING TEST OUTPUTS');
    
    const testItems = [
        { path: 'refactor/test-outputs/test_refactor', desc: 'Test components directory' },
        { path: 'refactor/test-outputs/inline_styles_audit.csv', desc: 'Audit results' }
    ];
    
    let passed = 0;
    testItems.forEach(item => {
        if (fs.existsSync(item.path)) {
            const stats = fs.statSync(item.path);
            if (stats.isDirectory()) {
                const result = checkDirectory(item.path, item.desc);
                if (result.exists) passed++;
            } else {
                if (checkFile(item.path, item.desc)) {
                    passed++;
                }
            }
        } else {
            log(`✗ ${item.desc} - Not found`, 'red');
        }
    });
    
    log(`\nTest Outputs: ${passed}/${testItems.length} verified`, passed === testItems.length ? 'green' : 'yellow');
    return passed === testItems.length;
}

function verifyConfiguration() {
    logSection('VERIFYING CONFIGURATION');
    
    const configs = [
        { path: 'refactor/config/refactor_config.json', desc: 'Main configuration file' }
    ];
    
    let passed = 0;
    configs.forEach(config => {
        if (checkFile(config.path, config.desc)) {
            // Try to parse JSON to verify it's valid
            try {
                const content = fs.readFileSync(config.path, 'utf8');
                JSON.parse(content);
                log(`  ✓ Valid JSON configuration`, 'green');
                passed++;
            } catch (error) {
                log(`  ✗ Invalid JSON configuration: ${error.message}`, 'red');
            }
        }
    });
    
    log(`\nConfiguration: ${passed}/${configs.length} verified`, passed === configs.length ? 'green' : 'yellow');
    return passed === configs.length;
}

function generateSystemReport() {
    logSection('SYSTEM VERIFICATION REPORT');
    
    const results = {
        scripts: verifyScripts(),
        documentation: verifyDocumentation(),
        backups: verifyBackups(),
        testOutputs: verifyTestOutputs(),
        configuration: verifyConfiguration()
    };
    
    const totalChecks = Object.keys(results).length;
    const passedChecks = Object.values(results).filter(Boolean).length;
    
    logSection('SUMMARY');
    log(`Total Checks: ${totalChecks}`, 'bold');
    log(`Passed: ${passedChecks}`, passedChecks === totalChecks ? 'green' : 'yellow');
    log(`Failed: ${totalChecks - passedChecks}`, passedChecks === totalChecks ? 'green' : 'red');
    
    if (passedChecks === totalChecks) {
        log('\n🎉 All refactoring system components are properly organized and verified!', 'green');
        log('The CSS refactoring system is ready for use.', 'green');
    } else {
        log('\n⚠️  Some components need attention. Please review the failed checks above.', 'yellow');
    }
    
    return passedChecks === totalChecks;
}

// Main execution
if (require.main === module) {
    log('CSS Refactoring System Verification', 'bold');
    log('=====================================', 'bold');
    
    const success = generateSystemReport();
    
    if (success) {
        log('\nNext steps:', 'bold');
        log('1. Run: node refactor/scripts/audit_inline_styles.js', 'blue');
        log('2. Run: node refactor/scripts/inline_style_refactor_system.js', 'blue');
        log('3. Review results in refactor/test-outputs/', 'blue');
    } else {
        log('\nPlease fix the issues above before proceeding with refactoring.', 'red');
    }
    
    process.exit(success ? 0 : 1);
}

module.exports = {
    verifyScripts,
    verifyDocumentation,
    verifyBackups,
    verifyTestOutputs,
    verifyConfiguration,
    generateSystemReport
}; 