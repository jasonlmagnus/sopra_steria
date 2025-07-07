# 🚀 IMMEDIATE TASKS FOR CODEX

## Current Status
- ✅ React migration is COMPLETE - all pages functional
- ❌ Component utilization is only ~60% (target: 90%+)
- ❌ Feature parity is only ~60% (target: 95%+)

## Phase 1: Quick Wins (START HERE)

### 1. Apply ScoreCard Variants
- [ ] `ExecutiveDashboard.tsx` - Add success/warning/danger variants for metrics
- [ ] `ImplementationTracking.tsx` - Add progress indicators
- [ ] `OpportunityImpact.tsx` - Add impact scoring variants

### 2. Integrate PlotlyChart
- [ ] `ExecutiveDashboard.tsx` - Replace basic charts with interactive Plotly
- [ ] `PersonaInsights.tsx` - Add persona comparison charts  
- [ ] `ContentMatrix.tsx` - Add interactive heatmaps

### 3. Apply Enhanced DataTable
- [ ] `PersonaViewer.tsx` - Add journey step filtering
- [ ] `AuditReports.tsx` - Add report filtering and sorting

## Phase 2: Core Components (NEXT)

### 1. Build ExpandableCard Component
- Pattern: Click to expand/collapse with smooth animation
- Apply to: `ExecutiveDashboard.tsx` (7 expandable sections)

### 2. Build FilterSystem Component  
- Multi-dimensional filtering with session state
- Integrate with existing FilterContext
- Apply to: `ContentMatrix.tsx` and `OpportunityImpact.tsx`

### 3. Build TabNavigation Component
- Multi-tab navigation system
- Apply to: `Methodology.tsx` (6 tabs) and `ReportsExport.tsx` (4 tabs)

## Key Rules
- Use TypeScript for all components
- Build in `/web/src/components/`
- Use existing brand styling
- Write unit tests for each component
- Use `registry.npmjs.org` for packages

## Success Metrics
- Component utilization: 60% → 90%+
- Feature parity: 60% → 95%+
- Page load times: < 2 seconds 