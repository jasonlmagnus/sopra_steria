# Agents Instructions for Sopra Steria Brand Audit Tool

## 🤖 AI Agent Guidelines for Codebase Interaction

This document provides explicit instructions for AI agents (like GitHub Codex) on how to properly understand and work with this codebase.

---

## 📋 **PROJECT IDENTIFICATION**

### **This is a PYTHON PROJECT, not Node.js**

**Primary Language:** Python 3.12+  
**Framework:** Streamlit (web dashboard)  
**Architecture:** Modular Python package with CLI and web interface  
**Dependencies:** Managed via `requirements.txt` and Python virtual environment

**⚠️ IMPORTANT:** If you see `package.json` files or JavaScript references, these are from Python dependencies (Playwright, Plotly) that include browser components. **DO NOT** treat this as a Node.js project.

---

## 🏗️ **CODEBASE STRUCTURE**

```
sopra_steria/
├── audit_tool/                    # Main Python package
│   ├── __init__.py                # Package initialization
│   ├── main.py                    # CLI entry point & orchestration
│   ├── ai_interface.py            # AI provider abstraction (OpenAI/Anthropic)
│   ├── scraper.py                 # Web scraping functionality
│   ├── methodology_parser.py      # YAML configuration parser
│   ├── persona_parser.py          # Markdown persona processor
│   ├── multi_persona_packager.py  # Data aggregation
│   ├── strategic_summary_generator.py # AI-powered summaries
│   ├── config/
│   │   ├── methodology.yaml       # Audit scoring methodology
│   │   └── unified_csv_columns.yaml # Data schema
│   ├── dashboard/                 # Streamlit web interface
│   │   ├── brand_health_command_center.py # Main dashboard
│   │   ├── components/            # Reusable dashboard components
│   │   └── pages/                 # Individual dashboard pages
│   ├── templates/                 # AI prompt templates
│   └── tests/                     # Test suite
├── audit_inputs/                  # Input data and configuration
│   ├── personas/                  # Persona definitions (markdown)
│   ├── prompts/                   # AI prompt templates
│   └── social_media/              # Social media audit data
├── audit_outputs/                 # Generated audit reports
├── audit_data/                    # Processed/unified datasets
├── cache/                         # Web scraping cache
├── product/                       # Documentation and specifications
├── requirements.txt               # Python dependencies
├── launch_brand_health_command_center.sh # Dashboard launcher
└── README.md                      # Project documentation
```

---

## 🎯 **KEY CONCEPTS**

### **Brand Audit Methodology**

- **Scoring System:** 0-10 scale with descriptive categories
- **Tier Classification:** Pages classified as Tier 1 (Brand), Tier 2 (Value Prop), Tier 3 (Functional)
- **Multi-Persona Analysis:** 5 different business personas evaluate same content
- **Criteria-Based Evaluation:** Weighted scoring across brand and performance criteria

### **Data Flow**

1. **Input:** URLs + Persona definitions
2. **Scraping:** Web content extraction (cached)
3. **AI Analysis:** Content evaluation via OpenAI/Anthropic
4. **Scoring:** Methodology-based numerical scoring
5. **Aggregation:** Multi-persona data unification
6. **Visualization:** Streamlit dashboard presentation

---

## 🔧 **DEVELOPMENT GUIDELINES**

### **Environment Setup**

```bash
# Always use Python virtual environment
python -m venv venv
source venv/bin/activate  # macOS/Linux
# venv\Scripts\activate   # Windows

# Install dependencies
pip install -r requirements.txt

# Launch dashboard
./launch_brand_health_command_center.sh
```

### **AI Provider Configuration**

- **Default Provider:** OpenAI (cost-effective)
- **Alternative:** Anthropic (premium quality)
- **Configuration:** Environment variables `OPENAI_API_KEY`, `ANTHROPIC_API_KEY`
- **Switching:** Modify `model_provider` parameter in `AIInterface()`

### **Code Patterns**

#### **Adding New Dashboard Pages**

```python
# File: audit_tool/dashboard/pages/N_🎯_Page_Name.py
import streamlit as st
from audit_tool.dashboard.components.data_loader import BrandHealthDataLoader

def main():
    st.title("🎯 Page Name")

    # Load data
    loader = BrandHealthDataLoader()
    datasets, master_df = loader.load_all_data()

    # Your page logic here

if __name__ == "__main__":
    main()
```

#### **AI Interface Usage**

```python
from audit_tool.ai_interface import AIInterface
from audit_tool.methodology_parser import MethodologyParser

# Initialize with OpenAI (default)
ai = AIInterface(model_provider="openai")

# Generate reports
methodology = MethodologyParser()
scorecard = ai.generate_hygiene_scorecard(
    url=url,
    page_content=content,
    persona_content=persona,
    methodology=methodology
)
```

#### **Data Loading Pattern**

```python
from audit_tool.dashboard.components.data_loader import BrandHealthDataLoader

loader = BrandHealthDataLoader()
datasets, master_df = loader.load_all_data()

# datasets contains: 'master', 'criteria_scores', 'experience', etc.
# master_df is the unified DataFrame with all audit data
```

---

## 📊 **DATA SCHEMA**

### **Unified Dataset Columns**

```python
# Key columns in master_df:
- page_id: str           # Unique page identifier
- url: str               # Full URL
- persona: str           # Persona name
- tier: str              # Page classification (tier_1, tier_2, tier_3)
- criterion_code: str    # Evaluation criterion identifier
- raw_score: float       # 0-10 numerical score
- final_score: float     # Weighted/adjusted score
- evidence: str          # Supporting quote/evidence
- descriptor: str        # Score interpretation
- weight_pct: float      # Criterion weight percentage
```

### **File Formats**

- **Input:** Markdown (personas), YAML (methodology), TXT (URLs)
- **Processing:** CSV (unified datasets), PKL (cache)
- **Output:** Markdown (reports), CSV (data exports)

---

## 🚨 **COMMON PITFALLS & SOLUTIONS**

### **1. Node.js Confusion**

**Problem:** AI agents think this is a Node.js project  
**Solution:** This is Python. `package.json` files are from Playwright/Plotly dependencies.

### **2. AI Provider Defaults**

**Problem:** Hardcoded Anthropic defaults cause API errors  
**Solution:** Always default to OpenAI unless explicitly specified

### **3. Data Loading Issues**

**Problem:** Dashboard pages expect different data structures  
**Solution:** Use `BrandHealthDataLoader.load_all_data()` for consistency

### **4. Import Errors**

**Problem:** Module not found errors  
**Solution:** Ensure virtual environment is activated and dependencies installed

### **5. Streamlit Caching**

**Problem:** Data not updating in dashboard  
**Solution:** Use `@st.cache_data` decorators and clear cache when needed

---

## 🧪 **TESTING GUIDELINES**

### **Running Tests**

```bash
# Full test suite
python audit_tool/tests/test_audit_tool.py

# Test individual components
python -c "from audit_tool.ai_interface import AIInterface; print('AI Interface OK')"
python -c "from audit_tool.main import run_audit; print('Main module OK')"
```

### **Expected Test Results**

- **YAML Configuration:** ✅ Should pass
- **Web Scraper:** ✅ Should pass
- **AI Interface:** ✅ Should pass
- **Persona Parsing:** ⚠️ May have minor issues (acceptable)
- **Full Pipeline:** ⚠️ Requires API keys

---

## 🔄 **GIT WORKFLOW**

### **Git Remote Setup (CRITICAL for AI Agents)**

**If you're in a container/environment without git remote configured:**

```bash
# Add the GitHub remote
git remote add origin https://github.com/jasonlmagnus/sopra_steria.git

# Verify remote is configured
git remote -v
# Should output:
# origin  https://github.com/jasonlmagnus/sopra_steria.git (fetch)
# origin  https://github.com/jasonlmagnus/sopra_steria.git (push)
```

**🚨 IMPORTANT FOR AI AGENTS:**

- No more "no git remote" excuses for not creating PRs
- This is a PYTHON project - create PRs for ALL meaningful changes
- Use GitHub API or git commands - both should work now

### **Branch Strategy**

- **main:** Stable production code
- **dev:** Development integration branch
- **codex:** Active development branch (current)
- **Feature branches:** For specific features/fixes

### **Commit Guidelines**

```bash
# Feature commits
git commit -m "feat: Add new dashboard page for persona analysis"

# Bug fixes
git commit -m "fix: Resolve AI provider default to OpenAI"

# Documentation
git commit -m "docs: Update API interface documentation"

# Refactoring
git commit -m "refactor: Simplify data loading logic"
```

### **PR Creation (Multiple Methods)**

```bash
# Method 1: Traditional git workflow
git checkout -b feature/your-feature-name
git push origin feature/your-feature-name
# Create PR via GitHub interface: feature/your-feature-name → codex

# Method 2: GitHub CLI (if available)
gh pr create --title "Your PR Title" --body "Description"

# Method 3: GitHub API (for containers)
# Use GitHub's REST API to create PRs programmatically
```

**🤖 AI AGENTS: You MUST create PRs for Python changes. No excuses.**

---

## 🎨 **UI/UX PATTERNS**

### **Streamlit Dashboard Conventions**

- **Page Icons:** Use emoji prefixes (🎯, 📊, 🚀, etc.)
- **Color Scheme:** Sopra Steria brand colors (navy #3d4a6b, red #dc3545)
- **Layout:** Sidebar navigation, main content area, expandable sections
- **Data Visualization:** Plotly charts with consistent styling

### **Component Structure**

```python
# Standard page layout
st.set_page_config(page_title="Page Name", page_icon="🎯", layout="wide")
st.title("🎯 Page Name")

with st.sidebar:
    # Filters and controls

col1, col2 = st.columns(2)
with col1:
    # Left content
with col2:
    # Right content
```

---

## 📚 **DOCUMENTATION STANDARDS**

### **Code Documentation**

```python
def function_name(param1: str, param2: int) -> Dict[str, Any]:
    """
    Brief description of function purpose.

    Args:
        param1: Description of parameter
        param2: Description of parameter

    Returns:
        Description of return value

    Raises:
        ValueError: When invalid input provided
    """
```

### **README Updates**

- Keep installation instructions current
- Update feature lists when adding functionality
- Include screenshots for UI changes
- Maintain accurate dependency lists

---

## 🚀 **DEPLOYMENT NOTES**

### **Local Development**

```bash
# Quick start
./launch_brand_health_command_center.sh

# Manual start
streamlit run audit_tool/dashboard/brand_health_command_center.py
```

### **Production Considerations**

- Set environment variables for API keys
- Configure appropriate port/host settings
- Ensure data directories exist and are writable
- Monitor resource usage (AI API calls can be expensive)

---

## 📞 **SUPPORT & TROUBLESHOOTING**

### **Common Issues**

1. **Import errors:** Check virtual environment activation
2. **API failures:** Verify API keys and provider settings
3. **Data not loading:** Check file paths and permissions
4. **Dashboard crashes:** Review Streamlit logs for errors

### **Debug Mode**

```python
# Enable detailed logging
import logging
logging.basicConfig(level=logging.DEBUG)

# Streamlit debug mode
streamlit run app.py --logger.level debug
```

---

## 🎯 **AGENT-SPECIFIC INSTRUCTIONS**

### **For Code Generation**

1. **Always** check if functionality already exists before creating new code
2. **Follow** existing patterns and conventions in the codebase
3. **Use** the established data loading and AI interface patterns
4. **Test** generated code against the existing test suite

### **For Bug Fixes**

1. **Identify** the root cause using the debugging guidelines above
2. **Check** if the issue is environment-related (API keys, dependencies)
3. **Follow** the established git workflow for fixes
4. **Update** tests if fixing test-related issues

### **For Feature Additions**

1. **Review** the product documentation in `/product/` directory
2. **Follow** the established architecture patterns
3. **Add** appropriate tests for new functionality
4. **Update** documentation as needed

---

**Remember:** This is a sophisticated brand audit tool with AI integration. Treat it as a professional Python application with proper software engineering practices.
