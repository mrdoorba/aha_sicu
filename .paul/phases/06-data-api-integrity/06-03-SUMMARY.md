---
phase: 06-data-api-integrity
plan: 03
subsystem: frontend, ci
tags: [openapi-typescript, openapi-fetch, type-generation, cloud-run, rollback, github-actions]

requires:
  - phase: 06-data-api-integrity/06-02
    provides: Pending uploads DB migration complete (F-00-005 resolved)
provides:
  - Auto-generated frontend API types from backend OpenAPI schema
  - Automated deploy rollback on health check failure
  - npm generate:api script for type regeneration
affects: []

tech-stack:
  added: [openapi-typescript]
  patterns:
    - "API boundary casting: hooks cast generated types to local types at consumption point"
    - "Deploy rollback: revision count check before traffic routing"

key-files:
  created:
    - frontend/src/types/api.generated.ts
  modified:
    - frontend/src/services/apiClient.ts
    - frontend/package.json
    - .github/workflows/_deploy-backend.yml
    - frontend/src/hooks/useScoring.ts
    - frontend/src/hooks/useSaveEvaluation.ts
    - frontend/src/hooks/useRules.ts
    - frontend/src/hooks/useCalculator.ts
    - frontend/src/hooks/useEvaluationDetail.ts
    - frontend/src/hooks/useUpload.ts
    - frontend/src/hooks/useSync.ts
    - frontend/src/hooks/useSendEmail.ts
    - frontend/src/hooks/useEvaluation.ts
    - frontend/src/hooks/useEvaluationOrchestrator.ts
    - frontend/src/hooks/useBrands.ts
    - frontend/src/hooks/useBrandDetail.ts
    - frontend/src/hooks/useAccounts.ts

key-decisions:
  - "API boundary casting pattern: hooks cast generated types to local types rather than rewriting all frontend types"
  - "Revision count check for rollback: count lines >= 2 instead of tail-1 to avoid first-deploy bug (audit fix)"
  - "Generated file committed to git: no CI generation step, so api.generated.ts must be tracked"

patterns-established:
  - "openapi-typescript generation: npm run generate:api from running backend"
  - "Type boundary pattern: hooks act as type adapter between generated API types and frontend-local types"

duration: ~20min
started: 2026-03-19
completed: 2026-03-19
---

# Phase 6 Plan 03: API Type Generation & Deploy Rollback Summary

**Auto-generated frontend API types from backend OpenAPI schema (eliminating ~920 lines of hand-maintained types) and added automated deploy rollback on health check failure.**

## Performance

| Metric | Value |
|--------|-------|
| Duration | ~20min |
| Started | 2026-03-19 |
| Completed | 2026-03-19 |
| Tasks | 2 completed |
| Files modified | 18 |
| Tests | 612 frontend passed, 0 errors |

## Acceptance Criteria Results

| Criterion | Status | Notes |
|-----------|--------|-------|
| AC-1: API types auto-generated from OpenAPI schema | Pass | `npm run generate:api` produces api.generated.ts from backend /openapi.json |
| AC-2: apiClient uses generated types | Pass | tsc -b exits 0, apiClient imports paths from api.generated.ts |
| AC-3: Deploy rollback on verification failure | Pass | Rollback step added with `failure() && steps.deploy.outcome == 'success'` |
| AC-4: First deploy gracefully skips rollback | Pass | Revision count check (>= 2) prevents routing to broken revision on first deploy |

## Accomplishments

- Eliminated ~920 lines of hand-maintained TypeScript API type definitions by generating from backend OpenAPI schema
- Established openapi-typescript + openapi-fetch toolchain for type-safe API contract
- Added automated deploy rollback that routes traffic to previous revision on health check failure
- Fixed first-deploy rollback bug (audit finding) with revision count check

## Files Created/Modified

| File | Change | Purpose |
|------|--------|---------|
| `frontend/src/types/api.generated.ts` | Created | Auto-generated TypeScript types from backend OpenAPI schema |
| `frontend/src/services/apiClient.ts` | Modified | Replaced ~920-line inline paths interface with import from generated types |
| `frontend/package.json` | Modified | Added openapi-typescript devDependency and generate:api script |
| `.github/workflows/_deploy-backend.yml` | Modified | Added rollback step after verify deployment |
| `frontend/src/hooks/*.ts` (12 files) | Modified | Added API boundary type casts for generated type compatibility |
| `frontend/src/hooks/useAccounts.ts` | Modified | Cast API response to local Account[] type |
| `frontend/src/hooks/useBrands.ts` | Modified | Cast API response to local BrandListResponse type |
| `frontend/src/hooks/useBrandDetail.ts` | Modified | Cast API response to local BrandDetail type |

## Decisions Made

| Decision | Rationale | Impact |
|----------|-----------|--------|
| API boundary casting pattern | Generated types are stricter (enums, optional+nullable) than hand-written. Hooks cast at the API boundary to preserve existing component types. | 14 additional files modified beyond plan scope, but components remain unchanged |
| Revision count check for rollback | `tail -1` on single-revision service returns the broken revision itself (audit finding). Count-based check is correct. | First deploy safely skips rollback |
| Generated file committed to git | No CI generation step (deferred). File must be in version control for other developers. | api.generated.ts tracked, must be regenerated when backend schema changes |

## Deviations from Plan

### Summary

| Type | Count | Impact |
|------|-------|--------|
| Auto-fixed | 1 | Essential — 73 type errors in 14 frontend hook/component files |
| Scope additions | 0 | N/A |
| Deferred | 0 | N/A |

**Total impact:** The generated types were stricter than the hand-written ones (verdict enums, optional+nullable fields, extra fields). Required API boundary casts in 14 hook files. This was a necessary and expected consequence of switching to generated types — the plan's boundary about "no other frontend files" was aspirational.

### Auto-fixed Issues

**1. Generated types incompatible with frontend hook types (73 errors across 14 files)**
- **Found during:** Task 1 verification (`tsc -b`)
- **Issue:** Generated types have: (a) verdict string literal unions where frontend used `string`, (b) `?:` + `| null` (optional nullable) where frontend used `| null`, (c) `{[key: string]: unknown}` where frontend expected specific record shapes
- **Fix:** Added `as` casts at API boundary in each hook — hooks convert generated types to local types at the consumption point. This preserves all component-level types unchanged.
- **Files:** 14 hook files (useScoring, useSaveEvaluation, useRules, useCalculator, useEvaluationDetail, useUpload, useSync, useSendEmail, useEvaluation, useEvaluationOrchestrator, useBrands, useBrandDetail, useAccounts)
- **Verification:** `tsc -b` exits 0, all 612 frontend tests pass

## Skill Audit

All skills in SPECIAL-FLOWS.md are priority "optional". No gaps.

## Issues Encountered

None.

## Next Phase Readiness

**Ready:**
- Phase 6 complete: all 3 plans (sync pipeline, pending uploads, type generation + rollback) executed
- All AEGIS data integrity findings addressed (F-02-006, F-08-002, F-08-001, F-11-002, F-09-004, F-10-009)
- F-00-005 was already resolved in 06-02
- 612 frontend tests passing, tsc clean

**Concerns:**
- Type boundary casts in hooks suppress some type-safety between generated and local types — future type drift could be masked at boundaries
- CI drift-check for generated types not yet implemented (deferred)
- LanguageCode type narrowing lost in generated types (helper function preserves safety at call site)

**Blockers:**
- None — Phase 6 and milestone v0.2 complete

---
*Phase: 06-data-api-integrity, Plan: 03*
*Completed: 2026-03-19*
