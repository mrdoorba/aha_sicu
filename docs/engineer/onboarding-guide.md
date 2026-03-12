# Onboarding Guide -- AHA SICU

This guide covers user provisioning, the daily BD workflow, role permissions, and a manual verification checklist for end-to-end validation.

---

## 1. User Provisioning Workflow

### 1.1 Prepare the Users Config

Copy the example config and fill in real credentials:

```bash
cp scripts/users-config.example.yaml scripts/users-config.yaml
```

Edit `scripts/users-config.yaml` with real user information:

```yaml
users:
  - email: "admin@yourcompany.com"
    password: "strong-initial-password"
    display_name: "System Admin"
    role: admin

  - email: "leader@yourcompany.com"
    password: "strong-initial-password"
    display_name: "BD Team Leader"
    role: leader

  - email: "member1@yourcompany.com"
    password: "strong-initial-password"
    display_name: "BD Member 1"
    role: member
```

**Security rules:**
- NEVER commit `users-config.yaml` (it is in `.gitignore`).
- Use strong initial passwords (minimum 6 characters, Firebase requirement).
- Distribute credentials securely -- not via email or chat.
- Users should change their password on first login.

### 1.2 Run the Provisioning Script

Prerequisites:
- `pip install firebase-admin pyyaml` (or use the backend virtualenv which already has `firebase-admin`).
- Firebase Admin credentials (service account JSON) for the target project.

Set credentials via one of these methods (checked in order):
1. `FIREBASE_CREDENTIALS_PATH` env var -- path to service account JSON file.
2. `--credentials` CLI argument -- path to service account JSON file.
3. Falls back to Application Default Credentials (ADC) if neither is set.

Run:

```bash
python scripts/provision-users.py --config scripts/users-config.yaml
```

The script creates Firebase Auth accounts and outputs a UID mapping table:

```
UID Mapping (for assign-roles.sql)
============================================================
  admin@yourcompany.com                    role=admin    uid=J7S2Y4A8W9XcyvKxR8OCnCNL8Ry2
  leader@yourcompany.com                   role=leader   uid=aPoacvrKhlhZHVgJCPKhCHdmc7Q2
  member1@yourcompany.com                  role=member   uid=59cBh87nfhgqWe3VVQ3RPKYXo5s2
```

If a user already exists in Firebase Auth, the script skips creation and prints the existing UID.

### 1.3 First Login (Auto-Create User Record)

Have ALL users log in once at the app URL (e.g., `https://aha-coms-sicu-prod.web.app`).

The backend's `get_current_user` dependency auto-creates a user record in the database with `role='member'` on first login. Users **must** log in before role assignment will work, because the `UPDATE` in the next step targets rows that only exist after this auto-creation.

### 1.4 Assign Roles

Update `scripts/assign-roles.sql` with the real UIDs from the provisioning output (step 1.2). Then run it against the production database.

Retrieve the database URL from Secret Manager:

```bash
export DATABASE_URL=$(gcloud secrets versions access latest --secret=aha_coms_sicu_prod_db_password)
```

Run the role assignment:

```bash
psql $DATABASE_URL -f scripts/assign-roles.sql
```

The script promotes users from the default `member` role to `admin` or `leader` as configured, then prints a verification query showing all users and their assigned roles.

---

## 2. Daily BD Workflow

The standard daily workflow for a BD team member:

### 2.1 Sync Brands

- Navigate to the Brands page (`/brands`).
- Trigger a manual sync (click the sync button) or wait for the scheduled sync.
- Verify sync completes via real-time SSE status updates.

### 2.2 Select Brand and Start Evaluation

- Select a brand from the synced brand list.
- Click to start a new evaluation for the selected brand.

### 2.3 Upload Shopee Export Files

Upload the following 4 file types:

| # | File Type | Format |
|---|-----------|--------|
| 1 | CPC Ad Report | CSV |
| 2 | Keyword Report | CSV |
| 3 | Order Export | XLSX |
| 4 | Mass Update | XLSX |

Files are uploaded via GCS signed URLs. Verify each file shows a success indicator in the evaluation UI.

### 2.4 Calculator Execution

After file uploads, three calculators run automatically:

1. **Ads Keyword Calculator** -- processes CPC ad and keyword report data.
2. **Discount Check Calculator** -- analyzes discount patterns from the mass update file.
3. **Top SKU Calculator** -- identifies top-performing SKUs from order data.

Verify each calculator completes and its results appear in the UI.

### 2.5 Manual Data Entry

Enter manual data across the 8 evaluation sections. Note the percentage convention: a value like `0.5` means 0.5% (not 50%).

### 2.6 Generate Score and Review Verdict

- Navigate to the final scoring step.
- The system generates a score and verdict based on calculator results, manual data, and configured scoring rules.
- Two scoring templates are available: **Fashion** and **Non-Fashion**.
- Review the score and verdict for correctness.

### 2.7 Save Evaluation

- Click save. The evaluation is persisted to the database.
- The saved evaluation appears in the History page (`/history`).

### 2.8 Send Email Report

- After saving, trigger the email report for the evaluation.
- The report is sent to configured recipients.

---

## 3. Role Permissions

| Capability | member | leader | admin |
|---|:---:|:---:|:---:|
| List brands | Y | Y | Y |
| Run evaluations | Y | Y | Y |
| Upload files | Y | Y | Y |
| View own evaluations | Y | Y | Y |
| View all evaluations | -- | Y | Y |
| Manage scoring rules | -- | Y | Y |
| Delete evaluations | -- | Y | Y |
| Full account management | -- | -- | Y |

**Role definitions:**
- **member** -- Standard BD team member. Can list brands, run evaluations, and upload files.
- **leader** -- BD team leader. All member permissions plus managing scoring rules, viewing all evaluations, and deleting evaluations.
- **admin** -- System owner. Full access including account management.

---

## 4. Manual Verification Checklist

A 10-step end-to-end verification cycle. Run this after each production deployment, before onboarding new users.

### Pre-requisites

| Item | Details |
|------|---------|
| Production Backend URL | Get via: `gcloud run services describe aha-coms-sicu-prod-api --region=asia-southeast2 --format="value(status.url)"` |
| Production Frontend URL | `https://aha-coms-sicu-prod.web.app` |
| Test user credentials | A valid Firebase Auth email/password account |
| Sample CPC Ad Report | CSV file with CPC ad data for a test brand |
| Sample Keyword Report | CSV file with keyword report data |
| Sample Order Export | XLSX file with order export data |
| Sample Mass Update | XLSX file with mass update data |

### Step 1: Login Flow

- [ ] Navigate to the production frontend URL.
- [ ] Verify the login page loads correctly.
- [ ] Enter test user email and password, click login.
- [ ] Verify redirect to the main dashboard/brands page.
- [ ] Verify user session is active (no auth errors).

### Step 2: Brand Sync Verification

- [ ] Navigate to the Brands page (`/brands`).
- [ ] Verify the brand list loads with data from the database.
- [ ] Trigger a manual sync (click sync button).
- [ ] Verify SSE updates appear in real-time (toast/status changes).
- [ ] Verify sync completes successfully (status shows last sync time).

### Step 3: Brand Selection and Evaluation Start

- [ ] Select a test brand from the brand list.
- [ ] Click to start a new evaluation for the selected brand.
- [ ] Verify the evaluation page loads with the brand information.
- [ ] Verify evaluation is in the correct initial state.

### Step 4: File Upload (4 File Types)

- [ ] Upload CPC Ad Report CSV -- verify success indicator.
- [ ] Upload Keyword Report CSV -- verify success indicator.
- [ ] Upload Order Export XLSX -- verify success indicator.
- [ ] Upload Mass Update XLSX -- verify success indicator.
- [ ] Verify all 4 files show as uploaded in the evaluation UI.

### Step 5: Calculator Execution (3 Calculators)

- [ ] Ads Keyword Calculator -- verify execution completes, results appear.
- [ ] Discount Check Calculator -- verify execution completes, results appear.
- [ ] Top SKU Calculator -- verify execution completes, results appear.
- [ ] Verify calculator results display correct data/scores.

### Step 6: Manual Data Entry

- [ ] Navigate to the manual data input section.
- [ ] Enter values in 3-5 fields across different categories.
- [ ] Verify values are saved/persisted correctly.
- [ ] Verify percentage convention: values like `0.5` mean 0.5% (not 50%).

### Step 7: Final Scoring

- [ ] Navigate to the final scoring step.
- [ ] Verify Fashion template scoring produces a score and verdict.
- [ ] Verify Non-Fashion template scoring produces a score and verdict.
- [ ] Verify the scoring uses configured rules (not hardcoded defaults).

### Step 8: Save Evaluation

- [ ] Click save evaluation.
- [ ] Verify the evaluation is saved successfully (success message/redirect).
- [ ] Note the evaluation ID for verification.

### Step 9: Verify in History

- [ ] Navigate to the History page (`/history`).
- [ ] Verify the newly saved evaluation appears in the list.
- [ ] Verify the evaluation shows correct brand name, date, score.
- [ ] Click into the evaluation detail view.
- [ ] Verify all evaluation data is correctly displayed.

### Step 10: Email Report

- [ ] Trigger the email report for the saved evaluation.
- [ ] Verify the email is sent successfully.
- [ ] Verify the email content is accurate (score, verdict, brand name).

### Summary Table

| Step | Description | Pass/Fail |
|------|-------------|-----------|
| 1 | Login Flow | |
| 2 | Brand Sync Verification | |
| 3 | Brand Selection & Evaluation Start | |
| 4 | File Upload (4 file types) | |
| 5 | Calculator Execution (3 calculators) | |
| 6 | Manual Data Entry | |
| 7 | Final Scoring | |
| 8 | Save Evaluation | |
| 9 | Verify in History | |
| 10 | Email Report | |

**Tested by:** ____________________
**Date:** ____________________
**Environment:** ____________________
