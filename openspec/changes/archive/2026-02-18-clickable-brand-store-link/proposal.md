## Why

The brand detail page (EvaluationHeader) displays all `raw_data` fields as plain text, including the "Link Shopee Mall / LazMall" URL. Users cannot click the URL to open the store — they must manually copy and paste it into their browser. This slows down the evaluation workflow since users need to visit the store to verify products and followers.

## What Changes

- Detect URL values in the EvaluationHeader field display and render them as clickable hyperlinks (`<a>` tags) instead of plain text
- Links open in a new tab with proper `rel="noopener noreferrer"` for security
- Applies to both VP Data fields and Meeting Data fields in the header

## Capabilities

### New Capabilities

_None — this is a small UI enhancement within existing components._

### Modified Capabilities

_None — no spec-level behavior changes._

## Impact

- **Frontend**: `EvaluationHeader.tsx` — field value rendering logic
- **No backend changes**
- **No API changes**
- **No dependency changes**
