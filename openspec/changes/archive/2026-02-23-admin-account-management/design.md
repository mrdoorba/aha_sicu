## Context

The application currently auto-provisions users on first Firebase login. There is no way to manage accounts without direct database/Firebase console access. The existing role system (`member`, `leader`, `admin`) is in place but roles can only be changed manually in the DB.

Four tables reference `users.id`:
- `evaluation_inputs.user_id` (NOT NULL, RESTRICT)
- `evaluations.user_id` (NOT NULL, RESTRICT)
- `brand_uploads.uploaded_by` (NOT NULL, RESTRICT)
- `scoring_rules.updated_by` (NULLABLE, RESTRICT)

## Goals / Non-Goals

**Goals:**
- Admin-only page to list, create, update role, reset password, and delete user accounts
- Safe deletion: retain all evaluation/upload/rule data when a user is removed
- Self-protection: admin cannot modify or delete their own account
- UI text in Bahasa Indonesia

**Non-Goals:**
- Email-based invite/password-reset flow (Firebase email delivery not configured)
- User self-service profile editing
- Disable/enable toggle (delete only)
- Pagination or search (user count is small, internal tool)

## Decisions

### 1. Hard delete with SET NULL references

**Decision**: Delete the user row from DB and Firebase. Before deletion, set all FK references to NULL.

**Why**: User requested no soft-delete to keep the users table clean. Evaluations and uploads are retained with `user_id = NULL`, displayed as "Pengguna Dihapus" in the UI.

**Alternative considered**: Soft delete with `deleted_at` column — rejected because user prefers a clean table without ghost rows.

**Migration**: A new migration will ALTER the 4 FK columns:
- `evaluation_inputs.user_id` → DROP NOT NULL, SET ON DELETE SET NULL
- `evaluations.user_id` → DROP NOT NULL, SET ON DELETE SET NULL
- `brand_uploads.uploaded_by` → DROP NOT NULL, SET ON DELETE SET NULL
- `scoring_rules.updated_by` → already NULLABLE, just change to ON DELETE SET NULL

### 2. Password set by admin directly

**Decision**: Use `firebase_admin.auth.update_user(uid, password=new_password)` to let admin set a new password directly.

**Why**: Firebase email delivery is not configured. Admin sets password, communicates it to user out-of-band.

**Alternative considered**: `generate_password_reset_link()` — rejected because email delivery isn't set up.

### 3. Backend module structure

**Decision**: New `backend/app/modules/accounts/` module with router, schemas, service, and queries — following the same pattern as `rules` and `evaluations` modules.

**Endpoints** (all require `require_role("admin")`):

| Method | Path | Action |
|--------|------|--------|
| GET | `/api/v1/accounts` | List all users |
| POST | `/api/v1/accounts` | Create new account |
| PATCH | `/api/v1/accounts/{id}/role` | Update user role |
| POST | `/api/v1/accounts/{id}/reset-password` | Reset password |
| DELETE | `/api/v1/accounts/{id}` | Delete account |

### 4. Self-protection guard

**Decision**: Backend rejects any modify/delete request where `target_user_id == current_user.id`. Frontend also disables controls on the admin's own row.

**Why**: Prevents admin from locking themselves out. Both layers enforce this for defense in depth.

### 5. Create account flow

**Decision**: Admin provides email + password + role. Backend creates Firebase account first, then inserts into DB with the Firebase UID.

**Rollback**: If DB insert fails after Firebase creation, delete the Firebase account to avoid orphans.

### 6. Frontend page structure

**Decision**: Single `AccountsPage` component with:
- User table (email, role dropdown, last login, action buttons)
- "Buat Akun" button → dialog with form (email, password, role)
- Reset password → dialog with password input
- Delete → confirmation dialog
- Role change → inline dropdown, immediate PATCH on change

Follows existing patterns from `RulesPage` and `HistoryPage`.

## Risks / Trade-offs

- **[Orphaned Firebase account]** → If DB delete succeeds but Firebase delete fails, user can't login (no DB row) but Firebase account lingers. Mitigation: delete Firebase last, log failures for manual cleanup.
- **[No undo for delete]** → Hard delete is permanent. Mitigation: confirmation dialog with user email displayed. Backend returns 409 if trying to delete self.
- **[Password visibility]** → Admin sees/sets the password in plaintext during creation and reset. Mitigation: acceptable for internal tool with small user base. Password field uses type="password" in UI.
