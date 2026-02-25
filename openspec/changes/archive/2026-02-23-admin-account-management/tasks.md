## 1. Database Migration

- [x] 1.1 Create migration to alter FK constraints on evaluation_inputs.user_id, evaluations.user_id, brand_uploads.uploaded_by to DROP NOT NULL and set ON DELETE SET NULL
- [x] 1.2 Alter scoring_rules.updated_by FK constraint to ON DELETE SET NULL (already nullable)

## 2. Backend — Accounts Module

- [x] 2.1 Create module structure: `backend/app/modules/accounts/` with router.py, schemas.py, service.py, queries.py
- [x] 2.2 Implement queries: get_all_users, create_user, update_user_role, delete_user
- [x] 2.3 Implement schemas: UserListResponse, CreateAccountRequest (email, password, role), UpdateRoleRequest, ResetPasswordRequest
- [x] 2.4 Implement service layer: create_account (Firebase + DB with rollback), update_role, reset_password (Firebase Admin SDK), delete_account (DB delete + Firebase delete)
- [x] 2.5 Implement router with all endpoints (GET, POST, PATCH, POST reset-pw, DELETE) — all with require_role("admin")
- [x] 2.6 Add self-protection guard: reject requests where target user_id == current user id (409 Conflict)
- [x] 2.7 Register accounts router in main.py

## 3. Backend Tests

- [x] 3.1 Write tests for accounts queries (get_all_users, create_user, update_user_role, delete_user)
- [x] 3.2 Write tests for accounts endpoints (list, create, update role, reset password, delete) including role enforcement and self-protection

## 4. Frontend — API & Hooks

- [x] 4.1 Add accounts API types and service functions (listAccounts, createAccount, updateRole, resetPassword, deleteAccount)
- [x] 4.2 Create React Query hooks: useAccounts, useCreateAccount, useUpdateRole, useResetPassword, useDeleteAccount

## 5. Frontend — Accounts Page

- [x] 5.1 Create AccountsPage component with user table (Email, Peran, Login Terakhir, Aksi columns)
- [x] 5.2 Implement inline role dropdown with immediate PATCH on change, disabled for own row
- [x] 5.3 Implement "Buat Akun" button and create account dialog (email, password, role fields)
- [x] 5.4 Implement reset password dialog
- [x] 5.5 Implement delete confirmation dialog
- [x] 5.6 Disable action controls (reset password, delete) on admin's own row

## 6. Frontend — Routing & Navigation

- [x] 6.1 Add /accounts route in App.tsx with RoleProtectedRoute (admin-only)
- [x] 6.2 Add "Akun" navigation link in Header, visible only to admin role

## 7. Frontend — Deleted User Display

- [x] 7.1 Update evaluation display components to show "Pengguna Dihapus" when user_id is NULL

## 8. Frontend Tests

- [x] 8.1 Write tests for AccountsPage (table rendering, dialogs, role dropdown, self-protection UI)
- [x] 8.2 Write tests for Header showing/hiding Akun link based on role
