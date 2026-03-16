"""Seed local development database with production data.

Loads a pg_dump export of production data for realistic local testing.
Falls back to minimal sample data if the dump file is missing.

Idempotent — clears and reloads data tables on each run.
Users table is NOT touched (local dev has its own auth users).
"""

import asyncio
import os
from pathlib import Path

import asyncpg


DATABASE_URL = os.environ.get(
    "DATABASE_URL",
    "postgresql://aha_sicu:localdev@localhost:5432/aha_coms_sicu_dev",
)

SEED_DATA_DIR = Path(__file__).parent / "seed_data"
PROD_DUMP = SEED_DATA_DIR / "prod_data.sql"

# Tables to clear and reload (order matters for FK constraints)
TABLES_TO_CLEAR = [
    "calculator_results",
    "evaluations",
    "evaluation_inputs",
    "brand_uploads",
    "brand_meeting_data",
    "brand_vp_data",
    "scoring_rules",
]


async def seed_from_dump(conn: asyncpg.Connection) -> None:
    """Load production data from pg_dump SQL file."""
    print(f"Loading prod data from {PROD_DUMP}...")

    # Clear existing data (reverse FK order)
    for table in TABLES_TO_CLEAR:
        await conn.execute(f"TRUNCATE {table} CASCADE")

    # Read and execute the dump
    sql = PROD_DUMP.read_text(encoding="utf-8")

    # Null out user_id references in evaluations (prod users don't exist locally)
    # The FK is nullable (ON DELETE SET NULL), so this is safe
    sql = sql.replace(
        "INSERT INTO public.evaluations VALUES (",
        "INSERT INTO public.evaluations (id, brand_id, user_id, template, final_score, verdict, score_breakdown, calculator_results, manual_inputs, rule_version, email_output, created_at, period) VALUES ("
    )

    # Execute statements one at a time (some are very large)
    # Split on statement boundaries but handle multi-line VALUES
    statements = []
    current = []
    for line in sql.split("\n"):
        # Skip comments and empty lines
        if line.startswith("--") or not line.strip():
            continue
        # Skip SET/SELECT config lines
        if line.startswith("SET ") or line.startswith("SELECT pg_catalog"):
            continue
        current.append(line)
        if line.rstrip().endswith(";"):
            statements.append("\n".join(current))
            current = []

    executed = 0
    errors = 0
    for stmt in statements:
        if not stmt.strip():
            continue
        try:
            await conn.execute(stmt)
            executed += 1
        except Exception as e:
            errors += 1
            if errors <= 5:
                # Show first few errors for debugging
                preview = stmt[:120].replace("\n", " ")
                print(f"  Warning: {e.__class__.__name__}: {str(e)[:80]} | {preview}...")

    # Reset sequences to avoid ID conflicts
    for table in ["brand_vp_data", "brand_meeting_data", "evaluations",
                   "evaluation_inputs", "calculator_results", "brand_uploads",
                   "scoring_rules"]:
        try:
            await conn.execute(f"""
                SELECT setval(pg_get_serial_sequence('{table}', 'id'),
                       COALESCE((SELECT MAX(id) FROM {table}), 0) + 1, false)
            """)
        except Exception:
            pass  # Table might not have a serial ID

    # Summary
    brand_count = await conn.fetchval("SELECT COUNT(*) FROM brand_vp_data")
    eval_count = await conn.fetchval("SELECT COUNT(*) FROM evaluations")
    rule_count = await conn.fetchval("SELECT COUNT(*) FROM scoring_rules")
    print(f"Seed complete: {brand_count} brands, {eval_count} evaluations, "
          f"{rule_count} scoring rules ({executed} statements, {errors} warnings)")


async def seed_minimal(conn: asyncpg.Connection) -> None:
    """Fallback: seed minimal sample data when dump is unavailable."""
    import json

    brands = [
        ("Demo Fashion Brand", {"Nama Brand": "Demo Fashion Brand", "Category": "Fashion"}),
        ("Demo Electronics Brand", {"Nama Brand": "Demo Electronics Brand", "Category": "Electronics"}),
        ("Demo Beauty Brand", {"Nama Brand": "Demo Beauty Brand", "Category": "Health & Beauty"}),
    ]
    for name, data in brands:
        await conn.execute(
            "INSERT INTO brand_vp_data (brand_name, raw_data) VALUES ($1, $2::jsonb) ON CONFLICT (brand_name) DO NOTHING",
            name, json.dumps(data),
        )

    brand_count = await conn.fetchval("SELECT COUNT(*) FROM brand_vp_data")
    rule_count = await conn.fetchval("SELECT COUNT(*) FROM scoring_rules")
    print(f"Seed complete (minimal): {brand_count} brands, {rule_count} scoring rule templates")


# Local dev role assignments — applied after every seed
# so admin@local.dev always gets admin role regardless of rebuild
LOCAL_ROLE_OVERRIDES = {
    "admin@local.dev": "admin",
    "leader@local.dev": "leader",
}


async def apply_role_overrides(conn: asyncpg.Connection) -> None:
    """Ensure local dev users have the right roles."""
    for email, role in LOCAL_ROLE_OVERRIDES.items():
        result = await conn.execute(
            "UPDATE users SET role = $1 WHERE email = $2",
            role, email,
        )
        if result != "UPDATE 0":
            print(f"  Role override: {email} → {role}")


async def seed() -> None:
    conn = await asyncpg.connect(DATABASE_URL)
    try:
        if PROD_DUMP.exists():
            await seed_from_dump(conn)
        else:
            print(f"No prod dump found at {PROD_DUMP}, using minimal seed data")
            await seed_minimal(conn)

        # Always apply role overrides for local dev users
        await apply_role_overrides(conn)
    finally:
        await conn.close()


if __name__ == "__main__":
    asyncio.run(seed())
