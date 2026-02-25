## 1. Remove Backend SSE Infrastructure

- [x] 1.1 Remove `sync_broadcaster.broadcast()` calls from `app/modules/sync/service.py` (3 call sites: sync start, completion, failure)
- [x] 1.2 Remove `sync_broadcaster.broadcast()` call from `app/modules/evaluations/service.py` (1 call site: new evaluation)
- [x] 1.3 Delete `app/services/event_broadcaster.py`
- [x] 1.4 Delete `app/modules/events/router.py`
- [x] 1.5 Remove events router registration from `app/main.py` (import and `include_router`)
- [x] 1.6 Remove `sse-starlette` from `pyproject.toml` dependencies and run `uv lock`

## 2. Remove Backend SSE Tests

- [x] 2.1 Delete `backend/tests/unit/events/test_event_broadcaster.py`
- [x] 2.2 Remove broadcast-related assertions from `backend/tests/integration/api/test_evaluation_save_broadcast.py` (delete file if only testing broadcast)
- [x] 2.3 Remove `sync_broadcaster` mock/patch from `backend/tests/unit/sync/test_service.py`

## 3. Frontend: Replace useSSE with Adaptive Polling

- [x] 3.1 Update `useSync.ts`: change `refetchInterval` from `60_000` to an adaptive function — 3s when `in_progress`, 30s otherwise
- [x] 3.2 Add `refetchInterval: 30_000` to evaluation list query for cross-user updates
- [x] 3.3 Delete `frontend/src/hooks/useSSE.ts`
- [x] 3.4 Delete `frontend/src/hooks/useSSE.test.ts`

## 4. Frontend: Update SyncStatus Component

- [x] 4.1 Remove `useSSE` import and call from `SyncStatus.tsx`
- [x] 4.2 Remove connection state UI block (Live/Connecting/Reconnecting/Disconnected/Offline indicators) from `SyncStatus.tsx`
- [x] 4.3 Update `SyncStatus.test.tsx` — remove SSE mock and connection state tests
- [x] 4.4 Update `BrandsPage.test.tsx` — remove `useSSE` mock
- [x] 4.5 Update `EvaluationPage.test.tsx` — remove `useSSE` mock

## 5. CI/CD: Enable On-Demand CPU

- [x] 5.1 Add `flags: --cpu-throttling` to the `deploy-cloudrun` step in `.github/workflows/deploy-backend.yml` for dev environment

## 6. Verify

- [x] 6.1 Run backend tests: `uv run pytest -v`
- [x] 6.2 Run backend lint: `uv run ruff check .`
- [x] 6.3 Run frontend tests: `npx vitest run`
- [x] 6.4 Run frontend lint and typecheck: `npm run lint && npx tsc --noEmit`
