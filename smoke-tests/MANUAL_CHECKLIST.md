# Manual Smoke Test Checklist — AHA SICU Production

**Purpose:** Verify the full evaluation workflow works end-to-end in production before user onboarding (Story 6.4).

**When to run:** After each production deployment, before onboarding new users.

---

## Pre-requisites

| Item | Details |
|------|---------|
| **Production Backend URL** | `https://aha-coms-sicu-prod-api-<hash>.asia-southeast2.run.app` (get via `gcloud run services describe aha-coms-sicu-prod-api --region=asia-southeast2 --format="value(status.url)"`) |
| **Production Frontend URL** | `https://aha-coms-sicu-prod.web.app` |
| **Test user credentials** | A valid Firebase Auth email/password account with access to the system |
| **Sample CPC Ad Report CSV** | CSV file with CPC ad data for a test brand |
| **Sample Keyword Report CSV** | CSV file with keyword report data |
| **Sample Order Export XLSX** | XLSX file with order export data |
| **Sample Mass Update XLSX** | XLSX file with mass update data |

---

## Checklist

### Step 1: Login Flow (Firebase Auth)

- [ ] Navigate to the production frontend URL
- [ ] Verify the login page loads correctly
- [ ] Enter test user email and password
- [ ] Click login / submit
- [ ] Verify redirect to the main dashboard/brands page
- [ ] Verify user session is active (no auth errors)

**Pass/Fail:** ____

---

### Step 2: Brand Sync Verification

- [ ] Navigate to the Brands page (`/brands`)
- [ ] Verify the brand list loads with data from the database
- [ ] Trigger a manual sync (click sync button)
- [ ] Verify SSE updates appear in real-time (toast/status changes)
- [ ] Verify sync completes successfully (status shows last sync time)
- [ ] Confirm brand list reflects synced data

**Pass/Fail:** ____

---

### Step 3: Brand Selection and Evaluation Start

- [ ] Select a test brand from the brand list
- [ ] Click to start a new evaluation for the selected brand
- [ ] Verify the evaluation page loads with the brand information
- [ ] Verify evaluation is in the correct initial state

**Pass/Fail:** ____

---

### Step 4: File Upload Flow

Upload each of the 4 file types and verify successful upload via GCS signed URL:

- [ ] **CPC Ad Report CSV** — Select file, upload, verify success indicator
- [ ] **Keyword Report CSV** — Select file, upload, verify success indicator
- [ ] **Order Export XLSX** — Select file, upload, verify success indicator
- [ ] **Mass Update XLSX** — Select file, upload, verify success indicator
- [ ] Verify all 4 files show as uploaded in the evaluation UI

**Pass/Fail:** ____

---

### Step 5: Calculator Execution Verification

After file uploads, verify calculators execute (auto-execute or manual trigger):

- [ ] **Ads Keyword Calculator** — Verify execution completes, results appear
- [ ] **Discount Check Calculator** — Verify execution completes, results appear
- [ ] **Top SKU Calculator** — Verify execution completes, results appear
- [ ] Verify calculator results display correct data/scores

**Pass/Fail:** ____

---

### Step 6: Manual Data Entry

Spot-check 3-5 manual data fields across different categories:

- [ ] Navigate to the manual data input section
- [ ] Enter value in field 1: _________________ (category: _________)
- [ ] Enter value in field 2: _________________ (category: _________)
- [ ] Enter value in field 3: _________________ (category: _________)
- [ ] Verify values are saved/persisted correctly
- [ ] Verify percentage convention: values like 0.5 mean 0.5% (not 50%)

**Pass/Fail:** ____

---

### Step 7: Final Scoring

- [ ] Navigate to the final scoring step
- [ ] Verify **Fashion template** scoring produces a score and verdict
- [ ] Verify **Non-Fashion template** scoring produces a score and verdict
- [ ] Verify the score and verdict are reasonable given the input data
- [ ] Verify the scoring uses configured rules (not hardcoded defaults)

**Pass/Fail:** ____

---

### Step 8: Save Evaluation

- [ ] Click save evaluation
- [ ] Verify the evaluation is saved successfully (success message/redirect)
- [ ] Note the evaluation ID for verification: _________

**Pass/Fail:** ____

---

### Step 9: Verify in History Page

- [ ] Navigate to the History page (`/history`)
- [ ] Verify the newly saved evaluation appears in the list
- [ ] Verify the evaluation shows correct brand name, date, score
- [ ] Click into the evaluation detail view
- [ ] Verify all evaluation data is correctly displayed

**Pass/Fail:** ____

---

### Step 10: SSE Notification Verification

- [ ] Open a second browser tab/session with the same user (or a different user)
- [ ] In the first tab, save a new evaluation (or trigger a sync)
- [ ] In the second tab, verify a real-time toast notification appears
- [ ] Verify the notification content is accurate

**Pass/Fail:** ____

---

## Summary

| Step | Description | Pass/Fail |
|------|-------------|-----------|
| 1 | Login Flow | |
| 2 | Brand Sync Verification | |
| 3 | Brand Selection & Evaluation Start | |
| 4 | File Upload Flow | |
| 5 | Calculator Execution | |
| 6 | Manual Data Entry | |
| 7 | Final Scoring | |
| 8 | Save Evaluation | |
| 9 | Verify in History | |
| 10 | SSE Notification | |

**Overall Result:** ____

**Tested by:** ____________________
**Date:** ____________________
**Environment:** ____________________
**Notes:**

---
