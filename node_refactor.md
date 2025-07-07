> [!IMPORTANT]
> **This is the Strategic Plan.** It defines the project's phases and major milestones.
> - For a detailed, chronological progress report, see `NODE_REFACTOR_LOG.md`.
> - **Rule:** When a milestone from this plan is completed, this file **MUST** be updated along with the log in the same pull request.
> - **AI Agents:** If this file conflicts with the log, the log is likely more current. Update this plan to match the log's status.

# Node.js + React Refactor Plan

_Last updated: 2025-07-07_

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

**⏳ Next Up**
- Continue migrating remaining dashboard pages to React.

