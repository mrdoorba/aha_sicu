---
phase: 07-remaining-hardening
plan: 01
subsystem: infra, api
tags: [terraform, wif, cloud-sql, pydantic, literal-types]

requires:
  - phase: 06-data-api-integrity
    provides: stable evaluation schemas, Terraform infrastructure
provides:
  - WIF branch restriction per environment
  - Cloud SQL authorized_networks lockdown
  - Evaluation schema Literal type enforcement
affects: []

tech-stack:
  added: []
  patterns:
    - "WIF attribute_condition with branch restriction"
    - "Dynamic authorized_networks with empty-default fail-closed"
    - "Literal type aliases for response schema enforcement"

key-files:
  created:
    - backend/tests/unit/test_evaluation_schemas.py
  modified:
    - infrastructure/terraform/modules/environment/main.tf
    - infrastructure/terraform/modules/environment/variables.tf
    - infrastructure/terraform/main.tf
    - infrastructure/terraform/cloud_sql.tf
    - infrastructure/terraform/variables.tf
    - backend/app/modules/evaluations/schemas.py

key-decisions:
  - "ScoringResponse.template uses CategoryType — scoring engine returns the request template, not the rule template key"
  - "RowScoreItem.verdict stays str — metric-level verdicts differ from evaluation-level VerdictType"

patterns-established:
  - "Response schemas use same Literal types as request schemas for consistency"

duration: ~15min
started: 2026-03-19T00:00:00Z
completed: 2026-03-19T00:15:00Z
---

# Phase 7 Plan 01: Remaining Hardening Summary

**WIF branch restriction, Cloud SQL authorized_networks lockdown, and evaluation schema Literal type enforcement — closes v0.2 AEGIS Security Remediation milestone.**

## Performance

| Metric | Value |
|--------|-------|
| Duration | ~15min |
| Tasks | 3 completed |
| Files modified | 10 |
| Tests added | 15 |
| Full suite | 1180 passed |

## Acceptance Criteria Results

| Criterion | Status | Notes |
|-----------|--------|-------|
| AC-1: WIF Branch Restriction | Pass | Dev uses `develop`, prod uses `main`. `attribute.ref` mapped, `attribute_condition` checks both repo and branch. `terraform validate` passes. |
| AC-2: Cloud SQL Authorized Networks Lockdown | Pass | Dynamic block with empty-default variable. Zero authorized_networks by default. `terraform validate` passes. |
| AC-3: Evaluation Schema Literal Types | Pass | 13 bare `str` fields replaced with `CategoryType`, `VerdictType`, `CalculatorStatusType`, `RunStatusType`. 15 new tests verify rejection of invalid values. |

## Accomplishments

- WIF providers now restrict authentication to allowed branches per environment (PB-04-008)
- Cloud SQL has zero public IP authorized_networks by default with opt-in override (PB-04-004)
- All evaluation response schemas enforce Literal types matching their request schema counterparts (PB-03-001)

## Files Created/Modified

| File | Change | Purpose |
|------|--------|---------|
| `infrastructure/terraform/modules/environment/main.tf` | Modified | Added `attribute.ref` mapping and branch condition to WIF provider |
| `infrastructure/terraform/modules/environment/variables.tf` | Modified | Added `wif_allowed_branch` variable |
| `infrastructure/terraform/main.tf` | Modified | Pass `wif_allowed_branch` = "develop" (dev) / "main" (prod) |
| `infrastructure/terraform/cloud_sql.tf` | Modified | Added dynamic `authorized_networks` block in ip_configuration |
| `infrastructure/terraform/variables.tf` | Modified | Added `authorized_networks` variable with empty default |
| `backend/app/modules/evaluations/schemas.py` | Modified | Added `CalculatorStatusType`, `RunStatusType`; changed 13 fields to Literal types |
| `backend/tests/unit/test_evaluation_schemas.py` | Created | 15 tests for Literal type validation |
| `backend/tests/unit/email/conftest.py` | Modified | Fixed fixture: "Good"→"✔️", "standard"→"fashion" |
| `backend/tests/unit/test_generate_score_marketplace.py` | Modified | Fixed mock: template "default"→"fashion" |
| `backend/tests/integration/api/test_email_send.py` | Modified | Fixed fixture: verdict "GOOD"→"✔️" |

## Decisions Made

| Decision | Rationale | Impact |
|----------|-----------|--------|
| `ScoringResponse.template` → `CategoryType` | Scoring engine returns the request template ("fashion"/"non_fashion"), not the rule template key ("default"). Verified via service.py line 417. | Test mock needed correction from "default" to "fashion" |
| `RowScoreItem.verdict` stays `str` | Metric-level verdicts ("Above", "Below") differ from evaluation-level VerdictType ("✔️", "❌"). Different domains. | No change to scoring row schemas |

## Deviations from Plan

### Summary

| Type | Count | Impact |
|------|-------|--------|
| Auto-fixed | 1 | Essential — prevented test failure |
| Scope additions | 0 | None |
| Deferred | 0 | None |

**Total impact:** One additional test fixture fix beyond what the audit identified. Same class of issue.

### Auto-fixed Issues

**1. Additional test fixture with non-Literal value**
- **Found during:** Task 3 (full suite regression run)
- **Issue:** `tests/integration/api/test_email_send.py` had `verdict="GOOD"` in `_make_evaluation_detail()`. The audit caught `conftest.py` and `test_generate_score_marketplace.py` but missed this one.
- **Fix:** Changed `verdict="GOOD"` → `verdict="✔️"`
- **Verification:** Full suite 1180/1180 passed

## Issues Encountered

None.

## Next Phase Readiness

**Ready:**
- All 3 remaining AEGIS playbooks (PB-04-008, PB-04-004, PB-03-001) addressed
- Phase 7 is the final phase of v0.2 AEGIS Security Remediation milestone
- Milestone ready for completion

**Concerns:**
- None

**Blockers:**
- None

---
*Phase: 07-remaining-hardening, Plan: 01*
*Completed: 2026-03-19*
