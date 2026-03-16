# GEMINI.md
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

## Test-Driven Development

**Cycle:** Red → Green → Refactor

**Three Rules of TDD:**
1. No production code except to pass a failing test
2. No more test code than sufficient to fail
3. No more production code than sufficient to pass

**Test structure — AAA:** Arrange (setup) → Act (execute) → Assert (verify). One assert per test.

**Naming:** `test_<expected>_when_<condition>` (backend) / `should <expected> when <condition>` (frontend)

---

## SOLID Principles

Apply SOLID where it reduces complexity — not as ritual.

- **S — Single Responsibility:** Each class/module has one reason to change. If a class handles both business logic and persistence, split it.
- **O — Open/Closed:** Extend behavior through new code (new classes, strategies, handlers), not by modifying existing working code. Use abstractions (protocols, interfaces) as extension points.
- **L — Liskov Substitution:** Subtypes must be substitutable for their base types without breaking behavior. If overriding changes the contract, the hierarchy is wrong.
- **I — Interface Segregation:** Prefer small, focused interfaces over fat ones. Clients should not depend on methods they don't use.
- **D — Dependency Inversion:** High-level modules depend on abstractions, not concrete implementations. Inject dependencies; don't instantiate them internally.

**When to apply:** Classes with multiple responsibilities, modules that change for unrelated reasons, or code that's hard to test due to tight coupling. **When to skip:** Simple scripts, one-off utilities, or code that's unlikely to change.

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
