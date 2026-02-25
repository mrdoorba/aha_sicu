## Why

Account deletion silently fails on the Firebase Auth step. The Cloud Run service account lacks `firebaseauth.admin` IAM role, causing `auth.delete_user()` to throw `INSUFFICIENT_PERMISSION`. The backend catches this error silently, returns 204 to the admin, and leaves an orphaned Firebase Auth record. This was confirmed on 2026-02-23 when deleting user "Yusuf" — the DB row was removed but the Firebase Auth account persisted.

## What Changes

- Grant `roles/firebaseauth.admin` to the Cloud Run service account via Terraform so Firebase Admin SDK operations (especially delete) have sufficient permissions
- Change the account deletion API to fail visibly when Firebase deletion fails, instead of returning 204 with a silent warning log
- Admin sees the actual error and can take action, rather than assuming deletion succeeded

## Capabilities

### New Capabilities

_(none)_

### Modified Capabilities

- `admin-account-management`: Account deletion must fail with an error response when Firebase Auth deletion fails, instead of silently succeeding. The DB deletion should be rolled back if Firebase deletion cannot complete.

## Impact

- **Infrastructure (Terraform):** `iam.tf` — new IAM role binding for Cloud Run SA
- **Backend:** `service.py` — deletion flow error handling changes
- **Backend tests:** Update tests to cover Firebase failure → rollback scenario
- **No frontend changes** — the API contract (DELETE returns 204 on success, error on failure) stays the same, but now failure is actually surfaced
