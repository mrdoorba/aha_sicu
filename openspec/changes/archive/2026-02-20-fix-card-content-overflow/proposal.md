## Why

The `overflow-hidden` fix on Card (commit 13ccafb) clips visual overflow but does not prevent the Card's layout width from expanding. CardContent, as a flex child inside Card's `flex-col`, retains `min-width: auto` by default — so wide content (tables with `whitespace-nowrap` cells) still forces the Card to grow, pushing the entire page layout wider and causing a horizontal scrollbar.

## What Changes

- Add `min-w-0` to `CardContent` so it can shrink within Card's flex-col layout, allowing the table container's `overflow-x-auto` to activate properly
- Update the existing card-overflow test to verify the fix works end-to-end

## Capabilities

### New Capabilities

_(none)_

### Modified Capabilities

- `card-overflow`: CardContent must also constrain its width within Card's flex layout so that nested scroll containers (like table wrappers) resolve to a definite width and produce scrollbars instead of expanding ancestors.

## Impact

- `frontend/src/components/ui/card.tsx` — CardContent class change
- `frontend/src/components/ui/card.test.tsx` — test update
- Affects every Card with wide content (TopSkuResults tables, EvaluationDetailPage tables, etc.) — all benefit automatically
