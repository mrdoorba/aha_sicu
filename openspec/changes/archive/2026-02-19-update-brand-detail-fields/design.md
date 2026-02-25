## Context

The `EvaluationHeader` component currently uses a generic `getDisplayFields()` function that takes the first 6 non-metadata fields from `raw_data` via `.slice(0, 6)`. This is order-dependent on JSONB key iteration and doesn't guarantee the right fields are shown. Users need a curated set of 9 specific business fields.

## Goals / Non-Goals

**Goals:**
- Display exactly 9 specified fields from `raw_data` in a defined order
- Maintain existing URL auto-detection for clickable links

**Non-Goals:**
- Changing backend or API responses
- Modifying the meeting data display section
- Making the field list configurable via UI

## Decisions

### Replace generic field slicing with a curated field list

**Decision**: Define a constant array of field keys in display order. Map over this array to extract values from `raw_data`, skipping fields that don't exist in the data.

**Rationale**: Simple, explicit, and easy to maintain. A constant array is clear about what's displayed and in what order. No backend changes needed since `raw_data` already contains all fields.

**Alternative considered**: Adding a backend endpoint to return "display fields" — rejected as over-engineered for a static list.

### Field key names must match Google Sheet column headers exactly

**Decision**: Use exact column names from the VP Google Sheet as keys (e.g., `"Link Shopee Mall / LazMall"`, `"Omset >100jt"`).

**Rationale**: The sync system stores columns as-is from the sheet. Any mismatch means the field won't render.

## Risks / Trade-offs

- **[Column rename in Google Sheet]** → If sheet column names change, the frontend won't display those fields. Mitigation: field names are in a single constant, easy to update.
- **[Field may be empty/missing]** → Some brands may not have all 9 fields populated. Mitigation: skip fields with empty/null/undefined values so the display stays clean.
