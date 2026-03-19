# Enterprise Plan Audit Report

**Plan:** .paul/phases/03-defensive-hardening/03-01-PLAN.md
**Audited:** 2026-03-19
**Verdict:** Conditionally Acceptable (accepted after applying findings)

---

## 1. Executive Verdict

**Conditionally Acceptable.** The plan's scope, task specificity, and boundary awareness are solid. However, three gaps would have caused production breakage or left security controls without regression protection. After applying the must-have and strongly-recommended findings below, the plan meets enterprise standards.

Would I approve this for production if accountable? **Yes, after the applied fixes.** The original plan would have deployed a fail-closed email validation change into an environment that never sets the required env var — a guaranteed production incident.

## 2. What Is Solid

- **SQL allowlist already-resolved treatment is correct.** The plan correctly identifies F-02-001/F-04-009 as already fixed and includes verification without redundant rework. This shows prior-phase awareness.
- **Dockerfile non-root approach is sound.** The plan correctly sequences chown after uv sync (which needs root for /usr/local writes), avoids COPY --chown on dependency install steps, and uses specific UID/GID.
- **Boundaries are well-defined.** Explicit protection of infrastructure, frontend, core modules, and sync router. Clear scope limits on rate limiting, role restriction, and structured logging.
- **Fail-closed pattern is correct.** Following the Phase 1 OIDC precedent for email domain validation is the right architectural decision.
- **Task specificity is high.** Files, actions, and verify are all concrete. No vague "implement security" tasks.

## 3. Enterprise Gaps Identified

### Gap 1: EMAIL_ALLOWED_DOMAINS not in deployment config (CRITICAL)

`config.py:68` defines `email_allowed_domains: str = ""` — defaults to empty string. The terraform Cloud Run configuration does NOT set `EMAIL_ALLOWED_DOMAINS` as an environment variable (confirmed: not present in `modules/environment/main.tf` env vars block). The fail-closed change (`if not allowed_raw: raise ValueError(...)`) will reject ALL email requests in ALL environments on deploy.

This is not a theoretical risk — it is a guaranteed production incident.

### Gap 2: Exception handler has no test (HIGH)

The global exception handler is a security control preventing information leakage (stack traces, file paths, library versions). The plan adds it but specifies no test. Security controls without tests have zero regression protection. A future developer removes or modifies the handler, no test fails, stack traces leak.

### Gap 3: Email fail-closed behavior has no test (HIGH)

The fail-closed change to email validation is a security invariant. The plan mentions "update test fixtures if needed" but does not specify a test that verifies the fail-closed behavior itself. The test must prove that empty `EMAIL_ALLOWED_DOMAINS` causes rejection — this is the assertion that prevents someone from reverting to fail-open.

### Gap 4: ScoringRequest frontend impact unverified (MEDIUM)

Making `verdict` required on `ScoringRequest` could break the frontend if it ever omits the field. Analysis confirmed this is safe (`ScoringSection.tsx:44` always sends verdict via `useState('✔️')`), but the plan did not document this verification.

## 4. Upgrades Applied to Plan

### Must-Have (Release-Blocking)

| # | Finding | Plan Section Modified | Change Applied |
|---|---------|----------------------|----------------|
| 1 | EMAIL_ALLOWED_DOMAINS not in terraform — fail-closed change breaks all email in production | Task 2 action, files_modified, boundaries | Added terraform env var configuration steps: variable declarations in modules/environment/variables.tf, root variables.tf, pass-through in main.tf, env var in Cloud Run config. Relaxed boundary to allow this specific terraform change. |

### Strongly Recommended

| # | Finding | Plan Section Modified | Change Applied |
|---|---------|----------------------|----------------|
| 1 | Exception handler has no regression test | Task 2 action, acceptance_criteria (AC-6), verification | Added test specification: trigger unhandled exception via test client, assert 500 status, assert no traceback/file paths in response body. Added AC-6 and verification check. |
| 2 | Email fail-closed has no regression test | Task 2 action, acceptance_criteria (AC-7), verification | Added test specification: validate SendEmailRequest with empty EMAIL_ALLOWED_DOMAINS raises ValueError, validate with configured domain passes. Added AC-7 and verification checks. |
| 3 | Frontend impact of required verdict unverified | Task 3 action | Added note confirming frontend always sends verdict (ScoringSection.tsx useState default '✔️'). |

### Deferred (Can Safely Defer)

| # | Finding | Rationale for Deferral |
|---|---------|----------------------|
| 1 | Correlation ID in exception handler error responses | Phase 4 (Observability & Audit) explicitly covers request correlation IDs. Adding one here without the logging infrastructure creates an orphan ID with no traceability value. |
| 2 | Structured JSON logging in exception handler | Phase 4 scope. Current basic logging is functional for this phase. Structured logging requires a holistic approach across all logging, not a one-off in the exception handler. |
| 3 | Rate limiting on email endpoint (F-05-007, F-DA-018) | Explicitly out of scope per plan boundaries. Requires infrastructure-level decision (middleware vs API gateway vs Cloud Armor). |

## 5. Audit & Compliance Readiness

**Defensible audit evidence:** After applying findings, the plan produces testable evidence — automated tests prove security controls work, Docker build proves non-root execution, terraform config proves env var propagation. Each acceptance criterion has a corresponding verification.

**Silent failure prevention:** The must-have finding (EMAIL_ALLOWED_DOMAINS) directly prevented a silent failure — email would have broken with a validation error but no infrastructure-level alert. The fail-closed pattern is correct, but only when the deployment configuration supports it.

**Post-incident reconstruction:** The exception handler logs full tracebacks server-side with path and method. This is sufficient for Phase 3. Phase 4 will add correlation IDs for full request tracing.

**Ownership and accountability:** Clear — all changes are in backend code and terraform configs with defined acceptance criteria. No ambiguous "verify manually" steps remain after audit upgrades.

## 6. Final Release Bar

**What must be true before this plan ships:**
- EMAIL_ALLOWED_DOMAINS is set in both dev and prod terraform tfvars
- Exception handler test proves no information leakage in 500 responses
- Email fail-closed test proves empty config causes rejection
- All existing tests pass without regression
- Docker container runs as non-root (UID 1001)

**Risks if shipped as-is (pre-audit):**
- Email functionality would break in all environments (fail-closed with no config)
- Exception handler could be removed without any test detecting the regression
- Email fail-closed could be reverted to fail-open without detection

**After audit fixes:** These risks are mitigated. I would sign my name to this plan.

---

**Summary:** Applied 1 must-have + 3 strongly-recommended upgrades. Deferred 3 items.
**Plan status:** Updated and ready for APPLY

---
*Audit performed by PAUL Enterprise Audit Workflow*
*Audit template version: 1.0*
