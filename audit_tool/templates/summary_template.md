# Strategic Summary Report

**Persona:** {{ report.persona_name }}
**Generated:** {{ timestamp }}

---

## Executive Summary

{{ report.executive_summary }}

---

## Overall Scores

- **Final Brand Score:** {{ "%.1f"|format(report.overall_score) }}/10
- **Onsite Score:** {{ "%.1f"|format(report.onsite_score) }}/10
- **Offsite Score:** {{ "%.1f"|format(report.offsite_score) }}/10

---

## Key Themes

### Strengths

{% for item in report.key_strengths %}

- {{ item }}
  {% endfor %}

### Weaknesses

{% for item in report.key_weaknesses %}

- {{ item }}
  {% endfor %}
