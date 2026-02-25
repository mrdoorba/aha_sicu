## ADDED Requirements

### Requirement: Brand header displays curated VP fields
The EvaluationHeader component SHALL display the following fields from `raw_data` in this exact order:
1. BD
2. Link Shopee Mall / LazMall
3. Kategori
4. Shopee Mall
5. No OPEX Issue
6. Omset >100jt
7. Score VP
8. No WA
9. Email

#### Scenario: All fields present
- **WHEN** a brand's `raw_data` contains all 9 curated fields
- **THEN** all 9 fields SHALL be displayed in the specified order

#### Scenario: Some fields missing or empty
- **WHEN** a brand's `raw_data` does not contain a curated field, or its value is empty/null
- **THEN** that field SHALL be omitted from the display (no empty label shown)

#### Scenario: Field contains a URL
- **WHEN** a curated field value starts with `https://` or `http://` (e.g., Link Shopee Mall / LazMall)
- **THEN** it SHALL render as a clickable link (existing URL detection behavior)

## REMOVED Requirements

### Requirement: Generic first-6-fields display
**Reason**: Replaced by curated field list — the generic `.slice(0, 6)` approach showed irrelevant fields while hiding important ones.
**Migration**: No migration needed. The `getDisplayFields` function is replaced with curated field logic.
