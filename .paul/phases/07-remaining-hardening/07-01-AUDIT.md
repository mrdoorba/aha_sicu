# Enterprise Plan Audit Report

**Plan:** .paul/phases/07-remaining-hardening/07-01-PLAN.md
**Audited:** 2026-03-19
**Verdict:** Conditionally acceptable (accepted after fixes applied)

---

## 1. Executive Verdict

**Conditionally acceptable.** The plan is well-scoped and addresses the correct playbooks. However, it had a release-blocking gap: changing response schemas to Literal types without updating existing test fixtures that use non-conforming values would cause test failures during APPLY. After applying the fixes below, the plan is enterprise-ready.

Would I approve this for production if accountable? **Yes, after the applied fixes.**

## 2. What Is Solid

- **Correct scope**: Three well-defined playbooks, no scope creep. The plan correctly avoids touching `manual_data: dict[str, Any]` (separate concern) and `CalculatorResultResponse.calculator_type` (extensible set).
- **WIF branch restriction approach**: Using `attribute_condition` at the provider level is the correct GCP pattern. Provider-level conditions act as the gatekeeper — tokens that don't match can't obtain Google credentials, regardless of IAM bindings.
- **Empty-default authorized_networks**: The fail-closed pattern (`default = []` → zero public IP access) is consistent with the project's established security conventions (OIDC fail-closed, email domain fail-closed).
- **Literal type selection**: The plan correctly identifies which fields should be `Literal` (response schemas with known enumerated values) and which should stay `str` (extensible calculator types, row-level verdict strings). The distinction between `VerdictType` (evaluation-level) and `RowScoreItem.verdict` (metric-level) is correct.
- **Boundaries section**: Properly protects router, service, scoring module, and migration files from unintended changes.
- **Existing Literal types reused**: `CategoryType` and `VerdictType` already exist — the plan extends their use rather than creating new types, which is correct.

## 3. Enterprise Gaps Identified

### Gap 1: Test fixtures use non-Literal values (RELEASE-BLOCKING)
Three test files use `verdict` and `template` values that are not in the Literal type sets:
- `tests/unit/email/conftest.py`: `"verdict": "Good"`, `"template": "standard"`
- `tests/unit/test_generate_score_marketplace.py`: `mock_result.template = "default"`

If the schemas change without updating these, the test suite fails during APPLY. This is not caught by the plan's new test file — it manifests in existing tests.

### Gap 2: Frontmatter missing root main.tf
Task 1 modifies `infrastructure/terraform/main.tf` (to pass `wif_allowed_branch` to modules), but this file was absent from `files_modified` frontmatter. Conflict detection relies on this list being accurate.

### Gap 3: Terraform verification was visual, not machine-verifiable
Tasks 1 and 2 specified "Review the terraform files" as verification — a human activity, not a command. For autonomous execution, `terraform validate` and `terraform fmt -check` are the minimum machine-verifiable checks.

### Gap 4: Task 3 verify only ran new tests
The task-level `<verify>` only ran `tests/unit/test_evaluation_schemas.py`. Schema changes affect serialization across all evaluation endpoints — the full suite must run as part of task verification to catch regressions in existing tests (especially the fixtures identified in Gap 1).

## 4. Upgrades Applied to Plan

### Must-Have (Release-Blocking)

| # | Finding | Plan Section Modified | Change Applied |
|---|---------|----------------------|----------------|
| 1 | Test fixtures use non-Literal values — will break existing tests | Task 3 `<action>`, `<files>` | Added step 4: update `conftest.py` ("Good"→"✔️", "standard"→"fashion") and `test_generate_score_marketplace.py` ("default"→"fashion"). Added both files to `<files>` list and frontmatter `files_modified`. |

### Strongly Recommended

| # | Finding | Plan Section Modified | Change Applied |
|---|---------|----------------------|----------------|
| 1 | Frontmatter missing `main.tf` | `files_modified` frontmatter | Added `infrastructure/terraform/main.tf` |
| 2 | TF verification was visual-only | Task 1 `<verify>`, Task 2 `<verify>` | Changed to `terraform fmt -check -recursive . && terraform validate` |
| 3 | Task 3 verify too narrow | Task 3 `<verify>` | Changed to run new tests AND full suite (`uv run pytest tests/ -x`) |

### Deferred (Can Safely Defer)

| # | Finding | Rationale for Deferral |
|---|---------|----------------------|
| 1 | `principalSet` IAM binding could also include `attribute.ref` for belt-and-suspenders | Provider-level `attribute_condition` is the gatekeeper — tokens that fail the condition cannot obtain Google credentials regardless of IAM bindings. The principalSet restriction would be defense-in-depth, but the provider condition is sufficient. |
| 2 | DB data conformance check for existing records | All data entering the system through the API already goes through `ScoringRequest` and `SaveEvaluationRequest` which enforce `CategoryType`/`VerdictType`. Risk of non-conforming DB data is near-zero unless data was inserted outside the API. |

## 5. Audit & Compliance Readiness

**Audit evidence:** The Terraform changes produce machine-verifiable artifacts (`terraform plan` output). The schema changes produce test results. Both are sufficient for audit evidence.

**Silent failure prevention:** The WIF branch restriction will loudly fail (GitHub Actions gets a 403 from WIF) rather than silently succeed. The Literal types will loudly fail (Pydantic 422) rather than silently accept. The authorized_networks lockdown will loudly fail (connection refused) rather than silently allow.

**Post-incident reconstruction:** Not directly applicable to this plan (infrastructure config + schema validation). The audit trail for admin actions was established in Phase 4.

**Ownership:** Changes are well-contained: 2 Terraform concerns (infra team) + 1 Python concern (backend team). No cross-team coordination required.

## 6. Final Release Bar

**What must be true before shipping:**
- All test fixtures updated to use valid Literal values
- `terraform validate` passes on both infra changes
- Full backend test suite passes with zero regressions
- The 3 AEGIS playbooks are fully addressed

**Risks if shipped as-is (pre-audit):**
- Test suite would fail during APPLY due to non-conforming fixture values (now fixed)
- Frontmatter inaccuracy could cause false negatives in conflict detection (now fixed)

**Sign-off:** With the applied fixes, I would sign my name to this plan. The scope is appropriate, the changes are well-constrained, and the verification is now machine-verifiable.

---

**Summary:** Applied 1 must-have + 3 strongly-recommended upgrades. Deferred 2 items.
**Plan status:** Updated and ready for APPLY

---
*Audit performed by PAUL Enterprise Audit Workflow*
*Audit template version: 1.0*
