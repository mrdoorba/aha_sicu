## ADDED Requirements

### Requirement: Admin can list all users
The system SHALL provide an API endpoint `GET /api/v1/accounts` that returns all users. The endpoint SHALL require admin role. The response SHALL include each user's id, email, role, created_at, and last_login.

#### Scenario: Admin lists users
- **WHEN** an authenticated admin requests the user list
- **THEN** the system returns all users with id, email, role, created_at, and last_login

#### Scenario: Non-admin attempts to list users
- **WHEN** a user with member or leader role requests the user list
- **THEN** the system returns 403 Forbidden

### Requirement: Admin can create a new account
The system SHALL provide an API endpoint `POST /api/v1/accounts` that creates a new user account. The endpoint SHALL require admin role. The request body SHALL include email, password, and role. The system SHALL create a Firebase Auth account and a corresponding database record. If the database insert fails, the system SHALL rollback by deleting the Firebase account.

#### Scenario: Admin creates a new account
- **WHEN** an admin submits a valid email, password, and role
- **THEN** the system creates a Firebase account, inserts the user into the database, and returns the new user record

#### Scenario: Admin creates account with duplicate email
- **WHEN** an admin submits an email that already exists in Firebase
- **THEN** the system returns 409 Conflict with an appropriate error message

#### Scenario: Admin creates account with invalid password
- **WHEN** an admin submits a password shorter than 6 characters
- **THEN** the system returns 400 Bad Request (Firebase minimum requirement)

### Requirement: Admin can update a user's role
The system SHALL provide an API endpoint `PATCH /api/v1/accounts/{id}/role` that updates a user's role. The endpoint SHALL require admin role. The allowed roles SHALL be member, leader, and admin.

#### Scenario: Admin changes user role
- **WHEN** an admin updates another user's role to a valid role value
- **THEN** the system updates the role in the database and returns the updated user record

#### Scenario: Admin attempts to change own role
- **WHEN** an admin attempts to update their own role
- **THEN** the system returns 409 Conflict with message indicating self-modification is not allowed

#### Scenario: Admin sets an invalid role
- **WHEN** an admin submits a role value not in (member, leader, admin)
- **THEN** the system returns 422 Unprocessable Entity

### Requirement: Admin can reset a user's password
The system SHALL provide an API endpoint `POST /api/v1/accounts/{id}/reset-password` that sets a new password for a user. The endpoint SHALL require admin role. The system SHALL use Firebase Admin SDK to update the user's password directly.

#### Scenario: Admin resets user password
- **WHEN** an admin submits a new password for another user
- **THEN** the system updates the password in Firebase Auth

#### Scenario: Admin attempts to reset own password
- **WHEN** an admin attempts to reset their own password via this endpoint
- **THEN** the system returns 409 Conflict

### Requirement: Admin can delete a user account
The system SHALL provide an API endpoint `DELETE /api/v1/accounts/{id}` that deletes a user account. The endpoint SHALL require admin role. The system SHALL delete the user row from the database (FK references become NULL via ON DELETE SET NULL), then delete the Firebase Auth account.

#### Scenario: Admin deletes a user
- **WHEN** an admin deletes another user's account
- **THEN** the system deletes the DB row (setting FK references to NULL), deletes the Firebase account, and returns 204

#### Scenario: Admin attempts to delete own account
- **WHEN** an admin attempts to delete their own account
- **THEN** the system returns 409 Conflict

#### Scenario: Evaluations retained after user deletion
- **WHEN** a user with existing evaluations is deleted
- **THEN** the evaluation records remain with user_id set to NULL

### Requirement: Database supports user deletion with data retention
The system SHALL alter foreign key constraints on evaluation_inputs.user_id, evaluations.user_id, brand_uploads.uploaded_by, and scoring_rules.updated_by to use ON DELETE SET NULL. The columns evaluation_inputs.user_id, evaluations.user_id, and brand_uploads.uploaded_by SHALL be changed from NOT NULL to NULLABLE.

#### Scenario: FK constraints allow user deletion
- **WHEN** a user row is deleted from the users table
- **THEN** all referencing columns in evaluation_inputs, evaluations, brand_uploads, and scoring_rules are set to NULL

### Requirement: Admin account management page
The frontend SHALL provide an admin-only page at route `/accounts` protected by RoleProtectedRoute with allowedRoles=['admin']. The page SHALL display a table of all users and provide controls for creating accounts, changing roles, resetting passwords, and deleting accounts. All UI text SHALL be in Bahasa Indonesia.

#### Scenario: Admin views the accounts page
- **WHEN** an admin navigates to /accounts
- **THEN** the page displays a table with columns: Email, Peran (role), Login Terakhir, and Aksi

#### Scenario: Non-admin cannot access accounts page
- **WHEN** a member or leader navigates to /accounts
- **THEN** the system redirects to /dashboard with an access denied toast

#### Scenario: Admin creates account via dialog
- **WHEN** an admin clicks "Buat Akun" and fills in email, password, and role
- **THEN** the system creates the account and shows a success toast "Akun berhasil dibuat"

#### Scenario: Admin changes role via dropdown
- **WHEN** an admin selects a new role from the dropdown on another user's row
- **THEN** the system updates the role immediately

#### Scenario: Admin row controls are disabled
- **WHEN** the accounts table renders the current admin's own row
- **THEN** the role dropdown and action buttons (reset password, delete) are disabled

#### Scenario: Admin deletes account via dialog
- **WHEN** an admin clicks delete and confirms in the confirmation dialog
- **THEN** the system deletes the account and shows a success toast "Akun berhasil dihapus"

#### Scenario: Deleted user shown in evaluations
- **WHEN** viewing an evaluation whose user_id is NULL
- **THEN** the UI displays "Pengguna Dihapus" instead of the user's email

### Requirement: Navigation shows Accounts link for admin
The Header component SHALL display an "Akun" navigation link to /accounts only when the current user's role is admin.

#### Scenario: Admin sees Accounts link
- **WHEN** an admin views the header navigation
- **THEN** an "Akun" link is visible pointing to /accounts

#### Scenario: Non-admin does not see Accounts link
- **WHEN** a member or leader views the header navigation
- **THEN** no "Akun" link is displayed
