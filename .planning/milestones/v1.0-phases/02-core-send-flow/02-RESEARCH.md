# Phase 2: Core Send Flow - Research

**Researched:** 2026-03-06
**Domain:** React UI (dialog, chart capture, API mutation), html-to-image library
**Confidence:** HIGH

## Summary

Phase 2 adds a complete email sending flow to the Presentation Dashboard: a send button in DashboardHeader, a dialog with brand summary and recipient input, chart-to-PNG capture via html-to-image, and loading/success/error feedback states. The backend endpoint (`POST /api/v1/email/send`) already exists from Phase 1, accepting `evaluation_id`, `recipient` (EmailStr), `chart_image` (base64 PNG), and optional `subject`.

The frontend stack is well-established: openapi-fetch typed client, TanStack Query mutations, Radix UI Dialog, Sonner toast, and Lucide icons. The main technical risk is html-to-image capturing a Recharts RadarChart wrapped in ResponsiveContainer -- this requires targeting the correct DOM element and handling SVG serialization. html-to-image is the right choice here (better SVG support than html2canvas) and the user has already decided on it.

**Primary recommendation:** Use html-to-image `toPng` with a React ref on the chart container div, add the `/api/v1/email/send` path type to apiClient.ts, and create a `useSendEmail` mutation hook following the established `useDeleteEvaluation` pattern.

<user_constraints>
## User Constraints (from CONTEXT.md)

### Locked Decisions
- Send button: outline variant, left of Edit Evaluation button, Lucide Mail icon + "Kirim Email" label, same h-10 height, visible to all authenticated users
- Dialog: title "Kirim Laporan Email", brand summary card at top (brand name, period, score), single recipient email input, pre-filled with PIC email from brand raw_data, send disabled until valid email
- Loading: inline in dialog, spinner + "Mengirim..." text, all fields disabled, dialog stays open
- Success: dialog closes automatically, Sonner toast "Email terkirim ke {recipient}" with checkmark, auto-dismiss 5s
- Error: inline in dialog, "Gagal mengirim email. Coba lagi." above buttons, send button changes to "Coba Lagi"
- Chart capture: html-to-image library, capture ScoreBreakdownChart RadarChart as PNG, triggered on send click, failure blocks send with error "Gagal menangkap grafik. Coba lagi.", base64 in API request body
- Footer: Batal (cancel) + Kirim (send) buttons

### Claude's Discretion
- Exact dialog width and spacing
- html-to-image configuration options (scale, quality, background)
- Chart capture target element selection strategy (ref vs querySelector)
- Hook structure for send mutation (useSendEmail or similar)
- API path type additions in apiClient.ts

### Deferred Ideas (OUT OF SCOPE)
- Editable subject line UI (Phase 3)
- Full HTML email preview in dialog (Phase 3, CONT-07)
- Recently used recipients from localStorage (v2, CONV-01)
</user_constraints>

<phase_requirements>
## Phase Requirements

| ID | Description | Research Support |
|----|-------------|-----------------|
| SEND-01 | User can click "Send Email" button in the DashboardHeader | Button placement, styling, and props documented; DashboardHeader component analyzed |
| SEND-02 | User enters recipient email address(es) in a dialog | Dialog structure with Radix Dialog, email input with validation, PIC pre-fill pattern from existing SendMailDialog |
| SEND-06 | User sees loading state while email is being sent | Inline loading pattern using mutation `isPending` state |
| SEND-07 | User sees success confirmation with recipient list after sending | Sonner toast with `toast.success()` pattern, auto-dismiss |
| SEND-08 | User sees clear error message if sending fails | Inline error in dialog using mutation `isError` / `error` state |
</phase_requirements>

## Standard Stack

### Core
| Library | Version | Purpose | Why Standard |
|---------|---------|---------|--------------|
| html-to-image | ^1.11.13 | DOM-to-PNG capture of RadarChart | Better SVG handling than html2canvas; lighter; user-decided |
| @tanstack/react-query | ^5.90.20 | `useMutation` for send email API call | Already in project, established pattern |
| openapi-fetch | ^0.15.0 | Typed API client for POST /api/v1/email/send | Already in project, typed paths interface |
| sonner | ^2.0.7 | Toast notifications for success feedback | Already in project and configured |
| radix-ui | ^1.4.3 | Dialog component for send email form | Already in project, Dialog already exists |
| lucide-react | ^0.563.0 | Mail icon for send button, Loader2 for spinner | Already in project |

### Supporting
| Library | Version | Purpose | When to Use |
|---------|---------|---------|-------------|
| react-i18next | ^16.5.4 | All UI text via translation keys | All new UI strings |
| recharts | ^3.7.0 | RadarChart being captured (existing) | Already renders the chart |

### Alternatives Considered
| Instead of | Could Use | Tradeoff |
|------------|-----------|----------|
| html-to-image | html2canvas | html2canvas worse at SVG; heavier; html-to-image user-decided |
| html-to-image | recharts-to-png | Wrapper around html2canvas; v3 recharts breaking changes reported |

**Installation:**
```bash
cd frontend && npm install html-to-image
```

## Architecture Patterns

### Recommended Project Structure
```
frontend/src/
├── components/dashboard/
│   ├── DashboardHeader.tsx      # MODIFY: add send button + dialog trigger
│   ├── PresentationDashboard.tsx # MODIFY: pass evaluation data + chart ref down
│   ├── ScoreBreakdownChart.tsx   # MODIFY: accept forwardRef for capture target
│   └── SendEmailDialog.tsx       # NEW: send email dialog component
├── hooks/
│   └── useSendEmail.ts           # NEW: mutation hook for email API
├── services/
│   └── apiClient.ts              # MODIFY: add /api/v1/email/send path type
└── locales/
    └── id.json                   # MODIFY: add new translation keys
```

### Pattern 1: Mutation Hook (follow useDeleteEvaluation pattern)
**What:** TanStack Query `useMutation` wrapping the typed openapi-fetch POST call
**When to use:** All API write operations
**Example:**
```typescript
// Source: existing useDeleteEvaluation.ts pattern
import { useMutation } from '@tanstack/react-query';
import client from '../services/apiClient';

interface SendEmailParams {
  evaluationId: number;
  recipient: string;
  chartImage: string; // base64 PNG
}

export function useSendEmail() {
  return useMutation({
    mutationFn: async ({ evaluationId, recipient, chartImage }: SendEmailParams) => {
      const { data, error } = await client.POST('/api/v1/email/send', {
        body: {
          evaluation_id: evaluationId,
          recipient: recipient,
          chart_image: chartImage,
        },
      });
      if (error) throw new Error('Failed to send email');
      return data;
    },
  });
}
```

### Pattern 2: html-to-image Capture with React Ref
**What:** Attach a ref to the chart container, use `toPng` to capture it
**When to use:** Chart capture before sending
**Example:**
```typescript
// Source: html-to-image README + Recharts integration
import { toPng } from 'html-to-image';

const chartRef = useRef<HTMLDivElement>(null);

const captureChart = async (): Promise<string> => {
  if (!chartRef.current) throw new Error('Chart ref not attached');
  const dataUrl = await toPng(chartRef.current, {
    cacheBust: true,
    backgroundColor: '#ffffff',
    pixelRatio: 2, // retina quality
  });
  // Strip data:image/png;base64, prefix for API
  return dataUrl.replace(/^data:image\/png;base64,/, '');
};
```

### Pattern 3: API Path Type Addition
**What:** Add typed path to the `paths` interface in apiClient.ts
**When to use:** When calling a new backend endpoint
**Example:**
```typescript
// Added to the paths interface in apiClient.ts
'/api/v1/email/send': {
  post: {
    requestBody: {
      content: {
        'application/json': {
          evaluation_id: number;
          recipient: string;
          chart_image: string;
          subject?: string | null;
        };
      };
    };
    responses: {
      200: {
        content: {
          'application/json': {
            success: boolean;
            message_id: string;
            recipient: string;
          };
        };
      };
    };
  };
};
```

### Pattern 4: Dialog with Feedback States
**What:** Radix Dialog that manages idle/loading/error states inline
**When to use:** Any dialog with async operations
**Example:**
```typescript
// Inline loading and error handling in dialog
const { mutate, isPending, isError, reset } = useSendEmail();

// Loading state: disable form, show spinner
<Button disabled={isPending}>
  {isPending ? (
    <><Loader2 className="mr-2 size-4 animate-spin" />Mengirim...</>
  ) : isError ? (
    'Coba Lagi'
  ) : (
    <><Mail className="mr-2 size-4" />Kirim</>
  )}
</Button>

// Error state: message above buttons
{isError && (
  <p className="text-sm text-destructive">Gagal mengirim email. Coba lagi.</p>
)}
```

### Anti-Patterns to Avoid
- **Capturing ResponsiveContainer directly:** ResponsiveContainer uses resize observers and may not have stable dimensions during capture. Capture the wrapping div, not the ResponsiveContainer itself.
- **Using querySelector for chart target:** Fragile, breaks with component restructuring. Use React ref instead.
- **Stripping base64 prefix server-side:** The backend expects base64 string. Strip the `data:image/png;base64,` prefix on the frontend before sending.
- **Showing raw SMTP errors to users:** Backend logs SMTP errors; frontend shows generic "Gagal mengirim email" message per user decision.

## Don't Hand-Roll

| Problem | Don't Build | Use Instead | Why |
|---------|-------------|-------------|-----|
| Email validation | Regex validator | HTML5 `type="email"` + pattern attr | Browser validation sufficient for single email; backend uses Pydantic EmailStr as safety net |
| Chart-to-PNG | Canvas drawing code | `html-to-image` toPng | SVG serialization, cross-browser fonts, retina support |
| Toast notifications | Custom notification system | `sonner` toast.success() | Already configured in app, Sonner component in layout |
| Loading spinners | Custom spinner component | Lucide `Loader2` with `animate-spin` | Already used across codebase |
| Dialog component | Custom modal | Radix `Dialog` components | Already exists at `components/ui/dialog.tsx` |

**Key insight:** Every UI primitive needed already exists in the project. The only new dependency is html-to-image.

## Common Pitfalls

### Pitfall 1: ResponsiveContainer Dimension Issues During Capture
**What goes wrong:** html-to-image captures a 0-width or incorrectly sized chart because ResponsiveContainer hasn't settled dimensions.
**Why it happens:** ResponsiveContainer uses ResizeObserver and may report 0 width when the dialog overlay is open or the chart is partially off-screen.
**How to avoid:** Place the ref on the outer div wrapping the entire chart card (not on ResponsiveContainer). The chart is rendered on the dashboard page behind the dialog, so it should have stable dimensions. If capture returns blank, consider adding a small delay or using `requestAnimationFrame`.
**Warning signs:** Blank or tiny PNG images in sent emails.

### Pitfall 2: html-to-image SVG CSS Variable Resolution
**What goes wrong:** Chart colors render as black or missing because CSS custom properties (e.g., `var(--chart-radar-fill)`) aren't resolved during SVG serialization.
**Why it happens:** html-to-image serializes DOM to SVG foreignObject, and CSS variables may not be inlined.
**How to avoid:** Test capture output visually. If colors are lost, use the `filter` option to inline computed styles or set explicit `backgroundColor: '#ffffff'` option. May need to set the chart's theme colors as inline styles instead of CSS variables for the capture.
**Warning signs:** Monochrome or unstyled chart in captured PNG.

### Pitfall 3: Base64 Prefix in API Request
**What goes wrong:** Backend rejects the chart_image because it includes the `data:image/png;base64,` prefix.
**Why it happens:** `toPng` returns a full data URL, not raw base64.
**How to avoid:** Strip the prefix: `dataUrl.replace(/^data:image\/png;base64,/, '')` before sending to API.
**Warning signs:** 422 validation error from backend.

### Pitfall 4: Dialog State Not Resetting on Close
**What goes wrong:** Error message persists when dialog is reopened after a failed send.
**Why it happens:** TanStack Query mutation state (`isError`) persists across dialog open/close cycles.
**How to avoid:** Call `mutation.reset()` when dialog closes (in `onOpenChange` handler).
**Warning signs:** Error message visible when dialog opens fresh.

### Pitfall 5: Missing Props Threading Through Components
**What goes wrong:** DashboardHeader doesn't have access to evaluation_id, brand_raw_data, or chart ref needed for the send flow.
**Why it happens:** PresentationDashboard currently only passes brandName, brandId, verdict, template, period to DashboardHeader.
**How to avoid:** Add new props to DashboardHeader (evaluationId, brandRawData, chartRef) or lift the dialog to PresentationDashboard level and pass a send trigger callback to DashboardHeader.
**Warning signs:** Prop drilling becomes excessive; consider lifting dialog state up.

## Code Examples

### Existing Reference: SendMailDialog on History Page
The existing `SendMailDialog.tsx` at `frontend/src/components/evaluations/` uses a mailto: approach. The new Phase 2 dialog is fundamentally different (API call, not mailto) but shares the PIC email pre-fill pattern:
```typescript
// Source: existing SendMailDialog.tsx line 36
const [picEmail, setPicEmail] = useState(brandRawData.email ?? '');
```

### Backend Contract
```typescript
// Source: backend/app/modules/email/schemas.py
// Request: POST /api/v1/email/send
{
  evaluation_id: number,    // required
  recipient: string,        // EmailStr validated
  chart_image: string,      // base64 PNG (no data: prefix)
  subject: string | null    // optional, auto-generated if null
}

// Response: 200
{
  success: boolean,
  message_id: string,
  recipient: string
}
```

### Data Availability in PresentationDashboard
```typescript
// Source: PresentationDashboard.tsx - evaluation object has all needed fields
evaluation.id              // evaluation_id for API
evaluation.brand_name      // for dialog summary
evaluation.final_score     // for dialog summary
evaluation.verdict         // for dialog summary
evaluation.template        // for dialog summary
evaluation.period          // for dialog summary
evaluation.brand_raw_data  // { email, pic_name, store_link, kategori }
// Note: brand_raw_data is on EvaluationDetail type but NOT currently passed to DashboardHeader
```

### Email Validation Pattern
```typescript
// Simple email format check for enabling send button
const isValidEmail = (email: string) => /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email);
// Backend does strict EmailStr validation as safety net
```

### Translation Keys Needed
```json
{
  "sendEmail.title": "Kirim Laporan Email",
  "sendEmail.brandSummary": "Ringkasan Brand",
  "sendEmail.recipient": "Penerima",
  "sendEmail.recipientPlaceholder": "email@contoh.com",
  "sendEmail.send": "Kirim",
  "sendEmail.sending": "Mengirim...",
  "sendEmail.retry": "Coba Lagi",
  "sendEmail.cancel": "Batal",
  "sendEmail.sendButton": "Kirim Email",
  "sendEmail.success": "Email terkirim ke {{recipient}}",
  "sendEmail.error": "Gagal mengirim email. Coba lagi.",
  "sendEmail.captureError": "Gagal menangkap grafik. Coba lagi."
}
```

## State of the Art

| Old Approach | Current Approach | When Changed | Impact |
|--------------|------------------|--------------|--------|
| html2canvas for DOM capture | html-to-image (SVG serialization) | 2023+ | Better SVG support, lighter bundle |
| recharts-to-png wrapper | Direct html-to-image + ref | Recharts v3 breaking changes | More control, fewer wrapper bugs |
| mailto: links for email | Backend SMTP API + frontend dialog | Phase 1-2 of this project | Real email delivery with HTML template |

**Deprecated/outdated:**
- `recharts-to-png`: Reports of breaking changes with Recharts v3; direct html-to-image is safer
- `dom-to-image`: Predecessor of html-to-image, unmaintained

## Open Questions

1. **CSS Variable Resolution in html-to-image**
   - What we know: html-to-image serializes to SVG foreignObject; CSS variables may not resolve
   - What's unclear: Whether Recharts RadarChart using `var(--chart-radar-fill)` will render correctly in capture
   - Recommendation: Test during implementation; fallback is to set inline styles on chart for capture. The STATE.md notes this as a known concern: "html-to-image + Recharts RadarChart compatibility needs spike at start of Phase 2"

2. **Chart Ref Threading**
   - What we know: ScoreBreakdownChart needs a ref; PresentationDashboard renders both the chart and triggers the dialog
   - What's unclear: Best component architecture -- lift dialog to PresentationDashboard or pass ref down
   - Recommendation: Lift the SendEmailDialog to PresentationDashboard level; pass `onSendClick` callback to DashboardHeader. This avoids deep prop drilling and keeps the chart ref local to PresentationDashboard.

## Validation Architecture

### Test Framework
| Property | Value |
|----------|-------|
| Framework | Vitest ^4.0.18 + @testing-library/react ^16.3.2 |
| Config file | `frontend/vite.config.ts` (test section) |
| Quick run command | `cd frontend && npx vitest run --reporter=verbose` |
| Full suite command | `cd frontend && npx vitest run` |

### Phase Requirements -> Test Map
| Req ID | Behavior | Test Type | Automated Command | File Exists? |
|--------|----------|-----------|-------------------|-------------|
| SEND-01 | Send button visible in DashboardHeader, opens dialog | unit | `cd frontend && npx vitest run src/components/dashboard/DashboardHeader.test.tsx -x` | No -- Wave 0 |
| SEND-02 | Email input in dialog, PIC pre-fill, validation disables send | unit | `cd frontend && npx vitest run src/components/dashboard/SendEmailDialog.test.tsx -x` | No -- Wave 0 |
| SEND-06 | Loading spinner shown, fields disabled during send | unit | `cd frontend && npx vitest run src/components/dashboard/SendEmailDialog.test.tsx -x` | No -- Wave 0 |
| SEND-07 | Success toast shown with recipient after send | unit | `cd frontend && npx vitest run src/components/dashboard/SendEmailDialog.test.tsx -x` | No -- Wave 0 |
| SEND-08 | Error message shown in dialog on failure | unit | `cd frontend && npx vitest run src/components/dashboard/SendEmailDialog.test.tsx -x` | No -- Wave 0 |

### Sampling Rate
- **Per task commit:** `cd frontend && npx vitest run --reporter=verbose`
- **Per wave merge:** `cd frontend && npx vitest run && npm run lint && tsc --noEmit`
- **Phase gate:** Full suite green before `/gsd:verify-work`

### Wave 0 Gaps
- [ ] `frontend/src/components/dashboard/SendEmailDialog.test.tsx` -- covers SEND-02, SEND-06, SEND-07, SEND-08
- [ ] `frontend/src/components/dashboard/DashboardHeader.test.tsx` -- covers SEND-01 (button render and click)
- [ ] `frontend/src/hooks/useSendEmail.test.ts` -- covers mutation hook behavior
- [ ] html-to-image mock setup in test environment (toPng returns fake base64)

## Sources

### Primary (HIGH confidence)
- Codebase analysis: `frontend/src/components/dashboard/` -- DashboardHeader, PresentationDashboard, ScoreBreakdownChart
- Codebase analysis: `frontend/src/services/apiClient.ts` -- paths interface pattern
- Codebase analysis: `frontend/src/hooks/useDeleteEvaluation.ts` -- mutation hook pattern
- Codebase analysis: `backend/app/modules/email/schemas.py` -- SendEmailRequest/Response contracts
- Codebase analysis: `backend/app/modules/email/router.py` -- POST /api/v1/email/send endpoint

### Secondary (MEDIUM confidence)
- [html-to-image GitHub README](https://github.com/bubkoo/html-to-image) -- API reference, toPng usage
- [npm-compare: html-to-image vs html2canvas](https://npm-compare.com/dom-to-image,html-to-image,html2canvas) -- SVG superiority for Recharts
- [Better Programming: html-to-image vs html2canvas](https://betterprogramming.pub/heres-why-i-m-replacing-html2canvas-with-html-to-image-in-our-react-app-d8da0b85eadf) -- Performance comparison

### Tertiary (LOW confidence)
- CSS variable resolution in html-to-image SVG serialization -- needs implementation validation

## Metadata

**Confidence breakdown:**
- Standard stack: HIGH -- all libraries already in project except html-to-image; backend endpoint verified
- Architecture: HIGH -- clear patterns from existing codebase (mutation hooks, dialog, apiClient types)
- Pitfalls: MEDIUM -- CSS variable issue and ResponsiveContainer capture are known risks needing implementation spike
- html-to-image integration: MEDIUM -- library API is simple but Recharts SVG + CSS vars interaction is unverified

**Research date:** 2026-03-06
**Valid until:** 2026-04-06 (stable stack, only html-to-image compat may shift)
