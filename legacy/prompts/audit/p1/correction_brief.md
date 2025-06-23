## CORRECTIVE ACTION BRIEF - Manus.ai Sopra Steria Audit

**TO:** Manus.ai Audit Engine
**FROM:** Compliance Oversight
**SUBJECT:** Re-evaluation of `p1_manus_results.md` for Strict Compliance

**SITUATION:**
Your previous audit output, `p1_manus_results.md`, was found to be **NON-COMPLIANT**. While the general format and gating rules were applied correctly, the core evaluation criteria used were incorrect and did not match the official methodology.

**YOUR TASK: CORRECTIVE ACTION ONLY**

You are to **RE-EVALUATE** the original 20 URLs, but **you do not need to start from scratch**. Your task is to fix the specific points of non-compliance using the corrected brief and your previous analysis as a baseline.

**MANDATORY CORRECTION PROCESS:**

1.  **REFERENCE YOUR PREVIOUS WORK:** Use the attached `p1_manus_results.md` as your starting point. You already have the URLs, classifications, and initial evidence quotes.

2.  **USE THE CORRECTED BRIEF:** All re-evaluation MUST use the criteria and weightings now explicitly defined in the updated `prompts/audit/audit_brief_manus_STRICT.md`.

3.  **RE-SCORE EACH CRITERION:** For every URL in your previous report, replace the old, incorrect criteria with the new, correct criteria from the updated brief. Re-score each new criterion based on the evidence on the page.

4.  **VALIDATE EVIDENCE QUOTES:**

    - For every score of 7 or higher, you **MUST** ensure the `Evidence Quote` is at least 25 words long.
    - If your original quote is too short, find a compliant one from the page.
    - If no compliant quote exists, you **MUST** apply the `-2 point` penalty as per the brief.

5.  **RECALCULATE ALL SCORES:**
    - Calculate the new weighted score for each Tier based on the correct criteria weights.
    - Pay special attention to the **Offsite Presence** tier, ensuring you use the correct weightings for `Owned`, `Influenced`, and `Independent` channels as specified in the new brief.
    - Calculate the new final, overall brand score.

**INPUTS:**

1.  **Corrected Brief (MASTER):** `prompts/audit/audit_brief_manus_STRICT.md`
2.  **Your Flawed Output (TO BE CORRECTED):** `prompts/audit/p1_new/p1_manus_results.md`
3.  **Methodology (Reference):** `prompts/audit/audit_method.md`
4.  **URL List (Reference):** `prompts/audit/audit_urls.md`

**DELIVERABLE:**

A single, corrected Markdown file named `p1_manus_results_CORRECTED.md`. This file should have the same structure as your original report but with all criteria, scores, and calculations updated to be fully compliant with the corrected brief.

**BEGIN CORRECTIVE AUDIT.**
