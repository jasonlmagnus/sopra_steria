# CSS Refactoring System - Quick Reference

**Created:** 2025-01-27

## 🚀 Quick Start

### 1. Verify System
```bash
node refactor/scripts/verify_refactor_system.js
```

### 2. Audit Current State
```bash
node refactor/scripts/audit_inline_styles.js
```

### 3. Run Full Refactoring
```bash
node refactor/scripts/inline_style_refactor_system.js
```

### 4. Test Results
```bash
node refactor/scripts/test_refactor_system.js
```

## 📁 Folder Structure

```
refactor/
├── backups/           # Original files before refactoring
├── test-outputs/      # Test results and audit data
├── scripts/           # All refactoring automation scripts
├── documentation/     # System guides and logs
├── config/           # Configuration files
├── README.md         # Complete system documentation
└── QUICK_REFERENCE.md # This file
```

## 🔧 Common Commands

### System Verification
```bash
# Verify all components are properly organized
node refactor/scripts/verify_refactor_system.js
```

### Auditing
```bash
# Audit inline styles in the codebase
node refactor/scripts/audit_inline_styles.js

# View audit results
cat refactor/test-outputs/inline_styles_audit.csv
```

### Refactoring
```bash
# Run the main refactoring system
node refactor/scripts/inline_style_refactor_system.js

# Run enhanced refactoring processor
node refactor/scripts/proper_inline_style_refactor.js
```

### Testing & Validation
```bash
# Test refactoring results
node refactor/scripts/test_refactor_system.js

# Fix any broken CSS
node refactor/scripts/fix_broken_css.js
```

### Backup & Restore
```bash
# Restore from backup if needed
node refactor/scripts/restore_backup.js
```

## 📊 Script Overview

| Script | Purpose | When to Use |
|--------|---------|-------------|
| `verify_refactor_system.js` | System verification | Before starting any work |
| `audit_inline_styles.js` | Find inline styles | To assess current state |
| `inline_style_refactor_system.js` | Main refactoring | Primary refactoring process |
| `proper_inline_style_refactor.js` | Enhanced processing | For complex style patterns |
| `fix_broken_css.js` | CSS repair | When issues are found |
| `test_refactor_system.js` | Validation | After refactoring |
| `restore_backup.js` | Backup restoration | If rollback is needed |

## 🎯 Workflows

### New Refactoring Session
1. `verify_refactor_system.js` - Ensure system is ready
2. `audit_inline_styles.js` - Assess current state
3. `inline_style_refactor_system.js` - Run refactoring
4. `test_refactor_system.js` - Validate results
5. `fix_broken_css.js` - Fix any issues (if needed)

### Maintenance Check
1. `verify_refactor_system.js` - Check system integrity
2. `audit_inline_styles.js` - Monitor inline style usage
3. Review audit results in `test-outputs/`

### Troubleshooting
1. `verify_refactor_system.js` - Identify system issues
2. `fix_broken_css.js` - Repair CSS problems
3. `restore_backup.js` - Rollback if necessary

## 📈 Monitoring

### Key Metrics to Track
- **Inline Style Count**: Should decrease over time
- **CSS File Sizes**: Monitor for optimization opportunities
- **Test Results**: Ensure refactoring maintains functionality
- **Audit Reports**: Track progress and identify patterns

### Files to Monitor
- `refactor/test-outputs/inline_styles_audit.csv` - Audit results
- `refactor/backups/` - Backup integrity
- `refactor/config/refactor_config.json` - Configuration changes

## 🚨 Troubleshooting

### Common Issues

**System Verification Fails**
- Check file permissions
- Ensure all scripts are in correct locations
- Verify configuration file is valid JSON

**Refactoring Errors**
- Check backup files exist
- Verify source files are accessible
- Review error logs for specific issues

**CSS Issues After Refactoring**
- Run `fix_broken_css.js`
- Check for syntax errors
- Validate CSS against web standards

### Emergency Procedures

**Complete Rollback**
```bash
node refactor/scripts/restore_backup.js
```

**System Reset**
```bash
# Verify system integrity
node refactor/scripts/verify_refactor_system.js

# If verification fails, check documentation
cat refactor/README.md
```

## 📚 Documentation

- **Complete Guide**: `refactor/README.md`
- **System Guide**: `refactor/documentation/REFACTOR_SYSTEM_GUIDE.md`
- **Node.js Log**: `refactor/documentation/NODE_REFACTOR_LOG.md`
- **Node.js Docs**: `refactor/documentation/node_refactor.md`

## 🔄 Version Control

The refactoring system maintains:
- **Backups**: Original files before refactoring
- **Audit Trails**: Records of all changes
- **Test Results**: Validation of refactoring outcomes
- **Configuration**: Settings and parameters

---

**Need Help?** Check the main `README.md` for detailed documentation and troubleshooting guides. 