#!/usr/bin/env python3
"""
JSON to Markdown Converter for Brand Audit Results

Converts persona audit JSON files to markdown format for Google LM Notebook.
"""

import json
import os
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any

def clean_persona_name(persona_name: str) -> str:
    """Clean persona name for filename."""
    return persona_name.lower().replace(' ', '_').replace('(', '').replace(')', '').replace('-', '_')

def format_score(score: float) -> str:
    """Format score with color indicator for readability."""
    if score >= 8:
        return f"🟢 **{score}/10** (Strong)"
    elif score >= 6:
        return f"🟡 **{score}/10** (Good)"
    elif score >= 4:
        return f"🟠 **{score}/10** (Needs Improvement)"
    else:
        return f"🔴 **{score}/10** (Poor)"

def format_sentiment(sentiment: str) -> str:
    """Format sentiment with emoji."""
    sentiment_map = {
        "Positive": "😊 Positive",
        "Neutral": "😐 Neutral", 
        "Negative": "😞 Negative",
        "Unknown": "❓ Unknown"
    }
    return sentiment_map.get(sentiment, sentiment)

def format_engagement(level: str) -> str:
    """Format engagement level with emoji."""
    level_map = {
        "High": "🔥 High",
        "Medium": "⚡ Medium",
        "Low": "📉 Low",
        "Very Low": "💤 Very Low",
        "Unknown": "❓ Unknown"
    }
    return level_map.get(level, level)

def convert_persona_json_to_md(json_file: Path, output_dir: Path) -> None:
    """Convert a persona JSON file to markdown."""
    
    with open(json_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    # Extract persona name from filename
    filename_parts = json_file.stem.split('_')
    if filename_parts[0] == 'persona':
        persona_parts = filename_parts[1:]
        persona_display_name = ' '.join(word.title() for word in persona_parts).replace('_', ' ')
    else:
        persona_display_name = "Combined Results"
    
    # Create output filename
    if json_file.stem == 'compiled_persona_data':
        output_filename = "ba_results_0725_all_personas_combined.md"
    elif json_file.stem == 'compilation_summary':
        output_filename = "ba_results_0725_summary_overview.md"
    else:
        clean_name = clean_persona_name(persona_display_name)
        output_filename = f"ba_results_0725_persona_{clean_name}.md"
    
    output_file = output_dir / output_filename
    
    # Handle different file types
    if json_file.stem == 'compilation_summary':
        convert_summary_to_md(data, output_file, persona_display_name)
    elif json_file.stem == 'compiled_persona_data':
        convert_combined_data_to_md(data, output_file)
    else:
        convert_individual_persona_to_md(data, output_file, persona_display_name)

def convert_summary_to_md(data: Dict, output_file: Path, title: str) -> None:
    """Convert compilation summary to markdown."""
    
    md_content = f"""# Brand Audit Results Summary - July 2025

**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}  
**Data Compiled:** {data.get('compilation_timestamp', 'Unknown')}

## Overview

- **Total Documents Analyzed:** {data.get('total_documents', 0)}
- **Unique Pages:** {data.get('unique_pages', 0)}
- **Domains Covered:** {data.get('unique_domains', 0)}
- **Content Types:** {len(data.get('content_types', []))}

## Personas Analyzed

"""
    
    for persona in data.get('personas', []):
        doc_count = data.get('documents_per_persona', {}).get(persona, 0)
        md_content += f"- **{persona}:** {doc_count} documents\n"
    
    md_content += f"""

## Content Types Identified

{', '.join(data.get('content_types', []))}

## Data Structure

Each persona evaluation includes:
- Hygiene scorecard with detailed scoring
- Experience report with strategic analysis
- Effective and ineffective copy examples
- Recommendations for improvement
- Metadata for filtering and analysis

---
*This summary provides an overview of the brand audit results across all personas and pages.*
"""
    
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(md_content)

def convert_combined_data_to_md(data: List[Dict], output_file: Path) -> None:
    """Convert combined persona data to markdown (summary format for notebook)."""
    
    # Group by persona
    personas = {}
    for doc in data:
        persona_name = doc.get('persona', {}).get('name', 'Unknown')
        if persona_name not in personas:
            personas[persona_name] = []
        personas[persona_name].append(doc)
    
    md_content = f"""# Brand Audit Results - All Personas Combined - July 2025

**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}  
**Total Documents:** {len(data)}

## Executive Summary

This document contains comprehensive brand audit results across all personas, analyzing how different user types experience Sopra Steria's digital presence.

"""

    for persona_name, docs in personas.items():
        md_content += f"""
## {persona_name}

**Documents Analyzed:** {len(docs)}

### Score Overview
"""
        
        # Calculate average scores
        scores = [doc.get('hygiene_scorecard', {}).get('final_score', 0) for doc in docs]
        avg_score = sum(scores) / len(scores) if scores else 0
        
        md_content += f"- **Average Score:** {format_score(avg_score)}\n"
        
        # Get top and bottom performing pages
        docs_with_scores = [(doc, doc.get('hygiene_scorecard', {}).get('final_score', 0)) for doc in docs]
        docs_with_scores.sort(key=lambda x: x[1], reverse=True)
        
        md_content += f"""
### Top Performing Pages
"""
        for doc, score in docs_with_scores[:3]:
            url = doc.get('url', 'Unknown URL')
            md_content += f"- {format_score(score)} - {url}\n"
        
        md_content += f"""
### Needs Improvement
"""
        for doc, score in docs_with_scores[-3:]:
            url = doc.get('url', 'Unknown URL')
            md_content += f"- {format_score(score)} - {url}\n"
        
        md_content += "\n---\n"
    
    md_content += """
## Usage in Google LM Notebook

This data can be used for:
- Cross-persona analysis and comparisons
- Content optimization recommendations
- Identifying patterns across different user types
- Strategic decision making for digital presence

### Query Examples

```python
# Find high-scoring pages across all personas
high_scores = [doc for doc in data if doc['hygiene_scorecard']['final_score'] >= 7.0]

# Compare persona sentiment
sentiments = {doc['persona']['name']: doc['experience_report']['overall_sentiment'] for doc in data}

# Analyze by content type
by_content_type = {}
for doc in data:
    content_type = doc['metadata']['content_type']
    if content_type not in by_content_type:
        by_content_type[content_type] = []
    by_content_type[content_type].append(doc)
```

---
*For detailed analysis of individual personas, see the separate persona-specific markdown files.*
"""
    
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(md_content)

def convert_individual_persona_to_md(data: List[Dict], output_file: Path, persona_name: str) -> None:
    """Convert individual persona data to detailed markdown."""
    
    if not data:
        return
    
    # Get persona info from first document
    sample_doc = data[0]
    persona_desc = sample_doc.get('persona', {}).get('description', '')
    
    md_content = f"""# Brand Audit Results: {persona_name} - July 2025

**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}  
**Documents Analyzed:** {len(data)}

## Persona Profile

{persona_desc}

## Overall Performance

"""
    
    # Calculate statistics
    scores = [doc.get('hygiene_scorecard', {}).get('final_score', 0) for doc in data]
    avg_score = sum(scores) / len(scores) if scores else 0
    max_score = max(scores) if scores else 0
    min_score = min(scores) if scores else 0
    
    sentiments = [doc.get('experience_report', {}).get('overall_sentiment', 'Unknown') for doc in data]
    engagement_levels = [doc.get('experience_report', {}).get('engagement_level', 'Unknown') for doc in data]
    
    md_content += f"""
- **Average Score:** {format_score(avg_score)}
- **Best Performance:** {format_score(max_score)}
- **Needs Most Improvement:** {format_score(min_score)}
- **Dominant Sentiment:** {format_sentiment(max(set(sentiments), key=sentiments.count))}
- **Typical Engagement:** {format_engagement(max(set(engagement_levels), key=engagement_levels.count))}

## Detailed Page Analysis

"""
    
    # Sort by score for analysis
    sorted_docs = sorted(data, key=lambda x: x.get('hygiene_scorecard', {}).get('final_score', 0), reverse=True)
    
    for i, doc in enumerate(sorted_docs, 1):
        url = doc.get('url', 'Unknown URL')
        score = doc.get('hygiene_scorecard', {}).get('final_score', 0)
        tier = doc.get('hygiene_scorecard', {}).get('tier', 'Unknown')
        sentiment = doc.get('experience_report', {}).get('overall_sentiment', 'Unknown')
        engagement = doc.get('experience_report', {}).get('engagement_level', 'Unknown')
        
        md_content += f"""
### {i}. Page Analysis

**URL:** {url}  
**Score:** {format_score(score)}  
**Tier:** {tier}  
**Sentiment:** {format_sentiment(sentiment)}  
**Engagement:** {format_engagement(engagement)}

"""
        
        # Add key themes
        themes = doc.get('embeddings_content', {}).get('key_themes', [])
        if themes:
            md_content += f"**Key Themes:** {', '.join(themes)}\n\n"
        
        # Add effective copy examples
        effective_copy = doc.get('experience_report', {}).get('effective_copy', [])
        if effective_copy:
            md_content += "**✅ Effective Copy:**\n"
            for copy_item in effective_copy[:2]:  # Limit to top 2
                text = copy_item.get('text', '')[:100] + '...' if len(copy_item.get('text', '')) > 100 else copy_item.get('text', '')
                analysis = copy_item.get('analysis', '')[:150] + '...' if len(copy_item.get('analysis', '')) > 150 else copy_item.get('analysis', '')
                md_content += f"- *\"{text}\"*\n  - {analysis}\n\n"
        
        # Add ineffective copy examples
        ineffective_copy = doc.get('experience_report', {}).get('ineffective_copy', [])
        if ineffective_copy:
            md_content += "**❌ Ineffective Copy:**\n"
            for copy_item in ineffective_copy[:2]:  # Limit to top 2
                text = copy_item.get('text', '')[:100] + '...' if len(copy_item.get('text', '')) > 100 else copy_item.get('text', '')
                analysis = copy_item.get('analysis', '')[:150] + '...' if len(copy_item.get('analysis', '')) > 150 else copy_item.get('analysis', '')
                md_content += f"- *\"{text}\"*\n  - {analysis}\n\n"
        
        # Add top recommendation
        recommendations = doc.get('hygiene_scorecard', {}).get('recommendations', [])
        if recommendations:
            top_rec = recommendations[0]
            priority = top_rec.get('priority', 'Medium')
            recommendation = top_rec.get('recommendation', '')[:200] + '...' if len(top_rec.get('recommendation', '')) > 200 else top_rec.get('recommendation', '')
            md_content += f"**🎯 Top Recommendation ({priority} Priority):**\n{recommendation}\n\n"
        
        md_content += "---\n\n"
    
    # Add strategic insights
    md_content += f"""
## Strategic Insights for {persona_name}

### Content Strengths
"""
    
    # Find common themes in high-scoring pages
    high_scoring_docs = [doc for doc in data if doc.get('hygiene_scorecard', {}).get('final_score', 0) >= 7.0]
    if high_scoring_docs:
        all_themes = []
        for doc in high_scoring_docs:
            all_themes.extend(doc.get('embeddings_content', {}).get('key_themes', []))
        
        if all_themes:
            from collections import Counter
            common_themes = Counter(all_themes).most_common(3)
            for theme, count in common_themes:
                md_content += f"- **{theme.title()}** (appears in {count} high-scoring pages)\n"
    
    md_content += f"""

### Areas for Improvement

"""
    
    # Find common issues in low-scoring pages
    low_scoring_docs = [doc for doc in data if doc.get('hygiene_scorecard', {}).get('final_score', 0) < 6.0]
    if low_scoring_docs:
        all_recommendations = []
        for doc in low_scoring_docs:
            recommendations = doc.get('hygiene_scorecard', {}).get('recommendations', [])
            for rec in recommendations:
                if rec.get('priority') == 'High':
                    all_recommendations.append(rec.get('recommendation', ''))
        
        if all_recommendations:
            # Show top 3 unique recommendations
            unique_recs = list(set(all_recommendations))[:3]
            for rec in unique_recs:
                short_rec = rec[:200] + '...' if len(rec) > 200 else rec
                md_content += f"- {short_rec}\n"
    
    md_content += """

---

## Usage in Google LM Notebook

This data can be analyzed using:

```python
import json

# Load data
with open('ba_results_0725_persona_[name].json') as f:
    persona_data = json.load(f)

# Analyze scores
scores = [doc['hygiene_scorecard']['final_score'] for doc in persona_data]
avg_score = sum(scores) / len(scores)

# Find best performing content types
content_performance = {}
for doc in persona_data:
    content_type = doc['metadata']['content_type']
    score = doc['hygiene_scorecard']['final_score']
    if content_type not in content_performance:
        content_performance[content_type] = []
    content_performance[content_type].append(score)

# Calculate averages
for content_type, scores in content_performance.items():
    avg = sum(scores) / len(scores)
    print(f"{content_type}: {avg:.2f}")
```

---
*This analysis provides detailed insights for optimizing content and user experience for this specific persona.*
"""
    
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(md_content)

def main():
    """Main conversion function."""
    data_dir = Path('data')
    output_dir = Path('md')
    
    if not data_dir.exists():
        print(f"❌ Data directory not found: {data_dir}")
        return
    
    output_dir.mkdir(exist_ok=True)
    
    # Process all JSON files
    json_files = list(data_dir.glob('*.json'))
    
    if not json_files:
        print("❌ No JSON files found in data directory")
        return
    
    print(f"🔄 Converting {len(json_files)} JSON files to markdown...")
    
    for json_file in json_files:
        try:
            print(f"📝 Converting {json_file.name}...")
            convert_persona_json_to_md(json_file, output_dir)
            print(f"✅ Created markdown file for {json_file.name}")
        except Exception as e:
            print(f"❌ Error converting {json_file.name}: {e}")
    
    print(f"\n🎉 Conversion complete! Check the 'md/' directory for results.")
    print(f"📁 Output location: {output_dir.absolute()}")

if __name__ == "__main__":
    main() 