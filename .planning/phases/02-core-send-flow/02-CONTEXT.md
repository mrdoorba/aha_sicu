# Phase 2: Core Send Flow - Context

**Gathered:** 2026-03-06
**Status:** Ready for planning

<domain>
## Phase Boundary

Users can send a dashboard email report through a complete UI flow: send button in DashboardHeader, recipient dialog with brand summary, chart capture to PNG, and loading/success/error feedback. Multiple recipients, CC/BCC, custom notes, and full email preview are Phase 3.

</domain>

<decisions>
## Implementation Decisions

### Send Button
- Outline variant, placed left of the existing Edit Evaluation button
- Lucide Mail icon + "Kirim Email" label (Indonesian, added to i18n)
- Same height (h-10) as Edit button, matching padding
- Visible to all authenticated users (no role restriction)
- Added as translation key in locales

### Dialog Structure
- Dialog title: "Kirim Laporan Email"
- Brand summary card at top showing: brand name, period, score (read-only confirmation of what's being sent)
- Single recipient email input field below summary
- Recipient pre-filled with PIC email from brand raw_data if available, otherwise empty
- Send button disabled until valid email format is entered (frontend validation)
- Footer: Batal (cancel) + Kirim (send) buttons

### Feedback States
- **Loading**: Inline in dialog — Send button shows spinner + "Mengirim..." text, all fields disabled, dialog stays open
- **Success**: Dialog closes automatically, Sonner toast shows "Email terkirim ke {recipient}" with checkmark, auto-dismisses after 5s
- **Error**: Inline in dialog — error message appears above buttons: "Gagal mengirim email. Coba lagi." Generic message for all error types (SMTP errors logged server-side but not exposed to user). Send button changes to "Coba Lagi" (retry)

### Chart Capture
- Use html-to-image library to capture ScoreBreakdownChart RadarChart as PNG
- Capture triggered on send click (chart is rendered on dashboard page behind dialog)
- If capture fails, block send and show error in dialog: "Gagal menangkap grafik. Coba lagi."
- Chart image sent as base64 in API request body (matches backend contract)

### Claude's Discretion
- Exact dialog width and spacing
- html-to-image configuration options (scale, quality, background)
- Chart capture target element selection strategy (ref vs querySelector)
- Hook structure for send mutation (useSendEmail or similar)
- API path type additions in apiClient.ts

</decisions>

<specifics>
## Specific Ideas

- Brand summary card in dialog gives user confidence about what report is being sent without full HTML preview (that's Phase 3)
- PIC email pre-fill mirrors existing SendMailDialog pattern on History page
- Generic error messages keep the UI simple — detailed errors are in server logs for debugging

</specifics>

<code_context>
## Existing Code Insights

### Reusable Assets
- `frontend/src/components/ui/dialog.tsx`: Radix-based Dialog with DialogContent, DialogHeader, DialogFooter, DialogTitle — direct reuse
- `frontend/src/components/ui/button.tsx`: Button with variant="outline" for send button
- `frontend/src/components/ui/input.tsx`: Input component for email field
- `frontend/src/components/ui/sonner.tsx`: Toast notifications already set up in app
- `frontend/src/components/evaluations/SendMailDialog.tsx`: Reference for PIC email pre-fill pattern (uses brandRawData.email)

### Established Patterns
- openapi-fetch client with typed paths interface at `frontend/src/services/apiClient.ts` — add `/api/v1/email/send` path type
- Hooks wrap TanStack Query mutations (useMutation) — create `useEmail.ts` or `useSendEmail.ts`
- Components receive data via props from parent (PresentationDashboard passes evaluation data down)
- i18n translations in `frontend/src/locales/id.json` for all UI text

### Integration Points
- `DashboardHeader`: Add Send Email button (needs evaluation_id and brand raw_data passed as new props)
- `PresentationDashboard`: Orchestrates data flow — needs to pass evaluation_id, brand info, and chart ref to new send dialog
- `ScoreBreakdownChart`: Needs a React ref attached for html-to-image capture target
- Backend endpoint already exists: `POST /api/v1/email/send` (evaluation_id, recipient, chart_image base64)

</code_context>

<deferred>
## Deferred Ideas

- Editable subject line UI — Phase 3 (backend already supports optional subject param)
- Full HTML email preview in dialog — Phase 3 (CONT-07)
- Recently used recipients from localStorage — v2 (CONV-01)

</deferred>

---

*Phase: 02-core-send-flow*
*Context gathered: 2026-03-06*
