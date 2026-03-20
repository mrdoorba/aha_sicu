# CLAUDE.md
## Git Workflow
### Atomic Commits

Each commit is **one logical, self-contained unit of work** — does exactly one thing, leaves the codebase working, and is independently understandable from its message and diff.

### Commit Messages

The first line is a **clear, scannable summary** — no metaphor, immediately parseable. The optional body carries **Subtle Mr. Door** from the Lord of Mysteries series novel flair. Every commit ends with `Author: Mr. Door`.

**Format:**
```
<clear one-line summary — what was done>

<optional Mr. Door body — personality, WHY, context>

Author: Mr. Door
```

**Examples:**
```
Add bulk CSV import for product listings

A new door opens — products may now arrive in waves of fifty thousand.
Adds POST /api/v1/products/import with chunked processing.

Author: Mr. Door
```

```
Fix race condition in WebSocket reconnection logic

Between one heartbeat and the next, two threads reached for the same
lock — and both believed themselves first. Now only one hand turns
the handle. Guards shared state with asyncio.Lock in the reconnect path.

Author: Mr. Door
```
---

## Test-Driven Development

**Cycle:** Red → Green → Refactor. AAA structure: Arrange → Act → Assert. One assert per test.

**Naming:** `test_<expected>_when_<condition>` (backend) / `should <expected> when <condition>` (frontend)

---

## SOLID Principles

Apply SOLID where it reduces complexity — not as ritual. Prefer composition over inheritance.

---

## Code Style & Conventions

### General Principles

Prioritize: simplicity, robustness, performance, correctness. Avoid over-engineering. Stay consistent with existing patterns unless they're clearly suboptimal — then improve and flag the change.

### Backend

- Type hints on all function signatures

### Frontend

- TypeScript strict mode

### Python Tooling

- Use **`uv`** for all Python-related tasks: dependency management, virtual environments, running scripts, and installing packages
- `uv run` to execute scripts, `uv add` / `uv remove` for dependencies, `uv sync` to install, `uv venv` for environments

---

## Running

- Backend tests: `cd backend && uv run pytest tests/ -x`
- Frontend tests: `cd frontend && npm test` (vitest in watch mode) / `npm run test:run` (single run)
- Dev stack: `docker-compose up`
- Backend lint: `cd backend && uv run ruff check .`
- Frontend lint: `cd frontend && npm run lint`

<!-- gitnexus:start -->
# GitNexus — Code Intelligence

This project is indexed by GitNexus as **aha_sicu** (3802 symbols, 8955 relationships, 154 execution flows). Use the GitNexus MCP tools to understand code, assess impact, and navigate safely.

> If any GitNexus tool warns the index is stale, run `npx gitnexus analyze` in terminal first.

## Always Do

- **MUST run impact analysis before editing any symbol.** Before modifying a function, class, or method, run `gitnexus_impact({target: "symbolName", direction: "upstream"})` and report the blast radius (direct callers, affected processes, risk level) to the user.
- **MUST run `gitnexus_detect_changes()` before committing** to verify your changes only affect expected symbols and execution flows.
- **MUST warn the user** if impact analysis returns HIGH or CRITICAL risk before proceeding with edits.
- When exploring unfamiliar code, use `gitnexus_query({query: "concept"})` to find execution flows instead of grepping. It returns process-grouped results ranked by relevance.
- When you need full context on a specific symbol — callers, callees, which execution flows it participates in — use `gitnexus_context({name: "symbolName"})`.

## When Debugging

1. `gitnexus_query({query: "<error or symptom>"})` — find execution flows related to the issue
2. `gitnexus_context({name: "<suspect function>"})` — see all callers, callees, and process participation
3. `READ gitnexus://repo/aha_sicu/process/{processName}` — trace the full execution flow step by step
4. For regressions: `gitnexus_detect_changes({scope: "compare", base_ref: "main"})` — see what your branch changed

## When Refactoring

- **Renaming**: MUST use `gitnexus_rename({symbol_name: "old", new_name: "new", dry_run: true})` first. Review the preview — graph edits are safe, text_search edits need manual review. Then run with `dry_run: false`.
- **Extracting/Splitting**: MUST run `gitnexus_context({name: "target"})` to see all incoming/outgoing refs, then `gitnexus_impact({target: "target", direction: "upstream"})` to find all external callers before moving code.
- After any refactor: run `gitnexus_detect_changes({scope: "all"})` to verify only expected files changed.

## Never Do

- NEVER edit a function, class, or method without first running `gitnexus_impact` on it.
- NEVER ignore HIGH or CRITICAL risk warnings from impact analysis.
- NEVER rename symbols with find-and-replace — use `gitnexus_rename` which understands the call graph.
- NEVER commit changes without running `gitnexus_detect_changes()` to check affected scope.

## Tools Quick Reference

| Tool | When to use | Command |
|------|-------------|---------|
| `query` | Find code by concept | `gitnexus_query({query: "auth validation"})` |
| `context` | 360-degree view of one symbol | `gitnexus_context({name: "validateUser"})` |
| `impact` | Blast radius before editing | `gitnexus_impact({target: "X", direction: "upstream"})` |
| `detect_changes` | Pre-commit scope check | `gitnexus_detect_changes({scope: "staged"})` |
| `rename` | Safe multi-file rename | `gitnexus_rename({symbol_name: "old", new_name: "new", dry_run: true})` |
| `cypher` | Custom graph queries | `gitnexus_cypher({query: "MATCH ..."})` |

## Impact Risk Levels

| Depth | Meaning | Action |
|-------|---------|--------|
| d=1 | WILL BREAK — direct callers/importers | MUST update these |
| d=2 | LIKELY AFFECTED — indirect deps | Should test |
| d=3 | MAY NEED TESTING — transitive | Test if critical path |

## Resources

| Resource | Use for |
|----------|---------|
| `gitnexus://repo/aha_sicu/context` | Codebase overview, check index freshness |
| `gitnexus://repo/aha_sicu/clusters` | All functional areas |
| `gitnexus://repo/aha_sicu/processes` | All execution flows |
| `gitnexus://repo/aha_sicu/process/{name}` | Step-by-step execution trace |

## Self-Check Before Finishing

Before completing any code modification task, verify:
1. `gitnexus_impact` was run for all modified symbols
2. No HIGH/CRITICAL risk warnings were ignored
3. `gitnexus_detect_changes()` confirms changes match expected scope
4. All d=1 (WILL BREAK) dependents were updated

## Keeping the Index Fresh

After committing code changes, the GitNexus index becomes stale. Re-run analyze to update it:

```bash
npx gitnexus analyze
```

If the index previously included embeddings, preserve them by adding `--embeddings`:

```bash
npx gitnexus analyze --embeddings
```

To check whether embeddings exist, inspect `.gitnexus/meta.json` — the `stats.embeddings` field shows the count (0 means no embeddings). **Running analyze without `--embeddings` will delete any previously generated embeddings.**

> Claude Code users: A PostToolUse hook handles this automatically after `git commit` and `git merge`.

## CLI

| Task | Read this skill file |
|------|---------------------|
| Understand architecture / "How does X work?" | `.claude/skills/gitnexus/gitnexus-exploring/SKILL.md` |
| Blast radius / "What breaks if I change X?" | `.claude/skills/gitnexus/gitnexus-impact-analysis/SKILL.md` |
| Trace bugs / "Why is X failing?" | `.claude/skills/gitnexus/gitnexus-debugging/SKILL.md` |
| Rename / extract / split / refactor | `.claude/skills/gitnexus/gitnexus-refactoring/SKILL.md` |
| Tools, resources, schema reference | `.claude/skills/gitnexus/gitnexus-guide/SKILL.md` |
| Index, status, clean, wiki CLI commands | `.claude/skills/gitnexus/gitnexus-cli/SKILL.md` |

<!-- gitnexus:end -->

<!-- aegis:start -->
# AEGIS Guardrails

Derived from AEGIS diagnostic audit (2026-03-19). 136 findings, 39 playbooks.
Full audit: `.aegis/report/AEGIS-REPORT.md` | Playbooks: `.aegis/remediation/playbooks/`

## Security

- When modifying Cloud Run env vars in Terraform, verify `CLOUD_RUN_URL` and `ALLOWED_SCHEDULER_EMAILS` are present. Never remove them without removing the OIDC code path.
- CORS origins must come from `CORS_ORIGINS` env var via `settings.cors_origin_list`. Never hardcode origin URLs in `main.py`.
- When a security feature depends on a config value (allowlist, audience, domain restriction), the empty/missing case must **deny**, not permit. No `if not config: return` in security paths.
- Email recipients must be validated against `EMAIL_ALLOWED_DOMAINS`. Never bypass domain validation.

## Infrastructure

- Terraform backend must be `gcs`, not `local`. Never switch back. If the GCS line is commented out, that is a bug.
- Each environment module must create its own `random_password` and `google_sql_user`. Never pass the same `db_password` to multiple environment modules.
- Every Dockerfile must include a non-root `USER` directive. Pattern: `adduser` → `COPY --chown` → `USER appuser`.

## Data Integrity

- Dynamic SQL `ORDER BY` columns must be validated against a `frozenset` allowlist before f-string interpolation, even if the schema layer also validates.
- Sync functions writing multiple rows must wrap in `async with conn.transaction()`. Never commit rows one-by-one without a wrapping transaction.
- Upload state must be in the `pending_uploads` database table. Never use module-level dicts or in-memory state — Cloud Run instances are ephemeral.

## Observability

- `/health` must verify DB connectivity (`SELECT 1`) and return 503 when unreachable. Never return static `{"status": "healthy"}`.
- Deploy verification in CI must hit `/health` and assert `"status": "healthy"`. Never verify against `/docs`.
- Admin mutations (role changes, deletions, email sends) must call `record_audit_event()`. Never add a mutation endpoint without an audit log call.

## Testing

- Backend tests must run with `--cov`. The `fail_under` threshold in `pyproject.toml` must never decrease — only ratchet upward.
- Frontend API types in `api.generated.ts` must be auto-generated from backend OpenAPI schema. Never hand-edit generated type files.
<!-- aegis:end -->
