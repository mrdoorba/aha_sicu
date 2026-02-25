## 1. Fix Existing Inaccuracies

- [x] 1.1 Fix DEFAULT_RULES description: change "DEFAULT_FASHION_RULES or DEFAULT_NON_FASHION_RULES" to accurately describe a single `DEFAULT_RULES` dict with fashion-specific behavior handled via `is_fashion` checks and DB rule overrides
- [x] 1.2 Fix ROI threshold description: clarify that `9.0` is the single default, and fashion `8.0` comes from DB-provided rules, not a separate hardcoded constant
- [x] 1.3 Fix conversion rate override flow: document that conversion rate starts at `3.0` in `_score_business()`, then gets overridden post-scoring at lines 1758-1764 of `calculate_score()` when template-specific rules apply

## 2. Add Formatting Functions Reference

- [x] 2.1 Add a "Formatting Functions Reference" section after "Data Conventions" listing all formatting functions: `_format_idr`, `_format_roas`, `_format_pct`, `_fmt_pct_1dp`, `_fmt_pct_0dp`, `_fmt_num_1dp`, `_fmt_num_2dp`, `_fmt_idr` (scoring variant with `.` separator), `_format_pct_1dp` (discount), `_roundup`, `_rounddown`, `_extract_pct`
- [x] 2.2 For each function, document: signature, format pattern, input→output examples, and which calculator/scoring rows use it

## 3. Add G-Column Message Templates (inline per category)

- [x] 3.1 Add message templates to Category 1 (Operational, rows 7-11): 10 templates (pass/fail for each of 5 rows) with `{val_str}`, `{threshold}` placeholders
- [x] 3.2 Add message templates to Category 2 (Business, rows 13, 20): pass/fail/fail_severe for row 13 with `{idr_val}`, `{change_pct}`, `{idr_avg}`; pass/fail for row 20 with `{val_str}`, `{benchmark}`
- [x] 3.3 Add message templates to Category 3 (Content, row 24): pass/fail with `{val_str}`, `{threshold}`
- [x] 3.4 Add message templates to Category 4 (Visitors, rows 28-29): pass/fail for each with `{val_str}`, `{threshold}`
- [x] 3.5 Add message templates to Category 5 (Promo, rows 31-43): 5 individual variants (zero, dependent, fail, pass, pass_afiliasi) with `{verdict}`, `{metric}`, `{pct_str}`, `{benchmark}`; plus summary row 42/43 templates
- [x] 3.6 Add message templates to Category 6 (Products, rows 45-46): pass/fail for product count with `{value_int}`, `{threshold}`; pass/fail for store status with `{store_status}`
- [x] 3.7 Add message templates to Category 7 (Ads, rows 50-53): ROI pass/fail, GMV ratio pass/fail/no_ads, cost ratio pass/fail/no_ads/too_minimal with all placeholders
- [x] 3.8 Add message templates to Category 8 (Campaign, row 57): pass/fail/no_data with `{pct_str}`, `{threshold}`
- [x] 3.9 Add message templates to Category 9 (Competition, rows 61-63): pass/fail with `{market_price}`

## 4. Add Complete DEFAULT_RULES Reference

- [x] 4.1 Add a "DEFAULT_RULES Reference" section with the complete rules structure organized as tables by category (operational, business, content, visitors, promo_tools, products_status, ads, campaign, stock, discount, marketing, competition, interpretation)
- [x] 4.2 Include all closing_messages in the interpretation section (6 verdict variants)

## 5. Add Fashion vs Non-Fashion Behavior Section

- [x] 5.1 Add a "Fashion vs Non-Fashion Behavior" section with a comparison table listing every difference: conversion rate threshold, ROI threshold, marketing floor, fashion adjustment, and upper limit
- [x] 5.2 Document the override mechanism: which differences are in DEFAULT_RULES vs DB rules vs `is_fashion` code checks

## 6. Add Edge Cases & Zero-State Behavior Section

- [x] 6.1 Document Calculator 1 zero-state: empty CPC data, empty keyword data, zero total_products
- [x] 6.2 Document Calculator 2 zero-state: empty order_data returns exact empty details structure
- [x] 6.3 Document Calculator 3 zero-state: empty order_data returns exact formatted zero output text
- [x] 6.4 Document scoring zero-states: missing calculator results (available=False), zero sales months, zero ad cost

## 7. Add Test Vectors Appendix

- [x] 7.1 Add Calculator 1 test vector: extract MND or KYPSO sample CPC/keyword data from tests with expected AK2/AK3/AK4 output and threshold calculations
- [x] 7.2 Add Calculator 2 test vector: extract sample order + mass_update data with expected output_1, output_2, and average_stock
- [x] 7.3 Add Calculator 3 test vector (no flag): extract SUKA-style sample with expected 4-line output
- [x] 7.4 Add Calculator 3 test vector (with flag): extract MND sample with expected 5-line output including exact totals (sum_n, sum_p, sum_voucher)
- [x] 7.5 Add threshold calculation test vector: AM6/AM7/AM9/AM10 from spec values (AM6=3,786,348, AM7=5, AM9=451,559, AM10=3)
