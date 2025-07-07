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

## In Progress
- Bridge Python functionality via FastAPI or shell wrappers *(FastAPI service created)*
- Begin migrating dataset list page to React
- Recreate Streamlit visuals using React components

## Next Tasks
- Implement Express proxy routes to call the FastAPI service for datasets and pages *(completed)*
- Use React Query to fetch dataset data in the new React page
- Add integration tests covering the Express → FastAPI call chain

## Todo
- Add authentication and environment-driven configuration
- Production hardening (Docker, CI/CD, load testing)
- Deprecate Streamlit dashboard once feature complete
