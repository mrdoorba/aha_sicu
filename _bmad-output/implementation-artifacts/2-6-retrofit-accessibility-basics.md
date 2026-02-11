# Story 2.6: Retrofit Accessibility Basics

Status: done

## Story

As a **BD team member using assistive technology**,
I want **core UI elements to have proper ARIA annotations and keyboard patterns**,
so that **I can navigate and operate Store ICU with a screen reader or keyboard alone**.

## Acceptance Criteria

1. **Icon-only buttons have accessible names**
   **Given** the app renders icon-only buttons (e.g., sync, logout, search clear, pagination arrows)
   **When** a screen reader focuses any icon-only button
   **Then** it announces a meaningful label (via `aria-label`)
   **And** the following components are updated:
     - `Header.tsx` — logout button, any icon-only actions
     - `BrandTable.tsx` — pagination arrows, sort toggles
     - `SyncStatus.tsx` — sync trigger button (if icon-only variant)
     - `BrandsPage.tsx` — search clear button, any icon-only filter controls

2. **Live regions announce sync state changes**
   **Given** the sync status changes (idle → syncing → success/failure)
   **When** `SyncStatus.tsx` renders the updated state
   **Then** the status text is wrapped in an `aria-live="polite"` region
   **And** sync completion or failure is announced to screen readers without requiring focus change

3. **Skip-to-content link exists**
   **Given** I land on any page using keyboard navigation
   **When** I press Tab as the first action
   **Then** a "Skip to main content" link becomes visible
   **And** activating it moves focus to the `<main>` landmark (or primary content area)
   **And** the link is implemented in `App.tsx` or the top-level layout component

4. **Search input has an accessible label**
   **Given** the brand search input on `BrandsPage.tsx`
   **When** a screen reader focuses the input
   **Then** it announces a descriptive label (e.g., "Search brands")
   **And** the label is either a visually-hidden `<label>` element or an `aria-label` attribute

5. **Logout confirmation uses accessible Dialog**
   **Given** I click the logout button in `Header.tsx`
   **When** the confirmation prompt appears
   **Then** it uses the shadcn `Dialog` component (Radix-based, already installed)
   **And** focus is trapped inside the dialog while open
   **And** pressing Escape closes the dialog
   **And** the dialog has an accessible title (`aria-labelledby` or Dialog.Title)

6. **Loading skeleton has aria-busy**
   **Given** the brand table in `BrandTable.tsx` is loading data
   **When** a skeleton/loading state is displayed
   **Then** the table or its container has `aria-busy="true"`
   **And** when loading completes, `aria-busy` is removed or set to `"false"`

## Tasks / Subtasks

- [x] Task 1: Add skip-to-content link in App.tsx (AC: #3)
  - [x] 1.1 Add a visually-hidden anchor `<a href="#main-content" className="sr-only focus:not-sr-only focus:absolute focus:z-50 ...">Skip to main content</a>` as the first child inside `<BrowserRouter>`, before `<AuthProvider>`
  - [x] 1.2 In `BrandsPage.tsx`, add `id="main-content"` and `tabIndex={-1}` to the existing `<main>` element (it already uses `<main>`)
  - [x] 1.3 In `DashboardPage.tsx`, ensure the primary content area has `id="main-content"` and `tabIndex={-1}` (check current structure first)
  - [x] 1.4 Style: visually hidden by default, appears top-left on focus with high-contrast background

- [x] Task 2: Add aria-labels and aria-hidden to BrandsPage icons (AC: #1, #4)
  - [x] 2.1 Search input: Add `aria-label="Search brands"` to the `<Input>` element
  - [x] 2.2 Search icon: Add `aria-hidden="true"` to the decorative `<Search>` icon (it's a visual affordance only — the input has its own label)
  - [x] 2.3 Pagination buttons: The "Previous" and "Next" buttons already have visible text alongside icons — add `aria-hidden="true"` to `<ChevronLeft>` and `<ChevronRight>` icons to prevent duplicate announcements
  - [x] 2.4 Error state icon: Add `aria-hidden="true"` to the `<XCircle>` in the error empty state (message text is sufficient)
  - [x] 2.5 Empty state icon: Add `aria-hidden="true"` to the `<RefreshCw>` in the "no brands" empty state

- [x] Task 3: Add aria-live region to SyncStatus (AC: #2)
  - [x] 3.1 Wrap the sync status badge area (the `<div>` containing the status Badge) with `aria-live="polite"` and `aria-atomic="true"` so screen readers announce status transitions
  - [x] 3.2 Add `aria-hidden="true"` to all decorative icons inside Badges (`<CheckCircle2>`, `<XCircle>`, `<Clock>`, `<RefreshCw>`) — the Badge text provides meaning
  - [x] 3.3 Add `aria-hidden="true"` to connection state icons (`<Wifi>`, `<WifiOff>`) — the adjacent text label provides meaning
  - [x] 3.4 Confirm "Sync Now" button already has visible text label ("Sync Now" / "Syncing...") — add `aria-hidden="true"` to the `<RefreshCw>` icon inside the button to prevent duplicate announcement

- [x] Task 4: Replace custom logout modal with shadcn Dialog (AC: #5)
  - [x] 4.1 Import `Dialog, DialogContent, DialogHeader, DialogTitle, DialogDescription, DialogFooter, DialogClose` from `../ui/dialog`
  - [x] 4.2 Replace the custom `{showConfirm && (<div className="fixed inset-0 ...">...`  modal with shadcn Dialog components:
    - `<Dialog open={showConfirm} onOpenChange={setShowConfirm}>`
    - `<DialogContent showCloseButton={false}>` (no X close button — use Cancel/Logout buttons only)
    - `<DialogHeader>` + `<DialogTitle>Confirm Logout</DialogTitle>` + `<DialogDescription>Are you sure you want to log out?</DialogDescription>`
    - `<DialogFooter>` with Cancel and Logout buttons
  - [x] 4.3 Remove the manual `useEffect` for Escape key handling — Radix Dialog handles this natively
  - [x] 4.4 Remove `handleBackdropClick` — Radix Dialog handles backdrop dismiss via `onOpenChange`
  - [x] 4.5 Remove `modalRef` — no longer needed
  - [x] 4.6 Keep `cancelButtonRef` for initial focus — or use Dialog's `autoFocus` on the cancel button (Radix focuses first focusable by default; if you want Cancel focused instead of Logout, add `autoFocus` to Cancel button)
  - [x] 4.7 Retain existing logout logic (`handleConfirmLogout`, `isLoggingOut` state) — only the modal shell changes

- [x] Task 5: Add aria-busy to BrandTable loading state (AC: #6)
  - [x] 5.1 Add `aria-busy={isLoading}` to the `<Table>` element (or its wrapping container)
  - [x] 5.2 Add `aria-label="Brand list"` to the `<Table>` for screen reader identification
  - [x] 5.3 Add `role="status"` and an `sr-only` span like `<span className="sr-only">Loading brands...</span>` inside the skeleton state (optional — `aria-busy` is the primary mechanism)

- [x] Task 6: Add aria-labels to Header icon elements (AC: #1)
  - [x] 6.1 The logout button already has visible "Logout" text — no change needed
  - [x] 6.2 Verify nav links (Dashboard, Brands) are accessible — they use `<Link>` with visible text, which is correct
  - [x] 6.3 No icon-only buttons found in Header currently — this task is a verification pass

- [x] Task 7: Write frontend tests for accessibility attributes (AC: all)
  - [x] 7.1 Test skip-to-content link: verify link exists, is focusable, has correct href `#main-content`
  - [x] 7.2 Test BrandsPage search input has accessible label (query by role + accessible name)
  - [x] 7.3 Test SyncStatus has `aria-live="polite"` region
  - [x] 7.4 Test BrandTable has `aria-busy="true"` when loading, `aria-busy="false"` when loaded
  - [x] 7.5 Test Header Dialog renders with accessible title when open (query by role "dialog")
  - [x] 7.6 Test decorative icons have `aria-hidden="true"`

## Dev Notes

### This Is a Frontend-Only Story

No backend changes. No database migrations. No new API endpoints. Only modify existing frontend components to add accessibility attributes.

### Architecture Compliance

**Frontend Pattern (MUST follow):**
- Components in `src/components/{feature}/` — e.g., `components/brands/`, `components/sync/`, `components/layout/`
- Pages in `src/pages/`
- Use shadcn/ui components (Radix-based) — Dialog already installed at `components/ui/dialog.tsx`
- Use Tailwind CSS for styling — `sr-only` utility class for visually-hidden content

**shadcn Dialog Component — Already Installed:**
- File: `frontend/src/components/ui/dialog.tsx`
- Radix-based with full a11y: focus trap, Escape dismiss, `aria-modal`, auto focus restoration
- Close button has `sr-only` label built-in
- Components: `Dialog`, `DialogContent`, `DialogHeader`, `DialogTitle`, `DialogDescription`, `DialogFooter`, `DialogClose`, `DialogTrigger`
- `DialogContent` has `showCloseButton` prop (default `true`) — set to `false` for logout confirmation since we want Cancel/Logout buttons only

### Current Component State — What Exists Today

**App.tsx:**
- Routes wrapped in `BrowserRouter` > `AuthProvider` > `Routes`
- No skip-to-content link
- No `<main>` wrapper at app level (each page provides its own)

**Header.tsx (`components/layout/Header.tsx`):**
- Custom modal implementation with manual `role="dialog"`, `aria-modal`, `aria-labelledby`, `aria-describedby`
- Manual Escape key handler via `useEffect` + `document.addEventListener`
- Manual backdrop click handling
- Focus management: `cancelButtonRef` focused on open, but no focus restoration on close
- Logout button has visible text "Logout" (NOT icon-only)
- Nav links use `<Link>` with visible text "Dashboard" and "Brands"

**BrandTable.tsx (`components/brands/BrandTable.tsx`):**
- Uses shadcn `Table` components (semantic `<table>` under the hood)
- Loading state: 10 skeleton rows with `animate-pulse` divs
- No `aria-busy`, no loading announcement
- No icon-only buttons in this component
- No pagination controls (those are in BrandsPage)

**SyncStatus.tsx (`components/sync/SyncStatus.tsx`):**
- Icons inside Badges with adjacent text (not icon-only — all have text labels)
- Connection state icons (Wifi/WifiOff) with adjacent text labels
- "Sync Now" button has icon + visible text
- No `aria-live` region for status changes
- No `aria-hidden` on decorative icons

**BrandsPage.tsx (`pages/BrandsPage.tsx`):**
- Search input: `<Input>` with `placeholder="Search brands..."` but no `aria-label` or `<label>`
- Decorative `<Search>` icon overlaid on input — no `aria-hidden`
- Pagination: Buttons with `<ChevronLeft>` icon + "Previous" text, "Next" text + `<ChevronRight>` icon
- Error state: `<XCircle>` icon + text message
- Empty state: `<RefreshCw>` icon + text message
- Has `<main>` element wrapping content (good)

### Key Implementation Guidance

**Skip-to-content link pattern:**
```tsx
{/* First focusable element in the DOM */}
<a
  href="#main-content"
  className="sr-only focus:not-sr-only focus:absolute focus:top-2 focus:left-2 focus:z-[100] focus:bg-background focus:text-foreground focus:px-4 focus:py-2 focus:rounded-md focus:ring-2 focus:ring-ring focus:outline-none"
>
  Skip to main content
</a>
```

**aria-live region pattern (SyncStatus):**
```tsx
{/* Wrap the status display area */}
<div aria-live="polite" aria-atomic="true">
  {/* existing Badge rendering for sync status */}
</div>
```

**Dialog migration pattern (Header.tsx):**
```tsx
<Dialog open={showConfirm} onOpenChange={setShowConfirm}>
  <DialogContent showCloseButton={false}>
    <DialogHeader>
      <DialogTitle>Confirm Logout</DialogTitle>
      <DialogDescription>Are you sure you want to log out?</DialogDescription>
    </DialogHeader>
    <DialogFooter>
      <Button variant="outline" onClick={handleCancelLogout} disabled={isLoggingOut}>
        Cancel
      </Button>
      <Button variant="destructive" onClick={handleConfirmLogout} disabled={isLoggingOut}>
        {isLoggingOut ? 'Logging out...' : 'Logout'}
      </Button>
    </DialogFooter>
  </DialogContent>
</Dialog>
```

**Cleanup after Dialog migration — REMOVE these from Header.tsx:**
- `modalRef` ref declaration and usage
- `handleBackdropClick` function
- `useEffect` for Escape key handling (`handleKeyDown`)
- The entire custom modal JSX block (`{showConfirm && (<div className="fixed inset-0 ...">...`)}`)
- Import of `useEffect` and `useRef` (if no other usage remains — `useState` is still needed)

**Keep after migration:**
- `showConfirm` state + `setShowConfirm`
- `handleLogoutClick`, `handleConfirmLogout`, `handleCancelLogout`
- `isLoggingOut` state
- `cancelButtonRef` only if you want explicit initial focus on Cancel (otherwise remove)

### Anti-Patterns to Avoid

1. **DO NOT** add `aria-label` to elements that already have visible text — visible text IS the accessible name. Only use `aria-label` when there is no visible text.
2. **DO NOT** duplicate announcements — if an icon has adjacent text, use `aria-hidden="true"` on the icon, not `aria-label`.
3. **DO NOT** use `aria-live="assertive"` — `"polite"` is correct for non-urgent status updates.
4. **DO NOT** add `role="button"` to `<button>` elements — they already have implicit button role.
5. **DO NOT** use `aria-label` on the `<Table>` AND a visible caption — choose one. Since there's no visible caption, `aria-label` is appropriate.
6. **DO NOT** add automated a11y testing (jest-axe/vitest-axe) — that's out of scope for this story.
7. **DO NOT** refactor color classes to design tokens — out of scope.
8. **DO NOT** add keyboard shortcuts (Ctrl+K search) — out of scope.
9. **DO NOT** touch backend code — this is frontend-only.
10. **DO NOT** add `aria-current="page"` to nav links — deferred per story scope.

### Previous Story Intelligence

**From Story 2.3 (Brand List UI with Sync Status):**
- Established frontend component patterns: components in `components/{feature}/`, hooks in `hooks/`, pages in `pages/`
- shadcn/ui components installed: Button, Input, Card, Badge, Table, Toast, Dialog, Progress
- Frontend tests use `@testing-library/react` + `vi.fn()` for mocks
- 48 frontend tests passing after Story 2.3

**From Story 2.4 (Real-Time Sync Status via SSE):**
- Added `useSSE` hook in `hooks/useSSE.ts` — provides `connectionState`
- SyncStatus component updated with connection state display (Wifi/WifiOff icons)
- SSE event handling patterns established

**From Epic 2 Retrospective:**
- Code review issue count decreased over the epic: 10→8→20→10→8
- Story 2.3 (first frontend story) had highest issue count — patterns now established
- Recurring issue: Story File List must include ALL changed files

### Code Review Lessons — Pre-Apply

- Story File List must include ALL files changed on the feature branch (check `git diff`)
- Type definitions must stay in sync between `apiClient.ts` paths and hooks
- Error handling in TanStack Query queryFn: throw errors, don't swallow them
- Test assertions should verify specific expected values, not just existence

### Testing Requirements

**Frontend Tests (Vitest + @testing-library/react):**

All tests should query elements by accessible role/name to validate a11y attributes work correctly.

- Test skip-to-content: `screen.getByRole('link', { name: /skip to main content/i })` exists and has `href="#main-content"`
- Test search input: `screen.getByRole('searchbox', { name: /search brands/i })` or `screen.getByLabelText(/search brands/i)` resolves
- Test aria-live: Container with `aria-live="polite"` exists in SyncStatus
- Test aria-busy: `screen.getByRole('table')` has `aria-busy="true"` when loading
- Test Dialog: When logout dialog opens, `screen.getByRole('dialog')` exists with accessible title
- Test decorative icons: Selected icons have `aria-hidden="true"` attribute

**Run tests:** `cd frontend && npx vitest run --reporter=verbose`

### Library & Framework Requirements

| Library | Version | Usage in This Story | Status |
|---------|---------|---------------------|--------|
| radix-ui (via shadcn Dialog) | existing | Dialog, DialogContent, DialogTitle, etc. | Installed |
| @testing-library/react | existing | Test a11y attributes via role queries | Installed |
| lucide-react | existing | Icon components (add aria-hidden) | Installed |
| tailwindcss | existing | `sr-only`, `focus:not-sr-only` utilities | Installed |

**No new dependencies required.**

### Project Structure Notes

No new files or directories needed (except tests). This story modifies existing files only:

```
frontend/src/App.tsx                              ← MODIFY: add skip-to-content link
frontend/src/components/layout/Header.tsx         ← MODIFY: replace custom modal with Dialog
frontend/src/components/brands/BrandTable.tsx     ← MODIFY: add aria-busy, aria-label
frontend/src/components/sync/SyncStatus.tsx       ← MODIFY: add aria-live, aria-hidden on icons
frontend/src/pages/BrandsPage.tsx                 ← MODIFY: add aria-label on search, aria-hidden on icons, id on main
```

Test files (create or extend existing):
```
frontend/src/App.test.tsx                         ← CREATE or EXTEND: skip-to-content test
frontend/src/components/layout/Header.test.tsx    ← EXTEND: Dialog a11y test
frontend/src/components/brands/BrandTable.test.tsx ← EXTEND: aria-busy test
frontend/src/components/sync/SyncStatus.test.tsx  ← EXTEND: aria-live test
frontend/src/pages/BrandsPage.test.tsx            ← EXTEND: search label, icon aria-hidden tests
```

### References

- [Source: _bmad-output/planning-artifacts/epics.md#Story 2.6: Retrofit Accessibility Basics]
- [Source: _bmad-output/planning-artifacts/architecture.md#Frontend Architecture]
- [Source: _bmad-output/implementation-artifacts/2-3-brand-list-ui-with-sync-status.md — Frontend patterns, component locations]
- [Source: _bmad-output/implementation-artifacts/2-4-real-time-sync-status-via-sse.md — SSE hook, connection state display]
- [Source: _bmad-output/lessons-learned.md — Code review patterns, frontend conventions]
- [Source: frontend/src/components/ui/dialog.tsx — shadcn Dialog component API]

## Dev Agent Record

### Agent Model Used

Claude Opus 4.6

### Debug Log References

- Initial test run: 3 failures (App.test.tsx mock incomplete, Header test button selector fragile, BrandsPage CSS selector wrong for SVG)
- Fixed all 3: added Toaster mock, used data-variant selector for dialog button, corrected SVG class selector
- Final run: 66/66 tests passing, 0 regressions

### Completion Notes List

- Task 1: Added skip-to-content link in App.tsx before AuthProvider; added `id="main-content"` and `tabIndex={-1}` to `<main>` in BrandsPage and DashboardPage; styled with sr-only + focus:not-sr-only pattern
- Task 2: Added `aria-label="Search brands"` to search input; added `aria-hidden="true"` to all decorative icons (Search, XCircle, RefreshCw, ChevronLeft, ChevronRight)
- Task 3: Added `aria-live="polite"` and `aria-atomic="true"` to sync status badge area; added `aria-hidden="true"` to all decorative icons in SyncStatus (Badge icons, connection state icons, Sync Now button icon)
- Task 4: Replaced custom logout modal with shadcn Dialog (Radix-based); removed manual Escape handler, backdrop click handler, modalRef, cancelButtonRef; Dialog provides native focus trap, Escape dismiss, aria-modal, auto focus restoration
- Task 5: Added `aria-busy={isLoading}` and `aria-label="Brand list"` to BrandTable `<Table>` element; subtask 5.3 (sr-only loading text) was optional and skipped since aria-busy is the primary mechanism
- Task 6: Verification pass — confirmed logout button has visible text, nav links use accessible `<Link>` with visible text, no icon-only buttons in Header
- Task 7: Created App.test.tsx for skip-to-content test; extended BrandTable, SyncStatus, BrandsPage, Header test files with a11y attribute tests; all 66 tests passing

### Change Log

- 2026-02-11: Implemented Story 2.6 — Retrofit Accessibility Basics. Added skip-to-content link, aria-labels, aria-hidden on decorative icons, aria-live region for sync status, replaced custom modal with shadcn Dialog, added aria-busy to loading table, and wrote comprehensive a11y tests.
- 2026-02-11: Code review fixes (9 issues: 1 HIGH, 5 MEDIUM, 3 LOW). Added id="main-content" to LoginPage for skip link coverage on all pages; replaced brittle CSS selectors in tests with accessible role queries; added DashboardPage tests; added skip-link target verification test; used DialogClose for Cancel button; added aria-live to connection state; added type="search" for searchbox semantics. Tests: 69/69 passing (10 files, +3 new tests).

### File List

- frontend/src/App.tsx (modified — added skip-to-content link)
- frontend/src/App.test.tsx (created — skip-to-content tests with target verification)
- frontend/src/pages/BrandsPage.tsx (modified — aria-label on search, type="search", aria-hidden on icons, id on main)
- frontend/src/pages/BrandsPage.test.tsx (modified — a11y tests with role-based queries)
- frontend/src/pages/DashboardPage.tsx (modified — id and tabIndex on main)
- frontend/src/pages/DashboardPage.test.tsx (created — main landmark and id verification tests)
- frontend/src/pages/LoginPage.tsx (modified — changed outer div to main with id="main-content" and tabIndex)
- frontend/src/components/layout/Header.tsx (modified — replaced custom modal with shadcn Dialog, DialogClose for Cancel, removed manual handlers)
- frontend/src/components/layout/Header.test.tsx (modified — accessible role queries for dialog buttons)
- frontend/src/components/brands/BrandTable.tsx (modified — added aria-busy, aria-label on Table)
- frontend/src/components/brands/BrandTable.test.tsx (modified — added aria-busy and aria-label tests)
- frontend/src/components/sync/SyncStatus.tsx (modified — added aria-live regions for sync status and connection state, aria-hidden on icons)
- frontend/src/components/sync/SyncStatus.test.tsx (modified — added aria-live and icon aria-hidden tests)
- _bmad-output/implementation-artifacts/sprint-status.yaml (modified — status updated to review)
- _bmad-output/implementation-artifacts/2-6-retrofit-accessibility-basics.md (modified — tasks marked complete, dev agent record updated, review fixes applied)
