"""Unit tests for rules query functions with marketplace filtering."""

from datetime import datetime, timezone
from unittest.mock import AsyncMock

from app.db.queries.rules import get_all_rules, get_rules_by_template_and_marketplace, update_rules


MOCK_ID_RULE = {
    "id": 1,
    "template": "default",
    "marketplace": "ID",
    "rules": {"business": {"six_month_avg_threshold": {"threshold": 100000000}}},
    "version": 1,
    "updated_by": None,
    "updated_at": datetime(2026, 2, 12, tzinfo=timezone.utc),
}

MOCK_TH_RULE = {
    "id": 2,
    "template": "default",
    "marketplace": "TH",
    "rules": {"business": {"six_month_avg_threshold": {"threshold": 190000}}},
    "version": 1,
    "updated_by": None,
    "updated_at": datetime(2026, 2, 12, tzinfo=timezone.utc),
}


async def test_get_all_rules_defaults_to_id_marketplace():
    """get_all_rules without marketplace arg filters by 'ID'."""
    conn = AsyncMock()
    conn.fetch = AsyncMock(return_value=[MOCK_ID_RULE])

    result = await get_all_rules(conn)

    assert len(result) == 1
    assert result[0]["marketplace"] == "ID"
    # Verify SQL contains WHERE marketplace = $1 and param is 'ID'
    call_args = conn.fetch.call_args[0]
    assert "marketplace = $1" in call_args[0]
    assert call_args[1] == "ID"


async def test_get_all_rules_th_marketplace():
    """get_all_rules(conn, marketplace='TH') returns only THB rules."""
    conn = AsyncMock()
    conn.fetch = AsyncMock(return_value=[MOCK_TH_RULE])

    result = await get_all_rules(conn, marketplace="TH")

    assert len(result) == 1
    assert result[0]["marketplace"] == "TH"
    call_args = conn.fetch.call_args[0]
    assert call_args[1] == "TH"


async def test_get_rules_by_template_and_marketplace_id():
    """get_rules_by_template_and_marketplace returns ID row for default template."""
    conn = AsyncMock()
    conn.fetchrow = AsyncMock(return_value=MOCK_ID_RULE)

    result = await get_rules_by_template_and_marketplace(conn, "default", marketplace="ID")

    assert result is not None
    assert result["marketplace"] == "ID"
    call_args = conn.fetchrow.call_args[0]
    assert "template = $1" in call_args[0]
    assert "marketplace = $2" in call_args[0]
    assert call_args[1] == "default"
    assert call_args[2] == "ID"


async def test_get_rules_by_template_and_marketplace_th():
    """get_rules_by_template_and_marketplace(conn, 'default', 'TH') returns the THB row."""
    conn = AsyncMock()
    conn.fetchrow = AsyncMock(return_value=MOCK_TH_RULE)

    result = await get_rules_by_template_and_marketplace(conn, "default", marketplace="TH")

    assert result is not None
    assert result["marketplace"] == "TH"
    assert result["rules"]["business"]["six_month_avg_threshold"]["threshold"] == 190000


async def test_get_rules_by_template_and_marketplace_default():
    """get_rules_by_template_and_marketplace defaults marketplace to 'ID'."""
    conn = AsyncMock()
    conn.fetchrow = AsyncMock(return_value=MOCK_ID_RULE)

    await get_rules_by_template_and_marketplace(conn, "default")

    call_args = conn.fetchrow.call_args[0]
    assert call_args[2] == "ID"


async def test_get_rules_by_template_and_marketplace_not_found():
    """get_rules_by_template_and_marketplace returns None when no match."""
    conn = AsyncMock()
    conn.fetchrow = AsyncMock(return_value=None)

    result = await get_rules_by_template_and_marketplace(conn, "nonexistent", marketplace="TH")

    assert result is None


async def test_update_rules_filters_by_template_and_marketplace():
    """update_rules WHERE clause includes both template AND marketplace."""
    updated_rule = {**MOCK_ID_RULE, "version": 2, "updated_by": 1}
    conn = AsyncMock()
    conn.fetchrow = AsyncMock(return_value=updated_rule)

    new_rules = {"business": {"six_month_avg_threshold": {"threshold": 200000000}}}
    result = await update_rules(conn, "default", new_rules, 1, marketplace="ID")

    assert result is not None
    assert result["version"] == 2
    call_args = conn.fetchrow.call_args[0]
    sql = call_args[0]
    assert "WHERE template = $3 AND marketplace = $4" in sql
    assert "RETURNING" in sql
    assert "marketplace" in sql
    assert call_args[3] == "default"
    assert call_args[4] == "ID"


async def test_update_rules_th_marketplace():
    """update_rules with marketplace='TH' targets the THB rules row."""
    updated_rule = {**MOCK_TH_RULE, "version": 2, "updated_by": 1}
    conn = AsyncMock()
    conn.fetchrow = AsyncMock(return_value=updated_rule)

    new_rules = {"business": {"six_month_avg_threshold": {"threshold": 200000}}}
    result = await update_rules(conn, "default", new_rules, 1, marketplace="TH")

    assert result["marketplace"] == "TH"
    call_args = conn.fetchrow.call_args[0]
    assert call_args[4] == "TH"


async def test_get_all_rules_returns_marketplace_in_select():
    """get_all_rules SELECT clause includes marketplace column."""
    conn = AsyncMock()
    conn.fetch = AsyncMock(return_value=[MOCK_ID_RULE])

    await get_all_rules(conn)

    call_args = conn.fetch.call_args[0]
    sql = call_args[0]
    assert "marketplace" in sql.split("FROM")[0]  # marketplace in SELECT before FROM
