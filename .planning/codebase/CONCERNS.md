# Codebase Concerns

**Analysis Date:** 2026-03-16

## Tech Debt

**Database Connection Pool Undersized for Production:**
- Issue: Connection pool max_size defaults to 5 (see `backend/app/db/connection.py:26`)
- Files: `backend/app/db/connection.py`
- Impact: Under high concurrency (>5 simultaneous requests), additional requests will queue and timeout. Production traffic with 50+ concurrent users will experience connection exhaustion
- Fix approach: Make pool size configurable via environment variable; recommend starting at min_size=10, max_size=20 for production. Test load under realistic user volume before deployment

**Email Template Hardcoded String Translations:**
- Issue: Strings dict in `backend/app/modules/email/template.py` contains hardcoded translations for id/en/th languages (line 37+)
- Files: `backend/app/modules/email/template.py` (~500+ lines of translation strings)
- Impact: Adding new languages or updating translations requires code changes and redeployment. No centralized translation system
- Fix approach: Migrate STRINGS dict to database or external i18n service; make language selection dynamic via configuration

**Large Email Template Module (1106 lines):**
- Issue: Single monolithic file handles CSS generation, HTML rendering, image embedding, localization
- Files: `backend/app/modules/email/template.py`
- Impact: Hard to maintain, test individual sections, or modify email layout without touching core logic
- Fix approach: Split into: `template_renderer.py` (HTML structure), `template_styles.py` (CSS), `template_localization.py` (STRINGS), `template_images.py` (image handling)

**Broad Exception Handling Masks Root Causes:**
- Issue: Multiple `except Exception as e:` blocks throughout codebase without specific error types
- Files: `backend/app/modules/evaluations/service.py`, `backend/app/modules/sync/service.py`, `backend/app/modules/email/service.py`
- Impact: Makes debugging production issues difficult; generic error messages don't indicate whether failure is auth, network, data validation, or database
- Fix approach: Create domain-specific exception hierarchy (CalcException, SyncException, EmailException, etc.); catch and re-raise with context

**Missing Transaction Boundaries in Multi-Step Operations:**
- Issue: Sync operations in `backend/app/modules/sync/service.py` loop through rows and insert independently without explicit transaction control
- Files: `backend/app/modules/sync/service.py:44-58` (sync_sheet_to_table function)
- Impact: Partial sync on failure: if sync fails on row 500 of 1000, rows 1-499 are committed; application state is inconsistent
- Fix approach: Wrap sync in explicit transaction; rollback all changes if any row fails. Add transaction support to connection pool

**Unvalidated Calculator Auto-Execution:**
- Issue: After file upload, calculator engine automatically runs if dependencies are met, but no validation that manual data is still valid
- Files: `backend/app/modules/upload/service.py`, `backend/app/calculators/engine.py`
- Impact: If user uploads invalid file (e.g., wrong date range, malformed data) after setting manual inputs, calculators run on garbage data without warning
- Fix approach: Add pre-execution validation step; require explicit user confirmation before auto-exec on upload

---

## Known Bugs

**Double-Encoded JSONB Fields in Database:**
- Symptoms: Calculator results stored as `string` instead of `dict`, requires JSON parsing in code
- Files: `backend/app/calculators/engine.py:63-71` (shows manual `json.loads()` workaround)
- Trigger: Likely caused by inconsistent serialization in evaluation save/load path
- Workaround: Code uses `isinstance(data, str)` check and `json.loads()` to handle both formats

**Email Image Embedding Inconsistency:**
- Symptoms: Email preview shows broken image references; sent email may show different images than preview
- Files: `backend/app/modules/email/template.py:1018-1032`, `backend/app/modules/email/service.py:60-130`
- Trigger: Chart images are embedded as base64 data URIs in preview, but sent as `cid:` Content-ID references. Mismatch if base64 decoding fails
- Workaround: Template tries both formats; falls back to placeholder if decoding fails, but user isn't notified

**Missing Null Checks in API Response Handling:**
- Symptoms: Frontend crashes if API returns `null` for expected nested object
- Files: `frontend/src/hooks/useBrandDetail.ts:7-9`, `frontend/src/pages/EvaluationDetailPage.tsx:63-76` (formatValue function assumes value exists)
- Trigger: Brand with no raw_data, or evaluation with missing calculator_results
- Workaround: Frontend uses `?.` optional chaining and fallback values, but incomplete coverage

---

## Security Considerations

**Firebase Token Validation Catches All Exceptions:**
- Risk: Any error during token validation (network hiccup, cert problem, Firebase outage) results in identical "invalid token" response
- Files: `backend/app/core/security.py:44-45` (bare `except Exception`)
- Current mitigation: Error is logged; user can't exploit to guess valid token formats
- Recommendations: Distinguish between validation failures (invalid token) vs infrastructure failures (retry); add monitoring for auth error patterns

**Credentials Loaded from Multiple Sources Without Priority Ordering:**
- Risk: If multiple credential sources are configured, behavior is ambiguous
- Files: `backend/app/core/security.py:21-28` (FIREBASE_AUTH_EMULATOR_HOST takes priority, then file, then ADC)
- Current mitigation: Documented in code; emulator mode hard-codes project ID
- Recommendations: Add explicit logging when credentials are selected; validate in startup that only one source is active in production

**Google Sheets Credentials in JSON String:**
- Risk: `gsheets_credentials_json` setting stores entire service account key as plaintext environment variable
- Files: `backend/app/modules/sync/sheets_client.py:29-34`
- Current mitigation: Credentials are in Google Secret Manager, not committed to repo
- Recommendations: Add Secret Manager client to load credentials at runtime instead of env var; rotate service account key quarterly

**SMTP Password in Plain Text:**
- Risk: SMTP credentials passed as environment variables; visible in process listing and logs
- Files: `backend/app/modules/email/service.py:152` (uses settings.smtp_host, settings.smtp_port)
- Current mitigation: Credentials stored in Secret Manager, not in codebase
- Recommendations: Add SMTP auth logging sanitization; rotate credentials regularly

**Base64-Encoded Chart Images Lack Validation:**
- Risk: User can POST arbitrary large base64 strings as chart_image parameter; no size limit
- Files: `backend/app/modules/email/service.py:42-59` (_decode_chart_image function)
- Current mitigation: Base64 decode will fail on invalid input; caught and handled
- Recommendations: Add size limit to base64 input (e.g., max 1MB); reject if decoded size exceeds threshold

---

## Performance Bottlenecks

**Large Test File (2486 lines) for Scoring Calculator:**
- Problem: Single test file `backend/tests/unit/calculators/test_scoring.py` tests all scoring logic
- Files: `backend/tests/unit/calculators/test_scoring.py`
- Cause: Monolithic scoring calculator with hundreds of rules requires exhaustive test coverage
- Improvement path: Split scorer into rule-based modules; move rule tests to separate files; use parameterized tests for variants

**Email Template String Interpolation in Python (Not Template Engine):**
- Problem: `backend/app/modules/email/template.py` uses f-strings and manual string building for 1100+ lines
- Files: `backend/app/modules/email/template.py:1070+` (raw HTML assembly)
- Cause: No Jinja2 or template engine; HTML escaping is manual via `_esc()` function
- Improvement path: Use Jinja2 with auto-escaping; reduces code by ~60%, prevents XSS bugs, simplifies i18n

**Synchronous Google Sheets Calls Blocked on Thread Pool:**
- Problem: Every Google Sheets fetch runs in `asyncio.to_thread()`, blocking thread pool for 1-5 seconds
- Files: `backend/app/modules/sync/sheets_client.py:82`
- Cause: Google API client is synchronous; no async version available
- Improvement path: Use google-api-python-client's batch request mode; cache results with 5-minute TTL to avoid re-fetch on retries

**Pagination Without Cursor (Offset-Based):**
- Problem: All list endpoints use LIMIT/OFFSET; full table scan for every page
- Files: `backend/app/db/queries/evaluations.py:190+`, `backend/app/db/queries/brands.py:69+`
- Cause: Simpler to implement than cursor pagination
- Improvement path: Implement cursor-based pagination using `created_at + id` composite key; add index on (created_at DESC, id)

**Frontend Large Components Not Code-Split:**
- Problem: Component bundle includes all pages; lazy loading would save initial load time
- Files: `frontend/src/pages/EvaluationDetailPage.tsx` (640 lines), `frontend/src/pages/RulesPage.tsx` (328 lines)
- Cause: React Router configured with eager import
- Improvement path: Use `React.lazy()` + Suspense for route-based code splitting; prioritize EvaluationDetailPage (heaviest)

**useEvaluationOrchestrator Hook Orchestrates Too Much:**
- Problem: Single hook manages data fetching, form state, scoring, calculator results, rules, save orchestration
- Files: `frontend/src/hooks/useEvaluationOrchestrator.ts` (261 lines)
- Cause: Complex evaluation workflow required consolidated state
- Improvement path: Split into focused hooks: useEvaluationForm, useEvaluationScoring, useEvaluationCalculators; compose in page component

---

## Fragile Areas

**Calculator Execution Engine (Lack of Idempotency):**
- Files: `backend/app/calculators/engine.py`
- Why fragile: Readiness check (`check_calculator_readiness`) can return "ready" but execution can fail partway through. No transactional guarantee that result is saved or rolled back
- Safe modification: Add explicit transaction wrapping in `run_ready_calculators()` function. Test that partial failure doesn't leave orphaned results
- Test coverage: Missing tests for concurrent calculator execution (two requests for same brand_id simultaneously)

**Evaluation Save Path (Manual Inputs Validation):**
- Files: `backend/app/modules/evaluations/service.py`, `backend/app/modules/evaluations/calculator_service.py`
- Why fragile: Manual inputs are stored as JSONB blob without schema validation. Frontend sends `Record<string, unknown>`. Backend accepts any JSON structure
- Safe modification: Add Pydantic model for ManualData schema validation on save endpoint. Add migration to validate existing data
- Test coverage: No tests for malformed manual_data (missing required fields, wrong types, extra fields)

**Sync Status Update Without Locking:**
- Files: `backend/app/modules/sync/service.py`, `backend/app/db/queries/sync_status.py`
- Why fragile: Multiple concurrent sync requests can overwrite each other's status. No row-level locking
- Safe modification: Add `FOR UPDATE` lock in sync_status query; ensure only one sync operation runs at a time (advisory lock or mutex)
- Test coverage: No concurrency tests for simultaneous sync triggers

**Frontend Auto-Save Without Conflict Detection:**
- Files: `frontend/src/hooks/useAutoSaveForm.ts` (315 lines)
- Why fragile: If multiple browser tabs edit same evaluation, last-write-wins; user loses data from other tab
- Safe modification: Add version field to manual_inputs; return conflict error on save if version mismatch; prompt user to reload
- Test coverage: No tests for concurrent saves from multiple clients

---

## Scaling Limits

**Database Pool Max Connections (5):**
- Current capacity: 5 concurrent requests; 6th request queues indefinitely
- Limit: Production traffic (50+ concurrent users) will exhaust pool
- Scaling path: Increase max_size to 20 (see Tech Debt section); monitor connection wait times; switch to pgBouncer if pool exhaustion persists

**Email Sending is Synchronous (Not Queued):**
- Current capacity: Each email request blocks HTTP response until SMTP send completes (2-10 seconds)
- Limit: ~10 concurrent email requests before request timeout
- Scaling path: Implement job queue (Celery, Temporal, Cloud Tasks); return 202 Accepted; send email async

**Google Sheets Sync Rate Limit (300 requests/minute):**
- Current capacity: Sheet has ~500 rows; fetch takes 1-2 seconds (including retries). Each sync is 2 API calls (VP + Meeting)
- Limit: Can sync every 10-15 seconds before hitting rate limit
- Scaling path: Implement caching with 5-minute TTL; batch row updates into single request; use Sheets API batch_update instead of individual upserts

**Calculator Results Stored as JSONB (No Indexing):**
- Current capacity: List evaluations can retrieve 1000 evaluations; each carries 20KB+ of JSON (score_breakdown, calculator_results)
- Limit: Memory usage grows linearly with result count; no ability to filter/search within JSON without full table scan
- Scaling path: Normalize calculator results into separate tables; keep summary in evaluation; add indexes on key metrics

**Frontend TypeScript Compilation Time:**
- Current capacity: Initial `tsc -b` takes ~30 seconds; watch mode adds 5-10 second delay per change
- Limit: Developer productivity suffers; CI checks take 2 minutes for type checking alone
- Scaling path: Use esbuild or SWC for faster compilation; enable experimental TypeScript 5.9 project references; exclude node_modules from tsc

---

## Dependencies at Risk

**Python 3.14 (Bleeding Edge):**
- Risk: Python 3.14 released Feb 2026; only 4 months stable. Rare edge cases and breaking changes in stdlib
- Impact: Production outages if unforeseen incompatibilities discovered; harder to debug novel issues
- Migration plan: Maintain compatibility with 3.13 (stable); test on 3.14 in CI but don't require it yet. Pin to 3.13 in production until 3.14 has 6+ months history

**Firebase Admin SDK 6.0+ (Unstable Authentication):**
- Risk: Firebase SDK has had auth initialization issues in recent releases; `firebase_admin._apps` pattern is private API
- Impact: Auth initialization may silently fail or re-initialize multiple times in long-running processes
- Migration plan: Add explicit initialization check in `init_firebase()`; unit test that init succeeds and _apps is non-empty

**Polars 1.0+ (Unstable DataFrame API):**
- Risk: Polars is young; breaking API changes between 1.0 and 1.x (e.g., column access syntax)
- Impact: File uploads fail if Polars releases breaking change in parsing or column renaming
- Migration plan: Pin to Polars ~1.0.0 (conservative); test upload parsing in CI against 1.0, 1.1, 1.2

**React 19 (Fresh Major Version):**
- Risk: React 19 uses Server Components and Suspense patterns; many libraries not yet compatible
- Impact: Potential incompatibilities with React Router 7, TanStack Query, Recharts as they update
- Migration plan: Monitor library compatibility; pin major versions explicitly (react-router-dom ^7.13.0, @tanstack/react-query ^5.90.20)

---

## Missing Critical Features

**No Audit Log for Evaluation Changes:**
- Problem: Users can't see who modified evaluation, when, or what changed
- Blocks: Compliance workflows (some BD teams need approval trail); debugging "what changed?" issues
- Impact: High: Manual evaluation edits have no history

**No Bulk Email with Template Customization:**
- Problem: Send email endpoint only accepts one evaluation at a time; no ability to customize message per recipient
- Blocks: Sending evaluation reports to 50 brands in one operation; personalizing email with recipient-specific notes
- Impact: Medium: Users must click "Send Email" 50 times

**No Calculator Result Comparison (A/B):**
- Problem: Users can't compare results from different calculator runs or different rule versions
- Blocks: Understanding impact of rule changes; debugging "why did score change?"
- Impact: Low: Workaround is manual Excel diff

**No Export to PDF/Excel for Evaluation Report:**
- Problem: Users must screenshot email to share evaluation outside system
- Blocks: Offline sharing; integration with external reporting tools
- Impact: Low: Email itself is readable and shareable

---

## Test Coverage Gaps

**No Tests for Concurrent Calculator Execution:**
- What's not tested: Two simultaneous requests to run calculators for same brand
- Files: `backend/app/calculators/engine.py`, `backend/tests/unit/calculators/test_engine.py`
- Risk: Race condition where both requests read readiness, both decide to run, both write results (last write wins)
- Priority: High — can corrupt calculator state

**No Tests for Manual Data Schema Validation:**
- What's not tested: Saving manual_data with missing fields, wrong types, or extra fields
- Files: `backend/app/modules/evaluations/service.py`
- Risk: Malformed data saved to database; scoring engine crashes when accessing expected fields
- Priority: High — can break evaluations

**No Tests for Sync Partial Failure Recovery:**
- What's not tested: Sync fails after 500 rows of 1000; rollback or retry behavior
- Files: `backend/app/modules/sync/service.py`
- Risk: Inconsistent database state; some brands synced, some not
- Priority: High — data integrity

**No Frontend Tests for API Error Responses:**
- What's not tested: Handling 500, 429, timeout responses from backend
- Files: `frontend/src/hooks/*.ts` (useQuery hooks)
- Risk: UI crashes or shows generic error when API fails
- Priority: Medium — UX degradation

**No Tests for Email Encoding Edge Cases:**
- What's not tested: Brand name with emoji, HTML special characters, or non-ASCII in evaluation data
- Files: `backend/app/modules/email/template.py`, `backend/app/modules/email/service.py`
- Risk: Email corrupted or unreadable if brand name contains `<`, `&`, emoji
- Priority: Medium — email quality

**No Integration Tests for Full Evaluation Workflow:**
- What's not tested: Create brand → upload file → save manual inputs → calculate → score → send email (end-to-end)
- Files: Spans multiple modules
- Risk: Workflow breaks at unknown step; caught only in manual testing
- Priority: High — core workflow

---

*Concerns audit: 2026-03-16*
