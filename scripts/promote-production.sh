#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT_DIR"

if ! git diff --quiet || ! git diff --cached --quiet; then
  echo "Working tree is not clean. Commit or stash changes before promoting production." >&2
  exit 1
fi

CURRENT_BRANCH="$(git branch --show-current)"

git fetch origin --prune

DEVELOP_SHA="$(git rev-parse origin/develop)"
PRODUCTION_SHA="$(git rev-parse origin/production)"

echo "origin/develop:    ${DEVELOP_SHA}"
echo "origin/production: ${PRODUCTION_SHA}"

if [ "$DEVELOP_SHA" = "$PRODUCTION_SHA" ]; then
  echo "Production already matches develop. Nothing to do."
  exit 0
fi

git checkout production
git reset --hard origin/production
git merge --ff-only origin/develop
git push origin production

echo
echo "Production fast-forwarded successfully."
echo "production/develop SHA: $(git rev-parse HEAD)"

if [ "$CURRENT_BRANCH" != "production" ]; then
  git checkout "$CURRENT_BRANCH"
fi
