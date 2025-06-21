# Functional Specification: Brand Audit Dashboard UI

## 1. Overview

The dashboard is a multi-page Streamlit application. Pages are:

1. **Run Audit** – upload persona & URLs, trigger pipeline, live log.
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

### 3.4 Accessibility

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
