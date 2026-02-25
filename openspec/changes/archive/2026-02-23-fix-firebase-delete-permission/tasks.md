## 1. Infrastructure — IAM Permission

- [x] 1.1 Add `roles/firebaseauth.admin` IAM binding for Cloud Run SA in `infrastructure/terraform/iam.tf`

## 2. Backend — Atomic Deletion Flow

- [x] 2.1 Refactor `delete_account()` in `backend/app/modules/accounts/service.py` to use explicit transaction: delete DB row, attempt Firebase delete, rollback on failure, raise `AppException` with code `FIREBASE_DELETE_FAILED` and status 502
- [x] 2.2 Update/add tests in `backend/tests/` to cover Firebase failure → DB rollback scenario and verify no orphaned state

## 3. Deploy & Cleanup

- [ ] 3.1 Run `terraform apply` to grant the IAM role (requires user action)
- [ ] 3.2 Manually delete orphaned Firebase Auth account `59cBh87nfhgqWe3VVQ3RPKYXo5s2` from Firebase Console (requires user action)
