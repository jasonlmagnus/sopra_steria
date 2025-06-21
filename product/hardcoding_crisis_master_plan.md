# HARDCODING CRISIS: MASTER RECOVERY PLAN

**Date:** 2025-01-27  
**Status:** CRITICAL SYSTEM FAILURE  
**Action Required:** Complete refactor to eliminate hardcoding

---

## THE PROBLEM (BRUTAL TRUTH)

The audit tool is **completely broken** for multi-persona use due to systematic hardcoding violations:

### What's Hardcoded (Evidence)

- **50+ "Benelux" references** throughout codebase
- **30+ "C-suite" references** in generators and AI interface
- **Entire methodology** embedded in Python code instead of YAML
- **Summary generation** assumes P1 persona only
- **AI prompts** contain fixed business context
- **No template system** - uses string concatenation instead of Jinja2

### Files That Are Fucked

- `audit_tool/generators.py:581-596` - Hardcoded P1 executive summary
- `audit_tool/methodology_parser.py` - Entire methodology hardcoded
- `audit_tool/ai_interface.py:25-70` - Persona-specific prompts
- `emergency_summary_fix.py` - Temporary P1-only fix

### Why This Is Catastrophic

- **P2-P5 personas generate inappropriate content** (Benelux C-suite language for everyone)
- **Cannot modify methodology** without code changes
- **Violates every specification** in your product documentation
- **System is fundamentally unusable** for intended purpose

---

## THE SOLUTION (WHAT NEEDS TO HAPPEN)

### Core Architecture Changes Required

1. **TEMPLATE SYSTEM** - Replace hardcoded strings with Jinja2 templates
2. **PERSONA PARSER** - Extract attributes dynamically from persona files
3. **YAML CONFIGURATION** - Move methodology from code to config files
4. **DYNAMIC AI PROMPTS** - Generate prompts based on persona attributes
5. **SEPARATION OF CONCERNS** - Business logic separate from presentation

### New Directory Structure

```
audit_tool/
├── config/
│   ├── methodology.yaml          # All scoring rules (replaces hardcoded)
│   └── persona_templates.yaml    # Persona-specific variables
├── templates/
│   └── strategic_summary.j2      # Jinja2 template (replaces hardcoded strings)
├── persona_parser.py             # Extract persona attributes dynamically
└── [existing files - refactored]
```

---

## THE IMPLEMENTATION (15-HOUR PLAN)

### PHASE 1: FOUNDATION (Hours 1-4)

#### Task 1.1: Create Template Infrastructure

```bash
mkdir -p audit_tool/config audit_tool/templates
pip install PyYAML Jinja2
```

#### Task 1.2: Build PersonaParser

**Create:** `audit_tool/persona_parser.py`

```python
@dataclass
class PersonaAttributes:
    name: str
    role: str
    industry: str
    geographic_scope: str
    key_priorities: List[str]
    business_context: str
    communication_style: str

class PersonaParser:
    def extract_attributes(self, persona_file: str) -> PersonaAttributes:
        # Parse persona .md file and extract structured attributes
        # Return PersonaAttributes object for template use
```

#### Task 1.3: Create Strategic Summary Template

**Create:** `audit_tool/templates/strategic_summary.j2`

```jinja2
# Strategic Summary Report

**Persona:** {{persona.name}}
**Analysis Date:** {{analysis_date}}

## Executive Summary - From the {{persona.role}} Perspective

As {{persona.business_context}}, I find {{overall_assessment}}. With an overall brand score of {{overall_score}}/10, {{performance_summary}}.

The audit reveals {{critical_count}} pages scoring 3/10 or below, indicating {{primary_concerns}}.
```

### PHASE 2: YAML CONFIGURATION (Hours 5-8)

#### Task 2.1: Create Methodology YAML

**Create:** `audit_tool/config/methodology.yaml`

```yaml
methodology:
  onsite_tiers:
    tier1:
      name: "TIER 1 - BRAND POSITIONING"
      weight: 0.3
      criteria:
        - name: "Corporate Positioning Alignment"
          weight: 0.25
        - name: "Brand Differentiation"
          weight: 0.20
```

#### Task 2.2: Refactor MethodologyParser

**Replace:** `audit_tool/methodology_parser.py`

```python
class MethodologyParser:
    def parse(self) -> Methodology:
        with open('audit_tool/config/methodology.yaml', 'r') as f:
            config = yaml.safe_load(f)
        # Build Methodology object from YAML instead of hardcoded data
```

### PHASE 3: REFACTOR GENERATORS (Hours 9-12)

#### Task 3.1: Fix Summary Generation

**Replace:** `audit_tool/generators.py:_create_enhanced_executive_summary`

```python
def _create_enhanced_executive_summary(self, data, persona_attrs: PersonaAttributes) -> str:
    from jinja2 import Environment, FileSystemLoader

    template_vars = {
        'persona': persona_attrs,
        'overall_score': self._calculate_overall_score(data),
        'critical_count': len([p for p in data if p['final_score'] <= 3]),
        'overall_assessment': self._generate_assessment(persona_attrs),
        'primary_concerns': self._generate_concerns(persona_attrs)
    }

    env = Environment(loader=FileSystemLoader('audit_tool/templates'))
    template = env.get_template('strategic_summary.j2')
    return template.render(**template_vars)
```

#### Task 3.2: Make AI Interface Persona-Agnostic

**Replace:** `audit_tool/ai_interface.py:generate_narrative`

```python
def generate_narrative(self, persona_attrs: PersonaAttributes, page_text: str) -> str:
    prompt = f"""
You are an expert at emulating personas. Adopt this persona:

Role: {persona_attrs.role}
Industry: {persona_attrs.industry}
Key Priorities: {', '.join(persona_attrs.key_priorities)}
Communication Style: {persona_attrs.communication_style}

Analyze this webpage from this persona's perspective:
{page_text[:12000]}
"""
    return self._call_ai_api(prompt)
```

### PHASE 4: INTEGRATION & TESTING (Hours 13-15)

#### Task 4.1: Update Main Application

**Modify:** `audit_tool/main.py`

```python
def main():
    # Parse persona attributes
    persona_parser = PersonaParser()
    persona_attrs = persona_parser.extract_attributes(args.persona)

    # Use YAML methodology
    methodology = MethodologyParser().parse()

    # Pass persona_attrs to generators
    summary_generator = SummaryGenerator(persona_attrs, methodology, ai_interface)
```

#### Task 4.2: Test All Personas

```bash
# Test each persona to ensure no hardcoding remains
python -m audit_tool.main --persona personas/v1/1_IT_exec.md --file audit_inputs/v2/P1.md
python -m audit_tool.main --persona personas/v1/2_Finance.md --file audit_inputs/v2/P2.md
python -m audit_tool.main --persona personas/v1/3_CDO.md --file audit_inputs/v2/P3.md
```

---

## SUCCESS CRITERIA (NON-NEGOTIABLE)

- [ ] **System works with ALL personas (P1-P5)** without code changes
- [ ] **ZERO hardcoded business context** anywhere in codebase
- [ ] **All methodology in YAML** - no Python hardcoding
- [ ] **Template-based reports** using Jinja2
- [ ] **Persona-appropriate language** in all generated content

---

## IMMEDIATE NEXT STEPS

1. **Start Phase 1** - Create template infrastructure
2. **Build PersonaParser** - Extract P1 attributes first
3. **Create basic template** - Replace hardcoded summary
4. **Test with P1** - Ensure it still works
5. **Extend to P2-P5** - Validate multi-persona functionality

**Timeline:** 15 hours of focused work to completely fix this mess.

**Priority:** CRITICAL - Current system is unusable for multi-persona strategy.

---

This is the **SINGLE MASTER PLAN** to fix the hardcoding crisis. Everything you need is in this one document.
