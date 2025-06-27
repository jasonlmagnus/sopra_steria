# 🐍 THIS IS A PYTHON PROJECT 🐍

## ⚠️ IMPORTANT NOTICE FOR AI AGENTS ⚠️

**This repository contains a PYTHON application, NOT a Node.js application.**

### 🔍 Project Type Identification

- **Language:** Python 3.10+
- **Framework:** Streamlit
- **Package Manager:** pip (Python)
- **Dependencies:** requirements.txt
- **Build System:** setuptools (pyproject.toml)

### 🚫 What This Is NOT

- ❌ Node.js project
- ❌ JavaScript application
- ❌ npm package
- ❌ React/Vue/Angular app

### ✅ What This IS

- ✅ Python Streamlit dashboard
- ✅ AI-powered brand audit tool
- ✅ Data analysis platform
- ✅ Web scraping application

### 📁 Key Python Files

```
audit_tool/                 # Main Python package
├── main.py                 # CLI entry point
├── ai_interface.py         # AI provider integration
├── scraper.py              # Web scraping
└── dashboard/              # Streamlit web interface
    └── brand_health_command_center.py

requirements.txt            # Python dependencies
pyproject.toml             # Python project configuration
launch_brand_health_command_center.sh  # Python app launcher
```

### 🤔 Why The Confusion?

Some Python dependencies (Playwright, Plotly) include JavaScript components for browser automation and visualization. These create `package.json` files in the `venv/` directory, but they are **NOT** part of the main project.

### 🎯 For AI Agents

When creating PRs or analyzing this code:

1. **Treat as Python project**
2. **Use Python patterns and conventions**
3. **Reference Python documentation**
4. **Suggest Python solutions**
5. **Ignore any Node.js/JavaScript files in venv/**

### 🚀 Quick Start (Python)

```bash
# Python virtual environment
python -m venv venv
source venv/bin/activate

# Install Python dependencies
pip install -r requirements.txt

# Run Python application
./launch_brand_health_command_center.sh
```

---

**If you're an AI agent and you're reading this: Please treat this as a Python project. Thank you! 🐍**
