# AHA SICU — Smoke Tests

Minimal API-only smoke tests for verifying backend deployments in CI. Uses Playwright's `APIRequestContext` — **no browser binaries required**.

## Setup

```bash
cd smoke-tests
npm install
```

## Environment Variables

| Variable | Required | Description |
|----------|----------|-------------|
| `SMOKE_BACKEND_URL` | Yes | Cloud Run backend URL (e.g., `https://aha-coms-sicu-dev-api-xxx.run.app`) |

### Getting `SMOKE_BACKEND_URL`

```bash
gcloud run services describe aha-coms-sicu-dev-api \
  --region=asia-southeast2 \
  --format="value(status.url)"
```

## Running Tests

```bash
# Run the same backend smoke checks used by CI
SMOKE_BACKEND_URL="https://..." \
npm run test:ci

# Run a single smoke lane
SMOKE_BACKEND_URL="https://..." npm run test:health
SMOKE_BACKEND_URL="https://..." npm run test:auth
```

## Test Coverage

| Test File | AC | Auth Required | Tests |
|-----------|----|----|-------|
| `backend-health.spec.ts` | AC1 | No | 2 |
| `auth-enforcement.spec.ts` | AC2 | No | 4 |
| **Total** | | | **6** |

These are the only smoke tests currently exercised by the deploy workflow in `.github/workflows/_deploy-backend.yml`.
