# Vitest CI Optimization Design

## Problem

Frontend tests take ~2m 1s in GitHub Actions, making the total frontend CI ~2m 39s.
Backend CI finishes in 21s. Goal: bring frontend test time as close to backend as possible.

## Root Cause

62 test files run sequentially in a single CI job with jsdom environment.
No parallelization across jobs (unlike backend which uses `pytest -n auto`).

## Approach: Vitest Sharding + Pool Optimization

### 1. CI Workflow Changes

Split current "Frontend Tests & Lint" into:

- **Frontend Lint & Type Check** — single job, runs `npm run lint` + `npx tsc -b --noEmit`
- **Frontend Tests (shard X/4)** — matrix job with 4 shards using `npx vitest run --shard=X/4`
- **Frontend CI** — merge gate job that depends on all above, for branch protection

```yaml
frontend-lint:
  name: Frontend Lint & Type Check
  # runs lint + typecheck

frontend-test:
  name: Frontend Tests (shard ${{ matrix.shard }})
  strategy:
    matrix:
      shard: [1/4, 2/4, 3/4, 4/4]
  steps:
    - run: npx vitest run --shard=${{ matrix.shard }}

frontend-gate:
  name: Frontend CI
  needs: [frontend-lint, frontend-test]
  # empty job, just a merge gate
```

### 2. Vitest Pool Optimization

Switch from default `threads` pool to `forks` in `vite.config.ts`:

```ts
test: {
  globals: true,
  environment: 'jsdom',
  setupFiles: './src/test/setup.ts',
  pool: 'forks',
  poolOptions: {
    forks: { minForks: 2, maxForks: 4 }
  }
}
```

`forks` provides better process isolation and is typically faster in CI where
each fork gets its own jsdom instance without shared-memory overhead.

### 3. Branch Protection Update

Update required status check from "Frontend Tests & Lint" to "Frontend CI" (the merge gate job).

## Expected Result

- Test wall-clock: ~2m 1s → ~25-35s (4 shards running ~15 files each)
- Total frontend CI: ~2m 39s → ~50-60s

## Constraints

- Keep jsdom (no switch to happy-dom)
- Keep lint + typecheck in one job (not worth splitting for 13s savings)

## Files to Change

1. `.github/workflows/ci.yml` — restructure frontend jobs with matrix sharding
2. `frontend/vite.config.ts` — add forks pool config
3. GitHub branch protection settings — update required check name
