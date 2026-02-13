# AHA SICU — Smoke Tests

Lightweight API-only smoke tests for verifying production deployments. Uses Playwright's `APIRequestContext` — **no browser binaries required**.

## Setup

```bash
cd smoke-tests
npm install
```

## Environment Variables

| Variable | Required | Description |
|----------|----------|-------------|
| `SMOKE_BACKEND_URL` | Yes | Cloud Run backend URL (e.g., `https://aha-sicu-dev-api-xxx.run.app`) |
| `SMOKE_FRONTEND_URL` | Yes | Firebase Hosting URL (e.g., `https://aha-sicu-dev.web.app`) |
| `SMOKE_AUTH_TOKEN` | No | Firebase JWT token for authenticated tests. Omit to skip auth tests. |

### Getting `SMOKE_BACKEND_URL`

```bash
gcloud run services describe aha-sicu-dev-api \
  --region=asia-southeast1 \
  --format="value(status.url)"
```

### Getting `SMOKE_FRONTEND_URL`

- **Dev:** `https://aha-sicu-dev.web.app`
- **Prod:** `https://aha-sicu-prod.web.app`

### Getting `SMOKE_AUTH_TOKEN`

Obtain a Firebase ID token via the Firebase Auth REST API:

```bash
curl -s "https://identitytoolkit.googleapis.com/v1/accounts:signInWithPassword?key=${FIREBASE_API_KEY}" \
  -H "Content-Type: application/json" \
  -d '{"email":"your-test-user@example.com","password":"your-password","returnSecureToken":true}' \
  | jq -r '.idToken'
```

The token is valid for **1 hour**. Set it as:

```bash
export SMOKE_AUTH_TOKEN="<token-from-above>"
```

## Running Tests

```bash
# Run ALL unauthenticated smoke tests (CI-safe)
SMOKE_BACKEND_URL="https://..." \
SMOKE_FRONTEND_URL="https://..." \
npx playwright test

# Run ALL tests including authenticated
SMOKE_BACKEND_URL="https://..." \
SMOKE_FRONTEND_URL="https://..." \
SMOKE_AUTH_TOKEN="<jwt>" \
npx playwright test

# Run a specific test file
npx playwright test tests/backend-health.spec.ts

# Run with npm scripts
npm test                  # All tests
npm run test:health       # Backend health only
npm run test:auth         # Auth enforcement only
npm run test:frontend     # Frontend SPA only
npm run test:db           # Database connectivity only
npm run test:signed-url   # GCS signed URL only
npm run test:sse          # SSE endpoint only
```

## Test Coverage

| Test File | AC | Auth Required | Tests |
|-----------|----|----|-------|
| `backend-health.spec.ts` | AC1 | No | 2 |
| `auth-enforcement.spec.ts` | AC2 | No | 4 |
| `frontend-spa.spec.ts` | AC3 | No | 4 |
| `database-connectivity.spec.ts` | AC4 | Yes | 2 |
| `signed-url.spec.ts` | AC5 | Partial | 3 |
| `sse-endpoint.spec.ts` | AC6 | Partial | 3 |
| **Total** | | | **18** |

Unauthenticated tests (~11) always run. Authenticated tests (~7) are automatically skipped when `SMOKE_AUTH_TOKEN` is not set.

## Manual Checklist

For the full end-to-end evaluation workflow walkthrough (AC7), see [`MANUAL_CHECKLIST.md`](./MANUAL_CHECKLIST.md).
