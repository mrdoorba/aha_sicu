# Enterprise Plan Audit Report

**Plan:** .paul/phases/05-testing-infrastructure/05-01-PLAN.md
**Audited:** 2026-03-19
**Verdict:** Conditionally Acceptable (accepted after applying findings below)

---

## 1. Executive Verdict

**Conditionally acceptable.** The plan addresses the right AEGIS findings and the scope is well-bounded. However, the original plan contained a factual error in Task 2 that would have produced tests asserting behavior that does not exist — the email router has **no role-based access control**, yet the plan specified 403 tests for `member` role. This would have either (a) produced tests that pass for the wrong reason, or (b) forced implementers to question the plan mid-execution.

After applying the must-have corrections below, I would approve this plan for production.

## 2. What Is Solid

- **Coverage threshold strategy (fail_under=40, ratchet up).** Starting low and ratcheting is the correct enterprise approach. Prevents coverage regression without blocking the team on an unreachable target.
- **Async marker cleanup methodology.** Counting tests before/after is the correct safety net. The plan correctly identifies `asyncio_mode = "auto"` as the replacement mechanism.
- **Boundaries section.** Explicitly protecting email router/service source, migrations, and existing unit tests prevents scope creep during a test-infrastructure phase.
- **Service-boundary mocking principle.** The instruction to mock at the service boundary (not internal SMTP state) directly addresses F-06-006 and produces resilient tests.
- **Task sequencing.** Task 1 (fixtures) before Task 2 (tests that use fixtures) is correctly ordered with genuine dependency.

## 3. Enterprise Gaps Identified

### GAP-1: Factually incorrect authorization assumptions (CRITICAL)

The email router (`backend/app/modules/email/router.py`) uses `Depends(get_current_user)` which provides **authentication only**. It does NOT use `require_role()`. The original plan specified:
- `test_send_email_returns_403_when_member_role`
- `test_preview_email_returns_403_when_member_role`

These tests assert 403 for member role, but no such behavior exists. Any authenticated user can send emails and preview them. Writing tests for nonexistent behavior is worse than having no tests — it creates false confidence in a security control that doesn't exist.

### GAP-2: Wrong mock target for email send

The plan specified mocking `app.modules.email.service.send_smtp_email`, but the router calls `send_evaluation_email` (which internally calls `send_smtp_email`). Mocking the wrong function would cause the test to hit real SMTP or fail to intercept the call.

### GAP-3: Missing fail-closed domain validation test

The email schema has a fail-closed pattern: if `EMAIL_ALLOWED_DOMAINS` is empty/unset, sending is denied entirely. This is an AEGIS guardrail. The original plan had no test covering this behavior.

### GAP-4: Missing preview 404 test

The original plan tested preview happy path and member-403 (which doesn't exist), but did not test the case where `get_evaluation_detail` raises 404 for a missing evaluation on the preview endpoint.

### GAP-5: pytest-xdist + pytest-cov interaction

The original CI step used `-n auto` (pytest-xdist parallel execution) combined with `--cov`. pytest-cov with parallel workers requires careful configuration for combining coverage data across workers. Without `--cov-config` and proper combining, coverage numbers will be inaccurate (typically under-reported). The safe approach is to run coverage without parallelism.

### GAP-6: No lint regression check in verification

The verification section checks test passes and coverage but does not verify that the new code passes ruff linting. New test files and conftest changes could introduce lint violations.

## 4. Upgrades Applied to Plan

### Must-Have (Release-Blocking)

| # | Finding | Plan Section Modified | Change Applied |
|---|---------|----------------------|----------------|
| 1 | GAP-1: Email endpoints have no role checks — 403 tests are factually wrong | AC-4, Task 2 action | Replaced member→403 tests with unauthenticated→401 tests. Added audit comment explaining email router uses get_current_user only. |
| 2 | GAP-2: Wrong mock target (send_smtp_email vs send_evaluation_email) | Task 2 action | Changed mock target to `send_evaluation_email` which is what the router actually calls. Added explicit avoid note for `send_smtp_email`. |

### Strongly Recommended

| # | Finding | Plan Section Modified | Change Applied |
|---|---------|----------------------|----------------|
| 1 | GAP-3: Missing fail-closed domain validation test | Task 2 action | Added `test_send_email_returns_422_when_domains_not_configured` to test empty EMAIL_ALLOWED_DOMAINS behavior. |
| 2 | GAP-4: Missing preview 404 test | Task 2 action | Added `test_preview_email_returns_404_when_evaluation_not_found` test. |
| 3 | GAP-5: pytest-xdist + pytest-cov conflict | Task 1 action (CI step) | Removed `-n auto` from coverage CI step. Added audit comment explaining why. |
| 4 | GAP-6: No lint check in verification | Verification section | Added `uv run ruff check .` to verification checklist. |

### Deferred (Can Safely Defer)

| # | Finding | Rationale for Deferral |
|---|---------|----------------------|
| 1 | Email endpoints lack role-based access control (`require_role`) | This is a product/security decision, not a testing infrastructure gap. If email should be restricted to certain roles, that's a code change belonging in a security phase, not a test phase. The tests now correctly reflect the actual behavior. |
| 2 | No `record_audit_event()` in email router for send actions | AEGIS guardrail requires audit trail for admin mutations. Email send is arguably a mutation. However, adding audit calls is a code change outside this plan's scope (testing infrastructure only). Noted as deferred issue. |
| 3 | Coverage combining for parallel test execution | Sequential execution with coverage is correct for now. When test suite grows and parallelism becomes necessary, add `--dist loadfile` and coverage combining configuration. |

## 5. Audit & Compliance Readiness

**Evidence production:** The plan will produce coverage reports (term-missing format) that serve as audit evidence for test adequacy. The fail_under threshold creates a measurable, enforceable gate.

**Silent failure prevention:** The before/after test count check in Task 3 prevents silent test drops during marker cleanup. Coverage threshold prevents silent coverage regression.

**Post-incident reconstruction:** CI PostgreSQL service enables database-dependent tests to run, meaning integration tests can validate actual query behavior — improving post-incident root-cause confidence.

**Ownership:** Plan is self-contained with clear verification steps. No ambiguity in what "done" means.

**Weakness noted:** The deferred items (missing role check on email, missing audit trail on email send) represent compliance gaps that exist in the codebase today. This plan correctly tests what exists rather than what should exist, but the gaps should be tracked.

## 6. Final Release Bar

**What must be true before this plan ships:**
- All 8 email endpoint tests pass and test actual endpoint behavior (not phantom 403s)
- Coverage threshold is enforced and the number is real (not inflated by parallel under-counting)
- Zero `@pytest.mark.asyncio` markers remain with unchanged test count
- CI YAML is syntactically valid with working PostgreSQL service

**Risks if shipped as-is (original plan, before fixes):**
- Tests would have asserted 403 for member role on email endpoints — either failing (if tests are correct about expectations) or passing vacuously (if mock setup accidentally returns 403 for other reasons). Both outcomes are bad.
- Coverage numbers from `-n auto --cov` would likely be inaccurate.

**After applying fixes:** I would sign my name to this plan. The corrections ensure tests validate real behavior, not assumed behavior.

---

**Summary:** Applied 2 must-have + 4 strongly-recommended upgrades. Deferred 3 items.
**Plan status:** Updated and ready for APPLY

---
*Audit performed by PAUL Enterprise Audit Workflow*
*Audit template version: 1.0*
