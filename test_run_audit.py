#!/usr/bin/env python3
"""
Test script for the run_audit function from 5_🚀_Run_Audit.py
"""

import os
import tempfile
import sys
from pathlib import Path

# Add audit_tool to path for imports
sys.path.append(str(Path(__file__).parent))

def get_persona_name(persona_content: str, filename: str = None) -> str:
    """Extract a human-readable persona name; fall back to P-number."""
    lines = persona_content.strip().split('\n')
    if lines:
        first = lines[0].strip()
        if first.startswith("Persona Brief:"):
            return first.replace("Persona Brief:", "").strip()
        if first and not first.startswith('#'):
            return first
    # fallback to P1, P2 etc.
    import re
    match = re.search(r"P\d+", persona_content)
    if not match and filename:
        match = re.search(r"P\d+", filename)
    return match.group(0) if match else "default_persona"

def run_audit(persona_file_path, urls_file_path, persona_name):
    """Runs the audit tool as a subprocess (inherits current working dir)."""
    import subprocess
    
    # Create output directory for this persona
    output_dir = os.path.join("audit_outputs", persona_name)
    os.makedirs(output_dir, exist_ok=True)
    
    command = [
        "python",
        "-m",
        "audit_tool.main",
        "--urls",
        urls_file_path,
        "--persona",
        persona_file_path,
        "--output",
        output_dir
    ]
    
    print(f"🚀 Running command: {' '.join(command)}")
    print(f"📁 Output directory: {output_dir}")
    
    process = subprocess.Popen(
        command,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        encoding='utf-8'
    )
    return process

def test_run_audit():
    """Test the run_audit function with sample data"""
    print("🧪 Testing run_audit function...")
    
    # Create temporary files
    temp_dir = tempfile.mkdtemp(prefix="test_audit_")
    
    try:
        # Create test persona file
        persona_content = """Persona Brief: Test Strategic Business Leader
**Role:** Test Executive
**Industry:** Test Industry
**Business Context:** Test context for audit functionality
**Key Priorities:** Test priorities
**Main Pain Points:** Test pain points
**Communication Style:** Professional, strategic
"""
        persona_file_path = os.path.join(temp_dir, "test_persona.md")
        with open(persona_file_path, "w", encoding="utf-8") as f:
            f.write(persona_content)
        
        # Create test URLs file
        urls_content = "https://www.soprasteria.com\n"
        urls_file_path = os.path.join(temp_dir, "test_urls.txt")
        with open(urls_file_path, "w", encoding="utf-8") as f:
            f.write(urls_content)
        
        # Get persona name
        persona_name = get_persona_name(persona_content, "test_persona.md")
        print(f"🎭 Detected persona: {persona_name}")
        
        # Test the run_audit function
        print("🔍 Starting audit process...")
        process = run_audit(persona_file_path, urls_file_path, persona_name)
        
        # Read first few lines of output to verify it starts correctly
        line_count = 0
        for line in iter(process.stdout.readline, ''):
            print(f"📝 {line.rstrip()}")
            line_count += 1
            
            # Stop after 10 lines or if we see an error
            if line_count >= 10 or "Error" in line or "Failed" in line:
                break
        
        # Terminate the process
        process.terminate()
        process.wait()
        
        print(f"✅ Test completed. Process return code: {process.returncode}")
        
        # Check if output directory was created
        output_dir = os.path.join("audit_outputs", persona_name)
        if os.path.exists(output_dir):
            print(f"✅ Output directory created: {output_dir}")
        else:
            print(f"❌ Output directory not found: {output_dir}")
        
    except Exception as e:
        print(f"❌ Test failed with error: {e}")
    finally:
        # Clean up temp directory
        import shutil
        if os.path.exists(temp_dir):
            shutil.rmtree(temp_dir)
        print("🧹 Cleaned up temporary files")

if __name__ == "__main__":
    test_run_audit() 