# Coding Conventions

**Analysis Date:** 2026-03-16

## Naming Patterns

**Files:**
- Components: PascalCase (`DeleteEvaluationDialog.tsx`, `SendMailDialog.tsx`)
- Utilities/helpers: camelCase (`renderTranslatable.ts`, `firebaseAuthService.ts`)
- Services: camelCase with Service suffix (`authService.ts`)
- Modules/features: lowercase with hyphens for directories (`app/modules/evaluations/`, `app/modules/auth/`)
- Test files: Same name as source + `.test.ts(x)` suffix (`App.test.tsx`, `test_parser.py`)

**Functions:**
- Frontend: camelCase (`handleOpenChange`, `renderTranslatable`, `useAuth`)
- Backend Python: snake_case (`app_exception_handler`, `list_evaluations`, `_build_skip_reason`)
- React hooks: camelCase with `use` prefix (`useAuth`, `useTranslation`, `useCalculator`)

**Variables:**
- Frontend TypeScript: camelCase (`brandName`, `confirmInput`, `isDeleting`)
- Backend Python: snake_case (`upload_id`, `brand_id`, `calculator_type`)
- Boolean prefixes: `is` or `has` (`isMatch`, `isDeleting`, `hasPointerCapture`, `_has_total_products`)

**Types:**
- Frontend: PascalCase (`AuthContextType`, `DeleteEvaluationDialogProps`, `TranslatableText`)
- Interfaces: PascalCase with `Props` suffix for component props (`DeleteEvaluationDialogProps`)
- Pydantic models (backend): PascalCase (`Settings`, `AppException`, `TranslatableTextSchema`)

## Code Style

**Formatting:**
- Frontend: Vite + ESLint + TypeScript strict mode
- Backend: Python 3.14+ with type hints on all functions
- Line length: No explicit limit configured, but code observed at reasonable lengths

**Linting:**
- Frontend ESLint: Uses recommended configs for ESLint, TypeScript-ESLint, React hooks, and React refresh
- No Prettier config found; formatting is ESLint-based
- Backend: Uses ruff (dev dependency in pyproject.toml)
- TypeScript strict mode enabled with:
  - `strict: true`
  - `noUnusedLocals: true`
  - `noUnusedParameters: true`
  - `noFallthroughCasesInSwitch: true`
  - `noUncheckedSideEffectImports: true`

## Import Organization

**Order:**
1. External libraries (React, Vitest, etc.)
2. Relative imports from `@/` alias or local paths
3. Type imports separated (TypeScript `type` keyword)

**Example (Frontend):**
```typescript
import { useState } from 'react';
import { Copy, ClipboardCheck } from 'lucide-react';
import type { AuthContextType } from '../types';
import { firebaseAuthService } from '../services/firebaseAuthService';
```

**Example (Backend):**
```python
import logging
from datetime import date
from typing import Any, Literal
from asyncpg import Connection
from app.core.exceptions import AppException
from app.db.queries import evaluations as eval_queries
```

**Path Aliases:**
- Frontend: `@/*` maps to `./src/*` (defined in `tsconfig.json`)
- Backend: No path aliases; direct imports from `app/` package root

## Error Handling

**Frontend Patterns:**
- Toast notifications for user-facing errors (`toast.error('message')`)
- Console errors logged via `console.error()`
- Mock Firebase errors in tests with `MockFirebaseError` class

**Backend Patterns:**
- Custom exception hierarchy: `AppException` (base) → `AuthException`, `SyncException`, `UploadException`, `CalculatorException`
- Each exception has: `code` (string identifier), `detail` (message), `status_code` (HTTP status)
- Centralized exception handler middleware (`app_exception_handler`) returns JSON with code, detail, timestamp
- Exceptions logged with context: code, detail, request path, method
- Service functions raise typed exceptions (e.g., `UploadException` with code `"UPLOAD_PARSE_FAILED"`)

**Example (Backend):**
```python
if not file_type:
    raise UploadException(
        code="UPLOAD_INVALID_FORMAT",
        detail="Unknown file type",
        status_code=400
    )
```

## Logging

**Frontend:**
- Uses console methods (not a dedicated logger)
- Toast library (`sonner`) for user notifications

**Backend:**
- `logging` module with logger per file: `logger = logging.getLogger(__name__)`
- Structured logs: `logger.error("msg", var1, var2)`
- Log level configured at app startup: `logging.basicConfig(level=logging.INFO)`
- Exception logging includes context (code, detail, path, method)

## Comments

**When to Comment:**
- Top-level docstrings on modules, classes, functions (shown in all reviewed files)
- Inline comments for non-obvious logic (e.g., "Startup", "Shutdown" in lifespan context manager)
- Comments explaining workarounds (e.g., "The hook is tightly coupled to this context...")

**JSDoc/TSDoc:**
- Docstrings used for functions: triple quotes in Python, comment blocks in TypeScript
- Example in `config.py`: `"""Application settings loaded from environment variables."""`
- Example in `renderTranslatable.ts`: multi-line function docs explaining behavior

**ESLint rule override comment:**
```typescript
// eslint-disable-next-line react-refresh/only-export-components
export const useAuth = () => { ... }
```

## Function Design

**Size:**
- Most functions are 5-30 lines
- Service functions handle orchestration and delegation (longer but decomposed)
- Utility functions are small, focused (renderTranslatable is 9 lines)

**Parameters:**
- Named parameters with type annotations mandatory
- Backend: All parameters typed (see `list_evaluations(*, conn: Connection, page: int, ...): EvaluationListResponse`)
- Frontend: Props passed as destructured object with interface type
- Optional parameters use `?` in TypeScript, `| None` in Python

**Return Values:**
- Async functions return awaitable types: `Promise<T>` (frontend), `Coroutine` (backend)
- Typed return annotations: `-> EvaluationListResponse`, `-> dict[str, str]`
- Services return domain-specific schemas/responses

**Example (Frontend Context Hook):**
```typescript
export const useAuth = () => {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};
```

**Example (Backend Async Service):**
```typescript
async def list_evaluations(
    *,
    conn: Connection,
    page: int,
    limit: int,
) -> EvaluationListResponse:
    """Return a paginated list of evaluations..."""
    limit, offset = paginate(page, limit)
    rows = await eval_queries.list_evaluations(conn, limit=limit, offset=offset)
    ...
```

## Module Design

**Exports:**
- Frontend: Named exports with `export function ComponentName() {}` or `export const useHook = () => {}`
- Components re-export from UI library barrel files (e.g., `card.tsx` exports `Card`, `CardContent`)
- No default exports observed; prefer named exports for consistency

**Barrel Files:**
- Frontend uses barrel files for UI components: `@/components/ui/` exports primitives
- Backend modules use barrel files: `app/modules/[feature]/__init__.py` for public API

**Example (Frontend):**
```typescript
// card.tsx
export { Card, CardContent, ... } from "@/ui/primitives"

// Component usage
import { Card, CardContent } from '@/components/ui/card';
```

**Example (Backend):**
```python
# app/modules/auth/__init__.py
# May re-export public symbols

# Usage
from app.modules.auth.router import router
from app.modules.auth.schemas import LoginRequest
```

## Frontend-Specific Conventions

**React Component Structure:**
```typescript
interface ComponentProps {
  prop1: Type;
  prop2?: OptionalType;
}

export function ComponentName({ prop1, prop2 }: ComponentProps) {
  const [state, setState] = useState<Type>(initial);

  const handleAction = () => { /* ... */ };

  return <JSX />;
}
```

**Hook Patterns:**
- Context hooks validate context exists (throw Error if not provided)
- Dependencies properly managed in useEffect
- Async operations in useEffect with cleanup functions

**Tailwind CSS:**
- Used for styling with Vite plugin integration
- Classes directly in JSX: `className="space-y-4 py-2"`
- Responsive prefixes: `md:`, `lg:`, etc. available

## Backend-Specific Conventions

**Async Programming:**
- FastAPI with async handlers: `async def` for route handlers
- asyncpg for database connections
- pytest-asyncio for async test execution (`asyncio_mode = "auto"`)

**Dependency Injection:**
- Services accept dependencies as parameters (e.g., `conn: Connection`)
- Modules use factory pattern or dependency containers
- Settings injected via `settings` singleton from `app.config`

**Database Queries:**
- Queries isolated in `app/db/queries/` modules by domain
- Example: `evaluations.py`, `brands.py`, `calculator_results.py`
- Query functions are async and accept connection: `async def list_evaluations(conn: Connection, ...) -> list[dict]`

**Schemas (Pydantic):**
- Input/output schemas in `schemas.py` per module
- Response schemas match API response structure
- Validation handled by Pydantic

---

*Convention analysis: 2026-03-16*
