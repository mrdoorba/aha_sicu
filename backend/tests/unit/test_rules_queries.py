"""Unit tests for marketplace-aware rules query functions."""

from unittest.mock import AsyncMock

import pytest

from app.db.queries.rules import get_all_rules, get_rules_by_template_and_marketplace, update_rules


@pytest.mark.asyncio
async def test_get_all_rules_defaults_to_marketplace_id():
    """get_all_rules without explicit marketplace passes 'ID' to SQL."""
    conn = AsyncMock()
    conn.fetch = AsyncMock(return_value=[])

    await get_all_rules(conn)

    call_args = conn.fetch.call_args[0]
    assert "marketplace = $1" in call_args[0]
    assert call_args[1] == "ID"


@pytest.mark.asyncio
async def test_get_all_rules_with_marketplace_th():
    """get_all_rules with marketplace='TH' passes 'TH' to SQL."""
    conn = AsyncMock()
    conn.fetch = AsyncMock(return_value=[])

    await get_all_rules(conn, marketplace="TH")

    call_args = conn.fetch.call_args[0]
    assert call_args[1] == "TH"


@pytest.mark.asyncio
async def test_get_all_rules_select_includes_marketplace():
    """get_all_rules SELECT includes marketplace column."""
    conn = AsyncMock()
    conn.fetch = AsyncMock(return_value=[])

    await get_all_rules(conn)

    sql = conn.fetch.call_args[0][0]
    assert "marketplace" in sql.lower()


@pytest.mark.asyncio
async def test_get_rules_by_template_and_marketplace_for_th():
    """get_rules_by_template_and_marketplace with TH filters correctly."""
    mock_row = {
        "id": 2,
        "template": "default",
        "marketplace": "TH",
        "rules": {"business": {}},
        "version": 1,
        "updated_by": None,
        "updated_at": "2026-01-01T00:00:00+00:00",
    }
    conn = AsyncMock()
    conn.fetchrow = AsyncMock(return_value=mock_row)

    result = await get_rules_by_template_and_marketplace(conn, "default", marketplace="TH")

    assert result["marketplace"] == "TH"
    call_args = conn.fetchrow.call_args[0]
    assert "template = $1" in call_args[0]
    assert "marketplace = $2" in call_args[0]
    assert call_args[1] == "default"
    assert call_args[2] == "TH"


@pytest.mark.asyncio
async def test_get_rules_by_template_and_marketplace_defaults_to_id():
    """get_rules_by_template_and_marketplace defaults marketplace to 'ID'."""
    conn = AsyncMock()
    conn.fetchrow = AsyncMock(return_value=None)

    await get_rules_by_template_and_marketplace(conn, "default")

    call_args = conn.fetchrow.call_args[0]
    assert call_args[2] == "ID"


@pytest.mark.asyncio
async def test_update_rules_includes_marketplace_in_where():
    """update_rules WHERE clause includes both template AND marketplace."""
    mock_row = {
        "id": 1,
        "template": "default",
        "marketplace": "TH",
        "rules": {"new": "rules"},
        "version": 2,
        "updated_by": 1,
        "updated_at": "2026-01-01T00:00:00+00:00",
    }
    conn = AsyncMock()
    conn.fetchrow = AsyncMock(return_value=mock_row)

    await update_rules(conn, "default", {"new": "rules"}, 1, marketplace="TH")

    sql = conn.fetchrow.call_args[0][0]
    assert "template = $3" in sql
    assert "marketplace = $4" in sql


@pytest.mark.asyncio
async def test_update_rules_returning_includes_marketplace():
    """update_rules RETURNING clause includes marketplace."""
    mock_row = {
        "id": 1,
        "template": "default",
        "marketplace": "ID",
        "rules": {},
        "version": 2,
        "updated_by": 1,
        "updated_at": "2026-01-01T00:00:00+00:00",
    }
    conn = AsyncMock()
    conn.fetchrow = AsyncMock(return_value=mock_row)

    result = await update_rules(conn, "default", {}, 1)

    assert result["marketplace"] == "ID"
    sql = conn.fetchrow.call_args[0][0]
    assert "marketplace" in sql.split("RETURNING")[1]


@pytest.mark.asyncio
async def test_update_rules_defaults_to_marketplace_id():
    """update_rules without explicit marketplace passes 'ID'."""
    conn = AsyncMock()
    conn.fetchrow = AsyncMock(return_value=None)

    await update_rules(conn, "default", {}, 1)

    call_args = conn.fetchrow.call_args[0]
    assert call_args[4] == "ID"
