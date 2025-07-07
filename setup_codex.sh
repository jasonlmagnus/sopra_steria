#!/usr/bin/env bash
set -e
echo "⚡ Quick Codex setup for Hybrid Python/Node Project"

# 1. Python venv for static analysis
echo "🐍 Setting up lightweight Python environment..."
python3 -m venv venv
source venv/bin/activate
python3 -m pip install --upgrade pip
python3 -m pip install -r local_requirements.txt

# 2. Node.js dependencies for frontend analysis (no build)
# Use the public npm registry for all installs
PNPM_REGISTRY="https://registry.npmjs.org"
pnpm config set registry "$PNPM_REGISTRY"

echo "🟢 Installing Node.js dependencies for web..."
if [ -f "web/package.json" ]; then
    (cd web && pnpm install --registry "$PNPM_REGISTRY")
else
    echo "web/package.json not found, skipping web dependencies."
fi

echo "🟢 Installing Node.js dependencies for api..."
if [ -f "api/package.json" ]; then
    (cd api && pnpm install --registry "$PNPM_REGISTRY")
else
    echo "api/package.json not found, skipping api dependencies."
fi


# 3. Hint to AI tools about project structure
export PROJECT_TYPE=HYBRID
export PYTHON_ROOT=./
export NODE_API_ROOT=./api
export NODE_WEB_ROOT=./web
echo "✅ Lightweight hybrid environment ready for static analysis" 