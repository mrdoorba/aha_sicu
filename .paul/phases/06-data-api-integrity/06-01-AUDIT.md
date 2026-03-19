# Enterprise Plan Audit Report

**Plan:** .paul/phases/06-data-api-integrity/06-01-PLAN.md
**Audited:** 2026-03-19
**Verdict:** Conditionally acceptable (accepted after fixes applied)

---

## 1. Executive Verdict

**Conditionally acceptable.** The plan correctly identifies two real AEGIS findings and proposes a sound architectural fix (transaction wrapping + unnest batch). However, the original plan contained a correctness bug that would have surfaced at runtime: PostgreSQL's `INSERT...ON CONFLICT DO UPDATE` cannot affect the same row twice in a single statement. If Google Sheets data contains duplicate brand names (which is plausible — spreadsheets commonly have duplicate entries), the batch upsert would fail with a hard error. This has been fixed.

After applying 2 must-have and 3 strongly-recommended upgrades, I would approve this plan for production.

## 2. What Is Solid

- **Transaction-per-sheet architecture**: Correct granularity. VP and Meeting sheets are independent sync units — atomic per sheet is the right boundary. All-or-nothing across both sheets would be overly coupled.
- **Unnest array approach**: Correct choice over `executemany()`. asyncpg's executemany sends N round-trips; unnest sends one. This is well-understood PostgreSQL pattern.
- **Pre-filter before DB**: Moving validation outside the transaction reduces lock hold time and separates concerns correctly.
- **Boundary protection**: Explicit protection of migrations, router, sheets_client, and existing query functions. No scope creep risk.
- **Existing function preservation**: Keeping `upsert_brand_data` intact prevents downstream breakage in other code paths.

## 3. Enterprise Gaps Identified

### GAP-1: Duplicate brand_name causes PostgreSQL hard error (CRITICAL)
PostgreSQL raises `"ON CONFLICT DO UPDATE command cannot affect row a second time"` when the same conflict key appears multiple times in a single INSERT statement. Google Sheets data commonly contains duplicate rows. Without deduplication, the batch upsert fails entirely — worse than the current row-by-row approach which would simply overwrite.

### GAP-2: AC-2 contradicts implementation approach
AC-2 specified "RETURNING clause confirms the upserted count" but Task 1 explicitly uses `conn.execute()` status string parsing (no RETURNING). The acceptance criterion would fail its own verification.

### GAP-3: Return type underspecified
Task 1 said "Return the result status string" without specifying how to extract the count. Callers would receive `"INSERT 0 100"` instead of `100`, forcing string parsing at every call site.

### GAP-4: Zero observability in new code path
Phase 4 established structured JSON logging with request correlation. The new batch upsert path — the most performance-sensitive database operation in the sync pipeline — had no logging. No way to measure batch performance, detect degradation, or trace sync timing in production.

### GAP-5: No test coverage for deduplication path
The deduplication logic (GAP-1 fix) is a critical correctness path with no test. If someone later refactors the dedup to "optimize" it, there's no regression gate.

## 4. Upgrades Applied to Plan

### Must-Have (Release-Blocking)

| # | Finding | Plan Section Modified | Change Applied |
|---|---------|----------------------|----------------|
| 1 | Duplicate brand_name in batch causes PostgreSQL error | AC (added AC-4), Task 2 action (added dedup step), Task 2 avoid list, Task 3 (added test 6) | Added deduplication requirement: last occurrence wins. Added AC-4 with Given/When/Then. Added explicit avoid directive. Added dedup test. |
| 2 | AC-2 contradicts implementation | AC-2 | Changed "RETURNING clause confirms count" → "parsed status string confirms count as integer" |

### Strongly Recommended

| # | Finding | Plan Section Modified | Change Applied |
|---|---------|----------------------|----------------|
| 1 | Return type underspecified | Task 1 action | Changed signature to accept parallel arrays, added explicit `int(status.split()[-1])` parsing pattern, added avoid directive for raw strings |
| 2 | Batch operation logging | Task 2 action (step 7) | Added structured logging requirement: table name, batch size, skipped count, duration |
| 3 | No test for dedup or int parsing | Task 3 action | Added test 7: verify status string "INSERT 0 50" → int 50 |

### Deferred (Can Safely Defer)

| # | Finding | Rationale for Deferral |
|---|---------|----------------------|
| 1 | Integration test against real PostgreSQL for batch_upsert | Unit tests + existing sync integration tests provide adequate coverage. Dedicated DB integration test can be added if batch bugs surface operationally. |
| 2 | Per-row error diagnostics on batch failure | All-or-nothing error reporting is acceptable for this scope. If operational need for granular diagnostics arises, a fallback-to-row-by-row-on-failure strategy can be added later. |

## 5. Audit & Compliance Readiness

**Audit evidence:** The plan produces testable artifacts — unit tests with specific assertions, grep-verifiable transaction usage, and structured logs that persist in Cloud Logging. Adequate for post-incident reconstruction.

**Silent failure prevention:** Transaction rollback prevents the most dangerous silent failure (partial sync). Structured logging ensures batch outcomes are observable. The dedup fix prevents a failure mode that would have been intermittent and hard to reproduce.

**Ownership:** Clear — sync pipeline is a single service module with explicit boundaries. No cross-cutting concerns introduced.

**Weakness:** No explicit metric or alert for sync duration regression. Acceptable for current scale but worth noting.

## 6. Final Release Bar

**Must be true before shipping:**
- All 7 unit tests pass (including dedup and int parsing tests)
- `_sync_sheet_to_table` uses `conn.transaction()` (grep-verifiable)
- Batch upsert deduplicates input by brand_name before INSERT
- `batch_upsert_brand_data` returns `int`, not `str`
- Structured log line emitted for each batch operation

**Remaining risks if shipped as-is (after fixes):**
- No integration test against real PostgreSQL for the unnest pattern specifically (low risk — pattern is well-established)
- Batch failure loses per-row error granularity (acceptable tradeoff — atomicity is more valuable)

**Sign-off:** After applying the 5 upgrades above, I would sign my name to this plan.

---

**Summary:** Applied 2 must-have + 3 strongly-recommended upgrades. Deferred 2 items.
**Plan status:** Updated and ready for APPLY

---
*Audit performed by PAUL Enterprise Audit Workflow*
*Audit template version: 1.0*
