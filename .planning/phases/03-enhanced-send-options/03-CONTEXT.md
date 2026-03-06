# Phase 3: Enhanced Send Options - Context

**Gathered:** 2026-03-06
**Status:** Ready for planning

<domain>
## Phase Boundary

Users have full control over email recipients and content before sending. Multiple recipients via tag/chip input, CC/BCC fields, custom note above report body, and in-dialog HTML email preview. Backend schema and endpoint updates to support multi-recipient, CC/BCC, and custom note fields.

</domain>

<decisions>
## Implementation Decisions

### Recipient Input
- Tag/chip input: type email, press Enter or comma to create a chip, Backspace to remove last chip
- Chips are individually deletable (x button)
- PIC email from brand raw_data pre-filled as first chip (consistent with Phase 2)
- Maximum 10 recipients combined across To + CC + BCC
- Validate email format on add (reject invalid immediately, input highlighted red with brief message)
- Send button disabled until at least one valid To recipient exists

### CC/BCC Fields
- Gmail-style "CC" and "BCC" text links next to the To label
- Clicking "CC" expands the CC field below To and hides the "CC" link
- Clicking "BCC" expands the BCC field below CC and hides the "BCC" link
- CC and BCC use the same tag/chip input component as To
- 10-recipient cap is combined total across all three fields
- Backend sends one email with To/CC/BCC headers (not individual emails per recipient)

### Custom Note
- Plain textarea, labeled "Catatan (opsional)"
- 500 character limit with live character count shown below textarea
- Placed below recipient fields, above brand summary card and preview
- Line breaks preserved in email rendering
- In received email: rendered as a subtle card/box with light background, visually distinct from report content
- Positioned below header image and brand info, above Score Overview section (matches Phase 1 decision)
- Optional — empty note means no note section in the email

### Email Preview
- Expandable "Pratinjau Email" toggle section below the compose fields
- Collapsed by default, click to expand
- Renders backend HTML in a scrollable iframe (~300px height)
- Source: GET /api/v1/email/preview/{evaluation_id} endpoint (currently dev-only)
- Enable preview endpoint in production for authenticated users (remove debug-only guard)
- Pass custom note as query parameter so preview reflects the note
- Header and footer images rendered as base64 data URIs in preview (so they display in iframe)
- Chart image shows a placeholder in preview (chart is captured at send time, not preview time)

### Claude's Discretion
- Tag/chip input component implementation (custom or library)
- Exact dialog width adjustments to accommodate new fields
- Preview iframe styling and loading state
- Backend schema changes for multi-recipient/CC/BCC/note fields
- Preview endpoint query parameter design for custom note
- How to convert CID images to data URIs for preview mode
- Textarea height and resize behavior

</decisions>

<specifics>
## Specific Ideas

- Gmail-style CC/BCC reveal pattern — familiar to all email users
- Tag/chip input mirrors Gmail compose UX for recipients
- Preview gives confidence about what the recipient will see before sending
- Custom note card in email uses the same visual language as the rest of the report (subtle, professional)
- Character count (128/500 style) gives clear feedback on note length

</specifics>

<code_context>
## Existing Code Insights

### Reusable Assets
- `frontend/src/components/dashboard/SendEmailDialog.tsx`: Current single-recipient dialog — extend with chip input, CC/BCC, note, preview
- `frontend/src/components/ui/dialog.tsx`: Radix Dialog components (DialogContent, DialogHeader, DialogFooter, DialogTitle)
- `frontend/src/components/ui/input.tsx`: Input component (base for chip input)
- `frontend/src/components/ui/label.tsx`: Label component
- `frontend/src/components/ui/card.tsx`: Card/CardContent for brand summary and note styling
- `frontend/src/hooks/useSendEmail.ts`: Mutation hook — needs schema update for multi-recipient/CC/BCC/note
- `backend/app/modules/email/schemas.py`: SendEmailRequest with single `recipient: EmailStr` — needs expansion
- `backend/app/modules/email/router.py`: Preview endpoint exists (dev-only guard to remove)
- `backend/app/modules/email/service.py`: send_evaluation_email — needs CC/BCC/note support
- `backend/app/modules/email/template.py`: render_email_html — needs custom note section rendering

### Established Patterns
- openapi-fetch client with typed paths at `frontend/src/services/apiClient.ts` — update path types
- TanStack Query mutations for API calls
- i18n translations in `frontend/src/locales/id.json` for all UI text
- Pydantic schemas for request validation
- AppException for error handling

### Integration Points
- SendEmailDialog.tsx: Major refactor — add chip input, CC/BCC toggle, textarea, preview iframe
- Backend SendEmailRequest schema: `recipient` becomes `recipients: list[EmailStr]`, add `cc`, `bcc`, `note` fields
- Backend email service: SMTP message construction needs To/CC/BCC headers
- Backend template: Add optional custom note section rendering
- Preview endpoint: Remove debug guard, accept note query param, return data URIs for images
- Frontend apiClient.ts: Update send and preview path types

</code_context>

<deferred>
## Deferred Ideas

- Editable subject line UI — backend already supports optional subject param (carried from Phase 1/2)
- Recently used recipients from localStorage — v2 (CONV-01)
- English language toggle — future (backend template uses string dict)

</deferred>

---

*Phase: 03-enhanced-send-options*
*Context gathered: 2026-03-06*
