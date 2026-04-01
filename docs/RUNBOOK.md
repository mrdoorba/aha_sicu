# Runbook

## Environments

| Environment | Frontend | Backend | Database |
|-------------|----------|---------|----------|
| **Production** | [aha-coms-sicu-prod.web.app](https://aha-coms-sicu-prod.web.app) | Cloud Run (asia-southeast2) | Cloud SQL PostgreSQL 18 |
| **Staging** | [aha-coms-sicu-dev.web.app](https://aha-coms-sicu-dev.web.app) | Cloud Run (asia-southeast2) | Cloud SQL PostgreSQL 18 |
| **Local** | `localhost:5173` | `localhost:8000` | Docker PostgreSQL 18 |

## Deployment

### Automatic (CI/CD)

| Trigger | Target | Approval |
|---------|--------|----------|
| Push to `develop` | Staging (dev) | Automatic |
| Push to `main` | Production | Manual approval |

Pipelines: `.github/workflows/deploy.yml` > `_deploy-backend.yml` / `_deploy-frontend.yml`

### Manual Backend Deploy

```bash
# Build and push container
gcloud builds submit --tag ${ARTIFACT_REGISTRY_URL}/backend:latest ./backend

# Deploy to Cloud Run
gcloud run deploy ${CLOUD_RUN_SERVICE} \
  --image ${ARTIFACT_REGISTRY_URL}/backend:latest \
  --region asia-southeast2
```

### Manual Frontend Deploy

```bash
cd frontend
npm run build
firebase deploy --only hosting:${FIREBASE_HOSTING_SITE}
```

## Health Checks

### Backend

```bash
# Health endpoint
curl https://<backend-url>/health

# OpenAPI docs (verify app is running)
curl -s https://<backend-url>/docs | head -1
```

### Frontend

```bash
# Check SPA loads
curl -s https://<frontend-url>/ | grep -q "Store ICU"
```

### Smoke Tests (post-deploy)

```bash
cd smoke-tests
SMOKE_BACKEND_URL="https://..." \
SMOKE_FRONTEND_URL="https://..." \
npx playwright test
```

## Database

### Run Migrations

```bash
# Local
cd backend && uv run alembic upgrade head

# Cloud Run (connect via Cloud SQL Proxy)
cloud-sql-proxy ${CLOUD_SQL_INSTANCE_CONNECTION} &
DATABASE_URL="postgresql://${DB_USER}:${DB_PASSWORD}@localhost:5432/${DB_NAME}" \
  uv run alembic upgrade head
```

### Rollback Migration

```bash
# Rollback one step
uv run alembic downgrade -1

# Rollback to specific revision
uv run alembic downgrade <revision_id>
```

### Check Migration Status

```bash
uv run alembic current   # Current revision
uv run alembic history   # Migration history
```

## Common Issues

### Backend won't start

1. Check `DATABASE_URL` is correct and database is reachable
2. Check Firebase credentials path exists: `FIREBASE_CREDENTIALS_PATH`
3. Run pending migrations: `uv run alembic upgrade head`
4. Check logs: `docker compose logs backend` or Cloud Run logs

### Frontend can't reach API

1. Verify `VITE_API_BASE_URL` points to the correct backend
2. Check CORS settings in backend if cross-origin
3. Check browser console for network errors

### Docker Compose issues

```bash
# Reset everything
docker compose down -v  # Remove volumes (destroys DB data)
docker compose up --build

# Rebuild single service
docker compose build backend
docker compose up backend
```

### Email not sending

1. Check `EMAIL_ENABLED=true`
2. Verify `SENDGRID_API_KEY` is set and valid
3. Verify `EMAIL_FROM_EMAIL` is a verified SendGrid sender
4. If Event Webhook handling matters, verify `SENDGRID_WEBHOOK_SECRET`
5. Local dev: if email is disabled, no outbound mail will be attempted

## Rollback Procedures

### Backend

```bash
# List recent revisions
gcloud run revisions list --service ${CLOUD_RUN_SERVICE} --region asia-southeast2

# Route traffic to previous revision
gcloud run services update-traffic ${CLOUD_RUN_SERVICE} \
  --region asia-southeast2 \
  --to-revisions <previous-revision>=100
```

### Frontend

```bash
# Firebase keeps recent deploys — roll back via console
# Or redeploy from a known-good commit:
git checkout <good-commit>
cd frontend && npm run build
firebase deploy --only hosting:${FIREBASE_HOSTING_SITE}
```

## Alerting & Escalation

| Signal | Where to look |
|--------|---------------|
| Backend errors | GCP Cloud Run > Logs |
| Deploy failures | GitHub Actions > workflow runs |
| Database issues | GCP Cloud SQL > Monitoring |
| Auth issues | Firebase Console > Authentication |
