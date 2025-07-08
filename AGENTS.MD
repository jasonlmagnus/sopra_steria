# 🤖 AI Agent Guidelines

## 📋 **PROJECT OVERVIEW**
**THIS IS A NODE.JS PROJECT NOW - NOT PYTHON!!!**

**Current Stack:**
- **Frontend:** React 19 + Vite + TypeScript (`/web` directory)
- **Backend:** Node.js Express + TypeScript (`/api` directory)  
- **Data Services:** Python 3.12 + FastAPI (`/audit_tool` directory - DATA PROCESSING ONLY)
- **Package Management:** `pnpm` for Node.js, `pip` for Python

**Architecture:**
- React frontend calls Node.js API
- Node.js API proxies to Python FastAPI services
- Python only handles data processing, AI analysis, web scraping
- Streamlit dashboard is **DEPRECATED** (reference only)

## 🎯 **CURRENT PRIORITIES**

See `CODEX_IMMEDIATE_TASKS.md` for specific tasks and progress tracking.

**Current Focus:** Evidence integration and real data connections
- Remove all mock data usage
- Connect React pages to real data sources
- Implement proper evidence display components
- Ensure HTML reports display actual files

## 🛠️ **DEVELOPMENT RULES**

**Technology Requirements:**
- Use TypeScript for all new components
- Use `@tanstack/react-query` for data fetching
- Use `@tanstack/react-table` for data tables
- Use `Recharts` for basic charts, `Plotly.js` for interactive charts
- Build components in `/web/src/components/`
- Use `registry.npmjs.org` for Node packages

**Code Quality:**
- Write unit tests for all components (`Vitest` + `React Testing Library`)
- Follow existing patterns and naming conventions
- Integrate with existing FilterContext and BrandStyling

## 🚀 **QUICK START**

```bash
# Primary development stack
pnpm install
pnpm --filter api dev     # Start Node.js API
pnpm --filter web dev     # Start React frontend

# Python backend (data services only)
python -m venv venv && source venv/bin/activate
pip install -r requirements.txt
python -m fastapi dev audit_tool/main.py
```

## 📊 **SUCCESS METRICS**

- Component utilization: 75% → 90%+
- Feature parity: 70% → 95%+
- Page load times: < 2 seconds
- Real data usage: 100% (no mock data)

## 🚫 **WHAT NOT TO DO**

- **DO NOT** treat this as a Python project
- **DO NOT** suggest Streamlit solutions
- **DO NOT** use mock data when real data is available
- **DO NOT** generate fake content for HTML reports

## 🔧 **CURRENT SERVER SETUP**

When all servers are running:
- **React Frontend:** http://localhost:5173
- **Express API:** http://localhost:3000  
- **FastAPI Service:** http://localhost:8000

Use `./start_all_servers.sh` to start all services.
