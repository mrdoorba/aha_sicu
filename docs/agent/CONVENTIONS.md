# Code Conventions

Rules and patterns for writing code that fits the AHA SICU codebase. Every example below is extracted from real source files.

---

## Python Conventions (Backend)

### File Naming

- All Python files use `snake_case`.
- Each backend module lives in `backend/app/modules/<name>/` and contains at minimum: `router.py`, `service.py`, `schemas.py`.
- Database query files live in `backend/app/db/queries/<name>.py`.

### Module Docstrings

Every Python file starts with a module-level docstring:

```python
"""Brand service for querying brand data."""
```

### Import Order

stdlib, then third-party, then local (`app.*`). Separate each group with a blank line:

```python
import math

from app.core.exceptions import AppException
from app.db.connection import db
from app.db.queries import brands as brand_queries
from app.modules.brands.schemas import BrandDetailResponse, BrandListItem, BrandListResponse
```

### Type Hints

Type hints on ALL function signatures -- parameters AND return types. Use modern union syntax (`X | None`, not `Optional[X]`):

```python
async def get_brands_paginated(
    page: int = 1,
    limit: int = 20,
    search: str | None = None,
) -> BrandListResponse:
```

### Async Everywhere

All route handlers and service functions use `async def`. No synchronous database calls:

```python
@router.get("", response_model=BrandListResponse)
async def list_brands(
    page: int = Query(1, ge=1, description="Page number"),
    limit: int = Query(20, ge=1, le=100, description="Items per page"),
    search: str | None = Query(None, max_length=200, description="Search by brand name"),
    current_user: dict = Depends(get_current_user),
) -> BrandListResponse:
```

### Router Structure

- Prefix: `/api/v1/<resource>` on the `APIRouter`.
- Use `response_model` on every route.
- Auth via `Depends(get_current_user)`.
- Role-based access via `Depends(require_role("leader", "admin"))`.

```python
router = APIRouter(prefix="/api/v1/brands", tags=["brands"])

@router.get("/{brand_id}", response_model=BrandDetailResponse)
async def get_brand(
    brand_id: int,
    current_user: dict = Depends(get_current_user),
) -> BrandDetailResponse:
    """Get a single brand by ID with meeting data enrichment."""
    return await get_brand_detail(brand_id=brand_id)
```

### Service Layer

- Services are plain async functions, not classes.
- Services import query modules and call them, passing the connection.
- Services construct and return Pydantic response models directly.

```python
async def get_brand_detail(brand_id: int) -> BrandDetailResponse:
    async with db.connection() as conn:
        row = await brand_queries.get_brand_by_id(conn, brand_id)

    if not row:
        raise AppException(
            code="BRAND_NOT_FOUND", detail="Brand not found", status_code=404
        )

    return BrandDetailResponse(**row)
```

### Database Connection Management

Always use the `db` singleton with `async with db.connection() as conn`:

```python
from app.db.connection import db

async with db.connection() as conn:
    rows = await brand_queries.get_brands_with_meeting(
        conn, limit=limit, offset=offset, search=search
    )
```

### Database Queries (asyncpg, No ORM)

- All SQL is parameterized using `$1`, `$2`, etc. (asyncpg positional params).
- Query functions accept `conn: Connection` as the first argument.
- Return `dict(row)` or `[dict(row) for row in rows]`.
- Use `conn.fetch()` for multiple rows, `conn.fetchrow()` for single row, `conn.fetchval()` for scalar.
- Validate dynamic table names against an allowlist to prevent SQL injection.

```python
from asyncpg import Connection

async def get_brand_by_id(conn: Connection, brand_id: int) -> dict | None:
    row = await conn.fetchrow(
        """
        SELECT v.id, v.brand_name, v.raw_data, v.updated_at,
               m.raw_data AS meeting_raw_data
        FROM brand_vp_data v
        LEFT JOIN brand_meeting_data m ON v.brand_name = m.brand_name
        WHERE v.id = $1
        """,
        brand_id,
    )
    return dict(row) if row else None
```

When table names must be dynamic, use a `Literal` type and validate against a frozen allowlist:

```python
TableName = Literal["brand_vp_data", "brand_meeting_data"]
_VALID_TABLES: frozenset[str] = frozenset({"brand_vp_data", "brand_meeting_data"})

def _validate_table(table: str) -> str:
    if table not in _VALID_TABLES:
        raise ValueError(f"Invalid table name: {table}")
    return table
```

### Pydantic Schemas

- Models inherit from `BaseModel`.
- Use `field_validator` with `mode="before"` for input coercion (e.g., JSONB parsing).
- Validators are `@classmethod` decorated.

```python
from pydantic import BaseModel, field_validator

class BrandListItem(BaseModel):
    id: int
    brand_name: str
    raw_data: dict[str, Any]
    updated_at: datetime
    meeting_raw_data: dict[str, Any] | None = None

    @field_validator("raw_data", "meeting_raw_data", mode="before")
    @classmethod
    def parse_jsonb(cls, v: Any) -> dict[str, Any] | None:
        return _parse_json(v)
```

Paginated responses follow this shape:

```python
class BrandListResponse(BaseModel):
    items: list[BrandListItem]
    total: int
    page: int
    limit: int
    pages: int
```

### Exception Handling

- Raise specific `AppException` subclasses. Never raise bare `Exception`.
- Each domain has its own exception subclass defined in `app/core/exceptions.py`.
- Exceptions take `code` (string constant), `detail` (human-readable message), and `status_code`.

```python
from app.core.exceptions import AppException

raise AppException(
    code="BRAND_NOT_FOUND", detail="Brand not found", status_code=404
)
```

Existing exception hierarchy:

| Class                | Default Status | Usage                    |
|----------------------|----------------|--------------------------|
| `AppException`       | 400            | Base / generic app error |
| `AuthException`      | 401            | Authentication failures  |
| `SyncException`      | 500            | Sync-related failures    |
| `UploadException`    | 400            | Upload-related failures  |
| `CalculatorException`| 400            | Calculator failures      |

When adding a new domain, add a new subclass to `backend/app/core/exceptions.py`.

---

## TypeScript Conventions (Frontend)

### File Naming

- Components: `PascalCase.tsx` (e.g., `BrandTable.tsx`).
- Hooks: `camelCase` prefixed with `use` (e.g., `useBrands.ts`).
- Tests: colocated, same name with `.test.tsx` or `.test.ts` suffix.
- Services/config: `camelCase.ts` (e.g., `apiClient.ts`).

### Import Order

React/library imports, then local imports. Use relative paths for same-feature imports. Use `@/` path alias for cross-feature imports:

```tsx
import { useState, useEffect } from 'react';
import { Search, ChevronLeft, ChevronRight } from 'lucide-react';
import { useTranslation } from 'react-i18next';
import { BrandTable } from '../components/brands/BrandTable';
import { Input } from '../components/ui/input';
import { useBrands } from '../hooks/useBrands';
```

### Component Pattern

- Arrow function components exported as named exports (not default exports).
- Props defined via an `interface` above the component.
- Destructured props in the function signature.

```tsx
interface BrandTableProps {
  brands: BrandListItem[];
  isLoading: boolean;
}

export const BrandTable = ({ brands, isLoading }: BrandTableProps) => {
  const navigate = useNavigate();
  const { t } = useTranslation();

  return (
    <Table aria-label="Brand list" aria-busy={isLoading}>
      {/* ... */}
    </Table>
  );
};
```

### Pages

- Exported as named `const` (e.g., `export const BrandsPage = () => {}`).
- Compose feature components; keep logic minimal in the page itself.
- Use `useState` for local UI state (search, pagination).

### React Query -- Read Hooks (useQuery)

- One hook per resource/query.
- Export the hook function and relevant TypeScript interfaces from the same file.
- Query keys are arrays: `['brands', page, limit, search]`.
- Use `client.GET(...)` from `apiClient.ts` inside `queryFn`.

```ts
import { useQuery } from '@tanstack/react-query';
import client from '../services/apiClient';

export interface BrandListResponse {
  items: BrandListItem[];
  total: number;
  page: number;
  limit: number;
  pages: number;
}

export function useBrands(page = 1, limit = 20, search = '') {
  return useQuery<BrandListResponse>({
    queryKey: ['brands', page, limit, search],
    queryFn: async () => {
      const { data, error } = await client.GET('/api/v1/brands', {
        params: {
          query: { page, limit, ...(search ? { search } : {}) },
        },
      });
      if (error) throw new Error('Failed to fetch brands');
      return data as BrandListResponse;
    },
  });
}
```

### React Query -- Write Hooks (useMutation)

- Invalidate related query keys in `onSuccess`.
- Throw on error inside `mutationFn`.

```ts
import { useMutation, useQueryClient } from '@tanstack/react-query';
import client from '../services/apiClient';

export function useDeleteEvaluation() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async (evaluationId: number) => {
      const { error } = await client.DELETE(
        '/api/v1/evaluations/{evaluation_id}',
        {
          params: {
            path: { evaluation_id: evaluationId },
          },
        },
      );
      if (error) throw new Error('Failed to delete evaluation');
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['evaluations-grouped'] });
      queryClient.invalidateQueries({ queryKey: ['brand-evaluations'] });
      queryClient.invalidateQueries({ queryKey: ['evaluations'] });
    },
  });
}
```

### API Client (openapi-fetch)

- All endpoint types are defined in the `paths` interface inside `frontend/src/services/apiClient.ts`.
- When adding a new endpoint, add its type definition to the `paths` interface.
- Keep hook response types in sync with the `paths` interface.

### UI Primitives

- Use existing shadcn components from `components/ui/` (Button, Input, Card, Table, Badge, etc.).
- Do NOT create custom UI primitives when shadcn provides one.
- Use `cn()` utility for conditional Tailwind classes.
- Icons come from `lucide-react`.

### Styling

- Tailwind CSS classes only. No custom CSS files.
- Use semantic color tokens: `text-foreground`, `text-muted-foreground`, `bg-muted`, `text-destructive`.
- Responsive/spacing via Tailwind utilities: `p-8`, `mb-6`, `gap-4`, etc.
- Skeleton loading states use `animate-pulse rounded bg-muted` pattern.

### State Management

- Server state: React Query (`useQuery` / `useMutation`). No other server state management.
- Local UI state: `useState`. Keep it minimal and colocated with the component that needs it.
- NO Redux, Zustand, or other global state libraries.

### Internationalization

- All user-visible strings go through `useTranslation()` hook: `t('brands.title')`.
- Never hardcode display strings in JSX.

### Accessibility

- Use `aria-label`, `aria-busy`, `aria-hidden` attributes where appropriate.
- Decorative icons get `aria-hidden="true"`.

### Testing

- Framework: vitest + @testing-library/react.
- Test files colocated with source: `BrandTable.test.tsx` next to `BrandTable.tsx`.
- Import test utilities explicitly:

```tsx
import { render, screen } from '@testing-library/react';
import { describe, it, expect } from 'vitest';
```

- Wrap components that use router in `<BrowserRouter>`:

```tsx
const renderBrandTable = (props: { brands: BrandListItem[]; isLoading: boolean }) => {
  return render(
    <BrowserRouter>
      <BrandTable {...props} />
    </BrowserRouter>
  );
};
```

- Firebase is mocked globally in `frontend/src/test/setup.ts`. Do not re-mock it per test file.
- Test behavior and rendered output, not implementation details.
- Use `screen.getByText()`, `screen.getByRole()`, `screen.queryByText()` for assertions.

---

## File Organization

### Backend

```
backend/app/
  core/               # Shared: exceptions.py, dependencies.py, security.py
  config.py           # Settings (pydantic-settings)
  db/
    connection.py      # DatabasePool singleton
    queries/           # Raw SQL query functions, one file per domain
      brands.py
      users.py
      utils.py         # Shared query helpers (e.g., escape_like)
  modules/
    brands/
      router.py        # FastAPI APIRouter with route handlers
      service.py       # Business logic (async functions)
      schemas.py       # Pydantic request/response models
    evaluations/
      router.py
      service.py
      schemas.py
      ...
```

### Frontend

```
frontend/src/
  components/
    ui/                # shadcn primitives (button, input, table, etc.)
    brands/            # Feature components
      BrandTable.tsx
      BrandTable.test.tsx
    sync/
      SyncStatus.tsx
  hooks/
    useBrands.ts       # One hook file per resource/action
    useSync.ts
  pages/
    BrandsPage.tsx      # Page-level components
  services/
    apiClient.ts        # openapi-fetch client + paths interface
  firebase/
    auth.ts             # Firebase auth helpers
  test/
    setup.ts            # Global test setup (Firebase mocks, polyfills)
```

### Rules

1. **No cross-module imports in backend.** Modules (`app/modules/X`) do not import from other modules (`app/modules/Y`). Shared code lives in `app/core/` or `app/db/`.
2. **Tests are colocated.** `BrandTable.test.tsx` sits next to `BrandTable.tsx`, not in a separate `__tests__` directory.
3. **One hook per file.** Each hook gets its own file in `hooks/`.

---

## Commit Style

- Atomic commits: one logical, self-contained change per commit.
- First line: clear summary of what was done (no metaphor, immediately parseable).
- Optional body: Mr. Door personality flair (Lord of Mysteries reference), context, and WHY.
- Every commit ends with `Author: Mr. Door`.

```
Add bulk CSV import for product listings

A new door opens -- products may now arrive in waves of fifty thousand.
Adds POST /api/v1/products/import with chunked processing.

Author: Mr. Door
```

See `CLAUDE.md` at the project root for the canonical reference.

---

## What NOT to Do

1. **No ORMs.** No SQLAlchemy, no Tortoise, no Django ORM. All database access is parameterized SQL via asyncpg.
2. **No Redux or global state managers.** React Query handles server state; `useState` handles local UI state.
3. **No cross-module imports in backend.** `app/modules/brands/` must not import from `app/modules/evaluations/`.
4. **No custom UI primitives when shadcn provides one.** Check `components/ui/` first.
5. **No bare `try/except` or generic `Exception` catches.** Always catch or raise specific exception types.
6. **No `console.log` in production code.** Use proper error handling and throw errors.
7. **No synchronous database calls.** All DB access is `async/await`.
8. **No `Optional[X]` syntax.** Use `X | None` (modern union syntax).
9. **No default exports in frontend.** Use named exports (`export const`, `export function`). The sole exception is `apiClient.ts` which default-exports the client instance.
10. **No hardcoded display strings in JSX.** All user-visible text goes through `t()` from `react-i18next`.
