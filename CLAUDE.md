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