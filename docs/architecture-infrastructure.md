# Architecture - Infrastructure

**Generated:** 2026-02-16 | **Scan Level:** Exhaustive | **Part:** infrastructure | **Type:** infra

## Overview

Infrastructure is managed as code using Terraform on Google Cloud Platform (GCP). The system runs in the `asia-southeast1` (Singapore) region with two environments: dev and prod.

## Technology Stack

| Category | Technology | Purpose |
|----------|-----------|---------|
| IaC | Terraform >= 1.0 | Infrastructure provisioning |
| Provider | hashicorp/google ~7.0 | GCP resource management |
| Cloud | Google Cloud Platform | Cloud provider |
| CI/CD | GitHub Actions | Deployment automation |
| Auth | Workload Identity Federation | Keyless CI/CD auth |

## Cloud Resources

### Compute & Hosting

| Resource | Service | Purpose |
|----------|---------|---------|
| Backend API | Cloud Run | Serverless container runtime |
| Frontend SPA | Firebase Hosting | Static site hosting with SPA rewrites |
| Docker Images | Artifact Registry | Container image storage |

### Data & Storage

| Resource | Service | Purpose |
|----------|---------|---------|
| Database | Neon PostgreSQL | Serverless PostgreSQL (external) |
| File Storage | Cloud Storage | Uploaded Shopee report files |
| Secrets | Secret Manager | Database URLs, API keys, credentials |

### Integration & Scheduling

| Resource | Service | Purpose |
|----------|---------|---------|
| Scheduler | Cloud Scheduler | Automated sync jobs |
| Sheets API | Google Sheets API | Brand data synchronization |

### Identity & Access

| Resource | Service | Purpose |
|----------|---------|---------|
| User Auth | Firebase Authentication | End-user login |
| Service Accounts | IAM | Service-to-service auth |
| CI/CD Auth | Workload Identity Federation | GitHub Actions → GCP |

## Environment Configuration

### Dev Environment

```hcl
project_id          = "YOUR_GCP_PROJECT_ID"
region              = "asia-southeast1"
environment         = "dev"
cloud_run_min_instances = 0      # Scale to zero
cloud_run_max_instances = 2
cloud_run_memory        = "512Mi"
cloud_run_cpu           = "1"
```

### Prod Environment

```hcl
project_id          = "YOUR_GCP_PROJECT_ID"
region              = "asia-southeast1"
environment         = "prod"
cloud_run_min_instances = 1      # Always-on
cloud_run_max_instances = 4
cloud_run_memory        = "512Mi"
cloud_run_cpu           = "1"
```

## Terraform Resources

### main.tf — Provider & API Enablement
- Google and Google-Beta providers
- Enables 7 GCP APIs: Cloud Run, Artifact Registry, Secret Manager, IAM, Firebase, Firebase Hosting, Cloud Scheduler, Google Sheets

### cloud_run.tf — Backend Service
- Cloud Run service with Docker image from Artifact Registry
- Environment variables injected from Secret Manager
- Configurable scaling (min/max instances, memory, CPU)
- IAM: Allow unauthenticated (public API with Firebase Auth at app level)

### iam.tf — Service Accounts & Permissions
- Cloud Run service account: `aha-sicu-{env}-run-sa`
- GitHub Actions service account: Workload Identity Federation
- Roles: Secret Manager accessor, Cloud Storage admin, etc.

### artifact_registry.tf — Docker Registry
- Repository: `aha-sicu-{env}`
- Format: Docker
- Region: asia-southeast1

### firebase.tf — Frontend Hosting
- Firebase Hosting sites: `aha-sicu-dev`, `aha-sicu-prod`
- SPA rewrite: all routes → /index.html
- Source: `frontend/dist/`

### secrets.tf — Secret Manager
Managed secrets:
- `aha_sicu_{env}_db_url` — Neon PostgreSQL connection string
- `aha_sicu_{env}_firebase_credentials` — Firebase Admin SA JSON
- `aha_sicu_{env}_gsheets_credentials` — Google Sheets SA JSON

### storage.tf — Cloud Storage
- Bucket: `aha-sicu-{env}-uploads`
- Purpose: Uploaded Shopee report files
- Lifecycle: Configurable retention

### scheduler.tf — Cloud Scheduler
- Scheduled sync job: triggers `POST /api/v1/sync` via OIDC-authenticated HTTP
- Cron expression: configurable per environment

## CI/CD Pipelines

### ci.yml — Pull Request Validation

**Trigger:** Pull requests to `develop` or `main`

```
Backend Job:
  1. Setup Python 3.14 + UV
  2. Install dependencies
  3. Run Ruff lint
  4. Run Pytest

Frontend Job:
  1. Setup Node.js
  2. npm install
  3. ESLint
  4. TypeScript check (tsc -b --noEmit)
  5. Vitest run
  6. Vite build
```

### deploy-backend.yml — Backend Deployment

**Trigger:** Push to `develop` or `main`

```
1. Authenticate to GCP (Workload Identity Federation)
2. Configure Docker for Artifact Registry
3. Build Docker image
4. Push to Artifact Registry
5. Deploy to Cloud Run
   - develop → dev environment (auto)
   - main → prod environment (manual approval)
```

### deploy-frontend.yml — Frontend Deployment

**Trigger:** Push to `develop` or `main`

```
1. Setup Node.js
2. npm install
3. Build (tsc + vite build)
4. Deploy to Firebase Hosting
   - develop → aha-sicu-dev target (auto)
   - main → aha-sicu-prod target (manual approval)
```

## Firebase Configuration

### firebase.json
Two hosting targets with SPA rewrites:
- `aha-sicu-dev` → `frontend/dist/`
- `aha-sicu-prod` → `frontend/dist/`

### .firebaserc
```json
{
  "projects": { "dev": "YOUR_GCP_PROJECT_ID", "prod": "YOUR_GCP_PROJECT_ID" },
  "targets": {
    "YOUR_GCP_PROJECT_ID": {
      "hosting": {
        "aha-sicu-dev": ["aha-sicu-dev"],
        "aha-sicu-prod": ["aha-sicu-prod"]
      }
    }
  }
}
```

## Utility Scripts

### provision-users.py
Creates Firebase Auth accounts from YAML config:
```bash
python scripts/provision-users.py --config scripts/users-config.yaml
```
Outputs UID mapping for role assignment.

### assign-roles.sql
Updates user roles in PostgreSQL:
```bash
psql $DATABASE_URL -f scripts/assign-roles.sql
```
Roles: admin, leader, member.

### Provisioning Flow
1. Run `provision-users.py` → Create Firebase accounts
2. Have users log in once → Auto-creates DB records
3. Run `assign-roles.sql` → Assign admin/leader roles

## Smoke Tests

Playwright-based API-only tests (no browser):
- Backend health check
- Auth enforcement verification
- Frontend SPA accessibility
- Database connectivity
- Signed URL generation
- SSE endpoint connectivity

```bash
cd smoke-tests && npx playwright test
```

Environment variables: `SMOKE_BACKEND_URL`, `SMOKE_FRONTEND_URL`, `SMOKE_AUTH_TOKEN`
