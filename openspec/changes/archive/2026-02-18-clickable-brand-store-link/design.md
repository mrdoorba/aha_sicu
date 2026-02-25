## Context

The `EvaluationHeader` component renders brand `raw_data` fields as key-value pairs using `getDisplayFields()`. All values are rendered as plain text via `{value}`. When a field value is a URL (e.g., "Link Shopee" = `https://shopee.co.id/cemilanklinikhot`), it appears as non-clickable text, forcing users to copy-paste.

The store link is already extracted and used as a clickable icon in `VisitorsForm` and `ProductsStatusForm`, but the header field display doesn't benefit from this.

## Goals / Non-Goals

**Goals:**
- URL values in the EvaluationHeader field display render as clickable links
- Links open in a new tab with security attributes
- Works for both VP Data fields and Meeting Data fields

**Non-Goals:**
- Not detecting URLs within mixed text (only values that are entirely a URL)
- Not adding link previews or favicons
- Not modifying how other components render links

## Decisions

**Inline URL detection in the render loop**

Rather than creating a separate utility or modifying `getDisplayFields()`, detect URLs at render time in the `.map()` callback. A value that starts with `https://` or `http://` is rendered as an `<a>` tag; everything else stays as plain text.

_Rationale:_ This is the simplest approach — a single conditional in the JSX. No new files, no new abstractions, no changes to the data layer. The same pattern can apply to the meeting data fields section since both use the same `.map()` structure.
