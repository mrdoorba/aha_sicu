## MODIFIED Requirements

### Requirement: G72/G73 marketing budget recommendation
The system SHALL compute the marketing budget recommendation using a two-branch comparison matching the spreadsheet logic:

1. Compute `capped_value` = `MAX(MAX(MIN(MIN(ROUNDDOWN(avg - 3%, 2), upper_limit), g68_left), 10%), floor)` where `g68_left` is the raw percentage extracted from G68 text before the "~" delimiter
2. Compute `ceiling_g68` = `CEILING(first_number_from_G68 / 100, 0.01)` (rounded up to nearest 0.01)
3. Compare: if `capped_value > ceiling_g68`, use `capped_value`; otherwise use `ceiling_g68`
4. Clamp the final result to the display range (10% - 25%)

This allows non-fashion stores to receive recommendations above 20% when the G68 competitor analysis supports it, rather than being hard-capped at 20%.

#### Scenario: Non-fashion store where capped value exceeds ceiling_g68 (G72=TRUE)
- **WHEN** a non-fashion store has discount/voucher/ad data that produces a capped value of 0.20 and G68 is "15.3% ~ 22.7%" (ceiling_g68 = 0.16)
- **THEN** `_compute_g72` SHALL return 0.20 (the capped value, since 0.20 > 0.16)

#### Scenario: Non-fashion store where capped value does NOT exceed ceiling_g68 (G72=FALSE)
- **WHEN** a non-fashion store has discount/voucher/ad data that produces a capped value of 0.14 and G68 is "15.3% ~ 22.7%" (ceiling_g68 = 0.16)
- **THEN** `_compute_g72` SHALL return 0.16 (the ceiling_g68 value, since 0.14 is NOT > 0.16)

#### Scenario: Non-fashion store with high G68 ceiling exceeding 20%
- **WHEN** a non-fashion store has G68 = "22.0% ~ 28.5%" (ceiling_g68 = 0.22) and capped value is 0.20
- **THEN** `_compute_g72` SHALL return 0.22 (ceiling_g68 used because 0.20 is NOT > 0.22), and G73 SHALL display "22%" in the recommendation text

#### Scenario: Fashion store retains existing behavior
- **WHEN** a fashion store has data producing a capped value of 0.25 and ceiling_g68 = 0.20
- **THEN** `_compute_g72` SHALL return 0.25 (capped value, since 0.25 > 0.20)

#### Scenario: G68 text is empty
- **WHEN** G68 text is empty (no competitor analysis data)
- **THEN** `_compute_g72` SHALL return the capped value using the existing MIN/MAX chain without the G68 comparison branch

#### Scenario: G68 text without "~" delimiter
- **WHEN** G68 text does not contain a "~" character
- **THEN** the g68_left extraction SHALL default to 0.0, causing the comparison to evaluate as FALSE, and the ceiling_g68 value SHALL be used as the result

### Requirement: G68 left-side value extraction
The system SHALL extract the G68 "left" value (for the MIN chain) by parsing the text before the "~" delimiter and converting to a float fraction. This is distinct from the ceiling extraction used for the fallback branch.

#### Scenario: Standard G68 format
- **WHEN** G68 text is "15.3% ~ 22.7%"
- **THEN** g68_left SHALL be 0.153 (the percentage before "~" converted to fraction)

#### Scenario: G68 with no tilde
- **WHEN** G68 text has no "~" character
- **THEN** g68_left SHALL default to 0.0
