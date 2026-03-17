# Quick Task: Accept comma-separated numbers in Visitors (Tinjauan Pengunjung) fields

**Date:** 2026-03-17
**Branch:** gsd/quick/2-in-teh-evaluation-page-field-tinjauan-pe

## What Changed
- Fixed `parseCount` in `NumberField.tsx` to strip commas in addition to periods as thousand separators
- Values like `18,219` now correctly parse to `18219` instead of returning `null`
- Affects all count-type fields (Visitors section and others using `unit: 'count'`)
- Added 5 new tests covering comma, period, mixed separator, empty, and non-numeric inputs

## Files Modified
- `frontend/src/components/evaluation/forms/NumberField.tsx` — `parseCount` regex: `/\./g` → `/[.,]/g`
- `frontend/src/components/evaluation/forms/NumberField.test.tsx` — 5 new tests for count field parsing

## Verification
- 551 frontend tests pass (546 prior + 5 new)
- Covers: comma-separated (`18,219`), period-separated (`18.219`), mixed (`1,234.567`), empty, non-numeric
