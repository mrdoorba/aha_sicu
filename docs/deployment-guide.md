# AHA Store ICU — Deployment Guide

## Overview

This guide covers deploying the AHA Store ICU application to Google Cloud. The stack consists of:

- **Backend**: FastAPI on Cloud Run (asia-southeast1)
- **Frontend**: React SPA on Firebase Hosting
- **Database**: Neon PostgreSQL (ap-southeast-1)
- **Auth**: Firebase Authentication
- **Secrets**: Google Cloud Secret Manager

## Prerequisites

- `gcloud` CLI authenticated with project access
- `firebase-tools` CLI (`npm install -g firebase-tools`)
- `uv` (Python package manager) installed
- Node.js 18+ and npm
- Access to the GCP project

## Environment Details

| Resource | Dev | Prod |
|----------|-----|------|
| GCP Project | `YOUR_GCP_PROJECT_ID` | `YOUR_GCP_PROJECT_ID` |
| Cloud Run Service | `aha-sicu-dev-api` | `aha-sicu-prod-api` |
| Cloud Run Region | `asia-southeast1` | `asia-southeast1` |
| Cloud Run URL | `https://aha-sicu-${ENV}-api-XXXXXXXXX.asia-southeast1.run.app` | Same pattern |
| Firebase Hosting | `aha-sicu-dev.web.app` | `aha-sicu-prod.web.app` |
| Firebase Project | `YOUR_GCP_PROJECT_ID` | `YOUR_GCP_PROJECT_ID` |
| Neon DB Host | `YOUR_NEON_HOST.aws.neon.tech` | Same pattern |
| API SA | `aha-sicu-${ENV}-api-sa@PROJECT_ID.iam.gserviceaccount.com` | Same pattern |
| Sheets SA | `aha-sicu-${ENV}-sheets-sa@PROJECT_ID.iam.gserviceaccount.com` | Same pattern |

---

## Step 1: Secret Injection

Three secrets must be populated in Secret Manager before deploying:

### 1a. Database URL

```bash
# Strip channel_binding=require if present — asyncpg doesn't support it
echo -n "postgresql://neondb_owner:PASSWORD@HOST/neondb?sslmode=require" \
  | gcloud secrets versions add aha_sicu_${ENV}_db_url --data-file=-
```

### 1b. Firebase Admin SDK Key

Generate a key for the Cloud Run API service account:

```bash
# Generate temporary key
gcloud iam service-accounts keys create /tmp/firebase-admin-key.json \
  --iam-account=aha-sicu-${ENV}-api-sa@PROJECT_ID.iam.gserviceaccount.com

# Inject into Secret Manager
gcloud secrets versions add aha_sicu_${ENV}_firebase_admin \
  --data-file=/tmp/firebase-admin-key.json

# Delete temporary key immediately
rm /tmp/firebase-admin-key.json
```

### 1c. Google Sheets SA Key

Generate a key for the Sheets sync service account:

```bash
gcloud iam service-accounts keys create /tmp/gsheets-key.json \
  --iam-account=aha-sicu-${ENV}-sheets-sa@PROJECT_ID.iam.gserviceaccount.com

gcloud secrets versions add aha_sicu_${ENV}_gsheets_credentials \
  --data-file=/tmp/gsheets-key.json

rm /tmp/gsheets-key.json
```

> **Important**: Share the Google Sheets with the Sheets SA email so it has read access.

---

## Step 2: Database Migrations

Run Alembic migrations against the Neon PostgreSQL database:

```bash
cd backend

# Use the same DB URL from Step 1a (with sslmode=require, WITHOUT channel_binding)
DATABASE_URL="postgresql://neondb_owner:PASSWORD@HOST/neondb?sslmode=require" \
  uv run alembic -c app/db/migrations/alembic.ini upgrade head
```

This creates all tables: `users`, `brand_vp_data`, `brand_meeting_data`, `sync_status`, `evaluation_inputs`, `brand_uploads`, `calculator_results`, `evaluations`, `scoring_rules`, `marketing_rules`, `message_templates`.

---

## Step 3: Deploy Backend to Cloud Run

Deploy using source-based deployment (Cloud Build builds the Docker image):

```bash
gcloud run deploy aha-sicu-${ENV}-api \
  --source backend/ \
  --region asia-southeast1 \
  --project PROJECT_ID \
  --update-secrets "DATABASE_URL=aha_sicu_${ENV}_db_url:latest,FIREBASE_CREDENTIALS_JSON=aha_sicu_${ENV}_firebase_admin:latest,GSHEETS_CREDENTIALS_JSON=aha_sicu_${ENV}_gsheets_credentials:latest" \
  --update-env-vars "GSHEETS_VP_SPREADSHEET_ID=VP_SHEET_ID,GSHEETS_MEETING_SPREADSHEET_ID=MEETING_SHEET_ID,GCS_UPLOAD_BUCKET=aha-sicu-${ENV}-uploads"
```

### Secret-to-env-var mapping

| Env Var | Secret | Purpose |
|---------|--------|---------|
| `DATABASE_URL` | `aha_sicu_${ENV}_db_url` | Neon PostgreSQL connection |
| `FIREBASE_CREDENTIALS_JSON` | `aha_sicu_${ENV}_firebase_admin` | Firebase Admin SDK |
| `GSHEETS_CREDENTIALS_JSON` | `aha_sicu_${ENV}_gsheets_credentials` | Google Sheets API |

### Plain env vars

| Env Var | Value | Purpose |
|---------|-------|---------|
| `GSHEETS_VP_SPREADSHEET_ID` | Spreadsheet ID | VP brand data sheet |
| `GSHEETS_MEETING_SPREADSHEET_ID` | Spreadsheet ID | 1st Meeting brand data sheet |
| `GCS_UPLOAD_BUCKET` | `aha-sicu-${ENV}-uploads` | File upload bucket |

---

## Step 4: Deploy Frontend to Firebase Hosting

### 4a. Configure environment

Create `frontend/.env` with Firebase client config:

```bash
VITE_FIREBASE_API_KEY=<firebase-web-api-key>
VITE_FIREBASE_AUTH_DOMAIN=YOUR_GCP_PROJECT_ID.firebaseapp.com
VITE_FIREBASE_PROJECT_ID=YOUR_GCP_PROJECT_ID
VITE_API_BASE_URL=https://YOUR_CLOUD_RUN_URL
```

To get the Firebase Web API key:
```bash
# Via gcloud
curl -s "https://firebase.googleapis.com/v1beta1/projects/PROJECT_ID/webApps" \
  -H "Authorization: Bearer $(gcloud auth print-access-token)" \
  | python3 -c "import sys,json; apps=json.load(sys.stdin).get('apps',[]); print(apps[0]['appId'] if apps else 'No apps')"

# Or check Firebase Console → Project Settings → General → Web API Key
```

### 4b. Build and deploy

```bash
cd frontend
npm ci
npm run build
cd ..
npx firebase-tools deploy --only hosting:aha-sicu-${ENV}
```

---

## Step 5: Post-Deployment

### 5a. Provision user accounts

```bash
cd scripts
# Edit users-config.yaml with team member details
uv run python provision-users.py
```

### 5b. Assign roles

After all users have logged in at least once:

```bash
# Get the DB URL
DB_URL=$(gcloud secrets versions access latest --secret=aha_sicu_${ENV}_db_url)

# Run role assignment
psql "$DB_URL" -f scripts/assign-roles.sql
```

### 5c. Share Google Sheets

Share both spreadsheets with the Sheets SA email address:
- VP Sheet → `aha-sicu-${ENV}-sheets-sa@PROJECT_ID.iam.gserviceaccount.com` (Viewer)
- 1st Meeting Sheet → same SA email (Viewer)

---

## Verification Checklist

- [ ] Backend health: `curl https://CLOUD_RUN_URL/health` → `{"status":"healthy"}`
- [ ] Swagger UI: `https://CLOUD_RUN_URL/docs` → API docs load
- [ ] Frontend: `https://aha-sicu-${ENV}.web.app` → Login page renders
- [ ] Login: Sign in with a provisioned account → Dashboard loads
- [ ] Sync: Trigger brand sync → Brands populate from Google Sheets
- [ ] Roles: Admin/leader users see appropriate UI sections

---

## Troubleshooting

### Backend won't start
- Check Cloud Run logs: `gcloud run services logs read aha-sicu-${ENV}-api --region=asia-southeast1 --limit=50`
- Verify secrets have real values (not placeholders): `gcloud secrets versions access latest --secret=SECRET_NAME`

### Database connection fails
- Ensure `channel_binding=require` is NOT in the URL (asyncpg incompatible)
- Verify `sslmode=require` IS present
- Check Neon dashboard for connection limits

### Firebase auth fails
- Verify the SA key in `aha_sicu_${ENV}_firebase_admin` is for the correct SA
- Ensure Firebase Auth is enabled in the Firebase Console
- Check that provisioned users exist: Firebase Console → Authentication → Users

### Google Sheets sync fails
- Ensure sheets are shared with the Sheets SA email
- Check the spreadsheet IDs are correct in env vars
- Verify the SA key in `aha_sicu_${ENV}_gsheets_credentials` is valid

### Frontend can't reach backend
- Check `VITE_API_BASE_URL` in frontend `.env` matches the Cloud Run URL
- Verify Cloud Run allows unauthenticated access (IAM: allUsers → roles/run.invoker)
- Check CORS if browser console shows errors
