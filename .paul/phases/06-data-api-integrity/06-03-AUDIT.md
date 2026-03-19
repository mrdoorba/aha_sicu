# Enterprise Plan Audit Report

**Plan:** .paul/phases/06-data-api-integrity/06-03-PLAN.md
**Audited:** 2026-03-19
**Verdict:** Conditionally acceptable (accepted after fixes applied)

---

## 1. Executive Verdict

**Conditionally acceptable.** The plan addresses its three AEGIS findings (F-11-002, F-09-004, F-10-009) with appropriate scope. One concrete bug in the rollback logic would have caused first-deploy rollback to silently target the broken revision. Two additional gaps around git strategy and task-level test verification were also addressed. After applying 1 must-have and 2 strongly-recommended fixes, the plan is production-safe.

Would I approve this for production? **Yes, after the applied fixes.**

## 2. What Is Solid

- **openapi-fetch + openapi-typescript pairing:** The project already uses `openapi-fetch` for type-safe API calls. Adding `openapi-typescript` for generation completes the toolchain naturally — no new runtime dependency, only a devDependency.
- **Rollback gate condition:** `failure() && steps.deploy.outcome == 'success'` correctly prevents rollback on build/push failures (where no new revision exists to roll back from).
- **Explicit boundary on DB migration rollback:** Acknowledged as a known architectural limitation rather than hidden. Honest about what rollback can and cannot do.
- **Independent tasks:** Two tasks with zero dependency enable parallel thinking and clean failure isolation.
- **Generated types as source of truth:** Eliminates an entire class of defects (type drift) by construction, not by discipline.

## 3. Enterprise Gaps Identified

### Gap 1: First-deploy rollback routes traffic to broken revision (CRITICAL)
The original plan used `--limit=2 | tail -1` to find the previous revision. On a service with only one revision (first deploy), `tail -1` returns the only line — the current broken revision. The `-n "$PREV_REVISION"` check passes (non-empty string), and `update-traffic` routes 100% traffic to the same broken revision. This is a silent no-op that logs misleading "rolled back to previous revision" output.

### Gap 2: Generated file git strategy unspecified
The plan generates `api.generated.ts` but doesn't specify whether it should be committed to git or generated in CI. Without a CI generation step (explicitly deferred in scope limits), the file MUST be committed. Ambiguity here could lead to the file being gitignored or omitted, breaking builds for other developers.

### Gap 3: Task-level verify missing test run
Task 1's `<verify>` section checks `tsc -b` (type correctness) and grep (import structure) but not `npm run test:run` (runtime behavior). The overall `<verification>` section includes the test run, but task-level verification should be self-contained — the executor may check task verify independently.

## 4. Upgrades Applied to Plan

### Must-Have (Release-Blocking)

| # | Finding | Plan Section Modified | Change Applied |
|---|---------|----------------------|----------------|
| 1 | First-deploy rollback targets broken revision | Task 2 `<action>` | Replaced `tail -1` with revision count check: store full list, count lines, only extract previous revision if count >= 2 |

### Strongly Recommended

| # | Finding | Plan Section Modified | Change Applied |
|---|---------|----------------------|----------------|
| 1 | Generated file must be committed to git | Task 1 `<action>` step 6 | Added explicit step: "Commit api.generated.ts to git — do NOT add to .gitignore" |
| 2 | Task-level verify missing test run | Task 1 `<verify>`, Task 2 `<verify>` | Added `npm run test:run` to Task 1 verify; added revision count check verification to Task 2 verify |

### Deferred (Can Safely Defer)

| # | Finding | Rationale for Deferral |
|---|---------|----------------------|
| 1 | LanguageCode type narrowing loss in generated types | Generated types will use `string` for the language request body where hand-written used `LanguageCode`. The `updateLanguage()` helper function preserves the `LanguageCode` constraint at the call site. Backend validates server-side. Safety preserved through existing helper pattern. |
| 2 | CI drift-check for generated types | Already acknowledged in plan scope limits. Requires frontend CI pipeline work — separate concern from type generation setup. |

## 5. Audit & Compliance Readiness

- **Reproducible contract:** Generated types from OpenAPI schema create an auditable, versioned contract between frontend and backend. Any schema change is traceable through git history of the generated file.
- **Rollback evidence:** GitHub Actions workflow logs capture rollback decisions, revision names, and traffic routing changes — sufficient for post-incident reconstruction.
- **No silent failures:** After the first-deploy fix, the rollback step either routes traffic (logging the target revision) or explicitly logs that no previous revision exists. No ambiguous states.
- **Ownership:** Deploy workflow changes are in the shared CI pipeline, owned by the team. Type generation script is documented in package.json.

## 6. Final Release Bar

**Must be true before shipping:**
- Rollback uses revision count check (not `-n` on potentially single-entry output)
- `api.generated.ts` is committed to git and tracked in version control
- All existing frontend tests pass with generated types

**Remaining risks if shipped as-is (after fixes):**
- Types can drift if developer modifies backend schema and forgets `npm run generate:api` (mitigated: tsc will catch most mismatches at build time)
- Rollback does not handle DB migration incompatibility (documented, architectural limitation)
- No automated re-generation in CI (deferred, documented)

**Sign-off:** After applying the 3 fixes above, I would sign my name to this plan.

---

**Summary:** Applied 1 must-have + 2 strongly-recommended upgrades. Deferred 2 items.
**Plan status:** Updated and ready for APPLY

---
*Audit performed by PAUL Enterprise Audit Workflow*
*Audit template version: 1.0*
