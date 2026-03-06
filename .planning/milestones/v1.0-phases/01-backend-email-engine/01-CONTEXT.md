# Phase 1: Backend Email Engine - Context

**Gathered:** 2026-03-06
**Status:** Ready for planning

<domain>
## Phase Boundary

A working backend that can accept an evaluation ID and send a complete, cross-client-compatible HTML email with embedded chart image via Gmail SMTP. Includes SMTP client, HTML email template, API endpoint, and preview/debug tooling. Frontend UI (send button, dialog, chart capture) is Phase 2.

</domain>

<decisions>
## Implementation Decisions

### HTML Template - Score Overview
- Large number + horizontal progress bar (not radial chart)
- Shows: score/100, colored progress bar, check/cross counts, template type
- Color thresholds match dashboard: green >= 80%, primary/blue >= 50%, orange < 50%

### HTML Template - Detailed Evaluation
- All categories stacked vertically (no tabs in email)
- Each category shows all metric cards with full detail: metric name, value, benchmark, verdict, score, message
- 2-column grid on desktop email, single column on mobile (responsive via media queries)

### HTML Template - Score Breakdown Chart
- PNG radar chart image (CID inline) at top of section
- Category bars with progress bars (CSS) and check/cross counts below the chart image

### HTML Template - Data Intelligence
- Both Ads Analysis and Top SKU sections stacked vertically
- Ads Analysis: preformatted text block (as-is from backend)
- Top SKU: revenue ranking table + stock ranking table, top 3 rows each (not 5)

### HTML Template - Header & Footer
- AHACommerce branded header image (my-designs/images/aha-e-mail-header-2026.png) as CID inline image
- Brand name, period, verdict, and template type displayed below header image
- AHACommerce branded footer image (my-designs/images/aha-e-mail-footer-2026.png) as CID inline image
- No evaluator info or timestamp in footer -- just the branded image
- Custom note (Phase 3) placement: below header, above report content

### HTML Template - General
- Section headers only (no numbered prefixes like 01, 02, 03, 04)
- Color scheme matches dashboard theme (primary brand color, card backgrounds, green/orange verdicts)
- Table-based layout with inline CSS for cross-client compatibility
- All images (header, footer, chart) embedded as CID inline attachments

### API Data Contract
- Endpoint: POST /api/v1/email/send
- Input: evaluation_id, recipient email, chart_image (base64 in JSON body), optional subject
- Backend fetches all evaluation data from Cloud SQL using evaluation_id (single source of truth)
- Requires authentication (existing Firebase auth middleware)
- No ownership validation -- trust authenticated users (internal tool)
- Response on success: {"success": true, "message_id": "...", "recipient": "..."}
- Optional subject parameter: if not provided, auto-generates "Laporan Evaluasi Brand: [Brand Name] - [Period]"

### API - Module Structure
- New `email` module at backend/app/modules/email/
- Files: __init__.py, router.py, service.py, schemas.py, template.py
- Preview endpoint: GET /api/v1/email/preview/{evaluation_id} (dev/staging only)

### Error Handling
- Categorized SMTP errors: smtp_auth_error, smtp_connection, smtp_timeout (with appropriate HTTP status codes)
- 422 for invalid evaluation_id (not found in DB)
- 422 for missing/malformed chart_image base64 (chart is required)
- Validate recipient email format before SMTP send (422 on invalid)
- No rate limiting -- trust authenticated users, Gmail 500/day is natural throttle
- Log failures only (not successes)

### Email Language & Localization
- Indonesian only for now, but template strings stored in a Python dict (not hardcoded inline)
- Structure: STRINGS = {"id": {"score_overview": "Ringkasan Skor", ...}} -- adding English later is just a new dict + lang param
- Metric/category names use Indonesian translations (mirror frontend id.json labels)
- Subject format: "Laporan Evaluasi Brand: [Brand Name] - [Period]"

### SMTP Configuration
- STARTTLS on port 587 (Gmail recommended)
- Per-request SMTP connection (open, send, close)
- No SMTP validation on startup -- errors surface on send
- 30 second hardcoded timeout
- EMAIL_ENABLED env var toggle to disable sending entirely
- SMTP_PASSWORD stored as GCP Secret Manager secret; other SMTP vars as plain Cloud Run env vars

### SMTP Env Vars
- SMTP_HOST (smtp.gmail.com)
- SMTP_PORT (587)
- SMTP_USER (login username)
- SMTP_PASSWORD (App Password)
- SMTP_FROM_NAME (display name, e.g., "AHA Commerce")
- SMTP_FROM_EMAIL (sender address, may differ from SMTP_USER)
- EMAIL_ENABLED (true/false toggle)

### Testing Strategy
- Mock SMTP in automated tests (no real Gmail in CI)
- Full content verification: HTML structure snapshot, correct data binding, inline CSS, all metric rows, table structure, CID references
- HTML snapshot test for visual review (open rendered HTML in browser)
- File output debug mode: when SMTP env vars empty or debug flag set, save rendered HTML to local file
- Preview endpoint for template iteration during development

### Claude's Discretion
- Exact inline CSS styling and spacing
- HTML table nesting structure for email layout
- Progress bar CSS implementation in email
- Responsive email media query breakpoints
- Python SMTP library choice (smtplib vs aiosmtplib)
- Test fixture data structure

</decisions>

<specifics>
## Specific Ideas

- Header/footer images exist at my-designs/images/aha-e-mail-header-2026.png and aha-e-mail-footer-2026.png
- Header image: AHACommerce logo with "Powered by AHABOT" on blue gradient
- Footer image: AHACommerce logo + Shopee Premium Enabler + Lazada Partner badges + "Superpower your brand"
- All data is guaranteed present when a brand has a dashboard page -- no empty state handling needed for email sections
- Email is for external sharing -- no internal IDs exposed
- Brand name text only (no brand logos in email)

</specifics>

<code_context>
## Existing Code Insights

### Reusable Assets
- `backend/app/modules/evaluations/`: Existing evaluation data access patterns -- email service can reuse evaluation queries
- `backend/app/core/dependencies.py`: Auth middleware for protecting the email endpoint
- `frontend/src/locales/id.json`: Indonesian translation keys for category/metric names -- backend should mirror these
- `frontend/src/lib/categoryMap.ts`: CATEGORY_MAP for backend-to-display name mapping
- `frontend/src/lib/verdictCounts.ts`: Verdict counting logic (computeVerdictCounts, computeCategoryVerdictCounts)

### Established Patterns
- Backend modules follow: router.py, service.py, schemas.py pattern (see accounts, auth, brands, evaluations)
- FastAPI dependency injection for auth/DB
- Frontend dashboard components: PresentationDashboard, ScoreOverview, DetailedEvaluation, ScoreBreakdownChart, DataIntelligence
- Charts use Recharts (RadarChart, RadialBarChart with ResponsiveContainer) -- need frontend capture to PNG in Phase 2

### Integration Points
- New email router registered in backend/app/main.py
- Email service needs DB session access (same pattern as other modules)
- Evaluation data model from evaluations module
- Branded images from my-designs/images/ need to be accessible to backend (copy to backend/assets or similar)

</code_context>

<deferred>
## Deferred Ideas

- Editable subject line UI -- Phase 2/3 (backend already supports optional subject param)
- English language toggle -- future (backend template uses string dict, ready for expansion)

</deferred>

---

*Phase: 01-backend-email-engine*
*Context gathered: 2026-03-06*
