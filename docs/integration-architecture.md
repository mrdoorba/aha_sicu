# Integration Architecture

**Generated:** 2026-02-16 | **Scan Level:** Exhaustive

## Overview

Store ICU is a multi-part system with clear integration boundaries between frontend, backend, and external services. Communication follows a REST API pattern.

## Integration Diagram

```
┌─────────────────────────────────────────────────────────────────────┐
│                        Google Cloud Platform                        │
│                                                                     │
│  ┌──────────────────┐     REST API      ┌────────────────────────┐ │
│  │  Firebase Hosting │ ──────────────── │     Cloud Run          │ │
│  │  (Frontend SPA)   │  Bearer Token    │   (Backend API)        │ │
│  │                   │ ◄──── JSON ───── │                        │ │
│  │  React 19         │                  │   FastAPI              │ │
│  │  + React Query    │                  │   + asyncpg            │ │
│  └──────────────────┘                  │                        │ │
│                                         │         │              │ │
│  ┌──────────────────┐                  │         │ SQL          │ │
│  │  Firebase Auth    │ ── Token ──────── │         │              │ │
│  │  (Authentication) │  Verification    │         ▼              │ │
│  └──────────────────┘                  │  ┌──────────────┐     │ │
│                                         │  │ Cloud SQL     │     │ │
│  ┌──────────────────┐  Signed URL      │  │ PostgreSQL    │     │ │
│  │  Cloud Storage    │ ◄── Upload ───── │  └──────────────┘     │ │
│  │  (File Uploads)   │ ── Download ──── │                        │ │
│  └──────────────────┘                  │                        │ │
│                                         │                        │ │
│  ┌──────────────────┐  Sheets API      │                        │ │
│  │  Google Sheets    │ ── Read ──────── │                        │ │
│  │  (Brand Data)     │                  │                        │ │
│  └──────────────────┘                  │                        │ │
│                                         │                        │ │
│  ┌──────────────────┐  OIDC Token      │                        │ │
│  │  Cloud Scheduler  │ ── HTTP POST ──── │                        │ │
│  │  (Cron Jobs)      │                  │                        │ │
│  └──────────────────┘                  └────────────────────────┘ │
│                                                                     │
│  ┌──────────────────┐                                              │
│  │  Secret Manager   │ ── Secrets → Cloud Run env vars             │
│  └──────────────────┘                                              │
│                                                                     │
│  ┌──────────────────┐                                              │
│  │  Artifact Registry│ ── Docker Image → Cloud Run                 │
│  └──────────────────┘                                              │
└─────────────────────────────────────────────────────────────────────┘

External:
┌──────────────────┐
│  GitHub Actions   │ ── Workload Identity Federation → GCP
│  (CI/CD)          │ ── Deploy → Cloud Run + Firebase Hosting
└──────────────────┘
```

## Integration Points

### 1. Frontend → Backend (REST API)

| From | To | Protocol | Auth | Description |
|------|----|----------|------|-------------|
| Frontend | Backend | HTTPS REST | Firebase Bearer Token | All API calls |

- **API Base URL**: Configured via `VITE_API_BASE_URL` env var
- **Client Library**: openapi-fetch with auth middleware
- **Data Format**: JSON request/response
- **Error Handling**: Standard HTTP status codes

### 2. Backend → Database (SQL)

| From | To | Protocol | Auth | Description |
|------|----|----------|------|-------------|
| Backend | Cloud SQL PostgreSQL | Unix socket | Cloud SQL socket path | Async queries via asyncpg |

- **Connection Pool**: 1-5 async connections
- **Driver**: asyncpg (async) for runtime, psycopg2 (sync) for migrations
- **Schema Management**: Alembic migrations

### 3. Backend → Google Sheets (API)

| From | To | Protocol | Auth | Description |
|------|----|----------|------|-------------|
| Backend | Google Sheets API | HTTPS | Service Account JSON | Read VP & Meeting data |

- **Sheets Read**: VP sheet (brand data) + 1st Meeting sheet
- **Trigger**: Manual via API or automated via Cloud Scheduler
- **Data Flow**: Sheets → parse rows → upsert to brand_vp_data / brand_meeting_data tables

### 4. Backend → Cloud Storage (GCS)

| From | To | Protocol | Auth | Description |
|------|----|----------|------|-------------|
| Frontend | GCS | HTTPS PUT | Signed URL | Direct file upload |
| Backend | GCS | HTTPS | Service Account | Download for processing |

- **Upload Flow**: Backend generates signed URL → Frontend uploads directly to GCS → Backend downloads and processes
- **Local Dev**: Falls back to local file storage when `GCS_UPLOAD_BUCKET` not configured

### 5. Cloud Scheduler → Backend (OIDC)

| From | To | Protocol | Auth | Description |
|------|----|----------|------|-------------|
| Cloud Scheduler | Backend | HTTPS POST | OIDC Token | Scheduled sync trigger |

- **Endpoint**: `POST /api/v1/sync`
- **Auth**: Google OIDC token with Cloud Run URL as audience
- **Schedule**: Configurable cron expression per environment

### 6. Firebase Auth (Shared)

| From | To | Protocol | Auth | Description |
|------|----|----------|------|-------------|
| Frontend | Firebase Auth | HTTPS | API Key | User login/logout |
| Backend | Firebase Auth | SDK | Admin SA | Token verification |

- **Frontend**: Firebase JS SDK for email/password auth
- **Backend**: Firebase Admin SDK for token verification
- **User Flow**: Frontend login → get ID token → send as Bearer → Backend verifies

### 7. CI/CD → GCP (Deployment)

| From | To | Protocol | Auth | Description |
|------|----|----------|------|-------------|
| GitHub Actions | GCP | HTTPS | Workload Identity Fed. | Keyless deployment |
| GitHub Actions | Artifact Registry | Docker | Workload Identity Fed. | Image push |
| GitHub Actions | Cloud Run | API | Workload Identity Fed. | Service deploy |
| GitHub Actions | Firebase Hosting | CLI | Firebase token | Frontend deploy |

## Data Flow Diagrams

### Evaluation Workflow

```
User (Browser)
  │
  ├── 1. Login ──────────► Firebase Auth ──► Backend /me (auto-create user)
  │
  ├── 2. Browse Brands ──► Backend /brands ──► PostgreSQL (VP + Meeting data)
  │
  ├── 3. Manual Input ───► Backend PUT /evaluations/brands/{id} (auto-save)
  │                                    └──► PostgreSQL (evaluation_inputs)
  │
  ├── 4. Upload Files ───► Backend /upload/signed-url
  │       │                       └──► GCS signed URL
  │       ├── XHR PUT ───► Cloud Storage (file upload)
  │       └── Process ───► Backend /upload/process
  │                              ├──► GCS download
  │                              ├──► Parse & store (brand_uploads)
  │                              └──► Auto-run calculators (calculator_results)
  │
  ├── 5. Run Calcs ──────► Backend /calculators/run-all
  │                              └──► Pure function execution
  │                              └──► Store results (calculator_results)
  │
  ├── 6. Score ──────────► Backend /score
  │                              └──► scoring.py (pure function)
  │                              └──► Return ScoringResponse
  │
  └── 7. Save ───────────► Backend /save
                                 └──► INSERT evaluation snapshot
                                 └──► Return saved evaluation
```

### Sync Workflow

```
Cloud Scheduler (cron)
  │
  └── POST /sync (OIDC auth)
        │
        ├── Advisory lock (prevent concurrent)
        ├── Fetch VP Sheet (Google Sheets API)
        ├── Fetch Meeting Sheet (Google Sheets API)
        ├── Upsert brand_vp_data (PostgreSQL)
        ├── Upsert brand_meeting_data (PostgreSQL)
        ├── Record sync_status
        └── Return sync results
```

## Shared Dependencies

| Dependency | Used By | Purpose |
|------------|---------|---------|
| Firebase Project | Frontend + Backend + Infrastructure | Auth, hosting |
| GCP Project | Backend + Infrastructure | Cloud resources |
| Cloud SQL PostgreSQL | Backend | Data storage (Unix socket connection) |
| Google Sheets | Backend + External users | Brand data source |
| Firebase Admin SDK | Backend | Token verification, account management |
| Cloud SQL Scheduler | Infrastructure | Cost optimization (auto start/stop) |
