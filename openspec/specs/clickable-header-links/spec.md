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

### Requirement: URL field values render as clickable links
The EvaluationHeader component SHALL render field values that are URLs as clickable hyperlinks (`<a>` elements) instead of plain text. A value is considered a URL if it starts with `https://` or `http://`.

#### Scenario: Field value is a URL
- **WHEN** a brand's raw_data field value starts with `https://` or `http://`
- **THEN** the value SHALL be rendered as a clickable `<a>` element with `target="_blank"` and `rel="noopener noreferrer"`

#### Scenario: Field value is not a URL
- **WHEN** a brand's raw_data field value does not start with `https://` or `http://`
- **THEN** the value SHALL be rendered as plain text (existing behavior)

#### Scenario: URL link in meeting data fields
- **WHEN** a meeting_raw_data field value starts with `https://` or `http://`
- **THEN** the value SHALL also be rendered as a clickable link with the same behavior
