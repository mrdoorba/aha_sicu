# Testing Patterns

**Analysis Date:** 2026-03-06

## Test Framework

### Frontend

**Runner:**
- Vitest 4.x
- Config: `frontend/vite.config.ts` (test section)
- Environment: jsdom
- Globals: enabled (no need to import `describe`, `it`, `expect` — though tests do import them explicitly from vitest)

**Assertion Library:**
- Vitest built-in (`expect`)
- `@testing-library/jest-dom` for DOM matchers (`toBeInTheDocument`, `toBeDisabled`, `toHaveAttribute`)

**Setup File:** `frontend/src/test/setup.ts`
- Imports `@testing-library/jest-dom`
- Mocks Firebase (`firebase/app`, `firebase/auth`) globally
- Mocks `IntersectionObserver` for jsdom
- Polyfills pointer/scroll APIs for Radix UI components

**Run Commands:**
```bash
npx vitest              # Watch mode
npx vitest run          # Run all tests (CI)
npm run test            # Watch mode (via package.json)
npm run test:run        # Run all tests (via package.json)
```

### Backend

**Runner:**
- pytest 8.x with pytest-asyncio
- Config: `backend/pyproject.toml` `[tool.pytest.ini_options]`
- `asyncio_mode = "auto"` — async tests run without `@pytest.mark.asyncio` (though some tests still include it)
- Test paths: `backend/tests/`

**Assertion Library:**
- Python built-in `assert`

**HTTP Client:**
- Integration tests: FastAPI `TestClient` (synchronous, wraps ASGI)
- Health check test: `httpx.AsyncClient` with `ASGITransport`

**Run Commands:**
```bash
cd backend && uv run pytest -v         # Run all tests
cd backend && uv run pytest tests/unit  # Unit tests only
cd backend && uv run ruff check .       # Lint check
```

## Test File Organization

### Frontend

**Location:** Colocated with source files

**Naming:** `{source}.test.{ts,tsx}`

**Structure:**
```
frontend/src/
├── services/
│   ├── apiClient.ts
│   └── apiClient.test.ts
├── hooks/
│   ├── useAutoSaveForm.ts
│   ├── useAutoSaveForm.test.ts
│   ├── useCalculator.ts
│   ├── useCalculator.test.ts
│   ├── useUpload.ts
│   └── useUpload.test.ts
├── pages/
│   ├── LoginPage.tsx
│   ├── LoginPage.test.tsx
│   ├── BrandsPage.tsx
│   ├── BrandsPage.test.tsx
│   ├── DashboardPage.tsx
│   ├── DashboardPage.test.tsx
│   ├── EvaluationPage.tsx
│   ├── EvaluationPage.test.tsx
│   ├── EvaluationDetailPage.tsx
│   ├── EvaluationDetailPage.test.tsx
│   ├── AccountsPage.tsx
│   └── AccountsPage.test.tsx
├── components/
│   ├── ui/
│   │   ├── card.tsx
│   │   └── card.test.tsx
│   ├── evaluation/
│   │   ├── EvaluationHeader.tsx
│   │   ├── EvaluationHeader.test.tsx
│   │   ├── FileUploadSection.tsx
│   │   ├── FileUploadSection.test.tsx
│   │   ├── FileUploadSlot.tsx
│   │   ├── FileUploadSlot.test.tsx
│   │   ├── SaveButton.test.tsx
│   │   └── SectionNav.test.tsx
│   └── layout/
│       ├── Header.tsx
│       ├── Header.test.tsx
│       ├── Sidebar.tsx
│       └── Sidebar.test.tsx
└── test/
    └── setup.ts
```

### Backend

**Location:** Separate `tests/` directory mirroring app structure

**Naming:** `test_{module}.py`

**Structure:**
```
backend/tests/
├── conftest.py              # Shared fixtures (TestClient)
├── test_main.py             # Health check
├── integration/
│   └── api/
│       ├── conftest.py      # TestClient fixture
│       ├── test_accounts.py
│       ├── test_auth.py
│       ├── test_brands.py
│       ├── test_brands_detail.py
│       ├── test_calculators.py
│       ├── test_delete_evaluation.py
│       ├── test_evaluation_detail.py
│       ├── test_evaluation_list.py
│       ├── test_evaluations.py
│       ├── test_grouped_evaluations.py
│       ├── test_rules.py
│       ├── test_rules_update.py
│       ├── test_save_evaluation.py
│       ├── test_scoring.py
│       ├── test_sync.py
│       ├── test_sync_trigger.py
│       └── test_upload.py
└── unit/
    ├── conftest.py           # Shared helpers (make_excel_bytes)
    ├── accounts/
    │   └── test_queries.py
    ├── calculators/
    │   ├── test_ads_keyword.py
    │   ├── test_discount.py
    │   ├── test_engine.py
    │   ├── test_scoring.py
    │   └── test_top_sku.py
    ├── core/
    │   └── test_oidc.py
    ├── sync/
    │   ├── test_service.py
    │   ├── test_sheets_client.py
    │   ├── test_sync_schemas.py
    │   └── test_sync_status_queries.py
    ├── test_calculator_service_helpers.py
    ├── test_ensure_dict.py
    ├── test_evaluation_queries.py
    ├── test_parser.py
    ├── test_security.py
    └── test_zip_handler.py
```

## Test Structure

### Frontend — Page/Component Tests

**Suite Organization:**
```typescript
import { render, screen, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { BrowserRouter } from 'react-router-dom';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { describe, it, expect, vi, beforeEach } from 'vitest';
import { BrandsPage } from './BrandsPage';

// Mock hooks at module level
const mockUseBrands = vi.fn();
vi.mock('../hooks/useBrands', () => ({
  useBrands: (...args: unknown[]) => mockUseBrands(...args),
}));

// QueryClient for TanStack Query context
const queryClient = new QueryClient({
  defaultOptions: { queries: { retry: false } },
});

// Render helper wrapping with providers
const renderBrandsPage = () => {
  return render(
    <QueryClientProvider client={queryClient}>
      <BrowserRouter>
        <BrandsPage />
      </BrowserRouter>
    </QueryClientProvider>
  );
};

describe('BrandsPage', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it('renders brand data in table', () => {
    mockUseBrands.mockReturnValue({ data: BRANDS_RESPONSE, isLoading: false });
    renderBrandsPage();
    expect(screen.getByText('Brand ABC')).toBeInTheDocument();
  });
});
```

### Frontend — Hook Tests

**Suite Organization:**
```typescript
import { renderHook, act } from '@testing-library/react';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest';
import React from 'react';

// Mock API client
const mockClientPOST = vi.fn();
vi.mock('../services/apiClient', () => ({
  default: {
    POST: (...args: unknown[]) => mockClientPOST(...args),
    GET: vi.fn(),
  },
}));

import { useRunCalculator } from './useCalculator';

let queryClient: QueryClient;

function createWrapper() {
  return ({ children }: { children: React.ReactNode }) =>
    React.createElement(QueryClientProvider, { client: queryClient }, children);
}

describe('useRunCalculator', () => {
  beforeEach(() => {
    queryClient = new QueryClient({ defaultOptions: { queries: { retry: false } } });
  });

  afterEach(() => {
    vi.restoreAllMocks();
    queryClient.clear();
  });

  it('clears auto-calc error on successful run', async () => {
    mockClientPOST.mockResolvedValue({ data: {...}, error: null });
    const { result } = renderHook(
      () => useRunCalculator(BRAND_ID, 'ads_keyword'),
      { wrapper: createWrapper() },
    );
    await act(async () => { await result.current.mutateAsync(); });
    // assertions...
  });
});
```

### Backend — Unit Tests

**Suite Organization:**
```python
"""Unit tests for file parser module."""

import polars as pl
import pytest

from app.core.exceptions import UploadException
from app.modules.upload.parser import parse_csv, validate_columns

def test_parse_csv_valid():
    csv_bytes = _shopee_csv("col_a,col_b", ["1,hello", "2,world"])
    df, lang = parse_csv(csv_bytes)
    assert df.shape == (2, 2)

def test_parse_csv_invalid():
    with pytest.raises(UploadException) as exc:
        parse_csv(b"")
    assert exc.value.code == "UPLOAD_PARSE_ERROR"
```

### Backend — Integration Tests

**Suite Organization:**
```python
"""Integration tests for brands API endpoints."""

from unittest.mock import AsyncMock, patch

AUTH_HEADERS = {"Authorization": "Bearer valid-token"}
MOCK_USER = {"id": 1, "firebase_uid": "test-uid", "email": "test@example.com", "role": "member", ...}

def test_brands_without_token(client):
    """Test GET /api/v1/brands returns 401 without Authorization header."""
    response = client.get("/api/v1/brands")
    assert response.status_code == 401
    assert response.json()["code"] == "AUTH_TOKEN_MISSING"

def test_brands_returns_paginated_response(client):
    with (
        patch("app.core.dependencies.verify_firebase_token") as mock_verify,
        patch("app.core.dependencies.db") as mock_db,
        ...
    ):
        mock_verify.return_value = {"uid": "test-uid", "email": "test@example.com"}
        mock_conn = AsyncMock()
        mock_db.connection.return_value.__aenter__.return_value = mock_conn
        ...
        response = client.get("/api/v1/brands", headers=AUTH_HEADERS)
        assert response.status_code == 200
```

**Patterns:**
- `beforeEach`: `vi.clearAllMocks()` (frontend), mock reset
- `afterEach`: `vi.restoreAllMocks()`, `queryClient.clear()`, `vi.useRealTimers()`
- Backend fixtures via `conftest.py`: `client` fixture returns `TestClient(app)`
- Frontend: explicit `vi.useFakeTimers()` / `vi.useRealTimers()` for debounce/timer tests

## Mocking

### Frontend

**Framework:** Vitest `vi.mock()` and `vi.fn()`

**Module Mocking Pattern:**
```typescript
// 1. Declare mock function
const mockUseBrands = vi.fn();

// 2. Mock module (hoisted automatically by vitest)
vi.mock('../hooks/useBrands', () => ({
  useBrands: (...args: unknown[]) => mockUseBrands(...args),
}));

// 3. Configure in test
mockUseBrands.mockReturnValue({ data: response, isLoading: false });
```

**API Client Mocking Pattern:**
```typescript
const mockClientPOST = vi.fn();
vi.mock('../services/apiClient', () => ({
  default: {
    POST: (...args: unknown[]) => mockClientPOST(...args),
    GET: vi.fn(),
  },
}));
```

**Firebase Auth Mocking:**
- Globally mocked in `frontend/src/test/setup.ts`
- Per-test auth context: `vi.mock('../context/AuthContext', () => ({ useAuth: () => ({...}) }))`

**Fetch Mocking (for apiClient tests):**
```typescript
global.fetch = vi.fn().mockImplementation((input: Request) => {
  capturedRequest = input;
  return Promise.resolve(new Response(JSON.stringify(data), { status: 200, headers: { 'Content-Type': 'application/json' } }));
});
```

**Dynamic Import for Module Re-import:**
```typescript
// Used in apiClient.test.ts to get fresh module with mocked fetch
const { getCurrentUser } = await import('./apiClient');
```

**What to Mock (Frontend):**
- Hooks that call APIs (`useBrands`, `useSync`, `useCalculator`)
- Auth context (`useAuth`)
- Firebase modules (globally in setup.ts)
- `global.fetch` when testing the API client itself
- `XMLHttpRequest` when testing upload hooks
- Browser APIs: `IntersectionObserver`, pointer capture, `scrollIntoView`

**What NOT to Mock (Frontend):**
- React rendering — use `@testing-library/react`
- Router — wrap with `BrowserRouter` or `MemoryRouter`
- TanStack Query — wrap with real `QueryClientProvider` (with `retry: false`)
- Pure utility functions — test directly

### Backend

**Framework:** `unittest.mock` (`patch`, `AsyncMock`)

**Integration Test Mocking Pattern:**
```python
def test_endpoint(client):
    with (
        patch("app.core.dependencies.verify_firebase_token") as mock_verify,
        patch("app.core.dependencies.db") as mock_db,
        patch("app.core.dependencies.user_queries") as mock_user_queries,
    ):
        mock_verify.return_value = {"uid": "test-uid", "email": "test@example.com"}
        mock_conn = AsyncMock()
        mock_db.connection.return_value.__aenter__.return_value = mock_conn
        mock_user_queries.get_user_by_firebase_uid = AsyncMock(return_value=MOCK_USER)
        ...
```

**What to Mock (Backend):**
- Firebase token verification (`app.core.dependencies.verify_firebase_token`)
- Database connections and queries (`app.core.dependencies.db`, `app.modules.*.service.db`)
- User queries for auth context (`app.core.dependencies.user_queries`)

**What NOT to Mock (Backend):**
- Pure business logic (calculators, parsers, scoring) — test directly with real data
- Pydantic models — test serialization directly
- FastAPI app — use `TestClient` against real app instance

## Fixtures and Factories

### Frontend

**Test Data:**
```typescript
// Inline constants at top of test file
const BRAND_ID = 1;
const BRANDS_RESPONSE = {
  items: [
    { id: 1, brand_name: 'Brand ABC', raw_data: {...}, updated_at: '...', meeting_raw_data: {...} },
  ],
  total: 2, page: 1, limit: 20, pages: 1,
};

// Typed test data
const SAMPLE_BRAND: BrandDetail = { id: 1, brand_name: 'Test Brand', ... };
```

**Location:** Inline in test files — no shared fixture files for frontend.

### Backend

**Shared Fixtures:**
- `backend/tests/conftest.py`: `client` fixture (`TestClient(app)`)
- `backend/tests/integration/api/conftest.py`: `client` fixture (same)
- `backend/tests/unit/conftest.py`: `make_excel_bytes()` helper for creating Excel test data

**pytest Fixtures:**
```python
@pytest.fixture
def full_manual_data():
    """Complete manual data for a typical store evaluation."""
    return {
        "operational": { "unfulfilledOrderRate": 0.5, ... },
        "business": { "salesMonth0": 200_000_000, ... },
        ...
    }
```

**Constants:** Module-level `AUTH_HEADERS`, `MOCK_USER`, `SAMPLE_BRANDS` dictionaries in integration test files.

## Coverage

**Requirements:** None enforced — no coverage thresholds configured.

**View Coverage:**
```bash
cd frontend && npx vitest run --coverage
cd backend && uv run pytest --cov=app
```

## Test Types

**Unit Tests (Frontend):**
- Pure function testing: `buildManualData()`, `mergeWithOverrides()` in `frontend/src/hooks/useAutoSaveForm.test.ts`
- UI component rendering: `card.test.tsx` tests CSS class output
- Hook behavior with `renderHook`: timer debouncing, state transitions

**Unit Tests (Backend):**
- Calculator logic: `backend/tests/unit/calculators/test_scoring.py` (extensive, tests scoring formulas)
- Parser validation: `backend/tests/unit/test_parser.py` (CSV/Excel parsing)
- Security: `backend/tests/unit/test_security.py`
- Sync schemas/queries: `backend/tests/unit/sync/`

**Integration Tests (Frontend):**
- Page-level rendering with mocked hooks: verify full page renders correctly
- User interaction flows: form submission, search, pagination
- Use `@testing-library/user-event` for realistic user interactions

**Integration Tests (Backend):**
- API endpoint testing via `TestClient` at `backend/tests/integration/api/`
- Tests both auth (401) and happy path with mocked dependencies
- Verifies response status codes, JSON structure, and database query arguments

**E2E Tests:**
- Smoke tests exist at `smoke-tests/` (separate from main test suites)
- No Playwright/Cypress detected

## Common Patterns

**Async Testing (Frontend):**
```typescript
// Async hook mutation
await act(async () => {
  await result.current.mutateAsync();
});

// Waiting for UI updates
await waitFor(() => {
  expect(screen.getByText('Brand ABC')).toBeInTheDocument();
});
```

**Timer Testing (Frontend):**
```typescript
beforeEach(() => { vi.useFakeTimers(); });
afterEach(() => { vi.useRealTimers(); });

// Advance timers
act(() => { vi.advanceTimersByTime(500); });
await act(async () => { await vi.advanceTimersByTimeAsync(5_000); });
await act(async () => { await vi.runAllTimersAsync(); });
```

**Error Testing (Frontend):**
```typescript
// Firebase error
const firebaseError = new FirebaseError('auth/invalid-credential', 'Invalid credentials');
mockLogin.mockRejectedValueOnce(firebaseError);

// API error
await expect(getCurrentUser()).rejects.toMatchObject(errorResponse);
```

**Error Testing (Backend):**
```python
with pytest.raises(UploadException) as exc:
    parse_csv(b"")
assert exc.value.code == "UPLOAD_PARSE_ERROR"
```

**Async Testing (Backend):**
```python
@pytest.mark.asyncio
async def test_health_check():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.get("/health")
    assert response.status_code == 200
```

**User Interaction Testing (Frontend):**
```typescript
const user = userEvent.setup();
await user.type(screen.getByLabelText(/email/i), 'test@example.com');
await user.click(screen.getByRole('button', { name: /masuk/i }));
```

**Provider Wrapping (Frontend):**
- Pages need: `QueryClientProvider` + `BrowserRouter` (or `MemoryRouter` for route params)
- Hooks with queries need: `QueryClientProvider` via `createWrapper()`
- Auth-dependent components need: `vi.mock('../context/AuthContext')`

## TypeScript Test Configuration

Test files are excluded from the main `tsconfig.app.json` build and have their own config:

**`frontend/tsconfig.test.json`:**
- Extends `tsconfig.app.json`
- Adds types: `vitest/globals`, `@testing-library/jest-dom`, `node`
- Includes: `src/**/*.test.ts`, `src/**/*.test.tsx`, `src/test/setup.ts`

---

*Testing analysis: 2026-03-06*
