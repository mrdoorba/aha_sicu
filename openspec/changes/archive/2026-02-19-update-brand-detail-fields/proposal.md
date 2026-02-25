## Why

The brand detail header currently displays the first 6 arbitrary fields from `raw_data` using a generic `.slice(0, 6)`. This shows irrelevant fields (like LBS, SHCU) while hiding critical business fields (Link Shopee Mall / LazMall, Kategori, Score VP, etc.). Users need to see a curated, specific set of fields to work effectively with brand data.

## What Changes

- Replace the generic "first 6 fields" display logic in `EvaluationHeader` with a curated list of specific fields in a defined order:
  1. BD
  2. Link Shopee Mall / LazMall (clickable URL)
  3. Kategori
  4. Shopee Mall
  5. No OPEX Issue
  6. Omset >100jt
  7. Score VP
  8. No WA
  9. Email
- Remove the `.slice(0, 6)` generic approach
- URL fields continue to render as clickable links (existing behavior)

## Capabilities

### New Capabilities

_(none)_

### Modified Capabilities

- `clickable-header-links`: The header now displays a fixed set of 9 curated fields instead of the first 6 generic fields

## Impact

- **Frontend**: `EvaluationHeader.tsx` — display logic changes
- **Backend**: No changes needed (raw_data already contains all fields)
- **Data**: Depends on Google Sheet column names matching exactly: `BD`, `Link Shopee Mall / LazMall`, `Kategori`, `Shopee Mall`, `No OPEX Issue`, `Omset >100jt`, `Score VP`, `No WA`, `Email`
