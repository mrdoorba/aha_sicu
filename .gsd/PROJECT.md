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

- [x] CSV parser handles THB-formatted values from Shopee Thailand
- [x] Currency formatting throughout UI (THB/IDR code prefix, proper decimal/grouping conventions)
- [x] Marketplace selection per evaluation (user chooses ID or TH at evaluation time)
- [x] THB thresholds derived from IDR values (initial conversion, then independently editable)
- [x] Rules page with marketplace tabs (IDR / THB) for admin/leader threshold management
- [x] Evaluation page marketplace selector to filter/display correct currency context
- [x] All revenue-related calculators respect marketplace-specific thresholds

### Out of Scope

- Live exchange rate integration — thresholds are set once and manually adjusted
- Automatic currency conversion of raw data — THB data stays in THB
- Multi-currency within a single evaluation — one evaluation = one marketplace
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
| Evaluation-level marketplace (not per-brand) | User knows which marketplace a brand belongs to; selects at evaluation time | Implemented (D018) |
| Rules page marketplace tabs | Keeps all threshold management in one place; admins can compare IDR vs THB | Implemented (D017) |
| Initial THB thresholds from IDR conversion | Provides reasonable starting values; admins can adjust manually after | Implemented (D002) |
| Marketplace default 'ID' everywhere | Explicit selection prevents accidental cross-currency evaluation | Implemented (D018) |
| Currency formatting centralized in formUtils.ts | Eliminates duplication; single breakpoint; deprecated re-exports for migration | Implemented (D016) |
| React Query queryKey includes marketplace | Prevents stale cross-marketplace cache hits | Implemented (D017) |
| User selects marketplace on evaluation page | Explicit selection prevents accidental cross-currency evaluation | Implemented (D018) |
| VARCHAR(2) + CHECK constraint for marketplace | Matches existing pattern; compact; enforces at DB level | Implemented (D001) |
| All functions default marketplace='ID' | Zero breaking changes for existing callers | Implemented (D004) |
| Currency formatting delegates to _fmt_idr | IDR/THB use same comma-thousands format; code injection via templates | Implemented (D007) |
| marketplace as keyword-only param, dict.get fallback | Prevents positional confusion; unknown marketplace → IDR | Implemented (D008) |
| THB raw numbers, IDR /1M juta scaling in conclusions | THB values are 3 OOM smaller; juta scaling is unreadable for THB | Implemented (D009) |

| Centralized price parsing in price_parser.py | DRY — replaces duplicate _clean_price; single extension point | Implemented (D011) |
| Read marketplace from evaluation_inputs in calculator_service | eval_inputs has marketplace column; brand_vp_data does not | Implemented (D012) |
| Calculator marketplace param is keyword-only with default "ID" | No positional confusion; full backward compatibility | Implemented (D013) |

---
*Last updated: 2026-03-17 after S04 completion — M001 complete*
