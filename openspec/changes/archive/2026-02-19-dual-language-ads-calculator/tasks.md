## 1. Parser — Language Detection

- [x] 1.1 Add `source_language` field to `dataframe_to_json()` output in `parser.py` — set `"en"` if column renames were applied, `"id"` otherwise
- [x] 1.2 Add unit tests for language detection (English CSV → `"en"`, Indonesian CSV → `"id"`)

## 2. Calculator — Sheet 1 Language Variants

- [x] 2.1 Add `language` parameter to `calculate_sheet1()` (default `"id"`)
- [x] 2.2 Implement Indonesian AK3: only Semua Penempatan + Iklan Toko (2 categories)
- [x] 2.3 Implement English AK3: all 4 categories (Search, Recommendation, All, Shop Ad)
- [x] 2.4 Implement Indonesian AK4: 3 flags (product participation, active ratio, Iklan Toko)
- [x] 2.5 Implement English AK4: 9 flags (adds Search/Recommendation placement + bidding checks)
- [x] 2.6 Add unit tests for both AK3 variants
- [x] 2.7 Add unit tests for both AK4 variants

## 3. Calculator — Sheet 2 Language Variants

- [x] 3.1 Add `language` parameter to `calculate_sheet2()` (default `"id"`)
- [x] 3.2 Implement language-variant BOTTOM thresholds (100K/cap-5 for ID, 50K/cap-4 for EN)
- [x] 3.3 Implement language-variant TOP fallback (ID has fallback, EN has no fallback)
- [x] 3.4 Implement language-variant AL6 check ("Otomatis" for ID, "Bidding Otomatis" for EN)
- [x] 3.5 Add unit tests for BOTTOM threshold variants
- [x] 3.6 Add unit tests for TOP fallback variants
- [x] 3.7 Add unit tests for AL6 variant

## 4. Calculator Entry Point & Service

- [x] 4.1 Add `language` parameter to `calculate_ads_keyword()` and wire through to sheet1/sheet2
- [x] 4.2 Update `calculator_service.py` — extract `source_language` from parsed data, validate both uploads match, pass to calculator
- [x] 4.3 Add integration-level test for full English-language calculator run
- [x] 4.4 Add test for language mismatch error case
