#!/usr/bin/env python3
"""
Generate HTML Brand Experience Report

This script generates comprehensive HTML reports from the unified audit data CSV.
"""

import sys
import os
import pandas as pd
from pathlib import Path

# Add the parent directory to Python path to access audit_tool modules
project_root = Path(__file__).parent.parent
sys.path.append(str(project_root))

from audit_tool.html_report_generator import HTMLReportGenerator

def list_available_personas():
    """List all available personas in the unified data"""
    try:
        df = pd.read_csv('../audit_data/unified_audit_data.csv')
        personas = df['persona_id'].unique()
        return sorted(personas)
    except Exception as e:
        print(f"Error loading persona list: {e}")
        return []

def main():
    if len(sys.argv) < 2:
        print("Usage: python generate_html_report.py <persona_name|consolidated> [output_path]")
        print("\nAvailable personas:")
        personas = list_available_personas()
        for i, persona in enumerate(personas, 1):
            print(f"  {i}. {persona}")
        print(f"\nSpecial options:")
        print(f"  - consolidated: Generate a single report across all personas")
        print(f"\nExamples:")
        print(f"  python generate_html_report.py \"The Technical Influencer\"")
        print(f"  python generate_html_report.py consolidated")
        sys.exit(1)
    
    persona_name = sys.argv[1]
    output_path = sys.argv[2] if len(sys.argv) > 2 else None
    
    # Check if unified data file exists
    if not os.path.exists('../audit_data/unified_audit_data.csv'):
        print("Error: unified_audit_data.csv not found in audit_data directory")
        sys.exit(1)
    
    try:
        generator = HTMLReportGenerator()
        
        if persona_name.lower() == 'consolidated':
            # Generate consolidated report
            print("🔄 Generating consolidated report across all personas...")
            output_file = generator.generate_consolidated_report(output_path)
            
            print(f"✅ Consolidated HTML report generated successfully!")
            print(f"📄 Type: Consolidated Report (All Personas)")
            print(f"📄 Output: {output_file}")
            print(f"📊 Open in browser: file://{os.path.abspath(output_file)}")
            
        else:
            # Verify persona exists in data
            available_personas = list_available_personas()
            if persona_name not in available_personas:
                print(f"Error: Persona '{persona_name}' not found in data")
                print("\nAvailable personas:")
                for i, persona in enumerate(available_personas, 1):
                    print(f"  {i}. {persona}")
                print(f"\nOr use 'consolidated' for a cross-persona report")
                sys.exit(1)
            
            # Generate individual persona report
            print(f"🔄 Generating report for persona: {persona_name}")
            output_file = generator.generate_report(persona_name, output_path)
            
            print(f"✅ HTML report generated successfully!")
            print(f"📄 Persona: {persona_name}")
            print(f"📄 Output: {output_file}")
            print(f"📊 Open in browser: file://{os.path.abspath(output_file)}")
        
    except Exception as e:
        print(f"❌ Error generating report: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main() 