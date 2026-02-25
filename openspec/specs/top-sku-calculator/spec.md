## MODIFIED Requirements

### Requirement: Mass update lookup uses first-match semantics
When building the mass update lookup (`name_to_kode` mapping), the system SHALL use the first matching entry for a given product label (Nama Produk + Nama Variasi), matching VLOOKUP first-match-wins behavior. Subsequent duplicate entries for the same label SHALL be ignored for the kode mapping.

#### Scenario: Duplicate product labels in mass update
- **WHEN** mass update data contains two entries with the same "Nama Produk - Nama Variasi" label but different Kode Variasi values
- **THEN** the system SHALL use the Kode Variasi from the first entry encountered
- **AND** the stock lookup SHALL use the stock associated with that first Kode Variasi

#### Scenario: Unique product labels in mass update
- **WHEN** mass update data contains only one entry per product label
- **THEN** behavior SHALL be unchanged from current implementation
