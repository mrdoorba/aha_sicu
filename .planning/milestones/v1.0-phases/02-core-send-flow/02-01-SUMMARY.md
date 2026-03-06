---
phase: 02-core-send-flow
plan: 01
subsystem: ui
tags: [react, tanstack-query, html-to-image, i18n, dialog, email]

# Dependency graph
requires:
  - phase: 01-backend-email-engine
    provides: POST /api/v1/email/send endpoint
provides:
  - SendEmailDialog component with chart capture and all feedback states
  - useSendEmail mutation hook for email send API
  - ScoreBreakdownChart forwardRef for html-to-image capture
  - API client typed path for /api/v1/email/send
  - Indonesian translations for email send UI
affects: [02-core-send-flow]

# Tech tracking
tech-stack:
  added: [html-to-image]
  patterns: [forwardRef for chart capture, mutation hook with inline onSuccess]

key-files:
  created:
    - frontend/src/hooks/useSendEmail.ts
    - frontend/src/hooks/useSendEmail.test.ts
    - frontend/src/components/dashboard/SendEmailDialog.tsx
    - frontend/src/components/dashboard/SendEmailDialog.test.tsx
  modified:
    - frontend/src/services/apiClient.ts
    - frontend/src/locales/id.json
    - frontend/src/components/dashboard/ScoreBreakdownChart.tsx
    - frontend/package.json

key-decisions:
  - "forwardRef on chart wrapper div (not ResponsiveContainer) with explicit white background for capture"
  - "Mock path in test must match relative import path from component file"

patterns-established:
  - "SendEmailDialog: mutation hook with inline onSuccess for toast + close"
  - "forwardRef chart capture pattern with html-to-image toPng"

requirements-completed: [SEND-02, SEND-06, SEND-07, SEND-08]

# Metrics
duration: 4min
completed: 2026-03-06
---

# Phase 02 Plan 01: Send Email Dialog Summary

**SendEmailDialog component with html-to-image chart capture, useSendEmail mutation hook, and full feedback states (idle/loading/error/capture-error)**

## Performance

- **Duration:** 4 min
- **Started:** 2026-03-06T07:45:19Z
- **Completed:** 2026-03-06T07:50:00Z
- **Tasks:** 3 (plus 1 TDD RED sub-commit)
- **Files modified:** 8

## Accomplishments
- useSendEmail hook with typed API client path for POST /api/v1/email/send
- ScoreBreakdownChart accepts forwardRef for chart capture with white background
- SendEmailDialog implements all feedback states: idle, loading, error, capture error
- 15 new tests (3 hook + 12 component), all 438 frontend tests pass

## Task Commits

Each task was committed atomically:

1. **Task 1: Install html-to-image, add API path type, i18n keys, and create useSendEmail hook** - `26b7309` (feat)
2. **Task 2: Add forwardRef to ScoreBreakdownChart** - `2311a77` (feat)
3. **Task 3 RED: Add failing tests for SendEmailDialog** - `2882798` (test)
4. **Task 3 GREEN: Create SendEmailDialog with all feedback states** - `e20c055` (feat)

## Files Created/Modified
- `frontend/src/hooks/useSendEmail.ts` - TanStack Query mutation hook for email send API
- `frontend/src/hooks/useSendEmail.test.ts` - 3 tests for the mutation hook
- `frontend/src/components/dashboard/SendEmailDialog.tsx` - Dialog with brand summary, recipient input, chart capture, all feedback states
- `frontend/src/components/dashboard/SendEmailDialog.test.tsx` - 12 tests covering all dialog states
- `frontend/src/services/apiClient.ts` - Added /api/v1/email/send typed path
- `frontend/src/locales/id.json` - 13 Indonesian translation keys for sendEmail
- `frontend/src/components/dashboard/ScoreBreakdownChart.tsx` - Added forwardRef with white background wrapper
- `frontend/package.json` - Added html-to-image dependency

## Decisions Made
- forwardRef placed on chart wrapper div (not ResponsiveContainer) with explicit `backgroundColor: '#ffffff'` style for reliable html-to-image capture
- useSendEmail hook uses inline `onSuccess` callback (not hook-level) since different callers may want different success behavior

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 1 - Bug] Fixed mock path in SendEmailDialog test**
- **Found during:** Task 3 (SendEmailDialog TDD GREEN)
- **Issue:** Mock path `../../../hooks/useSendEmail` was incorrect (3 levels up instead of 2)
- **Fix:** Changed to `../../hooks/useSendEmail` to match the component's import path
- **Files modified:** frontend/src/components/dashboard/SendEmailDialog.test.tsx
- **Verification:** All 12 tests pass after fix
- **Committed in:** e20c055 (Task 3 GREEN commit)

---

**Total deviations:** 1 auto-fixed (1 bug)
**Impact on plan:** Test mock path correction, no scope creep.

## Issues Encountered
None beyond the mock path fix documented above.

## User Setup Required
None - no external service configuration required.

## Next Phase Readiness
- SendEmailDialog is fully functional standalone component ready to be wired into PresentationDashboard
- Plan 02 will integrate the dialog into the dashboard page

---
*Phase: 02-core-send-flow*
*Completed: 2026-03-06*
