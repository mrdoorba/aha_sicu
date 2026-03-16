#!/bin/bash
set -e

echo "==> Running database migrations..."
uv run alembic -c app/db/migrations/alembic.ini upgrade head

echo "==> Seeding local dev data..."
uv run python -m scripts.seed_local

echo "==> Starting uvicorn with hot reload..."
exec uv run uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
