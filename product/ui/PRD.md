_Status: Active • Last-verified: 2025-06-22 • Owner: @design_lead_

**Note:** This document is a UI-specific supplement. For the master product requirements covering the full pipeline, see [../brand_audit_tool_prd.md](../brand_audit_tool_prd.md).

## Product Requirements Document: Brand Audit Dashboard UI

### 1. Purpose

Provide a professional, persona-aware Streamlit interface that (a) lets analysts RUN an audit pipeline, and (b) lets executives EXPLORE insight-rich dashboards powered by the YAML-driven scoring framework.

### 2. Goals & Objectives

1. Enable non-technical users to upload persona files + URL lists and trigger audits.
2. Surface quantitative scores and qualitative insights with enterprise-grade visualisations.
3. Compare results across personas and across historical runs.
4. Preserve accessibility, performance, and Apple-level design polish.

### 3. Key Features

| ID   | Feature              | Description                                           |
| ---- | -------------------- | ----------------------------------------------------- |
| F-1  | Run management       | Upload persona & URLs, launch audit, live log stream  |
| F-2  | Executive overview   | KPI tiles, descriptor share, tier contribution charts |
| F-3  | Persona comparison   | Radar & heatmaps to compare criteria across personas  |
| F-4  | Criteria explorer    | Drill-down histogram + evidence per criterion         |
| F-5  | Priority actions     | Critical gaps & quick wins cards with evidence        |
| F-6  | Journey consistency  | Journey ribbon and variance alerts per persona        |
| F-7  | Gating-rule breaches | Compliance table & severity filters                   |
| F-8  | Evidence gallery     | Best / worst quotes browser                           |
| F-9  | Run history          | Trend charts across multiple audit runs               |
| F-10 | Raw data export      | Download Parquet/CSV/JSON for BI tools                |

### 4. Success Metrics

- < 30 s dashboard load for 5 000 ScoreFacts.
- 100 % WCAG 2.1 AA contrast compliance.
- < 3 clicks to reach any insight from landing page.

### 5. Out-of-Scope

- Real-time multi-user collaboration.
- In-browser editing of methodology YAML.
