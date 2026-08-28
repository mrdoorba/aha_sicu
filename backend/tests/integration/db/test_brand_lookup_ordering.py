"""Match-tier ordering for brand lookup, exercised against real Postgres.

The bug this pins: searching "her" in production returned 149 matches ordered
alphabetically, so the brand actually named "Her" sat at rank 50 -- page five of
a dropdown that has no page two.
"""

import json

from app.db.queries.brands import get_brands_with_meeting


async def _seed(conn, *brand_names, marketplace="ID"):
    """Replace the brand roster with exactly these names (rolled back after the test)."""
    await conn.execute("DELETE FROM brand_vp_data")
    for name in brand_names:
        await conn.execute(
            """
            INSERT INTO brand_vp_data (brand_name, marketplace, raw_data, updated_at)
            VALUES ($1, $2, $3, NOW())
            """,
            name,
            marketplace,
            json.dumps({}),
        )


async def test_exact_match_outranks_alphabetically_earlier_substrings(pg_conn):
    """A name that *is* the query beats names that merely contain it."""
    await _seed(pg_conn, "420Father", "A 81 Herbal", "Acep Herbal", "Her", "Zher")

    rows = await get_brands_with_meeting(pg_conn, limit=10, search="her")

    assert rows[0]["brand_name"] == "Her"


async def test_prefix_matches_sit_between_exact_and_substring(pg_conn):
    """Tier order is exact, then prefix, then substring -- alphabetical within each."""
    await _seed(pg_conn, "Acep Herbal", "Her", "Herbal Zen", "Herbal Ayu", "Zher")

    rows = await get_brands_with_meeting(pg_conn, limit=10, search="her")

    assert [r["brand_name"] for r in rows] == [
        "Her",           # exact
        "Herbal Ayu",    # prefix, alphabetical
        "Herbal Zen",
        "Acep Herbal",   # substring, alphabetical
        "Zher",
    ]


async def test_exact_match_is_case_insensitive(pg_conn):
    """Typing "HER" finds the brand stored as "Her"."""
    await _seed(pg_conn, "A 81 Herbal", "Her")

    rows = await get_brands_with_meeting(pg_conn, limit=10, search="HER")

    assert rows[0]["brand_name"] == "Her"


async def test_browsing_without_search_stays_alphabetical(pg_conn):
    """No search term means every row shares one tier -- the brands page is untouched."""
    await _seed(pg_conn, "Zed", "Acme", "Mid")

    rows = await get_brands_with_meeting(pg_conn, limit=10)

    assert [r["brand_name"] for r in rows] == ["Acme", "Mid", "Zed"]


async def test_exact_match_survives_a_page_full_of_substrings(pg_conn):
    """The production shape: many substring matches, exact match still lands first."""
    await _seed(pg_conn, "Her", *[f"A{i:03d} Herbal" for i in range(30)])

    rows = await get_brands_with_meeting(pg_conn, limit=10, search="her")

    assert rows[0]["brand_name"] == "Her"
    assert len(rows) == 10
