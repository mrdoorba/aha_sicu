# Architecture Patterns

**Domain:** Dashboard-to-Email Report System
**Researched:** 2026-03-06

## Recommended Architecture

The email report system adds three new components to the existing stack and touches two existing ones. The core insight: all evaluation data already lives server-side (the `EvaluationDetail` response contains everything the dashboard renders), so the backend should own HTML generation. The frontend's only new responsibilities are (1) capturing a chart screenshot as PNG and (2) providing a send-email dialog.

```
Frontend (existing)                          Backend (new module)
+---------------------------+                +---------------------------+
| PresentationDashboard     |                | modules/email/            |
|   DashboardHeader         |                |   router.py               |
|     [Send Email button]---+---> Dialog     |   service.py              |
|   ScoreOverview           |     |          |   schemas.py              |
|   DetailedEvaluation      |     |          |   html_builder.py         |
|   ScoreBreakdownChart ----+---> PNG        |   smtp_client.py          |
|   DataIntelligence        |     |          +---------------------------+
|   DashboardFooter         |     |                    |
+---------------------------+     |                    v
                                  |          +---------------------------+
                                  +--------> | POST /api/v1/email/send   |
                                   JSON +    |   - evaluation_id         |
                                   base64    |   - recipients[]          |
                                   PNG       |   - chart_image (base64)  |
                                             +---------------------------+
                                                       |
                                                       v
                                             +---------------------------+
                                             | Gmail SMTP (aiosmtplib)   |
                                             +---------------------------+
```

### Component Boundaries

| Component | Responsibility | Communicates With |
|-----------|---------------|-------------------|
| **SendReportDialog** (frontend) | Recipient input, preview trigger, send action | DashboardHeader (trigger), useEmailReport hook (send), ScoreBreakdownChart (chart image) |
| **useEmailReport hook** (frontend) | Capture chart as PNG, call send API, manage loading/error state | apiClient (HTTP), html-to-image or recharts ref (chart capture) |
| **email router** (backend) | HTTP endpoint validation, auth | email service |
| **email service** (backend) | Orchestrate: load evaluation, build HTML, embed image, send via SMTP | html_builder, smtp_client, evaluation queries |
| **html_builder** (backend) | Pure function: evaluation data + chart PNG -> complete HTML email string | None (pure) |
| **smtp_client** (backend) | Async SMTP send with attachment handling | Gmail SMTP server (external) |

### Data Flow

```
1. User clicks "Send Email" in DashboardHeader
2. SendReportDialog opens with recipient input fields
3. User enters recipient(s) and clicks Send
4. Frontend captures ScoreBreakdownChart as PNG via html-to-image/canvas
5. Frontend POSTs to /api/v1/email/send:
   {
     evaluation_id: number,
     recipients: string[],
     chart_image: string (base64-encoded PNG)
   }
6. Backend loads full EvaluationDetail from DB (same query as GET /evaluations/{id})
7. html_builder constructs table-based HTML email:
   - Score overview section (inline CSS, no charts -- just numbers)
   - Detailed evaluation table (all categories, all metrics)
   - Chart section (embed base64 PNG as CID-attached inline image)
   - Data intelligence section (ads + top SKU tables)
   - Footer with evaluator + date
8. smtp_client sends multipart/related email:
   - text/html part (the HTML email)
   - image/png part (CID-referenced chart)
9. Backend returns success/failure to frontend
10. Frontend shows toast notification
```

## Patterns to Follow

### Pattern 1: Backend HTML Generation (Not Frontend-to-Backend HTML Pass-Through)

**What:** The backend generates the HTML email from structured evaluation data, not from HTML passed by the frontend.

**When:** Always for this feature.

**Why:** Frontend HTML uses Tailwind/CSS variables/JS interactivity that email clients cannot render. The backend must produce table-based, inline-CSS HTML specifically for email. Passing rendered frontend HTML would require a full browser rendering pipeline (headless Chrome) which is unnecessary complexity.

**Example:**
```python
# backend/app/modules/email/html_builder.py

def build_email_html(
    evaluation: EvaluationDetail,
    chart_image_cid: str,
) -> str:
    """Build complete HTML email from evaluation data.

    Uses table-based layout with inline CSS for email client compatibility.
    """
    sections = [
        _build_header(evaluation.brand_name, evaluation.period, evaluation.template),
        _build_score_overview(evaluation.final_score, evaluation.score_breakdown),
        _build_detailed_evaluation(evaluation.score_breakdown),
        _build_chart_section(chart_image_cid),
        _build_data_intelligence(evaluation.calculator_results),
        _build_footer(evaluation.evaluator_email, evaluation.created_at),
    ]
    return _wrap_email_shell("\n".join(sections))
```

### Pattern 2: CID-Attached Inline Images (Not Base64 Data URIs)

**What:** Embed the chart PNG as a MIME attachment referenced by Content-ID (CID), not as a base64 data URI in the `<img src>`.

**When:** For the ScoreBreakdownChart image in the email.

**Why:** Gmail strips `data:` URIs from emails. CID attachment is the universally supported way to embed images in HTML emails. The image is attached as a related MIME part and referenced via `<img src="cid:chart-image">`.

**Example:**
```python
# In smtp_client.py
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.image import MIMEImage

msg = MIMEMultipart("related")
html_part = MIMEText(html_body, "html", "utf-8")
msg.attach(html_part)

chart_img = MIMEImage(chart_bytes, _subtype="png")
chart_img.add_header("Content-ID", "<chart-image>")
chart_img.add_header("Content-Disposition", "inline", filename="chart.png")
msg.attach(chart_img)
```

### Pattern 3: New Backend Module Following Existing Convention

**What:** Create `backend/app/modules/email/` with `router.py`, `service.py`, `schemas.py` plus domain-specific `html_builder.py` and `smtp_client.py`.

**When:** For all email-related backend code.

**Why:** Follows the established module pattern (router -> service -> queries). The `html_builder` and `smtp_client` are analogous to how the `sync` module has `sheets_client.py` and `upload` has `gcs_client.py` -- domain-specific clients alongside the standard trio.

### Pattern 4: Frontend Chart Capture via html-to-image

**What:** Use `html-to-image` (or the built-in `recharts` ref approach) to capture the `ScoreBreakdownChart` DOM element as a PNG blob.

**When:** Right before sending the email, not proactively.

**Why:** Recharts renders to SVG in the DOM. Email clients do not support SVG reliably. The simplest approach is to capture the rendered chart DOM node as a rasterized PNG on the frontend, then send it to the backend as base64. This avoids needing a headless browser on the server.

**Implementation approach:**
```typescript
// useEmailReport.ts
import { toPng } from 'html-to-image';

async function captureChart(chartRef: RefObject<HTMLDivElement>): Promise<string> {
  if (!chartRef.current) throw new Error('Chart ref not available');
  const dataUrl = await toPng(chartRef.current, {
    backgroundColor: '#ffffff',
    pixelRatio: 2,  // crisp on retina
  });
  return dataUrl.split(',')[1]; // strip data:image/png;base64, prefix
}
```

### Pattern 5: Table-Based Email HTML with Inline Styles

**What:** All email HTML uses `<table>` layout with inline `style` attributes. No `<div>` layout, no CSS classes, no external stylesheets.

**When:** For all HTML generated by `html_builder.py`.

**Why:** Email clients (especially Outlook) strip `<style>` blocks, ignore CSS classes, and do not support flexbox/grid. Table-based layout with inline styles is the only reliable cross-client approach. This is well-established email development practice.

**Key constraints for the builder:**
- Max width: 600px (standard email width)
- Font stack: system fonts only (`Arial, Helvetica, sans-serif`)
- Colors: hardcoded hex values (no CSS variables)
- Images: CID references only (no external URLs, no data URIs)
- No `background-image` (Outlook ignores it)

## Anti-Patterns to Avoid

### Anti-Pattern 1: Server-Side Chart Rendering

**What:** Using Puppeteer/Playwright/headless Chrome on the backend to render the Recharts radar chart.

**Why bad:** Adds massive dependency (headless Chrome ~400MB), increases Cloud Run cold start time significantly, requires complex container setup, and is completely unnecessary since the chart is already rendered on the user's screen.

**Instead:** Capture the chart as PNG on the frontend using `html-to-image` and send it as base64 to the backend.

### Anti-Pattern 2: Sending Frontend-Rendered HTML Directly

**What:** Rendering the entire PresentationDashboard to HTML on the frontend and sending that HTML to the backend for emailing.

**Why bad:** Frontend HTML uses Tailwind utility classes, CSS custom properties (`var(--primary)`), responsive layouts, and interactive components (tabs, animations). None of this renders in email clients. The result would look broken in every email client.

**Instead:** Backend generates purpose-built email HTML from the structured evaluation data.

### Anti-Pattern 3: Using External Image URLs

**What:** Uploading the chart PNG to GCS and linking it via URL in the email.

**Why bad:** Many email clients block external images by default (showing "click to load images" prompts). The chart is the most visually important part of the report -- it should display immediately without user action.

**Instead:** CID-attached inline image, which displays without requiring the user to "load external images."

### Anti-Pattern 4: Template Engine Complexity

**What:** Using Jinja2 or another template engine for the email HTML.

**Why bad for this case:** Adds a dependency for what is essentially a single, fixed-layout email. The HTML structure is static (same sections every time), only the data values change. Python f-strings or string building with helper functions are simpler and easier to maintain for a single template.

**Exception:** If multiple email templates are needed in the future, introduce Jinja2 at that point. For one template, keep it simple.

### Anti-Pattern 5: Synchronous SMTP Sending

**What:** Using Python's built-in `smtplib` (synchronous) in the async FastAPI handler.

**Why bad:** Blocks the event loop during SMTP connection and send, degrading performance for all concurrent requests. SMTP operations involve network I/O (TLS handshake, authentication, data transfer) that can take 2-10 seconds.

**Instead:** Use `aiosmtplib` for async SMTP, or at minimum wrap `smtplib` in `asyncio.to_thread()`.

## Key Architectural Decisions

### Decision 1: Frontend Captures Chart, Backend Builds Everything Else

The chart is the only component that requires visual rendering (SVG to raster). Everything else (scores, tables, text) can be reconstructed from structured data into email-safe HTML by the backend. This split minimizes what the frontend needs to do (just capture one DOM node) and keeps HTML generation logic testable on the backend.

### Decision 2: evaluation_id, Not Full Data Payload

The frontend sends `evaluation_id` to the email endpoint, and the backend loads the evaluation data from the database. This is better than the frontend sending all evaluation data because:
- Reduces payload size
- Backend is the source of truth
- Backend already has the query (`get_evaluation_detail`)
- Prevents frontend from sending modified/stale data

### Decision 3: No Email Preview on Backend

The frontend dialog shows a simplified preview (just recipient list + confirmation). The actual HTML email is generated on the backend at send time. A "preview exactly what will be sent" feature would require the backend to return the rendered HTML for display, which adds a round-trip and complexity. Defer this unless users specifically request it.

### Decision 4: Settings Extension for SMTP

Add SMTP config to the existing `Settings` class in `backend/app/config.py`:
```python
# SMTP (Gmail)
smtp_host: str = "smtp.gmail.com"
smtp_port: int = 587
smtp_user: str = ""
smtp_password: str = ""
```

This follows the existing pattern where all config is centralized in `Settings` via env vars.

## Build Order (Dependencies Between Components)

The components have clear dependency ordering:

```
Phase 1: Backend Foundation (no frontend changes needed)
  1a. SMTP config in Settings (config.py) -- trivial, unblocks everything
  1b. smtp_client.py -- async SMTP send, testable in isolation
  1c. email schemas (schemas.py) -- request/response shapes

Phase 2: HTML Builder (no frontend changes needed)
  2a. html_builder.py -- pure function, extensively unit-testable
      Input: evaluation data dict + chart CID string
      Output: HTML string
      Can be developed and tested with hardcoded sample data

Phase 3: Backend Integration
  3a. email service.py -- orchestrates: load eval, build HTML, send SMTP
  3b. email router.py -- POST endpoint, auth, validation
  3c. Register router in main.py

Phase 4: Frontend Integration
  4a. Add html-to-image dependency
  4b. Chart ref on ScoreBreakdownChart (pass ref from parent)
  4c. useEmailReport hook (capture chart, call API)
  4d. SendReportDialog component (recipient input, send button)
  4e. Add Send Email button to DashboardHeader

Phase 5: Testing + Polish
  5a. Backend unit tests (html_builder, smtp_client mock, service)
  5b. Frontend tests (dialog, hook with mocked API)
  5c. Manual email client testing (Gmail, Outlook, Apple Mail)
```

**Why this order:**
- Phases 1-3 are backend-only and can be developed/tested without touching the frontend at all (use curl/httpie with hardcoded chart images for testing)
- Phase 2 (html_builder) is the most complex piece and benefits from being developed as a pure, isolated function with unit tests
- Phase 4 depends on Phase 3 (needs the API endpoint to exist)
- Phase 5 is integration testing across the full flow

**Key dependency chain:**
```
config.py SMTP settings
  -> smtp_client.py
    -> email service.py
      -> email router.py
        -> frontend hook + dialog
```

`html_builder.py` has NO dependencies on other new code -- it can be built in parallel with `smtp_client.py`.

## Existing Code Integration Points

| Existing Code | How Email Feature Touches It |
|--------------|------------------------------|
| `backend/app/config.py` (Settings) | Add 4 SMTP env vars |
| `backend/app/main.py` | Register email router |
| `frontend/src/services/apiClient.ts` | Add email endpoint type to paths interface |
| `frontend/src/components/dashboard/DashboardHeader.tsx` | Add Send Email button |
| `frontend/src/components/dashboard/ScoreBreakdownChart.tsx` | Accept optional `ref` for chart capture |
| `frontend/src/components/dashboard/PresentationDashboard.tsx` | Wire up dialog + chart ref |
| `backend/app/modules/evaluations/service.py` | Reuse `get_evaluation_detail()` -- no changes needed |

## Sources

- Existing codebase analysis (PresentationDashboard, DashboardHeader, ScoreBreakdownChart, all dashboard components)
- Existing module patterns (sync/sheets_client.py, upload/gcs_client.py as precedent for domain-specific clients)
- Existing SendMailDialog (History page mailto flow -- confirms the separation of concerns)
- Python `email.mime` stdlib documentation (CID attachment pattern)
- Recharts uses SVG rendering (confirmed from ScoreBreakdownChart source -- RadarChart renders to SVG via ResponsiveContainer)
- Email client compatibility constraints (table-based layout, inline CSS) -- established industry knowledge, HIGH confidence

---

*Architecture research: 2026-03-06*
