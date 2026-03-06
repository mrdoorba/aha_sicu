# Pitfalls Research

**Domain:** HTML email dashboard reports with embedded chart images
**Researched:** 2026-03-06
**Confidence:** HIGH (well-known domain with extensive community documentation of failure modes)

## Critical Pitfalls

### Pitfall 1: HTML Email Rendered with Web CSS Assumptions

**What goes wrong:**
The email HTML uses modern CSS (flexbox, grid, CSS variables, Tailwind utility classes, `gap`, `calc()`, `var(--*)`) and renders as a broken mess in Outlook, older Gmail, and Yahoo Mail. The dashboard looks perfect in Chrome but arrives as a jumbled wall of text.

**Why it happens:**
Developers reuse frontend component styles or write email HTML the same way they write web HTML. Email clients -- especially Outlook (which uses Word's rendering engine) -- support only a 2007-era subset of CSS. No flexbox, no grid, no CSS variables, no `gap`.

**How to avoid:**
- Build email templates with **table-based layout** from day one. Do not attempt to adapt the existing Tailwind/React component markup.
- Use only inline styles (no `<style>` blocks for critical layout -- Outlook strips `<head>` styles, Gmail strips `<style>` in some configurations).
- Stick to: `table`, `tr`, `td`, `padding`, `margin`, `background-color`, `color`, `font-family`, `font-size`, `font-weight`, `border`, `width`, `height`, `text-align`, `vertical-align`.
- Test with Litmus or Email on Acid, or at minimum send test emails to Gmail, Outlook (desktop + web), and Apple Mail.

**Warning signs:**
- Email template file contains `flex`, `grid`, `gap`, `var(--`, or Tailwind classes.
- Template reuses any React component markup directly.
- No cross-client testing has been done.

**Phase to address:**
Phase 1 (Email Template) -- this must be correct from the start. Retrofitting table layout into a flexbox template is a full rewrite.

---

### Pitfall 2: Recharts RadarChart Cannot Be Rendered Server-Side to PNG

**What goes wrong:**
The team assumes they can render the existing `ScoreBreakdownChart` (Recharts `RadarChart` with `ResponsiveContainer`) on the backend to produce a PNG. Recharts is a React/browser library that requires a DOM. Attempting to use it in Node.js SSR or Python produces errors or blank images. `ResponsiveContainer` specifically requires a measured parent element width/height, which does not exist outside a browser.

**Why it happens:**
Recharts renders to SVG inside React's virtual DOM with browser layout measurements. There is no built-in `toImage()` or server-side rendering capability. Developers discover this only after wiring up the entire email pipeline.

**How to avoid:**
Two viable approaches, pick one:

1. **Frontend canvas capture (recommended for this project):** Use `html-to-image` or `html2canvas` to capture the rendered chart as a PNG in the browser before sending. The frontend sends the base64 PNG to the backend along with the email request. This reuses the exact visual output the user sees.
2. **Backend chart generation:** Use a Python charting library (matplotlib, plotly) to regenerate the radar chart on the backend. This means maintaining two chart implementations (Recharts frontend + matplotlib backend) that must stay visually aligned.

Do NOT attempt: puppeteer/playwright on the server to render the React component -- massive dependency, slow, fragile, and overkill for one chart.

**Warning signs:**
- Architecture plan says "render Recharts on the server."
- No spike/POC for chart-to-image conversion has been done before building the email pipeline.
- `ResponsiveContainer` is in the component (it will produce 0x0 output without a browser).

**Phase to address:**
Phase 1 (Chart Image) -- validate the approach with a working POC before building any email template that depends on having a chart image.

---

### Pitfall 3: Gmail SMTP with Username/Password Rejected -- App Passwords Required

**What goes wrong:**
The backend uses `smtplib` with `SMTP_USER` and `SMTP_PASSWORD` env vars, but Gmail rejects the login with "Application-specific password required" or "Less secure app access" errors. The developer's personal Gmail works locally but the production/staging account does not.

**Why it happens:**
Google disabled "less secure app access" permanently in 2022. Standard Gmail accounts require either:
- An **App Password** (requires 2FA enabled on the account first), or
- **OAuth 2.0** (complex setup, overkill for server-to-server sending).

Google Workspace accounts may have additional admin policies that block SMTP.

**How to avoid:**
- Document clearly: the `SMTP_PASSWORD` env var must contain a **Gmail App Password**, not the account password.
- Add setup instructions: enable 2FA on the Gmail account first, then generate an App Password at `myaccount.google.com/apppasswords`.
- For Google Workspace: ensure the admin has not disabled "Less secure apps" or App Passwords for the organization.
- Test SMTP auth in isolation before integrating into the email pipeline.

**Warning signs:**
- README/setup docs say "enter your Gmail password."
- No mention of App Passwords in configuration docs.
- Works locally with one account, fails in CI/staging with another.

**Phase to address:**
Phase 1 (SMTP Setup) -- first thing to validate. If SMTP auth does not work, nothing else matters.

---

### Pitfall 4: Embedded Images Blocked or Shown as Attachments

**What goes wrong:**
Charts are embedded using CID (Content-ID) references in a MIME multipart message, but Gmail web shows them as attachments at the bottom instead of inline. Or images are embedded as base64 `data:` URIs and Gmail strips them entirely (Gmail blocks `data:` URIs in `<img src>`). The email arrives with a broken image icon where the chart should be.

**Why it happens:**
Email clients handle image embedding inconsistently:
- **`data:` URIs:** Gmail, Outlook.com, and Yahoo all strip these. Do not use them.
- **CID attachments:** Work in most clients but Gmail web sometimes displays them as attachments. The `Content-Disposition` must be `inline` (not `attachment`) and the `Content-ID` header must match the `cid:` reference exactly.
- **Hosted images:** Most reliable, but requires a publicly accessible URL and may be blocked by corporate proxies.

**How to avoid:**
- Use **CID embedding** with correct MIME structure: `Content-Disposition: inline`, `Content-ID: <chart123>`, referenced as `<img src="cid:chart123">`.
- Use Python's `email.mime` module correctly -- `MIMEImage` with `add_header('Content-ID', '<chart123>')` and `add_header('Content-Disposition', 'inline', filename='chart.png')`.
- Never use `data:` URIs in email HTML.
- Set a reasonable image width in the HTML (`width="600"` attribute on the `<img>` tag, not CSS `max-width`).
- Test in Gmail (web), Gmail (mobile), Outlook (desktop), and Apple Mail.

**Warning signs:**
- `<img src="data:image/png;base64,..."` appears in email template code.
- Images show as attachments in Gmail but inline in Apple Mail.
- `Content-ID` header missing angle brackets (must be `<id>` not just `id`).

**Phase to address:**
Phase 2 (Email Assembly) -- when building the MIME message with the chart image.

---

### Pitfall 5: Email HTML Content Injection / XSS via User Data

**What goes wrong:**
Brand names, evaluator emails, or evaluation data are interpolated directly into the HTML template without escaping. A brand name like `<script>alert('xss')</script>` or `"; DROP TABLE evaluations; --` ends up in the email. While email clients generally do not execute JavaScript, malformed HTML from unescaped data can break the entire email layout (unclosed tags, broken tables).

**Why it happens:**
Developers use f-strings or `.format()` to build the HTML template and forget that user-provided data may contain HTML special characters (`<`, `>`, `&`, `"`).

**How to avoid:**
- Use a proper template engine (Jinja2, which FastAPI already supports) with auto-escaping enabled.
- Never use f-strings to build HTML with user data.
- Sanitize all user-provided values with `markupsafe.escape()` or Jinja2's `{{ value }}` auto-escaping.

**Warning signs:**
- HTML template built with Python f-strings containing user data.
- No template engine dependency in requirements.
- Template strings contain `{brand_name}` instead of `{{ brand_name }}`.

**Phase to address:**
Phase 2 (Email Template Rendering) -- when building the template engine integration.

---

### Pitfall 6: Sending Email Synchronously Blocks the API Response

**What goes wrong:**
The `/api/send-email` endpoint connects to Gmail SMTP and sends the email synchronously. SMTP connections take 2-10 seconds (DNS resolution, TLS handshake, authentication, data transfer, server response). The user clicks "Send" and stares at a spinner for 5+ seconds. If Gmail is slow or temporarily unavailable, the request times out after 30 seconds and the user gets a 500 error.

**Why it happens:**
The simplest implementation is synchronous: receive request, build email, send email, return response. Developers do the simple thing first and never revisit.

**How to avoid:**
For this project's scale (internal tool, low volume), synchronous is acceptable IF:
- SMTP timeout is set to 10 seconds max.
- Frontend shows immediate feedback ("Sending...") and handles timeouts gracefully.
- Error messages are user-friendly ("Could not send email. Please try again.").

If latency becomes a problem later, move to background sending with `BackgroundTasks` in FastAPI (built-in, zero dependencies).

**Warning signs:**
- No timeout set on `smtplib.SMTP` connection.
- No loading state in the frontend send dialog.
- Users report the send button "does nothing" (it is just waiting).

**Phase to address:**
Phase 2 (API Endpoint) -- set timeouts from the start. Add `BackgroundTasks` only if needed.

---

## Technical Debt Patterns

| Shortcut | Immediate Benefit | Long-term Cost | When Acceptable |
|----------|-------------------|----------------|-----------------|
| Hardcoded HTML string instead of template engine | Faster to build | Unmaintainable, no escaping, painful to update layout | Never -- Jinja2 setup takes 30 minutes |
| Frontend captures full dashboard screenshot instead of just chart | Avoids rebuilding layout in email HTML | Massive image (2-5MB), slow to send, looks blurry on mobile, Gmail may clip | Never -- email needs proper HTML layout |
| Synchronous SMTP without timeout | Simpler code | API hangs on SMTP failures | Only with explicit 10s timeout set |
| Duplicate chart logic in Python backend | No frontend changes needed | Two implementations drift apart visually | Acceptable if the chart is simple enough |
| Skip email client testing | Ship faster | Broken emails in Outlook (40%+ of corporate users) | Only for MVP if all recipients use Gmail |

## Integration Gotchas

| Integration | Common Mistake | Correct Approach |
|-------------|----------------|------------------|
| Gmail SMTP | Using account password instead of App Password | Generate App Password after enabling 2FA |
| Gmail SMTP | Not handling `SMTPAuthenticationError` specifically | Catch it, return clear error "SMTP credentials invalid -- check App Password" |
| Gmail SMTP | Sending from a different "From" address than the authenticated user | Gmail silently rewrites the From header to the authenticated user's address -- do not promise "send from any address" |
| Gmail SMTP | Not setting `SMTP_PORT` correctly | Port 587 with STARTTLS (not port 465 with implicit SSL, not port 25) |
| Recharts | Trying `ReactDOMServer.renderToString()` on Recharts components | Recharts needs browser layout; use `html-to-image` in browser instead |
| MIME email | Using `MIMEMultipart('mixed')` for HTML + inline images | Use `MIMEMultipart('related')` -- 'mixed' causes images to show as attachments |

## Performance Traps

| Trap | Symptoms | Prevention | When It Breaks |
|------|----------|------------|----------------|
| Large chart PNG (>500KB) | Email takes 5+ seconds to send, Gmail clips the email | Resize to 600px width, compress PNG, or use JPEG at 85% quality | Images over 1MB |
| No SMTP connection reuse | Each email takes 3-5 seconds for TLS handshake | Acceptable at current scale; use connection pooling only if sending batches | Sending >10 emails in quick succession |
| Gmail rate limits | Emails silently fail after 500/day (personal) or 2000/day (Workspace) | Log send attempts, monitor daily count, alert at 80% of limit | When team grows or testing is heavy |
| Building email HTML on every request | Slow response, high CPU on template rendering | Pre-compile Jinja2 templates (automatic with `Environment`) | Not a real concern at this scale |

## Security Mistakes

| Mistake | Risk | Prevention |
|---------|------|------------|
| SMTP credentials in source code or frontend env | Gmail account compromise | Backend-only env vars, never expose to frontend, use `.env` + `.gitignore` |
| No rate limiting on email endpoint | Abuse as spam relay if auth is bypassed | Add rate limit (e.g., 10 emails/minute per user) and require authentication |
| Accepting arbitrary recipient addresses without validation | Spam relay, reputation damage | Validate email format, consider allowlist for initial release |
| User data in email without HTML escaping | Broken email layout, potential phishing content injection | Jinja2 auto-escaping |
| Logging full email content including recipient PII | Privacy violation, compliance risk | Log only: sender, recipient count, timestamp, success/failure status |

## UX Pitfalls

| Pitfall | User Impact | Better Approach |
|---------|-------------|-----------------|
| No preview before sending | User sends email with wrong data, cannot recall | Show email preview in dialog before confirming send |
| No success/failure feedback | User does not know if email was sent | Toast notification on success, error dialog on failure with retry option |
| Recipient input as plain text field | Users enter malformed emails, no way to add multiple | Use chip/tag input that validates each email, supports multiple recipients |
| Email looks nothing like the dashboard | User loses trust in the tool | Match color scheme, layout structure, and data presentation closely |
| No indication of who the email comes from | Recipient confused by sender identity | Show "Email will be sent from: {configured_email}" in the send dialog |
| Dark mode dashboard generates light mode email (or vice versa) | Visual mismatch, user confusion | Always generate email in light mode (email clients have poor dark mode support) |

## "Looks Done But Isn't" Checklist

- [ ] **Email template:** Tested in Outlook desktop (Word renderer) -- not just Gmail and Apple Mail
- [ ] **Chart image:** Verified CID embedding shows inline (not as attachment) in Gmail web
- [ ] **SMTP auth:** Tested with App Password, not account password
- [ ] **Indonesian text:** Verified special characters and Indonesian text render correctly (UTF-8 encoding in MIME headers)
- [ ] **Long brand names:** Tested with very long brand names that might overflow table cells
- [ ] **Missing data:** Tested email when some evaluation fields are null/empty (no broken layout)
- [ ] **Error handling:** SMTP timeout, auth failure, and invalid recipient all return user-friendly errors
- [ ] **Mobile email:** Checked email renders on mobile Gmail and iOS Mail (responsive tables, not fixed 900px width)
- [ ] **Gmail clipping:** Email under 102KB total (Gmail clips messages over this size with "View entire message" link)
- [ ] **From header:** Verified the "From" name is meaningful (e.g., "AHA SICU Report" not "smtp.user.2024@gmail.com")

## Recovery Strategies

| Pitfall | Recovery Cost | Recovery Steps |
|---------|---------------|----------------|
| Wrong CSS approach (flexbox in email) | HIGH | Full template rewrite to table-based layout |
| Server-side Recharts rendering fails | MEDIUM | Switch to frontend capture approach, adjust API contract to accept base64 image |
| SMTP auth not working | LOW | Generate App Password, update env var, redeploy |
| CID images showing as attachments | LOW | Fix MIME structure (use 'related', fix Content-ID headers) |
| No HTML escaping | MEDIUM | Introduce Jinja2 templates, migrate all string interpolation |
| Synchronous sending too slow | LOW | Wrap existing send logic in `BackgroundTasks`, return 202 Accepted |

## Pitfall-to-Phase Mapping

| Pitfall | Prevention Phase | Verification |
|---------|------------------|--------------|
| Gmail SMTP auth (App Password) | Phase 1: SMTP Setup | Successfully send a plain-text test email from FastAPI |
| Recharts not server-renderable | Phase 1: Chart POC | Generate a PNG of the radar chart and verify it visually matches |
| Wrong CSS in email (flexbox/grid) | Phase 2: Email Template | Template uses only tables + inline styles, tested in Outlook |
| CID image embedding broken | Phase 2: Email Assembly | Chart image displays inline in Gmail web, Outlook, Apple Mail |
| HTML content injection | Phase 2: Template Engine | All user data goes through Jinja2 auto-escaping |
| Synchronous API blocking | Phase 2: API Endpoint | Timeout set, loading state in UI, error handling works |
| Gmail clipping (>102KB) | Phase 3: Testing | Final email size measured and under 102KB |
| Cross-client rendering | Phase 3: Testing | Verified in Gmail (web+mobile), Outlook (desktop+web), Apple Mail |
| Email looks unlike dashboard | Phase 3: Visual QA | Side-by-side comparison of dashboard vs. email |

## Sources

- Recharts documentation: Recharts is a React-based charting library requiring browser DOM for rendering. `ResponsiveContainer` requires a parent with measured dimensions.
- Gmail SMTP: Google disabled less secure app access in May 2022. App Passwords are the only non-OAuth SMTP auth method.
- Email client CSS support: emailclientcss.com documents the CSS subset supported by each email client. Outlook uses Microsoft Word's HTML renderer.
- Gmail clipping: Messages over ~102KB are clipped with a "View entire message" link.
- MIME standards: RFC 2387 defines `multipart/related` for inline content references via Content-ID.
- Python `email` module: `MIMEMultipart('related')` is required for CID-referenced inline images; `'mixed'` treats them as attachments.

---
*Pitfalls research for: HTML email dashboard reports with embedded chart images*
*Researched: 2026-03-06*
