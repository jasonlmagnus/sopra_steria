#!/usr/bin/env python3
"""
SYSTEMATIC STYLESHEET COMPLETENESS AUDIT
Checks if perfect_stylesheet.css covers ALL required styling elements
"""

import re
from pathlib import Path

# ALL REQUIRED STYLING ELEMENTS (from our comprehensive audits)
REQUIRED_ELEMENTS = {
    # CORE VARIABLES
    "css_variables": [
        "--primary-color", "--primary-hover", "--secondary-color", 
        "--background", "--text-primary", "--text-secondary", 
        "--border-color", "--gray-border", "--status-excellent", 
        "--status-good", "--status-warning", "--status-critical",
        "--green-status", "--yellow-status", "--red-status", "--orange-status",
        "--font-size-h1", "--font-size-h2", "--font-size-body", 
        "--font-primary", "--font-secondary", "--font-serif",
        "--spacing-xs", "--spacing-sm", "--spacing-md", "--spacing-lg", "--spacing-xl",
        "--border-radius", "--shadow-sm", "--shadow-md",
        "--chart-height", "--chart-color-1", "--chart-color-2", 
        "--text-selection"
    ],
    
    # TYPOGRAPHY
    "typography": [
        ".main .block-container", "h1, h2, h3, h4, h5, h6", 
        ".main-header h1", ".section-header", ".body-text",
        "::selection"
    ],
    
    # LAYOUT COMPONENTS  
    "layout": [
        ".main-header", ".content-container"
    ],
    
    # CARD COMPONENTS
    "cards": [
        ".metric-card", ".metric-card.critical", ".metric-card.warning", ".metric-card.fair",
        ".metric-value", ".metric-label", ".content-card",
        ".brand-card", ".persona-card", ".matrix-card", 
        ".opportunity-card", ".success-card", ".report-card"
    ],
    
    # STATUS COMPONENTS
    "status": [
        ".status-card", ".status-excellent", ".status-good", 
        ".status-warning", ".status-critical", ".status-running", 
        ".status-complete", ".status-error",
        ".sentiment-positive", ".sentiment-neutral", ".sentiment-negative",
        ".engagement-high", ".engagement-medium", ".engagement-low",
        ".performance-excellent", ".performance-good", ".performance-fair"
    ],
    
    # BUTTON COMPONENTS
    "buttons": [
        ".primary-button", ".secondary-button", 
        ".apply-button", ".action-button", ".nav-button",
        ".export-button", ".audit-button", ".copy-button"
    ],
    
    # BADGE COMPONENTS
    "badges": [
        ".badge", ".badge-excellent", ".badge-good", ".badge-warning", ".badge-critical",
        ".strength-badge", ".quick-win-badge", ".pattern-tag", ".critical-badge"
    ],
    
    # IMPACT & PRIORITY
    "impact_priority": [
        ".impact-high", ".impact-medium", ".impact-low",
        ".priority-urgent", ".priority-high", ".priority-medium",
        ".success-excellent", ".success-good"
    ],
    
    # SPECIALIZED CARDS
    "specialized_cards": [
        ".pattern-card", ".ai-recommendation", ".criteria-insight",
        ".drill-down-section", ".audit-section", ".insights-box",
        ".comparison-section", ".tier-section", ".export-section",
        ".persona-quote", ".evidence-section", ".copy-example"
    ],
    
    # FORM COMPONENTS
    "forms": [
        ".form-group", ".form-label"
    ],
    
    # TABLE COMPONENTS
    "tables": [
        ".data-table", ".data-table th", ".data-table td"
    ],
    
    # ALERT COMPONENTS
    "alerts": [
        ".alert", ".alert-info", ".alert-success", ".alert-warning", ".alert-error"
    ],
    
    # LAYOUT UTILITIES
    "utilities": [
        ".flex", ".flex-col", ".items-center", ".justify-between",
        ".gap-sm", ".gap-md", ".gap-lg",
        ".mt-sm", ".mt-md", ".mt-lg", ".mt-xl",
        ".mb-sm", ".mb-md", ".mb-lg", ".mb-xl",
        ".p-sm", ".p-md", ".p-lg", ".p-xl",
        ".text-center", ".text-left", ".text-right",
        ".text-primary", ".text-secondary", ".text-brand",
        ".font-semibold", ".font-normal"
    ],
    
    # SCORE DISPLAY
    "score": [
        ".impact-score"
    ],
    
    # STREAMLIT OVERRIDES
    "streamlit_overrides": [
        ".stMetric", ".stSelectbox > div > div", ".stSlider > div > div", 
        ".stNumberInput > div > div", ".stButton > button", 
        "[data-testid=\"metric-container\"]",
        ".stTabs [data-baseweb=\"tab-list\"]", ".stTabs [data-baseweb=\"tab\"]",
        ".stTabs [data-baseweb=\"tab\"][aria-selected=\"true\"]"
    ],
    
    # HEADER OVERRIDES
    "header_overrides": [
        ".main h1", ".main h2", ".main h3", ".main h4", ".main h5", ".main h6",
        "div[data-testid=\"stMarkdownContainer\"] h1",
        "div[data-testid=\"stMarkdownContainer\"] h2",
        "div[data-testid=\"stMarkdownContainer\"] h3"
    ],
    
    # LINKS
    "links": [
        "a", "a:hover"
    ],
    
    # CHARTS
    "charts": [
        ".plotly-chart"
    ],
    
    # RESPONSIVE
    "responsive": [
        "@media (max-width: 768px)"
    ],
    
    # ACCESSIBILITY
    "accessibility": [
        "@media (prefers-reduced-motion: reduce)",
        "button:focus", "select:focus", "input:focus"
    ],
    
    # PRINT STYLES
    "print": [
        "@media print"
    ]
}

def load_stylesheet():
    """Load the perfect stylesheet"""
    css_file = Path("audit_tool/dashboard/components/perfect_stylesheet.css")
    if css_file.exists():
        with open(css_file, 'r') as f:
            return f.read()
    return ""

def check_element_coverage(css_content):
    """Check which required elements are covered"""
    results = {}
    missing_elements = []
    found_elements = []
    duplicates = {}
    
    for category, elements in REQUIRED_ELEMENTS.items():
        results[category] = {"found": [], "missing": []}
        
        for element in elements:
            # Escape CSS selector for regex
            escaped_element = re.escape(element)
            
            # Count occurrences - different patterns for variables vs selectors
            if element.startswith('--'):
                # CSS variable pattern: --variable-name:
                pattern = rf'{escaped_element}\s*:'
                matches = re.findall(pattern, css_content, re.IGNORECASE)
                count = len(matches)
            else:
                # CSS selector pattern: handle both single and grouped selectors
                # Look for the selector anywhere in the CSS, followed by comma, space, or {
                pattern = rf'{escaped_element}(?=\s*[,\{{])'
                matches = re.findall(pattern, css_content, re.IGNORECASE)
                count = len(matches)
            
            if count > 0:
                results[category]["found"].append(element)
                found_elements.append(element)
                
                if count > 1:
                    duplicates[element] = count
            else:
                results[category]["missing"].append(element)
                missing_elements.append(element)
    
    return results, missing_elements, found_elements, duplicates

def check_for_inconsistencies(css_content):
    """Check for inconsistencies in the stylesheet"""
    inconsistencies = []
    
    # Check for multiple font family declarations
    font_families = re.findall(r'font-family:\s*([^;]+);', css_content)
    unique_families = set(font_families)
    if len(unique_families) > 5:  # Allow for some variation
        inconsistencies.append(f"Too many font family variations: {len(unique_families)}")
    
    # Check for multiple color definitions for same purpose
    color_patterns = [
        (r'color:\s*(#[0-9a-fA-F]{6})', 'Direct color usage'),
        (r'background-color:\s*(#[0-9a-fA-F]{6})', 'Direct background color usage'),
        (r'border-color:\s*(#[0-9a-fA-F]{6})', 'Direct border color usage')
    ]
    
    for pattern, description in color_patterns:
        colors = re.findall(pattern, css_content)
        if len(set(colors)) > 10:  # Too many hardcoded colors
            inconsistencies.append(f"{description}: {len(set(colors))} different colors found")
    
    # Check for conflicting margin/padding values
    spacing_conflicts = []
    spacing_props = ['margin', 'padding', 'margin-top', 'margin-bottom', 'padding-top', 'padding-bottom']
    
    for prop in spacing_props:
        values = re.findall(rf'{prop}:\s*([^;]+);', css_content)
        unique_values = set(values)
        if len(unique_values) > 8:  # Too many different spacing values
            spacing_conflicts.append(f"{prop}: {len(unique_values)} different values")
    
    if spacing_conflicts:
        inconsistencies.append(f"Spacing inconsistencies: {', '.join(spacing_conflicts)}")
    
    return inconsistencies

def analyze_stylesheet():
    """Perform comprehensive stylesheet analysis"""
    print("🔍 SYSTEMATIC STYLESHEET COMPLETENESS AUDIT")
    print("=" * 60)
    
    css_content = load_stylesheet()
    if not css_content:
        print("❌ ERROR: Could not load perfect_stylesheet.css")
        return
    
    print(f"📄 Stylesheet loaded: {len(css_content)} characters")
    print()
    
    # Check element coverage
    results, missing_elements, found_elements, duplicates = check_element_coverage(css_content)
    
    # Summary statistics
    total_required = sum(len(elements) for elements in REQUIRED_ELEMENTS.values())
    total_found = len(found_elements)
    total_missing = len(missing_elements)
    coverage_percentage = (total_found / total_required) * 100
    
    print("📊 COVERAGE SUMMARY:")
    print(f"   Total Required Elements: {total_required}")
    print(f"   Elements Found: {total_found}")
    print(f"   Elements Missing: {total_missing}")
    print(f"   Coverage: {coverage_percentage:.1f}%")
    print()
    
    # Category breakdown
    print("📋 CATEGORY BREAKDOWN:")
    for category, data in results.items():
        found_count = len(data["found"])
        missing_count = len(data["missing"])
        total_count = found_count + missing_count
        category_coverage = (found_count / total_count) * 100 if total_count > 0 else 0
        
        status = "✅" if category_coverage == 100 else "⚠️" if category_coverage >= 80 else "❌"
        print(f"   {status} {category.upper()}: {found_count}/{total_count} ({category_coverage:.0f}%)")
        
        if missing_count > 0:
            print(f"      Missing: {', '.join(data['missing'])}")
    print()
    
    # Duplicates check
    if duplicates:
        print("🔄 DUPLICATES FOUND:")
        for element, count in duplicates.items():
            print(f"   ⚠️ {element}: {count} occurrences")
        print()
    else:
        print("✅ No duplicates found")
        print()
    
    # Inconsistencies check
    inconsistencies = check_for_inconsistencies(css_content)
    if inconsistencies:
        print("🚨 INCONSISTENCIES FOUND:")
        for inconsistency in inconsistencies:
            print(f"   ⚠️ {inconsistency}")
        print()
    else:
        print("✅ No major inconsistencies found")
        print()
    
    # Final verdict
    print("🎯 FINAL VERDICT:")
    if coverage_percentage == 100 and not duplicates and not inconsistencies:
        print("   🏆 PERFECT STYLESHEET - 100% COMPLETE AND CONSISTENT!")
    elif coverage_percentage >= 95:
        print("   🥇 EXCELLENT STYLESHEET - Nearly complete")
    elif coverage_percentage >= 85:
        print("   🥈 GOOD STYLESHEET - Minor gaps remain")
    else:
        print("   🥉 INCOMPLETE STYLESHEET - Significant work needed")
    
    print(f"   Final Score: {coverage_percentage:.1f}%")
    
    return {
        "coverage_percentage": coverage_percentage,
        "missing_elements": missing_elements,
        "duplicates": duplicates,
        "inconsistencies": inconsistencies,
        "total_required": total_required,
        "total_found": total_found
    }

if __name__ == "__main__":
    analyze_stylesheet() 