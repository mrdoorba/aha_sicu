## Context

The shared `Card` component (`frontend/src/components/ui/card.tsx`) uses `flex flex-col rounded-xl` but has no overflow constraint. When child content is wider than the card (e.g., tables with `whitespace-nowrap` cells), it visually overflows the card boundary and breaks the parent flex layout.

The `Table` component already wraps content in `overflow-x-auto`, but this only activates when the container's width is constrained. Without `overflow-hidden` on an ancestor, the card expands to fit content instead.

## Goals / Non-Goals

**Goals:**
- Card content is clipped at the card boundary, enabling child `overflow-x-auto` containers to scroll horizontally.

**Non-Goals:**
- Changing table-specific styling or adding per-table workarounds.
- Modifying the `Table` component.

## Decisions

**Add `overflow-hidden` to the shared `Card` base className.**

- *Why global, not targeted?* The issue applies to any Card containing wide content. Adding `overflow-hidden` globally is the correct default — cards with `rounded-xl` should clip content at their border radius. Portal-based elements (dropdowns, tooltips, popovers) render at `<body>` level and are unaffected.
- *Alternative considered:* Adding `overflow-hidden` only on `CalculatorCard` in `CalculatorResultsSection.tsx`. Rejected because it's a band-aid — the same issue could appear in any Card with wide content.

## Risks / Trade-offs

- [Clipping unintended content] → Low risk. No current components rely on content visually overflowing a Card. If one arises, it can override with `className="overflow-visible"`.
