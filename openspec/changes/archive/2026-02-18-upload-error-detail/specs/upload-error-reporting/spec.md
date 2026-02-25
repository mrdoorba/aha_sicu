## ADDED Requirements

### Requirement: Structured error detail extraction

The upload error handler SHALL extract the `detail` field from structured API error responses when available, instead of falling back to a generic message.

#### Scenario: Backend returns structured error with detail field

- **WHEN** the signed-url or process step fails with a response containing a `detail` field
- **THEN** the error state SHALL contain the backend's `detail` message

#### Scenario: Error has no structured detail

- **WHEN** any upload step fails with a plain Error (no `detail` field)
- **THEN** the error state SHALL use the Error's `message` property

#### Scenario: Error is not an Error instance

- **WHEN** any upload step fails with a non-Error value
- **THEN** the error state SHALL display "Upload failed"
