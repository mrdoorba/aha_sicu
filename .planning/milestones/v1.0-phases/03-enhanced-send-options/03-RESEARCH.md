# Phase 3: Enhanced Send Options - Research

**Researched:** 2026-03-06
**Domain:** Email compose UX (tag/chip input, CC/BCC, preview), backend multi-recipient SMTP
**Confidence:** HIGH

## Summary

Phase 3 extends the existing single-recipient send dialog into a full email compose experience. The codebase is well-structured for this: `SendEmailDialog.tsx` is a single component with clear boundaries, the backend `schemas.py` / `service.py` / `template.py` are cleanly separated, and the preview endpoint already exists (just needs the debug guard removed and data URI support added).

The main implementation areas are: (1) a tag/chip input component for email recipients, (2) Gmail-style CC/BCC reveal pattern, (3) custom note textarea with character counting, (4) iframe-based email preview with data URI images, and (5) backend schema + service updates for multi-recipient/CC/BCC/note support.

**Primary recommendation:** Build a custom `EmailChipInput` component (no library needed -- the interaction is Enter/comma to add, Backspace/x to remove, with email validation). Extend the backend schema to accept `recipients: list[EmailStr]`, `cc: list[EmailStr]`, `bcc: list[EmailStr]`, and `note: str | None`. Update `build_email_message` to set To/CC/BCC headers. Update `render_email_html` to accept an optional note parameter and render it as a styled card. Remove the debug guard on the preview endpoint and add data URI image support.

<user_constraints>
## User Constraints (from CONTEXT.md)

### Locked Decisions
- Tag/chip input: type email, press Enter or comma to create a chip, Backspace to remove last chip
- Chips are individually deletable (x button)
- PIC email from brand raw_data pre-filled as first chip (consistent with Phase 2)
- Maximum 10 recipients combined across To + CC + BCC
- Validate email format on add (reject invalid immediately, input highlighted red with brief message)
- Send button disabled until at least one valid To recipient exists
- Gmail-style "CC" and "BCC" text links next to the To label
- Clicking "CC" expands the CC field below To and hides the "CC" link
- Clicking "BCC" expands the BCC field below CC and hides the "BCC" link
- CC and BCC use the same tag/chip input component as To
- 10-recipient cap is combined total across all three fields
- Backend sends one email with To/CC/BCC headers (not individual emails per recipient)
- Plain textarea, labeled "Catatan (opsional)"
- 500 character limit with live character count shown below textarea
- Placed below recipient fields, above brand summary card and preview
- Line breaks preserved in email rendering
- In received email: rendered as a subtle card/box with light background, visually distinct from report content
- Positioned below header image and brand info, above Score Overview section
- Optional -- empty note means no note section in the email
- Expandable "Pratinjau Email" toggle section below the compose fields
- Collapsed by default, click to expand
- Renders backend HTML in a scrollable iframe (~300px height)
- Source: GET /api/v1/email/preview/{evaluation_id} endpoint
- Enable preview endpoint in production for authenticated users (remove debug-only guard)
- Pass custom note as query parameter so preview reflects the note
- Header and footer images rendered as base64 data URIs in preview (so they display in iframe)
- Chart image shows a placeholder in preview (chart is captured at send time, not preview time)

### Claude's Discretion
- Tag/chip input component implementation (custom or library)
- Exact dialog width adjustments to accommodate new fields
- Preview iframe styling and loading state
- Backend schema changes for multi-recipient/CC/BCC/note fields
- Preview endpoint query parameter design for custom note
- How to convert CID images to data URIs for preview mode
- Textarea height and resize behavior

### Deferred Ideas (OUT OF SCOPE)
- Editable subject line UI -- backend already supports optional subject param
- Recently used recipients from localStorage -- v2 (CONV-01)
- English language toggle -- future
</user_constraints>

<phase_requirements>
## Phase Requirements

| ID | Description | Research Support |
|----|-------------|-----------------|
| SEND-03 | User can send to multiple recipients (comma-separated or multi-input) | Tag/chip input component with Enter/comma triggers; backend `recipients: list[EmailStr]` schema; `build_email_message` To header accepts comma-joined list |
| SEND-04 | User can add CC and BCC recipients | Gmail-style CC/BCC reveal pattern; same chip input component reused; backend `cc`/`bcc` fields; `EmailMessage` CC header + BCC via `send_message` |
| SEND-05 | User can add a custom note/message above the report body | Textarea with 500-char limit + counter; backend `note` field; `render_email_html` inserts styled card between header and Score Overview |
| CONT-07 | User can preview the HTML email in-dialog before sending | Remove debug guard on preview endpoint; add `note` query param; convert CID images to data URIs for browser rendering; frontend iframe with srcdoc |
</phase_requirements>

## Standard Stack

### Core (already in project)
| Library | Version | Purpose | Why Standard |
|---------|---------|---------|--------------|
| React | ^19.2.0 | UI framework | Already in project |
| Radix UI (Dialog) | via radix-ui ^1.4.3 | Dialog primitives | Already used for SendEmailDialog |
| TanStack Query | ^5.90.20 | Server state / mutations | Already used for useSendEmail |
| openapi-fetch | ^0.15.0 | Typed API client | Already used for all API calls |
| Tailwind CSS | ^4.1.18 | Styling | Already in project |
| lucide-react | ^0.563.0 | Icons (X, ChevronDown, Eye) | Already in project |
| react-i18next | ^16.5.4 | Internationalization | Already used for all UI text |
| Pydantic | (existing) | Request/response schemas | Already used for email schemas |
| FastAPI | (existing) | API endpoints | Already used for email router |

### No new dependencies needed
The tag/chip input is simple enough to build custom. No animation or complex interaction library is required.

## Architecture Patterns

### Frontend: SendEmailDialog Refactor

The current `SendEmailDialog.tsx` is ~150 lines. After Phase 3 it will be significantly larger. Extract sub-components:

```
frontend/src/components/dashboard/
├── SendEmailDialog.tsx          # Main dialog orchestrator (refactored)
├── EmailChipInput.tsx           # Reusable tag/chip input component
├── EmailChipInput.test.tsx      # Tests for chip input
└── EmailPreview.tsx             # Preview iframe section (optional extraction)
```

### Pattern 1: EmailChipInput Component
**What:** A controlled input that converts typed emails into chips on Enter/comma, validates format, and allows removal via x button or Backspace.
**When to use:** All three recipient fields (To, CC, BCC) share this component.
**Example:**
```typescript
interface EmailChipInputProps {
  id: string;
  emails: string[];
  onChange: (emails: string[]) => void;
  disabled?: boolean;
  placeholder?: string;
  maxTotal?: number;       // cap across all fields
  currentTotal?: number;   // current count across all fields
}
```

Key behaviors:
- `onKeyDown` handler: Enter or comma triggers add (prevent default for comma)
- Backspace on empty input removes last chip
- `isValidEmail()` check on add -- if invalid, set input border red + show brief error
- Each chip renders with email text + X button
- Chips wrap naturally using flexbox
- Input field sits inline after chips (Gmail-style)

### Pattern 2: Gmail-style CC/BCC Reveal
**What:** "CC" and "BCC" as text links next to the To label. Clicking reveals the field and hides the link.
**When to use:** Standard email compose UX pattern.
**Example:**
```typescript
const [showCc, setShowCc] = useState(false);
const [showBcc, setShowBcc] = useState(false);

// In label area:
<div className="flex items-center gap-2">
  <Label>To</Label>
  {!showCc && <button onClick={() => setShowCc(true)} className="text-xs text-muted-foreground hover:text-foreground">CC</button>}
  {!showBcc && <button onClick={() => setShowBcc(true)} className="text-xs text-muted-foreground hover:text-foreground">BCC</button>}
</div>
```

### Pattern 3: Preview via iframe srcdoc
**What:** Fetch HTML from preview endpoint, render in iframe using `srcdoc` attribute.
**When to use:** Safer than `dangerouslySetInnerHTML`, provides natural sandboxing.
**Example:**
```typescript
const [previewHtml, setPreviewHtml] = useState<string | null>(null);
const [showPreview, setShowPreview] = useState(false);

// Fetch on expand:
const fetchPreview = async () => {
  const noteParam = note ? `?note=${encodeURIComponent(note)}` : '';
  const { data } = await client.GET(`/api/v1/email/preview/${evaluationId}${noteParam}`);
  setPreviewHtml(data);
};

// Render:
<iframe srcdoc={previewHtml} className="w-full h-[300px] border rounded" sandbox="allow-same-origin" />
```

### Pattern 4: Backend CID-to-DataURI Conversion for Preview
**What:** When preview mode is requested, load header/footer assets and encode as base64 data URIs instead of CID references.
**When to use:** Preview endpoint only. Actual send still uses CID.
**Example:**
```python
import base64

def _asset_to_data_uri(filename: str) -> str:
    data = _load_asset(filename)
    b64 = base64.b64encode(data).decode("ascii")
    return f"data:image/png;base64,{b64}"

# In preview endpoint:
header_uri = _asset_to_data_uri("aha-e-mail-header-2026.png")
footer_uri = _asset_to_data_uri("aha-e-mail-footer-2026.png")
chart_placeholder = "data:image/svg+xml,..."  # or a simple placeholder
html = render_email_html(
    evaluation_data=eval_dict,
    chart_cid=chart_placeholder,  # placeholder
    header_cid=header_uri,        # data URI works in src= just like cid:
    footer_cid=footer_uri,
    note=note,
)
```

**Important note:** The current `render_email_html` uses `cid:{header_cid}` format in img src. For data URIs, the approach needs to change -- either pass the full `src` value instead of just the CID, or add a `preview_mode` flag that changes how image sources are rendered. The cleanest approach: change the template parameter names from `*_cid` to `*_src` and pass full `cid:...` or `data:...` URIs from the caller. This is a minor but important refactor.

### Pattern 5: Backend Multi-Recipient Email
**What:** Python's `EmailMessage` handles To/CC natively. BCC is handled by including addresses in `send_message` recipients but NOT in headers.
**Example:**
```python
msg = EmailMessage()
msg["To"] = ", ".join(to_list)
if cc_list:
    msg["Cc"] = ", ".join(cc_list)
# BCC: do NOT set header -- just include in envelope recipients

# send_message accepts explicit recipients
all_recipients = to_list + cc_list + bcc_list
server.send_message(msg, to_addrs=all_recipients)
```

### Anti-Patterns to Avoid
- **Sending separate emails per recipient:** Use To/CC/BCC headers on a single email. Sending N separate emails wastes SMTP connections and loses the CC/BCC semantics.
- **Using innerHTML for preview:** Use iframe `srcdoc` for sandboxing. Never inject backend HTML directly into the React DOM.
- **Storing preview HTML in React Query cache:** Preview HTML is ephemeral and depends on the current note text. Use local state, not query cache.

## Don't Hand-Roll

| Problem | Don't Build | Use Instead | Why |
|---------|-------------|-------------|-----|
| Email validation regex | Complex RFC 5322 parser | Simple `/^[^\s@]+@[^\s@]+\.[^\s@]+$/` (already in codebase) | The existing regex is good enough for UX validation; Pydantic EmailStr does real validation on backend |
| Dialog component | Custom modal | Radix Dialog (already used) | Accessibility, focus trapping, scroll locking |
| Toast notifications | Custom notification system | sonner (already used) | Already wired up |

## Common Pitfalls

### Pitfall 1: BCC Header Leaking Recipients
**What goes wrong:** Setting `msg["Bcc"]` header in the email makes BCC recipients visible to all.
**Why it happens:** Misunderstanding of how BCC works at the SMTP protocol level.
**How to avoid:** NEVER set the Bcc header on the EmailMessage. Instead, pass BCC addresses only as envelope recipients to `server.send_message(msg, to_addrs=all_recipients)`.
**Warning signs:** BCC recipients can see each other's addresses.

### Pitfall 2: CID Images Not Rendering in iframe Preview
**What goes wrong:** `cid:xxx@domain` references don't resolve in a browser iframe -- they only work inside email clients.
**Why it happens:** CID is an email-specific protocol, not a browser-supported URI scheme.
**How to avoid:** Convert images to base64 data URIs for preview mode. Pass full `src` values to the template renderer.
**Warning signs:** Broken images in preview.

### Pitfall 3: Comma in Email Chip Input Conflicts with Typing
**What goes wrong:** User types comma intending it as part of text, but it triggers chip creation.
**Why it happens:** Comma is used as a delimiter.
**How to avoid:** In email input context, comma in email address is always wrong (not valid in local-part without quotes), so treating comma as delimiter is correct. Just ensure the validation catches the resulting invalid token.

### Pitfall 4: Preview Endpoint Fetching Stale Data
**What goes wrong:** Preview doesn't reflect the current custom note because the note wasn't passed to the endpoint.
**Why it happens:** Forgetting to include the note as a query parameter.
**How to avoid:** Always pass `?note=...` to the preview endpoint. Consider debouncing the preview refresh when note changes.

### Pitfall 5: Dialog Scrollability with Many Fields
**What goes wrong:** Dialog content overflows the viewport when CC, BCC, note, AND preview are all expanded.
**Why it happens:** Fixed dialog height or missing overflow handling.
**How to avoid:** Ensure `DialogContent` allows vertical scrolling. Use `max-h-[85vh] overflow-y-auto` on the content area inside the dialog.

### Pitfall 6: send_message vs sendmail for BCC
**What goes wrong:** Using `server.send_message(msg)` without explicit `to_addrs` only sends to addresses in To and Cc headers -- BCC recipients are excluded.
**Why it happens:** `send_message` extracts recipients from headers by default.
**How to avoid:** Explicitly pass `to_addrs=all_recipients` including BCC addresses.

## Code Examples

### EmailChipInput Component Structure
```typescript
// Custom component -- no library needed
function EmailChipInput({ id, emails, onChange, disabled, placeholder, maxTotal, currentTotal }: EmailChipInputProps) {
  const [inputValue, setInputValue] = useState('');
  const [error, setError] = useState('');

  const addEmail = (raw: string) => {
    const email = raw.trim().replace(/,$/, '');
    if (!email) return;
    if (!isValidEmail(email)) { setError(t('sendEmail.invalidEmail')); return; }
    if (emails.includes(email)) { setError(t('sendEmail.duplicateEmail')); return; }
    if (currentTotal !== undefined && maxTotal !== undefined && currentTotal >= maxTotal) return;
    onChange([...emails, email]);
    setInputValue('');
    setError('');
  };

  const handleKeyDown = (e: KeyboardEvent) => {
    if (e.key === 'Enter' || e.key === ',') {
      e.preventDefault();
      addEmail(inputValue);
    }
    if (e.key === 'Backspace' && !inputValue && emails.length > 0) {
      onChange(emails.slice(0, -1));
    }
  };

  return (
    <div className={cn("flex flex-wrap items-center gap-1 rounded-md border p-1.5 min-h-[38px]", error && "border-destructive")}>
      {emails.map(email => (
        <span key={email} className="inline-flex items-center gap-1 rounded bg-muted px-2 py-0.5 text-sm">
          {email}
          <button type="button" onClick={() => onChange(emails.filter(e => e !== email))} disabled={disabled}>
            <X className="size-3" />
          </button>
        </span>
      ))}
      <input
        id={id}
        type="email"
        value={inputValue}
        onChange={e => { setInputValue(e.target.value); setError(''); }}
        onKeyDown={handleKeyDown}
        onBlur={() => inputValue && addEmail(inputValue)}
        placeholder={emails.length === 0 ? placeholder : ''}
        disabled={disabled}
        className="flex-1 min-w-[120px] outline-none bg-transparent text-sm"
      />
      {error && <p className="w-full text-xs text-destructive mt-1">{error}</p>}
    </div>
  );
}
```

### Backend Schema Update
```python
class SendEmailRequest(BaseModel):
    evaluation_id: int
    recipients: list[EmailStr] = Field(min_length=1, max_length=10)
    cc: list[EmailStr] = Field(default_factory=list, max_length=10)
    bcc: list[EmailStr] = Field(default_factory=list, max_length=10)
    chart_image: str = Field(description="Base64-encoded PNG chart image")
    subject: str | None = Field(default=None, max_length=200)
    note: str | None = Field(default=None, max_length=500)

    @model_validator(mode="after")
    def validate_total_recipients(self) -> "SendEmailRequest":
        total = len(self.recipients) + len(self.cc) + len(self.bcc)
        if total > 10:
            raise ValueError("Total recipients (To + CC + BCC) cannot exceed 10")
        return self

class SendEmailResponse(BaseModel):
    success: bool
    message_id: str
    recipients: list[str]  # was: recipient: str
```

### Template Note Section
```python
def _render_note(note: str) -> str:
    """Render custom note as a styled card."""
    # Preserve line breaks by converting \n to <br>
    escaped = _esc(note).replace("\n", "<br>")
    return f"""\
<!-- Custom Note -->
<tr>
  <td style="padding:8px 30px 16px 30px;font-family:Arial,Helvetica,sans-serif;">
    <table role="presentation" width="100%" cellpadding="0" cellspacing="0" border="0"
           style="background-color:{CARD_BG};border-radius:6px;border-left:3px solid {PRIMARY_BLUE};">
      <tr>
        <td style="padding:14px 16px;font-size:13px;color:{TEXT_DARK};line-height:1.6;">
          {escaped}
        </td>
      </tr>
    </table>
  </td>
</tr>"""
```

### build_email_message with CC/BCC
```python
def build_email_message(
    *,
    subject: str,
    from_name: str,
    from_email: str,
    to_emails: list[str],
    cc_emails: list[str] | None = None,
    bcc_emails: list[str] | None = None,
    html_content: str,
    text_content: str,
    images: list[tuple[bytes, str, str]],
) -> EmailMessage:
    msg = EmailMessage()
    msg["Subject"] = subject
    msg["From"] = f"{from_name} <{from_email}>"
    msg["To"] = ", ".join(to_emails)
    if cc_emails:
        msg["Cc"] = ", ".join(cc_emails)
    # BCC: intentionally NOT set as header
    # ...rest same as before...
    return msg
```

## State of the Art

| Old Approach | Current Approach | When Changed | Impact |
|--------------|------------------|--------------|--------|
| Single `recipient: str` | `recipients: list[str]` + `cc` + `bcc` | This phase | Schema breaking change -- frontend + backend must update together |
| `to_email: str` in `build_email_message` | `to_emails: list[str]` | This phase | Function signature change |
| `cid:` only in template | Support both `cid:` and `data:` URIs | This phase | Template params change from `*_cid` to `*_src` or use full URI |
| Debug-only preview | Authenticated preview for all users | This phase | Remove `if not settings.debug` guard |

## Open Questions

1. **Preview endpoint response format for openapi-fetch**
   - What we know: Current preview endpoint returns `HTMLResponse` (raw HTML string). openapi-fetch expects typed JSON responses per the `paths` interface.
   - What's unclear: How to handle raw HTML response with openapi-fetch's typed client.
   - Recommendation: For the preview, either (a) add a path entry that returns `string` content type, or (b) use a plain `fetch()` call bypassing the typed client (simpler, since preview is a one-off read). Option (b) is simpler -- just do `fetch(url, { headers })` and `.text()`.

2. **Image source parameter naming in render_email_html**
   - What we know: Currently uses `header_cid`, `footer_cid`, `chart_cid` params and prepends `cid:` in template. For preview, we need `data:` URIs.
   - What's unclear: Whether to rename params or add a preview_mode flag.
   - Recommendation: Rename to `header_src`, `footer_src`, `chart_src` and pass the full URI (`cid:xxx` for send, `data:image/png;base64,...` for preview). Minimal template change -- just remove the `cid:` prefix from the template `src=` attributes.

3. **Chart placeholder in preview**
   - What we know: Chart is captured from the DOM at send time, not available during preview.
   - Recommendation: Use a simple gray placeholder with text "Chart akan ditampilkan di email" as an SVG data URI or a minimal PNG.

## Validation Architecture

### Test Framework
| Property | Value |
|----------|-------|
| Framework | Vitest 4.x (frontend), Pytest 9.x (backend) |
| Config file | `frontend/vite.config.ts` (test section), `backend/pytest.ini` or pyproject.toml |
| Quick run command | `cd frontend && npx vitest run src/components/dashboard/` / `cd backend && uv run pytest tests/unit/email/ -x` |
| Full suite command | `cd frontend && npx vitest run` / `cd backend && uv run pytest -v` |

### Phase Requirements -> Test Map
| Req ID | Behavior | Test Type | Automated Command | File Exists? |
|--------|----------|-----------|-------------------|-------------|
| SEND-03 | Multiple recipients chip input | unit | `cd frontend && npx vitest run src/components/dashboard/EmailChipInput.test.tsx` | Wave 0 |
| SEND-03 | Backend accepts recipients list | unit | `cd backend && uv run pytest tests/unit/email/test_service.py -x -k multi` | Wave 0 |
| SEND-04 | CC/BCC fields in dialog | unit | `cd frontend && npx vitest run src/components/dashboard/SendEmailDialog.test.tsx` | Exists (needs update) |
| SEND-04 | Backend CC/BCC in email headers | unit | `cd backend && uv run pytest tests/unit/email/test_service.py -x -k cc` | Wave 0 |
| SEND-05 | Custom note textarea + char count | unit | `cd frontend && npx vitest run src/components/dashboard/SendEmailDialog.test.tsx` | Exists (needs update) |
| SEND-05 | Note rendered in email HTML | unit | `cd backend && uv run pytest tests/unit/email/test_template.py -x -k note` | Wave 0 |
| CONT-07 | Preview iframe loads HTML | unit | `cd frontend && npx vitest run src/components/dashboard/SendEmailDialog.test.tsx` | Exists (needs update) |
| CONT-07 | Preview endpoint returns data URI HTML | unit | `cd backend && uv run pytest tests/unit/email/test_service.py -x -k preview` | Wave 0 |

### Sampling Rate
- **Per task commit:** `cd frontend && npx vitest run src/components/dashboard/ && cd ../backend && uv run pytest tests/unit/email/ -x`
- **Per wave merge:** `cd frontend && npx vitest run && cd ../backend && uv run pytest -v`
- **Phase gate:** Full suite green before `/gsd:verify-work`

### Wave 0 Gaps
- [ ] `frontend/src/components/dashboard/EmailChipInput.test.tsx` -- covers SEND-03 chip input behavior
- [ ] Update `frontend/src/components/dashboard/SendEmailDialog.test.tsx` -- covers SEND-04, SEND-05, CONT-07 integration
- [ ] Update `backend/tests/unit/email/test_service.py` -- covers multi-recipient, CC/BCC, note
- [ ] Update `backend/tests/unit/email/test_template.py` -- covers note rendering

## Sources

### Primary (HIGH confidence)
- Codebase inspection: `SendEmailDialog.tsx`, `useSendEmail.ts`, `apiClient.ts`, `schemas.py`, `router.py`, `service.py`, `template.py`
- Existing test files: `SendEmailDialog.test.tsx`, `test_service.py`, `test_template.py`, `conftest.py`
- Python `email.message.EmailMessage` documentation -- CC/BCC handling is well-documented standard library behavior

### Secondary (MEDIUM confidence)
- Gmail compose UX patterns -- widely known, no source needed

## Metadata

**Confidence breakdown:**
- Standard stack: HIGH - all libraries already in project, no new dependencies
- Architecture: HIGH - clear extension of existing patterns, well-understood refactor
- Pitfalls: HIGH - BCC header leak and CID-in-browser are well-documented gotchas
- Preview data URI approach: MEDIUM - the template param rename needs careful coordination

**Research date:** 2026-03-06
**Valid until:** 2026-04-06 (stable domain, no fast-moving dependencies)
