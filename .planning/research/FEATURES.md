# Feature Landscape

**Domain:** Dashboard-to-Email Report (HTML email from evaluation dashboard)
**Researched:** 2026-03-06
**Confidence:** HIGH (well-understood domain, clear project requirements)

## Table Stakes

Features users expect. Missing = product feels incomplete.

| Feature | Why Expected | Complexity | Notes |
|---------|--------------|------------|-------|
| Send Email button in dashboard | Users need a clear entry point to trigger the email flow | Low | Place in `DashboardHeader` alongside existing "Edit Evaluation" button |
| Recipient input dialog | Users must specify who receives the report | Low | Dialog with email input field(s). Existing `SendMailDialog` pattern available as reference |
| Multiple recipients (comma-separated or multi-input) | Reports are rarely sent to just one person; team leads CC stakeholders | Low | Simple comma-split on backend or multi-input UI. No need for address book |
| Visual fidelity with dashboard | The email must look like the dashboard. If it looks broken, users lose trust | High | HTML email rendering is fundamentally limited (no CSS grid, no flexbox in Outlook, no JS). Must use table-based layout. This is the hardest part of the entire feature |
| Score overview section in email | Core data -- the brand's score and verdict | Med | Translate `ScoreOverview` component to inline-styled HTML tables |
| Detailed evaluation breakdown in email | Users expect the full evaluation detail, not just a summary score | Med | Translate `DetailedEvaluation` to HTML tables with inline styles |
| Chart as static image | Charts are the visual centerpiece of the dashboard. Email clients cannot render JS charts | High | Requires server-side or client-side chart-to-PNG rendering. Embed as inline CID attachment or base64 data URI |
| Data intelligence section in email | Users expect calculator results included -- it is part of the dashboard | Med | Translate `DataIntelligence` component data to HTML tables |
| Loading/sending state feedback | Users need to know the email is being sent (not instant like mailto:) | Low | Button loading spinner, success toast, error toast |
| Error handling with clear messages | SMTP can fail (bad credentials, rate limit, invalid recipient). Silent failure is unacceptable | Low | Backend returns structured errors, frontend shows actionable messages |
| Email subject line with brand name and date | Recipients need to identify the report in their inbox | Low | Auto-generated: e.g., "Brand Evaluation Report - {brandName} - {period}" |
| Mobile-friendly email rendering | Many recipients read email on phones | Med | Use responsive email patterns (max-width containers, fluid tables). Test across clients |

## Differentiators

Features that set product apart. Not expected, but valued.

| Feature | Value Proposition | Complexity | Notes |
|---------|-------------------|------------|-------|
| Email preview before sending | Users can verify the report looks correct before sending. Builds confidence, reduces "oops" sends | Med | Render the HTML email in an iframe within the dialog. Reuse the same HTML template the backend will send |
| Custom message/note field | Sender can add personal context ("Please review Q4 numbers") above the report body | Low | Text area in dialog, injected as a paragraph at the top of the email body |
| Sender name/branding in email | Professional appearance -- email shows company name, not just a raw Gmail address | Low | Configurable `SMTP_FROM_NAME` env var, set in email headers |
| CC/BCC fields | Power users want to CC managers or BCC themselves | Low | Additional input fields in dialog, passed to backend SMTP call |
| Recently used recipients | After the 5th time typing the same email, users appreciate autofill | Med | Store last N recipients in localStorage or backend per-user. No full contact management needed |
| Success confirmation with recipient list | After sending, confirm exactly who received the email | Low | Toast or dialog showing "Email sent to alice@company.com, bob@company.com" |

## Anti-Features

Features to explicitly NOT build.

| Anti-Feature | Why Avoid | What to Do Instead |
|--------------|-----------|-------------------|
| Scheduled/recurring email reports | Massive scope increase (cron jobs, scheduling UI, timezone handling, retry logic). Out of scope per PROJECT.md | Keep as manual send-on-demand. Revisit only if validated user demand |
| Email delivery tracking / read receipts | Requires webhook infrastructure, tracking pixels, dedicated email service (SendGrid/Resend). Gmail SMTP has no delivery tracking API | Show send success/failure only. "Sent" means SMTP accepted it |
| PDF attachment generation | Adds a second rendering pipeline (HTML-to-PDF). Doubles the maintenance surface. Email body IS the report | If PDF is later needed, build as a separate "Export PDF" feature, not bundled with email |
| Rich text editor for email body | Over-engineering. The report IS the content. A simple optional note field is sufficient | Plain text note field above the report |
| Contact/address book management | Full CRUD for contacts is a product unto itself. Overkill for internal tool usage | Recently-used recipients list (localStorage) covers 90% of the need |
| Template customization / drag-and-drop email builder | The email template should match the dashboard exactly. User customization breaks visual consistency and multiplies testing surface | One fixed template that mirrors the dashboard layout |
| Non-Gmail SMTP providers | PROJECT.md explicitly scopes to Gmail SMTP. The SMTP abstraction in config allows future swap, but building multi-provider support now is waste | Use env vars (`SMTP_HOST`, `SMTP_PORT`, etc.) so the code is provider-agnostic, but only test/document Gmail |
| Inline editing of report data before sending | Users might want to tweak numbers before emailing. This creates a "lie" -- the email no longer matches the actual evaluation | The email reflects the evaluation as-is. If data is wrong, fix the evaluation first |
| Replacing History page mailto flow | PROJECT.md explicitly keeps the existing `SendMailDialog` mailto flow on the History page unchanged | Two separate email flows coexist. Dashboard = rich HTML via SMTP. History = plain text via mailto |

## Feature Dependencies

```
Send Email Button (DashboardHeader)
  --> Send Email Dialog (recipient input, preview, custom note)
    --> Backend API Endpoint (/api/v1/email/send-report)
      --> HTML Email Template (server-side rendered)
        --> Chart-to-PNG Rendering (for ScoreBreakdownChart)
      --> SMTP Integration (Gmail)
    --> Loading/Error State Handling
```

Dependency chain (build in this order):

1. **SMTP Integration** -- nothing works without email sending capability
2. **HTML Email Template** -- the core deliverable; must be built and tested across email clients before wiring up
3. **Chart-to-PNG Rendering** -- required by the template; can be developed in parallel but must integrate before template is complete
4. **Backend API Endpoint** -- receives dashboard data payload, renders template, sends via SMTP
5. **Send Email Dialog (frontend)** -- UI for recipients, optional note, preview, send button
6. **Send Email Button in DashboardHeader** -- trigger that opens the dialog
7. **Loading/Error States** -- polish layer on top of working flow

## MVP Recommendation

Prioritize (these are table stakes -- the feature is unusable without them):

1. **SMTP integration with Gmail** -- foundation; validate credentials and sending work on Cloud Run
2. **HTML email template** -- the hardest and highest-risk item; start early, test across Gmail/Outlook/Apple Mail
3. **Chart-to-PNG rendering** -- technical risk; choose between server-side (puppeteer/playwright) or client-side (html2canvas/canvas API) early
4. **Backend API endpoint** -- glues template + SMTP + chart rendering together
5. **Send dialog with recipient input** -- minimal UI: one email field, send button, loading state
6. **Send button in DashboardHeader** -- trivial wiring

Defer to post-MVP:
- **Email preview in dialog**: Valuable but not blocking. Can show a simplified preview or none initially
- **CC/BCC fields**: Easy to add later, not needed for first working version
- **Recently used recipients**: Convenience feature, add after core flow is validated
- **Custom note field**: Nice-to-have, add in second iteration

## Complexity Assessment

| Feature Area | Complexity | Risk | Notes |
|--------------|-----------|------|-------|
| HTML email template | **High** | **High** | Email client compatibility is the single biggest risk. Outlook uses Word's rendering engine. No CSS grid, limited flexbox, no media queries in some clients. Must use table-based layout with inline styles. Plan for significant testing/iteration |
| Chart-to-PNG | **High** | **Medium** | Two approaches: server-side (headless browser renders Recharts component) or client-side (html2canvas captures the DOM). Server-side is more reliable but adds infrastructure. Client-side is simpler but quality varies |
| SMTP integration | **Low** | **Low** | Python `smtplib` + `email.mime` is straightforward. Gmail App Passwords or OAuth2. Well-documented |
| Backend API endpoint | **Medium** | **Low** | Standard FastAPI endpoint. Receives JSON payload, renders template, sends email. Main consideration is payload size if chart image is large |
| Frontend dialog | **Low** | **Low** | Follows existing `SendMailDialog` pattern. Standard form with validation |
| Email preview | **Medium** | **Low** | Rendering HTML email in iframe is straightforward but may need sandbox attributes for security |

## Sources

- Project requirements from `.planning/PROJECT.md`
- Existing codebase analysis: `PresentationDashboard.tsx`, `SendMailDialog.tsx`, `DashboardHeader.tsx`, `ScoreBreakdownChart.tsx`
- Domain knowledge: HTML email rendering constraints are well-established (Outlook Word engine, Gmail CSS stripping, lack of JS support in all email clients)
- Recharts library used for `ScoreBreakdownChart` -- requires conversion to static image for email
