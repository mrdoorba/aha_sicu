## Context

Account deletion has a two-phase flow: delete from Postgres (Neon) first, then delete from Firebase Auth. The Firebase step currently fails silently with `INSUFFICIENT_PERMISSION` because the Cloud Run service account (`aha-sicu-{env}-api-sa`) lacks the `firebaseauth.admin` IAM role. The API returns 204 regardless, leaving orphaned Firebase Auth records.

Current deletion flow in `service.py:107-138`:
1. Delete DB row (inside `db.connection()` context manager)
2. Attempt Firebase `auth.delete_user()` outside the DB transaction
3. On failure: log warning, swallow exception

## Goals / Non-Goals

**Goals:**
- Grant Firebase Auth Admin permissions to Cloud Run SA via Terraform
- Make deletion atomic: if Firebase delete fails, roll back the DB deletion
- Surface Firebase errors to the admin via API error response

**Non-Goals:**
- Changing the deletion order (DB-first then Firebase is fine once permissions are fixed; rollback handles failure)
- Adding retry logic or background job for failed deletions
- Changing the frontend — the existing error handling (toast on non-204) already covers this

## Decisions

### 1. IAM role: `roles/firebaseauth.admin`

Add a project-level IAM binding in `iam.tf` granting `roles/firebaseauth.admin` to the Cloud Run SA.

**Why this role:** It's the narrowest predefined role that covers `firebaseauth.users.delete`, `firebaseauth.users.create`, and `firebaseauth.users.update` — all operations our backend performs. There is no single-permission role for just delete.

**Alternative considered:** `roles/firebase.admin` — too broad, grants access to all Firebase services (Firestore, Storage, etc.) which we don't need.

### 2. Deletion flow: DB delete inside transaction, rollback on Firebase failure

Restructure `delete_account()`:
1. Begin DB transaction
2. Delete DB row
3. Attempt Firebase `auth.delete_user()`
4. If Firebase succeeds → commit transaction
5. If Firebase fails → rollback transaction, raise `AppException` with 502

**Why 502:** The failure is in an upstream service (Firebase), not in our logic. 502 Bad Gateway accurately communicates this. The error code will be `FIREBASE_DELETE_FAILED`.

**Alternative considered:** Keep DB-first-then-Firebase with re-insert on failure — more complex, re-insert may also fail, and doesn't leverage the transaction we already have.

### 3. Use asyncpg transaction explicitly

The current code uses `db.connection()` which auto-commits. We need to wrap the delete + Firebase call in an explicit transaction so we can rollback if Firebase fails.

## Risks / Trade-offs

**[Risk] Firebase is slow → DB row locked longer during transaction**
→ Mitigation: Firebase Admin SDK calls typically complete in <500ms. The row is being deleted so lock contention is minimal.

**[Risk] Terraform apply required → needs infra deployment**
→ Mitigation: IAM changes are non-destructive and take effect immediately. Can be applied independently of code changes.

**[Risk] Existing orphaned Firebase account (Yusuf)**
→ Mitigation: Manual cleanup in Firebase Console. UID: `59cBh87nfhgqWe3VVQ3RPKYXo5s2`.
