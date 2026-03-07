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

**Example:**
```
Add bulk CSV import for product listings

A new door opens — products may now arrive in waves of fifty thousand.
Adds POST /api/v1/products/import with chunked processing.

Author: Mr. Door
```
---

## Code Style & Conventions

### General Principles

Prioritize: simplicity, robustness, performance, correctness. Avoid over-engineering.

### Backend

- Type hints on all function signatures
- Stay consistent with existing patterns unless they're clearly suboptimal — then improve and flag the change

### Frontend

- TypeScript strict mode
- Stay consistent with existing patterns unless they're clearly suboptimal — then improve and flag the change
- Test files colocated with source (`*.test.tsx`)

### Infrastructure

- Stay consistent with existing patterns unless they're clearly suboptimal — then improve and flag the change
