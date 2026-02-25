## Context

Card component has `overflow-hidden` (added in 13ccafb), and Table component wraps `<table>` in a div with `overflow-x-auto`. However, CardContent sits between them as a flex child of Card's `flex-col` layout without `min-width: 0`. Default flex behavior gives children `min-width: auto`, which means CardContent refuses to shrink below its content's intrinsic width — defeating the Card's `overflow-hidden`.

Current chain:
```
Card (flex flex-col, overflow-hidden)
  └── CardContent (px-6)           ← min-width: auto (DEFAULT, problem!)
        └── table-container (overflow-x-auto, w-full)
              └── <table> (w-full, whitespace-nowrap cells)
```

## Goals / Non-Goals

**Goals:**
- CardContent shrinks within Card's flex layout so nested scroll containers resolve to a definite width
- Tables with long content scroll horizontally inside the card instead of blowing out page width
- Fix applies globally to all Cards, not just specific pages

**Non-Goals:**
- Changing table cell wrapping behavior (whitespace-nowrap is intentional for data tables)
- Adding per-component overflow wrappers in TopSkuResults, EvaluationDetailPage, etc.
- Restructuring the Card component API

## Decisions

**Add `min-w-0` to CardContent**

`min-w-0` sets `min-width: 0`, allowing CardContent to shrink below its content's intrinsic width inside Card's flex-col. This lets the table container's `overflow-x-auto` activate at the correct width.

*Alternatives considered:*
- `overflow-hidden` on CardContent — clips content but prevents any intentional visual overflow from children (e.g., popovers, tooltips)
- Per-component wrappers — works but requires changes in every component that renders wide content in a Card; doesn't prevent future regressions
- `table-layout: fixed` on tables — changes column sizing behavior undesirably

## Risks / Trade-offs

- [Minimal risk] `min-w-0` is a standard flex constraint pattern. No known side effects for content that already fits within the Card width.
