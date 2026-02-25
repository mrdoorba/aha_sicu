## Why

The shared `Card` component lacks `overflow-hidden`, causing wide content (like calculator result tables with `whitespace-nowrap` cells) to visually overflow past the card boundary, overlap adjacent layout elements (Score Summary panel), and break the three-column page layout.

## What Changes

- Add `overflow-hidden` to the shared `Card` component's base className, so all cards clip their content at the card boundary.
- This enables the existing `overflow-x-auto` on the `Table` container to properly activate horizontal scrolling instead of blowing out the layout.

## Capabilities

### New Capabilities

_None — this is a CSS fix on an existing shared component._

### Modified Capabilities

_None — no spec-level behavior changes. The fix is purely visual/layout._

## Impact

- **Code**: `frontend/src/components/ui/card.tsx` — single class addition to `Card` component.
- **Visual**: All `Card` instances will now clip overflow. Content using portals (dropdowns, tooltips, popovers) is unaffected since they render at body level.
- **Dependencies**: None.
