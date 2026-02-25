## ADDED Requirements

### Requirement: Manual calculate trigger for ready calculators

When a calculator has all dependencies satisfied but no result exists, the UI SHALL display a "Calculate" button that allows the user to manually trigger that calculator.

#### Scenario: Calculate button in ready-but-no-result state

- **WHEN** a calculator card has status "ready" (all required files uploaded, no missing manual inputs) and no stored result
- **THEN** the UI SHALL display a "Calculate" button alongside the "Ready to calculate" text
- **AND** clicking the button SHALL call the individual calculator's run endpoint

#### Scenario: Calculate button shows loading state

- **WHEN** the user clicks the "Calculate" button
- **THEN** the button SHALL show a loading spinner and be disabled until the calculation completes or fails

#### Scenario: Calculate button shows error on failure

- **WHEN** the user clicks "Calculate" and the calculator endpoint returns an error
- **THEN** the UI SHALL display the error message with a "Retry" button

### Requirement: Calculate All button visibility

The "Calculate All" button SHALL be visible whenever any calculator is in a ready state, regardless of whether other calculators already have results.

#### Scenario: Calculate All visible with no existing results

- **WHEN** at least one calculator has status "ready" and no calculator has a stored result
- **THEN** the UI SHALL display a "Calculate All" button in the Calculator Results section header

#### Scenario: Calculate All visible with mixed states

- **WHEN** some calculators have results and at least one calculator has status "ready" without a result
- **THEN** the UI SHALL display a "Calculate All" button (labeled "Recalculate All" when results exist)

#### Scenario: Calculate All hidden when no calculator is actionable

- **WHEN** no calculator has status "ready" (all are pending or all have results with no ready-but-no-result calculators)
- **THEN** the "Calculate All" button SHALL NOT be displayed

### Requirement: Post-upload calculator cache invalidation

After a successful file upload and processing, the frontend SHALL always invalidate calculator result and status caches, regardless of whether the auto-calculated response contains any items.

#### Scenario: Cache invalidated when auto-calc returns results

- **WHEN** a file upload is processed successfully and the response includes auto_calculated items with status "success"
- **THEN** the frontend SHALL invalidate both `calculatorResults` and `calculatorStatus` query caches

#### Scenario: Cache invalidated when auto-calc returns empty

- **WHEN** a file upload is processed successfully and the response includes an empty auto_calculated array
- **THEN** the frontend SHALL still invalidate both `calculatorResults` and `calculatorStatus` query caches

### Requirement: Auto-calc error visibility

When auto-calculation fails during file upload, the affected calculator card SHALL display a warning indicating that auto-calculation failed, with the option to manually trigger calculation.

#### Scenario: Auto-calc error shown in calculator card

- **WHEN** a file upload response contains an auto_calculated item with status "error" for a given calculator type
- **THEN** the calculator card for that type SHALL display a warning message indicating auto-calculation failed
- **AND** the card SHALL display a "Calculate" button for manual retry

#### Scenario: Auto-calc error cleared on successful calculation

- **WHEN** the user manually runs a calculator that previously had an auto-calc error
- **AND** the manual calculation succeeds
- **THEN** the auto-calc error warning SHALL be cleared and replaced with the calculator result

#### Scenario: Auto-calc error cleared on new upload

- **WHEN** a new file is uploaded for a file type that affects the calculator with an auto-calc error
- **THEN** the previous auto-calc error SHALL be cleared (replaced by the new upload's auto-calc status)
