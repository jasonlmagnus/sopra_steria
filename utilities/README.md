# Utilities

**Created:** 2025-01-27  
**Purpose:** Utility scripts for automation, testing, and data analysis

## 📋 **Scripts Overview**

### **1. `analyze_strategic_data.py`**
**Purpose:** Cross-reference React TSX data requirements with actual data sources  
**Usage:** `python3 analyze_strategic_data.py`  
**Output:** `strategic_data_analysis_report.txt`  
**Status:** ✅ **Active** - Analyzes data alignment between frontend and backend

**What it does:**
- Extracts field references from `StrategicRecommendations.tsx`
- Analyzes CSV data, metrics calculator output, social media data
- Identifies fake fields (no real data source) vs real fields
- Provides actionable recommendations for data alignment

### **2. `generate_html_report.py`**
**Purpose:** CLI wrapper for HTML report generation  
**Usage:** `python3 generate_html_report.py <persona_name|consolidated> [output_path]`  
**Output:** HTML reports in `html_reports/` directory  
**Status:** ✅ **Active** - Provides convenient CLI access to HTML report generation

**Examples:**
```bash
# Generate report for specific persona
python3 generate_html_report.py "The Technical Influencer"

# Generate consolidated report across all personas
python3 generate_html_report.py consolidated

# Generate report with custom output path
python3 generate_html_report.py "The Technical Influencer" custom_report.html
```

**Available Personas:**
- The Benelux Cybersecurity Decision Maker
- The Benelux Strategic Business Leader (C-Suite Executive)
- The Benelux Transformation Programme Leader
- The Technical Influencer
- The_BENELUX_Technology_Innovation_Leader

### **3. `test_html_generator.py`**
**Purpose:** Test script for HTML report generator functionality  
**Usage:** `python3 test_html_generator.py`  
**Output:** Test report (`test_report.html`)  
**Status:** ✅ **Active** - Development/testing utility

**What it tests:**
- HTMLReportGenerator initialization
- Report generation for "The Technical Influencer" persona
- Template loading and rendering
- Data processing pipeline

## 🔧 **Technical Details**

### **Dependencies**
All utilities import from the main `audit_tool` package:
- `audit_tool.html_report_generator` - Core HTML report generation
- `audit_tool` modules - Various audit tool functionality

### **Path Resolution**
Utilities automatically handle path resolution for:
- Template directories (`audit_tool/templates`)
- Data files (`audit_data/unified_audit_data.csv`)
- Output directories (`html_reports/`)

### **Execution Context**
Scripts work from multiple execution contexts:
- Project root directory
- `utilities/` directory
- `audit_tool/` directory

## 🚀 **Usage Examples**

### **Data Analysis**
```bash
cd utilities
python3 analyze_strategic_data.py
# Generates strategic_data_analysis_report.txt
```

### **HTML Report Generation**
```bash
cd utilities
python3 generate_html_report.py consolidated
# Generates consolidated HTML report
```

### **Testing**
```bash
cd utilities
python3 test_html_generator.py
# Tests HTML report generation functionality
```

## 📊 **Integration**

### **With React Dashboard**
- `ReportsExport.tsx` - Uses HTML report generation via API
- `AuditReports.tsx` - Views generated HTML reports

### **With FastAPI Service**
- `/api/reports/html` endpoint - Uses HTMLReportGenerator
- `/api/html-reports` endpoint - Lists available reports

### **With Streamlit Dashboard**
- Reports Export page - Uses HTMLReportGenerator
- Audit Reports page - Regenerates reports

## 🔍 **Troubleshooting**

### **Common Issues**

**Template Not Found Error:**
```
'brand_experience_report.html' not found in search path: 'audit_tool/templates'
```
**Solution:** Ensure `audit_tool/templates/` directory exists with required template files.

**Data File Not Found:**
```
Error: unified_audit_data.csv not found in audit_data directory
```
**Solution:** Ensure `audit_data/unified_audit_data.csv` exists and is accessible.

**Import Errors:**
```
ImportError: No module named 'audit_tool'
```
**Solution:** Run from project root or ensure Python path includes project root.

## 📈 **Future Enhancements**

### **Planned Improvements**
- [ ] Add more comprehensive testing utilities
- [ ] Create batch processing scripts
- [ ] Add data validation utilities
- [ ] Create automated report scheduling

### **Integration Opportunities**
- [ ] CI/CD pipeline integration
- [ ] Automated testing workflows
- [ ] Data quality monitoring
- [ ] Performance benchmarking

---

**Note:** All utilities are designed to work independently while maintaining compatibility with the main audit tool system. 