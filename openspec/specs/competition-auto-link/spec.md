## Requirements

### Requirement: Auto-compute Shopee search link from selling price and keyword
The system SHALL automatically compute the competition product link using the Shopee search URL pattern whenever both `sellingPrice` and `keyword` are present. The computed URL SHALL use the format:
```
https://shopee.co.id/search?keyword={encodedKeyword}&maxPrice={sellingPrice×1.10}&minPrice={sellingPrice×0.75}&noCorrection=true&page=0&ratingFilter=4&sortBy=sales
```
where `maxPrice` and `minPrice` are rounded to the nearest integer.

#### Scenario: Both sellingPrice and keyword are present
- **WHEN** a competition product has `sellingPrice = 85000` and `keyword = "kaos polos"`
- **THEN** the system SHALL compute the link as `https://shopee.co.id/search?keyword=kaos%20polos&maxPrice=93500&minPrice=63750&noCorrection=true&page=0&ratingFilter=4&sortBy=sales`

#### Scenario: sellingPrice is missing
- **WHEN** a competition product has `sellingPrice = null` and `keyword = "kaos polos"`
- **THEN** the system SHALL set the link to `null`

#### Scenario: keyword is missing
- **WHEN** a competition product has `sellingPrice = 85000` and `keyword = null`
- **THEN** the system SHALL set the link to `null`

#### Scenario: Both inputs are missing
- **WHEN** a competition product has `sellingPrice = null` and `keyword = null`
- **THEN** the system SHALL set the link to `null`

### Requirement: Persist computed link via existing auto-save
The system SHALL store the computed link value in the `CompetitionProduct.link` field and persist it to the database through the existing auto-save mechanism. The link SHALL be recomputed and saved whenever `sellingPrice` or `keyword` changes.

#### Scenario: User changes sellingPrice
- **WHEN** a user updates the `sellingPrice` field of a competition product that already has a `keyword`
- **THEN** the system SHALL recompute the link with the new price and save it

#### Scenario: User changes keyword
- **WHEN** a user updates the `keyword` field of a competition product that already has a `sellingPrice`
- **THEN** the system SHALL recompute the link with the new keyword and save it

### Requirement: Display link as clickable hyperlink
The system SHALL display the computed link as a clickable hyperlink (`<a>` element) with `target="_blank"` and `rel="noopener noreferrer"` instead of a text input field.

#### Scenario: Link is computed (both inputs present)
- **WHEN** a competition product has a computed link
- **THEN** the system SHALL display a clickable hyperlink labeled with the translated link label text, opening the Shopee search in a new tab

#### Scenario: Link is null (inputs incomplete)
- **WHEN** a competition product has no computed link
- **THEN** the system SHALL display muted placeholder text indicating that selling price and keyword are required

### Requirement: Keyword with special characters is URL-encoded
The system SHALL URL-encode the keyword value using `encodeURIComponent` to handle spaces, ampersands, and other special characters.

#### Scenario: Keyword with spaces
- **WHEN** the keyword is `"kaos polos pria"`
- **THEN** the encoded keyword in the URL SHALL be `kaos%20polos%20pria`

#### Scenario: Keyword with ampersand
- **WHEN** the keyword is `"tas & dompet"`
- **THEN** the encoded keyword in the URL SHALL be `tas%20%26%20dompet`
