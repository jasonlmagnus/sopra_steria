#!/bin/bash

# Sopra Steria Brand Audit Tool - Python Environment Setup
# Forces Python runtime configuration for AI agents/containers

echo "🐍 CONFIGURING PYTHON RUNTIME ENVIRONMENT 🐍"
echo "=============================================="
echo "Project: Sopra Steria Brand Audit Tool"
echo "Language: Python 3.12+"
echo "Framework: Streamlit"
echo "Package Manager: pip"
echo "NOT Node.js, NOT JavaScript"
echo ""

# Set environment variables that AI agents can read
export PROJECT_TYPE="PYTHON"
export LANGUAGE="Python"
export FRAMEWORK="Streamlit"
export PACKAGE_MANAGER="pip"
export NOT_NODEJS="true"

# Create environment file for persistence
cat > /workspace/.env << EOF
# Python Project Environment Configuration
PROJECT_TYPE=PYTHON
LANGUAGE=Python
FRAMEWORK=Streamlit
PACKAGE_MANAGER=pip
NOT_NODEJS=true
PYTHON_VERSION=3.12
EOF

# Update Python path
export PYTHONPATH="/workspace:$PYTHONPATH"

# Install Python dependencies
echo "📦 Installing Python dependencies..."
pip install --upgrade pip
pip install -r requirements.txt

# Configure git remote
echo "🔧 Configuring git remote..."
git remote add origin https://github.com/jasonlmagnus/sopra_steria.git 2>/dev/null || true
git remote -v

# Create runtime detection file
cat > /workspace/RUNTIME_DETECTED.md << EOF
# Runtime Environment Detected

## Primary Language: Python 🐍
- Version: $(python --version)
- Location: $(which python)
- Pip Version: $(pip --version)

## Framework: Streamlit
- Installed: $(pip show streamlit | grep Version || echo "Not installed")

## Git Configuration
- Remote: $(git remote get-url origin 2>/dev/null || echo "Not configured")

## Environment Variables
- PROJECT_TYPE: $PROJECT_TYPE
- LANGUAGE: $LANGUAGE
- FRAMEWORK: $FRAMEWORK

## NOT Node.js
- This is NOT a Node.js project
- Any package.json files are from Python dependencies
- Use pip, not npm
- Use python, not node

---
Generated: $(date)
EOF

# Make this script executable
chmod +x /workspace/.devcontainer/setup.sh

echo ""
echo "✅ Python runtime environment configured successfully"
echo "🎯 AI Agents: This is definitively a Python project"
echo "🚫 Do not use Node.js, npm, or JavaScript tools"
echo "✅ Use Python, pip, and Streamlit commands"
echo "" 