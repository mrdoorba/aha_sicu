---
description: BDD Double Loop development workflow — Given-When-Then → Outer test → Inner Red-Green-Refactor → AAA → F.I.R.S.T.
---

# BDD Double Loop Workflow

Use this workflow when implementing any new feature or change. It layers four complementary practices into a single repeatable process.

---

## Phase 1: BDD — Define WHAT to Build

Before writing any code, write **Given-When-Then** scenarios that describe the desired behavior from a user/business perspective.

### Template

```gherkin
Feature: <Feature name>

  Scenario: <Happy path description>
    Given <initial context/state>
    When <action or event>
    Then <expected outcome>

  Scenario: <Edge case or failure path>
    Given <initial context/state>
    When <action or event>
    Then <expected outcome>
```

### Rules
- Collaborate with the user to validate scenarios before proceeding
- Each scenario = one testable behavior, not an implementation detail
- Use domain language (e.g., "selling price", "market price"), not code language (e.g., "the `_fmt_idr` function")
- Store scenarios as comments or docstrings in the outer test file for traceability

---

## Phase 2: Double Loop — Manage the WORKFLOW

### Outer Loop (Acceptance Test)

1. **Write a failing acceptance/integration test** from the BDD scenario
   - Frontend: render the full page/component, assert on visible output
   - Backend: call the top-level calculator/API function, assert on output
   - This test should fail initially — it's the "north star"

2. **Commit the outer test** with message prefix `OUTER RED:`

```
OUTER RED: Add acceptance test for <feature>

<Mr. Door body>

Author: Mr. Door
```

### Inner Loop (Red-Green-Refactor)

For each unit of work needed to make the outer test pass:

3. **RED** — Write a failing unit test for the smallest next piece
4. **GREEN** — Write the minimum code to make it pass
5. **REFACTOR** — Clean up without changing behavior
6. **Repeat** steps 3-5 until the outer acceptance test goes green

### Commit Strategy
- **Atomic commits** per inner cycle or logical batch:
  - `RED: <what tests now expect>`
  - `GREEN: <what source code changed to pass>`
  - `REFACTOR: <what was cleaned up>` (only if there are refactoring changes)
- When the outer test passes: `OUTER GREEN: <feature> acceptance test passes`

---

## Phase 3: AAA — Format Every TEST

Every test function follows **Arrange-Act-Assert**:

```python
def test_currency_displays_idr_with_commas():
    # Arrange — set up inputs and expected state
    sales_value = 244530790

    # Act — execute the behavior under test
    result = format_idr(sales_value)

    # Assert — verify the outcome
    assert result == "244,530,790"
```

```typescript
it('displays IDR with comma separators', () => {
  // Arrange
  render(<CurrencyField value={125000000} onChange={vi.fn()} />);

  // Act (implicit — component renders on mount)

  // Assert
  expect(screen.getByRole('textbox')).toHaveValue('125,000,000');
});
```

### Rules
- One logical assertion per test (multiple `expect` calls are fine if they verify the same behavior)
- If Arrange is complex, extract a helper/factory function
- If Act is implicit (render, mount), add a comment `// Act (implicit)`
- Keep each section visually separated with a blank line or comment

---

## Phase 4: F.I.R.S.T. — Quality Gate Before Commit

Before each commit, mentally verify all tests satisfy:

| Principle | Check | Fail signal |
|-----------|-------|-------------|
| **F**ast | Full suite runs in seconds, not minutes | Tests use real DB, network, or sleep |
| **I**ndependent | Tests pass in any order, no shared state | Test B fails only when Test A runs first |
| **R**epeatable | Same result every run, any environment | Tests depend on system clock, random data, or file system state |
| **S**elf-validating | Pass/fail — no manual inspection needed | You have to read logs or check a DB to know if it worked |
| **T**imely | Written before or alongside the code | Tests added after the feature is "done" |

// turbo-all

### Quick Check Commands

```bash
# Backend
cd backend && uv run pytest -v --tb=short

# Frontend
cd frontend && npx vitest run

# Lint
cd backend && uv run ruff check .
cd frontend && npm run lint
```

---

## Summary Flow

```
  ┌──────────────────────────────────┐
  │  1. Write BDD scenarios          │ ← Given-When-Then
  │     (validate with stakeholder)  │
  └──────────────┬───────────────────┘
                 ▼
  ┌──────────────────────────────────┐
  │  2. Write OUTER failing test     │ ← Acceptance test from BDD
  │     Commit: OUTER RED            │
  └──────────────┬───────────────────┘
                 ▼
  ┌──────────────────────────────────┐
  │  3. INNER LOOP (repeat N times): │
  │     RED   → failing unit test    │
  │     GREEN → make it pass         │
  │     REFACTOR → clean up          │
  │     Commit each cycle            │
  │     (use AAA in every test)      │
  └──────────────┬───────────────────┘
                 ▼
  ┌──────────────────────────────────┐
  │  4. Outer test now PASSES        │
  │     Commit: OUTER GREEN          │
  └──────────────┬───────────────────┘
                 ▼
  ┌──────────────────────────────────┐
  │  5. F.I.R.S.T. quality check     │ ← Pre-commit gate
  │     Fast? Independent? etc.      │
  └──────────────────────────────────┘
```
