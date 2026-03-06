# Dashboard Email Report

## What This Is

A feature that lets users send a rich HTML email containing the brand evaluation Dashboard — scores, detailed breakdown, charts rendered as static images, and data intelligence — directly from the Dashboard page. Includes multi-recipient To/CC/BCC, custom notes, and in-dialog email preview. Built on top of the existing AHA SICU evaluation platform.

## Core Value

Users can share a visually complete brand evaluation report via email without screenshots or manual formatting.

## Requirements

### Validated

- ✓ User can send an HTML email that visually matches the PresentationDashboard layout — v1.0
- ✓ Email includes score overview, detailed evaluation breakdown, chart as static image, and data intelligence — v1.0
- ✓ ScoreBreakdownChart is rendered as a PNG image embedded in the email — v1.0
- ✓ User enters recipient email address(es) manually each time — v1.0
- ✓ Send Email button is located in the DashboardHeader component — v1.0
- ✓ Backend API endpoint accepts dashboard data and sends HTML email via Gmail SMTP — v1.0
- ✓ SMTP credentials configured via environment variables (works with personal Gmail or Google Workspace) — v1.0
- ✓ User sees a dialog to enter recipients and preview before sending — v1.0
- ✓ Email sends from whichever Gmail account is configured in env vars — v1.0

### Active

(None — next milestone will define new requirements)

### Out of Scope

- Replacing the existing mailto flow on the History page — that stays as-is
- Scheduled/automated email sending — massive scope (cron, scheduling UI, timezones)
- Email delivery tracking or read receipts
- PDF attachment generation — separate rendering pipeline
- Non-Gmail email providers (SMTP abstraction allows future swap)
- Template customization — fixed template matching dashboard
- Contact/address book — overkill for internal tool

## Context

Shipped v1.0 with ~48,500 LOC (27K Python + 21K TypeScript).
Tech stack: FastAPI (Python), React + TypeScript, GCP (Cloud Run, Firebase Hosting, Cloud SQL).
Email: Gmail SMTP with CID inline images, table-based HTML template with Indonesian localization.
Frontend: html-to-image for chart capture, custom EmailChipInput component, iframe preview.
All 21 requirements satisfied. 1 low-severity tech debt item (apiClient type casting).

## Constraints

- **Email service**: Gmail SMTP (personal or Workspace) — configurable via env vars (`SMTP_HOST`, `SMTP_PORT`, `SMTP_USER`, `SMTP_PASSWORD`)
- **Gmail limits**: 500/day personal, 2000/day Workspace — sufficient for internal use
- **HTML email compatibility**: Must render correctly in major email clients (Gmail, Outlook, Apple Mail)
- **Chart rendering**: Charts must be converted to static images since email clients don't support JavaScript

## Key Decisions

| Decision | Rationale | Outcome |
|----------|-----------|---------|
| Gmail SMTP over Resend/SendGrid | Simplest setup, no new service dependency, free, flexible (personal or company Gmail) | ✓ Good — works reliably, no cost |
| Backend sends email (not mailto:) | mailto: can't send HTML emails; backend gives full control over formatting | ✓ Good — full HTML control |
| Charts as static PNG images | Email clients don't support interactive JS charts; PNG is universally supported | ✓ Good — html-to-image + forwardRef works |
| Dashboard page only | Keep existing History page mailto flow unchanged; separate concern | ✓ Good — clean separation |
| Env var SMTP config | Allows swapping between personal/company Gmail without code changes | ✓ Good — flexible |
| CID images over data URIs (email) | Data URIs blocked by many email clients; CID is universal | ✓ Good — reliable cross-client |
| Data URIs for preview | Preview in iframe needs self-contained HTML; CID not applicable | ✓ Good — works in sandboxed iframe |
| Custom EmailChipInput (no library) | Interaction simple enough, avoids dependency | ✓ Good — lightweight, full control |
| Template params *_src (not *_cid) | Supports both cid: and data: URI for email vs preview | ✓ Good — dual-mode flexibility |
| BCC via to_addrs only | Never as header — proper BCC privacy | ✓ Good — correct SMTP behavior |

---
*Last updated: 2026-03-06 after v1.0 milestone*
