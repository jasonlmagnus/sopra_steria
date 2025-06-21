# Brand Hygiene Scorecard

**URL:** {{ scorecard.url }}  
**Audited:** {{ timestamp }}

---

## Overall Assessment

- **Tier/Channel:** {{ scorecard.tier_name }}
- **Final Score:** {{ "%.1f"|format(scorecard.final_score) }}/10

---

## Detailed Scoring

| Category | Score | Rationale |
| -------- | ----- | --------- |

{% for criterion in scorecard.scored_criteria -%}
| **{{ criterion.name }}** | {{ "%.1f"|format(criterion.score) }}/10 | {{ criterion.notes }} |
{% endfor -%}

---

## Summary Rationale

A summary rationale for the final score will be generated in the final report.
