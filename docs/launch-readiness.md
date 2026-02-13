# Launch Readiness Report — AHA Store ICU

**Project:** AHA Store Internal Check Up (Store ICU)
**Date:** ____________________
**Prepared by:** ____________________
**Version:** 1.0

---

## 1. Executive Summary

| Item | Status |
|------|--------|
| **Validation Status** | Not Started / In Progress / Complete |
| **Brands Validated** | 0 of target 1-2 |
| **Critical Discrepancies** | 0 |
| **Go/No-Go Recommendation** | Pending |

_Brief narrative summary of validation findings and overall system readiness._

---

## 2. Validation Summary

### Brands Evaluated

| # | Brand Name | Category | Date Validated | Validation Report | Result |
|---|-----------|----------|----------------|-------------------|--------|
| 1 | | Fashion / Non-Fashion | | [Link to report](validation-report-{brand}.md) | PASS / FAIL |
| 2 | | Fashion / Non-Fashion | | [Link to report](validation-report-{brand}.md) | PASS / FAIL |

### Calculator Accuracy Summary

| Calculator | Brand 1 | Brand 2 | Notes |
|-----------|---------|---------|-------|
| Ads Keyword | PASS / FAIL | PASS / FAIL | |
| Discount Check | PASS / FAIL | PASS / FAIL | Within ±0.5% tolerance? |
| Top SKU | PASS / FAIL | PASS / FAIL | Within ±2 stock tolerance? |
| Final Scoring | PASS / FAIL | PASS / FAIL | Within ±1 point tolerance? |
| Verdict Agreement | PASS / FAIL | PASS / FAIL | Exact match? |

### End-to-End Workflow

| Step | Status | Notes |
|------|--------|-------|
| Login with Firebase Auth | ☐ | All 5 accounts verified |
| Brand sync from Google Sheet | ☐ | |
| File upload (4 types) | ☐ | |
| Manual data entry | ☐ | |
| Calculator auto-execution | ☐ | |
| Final scoring + verdict | ☐ | |
| Evaluation save | ☐ | |
| History search + filter | ☐ | |
| SSE real-time notifications | ☐ | |

---

## 3. Discrepancy Log

_Consolidated list of all discrepancies found across all validated brands._

| # | Brand | Calculator | Field | Expected | Actual | Delta | Severity | Root Cause | GitHub Issue | Status |
|---|-------|-----------|-------|----------|--------|-------|----------|------------|-------------|--------|
| 1 | | | | | | | Critical / Minor / Cosmetic | | | Open / Fixed / Won't Fix |
| 2 | | | | | | | | | | |
| 3 | | | | | | | | | | |

### Severity Definitions

| Severity | Definition | Launch Impact |
|----------|-----------|---------------|
| **Critical** | Output is materially wrong; affects scoring/verdict | **Blocks launch** — must fix and re-validate |
| **Minor** | Output differs slightly beyond tolerance; does not affect verdict | **Does not block launch** — acceptable variance |
| **Cosmetic** | Display/formatting only; no data impact | **Does not block launch** — fix when convenient |

---

## 4. Go/No-Go Criteria

All criteria must be met for a **GO** recommendation.

| # | Criterion | Met? | Evidence |
|---|-----------|------|----------|
| 1 | **Zero critical discrepancies** — No calculator output or scoring error that materially affects the verdict | ☐ | Discrepancy log shows 0 critical |
| 2 | **Calculator outputs within tolerance** — Discount ±0.5%, stock ±2, score ±1 | ☐ | Validation reports confirm |
| 3 | **All 5 user accounts can log in** — Admin, leader, and 3 members verified | ☐ | Login verification checklist |
| 4 | **Full workflow completes E2E** — At least 1 brand evaluated end-to-end without errors | ☐ | Validation report PASS |
| 5 | **No data loss on save** — Saved evaluation retrievable from history with all data intact | ☐ | History verification |

### User Account Verification

| # | Role | Email | Can Log In? | Correct Role? | Notes |
|---|------|-------|------------|---------------|-------|
| 1 | admin | | ☐ | ☐ | |
| 2 | leader | | ☐ | ☐ | |
| 3 | member | | ☐ | ☐ | |
| 4 | member | | ☐ | ☐ | |
| 5 | member | | ☐ | ☐ | |

---

## 5. Recommendation

### Decision

| Recommendation | Rationale |
|----------------|-----------|
| **GO** / **NO-GO** / **CONDITIONAL GO** | _Explain the recommendation based on criteria above_ |

### Conditions (if Conditional GO)

| # | Condition | Owner | Deadline | Status |
|---|-----------|-------|----------|--------|
| 1 | | | | |
| 2 | | | | |

---

## 6. Bug/Fix Fast-Track Process

If critical bugs are discovered during validation:

1. **Document** — Log in the Discrepancy Log above with full details
2. **Create GitHub Issue** — Label: `bug/critical`, include:
   - Reproduction steps
   - Expected vs actual output
   - Affected calculator/scoring category
   - Brand and data used for testing
3. **Fix** — Create feature branch from `develop`, implement fix
4. **Deploy** — Push to trigger CI/CD pipeline (auto-deploy to production)
5. **Re-validate** — Run the validation report again for the affected brand
6. **Update** — Mark the discrepancy as "Fixed" in this document

```
Timeline target: Bug report → Fix → Re-validate within 24 hours
```

---

## 7. Rollout Plan

### Option A: Phased Rollout (Recommended)

| Phase | Users | Duration | Success Criteria |
|-------|-------|----------|-----------------|
| 1. Pilot | 1 BD member + team leader | 1 week | 3+ brands evaluated without issues |
| 2. Expand | All 3 BD members | 1 week | Full team productive, no critical bugs |
| 3. Full operation | All 5 users | Ongoing | Routine evaluations, process stable |

### Option B: Big-Bang Rollout

| Step | Action |
|------|--------|
| 1 | Complete all validation with PASS result |
| 2 | Distribute credentials to all 5 users simultaneously |
| 3 | Conduct group onboarding session (walk through onboarding guide) |
| 4 | All users start evaluating immediately |

### Chosen Approach

☐ Phased Rollout
☐ Big-Bang Rollout

**Rationale:** ____________________

---

## 8. Sign-Off

| Role | Name | Signature / Approval | Date |
|------|------|---------------------|------|
| BD Team Leader | | ☐ Approved | |
| System Owner | | ☐ Approved | |
| Project Manager | | ☐ Approved | |

---

### Document History

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 1.0 | | | Initial template created |
| | | | |
