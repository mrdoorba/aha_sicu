# Dashboard Email Report

## What This Is

A feature that lets users send a rich HTML email containing the brand evaluation Dashboard — scores, detailed breakdown, charts rendered as static images, and data intelligence — directly from the Dashboard page. Built on top of the existing AHA SICU evaluation platform.

## Core Value

Users can share a visually complete brand evaluation report via email without screenshots or manual formatting.

## Requirements

### Validated

(None yet — ship to validate)

### Active

- [ ] User can send an HTML email that visually matches the PresentationDashboard layout
- [ ] Email includes score overview, detailed evaluation breakdown, chart as static image, and data intelligence
- [ ] ScoreBreakdownChart is rendered as a PNG image embedded in the email
- [ ] User enters recipient email address(es) manually each time
- [ ] Send Email button is located in the DashboardHeader component
- [ ] Backend API endpoint accepts dashboard data and sends HTML email via Gmail SMTP
- [ ] SMTP credentials configured via environment variables (works with personal Gmail or Google Workspace)
- [ ] User sees a dialog to enter recipients and preview before sending
- [ ] Email sends from whichever Gmail account is configured in env vars

### Out of Scope

- Replacing the existing mailto flow on the History page — that stays as-is
- Scheduled/automated email sending
- Email delivery tracking or read receipts
- PDF attachment generation
- Non-Gmail email providers (for now — SMTP abstraction allows future swap)

## Context

- The existing app has a `PresentationDashboard` component that renders: `DashboardHeader`, `ScoreOverview`, `DetailedEvaluation`, `ScoreBreakdownChart`, `DataIntelligence`, `DashboardFooter`
- There's already a `SendMailDialog` on the History page using `mailto:` for plain-text emails — this new feature is separate
- The app runs on GCP: Cloud Run (backend), Firebase Hosting (frontend), Cloud SQL (PostgreSQL)
- Backend is FastAPI (Python), frontend is React + TypeScript
- Charts use a frontend charting library that needs to be rendered to static PNG for email embedding
- The app uses Indonesian locale (`i18next` with `id.json`)

## Constraints

- **Email service**: Gmail SMTP (personal or Workspace) — configurable via env vars (`SMTP_HOST`, `SMTP_PORT`, `SMTP_USER`, `SMTP_PASSWORD`)
- **Gmail limits**: 500/day personal, 2000/day Workspace — sufficient for internal use
- **HTML email compatibility**: Must render correctly in major email clients (Gmail, Outlook, Apple Mail)
- **Chart rendering**: Charts must be converted to static images since email clients don't support JavaScript

## Key Decisions

| Decision | Rationale | Outcome |
|----------|-----------|---------|
| Gmail SMTP over Resend/SendGrid | Simplest setup, no new service dependency, free, flexible (personal or company Gmail) | — Pending |
| Backend sends email (not mailto:) | mailto: can't send HTML emails; backend gives full control over formatting | — Pending |
| Charts as static PNG images | Email clients don't support interactive JS charts; PNG is universally supported | — Pending |
| Dashboard page only | Keep existing History page mailto flow unchanged; separate concern | — Pending |
| Env var SMTP config | Allows swapping between personal/company Gmail without code changes | — Pending |

---
*Last updated: 2026-03-06 after initialization*
