## ADDED Requirements

### Requirement: Formatting functions reference section
The document SHALL include a "Formatting Functions Reference" section listing every value formatting function used across the calculators and scoring system, with exact signature, format pattern, and input→output examples.

#### Scenario: Developer looks up IDR formatting
- **WHEN** a developer needs to know how monetary values are formatted
- **THEN** they find `_fmt_idr(value)` documented with format pattern `{rounded:,}` with `,`→`.` replacement and examples like `1250000 → "1.250.000"`, `-500000 → "-500.000"`

#### Scenario: Developer looks up percentage formatting
- **WHEN** a developer needs to distinguish between `_fmt_pct_1dp`, `_fmt_pct_0dp`, and `_format_pct` functions
- **THEN** they find each function with its formula (`fraction × 100` vs raw number), decimal places, and which scoring rows use which function

### Requirement: G-column message templates inline with scoring categories
The document SHALL include all G-column message templates with exact `{placeholder}` syntax, placed inline within each scoring category section alongside the existing threshold and formula documentation.

#### Scenario: Developer modifies operational category messaging
- **WHEN** a developer reads the "Category 1: Kesehatan Operasional Toko" section
- **THEN** they find both the scoring logic (thresholds, point values) AND the message templates for rows 7-11 with placeholders like `{val_str}`, `{threshold}` in the same section

#### Scenario: Developer modifies promo tool messaging
- **WHEN** a developer reads the "Category 5: Promo Toko" section
- **THEN** they find the 5 message variants (zero, dependent, fail, pass, pass_afiliasi) with their exact templates and placeholder names

#### Scenario: All ~40 templates documented
- **WHEN** a developer counts all documented G-column message templates
- **THEN** every message template from `DEFAULT_RULES` and inline defaults in `_generate_*_messages()` functions is present

### Requirement: Complete DEFAULT_RULES reference
The document SHALL include the complete `DEFAULT_RULES` structure presented as organized tables by category, showing all keys, thresholds, point values, comparison operators, and message templates.

#### Scenario: Developer verifies a threshold default
- **WHEN** a developer needs the default threshold for `unfulfilled_order_rate`
- **THEN** they find it in the DEFAULT_RULES reference as `threshold: 1.0, points: 4, comparison: lte`

#### Scenario: Single rules set clearly documented
- **WHEN** a developer reads about the rules system
- **THEN** the document clearly states there is ONE `DEFAULT_RULES` dict (not separate fashion/non-fashion sets) and explains how fashion-specific behavior is achieved via `is_fashion` checks and DB-provided rule overrides

### Requirement: Fashion vs non-fashion behavior section
The document SHALL include a dedicated section listing every behavioral difference between fashion and non-fashion templates, with the exact code path where each difference applies.

#### Scenario: Developer identifies all fashion differences
- **WHEN** a developer reads the "Fashion vs Non-Fashion" section
- **THEN** they find a complete table listing: conversion rate threshold (2% vs 3%), marketing floor (15% vs 12%), fashion adjustment (+5% vs 0%), and where each is applied in the scoring flow

#### Scenario: Conversion rate override flow documented
- **WHEN** a developer reads about the conversion rate threshold
- **THEN** they understand it starts at `3.0` from DEFAULT_RULES, and the fashion override (to `2.0`) comes from DB rules or template-specific logic applied post-scoring in `calculate_score()`

### Requirement: Edge cases and zero-state behavior section
The document SHALL include a section documenting what each calculator and the scoring system returns when given empty, zero, or missing input data.

#### Scenario: Empty order data for Calculator 2
- **WHEN** a developer checks what `calculate_top_sku([])` returns
- **THEN** they find the exact zero-state return: `output_text=""`, `details={output_1:[], output_2:[], average_stock:0, product_count:0, total_unique_products:0}`

#### Scenario: Missing calculator results in scoring
- **WHEN** a developer checks how scoring handles missing Calculator 2 results
- **THEN** they find that the Stock category returns `available=False, score=0` with message "Calculator 2 (Top SKU) belum dijalankan"

### Requirement: Test vectors appendix
The document SHALL include a "Test Vectors" appendix with sample input data and expected exact output for each calculator and a representative scoring scenario.

#### Scenario: Calculator 1 test vector
- **WHEN** a developer reimplements the ads keyword calculator
- **THEN** they can verify their implementation against documented sample CPC/keyword data with expected AK2, AK3, AK4, AL2, AL3, AL5 output

#### Scenario: Calculator 3 test vector with fake discount detection
- **WHEN** a developer reimplements the discount calculator
- **THEN** they can verify against the MND sample data with expected exact output text including "📌 Berpotensi menggunakan 'fake discount'"

#### Scenario: Calculator 3 test vector without fake discount
- **WHEN** a developer reimplements the discount calculator
- **THEN** they can also verify against a sample (like SUKA) where the fake discount flag is NOT triggered

### Requirement: Fix inaccuracies in existing documentation
The document SHALL correct known inaccuracies in the current version.

#### Scenario: DEFAULT_RULES description corrected
- **WHEN** a developer reads about the rules fallback system
- **THEN** the document says "single `DEFAULT_RULES` dict" (not "DEFAULT_FASHION_RULES or DEFAULT_NON_FASHION_RULES")

#### Scenario: ROI threshold accurately described
- **WHEN** a developer reads about the ROI threshold
- **THEN** they understand the default is `9.0` from DEFAULT_RULES, and fashion-specific `8.0` comes from DB-provided rules (not a separate hardcoded constant)
