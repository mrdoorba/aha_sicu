# Vitest CI Optimization Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers-extended-cc:executing-plans to implement this plan task-by-task.

**Goal:** Cut frontend test CI time from ~2m 1s to ~25-35s using Vitest sharding and pool optimization.

**Architecture:** Split the single frontend test job into 4 parallel shards using Vitest's built-in `--shard` flag with a GitHub Actions matrix strategy. Switch the worker pool from `threads` to `forks` for better CI performance. Add a merge gate job for clean branch protection.

**Tech Stack:** Vitest 4.x, GitHub Actions matrix strategy, jsdom

---

### Task 0: Add forks pool config to vite.config.ts

**Files:**
- Modify: `frontend/vite.config.ts`

**Step 1: Update vite.config.ts with pool config**

Replace the `test` block in `frontend/vite.config.ts` with:

```ts
test: {
  globals: true,
  environment: 'jsdom',
  setupFiles: './src/test/setup.ts',
  pool: 'forks',
  poolOptions: {
    forks: {
      minForks: 2,
      maxForks: 4,
    },
  },
},
```

**Step 2: Run tests to verify nothing breaks**

Run: `cd frontend && npx vitest run`
Expected: All 62 test files pass, same as before.

**Step 3: Commit**

```bash
git add frontend/vite.config.ts
git commit -m "Switch vitest pool from threads to forks for CI performance"
```

---

### Task 1: Split CI workflow into sharded frontend jobs

**Files:**
- Modify: `.github/workflows/ci.yml`

**Step 1: Replace the frontend job section**

Replace the entire `frontend:` job block in `.github/workflows/ci.yml` with three new jobs. The full file should look like:

```yaml
# Store ICU - CI Workflow
# Runs backend tests + lint and frontend tests + lint + type-check on every PR.
#
# REQUIRED REPOSITORY SETUP:
#   Branch protection rules must be configured on `develop` and `main`:
#     1. Go to Settings → Branches → Add branch protection rule
#     2. Branch name pattern: `develop` (repeat for `main`)
#     3. Enable "Require status checks to pass before merging"
#     4. Add required checks: "Backend Tests & Lint", "Frontend CI"
#     5. Enable "Require branches to be up to date before merging"

name: CI

on:
  pull_request:
    branches: [develop, main]
  workflow_dispatch:
  workflow_call:

jobs:
  backend:
    name: Backend Tests & Lint
    runs-on: ubuntu-latest
    defaults:
      run:
        working-directory: backend

    steps:
      - uses: actions/checkout@v4

      - name: Install uv
        uses: astral-sh/setup-uv@v5
        with:
          version: "latest"
          enable-cache: true

      - name: Set up Python
        run: uv python install 3.14

      - name: Install dependencies
        run: uv sync --all-extras

      - name: Lint
        run: uv run ruff check .

      - name: Run tests
        run: uv run pytest -v -n auto

  frontend-lint:
    name: Frontend Lint & Type Check
    runs-on: ubuntu-latest
    defaults:
      run:
        working-directory: frontend

    steps:
      - uses: actions/checkout@v4

      - name: Setup Node.js
        uses: actions/setup-node@v4
        with:
          node-version: '20'
          cache: 'npm'
          cache-dependency-path: frontend/package-lock.json

      - name: Install dependencies
        run: npm ci

      - name: Lint
        run: npm run lint

      - name: Type check
        run: npx tsc -b --noEmit

  frontend-test:
    name: Frontend Tests (shard ${{ matrix.shard }})
    runs-on: ubuntu-latest
    strategy:
      matrix:
        shard: [1/4, 2/4, 3/4, 4/4]
    defaults:
      run:
        working-directory: frontend

    steps:
      - uses: actions/checkout@v4

      - name: Setup Node.js
        uses: actions/setup-node@v4
        with:
          node-version: '20'
          cache: 'npm'
          cache-dependency-path: frontend/package-lock.json

      - name: Install dependencies
        run: npm ci

      - name: Run tests
        run: npx vitest run --shard=${{ matrix.shard }}

  frontend-gate:
    name: Frontend CI
    runs-on: ubuntu-latest
    if: always()
    needs: [frontend-lint, frontend-test]
    steps:
      - name: Check results
        run: |
          if [ "${{ needs.frontend-lint.result }}" != "success" ] || [ "${{ needs.frontend-test.result }}" != "success" ]; then
            echo "Frontend CI failed"
            exit 1
          fi
```

**Step 2: Verify YAML syntax**

Run: `python3 -c "import yaml; yaml.safe_load(open('.github/workflows/ci.yml'))"`
Expected: No output (valid YAML).

**Step 3: Commit**

```bash
git add .github/workflows/ci.yml
git commit -m "Split frontend CI into sharded test jobs with merge gate"
```

---

### Task 2: Verify sharding works locally

**Step 1: Run shard 1/4**

Run: `cd frontend && npx vitest run --shard=1/4`
Expected: ~15-16 test files pass.

**Step 2: Run shard 2/4**

Run: `npx vitest run --shard=2/4`
Expected: ~15-16 test files pass (different files from shard 1).

**Step 3: Run shard 3/4**

Run: `npx vitest run --shard=3/4`
Expected: ~15-16 test files pass.

**Step 4: Run shard 4/4**

Run: `npx vitest run --shard=4/4`
Expected: ~15-16 test files pass.

**Step 5: Verify total coverage**

Sum up test file counts from all 4 shards. Should equal 62 total.

---

### Task 3: Push, verify CI, update branch protection

**Step 1: Push changes**

Run: `git push`

**Step 2: Trigger CI**

Create a test PR or use `gh workflow run ci.yml` to trigger the CI workflow.

**Step 3: Verify all jobs pass**

Check GitHub Actions — should see:
- Backend Tests & Lint ✓
- Frontend Lint & Type Check ✓
- Frontend Tests (shard 1/4) ✓
- Frontend Tests (shard 2/4) ✓
- Frontend Tests (shard 3/4) ✓
- Frontend Tests (shard 4/4) ✓
- Frontend CI ✓

**Step 4: Update branch protection**

Go to GitHub → Settings → Branches → Edit branch protection rules for `develop` and `main`:
- Remove required check: "Frontend Tests & Lint"
- Add required check: "Frontend CI"

**Step 5: Verify timing improvement**

Compare the wall-clock time for test execution across shards vs. the old single-job run.
Target: each shard ~25-35s, down from 2m 1s total.
