## Why

There is no way to manage user accounts in the application. Users are auto-provisioned on first login, and roles can only be changed directly in the database. Admins need a dedicated page to create accounts, assign roles, reset passwords, and remove users — all without touching the database or Firebase console.

## What Changes

- Add a new admin-only page at `/accounts` for managing user accounts
- Add backend API endpoints for account CRUD operations (list, create, update role, reset password, delete)
- Integrate Firebase Admin SDK for account creation, password reset, and deletion
- On user deletion: remove Firebase account, set evaluation references to NULL, then delete DB row
- Add navigation link visible only to admin role
- All UI text in Bahasa Indonesia

## Capabilities

### New Capabilities
- `admin-account-management`: Admin-only page and API for managing user accounts — list users, create accounts (email + password + role), change roles, reset passwords, and delete accounts. Includes guard preventing admin from modifying/deleting their own account.

### Modified Capabilities
<!-- No existing spec-level requirements are changing -->

## Impact

- **Backend**: New `accounts` module with router, schemas, and queries. New DB migration to make `user_id` nullable in evaluation-related tables (for ON DELETE SET NULL behavior).
- **Frontend**: New `AccountsPage` component, new API hooks, new route with `RoleProtectedRoute` (admin-only), updated Header navigation.
- **Firebase**: Uses Firebase Admin SDK (already initialized in backend) for `create_user`, `update_user`, `delete_user`.
- **Database**: Migration to alter foreign key constraints on evaluation tables to SET NULL on delete.
