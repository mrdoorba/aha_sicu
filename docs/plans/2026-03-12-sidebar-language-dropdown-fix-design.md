# Fix Language Dropdown Clipped in Collapsed Sidebar

## Problem

The sidebar `<aside>` has `overflow-hidden` which clips the LanguageToggle dropdown — both upward (expanded sidebar) and rightward (collapsed sidebar). The recent fix (deef620) repositioned the dropdown but didn't address the root clipping.

## Root Cause

`overflow-hidden` on `<aside>` prevents any child from rendering outside its bounds. The dropdown, being absolutely positioned inside the sidebar, gets clipped.

## Design

Remove the blanket `overflow-hidden` from `<aside>` and ensure all collapsible text elements self-contain their transitions using the `w-0 opacity-0` / `w-auto opacity-100` pattern.

### Changes

1. **Sidebar.tsx — `<aside>` element**: Remove `overflow-hidden`
2. **Sidebar.tsx — "Store ICU" title**: Change from `opacity-0`/`opacity-100` to `w-0 opacity-0`/`w-auto opacity-100` with `overflow-hidden` on the span (matches nav items and logout text pattern)
3. **No changes to LanguageToggle.tsx** — the collapsed positioning from deef620 is correct, it just needs the parent to stop clipping

### Why this works

Every text element in the sidebar already handles its own collapse:
- Nav item text: `w-0 opacity-0` / `w-auto opacity-100`
- User info: `h-0 opacity-0` / `h-8 opacity-100`
- Logout text: `w-0 opacity-0` / `w-auto opacity-100`
- Title (after fix): `w-0 opacity-0` / `w-auto opacity-100`

The nav section has `overflow-y-auto` which clips its own content. No text bleeds outside the sidebar during collapse.

### Files affected

- `frontend/src/components/layout/Sidebar.tsx`
