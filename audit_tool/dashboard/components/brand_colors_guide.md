# Brand Colors Guide

## Overview

The Brand Health Command Center uses a comprehensive, brand-compliant color palette for consistency across all visualizations and UI components.

## Quick Start

```python
from components.brand_styling import get_brand_colors, get_rag_colors, get_plotly_color_scale, get_chart_template

# Get all brand colors
colors = get_brand_colors()

# Use in Plotly charts
fig = px.bar(data, color_discrete_sequence=colors['chart_colors'])
fig.update_layout(**get_chart_template()['layout'])
```

## Color Palettes

### Core Brand Colors

- **Primary**: `#E85A4F` (Brand red)
- **Primary Light**: `#f4a298`
- **Primary Dark**: `#c73e2f`
- **Secondary**: `#2C3E50` (Brand blue-gray)
- **Secondary Light**: `#5d6d7e`
- **Secondary Dark**: `#1b2631`

### Status Colors (RAG)

- **Excellent**: `#10b981` (Professional emerald green)
- **Good**: `#059669` (Darker green for contrast)
- **Warning**: `#f59e0b` (Amber - softer than yellow)
- **Critical**: `#dc2626` (Red aligned with brand)
- **Info**: `#3b82f6` (Blue for informational)

### Chart Color Sequence

1. `#E85A4F` - Primary brand red
2. `#2C3E50` - Secondary brand blue-gray
3. `#10b981` - Success green
4. `#f59e0b` - Warning amber
5. `#8b5cf6` - Purple accent
6. `#06b6d4` - Cyan accent
7. `#84cc16` - Lime accent
8. `#f97316` - Orange accent

## Usage Examples

### Bar Charts with RAG Coloring

```python
colors = get_brand_colors()

fig = px.bar(
    data,
    color=score_column,
    color_continuous_scale=get_plotly_color_scale(),
    range_color=[0, 10]
)
fig.update_layout(**get_chart_template()['layout'])
```

### Categorical Charts

```python
colors = get_brand_colors()

fig = px.pie(
    data,
    color_discrete_sequence=colors['chart_colors']
)
fig.update_layout(**get_chart_template()['layout'])
```

### Status Indicators

```python
rag_colors = get_rag_colors()

# Use in conditional styling
if score >= 8:
    color = rag_colors['green']
elif score >= 6:
    color = rag_colors['dark_green']
elif score >= 4:
    color = rag_colors['amber']
else:
    color = rag_colors['red']
```

### CSS Classes

Use these CSS classes for consistent styling:

- `.status-excellent` - Green text
- `.status-good` - Dark green text
- `.status-warning` - Amber text
- `.status-critical` - Red text
- `.status-info` - Blue text

- `.metric-card.excellent` - Green left border
- `.metric-card.good` - Dark green left border
- `.metric-card.warning` - Amber left border
- `.metric-card.critical` - Red left border

## Functions Reference

### `get_brand_colors()`

Returns dictionary with all brand colors including:

- Core brand colors
- Status colors
- Chart color sequence
- Neutral colors

### `get_rag_colors()`

Returns simplified Red-Amber-Green status colors for quick access.

### `get_plotly_color_scale()`

Returns Plotly-compatible color scale for continuous data visualization.

### `get_chart_template()`

Returns complete Plotly template with brand fonts, colors, and styling.

## Best Practices

1. **Always use brand colors** - Never hardcode colors
2. **Consistent RAG logic** - Use same thresholds across pages
3. **Accessible contrast** - All colors meet WCAG guidelines
4. **White backgrounds** - All components have explicit white backgrounds for dark mode
5. **Font consistency** - Use Inter for UI, Crimson Text for headings

## Migration from Old Colors

Replace these patterns:

- `color_continuous_scale='RdYlGn'` → `color_continuous_scale=get_plotly_color_scale()`
- `color_continuous_scale='Blues'` → `color_discrete_sequence=[colors['secondary']]`
- Default pie chart colors → `color_discrete_sequence=colors['chart_colors']`
