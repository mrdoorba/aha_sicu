# upload-memory-optimization Specification

## Purpose
Memory-efficient processing for large ZIP uploads containing multiple Excel parts, reducing peak memory footprint during the parse-to-store pipeline. Also ensures calculator validation handles legacy double-encoded parsed_data.

## Requirements
### Requirement: Eager memory release during upload processing

The upload processing pipeline SHALL explicitly free intermediate data structures after each processing stage to minimize peak memory usage.

#### Scenario: ZIP file bytes freed after parsing

- **WHEN** a ZIP file has been downloaded from storage and parsed into a DataFrame
- **THEN** the raw file bytes SHALL be released from memory before proceeding to JSON conversion

#### Scenario: DataFrame freed after JSON conversion

- **WHEN** a parsed DataFrame has been converted to JSON-serializable format via `dataframe_to_json`
- **THEN** the DataFrame SHALL be released from memory before proceeding to database storage

### Requirement: Cloud Run memory allocation supports large order exports

The Cloud Run service SHALL be allocated sufficient memory to process Order Export ZIP files up to 20 MB containing up to 10,000 rows.

#### Scenario: 9 MB ZIP with thousands of order rows

- **WHEN** a user uploads a 9 MB Order Export ZIP containing ~5,000 order rows
- **THEN** the processing SHALL complete successfully without OOM termination

### Requirement: Calculator handles double-encoded parsed_data

The calculator validation layer SHALL handle `parsed_data` that is stored as a JSON string (double-encoded) in addition to properly-encoded dict format.

#### Scenario: parsed_data is a dict (normal case)

- **WHEN** a calculator retrieves `parsed_data` as a dict with a `columns` key
- **THEN** column validation SHALL proceed normally

#### Scenario: parsed_data is a JSON string (legacy double-encoded)

- **WHEN** a calculator retrieves `parsed_data` as a JSON string
- **THEN** the system SHALL parse the string into a dict before column validation

#### Scenario: parsed_data is None or empty

- **WHEN** a calculator retrieves `parsed_data` as None or empty string
- **THEN** the system SHALL raise a CALC_MISSING_DATA error with a descriptive message
