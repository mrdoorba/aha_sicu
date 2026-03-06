---
phase: 03-enhanced-send-options
plan: 01
subsystem: api
tags: [email, smtp, multi-recipient, cc-bcc, template, pydantic, fastapi]

# Dependency graph
requires:
  - phase: 01-backend-email-engine
    provides: Email service, template renderer, SMTP send, preview endpoint
provides:
  - Multi-recipient email with To/CC/BCC header support
  - Custom note rendering in email template
  - Production-ready preview endpoint with data URI images
  - asset_to_data_uri helper for converting assets to base64 data URIs
affects: [03-02, 03-03, frontend-send-dialog]

# Tech tracking
tech-stack:
  added: []
  patterns:
    - "*_src parameter convention for image URIs (cid: for send, data: for preview)"
    - "Explicit to_addrs in SMTP send for BCC support without header leak"
    - "_render_note helper for styled card HTML section"

key-files:
  created: []
  modified:
    - backend/app/modules/email/schemas.py
    - backend/app/modules/email/service.py
    - backend/app/modules/email/template.py
    - backend/app/modules/email/router.py
    - backend/tests/unit/email/test_service.py
    - backend/tests/unit/email/test_template.py
    - backend/tests/unit/email/test_config.py

key-decisions:
  - "Renamed template params from *_cid to *_src for dual cid:/data: URI support"
  - "BCC handled via explicit to_addrs in server.send_message, never as header"
  - "Preview endpoint debug guard removed -- auth-only protection sufficient"
  - "Chart placeholder in preview uses inline SVG data URI"

patterns-established:
  - "Image src parameters accept full URIs -- callers pass cid:xxx or data:xxx"
  - "asset_to_data_uri public helper in service.py for preview-mode images"

requirements-completed: [SEND-03, SEND-04, SEND-05, CONT-07]

# Metrics
duration: 7min
completed: 2026-03-06
---

# Phase 3 Plan 1: Backend Multi-Recipient, CC/BCC, Note, and Preview Summary

**Multi-recipient email with To/CC/BCC headers, custom note card in template, and production preview endpoint using data URI images**

## Performance

- **Duration:** 7 min
- **Started:** 2026-03-06T08:40:12Z
- **Completed:** 2026-03-06T08:47:00Z
- **Tasks:** 2
- **Files modified:** 7

## Accomplishments
- SendEmailRequest schema supports recipients list, cc, bcc, note with combined 10-recipient validator
- Email template renders custom note as styled card between header and score overview with line break preservation
- Preview endpoint works in production with data URI images and note query parameter
- Template parameter convention changed from *_cid to *_src for cid:/data: URI flexibility

## Task Commits

Each task was committed atomically:

1. **Task 1: Update schemas, service, and template** - `ee1b294` (feat, TDD)
2. **Task 2: Update preview and send endpoints** - `879e3bd` (feat)

## Files Created/Modified
- `backend/app/modules/email/schemas.py` - Multi-recipient request/response with cc, bcc, note, validator
- `backend/app/modules/email/service.py` - build_email_message with To/CC/BCC, _smtp_send_sync with to_addrs, asset_to_data_uri helper
- `backend/app/modules/email/template.py` - _render_note, *_src params, note section in HTML assembly
- `backend/app/modules/email/router.py` - Send endpoint with multi-recipient, preview with data URIs and note
- `backend/tests/unit/email/test_service.py` - New tests for multi-recipient, CC/BCC, note, to_addrs
- `backend/tests/unit/email/test_template.py` - TestCustomNote class with 6 tests, updated *_src params
- `backend/tests/unit/email/test_config.py` - Updated schema tests for new fields

## Decisions Made
- Renamed template params from *_cid to *_src for dual cid:/data: URI support
- BCC handled via explicit to_addrs in server.send_message, never as header
- Preview endpoint debug guard removed -- auth-only protection sufficient
- Chart placeholder in preview uses inline SVG data URI with Indonesian text

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 1 - Bug] Updated test_config.py schema tests for new field names**
- **Found during:** Task 1 (TDD GREEN phase)
- **Issue:** test_config.py had tests using old `recipient` field name, failing after schema update
- **Fix:** Updated all schema tests to use `recipients` list, added tests for cc/bcc defaults, note, and total validation
- **Files modified:** backend/tests/unit/email/test_config.py
- **Verification:** All 96 tests pass
- **Committed in:** ee1b294 (Task 1 commit)

---

**Total deviations:** 1 auto-fixed (1 bug)
**Impact on plan:** Necessary fix for existing tests to match schema changes. No scope creep.

## Issues Encountered
None

## User Setup Required
None - no external service configuration required.

## Next Phase Readiness
- Backend fully supports multi-recipient, CC/BCC, custom note, and preview
- Frontend can now build the enhanced SendEmailDialog against the updated API
- Preview endpoint returns renderable HTML with visible images for iframe display

---
*Phase: 03-enhanced-send-options*
*Completed: 2026-03-06*
