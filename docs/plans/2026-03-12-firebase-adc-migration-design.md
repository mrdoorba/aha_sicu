# Firebase ADC Migration — Fix Admin User Creation

## Problem

Admin users cannot create accounts or reset passwords on Cloud Run (both dev and prod).

### Root Cause

The Firebase Admin SDK is initialized with a stale service account key from Secret Manager:

- **Secret contains:** `aha-sicu-dev-api-sa@fbi-dev-484410.iam.gserviceaccount.com` (old, manually created — lacks `firebaseauth.admin`)
- **Terraform-managed Cloud Run SA:** `aha-coms-sicu-dev-api-sa@fbi-dev-484410.iam.gserviceaccount.com` (has `firebaseauth.admin`)

Token verification (`verify_id_token`) works because it only validates JWT signatures against Google's public keys — no IAM permissions needed. But write operations (`create_user`, `update_user`) call the Identity Toolkit API, which requires `firebaseauth.admin` on the calling service account.

## Solution

Switch from explicit credentials to Application Default Credentials (ADC) on Cloud Run. ADC automatically uses the Cloud Run runtime service account, which already has the correct IAM role.

## Changes

### 1. Backend — `app/core/security.py`

Add ADC fallback to `init_firebase()`:

```
firebase_credentials_json → firebase_credentials_path → ADC (default credentials)
```

Local dev continues using `FIREBASE_CREDENTIALS_PATH`. Cloud Run uses ADC.

### 2. Terraform — `modules/environment/main.tf`

- Remove `FIREBASE_CREDENTIALS_JSON` env var from Cloud Run service definition
- Remove `google_secret_manager_secret.firebase_admin` resource
- Remove `google_secret_manager_secret_iam_member.api_sa_firebase` resource

### 3. Manual Cleanup (requires IAM admin)

- Delete old SA: `aha-sicu-dev-api-sa@fbi-dev-484410.iam.gserviceaccount.com`
- Delete Secret Manager secrets: `aha_coms_sicu_dev_firebase_admin`, `aha_coms_sicu_prod_firebase_admin`

## Verification

After deployment:
- Create a new user from the Accounts page
- Reset a user's password
- Confirm login still works
