"""Unit tests for marketplace-aware brand queries."""

import pytest
from unittest.mock import AsyncMock, MagicMock


@pytest.mark.asyncio
async def test_batch_upsert_includes_marketplace():
    """batch_upsert_brand_data should include marketplace in INSERT and ON CONFLICT."""
    from app.db.queries.brands import batch_upsert_brand_data

    mock_conn = AsyncMock()
    mock_conn.execute = AsyncMock(return_value="INSERT 0 2")

    await batch_upsert_brand_data(
        mock_conn,
        table="brand_vp_data",
        brand_names=["Brand A", "Brand B"],
        raw_data_list=[{"col": "val1"}, {"col": "val2"}],
        marketplace="TH",
    )

    sql = mock_conn.execute.call_args[0][0]
    assert "marketplace" in sql
    assert "ON CONFLICT (brand_name, marketplace)" in sql


@pytest.mark.asyncio
async def test_batch_upsert_defaults_to_id_marketplace():
    """batch_upsert_brand_data should default marketplace to 'ID'."""
    from app.db.queries.brands import batch_upsert_brand_data

    mock_conn = AsyncMock()
    mock_conn.execute = AsyncMock(return_value="INSERT 0 1")

    await batch_upsert_brand_data(
        mock_conn,
        table="brand_vp_data",
        brand_names=["Brand A"],
        raw_data_list=[{"col": "val"}],
    )

    # Should pass 'ID' as the marketplace array
    args = mock_conn.execute.call_args[0]
    assert ["ID"] in args  # marketplace array


@pytest.mark.asyncio
async def test_get_brands_with_meeting_filters_by_marketplace():
    """get_brands_with_meeting should accept and filter by marketplace list."""
    from app.db.queries.brands import get_brands_with_meeting
    from unittest.mock import patch

    with patch("app.db.queries.brands.fetch_all", new_callable=AsyncMock) as mock_fetch:
        mock_fetch.return_value = []

        await get_brands_with_meeting(
            AsyncMock(), limit=20, offset=0, search=None, marketplaces=["TH"]
        )

        sql = mock_fetch.call_args[0][1]
        assert "marketplace" in sql


@pytest.mark.asyncio
async def test_get_brands_count_filters_by_marketplace():
    """get_brands_count_with_search should filter by marketplace list."""
    from app.db.queries.brands import get_brands_count_with_search

    mock_conn = AsyncMock()
    mock_conn.fetchval = AsyncMock(return_value=5)

    result = await get_brands_count_with_search(
        mock_conn, search=None, marketplaces=["ID", "TH"]
    )

    sql = mock_conn.fetchval.call_args[0][0]
    assert "marketplace" in sql
