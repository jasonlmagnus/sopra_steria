#!/usr/bin/env python3
"""
STYLE APPLICATION AUDIT
Comprehensive analysis of HOW styling is applied across the dashboard
"""

import os
import re
from pathlib import Path
from collections import defaultdict

class StyleApplicationAuditor:
    def __init__(self):
        self.dashboard_dir = Path("audit_tool/dashboard")
        self.pages_dir = Path("audit_tool/dashboard/pages")
        self.components_dir = Path("audit_tool/dashboard/components")
        
        # Style application methods
        self.css_files = []
        self.inline_style_methods = defaultdict(list)
        self.css_injection_methods = defaultdict(list)
        self.component_imports = defaultdict(list)
        self.streamlit_styling = defaultdict(list)
        self.custom_styling_functions = defaultdict(list)
        self.style_variables = defaultdict(list)
        
    def audit_all_styling_methods(self):
        """Audit all methods of applying styling"""
        print("🔍 COMPREHENSIVE STYLE APPLICATION AUDIT")
        print("=" * 70)
        
        # Find all CSS files
        self.find_css_files()
        
        # Audit all Python files
        all_files = []
        all_files.extend(list(self.pages_dir.glob("*.py")))
        all_files.extend(list(self.components_dir.glob("*.py")))
        all_files.extend(list(self.dashboard_dir.glob("*.py")))
        
        for file_path in all_files:
            if file_path.name.startswith("__"):
                continue
            print(f"\n📄 Auditing: {file_path.relative_to(self.dashboard_dir)}")
            self.audit_file_styling(file_path)
        
        self.generate_report()
    
    def find_css_files(self):
        """Find all CSS files in the project"""
        css_patterns = ["*.css", "*.scss", "*.sass"]
        
        for pattern in css_patterns:
            css_files = list(self.dashboard_dir.rglob(pattern))
            self.css_files.extend(css_files)
    
    def audit_file_styling(self, file_path):
        """Audit styling methods in a single file"""
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        file_name = str(file_path.relative_to(self.dashboard_dir))
        
        # 1. CSS FILE IMPORTS
        css_import_patterns = [
            r'import.*\.css',
            r'from.*css',
            r'\.css["\']',
            r'stylesheet',
            r'load_css',
            r'get.*css'
        ]
        
        for pattern in css_import_patterns:
            matches = re.findall(pattern, content, re.IGNORECASE)
            for match in matches:
                self.css_injection_methods[file_name].append(f"CSS import: {match}")
        
        # 2. ST.MARKDOWN CSS INJECTION
        markdown_css_patterns = [
            r'st\.markdown\([^)]*<style[^>]*>.*?</style>',
            r'st\.markdown\([^)]*unsafe_allow_html=True',
            r'st\.markdown\([^)]*<link[^>]*>',
            r'st\.markdown\([^)]*<meta[^>]*>'
        ]
        
        for pattern in markdown_css_patterns:
            matches = re.findall(pattern, content, re.DOTALL | re.IGNORECASE)
            for match in matches:
                self.css_injection_methods[file_name].append(f"st.markdown CSS: {match[:100]}...")
        
        # 3. INLINE STYLING METHODS
        inline_patterns = [
            r'style="[^"]*"',
            r"style='[^']*'",
            r'<[^>]*style\s*=',
            r'<div[^>]*class="[^"]*"[^>]*style=',
            r'<span[^>]*style='
        ]
        
        for pattern in inline_patterns:
            matches = re.findall(pattern, content)
            for match in matches:
                self.inline_style_methods[file_name].append(f"Inline style: {match[:80]}...")
        
        # 4. COMPONENT STYLING IMPORTS
        component_import_patterns = [
            r'from.*components.*import.*',
            r'import.*brand.*',
            r'import.*styling.*',
            r'from.*styling.*import',
            r'get_.*_css',
            r'get_.*_style',
            r'brand_.*',
            r'style_.*'
        ]
        
        for pattern in component_import_patterns:
            matches = re.findall(pattern, content, re.IGNORECASE)
            for match in matches:
                self.component_imports[file_name].append(f"Component import: {match}")
        
        # 5. STREAMLIT NATIVE STYLING
        streamlit_style_patterns = [
            r'st\.markdown\([^)]*#[^)]*\)',  # Headers
            r'st\.metric\([^)]*delta_color=',
            r'st\..*\([^)]*help=',
            r'st\..*\([^)]*use_container_width=',
            r'st\..*\([^)]*height=',
            r'st\..*\([^)]*width=',
            r'st\.columns\(',
            r'st\.container\(',
            r'st\.sidebar\.',
            r'st\.expander\(',
            r'st\.tabs\('
        ]
        
        for pattern in streamlit_style_patterns:
            matches = re.findall(pattern, content)
            for match in matches:
                self.streamlit_styling[file_name].append(f"Streamlit styling: {match[:60]}...")
        
        # 6. CUSTOM STYLING FUNCTIONS
        custom_function_patterns = [
            r'def.*style.*\(',
            r'def.*css.*\(',
            r'def.*brand.*\(',
            r'def get_.*_color',
            r'def apply_.*',
            r'def format_.*',
            r'class.*Style',
            r'class.*CSS'
        ]
        
        for pattern in custom_function_patterns:
            matches = re.findall(pattern, content, re.IGNORECASE)
            for match in matches:
                self.custom_styling_functions[file_name].append(f"Custom function: {match}")
        
        # 7. CSS VARIABLES AND COLOR DEFINITIONS
        variable_patterns = [
            r'--[a-zA-Z-]+\s*:',  # CSS variables
            r'var\(--[^)]+\)',
            r'#[0-9a-fA-F]{6}',  # Hex colors
            r'#[0-9a-fA-F]{3}',  # Short hex
            r'rgb\([^)]+\)',
            r'rgba\([^)]+\)',
            r'hsl\([^)]+\)',
            r'color\s*=\s*["\'][^"\']+["\']',
            r'background.*color',
            r'primary.*color',
            r'secondary.*color'
        ]
        
        for pattern in variable_patterns:
            matches = re.findall(pattern, content, re.IGNORECASE)
            for match in matches:
                if len(match.strip()) > 2:  # Filter out tiny matches
                    self.style_variables[file_name].append(f"Style variable: {match}")
    
    def generate_report(self):
        """Generate comprehensive style application report"""
        print("\n" + "=" * 100)
        print("🚨 COMPREHENSIVE STYLE APPLICATION DISASTER REPORT")
        print("=" * 100)
        
        # CSS FILES FOUND
        print(f"\n📁 CSS FILES DISCOVERED:")
        if self.css_files:
            for css_file in self.css_files:
                print(f"   • {css_file.relative_to(self.dashboard_dir)}")
        else:
            print("   • No dedicated CSS files found")
        
        # SUMMARY METRICS
        total_css_injections = sum(len(methods) for methods in self.css_injection_methods.values())
        total_inline_styles = sum(len(methods) for methods in self.inline_style_methods.values())
        total_component_imports = sum(len(methods) for methods in self.component_imports.values())
        total_streamlit_styling = sum(len(methods) for methods in self.streamlit_styling.values())
        total_custom_functions = sum(len(methods) for methods in self.custom_styling_functions.values())
        total_style_variables = sum(len(methods) for methods in self.style_variables.values())
        
        print(f"\n📊 STYLE APPLICATION METHODS FOUND:")
        print(f"   • CSS files: {len(self.css_files)}")
        print(f"   • CSS injection methods: {total_css_injections}")
        print(f"   • Inline styling methods: {total_inline_styles}")
        print(f"   • Component imports: {total_component_imports}")
        print(f"   • Streamlit native styling: {total_streamlit_styling}")
        print(f"   • Custom styling functions: {total_custom_functions}")
        print(f"   • Style variables/colors: {total_style_variables}")
        
        total_methods = (len(self.css_files) + total_css_injections + total_inline_styles + 
                        total_component_imports + total_streamlit_styling + total_custom_functions + 
                        total_style_variables)
        
        # DETAILED BREAKDOWN BY FILE
        print(f"\n📄 STYLE APPLICATION BY FILE:")
        
        all_files = set()
        all_files.update(self.css_injection_methods.keys())
        all_files.update(self.inline_style_methods.keys())
        all_files.update(self.component_imports.keys())
        all_files.update(self.streamlit_styling.keys())
        all_files.update(self.custom_styling_functions.keys())
        all_files.update(self.style_variables.keys())
        
        for file_name in sorted(all_files):
            print(f"\n   📋 {file_name}:")
            
            # CSS Injections
            if file_name in self.css_injection_methods:
                print(f"      🎨 CSS Injections ({len(self.css_injection_methods[file_name])}):")
                for method in self.css_injection_methods[file_name][:3]:
                    print(f"         • {method}")
                if len(self.css_injection_methods[file_name]) > 3:
                    print(f"         ... and {len(self.css_injection_methods[file_name]) - 3} more")
            
            # Inline Styles
            if file_name in self.inline_style_methods:
                print(f"      ✏️ Inline Styles ({len(self.inline_style_methods[file_name])}):")
                for method in self.inline_style_methods[file_name][:3]:
                    print(f"         • {method}")
                if len(self.inline_style_methods[file_name]) > 3:
                    print(f"         ... and {len(self.inline_style_methods[file_name]) - 3} more")
            
            # Component Imports
            if file_name in self.component_imports:
                print(f"      📦 Component Imports ({len(self.component_imports[file_name])}):")
                for method in self.component_imports[file_name][:3]:
                    print(f"         • {method}")
                if len(self.component_imports[file_name]) > 3:
                    print(f"         ... and {len(self.component_imports[file_name]) - 3} more")
            
            # Streamlit Styling
            if file_name in self.streamlit_styling:
                print(f"      🎯 Streamlit Styling ({len(self.streamlit_styling[file_name])}):")
                for method in self.streamlit_styling[file_name][:3]:
                    print(f"         • {method}")
                if len(self.streamlit_styling[file_name]) > 3:
                    print(f"         ... and {len(self.streamlit_styling[file_name]) - 3} more")
            
            # Custom Functions
            if file_name in self.custom_styling_functions:
                print(f"      ⚙️ Custom Functions ({len(self.custom_styling_functions[file_name])}):")
                for method in self.custom_styling_functions[file_name][:3]:
                    print(f"         • {method}")
                if len(self.custom_styling_functions[file_name]) > 3:
                    print(f"         ... and {len(self.custom_styling_functions[file_name]) - 3} more")
            
            # Style Variables
            if file_name in self.style_variables:
                print(f"      🎨 Variables/Colors ({len(self.style_variables[file_name])}):")
                for method in self.style_variables[file_name][:3]:
                    print(f"         • {method}")
                if len(self.style_variables[file_name]) > 3:
                    print(f"         ... and {len(self.style_variables[file_name]) - 3} more")
        
        # CRITICAL FINDINGS
        print(f"\n🚨 CRITICAL FINDINGS:")
        
        # Files with most styling methods
        file_method_counts = {}
        for file_name in all_files:
            count = 0
            count += len(self.css_injection_methods.get(file_name, []))
            count += len(self.inline_style_methods.get(file_name, []))
            count += len(self.component_imports.get(file_name, []))
            count += len(self.streamlit_styling.get(file_name, []))
            count += len(self.custom_styling_functions.get(file_name, []))
            count += len(self.style_variables.get(file_name, []))
            file_method_counts[file_name] = count
        
        worst_files = sorted(file_method_counts.items(), key=lambda x: x[1], reverse=True)[:5]
        
        print(f"   📊 Files with most styling methods:")
        for file_name, count in worst_files:
            print(f"      • {file_name}: {count} methods")
        
        # Most common styling patterns
        print(f"\n   🔍 Most problematic patterns:")
        if total_inline_styles > 0:
            print(f"      • {total_inline_styles} inline styling violations")
        if total_css_injections > 0:
            print(f"      • {total_css_injections} CSS injection methods")
        if total_custom_functions > 0:
            print(f"      • {total_custom_functions} custom styling functions")
        
        # RECOMMENDATIONS
        print(f"\n✅ PERFECT STYLESHEET STRATEGY:")
        print(f"   • ELIMINATE: All {total_inline_styles} inline styles")
        print(f"   • ELIMINATE: All {total_css_injections} CSS injections")
        print(f"   • ELIMINATE: All {total_custom_functions} custom functions")
        print(f"   • STANDARDIZE: All {total_component_imports} component imports to single source")
        print(f"   • CONSOLIDATE: All {total_style_variables} variables into single CSS file")
        print(f"   • REPLACE: Mixed styling with single st.markdown() CSS injection")
        
        print(f"\n💣 STYLE APPLICATION DISASTER LEVEL: MAXIMUM CHAOS")
        print(f"   Total styling application methods: {total_methods}")
        print(f"   Files using styling: {len(all_files)}")
        print(f"   This represents complete styling anarchy across the dashboard.")
        print(f"   Every file applies styling differently.")
        print(f"   SINGLE PERFECT STYLESHEET REQUIRED IMMEDIATELY.")

def main():
    auditor = StyleApplicationAuditor()
    auditor.audit_all_styling_methods()

if __name__ == "__main__":
    main() 