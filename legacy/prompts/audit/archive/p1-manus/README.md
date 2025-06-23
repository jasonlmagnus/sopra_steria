# P1 Brand Audit Analysis - Replication Guide

## 📋 Overview

This folder contains the complete P1 (BENELUX Public Sector IT Executive) brand audit analysis that achieved a **6.76/10 final brand score**. This README provides step-by-step instructions for replicating this analysis across other personas (P2-P5).

## 📁 File Structure

```
p1-manus/
├── README.md                    # This file - replication instructions
├── p1_brand_audit_results.md    # Complete detailed audit (131KB, 2053 lines)
├── offsite_fixed.md            # Corrected offsite scoring (29KB, 498 lines)
├── p1_audit_results.md         # Summary analysis (9.8KB, 304 lines)
├── p1_summary.md               # Executive dashboard (3.5KB, 111 lines)
└── p1_audit_data.csv           # Dashboard data (3.8KB, 21 rows)
```

## 🎯 Key Results Summary

- **Final Brand Score**: 6.76/10
- **Critical Crisis**: Trustpilot unclaimed profile (0.0/10)
- **Strongest Tier**: Functional Content (8.36/10)
- **Weakest Area**: Offsite Brand Presence (3.5/10)
- **Top Priority**: Claim Trustpilot profile immediately

---

## 🔄 REPLICATION PROCESS FOR P2-P5

### Step 1: Prepare Persona Materials

For each new persona (P2, P3, P4, P5):

1. **Create persona folder**: `prompts/audit/p[X]-manus/`
2. **Required files**:
   - `p[X]_urls.md` - 20 URLs for audit (same as P1 or persona-specific)
   - Persona brief from `personas/v2/P[X].md`

### Step 2: Run Manus.ai Audit

#### A. Use the Refined Prompt

Copy the exact prompt from `../audit_brief_manus.md`:

```
SYSTEM
You are Sopra Steria's Brand-Audit engine.

Follow EVERY rule, weight and scoring instruction found in the attached file:
    └── audit_method.md   (definitive methodology)

• Never invent or alter criteria, names or weights.
• Every criterion must be scored 0-10 with evidence quotes.
• All weighting columns must sum to 100 %.
• Apply validation errors and penalty flags exactly as written in the method.

USER
Context attachments for this audit run
1. Persona brief  : {{ATTACH: P[X].md}}
2. URL inventory  : {{ATTACH: p[X]_urls.md}}

[Rest of prompt as written in audit_brief_manus.md]
```

#### B. Attach Required Files

1. `../audit_method.md` (methodology - same for all)
2. `personas/v2/P[X].md` (specific persona)
3. `p[X]_urls.md` (URL list)

#### C. Execute Audit

- Send prompt to Manus.ai
- Save complete output as `p[X]_brand_audit_results.md`
- **Validate offsite scoring** against methodology

### Step 3: Validate and Correct Offsite Scoring

#### A. Check Offsite Compliance

Verify the audit follows exact methodology:

- **Owned Channels** (60% Brand | 40% Performance): LinkedIn, YouTube, Twitter/X
- **Influenced Channels** (40% Brand | 60% Authenticity): Glassdoor
- **Independent Channels** (20% Brand | 80% Sentiment): Trustpilot

#### B. Correct if Needed

If offsite scoring is incorrect:

1. Use refined prompt focusing on offsite channels only
2. Save corrected output as `offsite_fixed.md`
3. Apply corrections to main audit file

#### C. Calculate Final Composite Score

```
Final Score = (On-site × 0.7 + Off-site × 0.3) × Crisis Multiplier
```

### Step 4: Create Analysis Files

#### A. Summary Analysis (`p[X]_audit_results.md`)

Based on P1 template, update:

- Persona focus and priorities
- Tier averages and ranges
- Top/bottom performing assets
- Critical findings specific to persona
- ROI projections and recommendations

#### B. Executive Summary (`p[X]_summary.md`)

Create dashboard-ready summary with:

- Final brand score prominently displayed
- Crisis alerts and urgent actions
- Top opportunities with ROI potential
- Immediate action checklist
- Dashboard integration recommendations

#### C. Data File (`p[X]_audit_data.csv`)

Export data in standardized format:

```csv
URL,Asset_Name,Tier,Category,Score,Brand_Score,Performance_Score,Key_Issues,Priority_Actions,Strategic_Impact
```

---

## 🎯 QUALITY ASSURANCE CHECKLIST

### ✅ Mathematical Validation

- [ ] All tier averages calculated correctly
- [ ] Offsite composite follows 40/35/25% weighting
- [ ] Final brand score matches detailed calculation
- [ ] Individual asset scores validated against source data

### ✅ Methodology Compliance

- [ ] Tier classification correct (1: Brand, 2: Value Prop, 3: Functional)
- [ ] Brand/Performance ratios applied (80/20, 50/50, 30/70)
- [ ] Offsite channel types properly categorized
- [ ] Crisis penalties applied where appropriate

### ✅ Persona Relevance

- [ ] C-suite priorities addressed for specific persona
- [ ] Regional narratives appropriate (BENELUX vs UK vs Global)
- [ ] Industry-specific issues identified
- [ ] Strategic recommendations aligned with persona needs

### ✅ Data Structure

- [ ] CSV format matches P1 template
- [ ] All 20 assets included with complete data
- [ ] Priority actions linked to strategic impact
- [ ] Dashboard-ready formatting applied

---

## 🚨 CRITICAL SUCCESS FACTORS

### 1. **Offsite Scoring Accuracy**

- This was the major issue in P1 initial analysis
- **Must validate** against methodology before proceeding
- Use corrected offsite approach from `offsite_fixed.md`

### 2. **Crisis Detection**

- **Any asset scoring <3.0** requires immediate escalation
- Unclaimed profiles = automatic crisis status
- Poor ratings (<2.5/5) = urgent intervention needed

### 3. **Persona-Specific Insights**

- Don't just copy P1 findings
- Focus on **persona priorities** from brief
- Adjust regional narratives appropriately
- Consider industry-specific compliance needs

### 4. **Mathematical Precision**

- Use **exact calculations** not rounded estimates
- Validate all composite scores
- Ensure tier averages match individual scores
- Double-check final brand score calculation

---

## 📊 EXPECTED OUTCOMES BY PERSONA

### P2: BENELUX Financial Services Leader

- **Focus**: Regulatory compliance, digital transformation ROI
- **Expected Issues**: Financial services sub-narrative gaps
- **Key Metrics**: Risk management content, compliance signals

### P3: Chief Data Officer

- **Focus**: Data governance, AI ethics, technical depth
- **Expected Issues**: Technical content sophistication
- **Key Metrics**: Data strategy content, innovation positioning

### P4: Operations Transformation Executive

- **Focus**: Operational efficiency, change management
- **Expected Issues**: Transformation methodology gaps
- **Key Metrics**: Process improvement content, ROI demonstration

### P5: Cross-Sector IT Director

- **Focus**: Technology leadership, vendor evaluation
- **Expected Issues**: Technical credibility, industry breadth
- **Key Metrics**: Technical depth, multi-industry expertise

---

## 🔧 TROUBLESHOOTING

### Common Issues and Solutions

#### Issue: Manus.ai doesn't follow methodology exactly

**Solution**:

- Emphasize "Follow EVERY rule" in prompt
- Attach methodology file first
- Validate output against scoring weights

#### Issue: Offsite scoring incorrect

**Solution**:

- Use P1's corrected approach from `offsite_fixed.md`
- Focus on channel type classification
- Apply exact weighting ratios

#### Issue: Persona relevance unclear

**Solution**:

- Re-read persona brief carefully
- Focus on C-suite priorities listed
- Adjust regional/industry context appropriately

#### Issue: Mathematical errors in calculations

**Solution**:

- Use P1 validation approach
- Check all composite score formulas
- Validate tier averages against individual scores

---

## 📈 DASHBOARD INTEGRATION

### Multi-Persona Dashboard Structure

```
Dashboard/
├── persona_comparison.csv      # All P1-P5 data combined
├── crisis_alerts.json         # Real-time crisis monitoring
├── improvement_tracking.csv    # Before/after ROI measurement
└── executive_summary.md        # Cross-persona insights
```

### Key Metrics to Track Across Personas

1. **Brand Score Distribution** (P1-P5 comparison)
2. **Crisis Asset Count** (scores <3.0 by persona)
3. **Improvement Opportunity** (ROI potential ranking)
4. **Action Item Progress** (implementation tracking)

---

## 🎯 SUCCESS METRICS

### Analysis Quality Indicators

- **Mathematical Accuracy**: All calculations validated
- **Methodology Compliance**: 100% adherence to scoring rules
- **Persona Relevance**: Insights specific to target audience
- **Actionability**: Clear ROI-linked recommendations

### Business Impact Measures

- **Crisis Prevention**: Early detection of reputation risks
- **Improvement ROI**: Quantified score improvement potential
- **Strategic Alignment**: Recommendations linked to persona priorities
- **Implementation Ready**: Clear action plans with timelines

---

## 📞 SUPPORT

For questions or issues during replication:

1. **Reference**: P1 detailed audit for methodology examples
2. **Validate**: Against audit_method.md for scoring rules
3. **Compare**: With P1 results for quality benchmarking
4. **Escalate**: Any crisis-level findings (scores <3.0) immediately

---

_Last Updated: 2024 | Template Version: P1-Validated | Next: Apply to P2-P5_
