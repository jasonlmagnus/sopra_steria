# Project Backlog: Persona Experience & Brand Audit Tool

## High Priority Items

### 1. **Move Quantitative Methodology to YAML Configuration**

- **Current Issue**: The entire methodology (tiers, criteria, weights) is hardcoded in `audit_tool/methodology_parser.py`
- **Goal**: Extract all methodology data into a structured YAML file for easy editing and maintenance
- **Tasks**:
  - Create `methodology.yaml` with all tier definitions, criteria, and weights
  - Update `MethodologyParser` to read from YAML instead of hardcoded data
  - Add validation for YAML structure
  - Update documentation to reflect new configuration approach

### 2. **Upgrade UI for Real-time Report Viewing**

- **Current Issue**: Reports are only visible after the entire audit completes
- **Goal**: Allow users to see individual reports as they are created during the audit process
- **Tasks**:
  - Implement file system watching to detect new report files
  - Add live refresh capability to the results section
  - Show progress indicators for individual URL completion
  - Display partial results while audit is still running
  - Add expandable sections for each completed URL

## Medium Priority Items

### 3. **Fix Dashboard Launch Script Port Conflict**

- **Current Issue**: Dashboard launches on port 8502 instead of default 8501
- **Goal**: Ensure consistent port usage and handle port conflicts gracefully
- **Tasks**:
  - Update `launch_dashboard.sh` to use standard port 8501
  - Add port conflict detection and automatic fallback
  - Update documentation with correct port information

### 4. **Improve Error Handling in UI**

- **Goal**: Better user experience when audits fail
- **Tasks**:
  - Add detailed error messages for common failure scenarios
  - Implement retry mechanism for failed audits
  - Add validation for uploaded persona files and URL lists
  - Show clear status indicators for audit progress

### 5. **Add Audit History and Comparison**

- **Goal**: Allow users to track audit results over time
- **Tasks**:
  - Implement timestamped audit storage
  - Add UI for selecting and comparing historical audits
  - Create trend analysis and improvement tracking
  - Add export functionality for audit results

## Low Priority Items

### 6. **Performance Optimizations**

- Add caching for repeated URL audits
- Implement parallel processing for multiple URLs
- Optimize AI API usage to reduce costs

### 7. **Enhanced Reporting Features**

- Add PDF export for audit reports
- Create executive summary dashboard with charts
- Implement custom report templates
- Add email notification for completed audits

### 8. **Configuration Management**

- Create settings page in UI for methodology customization
- Add persona template library
- Implement audit configuration presets
- Add API key management interface

---

**Last Updated**: 2025-06-21
**Status**: Active Development
