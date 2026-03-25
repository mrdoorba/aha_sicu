"""Unit tests for multi-marketplace sync logic."""

import pytest
from unittest.mock import AsyncMock, patch, MagicMock


@pytest.mark.asyncio
async def test_sync_sheet_to_table_passes_marketplace():
    """_sync_sheet_to_table should pass marketplace to batch_upsert."""
    from app.modules.sync.service import _sync_sheet_to_table

    with patch("app.modules.sync.service.brand_queries") as mock_bq, \
         patch("app.modules.sync.service.db") as mock_db:
        mock_conn = AsyncMock()
        mock_txn = MagicMock()
        mock_txn.__aenter__ = AsyncMock(return_value=None)
        mock_txn.__aexit__ = AsyncMock(return_value=None)
        mock_conn.transaction = MagicMock(return_value=mock_txn)
        mock_db.connection.return_value.__aenter__.return_value = mock_conn
        mock_bq.batch_upsert_brand_data = AsyncMock(return_value=1)

        await _sync_sheet_to_table(
            rows=[{"Brand": "Test"}],
            table="brand_vp_data",
            brand_column="Brand",
            sheet_type="vp_th",
            marketplace="TH",
        )

        mock_bq.batch_upsert_brand_data.assert_called_once()
        call_kwargs = mock_bq.batch_upsert_brand_data.call_args
        assert call_kwargs.kwargs.get("marketplace") == "TH"
