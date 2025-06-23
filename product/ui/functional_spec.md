_Status: Active • Last-verified: 2025-06-22 • Owner: @frontend_dev_

# Functional Specification: Brand Audit Dashboard UI

## 1. Overview

The dashboard is a multi-page Streamlit application. Pages are:

1. **Run Audit** – upload persona & URLs, trigger pipeline, live log, post-processing with "ADD TO DATABASE" workflow.
2. **Executive Overview** – high-level KPIs for selected run(s).
3. **Persona Comparison** – radar, heatmap.
4. **Criteria Explorer** – histogram + evidence.
5. **Priority Actions** – quick wins & critical gaps.
6. **Journey Consistency** – journey ribbon.
7. **Gating Breaches** – compliance table.
8. **Evidence Gallery** – quote browser.
9. **Run History** – trend charts.
10. **Raw Data** – DataFrame viewer + export.

## 2. Inputs

| Name              | Source                                   | Format  |
| ----------------- | ---------------------------------------- | ------- |
| Run dataset       | `audit_runs/<run_id>/page_facts.parquet` | Parquet |
| Run manifest      | `run_manifest.json`                      | JSON    |
| Strategic summary | `strategic_summary.json`                 | JSON    |
| Methodology       | `audit_tool/config/methodology.yaml`     | YAML    |

## 3. Core Functional Behaviour

### 3.1 Data Loading

- Use `st.cache_resource` to load Parquet & JSON once per session.
- Expose `load_run(run_id)` utility returning pandas DataFrames.

### 3.2 Global Filters

- **Persona multiselect**
- **Tier/category multiselect**
- **Score range slider**
  Filters stored in `st.session_state` and applied across pages.

### 3.3 Page Interactions

| Page              | Key interactions                                                           |
| ----------------- | -------------------------------------------------------------------------- |
| Run Audit         | Start/stop buttons; real-time log poll every 1s                            |
| Executive         | Hover tooltips on KPI tiles; click descriptor to jump to Criteria Explorer |
| Criteria Explorer | Click row → open evidence modal                                            |
| Evidence Gallery  | Pagination & copy-to-clipboard                                             |
| History           | Dropdown of runs, multi-select for overlay charts                          |

### 3.4 Run Audit Page Workflow

The Run Audit page implements a comprehensive two-phase workflow:

**Phase 1: Audit Execution**

- **File Upload**: Persona markdown file upload with validation
- **URL Input**: Text area or file upload for URLs to audit
- **Model Selection**: Choice between OpenAI (cost-effective) and Anthropic (premium quality)
- **Live Execution**: Real-time progress with streaming log output
- **Completion Notification**: Success message with balloons animation

**Phase 2: Post-Processing ("ADD TO DATABASE")**

- **Automatic Detection**: System checks if audit output is already processed
- **Status Indicator**: Shows "Already processed" vs "Raw files only"
- **Processing Button**: Prominent "ADD TO DATABASE" button appears after audit completion
- **Live Progress**: Progress bar with step-by-step status updates:
  - 10% - Importing post-processor
  - 20% - Initializing processor
  - 30% - Validating audit output
  - 40% - Classifying page tiers
  - 60% - Processing backfill data
  - 80% - Generating strategic summary
  - 90% - Adding to unified database
  - 100% - Processing complete
- **Cache Refresh**: Automatic `st.cache_data.clear()` to make new data immediately available
- **Navigation Options**:
  - "Go to Dashboard Home" - Navigate to see new data
  - "Run Another Audit" - Reset state for additional audits

**Error Handling**:

- Import validation with detailed error messages
- Processing step failure recovery
- Comprehensive logging with expandable error details
- Graceful degradation for partial failures

**State Management**:

- Session state tracking for audit completion
- Processing status persistence
- Multi-audit workflow support
- Proper cleanup and reset functionality

### 3.5 Accessibility

- All interactive elements labelled with `aria-label`.
- Keyboard navigation supported via tabindex sequence.

## 4. Error Handling

- Missing run folder → warning toast.
- Corrupted parquet → fallback to JSON export, log error.
- Large file (>50 MB) → show spinner + progress.

## 5. Non-Functional Requirements

- Dashboard first paint <2 s on 50k ScoreFact rows (local laptop).
- Memory footprint <1 GB.
- Tested on Chrome, Safari, Edge latest versions.

**Note:** UI layer only – complements the core functional spec at [../functional_specification.md](../functional_specification.md).
