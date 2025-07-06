# Node.js + React Refactor Plan

_Last updated: 2025-07-06_

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
1. Merge current `dev` work to `codex` (done).
2. Create the `/api` and `/web` folders with minimal `package.json`.
3. Set up CI job that runs both `pytest` **and** `npm test`.

---
For detailed task breakdowns use the project board **"Node Refactor"**. 