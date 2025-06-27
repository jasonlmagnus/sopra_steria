#!/usr/bin/env python3
"""
Runtime Environment Detection for AI Agents
Sopra Steria Brand Audit Tool - Python Project

This script detects and reports the runtime environment to help AI agents
understand this is a Python project, not Node.js.
"""

import sys
import os
import subprocess
import platform
from pathlib import Path

def detect_python_environment():
    """Detect Python runtime environment details"""
    print("🐍 PYTHON RUNTIME ENVIRONMENT DETECTION")
    print("=" * 50)
    
    # Python version and location
    print(f"Python Version: {sys.version}")
    print(f"Python Executable: {sys.executable}")
    print(f"Python Path: {sys.path[0]}")
    
    # Platform information
    print(f"Platform: {platform.platform()}")
    print(f"Architecture: {platform.architecture()}")
    
    # Check for virtual environment
    venv = os.environ.get('VIRTUAL_ENV')
    if venv:
        print(f"Virtual Environment: {venv}")
    else:
        print("Virtual Environment: Not activated")
    
    print("\n📦 PYTHON PACKAGES")
    print("-" * 30)
    
    # Check key packages
    key_packages = ['streamlit', 'pandas', 'plotly', 'requests', 'pyyaml']
    for package in key_packages:
        try:
            result = subprocess.run([sys.executable, '-c', f'import {package}; print({package}.__version__)'], 
                                  capture_output=True, text=True)
            if result.returncode == 0:
                print(f"✅ {package}: {result.stdout.strip()}")
            else:
                print(f"❌ {package}: Not installed")
        except Exception as e:
            print(f"❌ {package}: Error checking - {e}")
    
    print("\n🚫 NOT NODE.JS")
    print("-" * 20)
    print("❌ This is NOT a Node.js project")
    print("❌ Do not use npm, node, or JavaScript tools")
    print("❌ Any package.json files are from Python dependencies")
    
    print("\n✅ PROJECT IDENTIFICATION")
    print("-" * 30)
    print("✅ Language: Python 3.12+")
    print("✅ Framework: Streamlit")
    print("✅ Package Manager: pip")
    print("✅ Project Type: Python web application")
    
    # Check for project files
    project_files = [
        'pyproject.toml',
        'requirements.txt', 
        'agents.md',
        'THIS_IS_PYTHON_NOT_NODEJS.txt',
        'CODEX_READ_THIS_PYTHON_PROJECT.md'
    ]
    
    print("\n📋 PROJECT FILES")
    print("-" * 20)
    for file in project_files:
        if Path(file).exists():
            print(f"✅ {file}")
        else:
            print(f"❌ {file}")
    
    # Git configuration
    print("\n🔧 GIT CONFIGURATION")
    print("-" * 25)
    try:
        result = subprocess.run(['git', 'remote', '-v'], capture_output=True, text=True)
        if result.returncode == 0 and result.stdout.strip():
            print("✅ Git remote configured:")
            print(result.stdout.strip())
        else:
            print("❌ No git remote configured")
            print("💡 Run: git remote add origin https://github.com/jasonlmagnus/sopra_steria.git")
    except Exception as e:
        print(f"❌ Git check failed: {e}")
    
    print("\n🤖 MESSAGE FOR AI AGENTS")
    print("=" * 30)
    print("🐍 This is a PYTHON project")
    print("🎯 Create PRs for ALL meaningful changes")
    print("🚫 Never use Node.js, npm, or JavaScript tools")
    print("✅ Use Python, pip, and Streamlit commands")
    print("=" * 50)

if __name__ == "__main__":
    detect_python_environment() 