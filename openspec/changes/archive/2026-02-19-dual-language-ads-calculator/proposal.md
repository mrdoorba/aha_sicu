## Why

The Ads Keyword Calculator currently runs a single logic path regardless of CSV language. However, the original spreadsheet has two distinct versions — Indonesian and English — with **different business rules** (different flag counts, different thresholds, different AK3 categories). When an English CSV is uploaded, the parser translates values to Indonesian and runs the Indonesian logic, producing incorrect results for brands that export in English.

## What Changes

- **Detect CSV language** at parse time and store it alongside parsed data (metadata flag: `"id"` or `"en"`).
- **AK3 (Ad Type Breakdown)**: Indonesian outputs 2 categories (Semua Penempatan + Iklan Toko); English outputs 4 categories (Search, Recommendation, All, Shop Ad).
- **AK4 (Recommendation Flags)**: Indonesian produces up to 3 flags; English produces up to 9 flags (adds Search/Recommendation placement + bidding method checks).
- **BOTTOM Ads**: Indonesian uses min cost 100,000 and fallback ROAS cap `min(*, 5)`; English uses min cost 50,000 and fallback ROAS cap `min(*, 4)`.
- **AL6 (Bottom flag)**: Indonesian checks substring `"Otomatis"`; English checks `"Bidding Otomatis"`.
- **TOP Ads fallback**: Indonesian has IFNA fallback; English has no fallback (direct query only).

## Capabilities

### New Capabilities
- `ads-calculator-language-variants`: Dual-language logic for the Ads Keyword Calculator — language detection, variant-specific AK3/AK4/AL5/AL6 logic, and threshold differences.

### Modified Capabilities

_(none — no existing spec-level requirements change)_

## Impact

- `backend/app/modules/upload/parser.py` — record detected language in parsed data metadata
- `backend/app/calculators/ads_keyword.py` — add language-variant logic for Sheet 1 (AK3, AK4) and Sheet 2 (AL5 thresholds, AL6)
- `backend/app/modules/evaluations/calculator_service.py` — pass language flag from parsed data to calculator
- `backend/tests/unit/calculators/test_ads_keyword.py` — dual test sets for both language paths
- `backend/tests/unit/test_parser.py` — test language detection
