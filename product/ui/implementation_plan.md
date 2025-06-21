# Implementation Plan: Brand Audit Dashboard UI

### Phase 0 – Prep (0.5 day)

1. Create `audit_runs/` folder and back-fill packager for existing P1 run.
2. Scaffold Streamlit multipage structure (`app.py`, `pages/`).

### Phase 1 – Data Packager (1 day)

- **Task 1.1**: Parse scorecard Markdown → dict (BeautifulSoup/markdown-it).
- **Task 1.2**: Build `metric_registry.py` from `methodology.yaml`.
- **Task 1.3**: Emit Parquet tables + JSON manifest.
- **Deliverable**: `audit_runs/<run_id>/…` folder for P1.

### Phase 2 – Data Gateway & Global State (0.5 day)

- Cache loaders (`st.cache_resource`).
- Create sidebar run selector; store manifest in `st.session_state`.

### Phase 3 – Core Pages MVP (1.5 day)

| Page               | Widgets                               | Effort |
| ------------------ | ------------------------------------- | ------ |
| Executive Overview | KPI tiles, tier bar, descriptor donut | 0.5 d  |
| Persona Comparison | radar, heatmap                        | 0.5 d  |
| Criteria Explorer  | histogram + evidence modal            | 0.5 d  |

### Phase 4 – Insight Pages (1 day)

- Port Priority Actions & Quick Wins cards (reuse CSS).
- Journey Consistency ribbon (Plotly Sankey).
- Gating Breaches table with severity filters.

### Phase 5 – Evidence Gallery & Raw Data (0.5 day)

- Paginated quote browser, copy-to-clipboard.
- Data export buttons.

### Phase 6 – Polish & Deploy (0.5 day)

- Mobile responsiveness QA.
- Accessibility audit (axe DevTools).
- Dockerfile + README.

**Total**: ~4 developer-days.
