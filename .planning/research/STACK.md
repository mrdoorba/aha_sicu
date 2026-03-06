# Technology Stack: Dashboard Email Report

**Project:** AHA SICU - Dashboard Email Report Feature
**Researched:** 2026-03-06
**Overall confidence:** MEDIUM (web search/fetch tools unavailable; versions verified via local package managers, rationale based on training data + project constraints)

## Recommended Stack

This stack adds email-sending capability to the existing FastAPI backend and chart-to-image capture on the existing React frontend. No new services or infrastructure required.

### Email Sending (Backend)

| Technology | Version | Purpose | Why |
|------------|---------|---------|-----|
| `aiosmtplib` | 5.1.0 | Async SMTP client | The backend is fully async (FastAPI + asyncpg). Using stdlib `smtplib` would block the event loop. `aiosmtplib` is the standard async SMTP library for Python, well-maintained, and supports STARTTLS for Gmail SMTP. Verified available at 5.1.0. |
| `email` (stdlib) | built-in | MIME message construction | Python's `email.mime` module handles multipart/related messages with inline image attachments (CID embedding). No external lib needed for message assembly. |

### Email Templating (Backend)

| Technology | Version | Purpose | Why |
|------------|---------|---------|-----|
| `jinja2` | 3.1.6 | HTML email template rendering | Industry standard Python template engine. Supports template inheritance, filters, conditionals. Already used internally by FastAPI (though not as a direct dependency here). Generates the HTML email body from dashboard data. |
| `premailer` | 3.10.0 | CSS inlining for email compatibility | Email clients (especially Gmail, Outlook) strip `<style>` tags. `premailer` converts CSS rules to inline `style=""` attributes, which is the only reliable cross-client approach. Essential for HTML emails that render correctly everywhere. |

### Chart-to-Image (Frontend)

| Technology | Version | Purpose | Why |
|------------|---------|---------|-----|
| `html-to-image` | 1.11.13 | Capture Recharts RadarChart as PNG | Converts any DOM node to PNG/JPEG using SVG foreignObject serialization (no canvas taint issues). Works natively with Recharts since Recharts renders SVG. Lighter and more reliable than `html2canvas` for SVG-based charts. The captured PNG gets sent to the backend as base64 in the API request. |

### No Additional Frontend Libraries Needed

The email dialog UI (recipient input, preview, send button) uses the existing component library:
- Radix UI primitives (Dialog, Input, Button) -- already installed
- react-hook-form -- already installed for form validation
- Sonner -- already installed for success/error toast notifications
- TanStack Query -- already installed for the mutation hook

## Alternatives Considered

| Category | Recommended | Alternative | Why Not |
|----------|-------------|-------------|---------|
| SMTP client | `aiosmtplib` | `smtplib` (stdlib) | Synchronous -- would block the FastAPI event loop. Would need `run_in_executor()` wrapper, adding complexity for no benefit. |
| SMTP client | `aiosmtplib` | `fastapi-mail` | Wrapper around `aiosmtplib` that adds Jinja2 integration. Adds a dependency for convenience we don't need -- we're already using Jinja2 directly and want explicit control over MIME construction for CID image embedding. |
| Email service | Gmail SMTP | SendGrid / Resend / AWS SES | Adds external service dependency, API keys, billing. Gmail SMTP is free, needs no new account, and handles the expected volume (internal tool, <100 emails/day). PROJECT.md explicitly chose Gmail SMTP. |
| CSS inlining | `premailer` | `css-inline` (Rust-based) | `css-inline` is faster but `premailer` is more battle-tested for email-specific edge cases (handling of `<table>` layouts, media query preservation). Performance difference irrelevant for sending one email at a time. |
| CSS inlining | `premailer` | Manual inline styles in template | Fragile, hard to maintain. `premailer` lets you write normal CSS in `<style>` tags and auto-inlines it. |
| Chart capture | `html-to-image` | `html2canvas` | `html2canvas` re-renders the DOM to a Canvas element by parsing CSS manually. It struggles with SVG (which Recharts uses). `html-to-image` serializes the actual DOM including SVG, producing faithful output. |
| Chart capture | `html-to-image` (frontend) | Server-side rendering with Puppeteer/Playwright | Requires a headless browser on the backend (Cloud Run). Adds ~400MB to the Docker image, increases cold start time, adds complexity. The chart is already rendered in the user's browser -- just capture it there. |
| HTML templating | `jinja2` | `mjml` (via `mjml-python`) | MJML is designed for responsive email templates, but adds a compilation step (MJML -> HTML). Our email mirrors a fixed-width dashboard layout, not a responsive marketing email. Jinja2 with table-based HTML is simpler and sufficient. |

## Architecture Decision: Frontend Capture vs Server-Side Rendering

**Decision: Frontend captures the chart image, sends it to the backend with the email request.**

**Rationale:**
1. The Recharts RadarChart is already rendered in the browser with correct data, theming, and i18n labels
2. Server-side chart rendering would require replicating the entire React rendering pipeline (Node.js subprocess or headless browser on Cloud Run)
3. `html-to-image` produces a PNG from the existing DOM node in ~100ms -- zero additional rendering work
4. The PNG is small (~50-150KB for a radar chart) -- acceptable to send as base64 in a POST body
5. This approach requires zero infrastructure changes to Cloud Run

**Tradeoff:** The chart image quality depends on the user's screen. Mitigation: use `pixelRatio: 2` option in `html-to-image` for retina-quality output regardless of screen.

## Data Flow for Email Sending

```
Frontend                              Backend
--------                              -------
1. User clicks "Send Email"
2. html-to-image captures chart PNG
3. POST /api/v1/email/send            4. Receive request
   {                                  5. Validate with Pydantic schema
     recipients: [...],               6. Render Jinja2 HTML template
     dashboard_data: {...},              with dashboard_data
     chart_image: "base64..."         7. premailer inlines CSS
   }                                  8. Build MIME multipart/related:
                                         - HTML body (with cid: refs)
                                         - Chart PNG as inline attachment
                                      9. aiosmtplib sends via Gmail SMTP
                                      10. Return success/failure
```

## New Backend Dependencies

```bash
# Add to backend/pyproject.toml dependencies
cd backend
uv add aiosmtplib jinja2 premailer
```

This adds:
- `aiosmtplib==5.1.0` -- async SMTP
- `jinja2==3.1.6` -- templating (+ `markupsafe` transitive)
- `premailer==3.10.0` -- CSS inlining (+ `lxml`, `cssutils`, `cssselect` transitive)

## New Frontend Dependencies

```bash
# Add to frontend/package.json
cd frontend
npm install html-to-image
```

This adds:
- `html-to-image@1.11.13` -- DOM-to-image capture (zero transitive dependencies)

## Configuration Additions

New environment variables for `backend/app/config.py` Settings class:

```python
# SMTP Configuration (Gmail)
smtp_host: str = "smtp.gmail.com"
smtp_port: int = 587
smtp_user: str = ""           # Gmail address
smtp_password: str = ""       # Gmail App Password (not account password)
smtp_from_name: str = "AHA SICU"
```

**Gmail App Password note:** Gmail requires an "App Password" (not the account password) when 2FA is enabled. This is a 16-character code generated in Google Account settings. For Google Workspace, the admin may need to allow "Less secure apps" or configure App Passwords.

## Confidence Assessment

| Component | Confidence | Reason |
|-----------|------------|--------|
| `aiosmtplib` 5.1.0 | HIGH | Version verified via `uv pip install --dry-run`. Well-known async SMTP lib for Python. |
| `jinja2` 3.1.6 | HIGH | Version verified via `uv pip install --dry-run`. Industry standard, extremely stable. |
| `premailer` 3.10.0 | HIGH | Version verified via `uv pip install --dry-run`. Standard tool for email CSS inlining. |
| `html-to-image` 1.11.13 | HIGH | Version verified via `npm info`. Works well with SVG-based charts (Recharts). |
| Frontend capture approach | MEDIUM | Based on training data experience with `html-to-image` + Recharts. Needs validation that RadarChart renders correctly with `toPng()` (CSS variables in SVG may need explicit color values for the capture). |
| Gmail SMTP via App Password | MEDIUM | Standard approach but Google's auth policies evolve. Needs validation that App Passwords still work as expected in 2026. |
| `premailer` email client compat | MEDIUM | Battle-tested but email client rendering is inherently fragile. Template needs testing across Gmail, Outlook, Apple Mail. |

## What NOT to Use

| Technology | Why Not |
|------------|---------|
| `fastapi-mail` | Unnecessary abstraction over `aiosmtplib` + `jinja2`. Hides MIME construction details we need for CID image embedding. |
| `smtplib` (sync) | Blocks the event loop. |
| Puppeteer / Playwright on backend | Massive Docker image bloat, slow cold starts on Cloud Run, complex dependency. |
| `html2canvas` | Poor SVG support -- Recharts renders SVG charts. |
| `mjml` / `react-email` | Over-engineered for a single, fixed-layout report email. |
| `nodemailer` (Node.js) | Would require a separate Node.js service or sidecar. Backend is Python. |
| SendGrid / Resend / Mailgun | External service dependency, billing, API keys -- overkill for low-volume internal tool. |
| `weasyprint` / `wkhtmltoimage` | Server-side HTML-to-image converters. Require system-level dependencies (cairo, Qt). Fragile on Cloud Run. |

## Sources

- Package versions verified locally:
  - `aiosmtplib==5.1.0` via `uv pip install --dry-run aiosmtplib`
  - `jinja2==3.1.6` via `uv pip install --dry-run jinja2`
  - `premailer==3.10.0` via `uv pip install --dry-run premailer`
  - `html-to-image@1.11.13` via `npm info html-to-image version`
- Existing project stack from `.planning/codebase/STACK.md`
- Project requirements from `.planning/PROJECT.md`
- Chart component structure from `frontend/src/components/dashboard/ScoreBreakdownChart.tsx`

---

*Stack research: 2026-03-06*
