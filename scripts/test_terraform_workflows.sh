#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
PLAN_WORKFLOW="$ROOT_DIR/.github/workflows/terraform-plan.yml"
APPLY_WORKFLOW="$ROOT_DIR/.github/workflows/terraform-apply.yml"

assert_contains() {
  local file="$1"
  local pattern="$2"
  if ! rg -q "$pattern" "$file"; then
    echo "Missing pattern '$pattern' in $file" >&2
    exit 1
  fi
}

assert_not_contains() {
  local file="$1"
  local pattern="$2"
  if rg -q "$pattern" "$file"; then
    echo "Unexpected pattern '$pattern' in $file" >&2
    exit 1
  fi
}

assert_contains "$PLAN_WORKFLOW" 'pull_request:'
assert_contains "$PLAN_WORKFLOW" 'terraform plan'
assert_contains "$PLAN_WORKFLOW" 'upload-artifact'
assert_not_contains "$PLAN_WORKFLOW" 'terraform apply'

assert_contains "$APPLY_WORKFLOW" 'workflow_dispatch:'
assert_contains "$APPLY_WORKFLOW" 'push:'
assert_contains "$APPLY_WORKFLOW" 'terraform apply -input=false tfplan'
assert_not_contains "$APPLY_WORKFLOW" 'pull_request:'

echo "Terraform workflow contract checks passed."
