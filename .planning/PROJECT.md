# THB Marketplace Expansion

## What This Is

Multi-marketplace currency support for the AHA SICU evaluation system. Currently all revenue-related evaluation thresholds and calculations are hardcoded for IDR (Indonesian Rupiah). This project adds THB (Thai Baht) support so Thai marketplace brands can be evaluated using appropriately converted thresholds, with admin-editable values per marketplace.

## Core Value

Thai marketplace brands can be evaluated using THB-appropriate thresholds, with the same accuracy and completeness as existing IDR evaluations.

## Requirements

### Validated

- ✓ IDR evaluation thresholds and scoring — existing
- ✓ Calculator engine with registry pattern — existing
- ✓ Scoring rules management (admin/leader) — existing
- ✓ Brand evaluation workflow — existing
- ✓ CSV parsing for Shopee data — existing

### Active

- [ ] Marketplace/currency field on brands (each brand belongs to one marketplace: ID or TH)
- [ ] THB thresholds derived from IDR values (initial conversion, then independently editable)
- [ ] Rules page with marketplace tabs (IDR / THB) for admin/leader threshold management
- [ ] Evaluation page marketplace selector to filter/display correct currency context
- [ ] All revenue-related calculators respect marketplace-specific thresholds
- [ ] CSV parser handles THB-formatted values from Shopee Thailand
- [ ] Currency formatting throughout UI (฿ symbol, THB decimal/grouping conventions)

### Out of Scope

- Live exchange rate integration — thresholds are set once and manually adjusted
- Automatic currency conversion of raw data — THB data stays in THB
- Multi-currency within a single brand — one brand = one marketplace
- Other marketplaces beyond ID and TH — future expansion

## Context

- The existing system evaluates Shopee Indonesia brands using revenue thresholds (e.g., Rata-rata 6 Bulan threshold of IDR 100,000,000 ≈ THB 191,591)
- Shopee Thailand CSV data uses the same format as Shopee Indonesia
- No Thai brands exist in the system yet, but Thai marketplace data is available
- The rules module (`app/modules/rules/`) already manages scoring thresholds — needs marketplace dimension
- The calculator engine (`app/calculators/engine.py`) runs scoring against rules — needs to select rules by marketplace
- Frontend already has i18n support with `th` locale files

## Constraints

- **Data format**: Shopee Thailand CSVs use same structure as Indonesia — no new parsers needed, only value handling
- **Existing brands**: All current brands are IDR — migration must preserve them as marketplace=ID
- **Architecture**: Follow existing module pattern (router/service/schemas) and calculator registry

## Key Decisions

| Decision | Rationale | Outcome |
|----------|-----------|---------|
| Brand-level marketplace (not per-evaluation) | Each brand belongs to one country marketplace; simplifies data model | — Pending |
| Rules page marketplace tabs | Keeps all threshold management in one place; admins can compare IDR vs THB | — Pending |
| Initial THB thresholds from IDR conversion | Provides reasonable starting values; admins can adjust manually after | — Pending |
| User selects marketplace on evaluation page | Explicit selection prevents accidental cross-currency evaluation | — Pending |

---
*Last updated: 2026-03-16 after initialization*
