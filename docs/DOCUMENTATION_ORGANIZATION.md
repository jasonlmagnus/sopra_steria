# Documentation Organization Guide

**Created:** 2025-01-27  
**Last Updated:** 2025-01-27

## Overview

This document explains the organization of all documentation in the Sopra project, including where files are located and why they were placed there.

## 📁 Documentation Structure

```
docs/
├── refactoring/                    # Current refactoring documentation
│   ├── README.md                  # Complete CSS refactoring system guide
│   ├── REFACTOR_SYSTEM_GUIDE.md   # Detailed refactoring system documentation
│   └── QUICK_REFERENCE.md         # Quick reference for refactoring tools
├── legacy/                        # Legacy and historical documentation
│   ├── NODE_REFACTOR_LOG.md       # Node.js migration progress log (completed)
│   ├── node_refactor.md           # Node.js migration plan (completed)
│   ├── detect_runtime.py          # Legacy Python utility
│   ├── CODEX_READ_THIS_PYTHON_PROJECT.md
│   ├── improvement_plan.md
│   └── improvement_prompts.md
├── react_evidence_audit_report.md # Current React audit documentation
├── react_evidence_implementation_plan.md
├── react_vs_streamlit_gap.md      # Current gap analysis
├── social-media-analysis-improvements.md
├── style_plan.md                  # Current styling documentation
├── visual_brand_hygiene_comparison_analysis.md
├── visual_brand_hygiene_dashboard_specification.md
└── DOCUMENTATION_ORGANIZATION.md  # This file
```

## 📋 File Classification Criteria

### **Current Documentation** → `docs/` (root level)
- **Active and relevant** to current development
- **Currently being used** by the team
- **Reflects current state** of the project
- **Contains actionable information** for ongoing work

### **Current Refactoring Documentation** → `docs/refactoring/`
- **CSS refactoring system** documentation
- **Currently functional** and actively used
- **Contains working scripts** and tools
- **Provides immediate value** for styling work

### **Legacy Documentation** → `docs/legacy/`
- **Completed projects** (e.g., Node.js migration)
- **Historical reference** material
- **Outdated but preserved** for context
- **No longer actively used** in current development

## 🔍 Documentation Review Results

### **Moved to `docs/refactoring/` (Current & Relevant)**

| File | Reason for Current Status |
|------|---------------------------|
| `REFACTOR_SYSTEM_GUIDE.md` | **Active CSS refactoring system** - Currently functional and used |
| `README.md` | **Complete system documentation** - Comprehensive guide for refactoring tools |
| `QUICK_REFERENCE.md` | **Quick reference guide** - Frequently used commands and workflows |

### **Moved to `docs/legacy/` (Completed/Historical)**

| File | Reason for Legacy Status |
|------|-------------------------|
| `NODE_REFACTOR_LOG.md` | **Completed migration** - Node.js migration is finished |
| `node_refactor.md` | **Completed project** - Migration plan fully executed |

### **Remained in `docs/` (Root Level - Current)**

| File | Reason for Current Status |
|------|---------------------------|
| `react_evidence_audit_report.md` | **Active audit documentation** - Current React implementation |
| `react_evidence_implementation_plan.md` | **Active implementation plan** - Ongoing React development |
| `react_vs_streamlit_gap.md` | **Active gap analysis** - Current comparison work |
| `social-media-analysis-improvements.md` | **Active improvements** - Ongoing social media work |
| `style_plan.md` | **Current styling plan** - Active styling work |
| `visual_brand_hygiene_*.md` | **Current brand hygiene work** - Active brand analysis |

## 🎯 Decision Making Process

### **Current vs Legacy Classification**

**Current Documentation:**
- ✅ **Functionally relevant** to ongoing work
- ✅ **Contains actionable information**
- ✅ **Reflects current project state**
- ✅ **Used by active development team**

**Legacy Documentation:**
- ❌ **Completed projects** or milestones
- ❌ **Historical reference only**
- ❌ **No longer actively maintained**
- ❌ **Preserved for context/history**

### **Refactoring Documentation Special Case**

The CSS refactoring system documentation was moved to `docs/refactoring/` because:
- **Self-contained system** with its own tools and scripts
- **Specialized domain** (CSS refactoring) separate from general development
- **Comprehensive documentation** that deserves its own section
- **Active and functional** system that needs clear organization

## 📖 How to Use This Organization

### **For Current Development**
1. **Check `docs/` (root)** for general project documentation
2. **Check `docs/refactoring/`** for CSS/styling related work
3. **Use `docs/legacy/`** only for historical reference

### **For New Documentation**
1. **Current work** → `docs/` (root level)
2. **Specialized systems** → `docs/[system-name]/`
3. **Completed work** → `docs/legacy/`

### **For Documentation Maintenance**
1. **Review quarterly** to reclassify as needed
2. **Move completed work** to legacy
3. **Update this guide** when reorganizing

## 🔄 Maintenance Schedule

- **Monthly**: Review new documentation for proper placement
- **Quarterly**: Reclassify documentation as current/legacy
- **Annually**: Clean up legacy documentation if needed

---

**Note**: This organization ensures that current, actionable documentation is easily accessible while preserving historical context for completed work. 