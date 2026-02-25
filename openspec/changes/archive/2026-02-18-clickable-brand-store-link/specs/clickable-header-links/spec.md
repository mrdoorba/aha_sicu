## ADDED Requirements

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
