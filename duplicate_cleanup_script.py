#!/usr/bin/env python3
"""
DUPLICATE CLEANUP SCRIPT
Systematically removes all duplicates and inconsistencies from perfect_stylesheet.css
"""

import re
from pathlib import Path
from collections import defaultdict

def load_stylesheet():
    """Load the perfect stylesheet"""
    css_file = Path("audit_tool/dashboard/components/perfect_stylesheet.css")
    if css_file.exists():
        with open(css_file, 'r') as f:
            return f.read()
    return ""

def save_stylesheet(content):
    """Save the cleaned stylesheet"""
    css_file = Path("audit_tool/dashboard/components/perfect_stylesheet.css")
    with open(css_file, 'w') as f:
        f.write(content)

def find_duplicates(css_content):
    """Find all duplicate CSS rules"""
    duplicates = defaultdict(list)
    
    # Find CSS variable duplicates
    var_pattern = r'(--[a-zA-Z-]+):\s*([^;]+);'
    var_matches = re.finditer(var_pattern, css_content)
    
    var_occurrences = defaultdict(list)
    for match in var_matches:
        var_name = match.group(1)
        var_value = match.group(2)
        var_occurrences[var_name].append((match.start(), match.end(), var_value))
    
    # Find CSS selector duplicates
    selector_pattern = r'([.#]?[a-zA-Z0-9_-]+(?:\[[^\]]+\])?(?:::[a-zA-Z-]+)?(?:\s*[,\s]\s*[.#]?[a-zA-Z0-9_-]+(?:\[[^\]]+\])?(?:::[a-zA-Z-]+)?)*)\s*\{'
    selector_matches = re.finditer(selector_pattern, css_content)
    
    selector_occurrences = defaultdict(list)
    for match in selector_matches:
        selector = match.group(1).strip()
        # Skip grouped selectors for now
        if ',' not in selector:
            selector_occurrences[selector].append((match.start(), match.end()))
    
    return var_occurrences, selector_occurrences

def remove_duplicates(css_content):
    """Remove duplicate CSS rules"""
    print("🔄 Removing duplicates...")
    
    var_occurrences, selector_occurrences = find_duplicates(css_content)
    
    # Remove duplicate variables (keep first occurrence)
    for var_name, occurrences in var_occurrences.items():
        if len(occurrences) > 1:
            print(f"   Removing {len(occurrences)-1} duplicate(s) of {var_name}")
            # Sort by position (reverse order to avoid index shifting)
            occurrences.sort(key=lambda x: x[0], reverse=True)
            
            # Remove all but the first occurrence
            for i in range(len(occurrences)-1):
                start, end, value = occurrences[i]
                css_content = css_content[:start] + css_content[end:]
    
    return css_content

def standardize_spacing(css_content):
    """Standardize spacing values to use CSS variables"""
    print("📏 Standardizing spacing...")
    
    # Define standard spacing mappings
    spacing_map = {
        '0.25rem': 'var(--spacing-xs)',
        '0.5rem': 'var(--spacing-sm)', 
        '1rem': 'var(--spacing-md)',
        '1.5rem': 'var(--spacing-lg)',
        '2rem': 'var(--spacing-xl)',
        '0.75rem': 'var(--spacing-sm)',  # Map to closest
        '1.25rem': 'var(--spacing-md)',  # Map to closest
        '2.5rem': 'var(--spacing-xl)',   # Map to closest
    }
    
    # Replace hardcoded spacing with variables
    for hardcoded, variable in spacing_map.items():
        css_content = css_content.replace(hardcoded, variable)
        print(f"   Replaced {hardcoded} with {variable}")
    
    return css_content

def standardize_fonts(css_content):
    """Standardize font family declarations"""
    print("🔤 Standardizing fonts...")
    
    # Define standard font mappings
    font_map = {
        '"Inter", sans-serif': 'var(--font-primary)',
        "'Inter', sans-serif": 'var(--font-primary)',
        'Inter, sans-serif': 'var(--font-primary)',
        '"Crimson Text", serif': 'var(--font-serif)',
        "'Crimson Text', serif": 'var(--font-serif)',
        'Crimson Text, serif': 'var(--font-serif)',
        '"Inter", monospace': 'var(--font-primary)', # Close enough
    }
    
    # Replace hardcoded fonts with variables
    for hardcoded, variable in font_map.items():
        if hardcoded in css_content:
            css_content = css_content.replace(hardcoded, variable)
            print(f"   Replaced {hardcoded} with {variable}")
    
    return css_content

def remove_redundant_rules(css_content):
    """Remove redundant CSS rules"""
    print("🗑️ Removing redundant rules...")
    
    # Remove duplicate .main-header definitions
    # Keep only the most comprehensive one
    main_header_pattern = r'\.main-header\s*\{[^}]+\}'
    main_header_matches = list(re.finditer(main_header_pattern, css_content, re.DOTALL))
    
    if len(main_header_matches) > 1:
        print(f"   Found {len(main_header_matches)} .main-header definitions, keeping the most comprehensive")
        
        # Find the longest/most comprehensive definition
        longest_match = max(main_header_matches, key=lambda m: len(m.group(0)))
        
        # Remove all others (in reverse order to avoid index shifting)
        for match in reversed(main_header_matches):
            if match != longest_match:
                css_content = css_content[:match.start()] + css_content[match.end():]
    
    # Similar cleanup for other duplicate selectors
    duplicate_selectors = ['.metric-card', '.content-card', '.status-card']
    
    for selector in duplicate_selectors:
        pattern = rf'{re.escape(selector)}\s*\{{[^}}]+\}}'
        matches = list(re.finditer(pattern, css_content, re.DOTALL))
        
        if len(matches) > 1:
            print(f"   Found {len(matches)} {selector} definitions, consolidating")
            # Keep the first comprehensive one, remove others
            for match in reversed(matches[1:]):
                css_content = css_content[:match.start()] + css_content[match.end():]
    
    return css_content

def optimize_css_structure(css_content):
    """Optimize CSS structure and organization"""
    print("🎯 Optimizing CSS structure...")
    
    # Remove excessive whitespace
    css_content = re.sub(r'\n\s*\n\s*\n', '\n\n', css_content)  # Max 2 consecutive newlines
    css_content = re.sub(r'[ \t]+', ' ', css_content)  # Normalize spaces
    css_content = re.sub(r' *\{ *', ' {\n    ', css_content)  # Format opening braces
    css_content = re.sub(r'; *', ';\n    ', css_content)  # Format semicolons
    css_content = re.sub(r' *\} *', '\n}\n', css_content)  # Format closing braces
    
    return css_content

def cleanup_stylesheet():
    """Main cleanup function"""
    print("🧹 CLEANING UP PERFECT STYLESHEET")
    print("=" * 50)
    
    css_content = load_stylesheet()
    if not css_content:
        print("❌ ERROR: Could not load stylesheet")
        return
    
    print(f"📄 Original stylesheet: {len(css_content)} characters")
    
    # Step 1: Remove duplicates
    css_content = remove_duplicates(css_content)
    
    # Step 2: Standardize spacing
    css_content = standardize_spacing(css_content)
    
    # Step 3: Standardize fonts
    css_content = standardize_fonts(css_content)
    
    # Step 4: Remove redundant rules
    css_content = remove_redundant_rules(css_content)
    
    # Step 5: Optimize structure
    css_content = optimize_css_structure(css_content)
    
    print(f"📄 Cleaned stylesheet: {len(css_content)} characters")
    
    # Save cleaned stylesheet
    save_stylesheet(css_content)
    print("✅ Cleaned stylesheet saved!")
    
    return css_content

if __name__ == "__main__":
    cleanup_stylesheet() 