# AGENTS.md - Codex Development Instructions

**Created:** 2025-01-27  
**Purpose:** Clear instructions for Codex to create new React dashboard pages alongside existing ones

## Overview

This document provides precise instructions for Codex to create new React dashboard pages that:
1. Work alongside existing React dashboard pages
2. Use and extend the data mapping utility
3. Maintain compatibility with Streamlit reference pages
4. Preserve all existing functionality

## Current Architecture

### Existing Structure
- **React Dashboard:** `web/src/pages/` - Main dashboard pages
- **Data Mapping:** `web/src/utils/mapApiData.ts` - Centralized data normalization
- **API Integration:** FastAPI backend with unified CSV data source
- **Reference Implementation:** Streamlit dashboard for comparison

### Key Files to Understand
- `web/src/utils/mapApiData.ts` - Maps API data to consistent format
- `web/src/pages/` - All existing React dashboard pages
- `audit_tool/dashboard/` - Streamlit reference implementation
- `api/src/` - FastAPI backend with metrics calculation

## Development Rules

### 1. Data Mapping Requirements

**ALWAYS use the mapping utility:**
```typescript
import { mapApiData } from '../utils/mapApiData';

// Use for all API data
const mappedData = mapApiData(rawApiData);
```

**Extend the mapping utility when needed:**
- Add new field mappings to `mapApiData.ts`
- Maintain backward compatibility
- Document new mappings with comments
- Test with existing pages

### 2. Page Creation Guidelines

**File Naming Convention:**
- **For NEW features:** Use descriptive names: `NewFeaturePage.tsx`
- **For Ant Design versions of existing pages:** Use `{OriginalPageName}_AntDesign.tsx`
- **Examples:**
  - Original: `ExecutiveDashboard.tsx` → Ant Design: `ExecutiveDashboard_AntDesign.tsx`
  - Original: `AuditReports.tsx` → Ant Design: `AuditReports_AntDesign.tsx`
  - Original: `ContentMatrix.tsx` → Ant Design: `ContentMatrix_AntDesign.tsx`
- **NEVER overwrite existing files** - always create alongside them
- Place in `web/src/pages/` directory

**Component Structure:**
```typescript
import React, { useState, useEffect } from 'react';
import { mapApiData } from '../utils/mapApiData';
import { useDataset } from '../hooks/useDataset';
import { useFilters } from '../hooks/useFilters';

const NewFeaturePage: React.FC = () => {
  const { data, loading, error } = useDataset();
  const { filters } = useFilters();
  
  // Always map API data
  const mappedData = data ? mapApiData(data) : null;
  
  // Component logic here
  return (
    <div>
      {/* UI components */}
    </div>
  );
};

export default NewFeaturePage;
```

### 3. API Integration Rules

**Use existing hooks:**
- `useDataset()` - For main dataset
- `useFilters()` - For filter state
- `useApiData()` - For specific API endpoints

**Data Flow:**
1. Fetch data from API
2. Apply `mapApiData()` transformation
3. Use mapped data in components
4. Handle loading/error states

### 4. Compatibility Requirements

**Maintain existing functionality:**
- Don't break existing pages
- Preserve current data flow
- Keep existing styling patterns
- Maintain filter integration

**Cross-reference with Streamlit:**
- Compare data display between React and Streamlit
- Ensure consistent field names
- Match data transformations
- Verify calculation accuracy

### 5. Styling Guidelines

**Use existing patterns:**
- Import from `web/src/styles/`
- Follow Ant Design patterns
- Maintain consistent spacing
- Use existing color schemes

**CSS Organization:**
```typescript
import '../styles/pages/NewFeaturePage.css';
import '../styles/components/card.css';
```

### 6. Testing Requirements

**Before creating new pages:**
1. Verify existing pages work
2. Test data mapping utility
3. Check API responses
4. Compare with Streamlit output

**After creating new pages:**
1. Test with real data
2. Verify data mapping works
3. Check responsive design
4. Validate filter integration

## Specific Instructions for Codex

### When Creating New Pages

1. **Analyze existing pages first:**
   - Review `web/src/pages/` for patterns
   - Understand data flow in existing components
   - Note styling and layout approaches

2. **Check data mapping utility:**
   - Review `web/src/utils/mapApiData.ts`
   - Understand current field mappings
   - Identify any gaps for new features

3. **Reference Streamlit implementation:**
   - Check `audit_tool/dashboard/pages/` for reference
   - Understand data calculations
   - Verify field names and transformations

4. **Create new page:**
   - **For Ant Design versions:** Use `{OriginalPageName}_AntDesign.tsx` naming
   - Follow component structure above
   - Use existing hooks and utilities
   - Apply Ant Design styling patterns
   - Implement proper error handling
   - **NEVER overwrite original files**

5. **Extend mapping utility if needed:**
   - Add new field mappings
   - Maintain backward compatibility
   - Document changes clearly
   - Test with existing pages

### Data Mapping Extensions

**When adding new fields:**
```typescript
// In mapApiData.ts
export const mapApiData = (data: any) => {
  return {
    // Existing mappings...
    title: data.page_title || data.title || 'Untitled',
    url: data.url || '',
    score: data.raw_score || data.score || 0,
    persona: data.persona || data.persona_id || 'Unknown',
    
    // New mappings for your feature
    newField: data.api_field || data.fallback_field || defaultValue,
  };
};
```

### Error Handling

**Always implement:**
```typescript
if (loading) return <div>Loading...</div>;
if (error) return <div>Error: {error.message}</div>;
if (!mappedData) return <div>No data available</div>;
```

### Performance Considerations

**Optimize data processing:**
- Use React.memo for expensive components
- Implement proper dependency arrays in useEffect
- Avoid unnecessary re-renders
- Cache mapped data when appropriate

## Quality Assurance Checklist

Before submitting any new pages:

- [ ] Uses `mapApiData()` utility
- [ ] Follows existing component patterns
- [ ] Implements proper error handling
- [ ] Uses existing hooks and utilities
- [ ] Maintains responsive design
- [ ] Integrates with filter system
- [ ] Matches Streamlit data display
- [ ] Preserves existing functionality
- [ ] Uses consistent styling
- [ ] Includes proper TypeScript types
- [ ] **For Ant Design versions:** Uses `{OriginalPageName}_AntDesign.tsx` naming
- [ ] **For Ant Design versions:** Does NOT overwrite original files
- [ ] **For Ant Design versions:** Uses Ant Design components and styling

## Troubleshooting

**Common Issues:**
1. **Data not displaying:** Check `mapApiData()` mapping
2. **Styling inconsistencies:** Import existing CSS files
3. **API errors:** Verify endpoint and data structure
4. **Performance issues:** Check for unnecessary re-renders

**Debugging Steps:**
1. Console.log raw API data
2. Console.log mapped data
3. Compare with Streamlit output
4. Check browser network tab
5. Verify component props

## Contact

For questions about these instructions, refer to:
- Existing code in `web/src/pages/`
- Data mapping utility in `web/src/utils/mapApiData.ts`
- Streamlit reference in `audit_tool/dashboard/`
- API documentation in `api/src/`

---

**Remember:** Always prioritize maintaining existing functionality while adding new features. The data mapping utility is the foundation for consistent data display across all pages.

## Critical Naming Convention Summary

**For Ant Design versions of existing pages:**
- ✅ **CORRECT:** `ExecutiveDashboard_AntDesign.tsx` (alongside `ExecutiveDashboard.tsx`)
- ✅ **CORRECT:** `AuditReports_AntDesign.tsx` (alongside `AuditReports.tsx`)
- ❌ **WRONG:** Overwriting `ExecutiveDashboard.tsx` with Ant Design code
- ❌ **WRONG:** Using generic names like `NewPage.tsx`

**This ensures:**
- Original React pages remain intact
- Ant Design versions are clearly identifiable
- Both versions can coexist in the same directory
- Easy switching between implementations 