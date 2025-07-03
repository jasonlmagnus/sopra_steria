# Brand Audit Results - All Personas Combined - July 2025

**Generated:** 2025-07-03 08:03:52  
**Total Documents:** 87

## Executive Summary

This document contains comprehensive brand audit results across all personas, analyzing how different user types experience Sopra Steria's digital presence.


## The_BENELUX_Technology_Innovation_Leader

**Documents Analyzed:** 15

### Score Overview
- **Average Score:** 🟡 **7.1866666666666665/10** (Good)

### Top Performing Pages
- 🟡 **7.8/10** (Good) - https://www.soprasteria.be/whatwedo/digital-themes/deliver-flexible-always-on-performance/cloud-infrastructure-platforms/sopra-steria-transformation-services-for-microsoft-azure
- 🟡 **7.8/10** (Good) - https://www.soprasteria.nl/newsroom/blog/details/interacting-with-large-language-models
- 🟡 **7.8/10** (Good) - https://www.soprasteria.nl/newsroom/press-releases/details/sopra-steria-next-predicts

### Needs Improvement
- 🟡 **6.6/10** (Good) - https://www.soprasteria.be/whatwedo/management-digital-transformation-consulting/services-operations-automation
- 🟡 **6.4/10** (Good) - https://www.soprasteria.com/about-us/history
- 🟠 **5.2/10** (Needs Improvement) - https://www.soprasteria.nl/newsroom/press-releases/details/welcome-to-the-future-of-innovation

---

## The Technical Influencer

**Documents Analyzed:** 18

### Score Overview
- **Average Score:** 🟡 **6.266666666666667/10** (Good)

### Top Performing Pages
- 🟡 **7.6/10** (Good) - https://www.soprasteria.be/whatwedo/digital-themes/deliver-flexible-always-on-performance/cloud-infrastructure-platforms/sopra-steria-transformation-services-for-microsoft-azure
- 🟡 **7.4/10** (Good) - https://www.soprasteria.be/
- 🟡 **7.4/10** (Good) - https://www.soprasteria.nl/

### Needs Improvement
- 🟠 **5.8/10** (Needs Improvement) - https://www.soprasteria.nl/newsroom/press-releases/details/welcome-to-the-future-of-innovation
- 🔴 **1.4/10** (Poor) - https://www.youtube.com/@SopraSteria_Benelux
- 🔴 **0.0/10** (Poor) - https://www.linkedin.com/company/soprasteria-benelux/

---

## The Benelux Strategic Business Leader (C-Suite Executive)

**Documents Analyzed:** 18

### Score Overview
- **Average Score:** 🟡 **6.4222222222222225/10** (Good)

### Top Performing Pages
- 🟡 **7.4/10** (Good) - https://www.soprasteria.be/whatwedo/data-ai/data-science-and-ai/the-future-of-generative-ai
- 🟡 **7.4/10** (Good) - https://www.soprasteria.nl/newsroom/blog/details/ecosystems-yes-please-but-how-can-we-trust-each-other
- 🟡 **7.4/10** (Good) - https://www.soprasteria.be/

### Needs Improvement
- 🟠 **5.6/10** (Needs Improvement) - https://www.nldigital.nl/leden/sopra-steria-nederland-b-v/
- 🔴 **3.6/10** (Poor) - https://www.youtube.com/@SopraSteria_Benelux
- 🔴 **1.0/10** (Poor) - https://www.linkedin.com/company/soprasteria-benelux/

---

## The Benelux Cybersecurity Decision Maker

**Documents Analyzed:** 18

### Score Overview
- **Average Score:** 🟠 **5.894444444444444/10** (Needs Improvement)

### Top Performing Pages
- 🟡 **7.4/10** (Good) - https://www.soprasteria.nl/
- 🟡 **7.4/10** (Good) - https://www.soprasteria.be/industries/financial-services
- 🟡 **7.2/10** (Good) - https://www.soprasteria.be/

### Needs Improvement
- 🟠 **5.5/10** (Needs Improvement) - https://www.nldigital.nl/leden/sopra-steria-nederland-b-v/
- 🔴 **2.6/10** (Poor) - https://www.youtube.com/@SopraSteria_Benelux
- 🔴 **0.0/10** (Poor) - https://www.linkedin.com/company/soprasteria-benelux/

---

## The Benelux Transformation Programme Leader

**Documents Analyzed:** 18

### Score Overview
- **Average Score:** 🟡 **6.272222222222222/10** (Good)

### Top Performing Pages
- 🟡 **7.4/10** (Good) - https://www.soprasteria.be/whatwedo/digital-themes/deliver-flexible-always-on-performance/cloud-infrastructure-platforms/sopra-steria-transformation-services-for-microsoft-azure
- 🟡 **7.4/10** (Good) - https://www.soprasteria.nl/
- 🟡 **7.2/10** (Good) - https://www.soprasteria.be/whatwedo/data-ai/data-science-and-ai/the-future-of-generative-ai

### Needs Improvement
- 🟠 **5.5/10** (Needs Improvement) - https://www.nldigital.nl/leden/sopra-steria-nederland-b-v/
- 🔴 **3.6/10** (Poor) - https://www.youtube.com/@SopraSteria_Benelux
- 🔴 **0.0/10** (Poor) - https://www.linkedin.com/company/soprasteria-benelux/

---

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
