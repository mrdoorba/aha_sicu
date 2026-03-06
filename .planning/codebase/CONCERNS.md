# Codebase Concerns

**Analysis Date:** 2026-03-06

## Tech Debt

**Duplicated utility functions across calculators:**
- Issue: `_safe_num()` is copy-pasted identically in 4 calculator modules, and `_clean_price()` is duplicated in 2 modules. Each copy is 15-20 lines of identical logic.
- Files: `backend/app/calculators/scoring.py:92`, `backend/app/calculators/ads_keyword.py:56`, `backend/app/calculators/discount.py:32`, `backend/app/calculators/top_sku.py:31`; `_clean_price()` in `backend/app/calculators/discount.py:49` and `backend/app/calculators/top_sku.py:48`
- Impact: Bug fixes or behavior changes must be applied in 4 places. Easy to miss one copy, causing inconsistent parsing.
- Fix approach: Extract `_safe_num`, `_safe_str`, and `_clean_price` into a shared module at `backend/app/calculators/utils.py` and import from there.

**Hand-written OpenAPI types in frontend apiClient (821 lines):**
- Issue: The entire `paths` interface in `frontend/src/services/apiClient.ts` (lines 9-787) is manually written rather than auto-generated from the FastAPI OpenAPI schema. The comment on line 7 acknowledges this: "can be replaced with generated OpenAPI types."
- Files: `frontend/src/services/apiClient.ts`
- Impact: API contract drift between backend and frontend. When backend endpoints change, the frontend types must be manually updated. No compile-time or CI-time validation that types match reality.
- Fix approach: Use `openapi-typescript` to generate types from the FastAPI `/openapi.json` endpoint. Add a `package.json` script for regeneration.

**Monolithic scoring module (1835 lines):**
- Issue: `backend/app/calculators/scoring.py` is the largest application source file at 1835 lines. It contains all scoring logic for 10 categories, message generation, email assembly, and default rule definitions in a single file.
- Files: `backend/app/calculators/scoring.py`
- Impact: Difficult to navigate, test individual categories in isolation, or have multiple developers work on different scoring categories simultaneously.
- Fix approach: Split into per-category scoring modules under `backend/app/calculators/scoring/` with an `__init__.py` that re-exports `calculate_score`. Keep shared helpers and `DEFAULT_RULES` in a common module.

**In-memory pending uploads store:**
- Issue: `_pending_uploads` dict in `backend/app/modules/upload/service.py:65` stores pending upload state in process memory. The comment acknowledges this: "sufficient for single Cloud Run instance."
- Files: `backend/app/modules/upload/service.py:64-73`
- Impact: If Cloud Run scales to multiple instances, a signed URL generated on instance A cannot be completed on instance B. Also lost on instance restart/cold start.
- Fix approach: Move pending upload tracking to the database or Redis. Alternatively, rely on GCS signed URLs being self-contained (encode metadata in the object name or use GCS metadata).

**Hardcoded business text in Python source code:**
- Issue: Indonesian-language business messages (closing messages, scoring messages, email templates) are hardcoded as Python string literals throughout `backend/app/calculators/scoring.py` (lines 300-435). These are business-critical customer-facing texts.
- Files: `backend/app/calculators/scoring.py:300-435` (DEFAULT_RULES dict), and inline throughout message generation functions
- Impact: Changing customer-facing text requires code deployment. Non-technical stakeholders cannot review or edit messages without developer involvement.
- Fix approach: The database-stored `scoring_rules` with message templates partially addresses this. Ensure all message templates are configurable via rules, not just some.

## Security Considerations

**OIDC audience validation disabled in local dev:**
- Risk: When `cloud_run_url` is empty (local dev), `audience` is set to `None` in `backend/app/core/oidc.py:36`, which means any valid Google OIDC token is accepted regardless of intended audience.
- Files: `backend/app/core/oidc.py:36`
- Current mitigation: Only affects local development. Production has `cloud_run_url` set.
- Recommendations: This is acceptable for local dev but should be documented. Consider logging a warning when audience validation is disabled.

**Empty scheduler email allowlist accepts any service account:**
- Risk: When `allowed_scheduler_emails` is empty (per `backend/app/config.py:47`), any valid OIDC token with correct audience is accepted for scheduler endpoints.
- Files: `backend/app/core/dependencies.py:53-60`, `backend/app/config.py:46-47`
- Current mitigation: Comment in config acknowledges the behavior. Production should have the allowlist configured.
- Recommendations: Add a startup warning log when `allowed_scheduler_emails` is empty in non-debug mode.

**CORS allows all methods and headers:**
- Risk: `allow_methods=["*"]` and `allow_headers=["*"]` in `backend/app/main.py:53-54` is broader than necessary.
- Files: `backend/app/main.py:42-55`
- Current mitigation: Origin allowlist is properly restricted to specific Firebase Hosting domains and localhost.
- Recommendations: Restrict to `["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"]` and specific headers like `Authorization`, `Content-Type`. Low priority since origin restriction is in place.

## Performance Bottlenecks

**Synchronous sync execution blocks request:**
- Problem: `POST /api/v1/sync` in `backend/app/modules/sync/router.py:18-43` runs the entire sync operation synchronously within the HTTP request. The response is only sent after all brands are synced.
- Files: `backend/app/modules/sync/router.py:41` (`await run_sync(sync_id=sync_id)`)
- Cause: Sync fetches data from Google Sheets for all brands, which can take significant time. The request blocks until completion.
- Improvement path: Return the `sync_id` immediately (202 Accepted) and run the sync as a background task using `asyncio.create_task()` or a task queue. The frontend already polls `/sync/status` for updates.

**Two database queries for paginated lists (count + fetch):**
- Problem: Every paginated endpoint (evaluations, brands) issues two separate queries: one for the result rows and one for `COUNT(*)`.
- Files: `backend/app/db/queries/evaluations.py:136-170` (list) and `backend/app/db/queries/evaluations.py:173-179` (count)
- Cause: Standard pagination pattern, but the count query re-scans the same filtered data.
- Improvement path: Use a window function (`COUNT(*) OVER()`) in the main query to get total count in a single round-trip. Low priority unless pagination queries become slow.

## Fragile Areas

**Scoring calculator coupling to manual_data shape:**
- Files: `backend/app/calculators/scoring.py` (entire file), `frontend/src/components/evaluation/forms/formConfig.ts`
- Why fragile: The scoring system uses deeply nested key paths like `_get_nested(manual_data, "business", "salesMonth0")` (line 1801) with string-based field access. Frontend form field keys in `formConfig.ts` must exactly match the Python dictionary keys. There is no shared schema or validation.
- Safe modification: When adding or renaming manual input fields, update both `frontend/src/components/evaluation/forms/formConfig.ts` and the corresponding `_get_nested()` calls in `backend/app/calculators/scoring.py`. Run both frontend and backend test suites.
- Test coverage: Backend scoring has strong unit tests (`backend/tests/unit/calculators/test_scoring.py`, 2487 lines). Frontend form config has tests (`frontend/src/components/evaluation/forms/formConfig.test.ts`). The gap is cross-system integration testing.

**Dynamic SQL construction in evaluation queries:**
- Files: `backend/app/db/queries/evaluations.py:103-170`
- Why fragile: `_build_filter_clauses()` constructs SQL WHERE clauses dynamically with f-string interpolation for column names (e.g., `e.{sort_by}` on line 166). While `sort_by` is constrained by `Literal` type annotation, the safety depends on FastAPI's query parameter validation.
- Safe modification: Always validate sort column names against an allowlist before string interpolation. The `Literal["created_at", "final_score"]` type does this at the router level.
- Test coverage: Integration tests exist in `backend/tests/integration/api/test_evaluation_list.py` (830 lines).

**Eslint-disable for react-hooks/exhaustive-deps:**
- Files: `frontend/src/pages/EvaluationPage.tsx:80`, `frontend/src/components/evaluation/scoring/ScoringSection.tsx:74`
- Why fragile: Intentionally omitting dependencies from `useEffect` can cause stale closure bugs if the suppressed dependencies change unexpectedly. The comments explain the intent, which mitigates somewhat.
- Safe modification: When modifying state management in these components, verify the effect dependencies are still correct. Consider refactoring to avoid the suppressions.
- Test coverage: Both files have companion test files.

## Dependencies at Risk

**No dependency risks detected:**
- The project uses well-maintained, popular packages (FastAPI, React 19, Firebase, asyncpg, Polars).
- All frontend dependencies are on recent major versions (React 19, Vite 7, Vitest 4, TypeScript 5.9).
- Backend uses `uv` for package management with a lockfile.

## Test Coverage Gaps

**No tests for `backend/app/services/` directory:**
- What's not tested: The `backend/app/services/` directory exists but only contains `__init__.py`. This is a placeholder, not a gap.
- Risk: None currently.
- Priority: N/A

**No E2E tests in main test suites:**
- What's not tested: Full user flows from frontend through API to database. Smoke tests exist in `smoke-tests/` but are separate from the main CI test suites.
- Files: `smoke-tests/` directory
- Risk: Integration bugs between frontend and backend (e.g., API contract mismatches from hand-written types) may not be caught until manual testing.
- Priority: Medium. The hand-written OpenAPI types in `apiClient.ts` make this more risky. Auto-generating types would reduce the need for E2E tests.

**Upload service integration with GCS not fully testable locally:**
- What's not tested: The GCS signed URL flow (`backend/app/modules/upload/gcs_client.py`) depends on real GCS credentials. Local dev likely uses a fallback path.
- Files: `backend/app/modules/upload/gcs_client.py:124`, `backend/app/modules/upload/service.py`
- Risk: GCS-specific bugs (permissions, signed URL expiry, content-type handling) may not surface in CI.
- Priority: Low. Integration tests mock the GCS client (`backend/tests/integration/api/test_upload.py`).

**Unused `onResetSave` prop suppressed with eslint-disable:**
- What's not tested: `frontend/src/components/evaluation/EvaluationSections.tsx:79` destructures `onResetSave` but immediately aliases it to `_onResetSave` with an eslint-disable for unused vars.
- Files: `frontend/src/components/evaluation/EvaluationSections.tsx:79`
- Risk: Dead prop in the interface. Minor but adds confusion.
- Priority: Low. Remove the prop from the component interface if truly unused.

---

*Concerns audit: 2026-03-06*
