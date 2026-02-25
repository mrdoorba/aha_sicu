## MODIFIED Requirements

### Requirement: Structured error detail extraction

The upload error handler SHALL extract the `detail` field from structured API error responses when available, instead of falling back to a generic message. Additionally, the process step SHALL enforce a timeout and surface a user-friendly message when the backend takes too long.

#### Scenario: Backend returns structured error with detail field

- **WHEN** the signed-url or process step fails with a response containing a `detail` field
- **THEN** the error state SHALL contain the backend's `detail` message

#### Scenario: Error has no structured detail

- **WHEN** any upload step fails with a plain Error (no `detail` field)
- **THEN** the error state SHALL use the Error's `message` property

#### Scenario: Error is not an Error instance

- **WHEN** any upload step fails with a non-Error value
- **THEN** the error state SHALL display "Upload failed"

#### Scenario: Process request exceeds timeout

- **WHEN** the POST `/api/v1/upload/process` request does not complete within 120 seconds
- **THEN** the request SHALL be aborted and the error state SHALL display a message indicating the file may be too large to process (e.g., "Processing timed out. The file may be too large — try splitting it into smaller parts.")
