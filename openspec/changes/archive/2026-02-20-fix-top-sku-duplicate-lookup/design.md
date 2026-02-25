## Context

`_build_mass_update_lookup()` in `top_sku.py` iterates over mass update rows and builds a `name_to_kode` dict keyed by `"Nama Produk - Nama Variasi"`. When duplicate labels exist (same product listed twice with different Kode Variasi), the dict overwrites with the last entry. The reference spreadsheet uses VLOOKUP which returns the first match.

Verified against real data (cemilanklinikhot, Jan 2026): 2 of 32 top products have duplicate labels in mass update, causing wrong Kode Variasi, wrong stock, and average stock off by ~1,270.

## Goals / Non-Goals

**Goals:**
- Match VLOOKUP first-match-wins semantics in `_build_mass_update_lookup()`
- Add test coverage for the duplicate-label edge case

**Non-Goals:**
- Changing the revenue calculation formula (verified correct)
- Changing the ranking/aggregation logic (verified correct)
- Investigating why mass update data has duplicates (that's a Shopee export issue)

## Decisions

**First-match-wins via guard clause**: Add `if label not in name_to_kode` before assignment. Simple, minimal, and directly matches VLOOKUP behavior. Alternative (deduplicating input data) rejected — adds complexity and masks the actual data shape.

## Risks / Trade-offs

- [Low risk] Other stores may also have duplicates in mass update data → This fix benefits all stores consistently
- [No migration needed] Pure logic fix, no data model or API changes. Existing stored results will be recalculated on next upload.
