# SOLID Principles Refactoring — Design Document

**Date:** 2026-03-10
**Scope:** Full-stack (backend + frontend)
**Approach:** Safe, incremental refactoring — no behavior changes

---

## Guiding Principles

1. **Extract, don't rewrite** — move existing code into new modules/components, don't rewrite logic
2. **Tests must pass at every step** — run the full test suite after each change
3. **One logical change per commit** — each commit is independently safe and revertable
4. **No API changes** — request/response contracts remain identical
5. **No new features** — pure structural improvement

---

## Refactoring Plan

### Phase 1: Backend — Single Responsibility Fixes

#### 1A. Split `calculators/scoring.py` (1829 lines → ~6 files)

Extract into `calculators/scoring/` package:
- `models.py` — `RowScore`, `CategoryScore`, `ScoringResult` dataclasses
- `helpers.py` — formatting, safe access, rule extraction utilities
- `rules.py` — `DEFAULT_RULES` dict and rule lookup functions
- `categories/` — one module per category scorer (`operational.py`, `business.py`, etc.)
- `messages.py` — per-category message generation functions
- `calculator.py` — main `calculate_score` orchestration function
- `__init__.py` — re-export `calculate_score` so all existing imports keep working

**Safety:** Re-export from `__init__.py` ensures zero import breakage. Run tests after each extraction.

#### 1B. Extract `upload/service.py` god function

Split `process_upload` into composed steps:
- Extract `_validate_upload(conn, upload_id, brand_id)` — validation logic
- Extract `_download_and_parse(conn, upload_row, file_type)` — file I/O + parsing
- Extract `_store_and_trigger(conn, brand_id, file_type, parsed_data, user_id)` — DB write + calculator trigger
- Keep `process_upload` as the orchestrator calling these three

**Safety:** All new functions are private to the same module. No public API changes.

#### 1C. Move business logic out of `evaluations/router.py`

Move calculator DB queries from router endpoints into `evaluations/service.py`:
- `get_calculator_results(brand_id)` → service function
- `get_calculator_status(brand_id)` → service function
- `run_all_calculators(brand_id)` → service function

**Safety:** Router calls service instead of DB directly. Same HTTP behavior.

#### 1D. Extract `sync/service.py` sheet logic

Extract `_sync_vp_sheet` and `_sync_meeting_sheet` as separate private functions from the 161-line `run_sync`. Keep `run_sync` as orchestrator.

**Safety:** Private function extraction within same module.

### Phase 2: Backend — Open/Closed Improvements

#### 2A. Calculator registry in `calculators/engine.py`

Replace hard-coded dicts with a registry pattern:
```python
CALCULATOR_REGISTRY: dict[str, CalculatorConfig] = {
    "ads_keyword": CalculatorConfig(
        required_files=["ads_keyword"],
        required_manual=["ads"],
        runner=run_ads_keyword_calculator,
    ),
    ...
}
```

Single source of truth instead of 3 separate dicts. Adding a calculator = one registry entry.

**Safety:** Same runtime behavior, just consolidated configuration.

#### 2B. Strategy pattern for file parsing in `upload/service.py`

Replace `if ZIP/CSV/XLSX` branches with a parser registry:
```python
PARSERS: dict[str, Callable] = {
    "csv": parse_csv,
    "xlsx": parse_excel,
    "zip": parse_zip,
}
```

**Safety:** Same parsers, same behavior, just dispatch via dict lookup.

### Phase 3: Backend — Dependency Inversion

#### 3A. Make `db` injectable via FastAPI dependency

Create a `get_db` dependency that returns the connection, making it mockable:
```python
async def get_db_connection():
    async with db.connection() as conn:
        yield conn
```

Services receive `conn` from router via `Depends(get_db_connection)` instead of importing `db` directly.

**Safety:** Incremental — migrate one service at a time. Existing tests continue working.

### Phase 4: Frontend — Single Responsibility Fixes

#### 4A. Extract `EvaluationPage.tsx` concerns

- Extract `useEvaluationOrchestrator(brandId)` hook — combines brand fetch, evaluation state, auto-save, scoring, calculator results
- Extract `buildSavePayload()` utility — payload construction from `handleSaveEvaluation`
- Page becomes a thin shell: hook + layout

**Safety:** Same render output. Hook returns same values page currently computes inline.

#### 4B. Split `EvaluationSections.tsx` props

- Group props into focused interfaces: `FormProps`, `ScoringProps`, `SaveProps`, `StatusProps`
- `EvaluationSectionsProps` composes these groups
- No render changes — just type-level organization for now

**Safety:** TypeScript-only change. Zero runtime impact.

#### 4C. Split `formConfig.ts`

- `types.ts` — interfaces (`ManualData`, `OperationalData`, etc.)
- `defaults.ts` — `EMPTY_MANUAL_DATA`
- `fields.ts` — field definition arrays
- `utils.ts` — `formatIDR`, `parseIDR`, `generateMonthLabels`, `computeSectionProgress`
- `formConfig.ts` — re-exports everything for backward compatibility

**Safety:** Re-export barrel file ensures zero import breakage.

#### 4D. Extract `useAutoSaveForm.ts` merge logic

- Extract `mergeManualData(serverData, overrides)` to a utility
- Extract debounce logic to `useDebounce` hook (if not already available)

**Safety:** Pure extraction, same behavior.

### Phase 5: Frontend — Dependency Inversion

#### 5A. Abstract Firebase auth

- Create `src/services/authService.ts` interface:
  ```typescript
  interface AuthService {
    getToken(): Promise<string | null>;
    subscribe(cb: (user: User | null) => void): () => void;
    login(email: string, password: string): Promise<void>;
    logout(): Promise<void>;
  }
  ```
- Create `src/services/firebaseAuthService.ts` — concrete implementation wrapping existing Firebase calls
- Update `AuthContext.tsx` and `apiClient.ts` to use the abstraction

**Safety:** Same Firebase calls underneath. Abstraction layer is additive.

---

## What We're NOT Doing

- No new features or endpoints
- No database schema changes
- No dependency upgrades
- No LSP fixes (low severity, high risk of subtle breakage)
- No route configuration refactor in `App.tsx` (low severity)
- No `AuthContext` interface segregation split (over-engineering for current app size)

---

## Verification Strategy

- Run `cd backend && uv run pytest` after every backend change
- Run `cd frontend && npm run test:run` after every frontend change
- Run `cd frontend && npm run build` to catch TypeScript errors
- Each commit is atomic and revertable
