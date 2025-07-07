# React vs Streamlit Functionality Gap

This summary captures missing functionality for each React page compared to its original Streamlit implementation. Details come from the manual comparisons documented in `product/plans/streamlit_page_audit_results.md`.

## Pages with Identified Gaps

### ExecutiveDashboard.tsx
- Only basic `ScoreCard` used; variants (success/warning/danger) not applied.
- No charts implemented.
- Missing `ExpandableCard` for opportunities and success stories.
- Missing `FilterSystem` for tier filtering.

### PersonaInsights.tsx
- Still largely a placeholder.
- Lacks `PlotlyChart` comparison visuals.
- Missing `PersonaSelector` for mode switching.
- Missing enhanced `DataTable` for persona analysis.

### ContentMatrix.tsx
- Still largely a placeholder.
- Heatmap visuals not implemented with `PlotlyChart`.
- `FilterSystem` for four-column filtering not present.
- Drill‑down `DataTable` missing.

### SuccessLibrary.tsx
- Still largely a placeholder.
- Distribution charts not implemented using `PlotlyChart`.
- `EvidenceBrowser` search component absent.
- Enhanced `DataTable` for success stories missing.

### Methodology.tsx
- Placeholder implementation.
- Missing `TabNavigation` system for section switching.
- Does not use enhanced display components.

### OpportunityImpact.tsx
- Uses enhanced components but `ScoreCard` variants not applied.

### ImplementationTracking.tsx
- Uses enhanced components but `ScoreCard` variants not applied.

## Pages Pending Audit

The following pages have been migrated to React but have not yet been fully compared against their Streamlit versions. Gaps will be added once documentation is complete:

- ReportsExport.tsx
- RunAudit.tsx
- SocialMediaAnalysis.tsx
- PersonaViewer.tsx
- VisualBrandHygiene.tsx
- Recommendations.tsx
- AuditReports.tsx
- DatasetList.tsx / DatasetDetail.tsx
- PagesList.tsx

---

**Registry Note:** Node packages are installed from `https://registry.npmjs.org` as configured in `.npmrc`.
