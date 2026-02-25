## MODIFIED Requirements

### Requirement: Admin can delete a user account
The system SHALL provide an API endpoint `DELETE /api/v1/accounts/{id}` that deletes a user account. The endpoint SHALL require admin role. The system SHALL delete the user row from the database and the Firebase Auth account within a single logical operation. If the Firebase Auth deletion fails, the system SHALL rollback the database deletion and return an error response. The endpoint SHALL return 204 only when both the database row and the Firebase Auth account are successfully deleted.

#### Scenario: Admin deletes a user
- **WHEN** an admin deletes another user's account
- **THEN** the system deletes the DB row (setting FK references to NULL), deletes the Firebase account, and returns 204

#### Scenario: Admin attempts to delete own account
- **WHEN** an admin attempts to delete their own account
- **THEN** the system returns 409 Conflict

#### Scenario: Evaluations retained after user deletion
- **WHEN** a user with existing evaluations is deleted
- **THEN** the evaluation records remain with user_id set to NULL

#### Scenario: Firebase deletion fails
- **WHEN** the database row is deleted but Firebase Auth deletion fails (e.g., permission error, network error)
- **THEN** the system rolls back the database deletion, preserving the user row intact
- **AND** returns 502 with error code `FIREBASE_DELETE_FAILED` and a message indicating Firebase cleanup failed

#### Scenario: Firebase deletion fails — no orphaned state
- **WHEN** Firebase Auth deletion fails during account deletion
- **THEN** the user record remains fully intact in both the database and Firebase Auth (no partial deletion)
