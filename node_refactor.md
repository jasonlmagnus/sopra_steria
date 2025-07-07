> [!IMPORTANT]
> **This is the Strategic Plan.** It defines the project's phases and major milestones.
> - For a detailed, chronological progress report, see `NODE_REFACTOR_LOG.md`.
> - **Rule:** When a milestone from this plan is completed, this file **MUST** be updated along with the log in the same pull request.
> - **AI Agents:** If this file conflicts with the log, the log is likely more current. Update this plan to match the log's status.

# Node.js + React Refactor Plan

_Last updated: 2025-07-29_

## 🎯 Objective
Migrate the current Streamlit-based Python dashboard to a modern web stack: **Node.js (Express + TypeScript) API** and **React (Vite + TypeScript) front-end** while preserving all data-science and AI workloads that are already written in Python.

## Phased Roadmap

| Phase | Goal | Key Tasks | Owner | Target Date |
|-------|------|----------|-------|-------------|
| 0 | Foundations | • Agree tech stack (Node 22 LTS, Express 5, React 19, Vite, pnpm)<br/>• Create `package.json`, monorepo layout (`/api`, `/web`)<br/>• ESLint + Prettier + Husky | FE Lead | 2025-07-10 |
| 1 | API Skeleton | • Set up Express server (`/api`)<br/>• REST endpoints stubbed for `/datasets`, `/pages`, `/recommendations`<br/>• Integrate Swagger / OpenAPI docs | BE Lead | 2025-07-15 |
| 2 | Data Bridge | • Expose existing Python functions via **FastAPI** or **Python-Shell** wrappers<br/>• Use gRPC or REST to call from Node | Data Eng | 2025-07-22 |
| 3 | React UI MVP | • Scaffold Vite React app (`/web`)<br/>• Implement routing + basic layout<br/>• Fetch data from Node API | FE Team | 2025-07-29 |
| 4 | Component Migration | • Recreate Streamlit visuals using `@tanstack/react-table`, `Recharts / Plotly.js`<br/>• Build reusable design-system components | FE Team | 2025-08-12 |
| 5 | Auth & Config | • Add JWT auth (Keycloak / Auth0)<br/>• Env-driven config for AI keys | DevOps | 2025-08-19 |
| 6 | Production Hardening | • Docker-compose / Kubernetes manifests<br/>• GitHub Actions CI/CD<br/>• Load testing | DevOps | 2025-08-26 |
| 7 | Cut-over & Deprecation | • Beta release → feedback<br/>• Freeze Streamlit UI<br/>• Update docs, remove old dashboard | PM | 2025-09-02 |

## Repo Layout After Migration
```
/
├── api/              # Node.js (Express) backend
│   └── src/
├── web/              # React front-end
│   └── src/
├── python/           # Existing Python package (audit_tool etc.)
├── node_refactor.md  # ← you are here
└── AGENTS.MD         # Updated instructions for AI agents
```

## Immediate Next Steps

**✅ Completed**
- [x] Merge current `dev` work to `codex`.
- [x] Create the `/api` and `/web` folders with `pnpm` monorepo structure.
- [x] Set up CI job that runs both `pytest` and `pnpm test`.
- [x] Install `axios` in the API package to prepare for calling Python services.
- [x] **Expose Python audit functions via FastAPI service.** (Initial version complete).
- [x] **Add Express proxy routes for FastAPI data.**
- [x] **Integrate React Query for dataset fetching.**
- [x] **Complete migration of the dataset list page to React.**
- [x] **Write integration tests for the new data flow.**
- [x] **Verified integration tests passing.** (2025-07-07)
- [x] **Create dataset detail page using React Table.**
- [x] **Start migration of additional pages (added Recommendations page).**
- [x] **Added Methodology page, fetching YAML via new API route.**
- [x] **Migrated core data pages:** Executive Dashboard, Opportunity Impact, Pages List.
- [x] **Created placeholder UI for all remaining Streamlit pages.**
- [x] **COMPLETED ALL PAGE MIGRATIONS:** All Streamlit pages migrated to React with API connections.

**⏳ Next Up: Comprehensive Audit & Functionality Comparison**

The React migration is functionally complete. The next critical phase is to ensure complete feature parity between the original Streamlit dashboard and the new React implementation.

**Page Migration Status:**
*   `[x]` **Executive Dashboard** (`ExecutiveDashboard.tsx`) - **Implemented**
*   `[x]` **Opportunity Impact** (`OpportunityImpact.tsx`) - **Implemented**
*   `[x]` **Methodology** (`Methodology.tsx`) - **Implemented**
*   `[x]` **Recommendations** (`Recommendations.tsx`) - **Implemented**
*   `[x]` **Pages List** (`PagesList.tsx`) - **Implemented**
*   `[x]` **Dataset List & Detail** (`DatasetList.tsx`, `DatasetDetail.tsx`) - **Implemented**
*   `[x]` **Content Matrix** (`ContentMatrix.tsx`) - **Implemented**
*   `[x]` **Success Library** (`SuccessLibrary.tsx`) - **Implemented**
*   `[x]` **Audit Reports** (`AuditReports.tsx`) - **Implemented**
*   `[x]` **Reports Export** (`ReportsExport.tsx`) - **Implemented**
*   `[x]` **Run Audit** (`RunAudit.tsx`) - **Implemented**
*   `[x]` **Social Media Analysis** (`SocialMediaAnalysis.tsx`) - **Implemented**
*   `[x]` **Persona Viewer** (`PersonaViewer.tsx`) - **Implemented**
*   `[x]` **Visual Brand Hygiene** (`VisualBrandHygiene.tsx`) - **Implemented**
*   `[x]` **Persona Insights** (`PersonaInsights.tsx`) - **Implemented**
*   `[x]` **Implementation Tracking** (`ImplementationTracking.tsx`) - **Implemented**

## 🔍 **NEXT PHASE: COMPREHENSIVE AUDIT & FUNCTIONALITY COMPARISON**

**Objective:** Ensure 100% feature parity between original Streamlit pages and new React implementation.

**Instructions for AI Agents:**

### **Phase 1: Streamlit Page Analysis**
1. **Launch the original Streamlit dashboard:**
   ```bash
   ./launch_brand_health_command_center.sh
   ```

2. **Document each page systematically:**
   - **Page Structure:** Layout, sections, tabs, sidebars
   - **Data Sources:** What data is displayed, from which files/APIs
   - **Interactive Elements:** Filters, dropdowns, date pickers, search boxes
   - **Visualizations:** Chart types, data series, styling
   - **Export/Download Features:** Available file formats, data exports
   - **User Workflows:** Multi-step processes, form submissions

### **Phase 2: React Page Comparison**
For each React page, compare against the Streamlit equivalent:

1. **Data Completeness:**
   - Verify all data fields are present
   - Check data formatting and calculations
   - Ensure aggregations and metrics match

2. **Interactive Features:**
   - Test all filters and verify they work correctly
   - Check dropdown options match original
   - Verify search functionality
   - Test sorting and pagination

3. **Visual Consistency:**
   - Compare chart types and styling
   - Verify color schemes match brand guidelines
   - Check responsive layout behavior

4. **Missing Functionality Identification:**
   - Document any missing filters or controls
   - Note absent tabs or sections
   - Identify missing export/download options

### **Phase 3: Gap Analysis & Fixes**
1. **Create detailed gap analysis report** documenting:
   - Missing interactive elements
   - Data discrepancies
   - Styling inconsistencies
   - Broken or incomplete features

2. **Prioritize fixes** by impact:
   - **Critical:** Core functionality missing
   - **High:** Important filters or data missing
   - **Medium:** Styling or UX improvements
   - **Low:** Nice-to-have features

3. **Implement fixes systematically:**
   - Add missing API endpoints as needed
   - Implement missing React components
   - Fix data processing issues
   - Update styling to match original

### **Phase 4: Testing & Validation**
1. **Functional Testing:**
   - Test all user workflows end-to-end
   - Verify data accuracy across all pages
   - Check error handling and edge cases

2. **Cross-browser Testing:**
   - Test in Chrome, Firefox, Safari
   - Verify mobile responsiveness

3. **Performance Testing:**
   - Check page load times
   - Verify chart rendering performance
   - Test with large datasets

**Deliverables:**
- Comprehensive gap analysis report
- Updated React components with full functionality
- Test results documentation
- Performance optimization recommendations

**Component & Testing Strategy:**
*   **Component Library:** Recreate Streamlit visuals using `@tanstack/react-table` for data grids and `Recharts` for charting. Develop a library of reusable components for common UI elements (e.g., scorecards, filter bars).
*   **Testing Approach:**
    *   **Unit Tests:** Use `Vitest` and `React Testing Library` for every component.
    *   **Integration Tests:** Expand existing tests to cover the full data flow for each new page, mocking API calls where necessary.
    -   **E2E Tests:** Implement `Playwright` tests for key user journeys on each page.
    -   **API Tests:** Use `supertest` to test the Node.js API endpoints independently.

