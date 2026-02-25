## ADDED Requirements

### Requirement: Parser records source language in parsed data
The parser SHALL detect whether a Shopee CSV export is in Indonesian or English and store `"source_language": "id"` or `"source_language": "en"` in the `parsed_data` dict. Detection is based on whether English column headers were found and renamed.

#### Scenario: English CSV detected
- **WHEN** a CSV with English column headers (e.g., "Ad Name", "Ads Type") is parsed
- **THEN** `parsed_data["source_language"]` SHALL be `"en"`

#### Scenario: Indonesian CSV detected
- **WHEN** a CSV with Indonesian column headers (e.g., "Nama Iklan", "Jenis Iklan") is parsed
- **THEN** `parsed_data["source_language"]` SHALL be `"id"`

#### Scenario: Existing data without language flag
- **WHEN** calculator receives parsed data without `source_language` key
- **THEN** it SHALL default to `"id"`

### Requirement: AK3 outputs different categories based on language
The calculator SHALL output different AK3 ad type breakdowns depending on source language.

#### Scenario: Indonesian AK3 — 2 categories
- **WHEN** language is `"id"`
- **THEN** AK3 SHALL output only:
  - `{n} Iklan Produk Otomatis Semua Halaman.`
  - `{n} Iklan Toko ({auto} Otomatis & {manual} Manual).`

#### Scenario: English AK3 — 4 categories
- **WHEN** language is `"en"`
- **THEN** AK3 SHALL output all four categories:
  - `{n} Iklan Produk Halaman Pencarian ({auto} Otomatis & {manual} Manual).`
  - `{n} Iklan Produk Halaman Rekomendasi ({auto} Otomatis & {manual} Manual).`
  - `{n} Iklan Produk Otomatis Semua Halaman.`
  - `{n} Iklan Toko ({auto} Otomatis & {manual} Manual).`

### Requirement: AK4 outputs different flags based on language
The calculator SHALL produce different recommendation flags depending on source language.

#### Scenario: Indonesian AK4 — 3 flags
- **WHEN** language is `"id"`
- **THEN** AK4 SHALL evaluate exactly these flags:
  1. Product participation (`product_pct < 0.5` → kurang maksimal / else sudah cukup baik)
  2. Active ratio (`active_ratio < 0.5` → kurang maksimal / elif `product_pct >= 0.5` → sudah cukup baik / else suppressed)
  3. Iklan Toko (`COUNTIF("Iklan Toko") = 0` → belum dimanfaatkan) — checks ALL rows including ended

#### Scenario: English AK4 — 9 flags
- **WHEN** language is `"en"`
- **THEN** AK4 SHALL evaluate exactly these flags:
  1. Product participation (same as Indonesian)
  2. Active ratio (same as Indonesian)
  3. Halaman Pencarian belum dimanfaatkan (no row with `Penempatan == "Halaman Pencarian"`)
  4. Halaman Pencarian (Bidding Otomatis) belum dimanfaatkan (no row with `Penempatan == "Halaman Pencarian"` AND `Mode Bidding == "Bidding Otomatis"`)
  5. Halaman Pencarian (Bidding Manual) belum dimanfaatkan (no row with `Penempatan == "Halaman Pencarian"` AND `Mode Bidding == "Bidding Manual"`)
  6. Halaman Rekomendasi belum dimanfaatkan (no row with `Penempatan == "Halaman Rekomendasi"`)
  7. Halaman Rekomendasi (Bidding Otomatis) belum dimanfaatkan (no row with `Penempatan == "Halaman Rekomendasi"` AND `Mode Bidding == "Bidding Otomatis"`)
  8. Halaman Rekomendasi (Bidding Manual) belum dimanfaatkan (no row with `Penempatan == "Halaman Rekomendasi"` AND `Mode Bidding == "Bidding Manual"`)
  9. Iklan Toko belum dimanfaatkan (same as Indonesian flag 3)
  - All flags check ALL rows including ended.

### Requirement: BOTTOM ads use different thresholds based on language
The calculator SHALL apply different BOTTOM ad selection thresholds depending on source language.

#### Scenario: Indonesian BOTTOM thresholds
- **WHEN** language is `"id"`
- **THEN** primary filter SHALL use `Biaya > 100000` and fallback ROAS cap SHALL be `min(round(AM10 * 2), 5)`

#### Scenario: English BOTTOM thresholds
- **WHEN** language is `"en"`
- **THEN** primary filter SHALL use `Biaya > 50000` and fallback ROAS cap SHALL be `min(round(AM10 * 2), 4)`

### Requirement: TOP ads fallback differs by language
The calculator SHALL handle TOP ads fallback differently based on source language.

#### Scenario: Indonesian TOP — has fallback
- **WHEN** language is `"id"` AND primary TOP query returns no results
- **THEN** calculator SHALL run the fallback query (`GMV > AM6/2`, `ROAS > max(AM7/2, 6)`)

#### Scenario: English TOP — no fallback
- **WHEN** language is `"en"` AND primary TOP query returns no results
- **THEN** AL2 SHALL be empty (no fallback query)

### Requirement: AL6 check differs by language
The calculator SHALL use different substring checks for AL6 (bottom auto flag) based on source language.

#### Scenario: Indonesian AL6
- **WHEN** language is `"id"`
- **THEN** AL6 SHALL trigger when `count("Otomatis") >= 1` in AL5 text

#### Scenario: English AL6
- **WHEN** language is `"en"`
- **THEN** AL6 SHALL trigger when `count("Bidding Otomatis") >= 1` in AL5 text

### Requirement: Calculator service validates language consistency
The calculator service SHALL ensure both CPC and Keyword uploads have the same source language before running the calculator.

#### Scenario: Matching languages
- **WHEN** CPC upload has `source_language: "en"` and Keyword upload has `source_language: "en"`
- **THEN** calculator SHALL run with `language="en"`

#### Scenario: Mismatched languages
- **WHEN** CPC upload has `source_language: "en"` and Keyword upload has `source_language: "id"` (or vice versa)
- **THEN** calculator service SHALL raise `CALC_MISSING_DATA` with detail explaining the language mismatch
