#!/usr/bin/env bash
set -euo pipefail

# Store ICU - Terraform Bootstrap Script
# Automates: init → apply → secret injection → output summary

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

info()  { echo -e "${CYAN}[INFO]${NC} $1"; }
ok()    { echo -e "${GREEN}[OK]${NC} $1"; }
warn()  { echo -e "${YELLOW}[WARN]${NC} $1"; }
error() { echo -e "${RED}[ERROR]${NC} $1"; }

# ─── Step 1: Check prerequisites ───────────────────────────────────────────────

echo ""
echo "======================================"
echo "  Store ICU - Terraform Setup"
echo "======================================"
echo ""

info "Checking prerequisites..."

if ! command -v terraform &> /dev/null; then
  error "terraform not found. Install from https://www.terraform.io/downloads"
  exit 1
fi
ok "terraform $(terraform version -json | python3 -c 'import sys,json; print(json.load(sys.stdin)["terraform_version"])' 2>/dev/null || terraform version | head -1)"

if ! command -v gcloud &> /dev/null; then
  error "gcloud CLI not found. Install from https://cloud.google.com/sdk/docs/install"
  exit 1
fi
ok "gcloud $(gcloud version 2>/dev/null | head -1 | awk '{print $NF}')"

# Check gcloud auth
ACTIVE_ACCOUNT=$(gcloud auth list --filter=status:ACTIVE --format="value(account)" 2>/dev/null || true)
if [ -z "$ACTIVE_ACCOUNT" ]; then
  error "No active gcloud account. Run: gcloud auth login && gcloud auth application-default login"
  exit 1
fi
ok "Authenticated as: $ACTIVE_ACCOUNT"

# ─── Step 2: Select environment ────────────────────────────────────────────────

echo ""
info "Available environments:"
echo "  1) dev  (environments/dev.tfvars)"
echo "  2) prod (environments/prod.tfvars)"
echo ""
read -rp "Select environment [1/2]: " ENV_CHOICE

case "$ENV_CHOICE" in
  1|dev)   ENV="dev" ;;
  2|prod)  ENV="prod" ;;
  *)
    error "Invalid choice. Use 1 (dev) or 2 (prod)."
    exit 1
    ;;
esac

TFVARS="environments/${ENV}.tfvars"
if [ ! -f "$TFVARS" ]; then
  error "File not found: $TFVARS"
  exit 1
fi

PROJECT_ID=$(grep '^project_id' "$TFVARS" | sed 's/.*= *"\(.*\)"/\1/')
ok "Environment: $ENV"
ok "Project: $PROJECT_ID"

# Set gcloud project
gcloud config set project "$PROJECT_ID" --quiet 2>/dev/null
ok "gcloud project set to $PROJECT_ID"

# ─── Step 3: Terraform init ────────────────────────────────────────────────────

echo ""
info "Running terraform init..."
terraform init -upgrade -input=false
ok "Terraform initialized"

# ─── Step 4: Terraform plan ────────────────────────────────────────────────────

echo ""
info "Running terraform plan..."
echo ""
terraform plan -var-file="$TFVARS" -out=tfplan.out

echo ""
read -rp "Apply this plan? [y/N]: " APPLY_CONFIRM
if [[ ! "$APPLY_CONFIRM" =~ ^[Yy]$ ]]; then
  info "Aborted. Plan saved to tfplan.out — apply manually with: terraform apply tfplan.out"
  exit 0
fi

# ─── Step 5: Terraform apply ──────────────────────────────────────────────────

echo ""
info "Applying terraform plan..."
terraform apply tfplan.out
rm -f tfplan.out
ok "Terraform apply complete"

# ─── Step 6: Inject secret placeholders if needed ──────────────────────────────

echo ""
info "Checking Secret Manager versions..."

SECRETS=(
  "aha_coms_sicu_${ENV}_db_password"
  "aha_coms_sicu_${ENV}_gsheets_credentials"
  "aha_coms_sicu_${ENV}_firebase_admin"
  "aha_coms_sicu_${ENV}_smtp_password"
)

SECRETS_NEEDING_VALUES=()

for SECRET_NAME in "${SECRETS[@]}"; do
  VERSION_COUNT=$(gcloud secrets versions list "$SECRET_NAME" \
    --project "$PROJECT_ID" \
    --format="value(name)" \
    --limit=1 2>/dev/null | wc -l | tr -d ' ')

  if [ "$VERSION_COUNT" -eq 0 ]; then
    warn "$SECRET_NAME has no versions — injecting placeholder"
    echo -n "placeholder" > /tmp/_tf_secret_placeholder.txt
    gcloud secrets versions add "$SECRET_NAME" \
      --data-file /tmp/_tf_secret_placeholder.txt \
      --project "$PROJECT_ID"
    rm -f /tmp/_tf_secret_placeholder.txt
    SECRETS_NEEDING_VALUES+=("$SECRET_NAME")
  else
    ok "$SECRET_NAME has version(s)"
  fi
done

if [ ${#SECRETS_NEEDING_VALUES[@]} -gt 0 ]; then
  echo ""
  warn "The following secrets have PLACEHOLDER values — update with real values:"
  for S in "${SECRETS_NEEDING_VALUES[@]}"; do
    echo "  gcloud secrets versions add $S --data-file /path/to/value.txt --project $PROJECT_ID"
  done
fi

# ─── Step 7: Show outputs ─────────────────────────────────────────────────────

echo ""
echo "======================================"
echo "  Terraform Outputs"
echo "======================================"
echo ""
terraform output
echo ""
ok "Setup complete for $ENV environment!"
echo ""
