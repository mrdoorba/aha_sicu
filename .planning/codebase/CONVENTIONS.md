# Coding Conventions

**Analysis Date:** 2026-03-06

## Naming Patterns

**Files (Frontend):**
- Pages: PascalCase with `Page` suffix — `BrandsPage.tsx`, `LoginPage.tsx`, `EvaluationDetailPage.tsx`
- Components: PascalCase — `EvaluationHeader.tsx`, `FileUploadSlot.tsx`, `SectionNav.tsx`
- Hooks: camelCase with `use` prefix — `useBrands.ts`, `useAutoSaveForm.ts`, `useCalculator.ts`
- Test files: colocated, same name + `.test` suffix — `useBrands.ts` -> (no test yet), `useAutoSaveForm.ts` -> `useAutoSaveForm.test.ts`
- UI components (shadcn/ui): kebab-case — `card.tsx`, `radio-group.tsx`, `select.tsx`
- Utilities: camelCase — `utils.ts`, `categoryMap.ts`, `verdictCounts.ts`
- Config/services: camelCase — `apiClient.ts`

**Files (Backend):**
- Modules: snake_case — `router.py`, `service.py`, `schemas.py`
- Tests: `test_` prefix — `test_brands.py`, `test_scoring.py`, `test_parser.py`
- All Python files use snake_case throughout

**Functions (Frontend):**
- camelCase for all functions and hooks: `useBrands()`, `getCurrentUser()`, `buildManualData()`
- React components use PascalCase: `LoginPage`, `EvaluationHeader`
- Render helpers in tests use camelCase: `renderLoginPage()`, `renderBrandsPage()`

**Functions (Backend):**
- snake_case for all functions: `get_brands_paginated()`, `get_current_user()`, `calculate_score()`
- Async functions: use `async def` throughout (FastAPI pattern)
- Private/internal functions: underscore prefix — `_parse_json()`, `_compute_g68()`, `_score_ads()`

**Variables (Frontend):**
- camelCase: `queryClient`, `mockLogin`, `capturedRequest`
- Constants: UPPER_SNAKE_CASE — `BRAND_ID`, `BRANDS_RESPONSE`, `EMPTY_MANUAL_DATA`, `AUTH_HEADERS`
- Mock variables: `mock` prefix — `mockUseBrands`, `mockClientPOST`

**Variables (Backend):**
- snake_case: `token_data`, `brand_id`, `mock_conn`
- Constants: UPPER_SNAKE_CASE — `AUTH_HEADERS`, `MOCK_USER`, `SAMPLE_BRANDS`

**Types (Frontend):**
- Interfaces: PascalCase, no `I` prefix — `BrandListItem`, `BrandListResponse`, `AuthContextType`
- Type exports colocated with hooks: `export type { AutoCalcError }` in `useCalculator.ts`
- API response types defined inline in `apiClient.ts` paths interface

**Types (Backend):**
- Pydantic models: PascalCase — `BrandListItem`, `BrandDetailResponse`, `BrandListResponse`
- Type hints on all function signatures using Python 3.10+ syntax: `str | None`, `dict[str, Any]`

## Code Style

**Formatting (Frontend):**
- No Prettier config detected — uses ESLint for style
- Single quotes for imports (TypeScript convention)
- 2-space indentation (standard Vite/React default)
- Semicolons: not enforced (mixed usage, leaning toward no semicolons in some files)

**Formatting (Backend):**
- Ruff for linting and formatting
- 4-space indentation (Python standard)
- Double quotes for strings

**Linting (Frontend):**
- ESLint 9 with flat config at `frontend/eslint.config.js`
- `@eslint/js` recommended rules
- `typescript-eslint` recommended rules
- `react-hooks` recommended rules (enforces rules of hooks)
- `react-refresh` Vite plugin rules
- No custom rule overrides — uses defaults

**Linting (Backend):**
- Ruff (`>=0.11.0`) — configured via dev dependencies in `backend/pyproject.toml`
- Run with `uv run ruff check .`

**TypeScript (Frontend):**
- Strict mode enabled in `frontend/tsconfig.app.json`
- `noUnusedLocals: true`, `noUnusedParameters: true`
- `noFallthroughCasesInSwitch: true`
- `verbatimModuleSyntax: true` — requires explicit `type` imports
- Target: ES2022
- Module: ESNext with bundler resolution

## Import Organization

**Order (Frontend):**
1. React/framework imports (`react`, `react-dom`, `react-router-dom`)
2. Third-party libraries (`@tanstack/react-query`, `firebase/*`, `vitest`)
3. Internal absolute imports using `@/*` alias (`@/components/*`, `@/hooks/*`)
4. Relative imports (`../services/apiClient`, `./LoginPage`)

**Path Aliases (Frontend):**
- `@/*` maps to `./src/*` — configured in `frontend/tsconfig.json` and `frontend/vite.config.ts`
- In practice, relative imports are used more frequently than `@/` aliases

**Order (Backend):**
1. Standard library (`logging`, `math`, `json`)
2. Third-party (`fastapi`, `pydantic`, `polars`)
3. Internal (`app.core.*`, `app.db.*`, `app.modules.*`)

## Error Handling

**Backend Patterns:**
- Custom exception hierarchy rooted in `AppException` at `backend/app/core/exceptions.py`
- Domain-specific subclasses: `AuthException` (401), `SyncException` (500), `UploadException` (400), `CalculatorException` (400)
- All exceptions carry structured `code` + `detail` fields
- Global exception handler in `backend/app/core/middleware.py` converts to JSON: `{"code": "...", "detail": "...", "timestamp": "..."}`
- Raise pattern: `raise AppException(code="BRAND_NOT_FOUND", detail="Brand not found", status_code=404)`

**Frontend Patterns:**
- API client uses openapi-fetch `{ data, error }` destructuring pattern
- Hooks throw on error: `if (error) throw new Error('Failed to fetch brands')`
- Auth errors caught with `FirebaseError` type checking (`error.code === 'auth/invalid-credential'`)
- Server errors (HTTP 500) dispatch custom DOM event: `window.dispatchEvent(new CustomEvent('api-server-error'))`
- Context guards: `if (!context) throw new Error('useAuth must be used within an AuthProvider')`

## Logging

**Backend:** Python `logging` module
- Module-level logger: `logger = logging.getLogger(__name__)`
- Structured log format: `"%(levelname)s: %(name)s: %(message)s"` configured in `backend/app/main.py`
- Log levels: `logger.info()` for auth events, `logger.error()` for exceptions, `logger.debug()` for fallback paths, `logger.warning()` for security rejections

**Frontend:** `console` (no logging framework)
- No structured logging detected

## Comments

**When to Comment:**
- Module-level docstrings on all Python files: `"""Brand service for querying brand data."""`
- Function docstrings with Args/Returns/Raises sections (Google style) on backend service functions
- Inline comments for non-obvious logic: `# 0.5% -- pass (<1%)`
- Section dividers in test files using `# ---- Section Name ----` pattern
- ESLint disable comments with explanation: `// eslint-disable-next-line react-refresh/only-export-components`

**JSDoc/TSDoc:**
- Not used — TypeScript types serve as documentation
- Inline `// Keep in sync with apiClient.ts` comments for cross-file dependencies

## Function Design

**Size:**
- Backend service functions are short (10-30 lines typical)
- Router handlers are thin wrappers (1-5 lines of logic)
- Calculators can be larger but use internal helpers with `_` prefix

**Parameters (Backend):**
- Use keyword arguments with defaults: `page: int = 1, limit: int = 20`
- FastAPI Query/Depends for router parameters
- Return Pydantic models from services

**Parameters (Frontend):**
- Hooks accept primitive parameters: `useBrands(page, limit, search)`
- Complex hooks accept options objects: `useAutoSaveForm({ brandId, categoryType, initialData })`
- Render helpers in tests accept props objects matching component interfaces

**Return Values (Frontend):**
- Hooks return TanStack Query result objects: `{ data, isLoading, error }`
- Custom hooks return state + handlers: `{ manualData, handleFieldChange, triggerSave, saveStatus }`
- API client functions return `{ data, error }` from openapi-fetch

## Module Design

**Exports (Frontend):**
- Named exports for components: `export const LoginPage = () => { ... }`
- Named exports for hooks: `export function useBrands(...) { ... }`
- Default export for API client singleton: `export default client`
- Type exports: `export type { AutoCalcError }`, `export interface BrandListItem { ... }`

**Exports (Backend):**
- No `__init__.py` barrel files — direct imports from modules
- Router instances: `router = APIRouter(prefix="/api/v1/brands", tags=["brands"])`
- Service functions imported directly: `from app.modules.brands.service import get_brands_paginated`

**Barrel Files:**
- Not used in frontend or backend — all imports are direct file references

## Backend Module Structure

Each backend module at `backend/app/modules/{module}/` follows a consistent three-file pattern:
- `router.py` — FastAPI route definitions (thin, delegates to service)
- `service.py` — Business logic (async functions, uses db queries)
- `schemas.py` — Pydantic models for request/response validation

## Frontend Component Patterns

**Page Components** at `frontend/src/pages/`:
- Compose hooks and UI components
- Handle routing params
- Named export: `export const BrandsPage = () => { ... }`

**Feature Components** at `frontend/src/components/{feature}/`:
- Domain-specific UI (evaluation forms, brand cards, etc.)
- Receive data via props, not hooks directly (where practical)

**UI Components** at `frontend/src/components/ui/`:
- shadcn/ui-based primitives (Radix UI + Tailwind)
- Use `cn()` utility from `frontend/src/lib/utils.ts` for class merging
- `class-variance-authority` for variant patterns

**Hooks** at `frontend/src/hooks/`:
- Wrap TanStack Query `useQuery`/`useMutation` calls
- Define response interfaces alongside the hook
- One hook file per API domain: `useBrands.ts`, `useSync.ts`, `useUpload.ts`

**API Client** at `frontend/src/services/apiClient.ts`:
- Single `openapi-fetch` client with inline `paths` interface
- Auth middleware injects Firebase token automatically
- Server error middleware dispatches DOM events for 500s

---

*Convention analysis: 2026-03-06*
