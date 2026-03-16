# Testing Patterns

**Analysis Date:** 2026-03-16

## Test Framework

**Frontend Runner:**
- **Vitest** 4.0.18
- Config: `frontend/vite.config.ts`
- Environment: jsdom (browser-like)
- Pool: forks (isolated test processes)
- Global test APIs enabled (describe, it, expect without imports)

**Frontend Assertion Library:**
- **Vitest** built-in expect
- **@testing-library/react** (React component testing utilities)
- **@testing-library/jest-dom** (DOM matchers)
- **@testing-library/user-event** (user interaction simulation)

**Backend Runner:**
- **pytest** 8.0+
- Async support: pytest-asyncio 0.24+
- Distribution: pytest-xdist 3.5+
- Config: `backend/pyproject.toml`
  - `asyncio_mode = "auto"` (automatic async fixture detection)
  - `testpaths = ["tests"]`

**Backend Assertion Library:**
- **pytest** assertions (assert statements)
- No explicit mock framework configured; uses `unittest.mock` from stdlib

**Run Commands:**
```bash
# Frontend
npm test              # Watch mode
npm run test:run      # Run once and exit

# Backend
pytest                # Run all tests (discovery from tests/ dir)
pytest -v             # Verbose output
pytest -x             # Stop on first failure
pytest --asyncio-mode=auto  # Explicit async mode (auto by default)
pytest -n auto        # Parallel execution with pytest-xdist
```

## Test File Organization

**Location:**
- Frontend: Co-located with source. Test file path mirrors source path with `.test.ts(x)` suffix.
  - `src/App.tsx` → `src/App.test.tsx`
  - `src/components/ui/card.tsx` → `src/components/ui/card.test.tsx`
  - `src/utils/renderTranslatable.ts` → `src/utils/renderTranslatable.test.ts`

- Backend: Separate `tests/` directory with subdirectories mirroring `app/` structure.
  - `app/modules/upload/parser.py` → `tests/unit/test_parser.py`
  - `app/calculators/engine.py` → `tests/unit/calculators/test_engine.py`
  - `app/core/oidc.py` → `tests/unit/core/test_oidc.py`

**Naming:**
- Frontend: `[ComponentName].test.tsx` or `[functionName].test.ts`
- Backend: `test_[module_name].py` (pytest convention)

**Structure:**
```
frontend/src/
├── components/
│   ├── evaluations/
│   │   ├── SendMailDialog.tsx
│   │   └── SendMailDialog.test.tsx
│   └── ui/
│       ├── card.tsx
│       └── card.test.tsx

backend/tests/
├── unit/
│   ├── test_parser.py
│   ├── test_security.py
│   ├── conftest.py
│   ├── calculators/
│   │   └── test_engine.py
│   └── core/
│       └── test_oidc.py
```

## Test Structure

**Frontend Suite Organization:**
```typescript
import { render, screen, act } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { describe, it, expect, vi, beforeEach } from 'vitest';
import { Component } from './Component';

describe('Component', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it('renders title', () => {
    render(<Component />);
    expect(screen.getByRole('heading', { name: /title/i })).toBeInTheDocument();
  });

  describe('nested describe block', () => {
    it('handles user interaction', async () => {
      const user = userEvent.setup();
      render(<Component />);

      await user.click(screen.getByRole('button'));

      expect(screen.getByText('Expected')).toBeInTheDocument();
    });
  });
});
```

**Setup and Teardown:**
- `beforeEach` clears mocks before each test
- `afterEach` not shown but available if needed
- Setup file at `frontend/src/test/setup.ts` handles global mocks (Firebase, IntersectionObserver, Radix UI APIs)

**Assertion Pattern:**
- One assertion per test (when possible; multiple assertions on same element are acceptable)
- Assertions use `.toBe()`, `.toHaveValue()`, `.toBeInTheDocument()`, `.toContain()`, etc.
- DOM queries prefer `getByRole()` over `getByTestId()` (accessible queries first)

**Example (Frontend AAA pattern):**
```typescript
it('updates [EMAIL TO:] line when PIC email field changes', async () => {
  // Arrange
  const user = userEvent.setup();
  renderDialog();

  // Act
  const picInput = screen.getByLabelText('Email PIC');
  await user.clear(picInput);
  await user.type(picInput, 'new@brand.com');

  // Assert
  const body = screen.getByTestId('mail-body');
  expect(body).toHaveTextContent('[EMAIL TO: new@brand.com]');
});
```

**Backend Suite Organization:**
```python
"""Unit tests for module."""

import pytest
from unittest.mock import AsyncMock, patch

from app.core.exceptions import UploadException
from app.modules.upload.parser import parse_csv

class TestDependencyMaps:
    def test_file_to_calculator_mapping(self):
        """Short description of test."""
        # Arrange
        csv_bytes = _shopee_csv("col_a,col_b", ["1,hello"])

        # Act
        df, lang = parse_csv(csv_bytes)

        # Assert
        assert df.shape == (2, 2)
        assert lang == "id"

    def test_invalid_raises_exception(self):
        """Specific error raised on invalid input."""
        with pytest.raises(UploadException) as exc:
            parse_csv(b"")
        assert exc.value.code == "UPLOAD_PARSE_FAILED"
```

**Patterns:**
- Classes group related tests (TestDependencyMaps, TestDataFlow, etc.)
- Private helper functions prefixed with `_` (e.g., `_make_upload`, `_shopee_csv`)
- Fixtures in `conftest.py` shared across tests

## Mocking

**Frontend Framework:**
- **vitest** built-in mocking with `vi.mock()`, `vi.fn()`, `vi.spyOn()`
- Module-level mocks at top of test file

**Frontend Example:**
```typescript
vi.mock('react-i18next', () => ({
  useTranslation: () => ({
    t: (key: string) => mockTranslations[key] ?? key,
  }),
}));

vi.mock('./context/AuthContext', () => ({
  AuthProvider: ({ children }: { children: React.ReactNode }) => <>{children}</>,
  useAuth: () => ({
    user: null,
    loading: false,
    login: vi.fn(),
    logout: vi.fn(),
  }),
}));
```

**Backend Framework:**
- `unittest.mock.AsyncMock` for async function mocks
- `unittest.mock.patch` for module-level patching
- Example: `vi.spyOn(window, 'open').mockImplementation(() => null)`

**What to Mock:**
- External services (Firebase, HTTP clients, email)
- Context providers and custom hooks
- API calls
- Browser APIs unavailable in jsdom (IntersectionObserver, clipboard, pointer events)

**What NOT to Mock:**
- Utilities and helpers (renderTranslatable, parser functions)
- Pure functions
- Database queries (in integration tests; in unit tests may be mocked)
- Components under test (render them instead)

**Mock Setup in Frontend:**
```typescript
const windowOpen = vi.spyOn(window, 'open').mockImplementation(() => null);
const onOpenChange = vi.fn();

// Use mocks
await user.click(button);
expect(windowOpen).toHaveBeenCalledTimes(1);
expect(onOpenChange).toHaveBeenCalledWith(false);

// Cleanup
windowOpen.mockRestore();
```

## Fixtures and Factories

**Frontend Test Data:**
```typescript
const defaultProps = {
  open: true,
  onOpenChange: vi.fn(),
  brandName: 'Nike Indonesia',
  period: 'Jan 2026',
  emailOutput: 'Score: 78.5',
  brandRawData: {
    email: 'pic@nike.com',
    pic_name: 'Budi Santoso',
    store_link: 'https://shopee.co.id/nike',
    kategori: 'Fashion',
  },
};

const renderDialog = (props = {}) => {
  return render(<SendMailDialog {...defaultProps} {...props} />);
};
```

**Backend Test Data:**
```python
def _make_upload(file_type: str) -> dict:
    return {"file_type": file_type, "id": 1, "brand_id": 1}

def _make_result(calculator_type: str) -> dict:
    return {
        "calculator_type": calculator_type,
        "details": {},
        "output_text": "test",
        "calculated_at": datetime(2026, 2, 11, 10, 0, tzinfo=timezone.utc),
    }

def _shopee_csv(header_line: str, data_lines: list[str] | None = None) -> bytes:
    """Build a Shopee-style CSV with metadata rows."""
    metadata = [
        "Semua Laporan Iklan CPC - Shopee Indonesia",
        "Username,testuser",
        # ... 7 total metadata rows
    ]
    lines = metadata + [header_line] + (data_lines or [])
    return "\n".join(lines).encode()
```

**Location:**
- Frontend: Inline in test file (after imports, before describe blocks)
- Backend: In `conftest.py` as shared fixtures or helper functions in test file

## Coverage

**Requirements:**
- Not explicitly enforced in config (no coverage thresholds in `pyproject.toml`)
- Frontend and backend use default coverage approach (runs but no fail gate)

**View Coverage:**
```bash
# Frontend
npm run test:run -- --coverage

# Backend
pytest --cov=app tests/
```

## Test Types

**Frontend Unit Tests:**
- Component isolation tests
- Scope: Single component or hook behavior
- Approach: render component, simulate user interactions, assert output
- Example: `Card.test.tsx` tests overflow handling in UI component

**Frontend Integration Tests:**
- Multiple component interaction
- Scope: Dialog with forms, state management, mocking
- Approach: render feature, mock external dependencies, test workflows
- Example: `SendMailDialog.test.tsx` tests form submission and email generation

**Frontend E2E Tests:**
- Not present in observed test files
- Would use Playwright, Cypress, or similar
- Framework: Not detected in dependencies

**Backend Unit Tests:**
- Pure function testing
- Scope: Parser functions, calculators, query helpers
- Approach: Call function, assert output
- Example: `test_parser.py` tests CSV parsing with various inputs

**Backend Integration Tests:**
- Database and service interaction
- Scope: Service layer with database
- Approach: Setup data, call service, verify database state and responses
- Not explicitly separated; integration tests live in `tests/unit/` (naming convention)

## Common Patterns

**Frontend Async Testing:**
```typescript
it('async operation completes', async () => {
  const user = userEvent.setup();
  render(<Component />);

  const button = screen.getByRole('button');
  await user.click(button);  // userEvent.setup() returns promise-aware user object

  await expect(screen.findByText('Success')).resolves.toBeInTheDocument();
});
```

**Backend Async Testing:**
```python
@pytest.mark.asyncio
async def test_async_function():
    """Test async service with mocked database."""
    # asyncio_mode="auto" makes this work without @pytest.mark.asyncio in many cases
    result = await list_evaluations(conn=mock_conn, page=1, limit=10)
    assert result.total == 100
```

**Frontend Error Testing:**
```typescript
it('shows error toast on clipboard failure', async () => {
  const user = userEvent.setup();
  vi.spyOn(navigator.clipboard, 'writeText').mockRejectedValue(new Error('Denied'));

  render(<Component />);
  await user.click(screen.getByRole('button'));

  expect(toast.error).toHaveBeenCalledWith('Error message');
});
```

**Backend Error Testing:**
```python
def test_parse_csv_invalid():
    """Invalid CSV raises specific error."""
    with pytest.raises(UploadException) as exc:
        parse_csv(b"")
    assert exc.value.code == "UPLOAD_PARSE_FAILED"
    assert exc.value.status_code == 400
```

**Frontend Describe Nesting:**
```typescript
describe('SendMailDialog', () => {
  it('renders dialog title', () => {
    // Top-level test
  });

  describe('email field updates', () => {
    it('updates when user types', async () => {
      // Nested test
    });
  });
});
```

---

*Testing analysis: 2026-03-16*
