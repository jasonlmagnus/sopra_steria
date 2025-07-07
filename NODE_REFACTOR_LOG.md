> [!IMPORTANT]
> **This is the Progress Log.** It is a detailed, chronological record of completed work.
> - For the high-level strategy and major milestones, see `node_refactor.md`.
> - **Rule:** When a milestone from the plan is completed, this log **MUST** be updated along with the plan in the same pull request.
> - **AI Agents:** This file is the source of truth for recent, specific tasks. If it conflicts with the plan, update the plan to match this log.

# Node Refactor Progress Log

This file tracks the ongoing migration from the Streamlit dashboard to the Node.js + React stack. See `node_refactor.md` for the overall roadmap.

## Completed
- pnpm monorepo scaffold with `api` and `web` packages
- CI workflow running both `pytest` and `pnpm test`
- Express API with `/api/hello` endpoint and basic tests
- Vite React app scaffold
- Stub routes for `/datasets`, `/pages`, `/recommendations`
- Swagger UI documentation
- Additional API tests (including docs endpoint)
- Added axios dependency for future FastAPI integration
- Bridge Python functionality via FastAPI or shell wrappers *(FastAPI service created)*
- Implement Express proxy routes to call the FastAPI service for datasets and pages
- React Query integrated for dataset list page
- Integration tests covering the Express → FastAPI call chain
- Integration tests verified passing on 2025-07-07
- Added dataset detail page in React using @tanstack/react-table
- Created recommendations page in React using React Table
- Added Methodology page in React fetching YAML via new API route
- Migrated Implementation Tracking page to React using Recharts for progress visualization

## In Progress
- **Page Migration:** The migration of the remaining dashboard pages from Streamlit to React is underway. For a detailed checklist of pages and the testing strategy, see the "Next Up" section in `node_refactor.md`.

## Next Tasks
- Add authentication and environment-driven configuration

## Todo
- Production hardening (Docker, CI/CD, load testing)
- Deprecate Streamlit dashboard once feature complete
