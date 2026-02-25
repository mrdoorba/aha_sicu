# upload-error-recovery Specification

## Purpose
On upload error, verify with the backend whether the upload actually succeeded before displaying failure to the user. Prevents false-negative errors caused by frontend timeouts or transient network issues during the process call.

## Requirements

### Requirement: Pre-upload state capture

Before initiating an upload, the system SHALL capture the current upload record (filename and uploaded_at) for the target file_type from the cached brand uploads data. This snapshot is used after an error to determine whether the backend saved a new upload.

#### Scenario: Snapshot is captured before upload starts

- **WHEN** a file upload is initiated for a given file_type
- **THEN** the system SHALL store the current upload's filename and uploaded_at for that file_type (or null if no prior upload exists) before the first network call

#### Scenario: No prior upload exists for the file_type

- **WHEN** a file upload is initiated and no prior upload record exists for that file_type
- **THEN** the snapshot SHALL be null, and any post-error upload record found for that file_type SHALL be treated as a successful new upload

### Requirement: Verification on upload error

When any stage of the upload flow throws an error, the system SHALL verify with the backend whether the upload actually succeeded before displaying an error to the user.

#### Scenario: Upload error with backend confirmation of success

- **WHEN** the upload flow throws an error (XHR network error, process timeout, or fetch failure)
- **AND** the system queries the backend and finds an upload record for the same file_type with a different filename or newer uploaded_at than the pre-upload snapshot
- **THEN** the system SHALL transition to the success state and invalidate relevant query caches (brandUploads, calculatorResults, calculatorStatus)

#### Scenario: Upload error with backend processing still in-flight

- **WHEN** the upload flow throws an error
- **AND** the immediate backend check shows no change from the pre-upload snapshot
- **THEN** the system SHALL retry the backend check up to 3 times at 5-second intervals (maximum 15 seconds total wait)

#### Scenario: Upload error confirmed as genuine failure

- **WHEN** the upload flow throws an error
- **AND** all verification attempts (immediate + up to 3 retries) show no change from the pre-upload snapshot
- **THEN** the system SHALL transition to the error state with the original error message

#### Scenario: Verification is aborted by new upload

- **WHEN** the verification polling is in progress
- **AND** the user initiates a new upload (via Retry or Re-upload)
- **THEN** the verification polling SHALL be cancelled and the new upload SHALL proceed normally

### Requirement: Verifying UI state

During the verification check, the system SHALL display a "verifying" state to the user instead of the error state.

#### Scenario: Verifying state display

- **WHEN** the upload flow has errored and verification is in progress
- **THEN** the UI SHALL display a spinner with the text "Verifying upload…"
- **AND** the UI SHALL NOT display the error message during verification

#### Scenario: Transition from verifying to success

- **WHEN** verification confirms the upload succeeded
- **THEN** the UI SHALL transition from "Verifying upload…" to the standard success state showing filename, row count, and timestamp

#### Scenario: Transition from verifying to error

- **WHEN** verification confirms the upload genuinely failed
- **THEN** the UI SHALL transition from "Verifying upload…" to the standard error state with the error message and Retry button
