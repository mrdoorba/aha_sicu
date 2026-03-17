# Knowledge Base

## Worktree Testing Setup

When running tests from a git worktree (`.gsd/worktrees/M001/`), the backend venv lives in the main repo at `/Users/mac/HT/Project/aha_sicu/backend/.venv/`. Run tests from the worktree directory with `PYTHONPATH=backend` and the main repo's Python:

```bash
cd /Users/mac/HT/Project/aha_sicu/.gsd/worktrees/M001
PYTHONPATH=backend /Users/mac/HT/Project/aha_sicu/backend/.venv/bin/python -m pytest backend/tests/... -x
```

The `--timeout` flag is not available (pytest-timeout not installed).

## Pre-existing Test Failure

`backend/tests/unit/calculators/test_ads_keyword.py::TestSheet2BottomThresholdVariants::test_en_bottom_min_cost_50k` — fails with `assert 'Ad Above 50K' in ''`. Unrelated to scoring changes.

## Migration Template Drift Test

`TestMigrationTemplatesDrift` in `test_scoring.py` replays migrations 012→019→020→021→027 to build effective DB state and compares against DEFAULT_RULES. Any new migration that modifies message templates must:
1. Be added to the replay chain in `_build_effective_db_templates()`
2. Expose an `_apply_patches(rules, forward)` function importable from the migration module

## Scoring Message Marketplace Pattern

Currency codes in scoring messages are injected via `{currency}` template placeholder + `_format_message_template(..., currency=currency_code)`. The formatting function `_fmt_currency` only formats the number (comma separator); it does NOT prepend the currency code. The currency code comes from `MARKETPLACE_CURRENCY.get(marketplace, "IDR")`.

For conclusion text (`_compute_g66`), THB marketplace uses raw formatted numbers while IDR uses `/1_000_000` with `juta` suffix. This is a display convention difference, not a formatting difference.

## Worktree ↔ Main Repo Code Divergence

Git worktrees (`.gsd/worktrees/M001/`) are separate checkouts on their own branches. If a previous task executor makes code changes in the worktree but only commits documentation files, the production code changes will be lost to the main repo (develop branch). Always verify that the auto-commit captured actual code changes, not just `.gsd/` files. If code is only in the worktree as uncommitted modifications, copy it to the main repo before running tests.

## S01 Wiring Test Assertion Style

The service.py `generate_score` function passes `marketplace` as a **positional** arg (not keyword) to `get_rules_by_template_and_marketplace`. Mock `assert_called_once_with` must match the calling convention exactly — `(conn, "default", "TH")` not `(conn, "default", marketplace="TH")`.
