# Phase 1: Backend Email Engine - Research

**Researched:** 2026-03-06
**Domain:** Python SMTP email sending, HTML email templates, CID inline images
**Confidence:** HIGH

## Summary

Phase 1 builds a new `email` module in the existing FastAPI backend that accepts an evaluation ID + base64 chart image, fetches all evaluation data from Cloud SQL, renders a cross-client HTML email template, and sends it via Gmail SMTP with CID-embedded images (header, footer, radar chart). The backend already has well-established module patterns (router/service/schemas), an existing evaluation detail endpoint that returns all the data needed, and Firebase auth middleware ready to protect the new endpoint.

Python's standard library (`smtplib` + `email.message.EmailMessage`) handles everything needed -- STARTTLS, HTML with inline CID images, and SMTP auth. No third-party email libraries are required. The HTML template must use table-based layout with inline CSS (no `<style>` blocks) because Gmail strips `<style>` tags and Outlook uses the Word rendering engine. All three images (header, footer, chart) must be attached as `multipart/related` with Content-ID references.

**Primary recommendation:** Use Python stdlib `smtplib` + `email.message.EmailMessage` with `add_related()` for CID images. Build the HTML template as a Python string formatter with table-based layout and inline CSS. Follow the existing module pattern exactly (router.py, service.py, schemas.py, template.py).

<user_constraints>
## User Constraints (from CONTEXT.md)

### Locked Decisions
- HTML Template - Score Overview: Large number + horizontal progress bar (not radial chart). Shows score/100, colored progress bar, check/cross counts, template type. Color thresholds: green >= 80%, primary/blue >= 50%, orange < 50%.
- HTML Template - Detailed Evaluation: All categories stacked vertically. Each category shows all metric cards with full detail. 2-column grid on desktop, single column on mobile.
- HTML Template - Score Breakdown Chart: PNG radar chart image (CID inline) at top. Category bars with CSS progress bars and check/cross counts below.
- HTML Template - Data Intelligence: Ads Analysis as preformatted text. Top SKU: revenue + stock ranking tables, top 3 rows each.
- HTML Template - Header & Footer: AHACommerce branded header/footer images as CID inline. Brand name, period, verdict, template displayed below header. Custom note placeholder for Phase 3.
- HTML Template - General: Section headers only (no numbered prefixes). Table-based layout with inline CSS. All images embedded as CID.
- API Data Contract: POST /api/v1/email/send. Input: evaluation_id, recipient email, chart_image (base64), optional subject. Backend fetches evaluation data by ID. Requires Firebase auth. Response: {"success": true, "message_id": "...", "recipient": "..."}.
- API Module Structure: backend/app/modules/email/ with __init__.py, router.py, service.py, schemas.py, template.py.
- Preview endpoint: GET /api/v1/email/preview/{evaluation_id} (dev/staging only).
- Error Handling: Categorized SMTP errors with appropriate HTTP status codes. 422 for invalid evaluation_id or malformed chart_image. Validate recipient email format. Log failures only.
- Email Language: Indonesian only. Template strings in a Python dict. Mirror frontend id.json labels.
- SMTP: STARTTLS on port 587. Per-request connection. 30s timeout. EMAIL_ENABLED toggle. SMTP_PASSWORD via GCP Secret Manager.
- SMTP Env Vars: SMTP_HOST, SMTP_PORT, SMTP_USER, SMTP_PASSWORD, SMTP_FROM_NAME, SMTP_FROM_EMAIL, EMAIL_ENABLED.
- Testing: Mock SMTP. Full content verification. HTML snapshot test. File output debug mode. Preview endpoint.

### Claude's Discretion
- Exact inline CSS styling and spacing
- HTML table nesting structure for email layout
- Progress bar CSS implementation in email
- Responsive email media query breakpoints
- Python SMTP library choice (smtplib vs aiosmtplib)
- Test fixture data structure

### Deferred Ideas (OUT OF SCOPE)
- Editable subject line UI -- Phase 2/3
- English language toggle -- future
</user_constraints>

<phase_requirements>
## Phase Requirements

| ID | Description | Research Support |
|----|-------------|-----------------|
| INFRA-01 | Backend API endpoint accepts evaluation data + chart image and sends HTML email | Existing module pattern (router/service/schemas) + smtplib + EmailMessage API |
| INFRA-02 | SMTP credentials configured via environment variables | pydantic-settings BaseSettings pattern already in config.py -- add SMTP fields |
| INFRA-03 | Email sent via Gmail SMTP | Gmail App Passwords still work (2026) with 2FA enabled, STARTTLS port 587 |
| INFRA-04 | HTML email template uses table-based layout with inline CSS | Table layout + inline CSS required for Gmail (strips style tags) and Outlook (Word engine) |
| INFRA-05 | Chart PNG embedded as CID inline image | EmailMessage.add_related() with make_msgid() for CID references |
| INFRA-06 | Configurable sender display name via env var | SMTP_FROM_NAME env var, set in EmailMessage From header |
| CONT-01 | Email includes score overview | Data available from get_evaluation_detail: final_score, verdict, template, score_breakdown |
| CONT-02 | Email includes detailed evaluation breakdown | score_breakdown contains CategoryScoreItem list with full RowScoreItem detail |
| CONT-03 | Email includes ScoreBreakdownChart as static PNG | chart_image base64 in request body, decoded and attached as CID inline image |
| CONT-04 | Email includes data intelligence section | calculator_results dict contains ads_keyword and top_sku data |
| CONT-05 | Email renders correctly on mobile devices | Responsive via media queries in style block (Gmail mobile app supports some), table width fallbacks |
| CONT-06 | Email subject auto-generated with brand name and period | "Laporan Evaluasi Brand: [Brand Name] - [Period]" format, optional override param |
</phase_requirements>

## Standard Stack

### Core
| Library | Version | Purpose | Why Standard |
|---------|---------|---------|--------------|
| smtplib | stdlib (Python 3.14) | SMTP connection and sending | Built-in, no dependencies, handles STARTTLS, proven stable |
| email.message.EmailMessage | stdlib (Python 3.14) | Email composition with CID attachments | Modern API with add_alternative/add_related, official Python recommendation |
| email.utils.make_msgid | stdlib (Python 3.14) | Generate unique Content-IDs | Standard way to create CID references for inline images |
| pydantic | >=2.0 (via FastAPI) | Request/response schemas | Already used across all modules |
| pydantic-settings | >=2.6.0 | SMTP env var config | Already used in app/config.py Settings class |

### Supporting
| Library | Version | Purpose | When to Use |
|---------|---------|---------|-------------|
| base64 | stdlib | Decode chart_image from request body | Every email send request |
| logging | stdlib | Log SMTP failures | Error paths only (per decision) |

### Alternatives Considered
| Instead of | Could Use | Tradeoff |
|------------|-----------|----------|
| smtplib (sync) | aiosmtplib | Async SMTP, but adds dependency for minimal gain -- per-request connection is fast enough. smtplib in a thread executor is fine for FastAPI. |
| String templates | Jinja2 | More features but overkill -- template is a single function returning HTML string. No user-editable templates. |

**Recommendation (Claude's Discretion - SMTP library):** Use `smtplib` (sync) wrapped in `asyncio.to_thread()` for FastAPI compatibility. The per-request SMTP connection is a short-lived blocking call (~1-3s). This avoids adding aiosmtplib as a dependency and keeps the stack simpler. Python 3.14 stdlib is sufficient.

**Installation:**
```bash
# No additional packages needed -- all stdlib
# Just add SMTP config fields to existing Settings class
```

## Architecture Patterns

### Recommended Module Structure
```
backend/app/modules/email/
    __init__.py          # Empty or exports
    router.py            # POST /send, GET /preview/{id}
    service.py           # send_email(), build_email_message()
    schemas.py           # SendEmailRequest, SendEmailResponse
    template.py          # render_email_html(), STRINGS dict, section renderers
```

### Pattern 1: Follow Existing Module Pattern
**What:** Mirror the router/service/schemas pattern used by evaluations, brands, accounts modules.
**When to use:** Always -- this is the established project convention.
**Example:**
```python
# router.py - follows exact same pattern as evaluations/router.py
from fastapi import APIRouter, Depends
from app.core.dependencies import get_current_user
from app.modules.email.schemas import SendEmailRequest, SendEmailResponse
from app.modules.email.service import send_evaluation_email

router = APIRouter(prefix="/api/v1/email", tags=["email"])

@router.post("/send", response_model=SendEmailResponse)
async def send_email_endpoint(
    body: SendEmailRequest,
    current_user: dict = Depends(get_current_user),
) -> SendEmailResponse:
    return await send_evaluation_email(
        evaluation_id=body.evaluation_id,
        recipient=body.recipient,
        chart_image_b64=body.chart_image,
        subject=body.subject,
    )
```

### Pattern 2: EmailMessage with Multiple CID Images
**What:** Build MIME multipart/alternative message with text fallback + HTML, attach 3 CID images (header, footer, chart).
**When to use:** For the email composition in service.py.
**Example:**
```python
# Source: https://docs.python.org/3/library/email.examples.html
from email.message import EmailMessage
from email.utils import make_msgid
import smtplib

def build_email_message(
    *,
    subject: str,
    from_name: str,
    from_email: str,
    to_email: str,
    html_content: str,
    text_content: str,
    images: list[tuple[bytes, str, str]],  # (data, subtype, cid)
) -> EmailMessage:
    msg = EmailMessage()
    msg["Subject"] = subject
    msg["From"] = f"{from_name} <{from_email}>"
    msg["To"] = to_email

    # Plain text fallback
    msg.set_content(text_content)

    # HTML alternative
    msg.add_alternative(html_content, subtype="html")

    # Attach CID images to HTML part
    html_part = msg.get_payload()[1]
    for img_data, img_subtype, cid in images:
        html_part.add_related(img_data, "image", img_subtype, cid=cid)

    return msg
```

### Pattern 3: SMTP Send with Error Categorization
**What:** Per-request SMTP connection with categorized error handling, run in thread executor.
**When to use:** In service.py for the actual send operation.
**Example:**
```python
import asyncio
import smtplib
from app.core.exceptions import AppException

async def smtp_send(msg: EmailMessage) -> str:
    """Send email via SMTP in a thread (non-blocking for FastAPI)."""
    try:
        return await asyncio.to_thread(_smtp_send_sync, msg)
    except AppException:
        raise
    except Exception as e:
        raise AppException(
            code="SMTP_UNKNOWN_ERROR",
            detail=f"Unexpected SMTP error: {e}",
            status_code=502,
        ) from e

def _smtp_send_sync(msg: EmailMessage) -> str:
    try:
        with smtplib.SMTP(settings.smtp_host, settings.smtp_port, timeout=30) as server:
            server.starttls()
            server.login(settings.smtp_user, settings.smtp_password)
            server.send_message(msg)
            return msg["Message-ID"] or ""
    except smtplib.SMTPAuthenticationError as e:
        raise AppException(code="SMTP_AUTH_ERROR", detail="SMTP authentication failed", status_code=502) from e
    except smtplib.SMTPConnectError as e:
        raise AppException(code="SMTP_CONNECTION_ERROR", detail="Failed to connect to SMTP server", status_code=502) from e
    except TimeoutError as e:
        raise AppException(code="SMTP_TIMEOUT", detail="SMTP connection timed out", status_code=504) from e
```

### Pattern 4: Template with Localized Strings Dict
**What:** All user-visible strings in a dictionary keyed by language code, template functions take data and return HTML.
**When to use:** In template.py for all email content rendering.
**Example:**
```python
STRINGS = {
    "id": {
        "score_overview": "Ringkasan Skor",
        "detailed_evaluation": "Evaluasi Detail",
        "score_breakdown": "Rincian Skor",
        "data_intelligence": "Data Inteligensi",
        "ads_analysis": "Analisis Iklan",
        "top_sku": "Top SKU",
        "revenue_ranking": "Peringkat Omzet",
        "stock_ranking": "Peringkat Stok",
        "metric": "Metrik",
        "value": "Nilai",
        "benchmark": "Benchmark",
        "verdict": "Keputusan",
        "score": "Skor",
        "message": "Pesan",
        "approved": "Disetujui",
        "rejected": "Ditolak",
        # ... mirror frontend id.json keys
    }
}
```

### Pattern 5: Debug File Output Mode
**What:** When SMTP is not configured or debug flag is set, write rendered HTML to a local file instead of sending.
**When to use:** During development and template iteration.
**Example:**
```python
import pathlib

async def send_evaluation_email(...) -> SendEmailResponse:
    html = render_email_html(evaluation_data, chart_image, header_image, footer_image)

    if not settings.email_enabled:
        # Debug mode: save to file
        debug_path = pathlib.Path(f"/tmp/email_preview_{evaluation_id}.html")
        debug_path.write_text(html)
        return SendEmailResponse(success=True, message_id="debug-file", recipient=recipient)

    # ... build and send actual email
```

### Anti-Patterns to Avoid
- **Using `<style>` blocks in HTML email:** Gmail strips them entirely. Use inline `style=""` attributes on every element.
- **Using div-based layout:** Outlook uses Word engine for rendering. Tables are the only reliable layout primitive.
- **Using data: URIs for images:** Many email clients block data URIs. CID inline attachments are the standard.
- **Async SMTP without thread isolation:** smtplib is blocking -- calling it directly in async code blocks the event loop. Always use `asyncio.to_thread()`.
- **Hardcoding Indonesian strings inline:** Makes future English support painful. Use the STRINGS dict pattern.

## Don't Hand-Roll

| Problem | Don't Build | Use Instead | Why |
|---------|-------------|-------------|-----|
| Email composition with attachments | Custom MIME assembly | `email.message.EmailMessage` | Handles multipart/alternative + multipart/related structure correctly |
| Content-ID generation | Random string concatenation | `email.utils.make_msgid()` | Generates RFC-compliant Message-IDs with proper format |
| Email address validation | Custom regex | `pydantic.EmailStr` or basic regex | Pydantic handles RFC 5322 validation |
| SMTP connection management | Manual socket handling | `smtplib.SMTP` context manager | Handles EHLO, STARTTLS, cleanup automatically |
| Base64 image decoding | Manual parsing | `base64.b64decode()` | Handles padding, validation |

**Key insight:** Python's stdlib email package has a modern API (EmailMessage) that handles the complex MIME structure for HTML emails with inline images. The older MIMEMultipart approach still works but is more verbose.

## Common Pitfalls

### Pitfall 1: Gmail Strips Style Blocks
**What goes wrong:** CSS in `<style>` tags is removed by Gmail, leaving unstyled content.
**Why it happens:** Gmail's security policy strips `<head>` content and `<style>` tags.
**How to avoid:** Every visual element needs `style=""` inline. No exceptions.
**Warning signs:** Email looks fine in preview HTML file but ugly in Gmail.

### Pitfall 2: Outlook Word Engine Rendering
**What goes wrong:** Padding, margins, border-radius don't work. Float/flexbox/grid ignored entirely.
**Why it happens:** Outlook desktop uses the Microsoft Word HTML engine, not a browser engine.
**How to avoid:** Use `<table>`, `<tr>`, `<td>` for ALL layout. Use `cellpadding`, `cellspacing`, `bgcolor` attributes (not just CSS). Avoid border-radius on critical elements.
**Warning signs:** Layout broken in Outlook but fine elsewhere.

### Pitfall 3: CID Image Not Displaying
**What goes wrong:** Image shows as broken icon or attachment instead of inline.
**Why it happens:** CID format mismatch -- `make_msgid()` returns `<id@domain>` but HTML needs just `id@domain` (without angle brackets).
**How to avoid:** Strip angle brackets: `cid = make_msgid()` then in HTML use `cid:{cid[1:-1]}`.
**Warning signs:** Images show as attachments at bottom of email.

### Pitfall 4: Gmail 102KB Clipping
**What goes wrong:** Gmail clips the email with "View entire message" link, hiding content below.
**Why it happens:** Gmail clips emails larger than ~102KB of HTML.
**How to avoid:** Keep HTML minimal -- no unnecessary whitespace, short class names (or none), compact inline styles. The detailed evaluation section with all metrics could be large.
**Warning signs:** Email cuts off partway through in Gmail.

### Pitfall 5: Blocking the FastAPI Event Loop
**What goes wrong:** API becomes unresponsive during email sending.
**Why it happens:** `smtplib` is synchronous -- calling it in async handler blocks the loop.
**How to avoid:** Wrap in `asyncio.to_thread()` for the SMTP send operation.
**Warning signs:** Other API requests stall while email is being sent.

### Pitfall 6: Base64 Chart Image Validation
**What goes wrong:** Invalid base64 data causes crash during email composition.
**Why it happens:** Frontend sends malformed base64 or includes the `data:image/png;base64,` prefix.
**How to avoid:** Validate and strip data URI prefix before decoding. Return 422 with clear message on failure.
**Warning signs:** Intermittent 500 errors on send.

## Code Examples

### Email Configuration in Settings
```python
# Add to backend/app/config.py Settings class
# Source: existing pattern in config.py

# Email / SMTP
smtp_host: str = "smtp.gmail.com"
smtp_port: int = 587
smtp_user: str = ""
smtp_password: str = ""
smtp_from_name: str = "AHA Commerce"
smtp_from_email: str = ""
email_enabled: bool = False
```

### Request Schema
```python
# backend/app/modules/email/schemas.py
from pydantic import BaseModel, EmailStr, Field

class SendEmailRequest(BaseModel):
    evaluation_id: int
    recipient: EmailStr
    chart_image: str = Field(..., description="Base64-encoded PNG chart image")
    subject: str | None = Field(default=None, max_length=200)

class SendEmailResponse(BaseModel):
    success: bool
    message_id: str
    recipient: str
```

### HTML Table Layout Pattern for Email
```html
<!-- Outer wrapper table for email body -->
<table role="presentation" width="100%" cellpadding="0" cellspacing="0" border="0"
       style="background-color:#f5f5f5;">
  <tr>
    <td align="center" style="padding:20px 0;">
      <!-- Content table, 600px max width -->
      <table role="presentation" width="600" cellpadding="0" cellspacing="0" border="0"
             style="background-color:#ffffff; border-radius:8px;">
        <!-- Header image -->
        <tr>
          <td style="padding:0;">
            <img src="cid:{header_cid}" width="600" style="display:block; width:100%; height:auto;" alt="AHA Commerce">
          </td>
        </tr>
        <!-- Content sections go here -->
      </table>
    </td>
  </tr>
</table>
```

### Progress Bar in Email (CSS-only)
```html
<!-- Score progress bar using nested tables -->
<table role="presentation" width="100%" cellpadding="0" cellspacing="0" border="0">
  <tr>
    <td style="background-color:#e0e0e0; border-radius:4px; height:12px; padding:0;">
      <table role="presentation" width="{score_pct}%" cellpadding="0" cellspacing="0" border="0">
        <tr>
          <td style="background-color:{color}; border-radius:4px; height:12px; font-size:0; line-height:0;">
            &nbsp;
          </td>
        </tr>
      </table>
    </td>
  </tr>
</table>
```

### Verdict Counting in Python (mirrors frontend verdictCounts.ts)
```python
def compute_verdict_counts(categories: list[dict]) -> dict:
    checks = 0
    xs = 0
    for cat in categories:
        for row in cat.get("rows", []):
            if row.get("verdict") == "\u2714\ufe0f":  # check mark
                checks += 1
            elif row.get("verdict") == "\u274c":  # cross mark
                xs += 1
    total = checks + xs
    score = round((checks / total) * 100) if total > 0 else 0
    return {"checks": checks, "xs": xs, "total": total, "score": score}
```

### Category Name Mapping (mirrors frontend categoryMap.ts)
```python
CATEGORY_MAP: dict[str, str] = {
    "Kesehatan Operasional Toko": "Operasional",
    "Bisnis Analisis": "Bisnis",
    "Tinjauan Pengunjung": "Pengunjung",
    "Promo Toko": "Alat Promo",
    "Jumlah Produk & Status Toko": "Produk & Status",
    "Data Iklan": "Iklan",
    "Partisipasi Campaign": "Campaign",
    "Kompetisi TOP Produk": "Kompetisi",
    "Stok": "Stok",
    "Discount": "Diskon",
}
```

## State of the Art

| Old Approach | Current Approach | When Changed | Impact |
|--------------|------------------|--------------|--------|
| MIMEMultipart/MIMEText/MIMEImage | EmailMessage with add_alternative/add_related | Python 3.6+ | Cleaner API, less boilerplate |
| Gmail "Less Secure Apps" | App Passwords with 2FA | Sept 2024 | Must use App Password, not regular password |
| CSS in `<style>` blocks | All inline CSS | Always (email) | Gmail strips style blocks; inline is the only reliable approach |

**Gmail SMTP status (verified 2026):** App Passwords still work with 2FA enabled. STARTTLS on port 587 is the recommended connection method. Gmail enforces a 500 emails/day limit for consumer accounts, 2000/day for Workspace.

## Open Questions

1. **Header/footer image file access from backend**
   - What we know: Images exist at `my-designs/images/aha-e-mail-header-2026.png` and `aha-e-mail-footer-2026.png`
   - What's unclear: Whether to copy to `backend/assets/` or read from `my-designs/` at runtime
   - Recommendation: Copy to `backend/app/modules/email/assets/` during implementation -- keeps the module self-contained and avoids path issues in Docker/Cloud Run deployment

2. **Evaluation data structure for calculator_results**
   - What we know: It's a dict with keys like `ads_keyword`, `top_sku` containing `details` and `output_text`
   - What's unclear: Exact structure of `details` dict for Top SKU (revenue ranking, stock ranking tables)
   - Recommendation: Inspect actual database data or frontend component that renders it to confirm field names

## Validation Architecture

### Test Framework
| Property | Value |
|----------|-------|
| Framework | pytest 8.0+ with pytest-asyncio |
| Config file | backend/pyproject.toml `[tool.pytest.ini_options]` |
| Quick run command | `cd backend && uv run pytest tests/unit/ -x -q` |
| Full suite command | `cd backend && uv run pytest -v` |

### Phase Requirements -> Test Map
| Req ID | Behavior | Test Type | Automated Command | File Exists? |
|--------|----------|-----------|-------------------|-------------|
| INFRA-01 | POST /api/v1/email/send accepts data and sends email | unit | `uv run pytest tests/unit/email/test_service.py -x` | Wave 0 |
| INFRA-02 | SMTP config loaded from env vars | unit | `uv run pytest tests/unit/email/test_config.py -x` | Wave 0 |
| INFRA-03 | Email sent via Gmail SMTP (mocked) | unit | `uv run pytest tests/unit/email/test_service.py::test_smtp_send -x` | Wave 0 |
| INFRA-04 | HTML uses table layout with inline CSS | unit | `uv run pytest tests/unit/email/test_template.py -x` | Wave 0 |
| INFRA-05 | Chart PNG embedded as CID inline image | unit | `uv run pytest tests/unit/email/test_service.py::test_cid_images -x` | Wave 0 |
| INFRA-06 | Sender display name from env var | unit | `uv run pytest tests/unit/email/test_service.py::test_from_header -x` | Wave 0 |
| CONT-01 | Score overview section rendered | unit | `uv run pytest tests/unit/email/test_template.py::test_score_overview -x` | Wave 0 |
| CONT-02 | Detailed evaluation breakdown rendered | unit | `uv run pytest tests/unit/email/test_template.py::test_detailed_evaluation -x` | Wave 0 |
| CONT-03 | Chart image appears as inline CID | unit | `uv run pytest tests/unit/email/test_service.py::test_chart_cid -x` | Wave 0 |
| CONT-04 | Data intelligence section rendered | unit | `uv run pytest tests/unit/email/test_template.py::test_data_intelligence -x` | Wave 0 |
| CONT-05 | Responsive table structure in HTML | unit | `uv run pytest tests/unit/email/test_template.py::test_responsive -x` | Wave 0 |
| CONT-06 | Subject auto-generated with brand+period | unit | `uv run pytest tests/unit/email/test_service.py::test_subject_generation -x` | Wave 0 |

### Sampling Rate
- **Per task commit:** `cd backend && uv run pytest tests/unit/email/ -x -q`
- **Per wave merge:** `cd backend && uv run pytest -v && uv run ruff check .`
- **Phase gate:** Full suite green before `/gsd:verify-work`

### Wave 0 Gaps
- [ ] `tests/unit/email/` -- directory does not exist
- [ ] `tests/unit/email/__init__.py` -- package init
- [ ] `tests/unit/email/test_template.py` -- covers INFRA-04, CONT-01 through CONT-05
- [ ] `tests/unit/email/test_service.py` -- covers INFRA-01, INFRA-03, INFRA-05, INFRA-06, CONT-03, CONT-06
- [ ] `tests/unit/email/conftest.py` -- shared fixtures (mock evaluation data, mock SMTP, sample base64 image)

## Sources

### Primary (HIGH confidence)
- [Python 3.14 email.examples](https://docs.python.org/3/library/email.examples.html) - EmailMessage API with CID inline images
- [Python 3.14 email.message](https://docs.python.org/3/library/email.message.html) - EmailMessage.add_related() and add_alternative() documentation
- Existing codebase: backend/app/modules/evaluations/ - established module pattern
- Existing codebase: backend/app/config.py - Settings pattern for env vars
- Existing codebase: backend/app/core/dependencies.py - Auth middleware pattern

### Secondary (MEDIUM confidence)
- [Gmail App Password Support](https://support.google.com/mail/answer/185833?hl=en) - App Passwords still available with 2FA (verified 2026)
- [Gmail SMTP Settings 2026](https://emailwarmup.com/blog/smtp/gmail-smtp-settings/) - STARTTLS port 587 confirmation
- [HTML/CSS in Emails 2026](https://designmodo.com/html-css-emails/) - Current email client CSS support
- [Email Development Best Practices](https://www.emailonacid.com/blog/article/email-development/email-development-best-practices-2/) - Table layout, inline CSS requirements

### Tertiary (LOW confidence)
- Gmail 102KB clipping threshold -- widely reported but not officially documented by Google

## Metadata

**Confidence breakdown:**
- Standard stack: HIGH - Python stdlib, no dependencies, official docs verified
- Architecture: HIGH - follows exact existing project patterns, all code inspected
- Pitfalls: HIGH - well-known email rendering issues, extensively documented
- Data structure: MEDIUM - evaluation detail response inspected but calculator_results internal structure needs runtime verification

**Research date:** 2026-03-06
**Valid until:** 2026-04-06 (stable domain -- email rendering standards move slowly)
