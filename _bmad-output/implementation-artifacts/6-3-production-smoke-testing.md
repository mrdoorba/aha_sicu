# Story 6.3: Production Smoke Testing

Status: ready-for-dev

<!-- Note: Validation is optional. Run validate-create-story for quality check before dev-story. -->

## Story

As a **QA engineer**,
I want **to run end-to-end smoke tests against the production environment**,
so that **we verify the full workflow works in production before user onboarding (Story 6.4)**.

## Acceptance Criteria

1. **AC1: Backend health and reachability** — The Cloud Run backend service at its deployed URL responds with `{"status": "healthy"}` on `GET /health` within 10 seconds. The FastAPI Swagger UI at `/docs` also returns HTTP 200.

2. **AC2: Authentication enforcement** — All `/api/v1/*` endpoints reject unauthenticated requests with HTTP 401 or 403. Specifically, `GET /api/v1/brands`, `GET /api/v1/evaluations`, `POST /api/v1/sync`, and `POST /api/v1/upload/signed-url` all return 401/403 without a valid Firebase JWT.

3. **AC3: Frontend SPA loads and routes** — Firebase Hosting serves the SPA at the deployed URL. Root path (`/`) returns HTTP 200 with `text/html` content containing `<script` tags and `<div id="root"`. Deep links (e.g., `/brands`, `/history`, `/evaluation/1`) also return HTTP 200 (SPA rewrite working).

4. **AC4: Database connectivity** — An authenticated request to `GET /api/v1/brands?page=1&limit=1` returns HTTP 200 with a valid JSON response (confirming Neon PostgreSQL connectivity from Cloud Run). An authenticated request to `GET /api/v1/sync/status` returns sync status data (confirming `sync_status` table accessible).

5. **AC5: GCS signed URL generation** — An authenticated `POST /api/v1/upload/signed-url` with a valid payload (`{"filename": "smoke-test.csv", "content_type": "text/csv", "file_type": "cpc_ad_report", "brand_id": <valid_brand_id>}`) returns a response containing `upload_url`, `upload_id`, and `expires_at` fields. The `upload_url` points to `storage.googleapis.com`.

6. **AC6: SSE endpoint connectivity** — `GET /api/v1/events` without a token returns HTTP 422 (missing required query parameter). With an invalid token, returns HTTP 401/403. With a valid token, returns `Content-Type: text/event-stream` and the connection stays open (confirming SSE infrastructure works).

7. **AC7: Full evaluation workflow (manual walkthrough checklist)** — A documented manual test procedure covers the complete flow: login → navigate to brands → select a brand → upload test files → verify calculator execution → enter manual data → generate final score → save evaluation → verify in history. Checklist is stored as `smoke-tests/MANUAL_CHECKLIST.md`.

8. **AC8: Smoke test automation** — Automated smoke tests (Playwright API tests, no browser required) cover AC1-AC6 and can be run via a single command: `npx playwright test --config=smoke-tests/playwright.config.ts`. Tests accept environment URLs via `SMOKE_BACKEND_URL` and `SMOKE_FRONTEND_URL` environment variables. All unauthenticated tests pass in CI; authenticated tests documented for manual execution.

## Tasks / Subtasks

- [ ] Task 1: Set up Playwright smoke test infrastructure (AC: #8)
  - [ ] 1.1 Create `smoke-tests/` directory at project root
  - [ ] 1.2 Create `smoke-tests/package.json` with `@playwright/test` dependency (standalone from frontend package.json — smoke tests are project-level, not frontend-specific)
  - [ ] 1.3 Create `smoke-tests/playwright.config.ts` with API-only configuration (no browser binaries needed): 30s timeout, 1 retry, `SMOKE_BACKEND_URL` and `SMOKE_FRONTEND_URL` env vars, JSON reporter for CI output
  - [ ] 1.4 Create `smoke-tests/tsconfig.json` for TypeScript support
  - [ ] 1.5 Add `smoke-tests/node_modules/` to `.gitignore`

- [ ] Task 2: Implement backend health smoke tests (AC: #1)
  - [ ] 2.1 Create `smoke-tests/tests/backend-health.spec.ts`
  - [ ] 2.2 Test: `GET /health` returns 200 with `{"status": "healthy"}`
  - [ ] 2.3 Test: `GET /docs` returns 200 (FastAPI Swagger UI accessible)

- [ ] Task 3: Implement auth enforcement smoke tests (AC: #2)
  - [ ] 3.1 Create `smoke-tests/tests/auth-enforcement.spec.ts`
  - [ ] 3.2 Test: `GET /api/v1/brands` without auth returns 401/403
  - [ ] 3.3 Test: `GET /api/v1/evaluations` without auth returns 401/403
  - [ ] 3.4 Test: `POST /api/v1/sync` without auth returns 401/403
  - [ ] 3.5 Test: `POST /api/v1/upload/signed-url` without auth returns 401/403

- [ ] Task 4: Implement frontend SPA smoke tests (AC: #3)
  - [ ] 4.1 Create `smoke-tests/tests/frontend-spa.spec.ts`
  - [ ] 4.2 Test: Root URL (`/`) returns 200 with `text/html` content-type
  - [ ] 4.3 Test: HTML body contains `<script` tags and `<div id="root"`
  - [ ] 4.4 Test: Deep link `/brands` returns 200 (SPA rewrite working)
  - [ ] 4.5 Test: Deep link `/history` returns 200 (SPA rewrite working)

- [ ] Task 5: Implement database connectivity smoke tests (AC: #4)
  - [ ] 5.1 Create `smoke-tests/tests/database-connectivity.spec.ts`
  - [ ] 5.2 Test (authenticated): `GET /api/v1/brands?page=1&limit=1` returns 200 with JSON containing `items` array
  - [ ] 5.3 Test (authenticated): `GET /api/v1/sync/status` returns 200 with sync status JSON
  - [ ] 5.4 Add skip annotation for authenticated tests when `SMOKE_AUTH_TOKEN` env var is not set, with clear instructions in test file comments

- [ ] Task 6: Implement GCS signed URL smoke tests (AC: #5)
  - [ ] 6.1 Create `smoke-tests/tests/signed-url.spec.ts`
  - [ ] 6.2 Test (unauthenticated): `POST /api/v1/upload/signed-url` returns 401/403
  - [ ] 6.3 Test (authenticated): `POST /api/v1/upload/signed-url` with valid payload returns response with `upload_url`, `upload_id`, `expires_at`
  - [ ] 6.4 Test (authenticated): Verify `upload_url` contains `storage.googleapis.com`
  - [ ] 6.5 Add skip annotation for authenticated tests when token not available

- [ ] Task 7: Implement SSE endpoint smoke tests (AC: #6)
  - [ ] 7.1 Create `smoke-tests/tests/sse-endpoint.spec.ts`
  - [ ] 7.2 Test: `GET /api/v1/events` without token query param returns 422
  - [ ] 7.3 Test: `GET /api/v1/events?token=invalid` returns 401/403
  - [ ] 7.4 Test (authenticated): Verify response `Content-Type` is `text/event-stream` (skip if no token)

- [ ] Task 8: Create manual walkthrough checklist (AC: #7)
  - [ ] 8.1 Create `smoke-tests/MANUAL_CHECKLIST.md`
  - [ ] 8.2 Document pre-requisites: production URLs, test user credentials, sample data files (CPC Ad Report CSV, Keyword Report CSV, Order Export XLSX, Mass Update XLSX)
  - [ ] 8.3 Document step-by-step login flow (Firebase Auth)
  - [ ] 8.4 Document brand sync verification (trigger sync, verify SSE updates, check brand list)
  - [ ] 8.5 Document brand selection and evaluation start
  - [ ] 8.6 Document file upload flow (4 file types, verify each uploads successfully via GCS signed URL)
  - [ ] 8.7 Document calculator execution verification (Ads Keyword, Discount Check, Top SKU)
  - [ ] 8.8 Document manual data entry (spot check 3-5 fields across categories)
  - [ ] 8.9 Document final scoring (Fashion + Non-Fashion template, verify score + verdict)
  - [ ] 8.10 Document save evaluation and verify in history page
  - [ ] 8.11 Document SSE notification verification (save evaluation → other session sees toast)
  - [ ] 8.12 Add pass/fail checkbox for each step

- [ ] Task 9: Add smoke test npm scripts and documentation (AC: #8)
  - [ ] 9.1 Add `README.md` in `smoke-tests/` with setup and run instructions
  - [ ] 9.2 Document how to obtain `SMOKE_AUTH_TOKEN` (Firebase Auth REST API with test user credentials)
  - [ ] 9.3 Document environment variables: `SMOKE_BACKEND_URL`, `SMOKE_FRONTEND_URL`, `SMOKE_AUTH_TOKEN`
  - [ ] 9.4 Verify all unauthenticated smoke tests pass against dev environment

## Dev Notes

### Technical Requirements & Constraints

- **Playwright API-only tests** — Use `@playwright/test` with `request` API context. Do NOT install browser binaries (`npx playwright install` not needed). This keeps the smoke test suite lightweight (~5MB vs ~500MB with browsers).
- **No browser tests** — All smoke tests use HTTP requests only. The project has no E2E test framework, and adding full browser tests is out of scope for this story.
- **Environment-agnostic** — Tests MUST work against any environment (dev, prod) by accepting URLs via env vars. Do NOT hardcode any URLs, project IDs, or service names.
- **Authentication split** — Tests are split into two categories:
  1. **Unauthenticated** (AC1, AC2, AC3, part of AC5, AC6): Can run in CI without credentials
  2. **Authenticated** (AC4, part of AC5, AC6): Require a valid Firebase JWT token. Skipped automatically when `SMOKE_AUTH_TOKEN` is not set.
- **Firebase JWT token for authenticated tests** — Obtain via Firebase Auth REST API: `POST https://identitytoolkit.googleapis.com/v1/accounts:signInWithPassword?key={FIREBASE_API_KEY}` with email/password. The `idToken` from the response is the `SMOKE_AUTH_TOKEN`.
- **Cloud Run auth model** — The Cloud Run service is publicly accessible (no IAM-based auth). Authentication is handled at the application level by FastAPI middleware validating Firebase JWTs. This means smoke tests can reach the service directly without GCP IAM credentials.
- **Standalone package** — `smoke-tests/` has its own `package.json` to keep test dependencies separate from `frontend/`. This avoids polluting the frontend with test-only deps and makes smoke tests project-level (testing both backend and frontend).
- **SSE testing limitation** — Playwright's `request` API does not support streaming responses. For SSE tests, use `fetch()` with `AbortController` timeout or simply verify HTTP status codes and headers.
- **No test data mutation in production** — Unauthenticated tests are pure GET/validation. Authenticated tests that POST (signed URL) should use a dedicated test brand if available, or be clearly documented as requiring cleanup.

### Architecture Compliance

**Smoke test suite is additive** — does NOT modify any existing code:

| Aspect | Compliance |
|--------|------------|
| Backend code | No changes — tests hit existing endpoints |
| Frontend code | No changes — tests verify deployed SPA |
| CI workflows | No changes — smoke tests run manually or in a future CI step |
| Infrastructure | No changes — tests validate existing resources |
| Database | Read-only for automated tests — no data created |

**Endpoint verification matrix (from `backend/app/main.py`):**

| Endpoint | Auth | Smoke Test Type |
|----------|------|-----------------|
| `GET /health` | None | Automated (AC1) |
| `GET /docs` | None | Automated (AC1) |
| `GET /api/v1/brands` | Required | Unauth rejection (AC2) + Auth connectivity (AC4) |
| `GET /api/v1/evaluations` | Required | Unauth rejection (AC2) |
| `POST /api/v1/sync` | Required | Unauth rejection (AC2) |
| `GET /api/v1/sync/status` | Required | Auth connectivity (AC4) |
| `POST /api/v1/upload/signed-url` | Required | Unauth rejection (AC2) + Auth generation (AC5) |
| `GET /api/v1/events` | Token query | Missing token 422 (AC6) + Invalid token 401 (AC6) |

### Library & Framework Requirements

| Package | Version | Purpose | Install Location |
|---------|---------|---------|-----------------|
| `@playwright/test` | `^1.58` | HTTP API smoke test framework | `smoke-tests/package.json` devDependency |
| `typescript` | `^5.9` | TypeScript for test files | `smoke-tests/package.json` devDependency |

**No browser binaries needed.** The `@playwright/test` package provides `APIRequestContext` natively without downloading Chromium/Firefox/WebKit.

**Why Playwright over alternatives:**
- Already in Node.js ecosystem (project uses Node 20 for frontend)
- `APIRequestContext` provides clean HTTP testing without browser overhead
- Built-in assertions, retries, parallel execution, and JSON reporter
- Can be extended to browser tests later (Story 6.4 onboarding validation) without framework change
- Superior to raw `fetch()` scripts: built-in timeout handling, retry logic, structured reporting

### File Structure Requirements

**Files to CREATE:**
```
smoke-tests/
├── package.json                      # Standalone deps: @playwright/test, typescript
├── tsconfig.json                     # TypeScript config for smoke tests
├── playwright.config.ts              # Playwright config (API-only, no browsers)
├── README.md                         # Setup and run instructions
├── MANUAL_CHECKLIST.md               # Manual walkthrough checklist (AC7)
└── tests/
    ├── backend-health.spec.ts        # AC1: /health and /docs checks
    ├── auth-enforcement.spec.ts      # AC2: Unauthenticated rejection
    ├── frontend-spa.spec.ts          # AC3: SPA loads and routes
    ├── database-connectivity.spec.ts # AC4: Authenticated DB connectivity
    ├── signed-url.spec.ts            # AC5: GCS signed URL generation
    └── sse-endpoint.spec.ts          # AC6: SSE endpoint connectivity
```

**Files to MODIFY:**
```
.gitignore                            # Add smoke-tests/node_modules/
```

**Files to REFERENCE (do NOT modify):**
```
backend/app/main.py                   # Health endpoint, router mounts
backend/app/modules/*/router.py       # API endpoint signatures
frontend/src/main.tsx                  # React root element
firebase.json                         # Firebase Hosting SPA rewrite config
.firebaserc                           # Hosting site IDs (aha-sicu-dev, aha-sicu-prod)
.github/workflows/deploy-backend.yml  # Cloud Run service URL
.github/workflows/deploy-frontend.yml # Firebase Hosting URL
```

### Testing Requirements

**Smoke test design principles:**
1. **Fast** — Total suite under 30 seconds. Each test under 5 seconds.
2. **Idempotent** — No side effects. Can run repeatedly without cleanup.
3. **Independent** — Each test file runs independently. No test ordering dependencies.
4. **Non-destructive** — Read-only operations for automated tests. No data creation/mutation.
5. **Environment-portable** — Works against dev or prod via env vars.

**Test execution modes:**
```bash
# Run ALL unauthenticated smoke tests (CI-safe)
cd smoke-tests && npx playwright test

# Run ALL tests including authenticated (requires token)
SMOKE_AUTH_TOKEN="<firebase_jwt>" npx playwright test

# Run specific test file
npx playwright test tests/backend-health.spec.ts

# Run against specific environment
SMOKE_BACKEND_URL="https://aha-sicu-dev-api-xxx.run.app" \
SMOKE_FRONTEND_URL="https://aha-sicu-dev.web.app" \
npx playwright test
```

**Expected test counts:**
- Unauthenticated: ~10 tests (always run)
- Authenticated: ~5 tests (skipped without token)
- Total: ~15 tests

### Previous Story Intelligence

**From Story 6.2 (CI/CD Pipeline Activation) — Critical learnings:**

| Learning | Impact on This Story |
|----------|---------------------|
| CI workflow already verifies backend + frontend builds and tests | Smoke tests are complementary — they verify the DEPLOYED artifact, not the build |
| Deploy workflows include health check step (`curl /docs`) | AC1 duplicates this intentionally — smoke tests run independently of deploy pipeline |
| Environment prefix `aha-sicu-{env}-*` on all resources | Smoke test docs must reference env-prefixed URLs (e.g., `aha-sicu-dev.web.app`) |
| Firebase CLI deploys via WIF (no SA keys) | Smoke tests don't deploy — they only verify deployed state |
| Pre-existing lint/test issues fixed in Story 6.2 | All CI checks pass — no blockers for smoke test development |
| `firebase.json` uses multi-target config (`aha-sicu-dev` + `aha-sicu-prod`) | Frontend smoke tests must use the correct site URL per environment |
| Cloud Run `/docs` endpoint used for deploy health check | Reuse same endpoint in smoke tests for consistency |
| `SMOKE_BACKEND_URL` not yet defined anywhere | New env var introduced by this story — document in README |

**From Story 6.1 (Infrastructure Provisioning) — Relevant context:**

| Learning | Impact on This Story |
|----------|---------------------|
| Cloud Run service publicly accessible (no IAM auth on service) | Smoke tests can hit Cloud Run directly — no GCP IAM token needed |
| GCS bucket `aha_sicu_{env}_uploads` with 24h auto-delete lifecycle | Test uploads will be auto-cleaned — no manual cleanup needed |
| Secret Manager stores DB URL, GSheets creds, Firebase Admin creds | Smoke tests don't need secrets — they test via HTTP endpoints only |
| Neon PostgreSQL accessible from Cloud Run via connection string | DB connectivity verified indirectly via API endpoint tests (AC4) |

### Git Intelligence Summary

**Recent commit patterns (last 10 commits):**
```
93695aa Merge feature/story-6-2-cicd-pipeline-activation into develop
8f5531f Fix code review findings for Story 6.2 (11 issues)
f226305 Fix pre-existing TypeScript build errors for CI
9fe2501 Fix pre-existing test failures for CI
99e70b2 Fix all lint errors across backend and frontend
42cc5c8 Implement CI/CD pipeline activation (Story 6.2)
679edf8 Create story 6.2: CI/CD Pipeline Activation
48c14b8 Merge feature/fix-readme-secret-names into develop
b0c2656 Update docs to reflect env-prefixed secret names and terraform lessons
b265cbd Add interactive terraform setup script
```

**Insights:**
- All recent work is Epic 6 infrastructure/CI-CD — smoke testing is the natural next step
- Branching pattern confirmed: `feature/story-6-3-*` → merge to `develop`
- Story 6.2 established CI/CD patterns that smoke tests complement but don't overlap with
- Code review pattern: 11 issues found in 6.2 review — expect similar for smoke test code
- Story commit pattern: create story → implement → fix review findings → merge

### Latest Tech Information

**Playwright v1.58 (Feb 2026):**
- `APIRequestContext` provides HTTP testing without browser overhead
- `@playwright/test` package alone (~5MB) sufficient for API-only tests
- Built-in JSON reporter (`['json', { outputFile: 'smoke-results.json' }]`) for CI integration
- `test.skip()` conditional annotation for skipping authenticated tests when no token
- `test.describe` with `{ tag: '@smoke' }` for test categorization
- Configuration: `timeout: 30000` (30s per test), `retries: 1` for transient network issues

**Firebase Auth REST API (for obtaining test tokens):**
```bash
# Exchange email/password for Firebase ID token
curl -s "https://identitytoolkit.googleapis.com/v1/accounts:signInWithPassword?key=${FIREBASE_API_KEY}" \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","password":"testpass","returnSecureToken":true}' \
  | jq -r '.idToken'
```
- Token valid for 1 hour
- Used as `Authorization: Bearer <token>` for API requests
- Used as `?token=<token>` query param for SSE endpoint

**Cloud Run URLs:**
- Dev: `https://aha-sicu-dev-api-<hash>.asia-southeast1.run.app`
- Get via: `gcloud run services describe aha-sicu-dev-api --region=asia-southeast1 --format="value(status.url)"`

**Firebase Hosting URLs:**
- Dev: `https://aha-sicu-dev.web.app`
- Prod: `https://aha-sicu-prod.web.app`

### Project Structure Notes

- `smoke-tests/` is a NEW top-level directory — same level as `backend/`, `frontend/`, `infrastructure/`
- Standalone `package.json` keeps smoke test dependencies isolated from frontend
- No impact on existing CI/CD workflows — smoke tests are run manually for now (future: add as post-deploy step)
- `.gitignore` update required to exclude `smoke-tests/node_modules/`

### References

- [Source: _bmad-output/planning-artifacts/epics.md#Epic 6 - Story 6.3]
- [Source: _bmad-output/planning-artifacts/architecture.md#Infrastructure & Deployment, #API & Communication]
- [Source: _bmad-output/planning-artifacts/architecture.md#File Upload Architecture - GCS Signed URL Pattern]
- [Source: _bmad-output/planning-artifacts/architecture.md#API Boundaries]
- [Source: backend/app/main.py - Health endpoint at /health, router mounts under /api/v1/]
- [Source: backend/app/modules/events/router.py - SSE endpoint at /api/v1/events with token query param]
- [Source: backend/app/modules/upload/router.py - Signed URL at POST /api/v1/upload/signed-url]
- [Source: backend/app/modules/brands/router.py - Brand list at GET /api/v1/brands]
- [Source: backend/app/modules/sync/router.py - Sync status at GET /api/v1/sync/status]
- [Source: firebase.json - Multi-target hosting config with SPA rewrites]
- [Source: .firebaserc - Project aliases and hosting targets]
- [Source: .github/workflows/deploy-backend.yml - Cloud Run deploy with health check]
- [Source: .github/workflows/deploy-frontend.yml - Firebase Hosting deploy with health check]
- [Source: _bmad-output/implementation-artifacts/6-2-cicd-pipeline-activation.md - Previous story learnings]
- [Source: _bmad-output/implementation-artifacts/6-1-infrastructure-provisioning.md - Infrastructure context]
- [Source: _bmad-output/lessons-learned.md - Project-wide lessons]

## Dev Agent Record

### Agent Model Used

{{agent_model_name_version}}

### Debug Log References

### Completion Notes List

- Ultimate context engine analysis completed - comprehensive developer guide created

### Change Log

### File List
