# Project Retrospective

*A living document updated after each milestone. Lessons feed forward into future planning.*

## Milestone: v1.0 — Dashboard Email Report

**Shipped:** 2026-03-06
**Phases:** 3 | **Plans:** 7 | **Tasks:** 15

### What Was Built
- SMTP email engine with CID inline images and categorized error handling
- Table-based HTML email template with 6 content sections and Indonesian localization
- Complete send flow UI: DashboardHeader button → dialog → chart capture → API → SMTP → feedback
- Multi-recipient To/CC/BCC with Gmail-style chip input
- In-dialog email preview with sandboxed iframe
- Custom note support rendered as styled card in email body

### What Worked
- Backend-first phase ordering: SMTP + template + router all testable without UI — fast iteration
- Single-day execution (~31 min across 7 plans) — tight scope and clear requirements enabled velocity
- TDD approach in Phase 2: RED → GREEN cycle for SendEmailDialog caught issues early
- Audit passed cleanly: 21/21 requirements, 12/12 integrations, 3/3 E2E flows

### What Was Inefficient
- ROADMAP.md phase checkboxes not consistently updated (Phase 1/2 still showed unchecked despite completion)
- Nyquist validation only partially compliant across all 3 phases — validation strategy docs added late
- Phase 1 plan count discrepancy (ROADMAP said "2/3 plans executed" but all 3 completed)

### Patterns Established
- CID images for email, data URIs for preview — dual-mode `*_src` template params
- Custom lightweight components over library deps when interaction is simple (EmailChipInput)
- BCC via `to_addrs` only, never as header — correct SMTP privacy pattern
- `asyncio.to_thread` for wrapping sync SMTP in async FastAPI context

### Key Lessons
1. Backend-first sequencing pays off — each phase had a stable foundation to build on
2. Chart capture (html-to-image) requires explicit white background and forwardRef on wrapper div, not chart container
3. Preview endpoint needs different image strategy than send (data URIs vs CID) — plan for this from the start
4. Email HTML is table-based with inline CSS — media queries are progressive enhancement only

### Cost Observations
- Model mix: primarily opus
- Sessions: ~4 sessions across planning + execution
- Notable: All 7 plans executed in ~31 minutes total — average ~4 min/plan

---

## Cross-Milestone Trends

### Process Evolution

| Milestone | Phases | Plans | Key Change |
|-----------|--------|-------|------------|
| v1.0 | 3 | 7 | First milestone — established backend-first pattern |

### Cumulative Quality

| Milestone | Tests | Tech Debt | Requirements |
|-----------|-------|-----------|-------------|
| v1.0 | 237+ (80 BE Phase 1 + 15 FE Phase 2 + 142 Phase 3) | 1 low-severity | 21/21 satisfied |

### Top Lessons (Verified Across Milestones)

1. Backend-first phase ordering enables fast, testable iteration
2. Tight scope + clear requirements = single-day execution
