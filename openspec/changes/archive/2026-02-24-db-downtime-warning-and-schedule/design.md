## Context

Users who access Store ICU outside database operating hours (currently 07:30–19:00 WIB) see broken UI — failed API calls result in generic error states with no explanation. The DB schedule also needs updating to better match actual usage: 08:00–18:30 WIB active hours with scheduler start at 08:30 WIB.

The frontend is a React SPA using shadcn/ui (Radix UI + Tailwind), React Query for data fetching, and openapi-fetch as API client. There's an existing `Dialog` component and no global error handler — errors are currently handled per-mutation.

## Goals / Non-Goals

**Goals:**
- Show a clear modal warning when API calls fail due to DB downtime, informing users of operating hours
- Update Cloud SQL scheduler to reflect new operating hours
- Detect DB downtime errors in the frontend without backend changes

**Non-Goals:**
- Caching data for offline access during downtime
- Adding a health check endpoint that validates DB connectivity
- Changing backend error responses (500s stay as-is)
- Client-side time-based detection (unreliable — user clocks vary, DB might be manually started/stopped)

## Decisions

### 1. Detection: apiClient response middleware + CustomEvent

**Choice:** Add an `onResponse` middleware to the openapi-fetch client that dispatches a `CustomEvent('api-server-error')` on HTTP 500 responses. App.tsx listens for the event via `useEffect` and sets React state to show the modal.

**Why:** Existing React Query hooks throw generic `Error` objects without HTTP status codes (e.g., `throw new Error('Failed to fetch brands')`). This makes it impossible to detect 500s from `QueryCache`/`MutationCache` `onError` callbacks without modifying every hook. The middleware approach detects the status at the source (the HTTP response), and the CustomEvent bridge keeps modal state in React where it belongs.

**Alternative considered:** `QueryCache` and `MutationCache` `onError` callbacks — rejected because the error objects reaching those callbacks are plain `Error` instances with no status information, requiring changes to all existing hooks.

**Implementation:** A `serverErrorMiddleware` in `apiClient.ts` checks `response.status === 500` and dispatches a DOM event. `App.tsx` registers a `useEffect` listener that sets `showDowntimeWarning` state, gated by a `useRef` to track dismissal.

### 2. Modal trigger: HTTP 500 status detection

**Choice:** Trigger the modal when any API call returns HTTP 500 (Internal Server Error).

**Why:** When the DB is down, every protected endpoint returns 500 because `get_current_user()` fails with `RuntimeError`. This is the actual signal. The modal shows operating hours as guidance, not as a definitive "the DB is down because of schedule" claim — it says the system may be unavailable and shows operating hours for reference.

**Alternative considered:** Client-side time check (show modal if outside 08:00–18:30 WIB) — rejected because user device clocks are unreliable and the DB could be manually started/stopped outside schedule.

### 3. Modal component: New `DowntimeWarningDialog` using existing Dialog primitive

**Choice:** Create a new component that wraps the existing Radix `Dialog` from `components/ui/dialog.tsx`.

**Why:** Follows established pattern (same as `DeleteEvaluationDialog`, `PasswordConfirmDialog`). Consistent look and feel.

### 4. Modal behavior: Show once per session, dismissible

**Choice:** Show the modal on first 500 error. After user clicks "Mengerti", suppress it for the rest of the browser session (using React state — not localStorage).

**Why:** Showing it on every failed request would be extremely annoying. Once is enough — the user understands. Using React state (not localStorage) means it resets on page refresh, which is appropriate since the situation may have changed.

### 5. Terraform schedule: Direct cron update

**Choice:** Update the two cron expressions and descriptions in `cloud_sql.tf` directly.

**Why:** Minimal change, no new resources needed. Just updating schedule times.

- START: `30 1 * * *` UTC = 08:30 WIB
- STOP: `30 11 * * *` UTC = 18:30 WIB

## Risks / Trade-offs

- **False positive on non-DB 500s** → The modal shows for any 500 error, not just DB downtime. Acceptable because: (a) 500s are rare in normal operation, (b) the modal message says "mungkin di luar jam operasional" (may be outside operating hours), not definitively "DB is down"
- **User dismisses then forgets** → After dismissing, all subsequent API errors show normal inline error states. This is fine — the user already knows the system is down
- **Schedule gap: DB starts at 08:00 but scheduler fires at 08:30** → The DB active hours are 08:00–18:30 but the START scheduler fires at 08:30. This means there's a 30-minute buffer between when DB actually activates and when the schedule says it should. The STOP job at 18:30 WIB matches the end of active hours exactly. This is intentional per user request.

## Open Questions

None — requirements are clear from the explore session.
