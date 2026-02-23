#!/usr/bin/env bash
set -euo pipefail

# Store ICU — Cloud SQL Migration Script
# Interactive, phase-based, idempotent.
# Migrates from Neon PostgreSQL to Cloud SQL in Jakarta (asia-southeast2).

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# ─── Colors & logging ────────────────────────────────────────────────────────

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
BOLD='\033[1m'
NC='\033[0m'

info()   { echo -e "${CYAN}[INFO]${NC} $1"; }
ok()     { echo -e "${GREEN}[OK]${NC} $1"; }
warn()   { echo -e "${YELLOW}[WARN]${NC} $1"; }
error()  { echo -e "${RED}[ERROR]${NC} $1"; }
header() { echo -e "\n${BOLD}═══ $1 ═══${NC}\n"; }

# ─── Constants ────────────────────────────────────────────────────────────────

PROJECT_ID="fbi-dev-484410"
REGION="asia-southeast2"
INSTANCE_NAME="aha-sicu-db"
INSTANCE_CONNECTION="${PROJECT_ID}:${REGION}:${INSTANCE_NAME}"
DB_USER="aha_sicu"
PROXY_PORT=15432
GITHUB_REPO="HandersThe/aha_sicu"

# Add Homebrew libpq to PATH if pg_dump/psql not already available (keg-only)
if ! command -v pg_dump &>/dev/null && [ -d "/opt/homebrew/opt/libpq/bin" ]; then
  export PATH="/opt/homebrew/opt/libpq/bin:$PATH"
fi

# ─── Usage ────────────────────────────────────────────────────────────────────

usage() {
  cat <<EOF
Usage: $(basename "$0") [OPTIONS]

Store ICU — Cloud SQL Migration Script (Neon → Cloud SQL)

Phases:
  1  Pre-flight checks (tools, auth, env file)
  2  Terraform init → plan → apply
  3  Set database password + store in Secret Manager
  4  Set GitHub Actions environment variables
  5  Data migration (pg_dump from Neon → pg_restore to Cloud SQL)
  6  Verification (connectivity, tables, row counts, Alembic)

Options:
  --phase N    Run only phase N (1-6)
  -h, --help   Show this help message

Without --phase, runs all phases sequentially with confirmations.
EOF
}

# ─── Parse arguments ─────────────────────────────────────────────────────────

PHASE=""
while [[ $# -gt 0 ]]; do
  case $1 in
    --phase)
      if [[ -z "${2:-}" ]]; then
        error "--phase requires a value (1-6)"
        exit 1
      fi
      PHASE="$2"; shift 2
      ;;
    -h|--help) usage; exit 0 ;;
    *) error "Unknown argument: $1"; usage; exit 1 ;;
  esac
done

# ─── Banner ───────────────────────────────────────────────────────────────────

echo ""
echo "======================================"
echo "  Store ICU — Cloud SQL Migration"
echo "======================================"
echo ""

# ─── Environment selection ────────────────────────────────────────────────────

info "Available environments:"
echo "  1) dev  (environments/dev.tfvars)"
echo "  2) prod (environments/prod.tfvars)"
echo ""
read -rp "Select environment [1/2]: " ENV_CHOICE

case "$ENV_CHOICE" in
  1|dev)  ENV="dev" ;;
  2|prod) ENV="prod" ;;
  *)      error "Invalid choice. Use 1 (dev) or 2 (prod)."; exit 1 ;;
esac

TFVARS="environments/${ENV}.tfvars"
if [ ! -f "$TFVARS" ]; then
  error "File not found: $TFVARS"
  exit 1
fi

# Derive environment-specific values
DB_NAME="aha_sicu_${ENV}"
SECRET_NAME="aha_sicu_${ENV}_db_password"
if [ "$ENV" = "prod" ]; then
  GITHUB_ENV="production"
else
  GITHUB_ENV="dev"
fi
REGISTRY_URL="${REGION}-docker.pkg.dev/${PROJECT_ID}/aha-sicu-${ENV}-registry"

ok "Environment: $ENV"
ok "Database: $DB_NAME"
ok "GitHub environment: $GITHUB_ENV"

# Set gcloud project
gcloud config set project "$PROJECT_ID" --quiet 2>/dev/null
ok "gcloud project set to $PROJECT_ID"

# ─── Helpers ──────────────────────────────────────────────────────────────────

confirm() {
  local prompt="${1:-Continue?}"
  read -rp "$prompt [y/N]: " answer
  [[ "$answer" =~ ^[Yy]$ ]]
}

PROXY_PID=""
cleanup_proxy() {
  if [ -n "$PROXY_PID" ] && kill -0 "$PROXY_PID" 2>/dev/null; then
    info "Stopping Cloud SQL Auth Proxy (PID $PROXY_PID)..."
    kill "$PROXY_PID" 2>/dev/null || true
    wait "$PROXY_PID" 2>/dev/null || true
    ok "Auth Proxy stopped"
  fi
}
trap cleanup_proxy EXIT

start_proxy() {
  local proxy_dir="/tmp/cloudsql-migration"
  local proxy_bin="${proxy_dir}/cloud-sql-proxy"

  if [ ! -f "$proxy_bin" ]; then
    error "Cloud SQL Auth Proxy not found at $proxy_bin"
    error "Run phase 5 first to download it, or download manually."
    exit 1
  fi

  info "Starting Cloud SQL Auth Proxy on port ${PROXY_PORT}..."
  "$proxy_bin" "$INSTANCE_CONNECTION" --port "$PROXY_PORT" &
  PROXY_PID=$!
  sleep 3

  if ! kill -0 "$PROXY_PID" 2>/dev/null; then
    error "Auth Proxy failed to start"
    exit 1
  fi
  ok "Auth Proxy running (PID $PROXY_PID)"
}

# ═══════════════════════════════════════════════════════════════════════════════
# Phase 1: Pre-flight checks
# ═══════════════════════════════════════════════════════════════════════════════

phase_preflight() {
  header "Phase 1: Pre-flight Checks"

  local tools=("terraform" "gcloud" "gh" "pg_dump" "psql")
  local missing=()

  for tool in "${tools[@]}"; do
    if command -v "$tool" &>/dev/null; then
      ok "$tool found"
    else
      missing+=("$tool")
      error "$tool not found"
    fi
  done

  if [ ${#missing[@]} -gt 0 ]; then
    error "Missing required tools: ${missing[*]}"
    exit 1
  fi

  # gcloud auth
  ACTIVE_ACCOUNT=$(gcloud auth list --filter=status:ACTIVE --format="value(account)" 2>/dev/null || true)
  if [ -z "$ACTIVE_ACCOUNT" ]; then
    error "No active gcloud account. Run: gcloud auth login"
    exit 1
  fi
  ok "gcloud authenticated as: $ACTIVE_ACCOUNT"

  # gh auth
  if ! gh auth status &>/dev/null; then
    error "GitHub CLI not authenticated. Run: gh auth login"
    exit 1
  fi
  ok "GitHub CLI authenticated"

  # tfvars
  if [ ! -f "$TFVARS" ]; then
    error "Terraform vars file not found: $TFVARS"
    exit 1
  fi
  ok "Terraform vars: $TFVARS"

  echo ""
  ok "All pre-flight checks passed"
}

# ═══════════════════════════════════════════════════════════════════════════════
# Phase 2: Terraform apply
# ═══════════════════════════════════════════════════════════════════════════════

phase_terraform() {
  header "Phase 2: Terraform Apply"

  info "Running terraform init..."
  terraform init -upgrade -input=false
  ok "Terraform initialized"

  # Prod: import shared resources already created by dev workspace
  if [ "$ENV" = "prod" ]; then
    echo ""
    info "Production: importing shared Cloud SQL resources created by dev..."
    echo ""

    local imports=(
      "google_sql_database_instance.main|projects/${PROJECT_ID}/instances/${INSTANCE_NAME}"
      "google_sql_database.dev|projects/${PROJECT_ID}/instances/${INSTANCE_NAME}/databases/aha_sicu_dev"
      "google_sql_database.prod|projects/${PROJECT_ID}/instances/${INSTANCE_NAME}/databases/aha_sicu_prod"
      "google_sql_user.app|${PROJECT_ID}/${INSTANCE_NAME}/${DB_USER}"
      "google_service_account.cloud_sql_scheduler|projects/${PROJECT_ID}/serviceAccounts/aha-sicu-sql-scheduler-sa@${PROJECT_ID}.iam.gserviceaccount.com"
      "google_project_iam_member.cloud_sql_scheduler_admin|${PROJECT_ID} roles/cloudsql.admin serviceAccount:aha-sicu-sql-scheduler-sa@${PROJECT_ID}.iam.gserviceaccount.com"
      "google_cloud_scheduler_job.cloud_sql_start|projects/${PROJECT_ID}/locations/${REGION}/jobs/aha-sicu-cloud-sql-start"
      "google_cloud_scheduler_job.cloud_sql_stop|projects/${PROJECT_ID}/locations/${REGION}/jobs/aha-sicu-cloud-sql-stop"
    )

    for entry in "${imports[@]}"; do
      local resource="${entry%%|*}"
      local id="${entry##*|}"

      if terraform state show "$resource" &>/dev/null; then
        ok "$resource — already in state"
      else
        info "Importing $resource..."
        if terraform import -var-file="$TFVARS" "$resource" "$id"; then
          ok "Imported $resource"
        else
          warn "Import failed for $resource — may need manual review"
        fi
      fi
    done
  fi

  echo ""
  info "Running terraform plan..."
  echo ""
  terraform plan -var-file="$TFVARS" -out=tfplan.out

  echo ""
  if ! confirm "Apply this plan?"; then
    info "Aborted. Plan saved to tfplan.out"
    return 0
  fi

  echo ""
  info "Applying terraform plan..."
  terraform apply tfplan.out
  rm -f tfplan.out
  ok "Terraform apply complete"
}

# ═══════════════════════════════════════════════════════════════════════════════
# Phase 3: Database password
# ═══════════════════════════════════════════════════════════════════════════════

phase_password() {
  header "Phase 3: Database Password"

  # For prod, offer to copy the dev password
  if [ "$ENV" = "prod" ]; then
    info "Prod shares the same Cloud SQL user as dev."
    info "Checking if dev password exists in Secret Manager..."

    DEV_SECRET="aha_sicu_dev_db_password"
    if gcloud secrets versions access latest --secret="$DEV_SECRET" --project="$PROJECT_ID" &>/dev/null; then
      ok "Dev password secret exists"
      echo ""
      if confirm "Copy dev password to prod secret ($SECRET_NAME)?"; then
        DEV_PASSWORD=$(gcloud secrets versions access latest --secret="$DEV_SECRET" --project="$PROJECT_ID")
        echo -n "$DEV_PASSWORD" | gcloud secrets versions add "$SECRET_NAME" --data-file=- --project="$PROJECT_ID"
        ok "Password copied to $SECRET_NAME"
        return 0
      fi
      info "Skipping copy — will prompt for a new password"
    else
      warn "Dev password not found — you'll set a fresh password"
    fi
  fi

  echo ""
  info "Setting password for Cloud SQL user '${DB_USER}' on instance '${INSTANCE_NAME}'"
  echo ""
  read -rsp "Enter password: " DB_PASSWORD
  echo ""
  read -rsp "Confirm password: " DB_PASSWORD_CONFIRM
  echo ""

  if [ "$DB_PASSWORD" != "$DB_PASSWORD_CONFIRM" ]; then
    error "Passwords do not match"
    exit 1
  fi

  if [ -z "$DB_PASSWORD" ]; then
    error "Password cannot be empty"
    exit 1
  fi

  # Create or update the Cloud SQL user
  info "Checking if user '${DB_USER}' exists on instance '${INSTANCE_NAME}'..."
  if gcloud sql users list --instance="$INSTANCE_NAME" --project="$PROJECT_ID" --format="value(name)" 2>/dev/null | grep -q "^${DB_USER}$"; then
    info "User exists — updating password..."
    gcloud sql users set-password "$DB_USER" \
      --instance="$INSTANCE_NAME" \
      --password="$DB_PASSWORD" \
      --project="$PROJECT_ID"
    ok "Cloud SQL user password updated"
  else
    info "User does not exist — creating with password..."
    gcloud sql users create "$DB_USER" \
      --instance="$INSTANCE_NAME" \
      --password="$DB_PASSWORD" \
      --project="$PROJECT_ID"
    ok "Cloud SQL user created"
  fi

  info "Storing password in Secret Manager ($SECRET_NAME)..."
  echo -n "$DB_PASSWORD" | gcloud secrets versions add "$SECRET_NAME" --data-file=- --project="$PROJECT_ID"
  ok "Password stored in Secret Manager"

  # Import user into terraform state if not already there
  if ! terraform state show "google_sql_user.app" &>/dev/null; then
    info "Importing user into terraform state..."
    terraform import -var-file="$TFVARS" "google_sql_user.app" "${PROJECT_ID}/${INSTANCE_NAME}/${DB_USER}" || true
  fi
}

# ═══════════════════════════════════════════════════════════════════════════════
# Phase 4: GitHub Actions variables
# ═══════════════════════════════════════════════════════════════════════════════

phase_github_vars() {
  header "Phase 4: GitHub Actions Variables"

  info "Setting variables for GitHub environment: $GITHUB_ENV"
  info "Repository: $GITHUB_REPO"
  echo ""

  local vars=(
    "GCP_REGION|${REGION}"
    "ARTIFACT_REGISTRY_URL|${REGISTRY_URL}"
    "DB_SECRET_NAME|${SECRET_NAME}"
    "CLOUD_SQL_INSTANCE_CONNECTION|${INSTANCE_CONNECTION}"
    "DB_USER|${DB_USER}"
    "DB_NAME|${DB_NAME}"
  )

  for entry in "${vars[@]}"; do
    local var_name="${entry%%|*}"
    local var_value="${entry##*|}"

    gh variable set "$var_name" \
      --body "$var_value" \
      --env "$GITHUB_ENV" \
      --repo "$GITHUB_REPO"
    ok "$var_name = $var_value"
  done

  echo ""
  ok "All GitHub Actions variables set for $GITHUB_ENV"
}

# ═══════════════════════════════════════════════════════════════════════════════
# Phase 5: Data migration (Neon → Cloud SQL)
# ═══════════════════════════════════════════════════════════════════════════════

phase_data_migration() {
  header "Phase 5: Data Migration (Neon → Cloud SQL)"

  echo ""
  info "This phase will:"
  echo "  1. Download Cloud SQL Auth Proxy"
  echo "  2. pg_dump from Neon"
  echo "  3. Restore to Cloud SQL via Auth Proxy"
  echo ""

  read -rp "Enter Neon database URL (postgresql://...): " NEON_URL

  if [ -z "$NEON_URL" ]; then
    error "Neon URL cannot be empty"
    exit 1
  fi

  # Read password from Secret Manager
  info "Reading database password from Secret Manager..."
  DB_PASSWORD=$(gcloud secrets versions access latest --secret="$SECRET_NAME" --project="$PROJECT_ID")
  if [ -z "$DB_PASSWORD" ]; then
    error "Could not read password from $SECRET_NAME — run phase 3 first"
    exit 1
  fi
  ok "Password retrieved"

  # Download Cloud SQL Auth Proxy
  PROXY_DIR="/tmp/cloudsql-migration"
  PROXY_BIN="${PROXY_DIR}/cloud-sql-proxy"
  mkdir -p "$PROXY_DIR"

  if [ -f "$PROXY_BIN" ]; then
    ok "Cloud SQL Auth Proxy already downloaded"
  else
    info "Downloading Cloud SQL Auth Proxy..."

    ARCH=$(uname -m)
    case "$ARCH" in
      arm64|aarch64) PROXY_ARCH="arm64" ;;
      x86_64)        PROXY_ARCH="amd64" ;;
      *)             error "Unsupported architecture: $ARCH"; exit 1 ;;
    esac

    OS=$(uname -s | tr '[:upper:]' '[:lower:]')
    PROXY_URL="https://storage.googleapis.com/cloud-sql-connectors/cloud-sql-proxy/v2.14.3/cloud-sql-proxy.${OS}.${PROXY_ARCH}"

    curl -o "$PROXY_BIN" "$PROXY_URL"
    chmod +x "$PROXY_BIN"
    ok "Auth Proxy downloaded (${OS}/${PROXY_ARCH})"
  fi

  # Start Auth Proxy
  start_proxy

  # Dump from Neon
  DUMP_FILE="${PROXY_DIR}/${DB_NAME}_dump.sql"
  info "Dumping from Neon..."
  pg_dump "$NEON_URL" \
    --format=plain \
    --no-owner \
    --no-privileges \
    --clean \
    --if-exists \
    > "$DUMP_FILE"

  DUMP_SIZE=$(du -h "$DUMP_FILE" | cut -f1)
  ok "Dump complete — ${DUMP_SIZE} saved to ${DUMP_FILE}"

  echo ""
  info "Target: ${DB_USER}@127.0.0.1:${PROXY_PORT}/${DB_NAME}"
  echo ""

  if ! confirm "Restore this dump to Cloud SQL?"; then
    info "Dump saved at $DUMP_FILE — restore manually when ready"
    cleanup_proxy
    PROXY_PID=""
    return 0
  fi

  # Restore to Cloud SQL
  info "Restoring to Cloud SQL..."
  PGPASSWORD="$DB_PASSWORD" psql \
    -h 127.0.0.1 \
    -p "$PROXY_PORT" \
    -U "$DB_USER" \
    -d "$DB_NAME" \
    -v ON_ERROR_STOP=0 \
    -f "$DUMP_FILE"
  ok "Restore complete"

  # Stop proxy
  cleanup_proxy
  PROXY_PID=""
}

# ═══════════════════════════════════════════════════════════════════════════════
# Phase 6: Verification
# ═══════════════════════════════════════════════════════════════════════════════

phase_verify() {
  header "Phase 6: Verification"

  # Read password
  info "Reading database password from Secret Manager..."
  DB_PASSWORD=$(gcloud secrets versions access latest --secret="$SECRET_NAME" --project="$PROJECT_ID")

  # Start Auth Proxy
  start_proxy

  # Connectivity
  info "Testing connectivity..."
  if PGPASSWORD="$DB_PASSWORD" psql -h 127.0.0.1 -p "$PROXY_PORT" -U "$DB_USER" -d "$DB_NAME" -c "SELECT 1;" &>/dev/null; then
    ok "Database connectivity OK"
  else
    error "Cannot connect to $DB_NAME"
    cleanup_proxy
    PROXY_PID=""
    exit 1
  fi

  # Table count
  TABLE_COUNT=$(PGPASSWORD="$DB_PASSWORD" psql -h 127.0.0.1 -p "$PROXY_PORT" -U "$DB_USER" -d "$DB_NAME" \
    -t -A -c "SELECT count(*) FROM information_schema.tables WHERE table_schema = 'public' AND table_type = 'BASE TABLE';")
  ok "Tables in public schema: $TABLE_COUNT"

  # Row counts
  echo ""
  info "Row counts:"
  PGPASSWORD="$DB_PASSWORD" psql -h 127.0.0.1 -p "$PROXY_PORT" -U "$DB_USER" -d "$DB_NAME" \
    -t -A -c "
      SELECT table_name || ': ' || (xpath('/row/cnt/text()', xml_count))[1]::text
      FROM (
        SELECT table_name,
               query_to_xml('SELECT count(*) AS cnt FROM public.' || quote_ident(table_name), false, true, '') AS xml_count
        FROM information_schema.tables
        WHERE table_schema = 'public' AND table_type = 'BASE TABLE'
        ORDER BY table_name
      ) t;
    " | while IFS= read -r line; do
    [ -n "$line" ] && echo "  $line"
  done

  # Alembic version
  echo ""
  ALEMBIC_VERSION=$(PGPASSWORD="$DB_PASSWORD" psql -h 127.0.0.1 -p "$PROXY_PORT" -U "$DB_USER" -d "$DB_NAME" \
    -t -A -c "SELECT version_num FROM alembic_version LIMIT 1;" 2>/dev/null || echo "NOT_FOUND")
  if [ "$ALEMBIC_VERSION" = "NOT_FOUND" ]; then
    warn "alembic_version table not found (migrations haven't run yet)"
  else
    ok "Alembic version: $ALEMBIC_VERSION"
  fi

  # Cleanup
  cleanup_proxy
  PROXY_PID=""

  echo ""
  ok "Verification complete for $ENV"
}

# ═══════════════════════════════════════════════════════════════════════════════
# Main
# ═══════════════════════════════════════════════════════════════════════════════

PHASE_NAMES=(
  ""
  "Pre-flight checks"
  "Terraform apply"
  "Database password"
  "GitHub Actions variables"
  "Data migration"
  "Verification"
)

run_phase() {
  case $1 in
    1) phase_preflight ;;
    2) phase_terraform ;;
    3) phase_password ;;
    4) phase_github_vars ;;
    5) phase_data_migration ;;
    6) phase_verify ;;
    *) error "Invalid phase: $1 (valid: 1-6)"; exit 1 ;;
  esac
}

if [ -n "$PHASE" ]; then
  run_phase "$PHASE"
else
  for p in 1 2 3 4 5 6; do
    run_phase "$p"
    if [ "$p" -lt 6 ]; then
      echo ""
      if ! confirm "Continue to phase $((p + 1)) (${PHASE_NAMES[$((p + 1))]})?" ; then
        info "Paused after phase $p. Resume with: $(basename "$0") --phase $((p + 1))"
        exit 0
      fi
    fi
  done
fi

echo ""
echo "======================================"
echo "  Migration complete for $ENV!"
echo "======================================"
echo ""
