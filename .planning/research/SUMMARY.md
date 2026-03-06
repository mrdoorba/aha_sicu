# Project Research Summary

**Project:** AHA SICU - Dashboard Email Report Feature
**Domain:** HTML email report generation from evaluation dashboard
**Researched:** 2026-03-06
**Confidence:** HIGH

## Executive Summary

This feature adds the ability to send the AHA SICU evaluation dashboard as a formatted HTML email with an embedded radar chart image. The domain is well-understood: HTML email rendering is a solved but notoriously constrained problem (table-based layout, inline CSS, CID image embedding). The recommended approach splits responsibility cleanly: the frontend captures the Recharts radar chart as a PNG using `html-to-image`, while the backend generates purpose-built email HTML from structured evaluation data, embeds the chart via CID attachment, and sends through Gmail SMTP using `aiosmtplib`.

The stack additions are minimal -- three Python packages (`aiosmtplib`, `jinja2`, `premailer`) and one JS package (`html-to-image`). No new infrastructure or services are needed. The existing FastAPI module pattern (`router.py`, `service.py`, `schemas.py`) extends naturally with domain-specific `html_builder.py` and `smtp_client.py` files. The backend loads evaluation data from the database (using the existing `get_evaluation_detail` query), so the frontend only sends `evaluation_id` + `recipients` + `chart_image` (base64).

The single biggest risk is email client rendering fidelity. Outlook uses Microsoft Word's HTML engine, Gmail strips `<style>` blocks, and no client supports modern CSS. The HTML template must be table-based with inline styles from day one -- retrofitting is a full rewrite. Secondary risks include Gmail App Password setup (not account password) and ensuring CID image embedding displays inline rather than as an attachment. Both are well-documented and preventable with correct implementation from the start.

## Key Findings

### Recommended Stack

The feature requires minimal new dependencies, all well-established and version-verified.

**Core technologies:**
- `aiosmtplib` (5.1.0): Async SMTP client -- required because the backend is fully async (FastAPI + asyncpg); synchronous `smtplib` would block the event loop
- `jinja2` (3.1.6): HTML email template rendering -- provides auto-escaping (critical for security) and clean separation of HTML structure from data
- `premailer` (3.10.0): CSS inlining -- converts `<style>` blocks to inline `style=""` attributes, the only reliable cross-client approach
- `html-to-image` (1.11.13): Frontend chart capture -- serializes SVG DOM nodes faithfully (unlike `html2canvas` which struggles with SVG)

**What NOT to add:** `fastapi-mail` (unnecessary wrapper), Puppeteer/Playwright (massive Docker bloat for Cloud Run), `html2canvas` (poor SVG support), SendGrid/Resend (overkill for low-volume internal tool).

### Expected Features

**Must have (table stakes):**
- Send Email button in DashboardHeader
- Recipient input dialog with multi-recipient support
- Score overview, detailed evaluation, chart, and data intelligence sections in email
- Visual fidelity with dashboard (table-based HTML mirroring dashboard layout)
- Loading/sending state feedback and clear error messages
- Auto-generated subject line with brand name and date

**Should have (differentiators):**
- Email preview before sending (builds user confidence)
- Custom message/note field
- CC/BCC fields
- Success confirmation with recipient list

**Defer (v2+):**
- Scheduled/recurring reports (massive scope)
- Email delivery tracking (requires webhook infrastructure)
- PDF attachment generation (separate rendering pipeline)
- Contact/address book management
- Recently used recipients (localStorage convenience)

### Architecture Approach

The architecture follows a clean frontend-capture / backend-build split. The frontend's only new job is capturing the radar chart as PNG and providing a send dialog. The backend owns all HTML generation, SMTP sending, and data loading. The `evaluation_id`-based approach (not full data payload) keeps the backend as source of truth and minimizes request size.

**Major components:**
1. `SendReportDialog` (frontend) -- recipient input, optional note, send trigger
2. `useEmailReport` hook (frontend) -- chart capture via `html-to-image`, API mutation
3. `email/router.py` (backend) -- POST endpoint with auth and validation
4. `email/service.py` (backend) -- orchestrates: load eval, build HTML, send SMTP
5. `email/html_builder.py` (backend) -- pure function: evaluation data + chart CID -> HTML string
6. `email/smtp_client.py` (backend) -- async SMTP with CID attachment handling

### Critical Pitfalls

1. **HTML email with web CSS assumptions** -- Email clients do not support flexbox, grid, or CSS variables. Build with table-based layout and inline styles from day one. Retrofitting is a full rewrite.
2. **Recharts not server-renderable** -- Recharts requires browser DOM and `ResponsiveContainer` needs measured dimensions. Use frontend `html-to-image` capture, not server-side rendering.
3. **Gmail SMTP auth requires App Password** -- Google killed "less secure app access" in 2022. Must use App Password (requires 2FA enabled first), not account password.
4. **CID images shown as attachments** -- Use `MIMEMultipart('related')` (not `'mixed'`), set `Content-Disposition: inline`, and match `Content-ID` angle brackets exactly.
5. **HTML content injection** -- Never use f-strings with user data. Use Jinja2 auto-escaping for all interpolated values.

## Implications for Roadmap

Based on research, the feature has a clear dependency chain that dictates build order. The HTML email template is the highest-risk, highest-effort item and should start early. SMTP integration is the first validation gate.

### Phase 1: Backend Foundation (SMTP + Config)
**Rationale:** Nothing works without email sending capability. Validate Gmail SMTP auth first -- if it fails, everything else is blocked.
**Delivers:** Working async SMTP client, SMTP config in Settings, email schemas (request/response Pydantic models)
**Addresses:** SMTP integration (table stakes), error handling foundation
**Avoids:** Pitfall 3 (Gmail App Password auth), Pitfall 6 (sync SMTP blocking)

### Phase 2: HTML Email Template
**Rationale:** This is the hardest and highest-risk component. It is a pure function with no dependencies on other new code, so it can be built and tested in isolation with sample data. Starting early allows time for cross-client iteration.
**Delivers:** `html_builder.py` -- complete HTML email from evaluation data + chart CID reference. Table-based layout, inline CSS, all dashboard sections represented.
**Addresses:** Visual fidelity (table stakes), score overview, detailed evaluation, data intelligence sections
**Avoids:** Pitfall 1 (web CSS in email), Pitfall 5 (HTML injection via Jinja2 auto-escaping)

### Phase 3: Backend Integration (Service + Router)
**Rationale:** Depends on Phase 1 (SMTP client) and Phase 2 (HTML builder). Wires everything together: loads evaluation from DB, calls html_builder, sends via smtp_client.
**Delivers:** Working POST `/api/v1/email/send` endpoint that accepts evaluation_id + recipients + chart_image and sends a complete HTML email
**Addresses:** Backend API endpoint (table stakes), email subject line generation

### Phase 4: Frontend Integration
**Rationale:** Depends on Phase 3 (needs working API endpoint). Adds `html-to-image`, chart ref, hook, dialog, and button.
**Delivers:** Complete user-facing flow: Send Email button -> dialog -> chart capture -> API call -> success/error toast
**Addresses:** Send Email button, recipient dialog, loading states, chart-to-PNG capture (all table stakes)
**Avoids:** Pitfall 2 (server-side chart rendering -- uses frontend capture instead)

### Phase 5: Testing + Polish
**Rationale:** Integration testing across the full flow. Cross-client email testing is essential -- Outlook alone represents 40%+ of corporate email users.
**Delivers:** Verified rendering in Gmail (web + mobile), Outlook (desktop + web), Apple Mail. Edge case handling (long brand names, missing data, Indonesian text/UTF-8).
**Addresses:** Mobile-friendly email rendering (table stakes), Gmail clipping check (<102KB)
**Avoids:** Pitfall 4 (CID images as attachments -- verified inline display)

### Phase Ordering Rationale

- **Phases 1-3 are backend-only** and can be developed/tested without touching the frontend (use curl with hardcoded chart images). This minimizes context-switching.
- **Phase 2 (html_builder) is parallelizable** with Phase 1 -- it has zero dependencies on SMTP code. Both can proceed simultaneously.
- **Phase 4 depends on Phase 3** -- the frontend needs a working API endpoint to integrate against.
- **Phase 5 is inherently last** -- cross-client testing requires the complete flow to be functional.

### Research Flags

Phases likely needing deeper research during planning:
- **Phase 2 (HTML Email Template):** Email client CSS support is well-documented but the specific layout translation (dashboard sections to table-based email) requires careful implementation. The html_builder is the most code-intensive component. Research the exact evaluation data shape to design section builders.
- **Phase 4 (Frontend Integration):** Validate `html-to-image` works with the specific Recharts RadarChart + `ResponsiveContainer` setup. CSS variables in SVG may need explicit color values for capture. Run a quick spike before building the full hook.

Phases with standard patterns (skip research-phase):
- **Phase 1 (SMTP + Config):** Well-documented `aiosmtplib` usage, standard Settings extension pattern.
- **Phase 3 (Service + Router):** Follows existing module pattern exactly (router -> service -> queries).
- **Phase 5 (Testing):** Standard email testing workflow, no novel patterns.

## Confidence Assessment

| Area | Confidence | Notes |
|------|------------|-------|
| Stack | HIGH | All package versions verified locally via `uv pip install --dry-run` and `npm info`. Well-established libraries with no exotic choices. |
| Features | HIGH | Clear project requirements, well-understood domain. Table stakes are unambiguous. |
| Architecture | HIGH | Clean separation follows existing codebase patterns. Frontend-capture approach avoids infrastructure changes. |
| Pitfalls | HIGH | HTML email pitfalls are extensively documented by the industry. Gmail SMTP constraints are well-known. |

**Overall confidence:** HIGH

### Gaps to Address

- **html-to-image + Recharts RadarChart compatibility:** Needs a quick spike to confirm `toPng()` captures the SVG chart correctly, especially with CSS variables for colors. Run this validation at the start of Phase 4.
- **Gmail App Password availability in 2026:** Google's auth policies evolve. Confirm App Passwords are still supported before committing to this approach. If deprecated, `xoauth2` with a service account is the fallback.
- **Outlook rendering of specific table structures:** The exact table layout for score breakdowns and data intelligence sections needs cross-client testing. Budget iteration time in Phase 5.
- **Email size vs Gmail 102KB clip threshold:** The final email with inline chart PNG must stay under 102KB. If the chart image is large, may need JPEG compression or reduced `pixelRatio`.

## Sources

### Primary (HIGH confidence)
- Package versions verified locally: `aiosmtplib==5.1.0`, `jinja2==3.1.6`, `premailer==3.10.0`, `html-to-image@1.11.13`
- Existing codebase analysis: PresentationDashboard, DashboardHeader, ScoreBreakdownChart, SendMailDialog, module patterns
- Project requirements from `.planning/PROJECT.md`

### Secondary (MEDIUM confidence)
- Email client CSS support constraints (emailclientcss.com reference, industry standard knowledge)
- Gmail SMTP App Password requirements (Google disabled less secure apps May 2022)
- MIME standards: RFC 2387 for `multipart/related` CID references
- Recharts SVG rendering behavior and `ResponsiveContainer` browser dependency

### Tertiary (LOW confidence)
- Gmail App Password availability in 2026 (policy may have changed -- needs validation)
- `html-to-image` behavior with CSS variables inside SVG (needs spike/POC)

---
*Research completed: 2026-03-06*
*Ready for roadmap: yes*
