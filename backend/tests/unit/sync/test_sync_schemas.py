"""Unit tests for sync schema models."""

from datetime import datetime

from app.modules.sync.schemas import SyncStatusResponse


def test_sync_status_response_maps_timed_out_to_failed():
    """SyncStatusResponse maps timed-out records to status='failed' with timeout message."""
    response = SyncStatusResponse.model_validate(
        {
            "id": 1,
            "started_at": datetime(2026, 2, 24, 18, 57, 0),
            "completed_at": None,
            "success": None,
            "brands_synced": 0,
            "error_message": None,
            "sync_details": None,
            "timed_out": True,
        }
    )

    assert response.status == "failed"
    assert response.error_message == "Sync timed out after 10 minutes"


def test_sync_status_response_in_progress_when_not_timed_out():
    """SyncStatusResponse shows in_progress for active (non-timed-out) syncs."""
    response = SyncStatusResponse.model_validate(
        {
            "id": 2,
            "started_at": datetime(2026, 2, 25, 10, 0, 0),
            "completed_at": None,
            "success": None,
            "brands_synced": 0,
            "error_message": None,
            "sync_details": None,
            "timed_out": False,
        }
    )

    assert response.status == "in_progress"
    assert response.error_message is None


def test_sync_status_response_preserves_existing_error_message_on_timeout():
    """SyncStatusResponse does not overwrite an existing error_message on timeout."""
    response = SyncStatusResponse.model_validate(
        {
            "id": 3,
            "started_at": datetime(2026, 2, 24, 18, 57, 0),
            "completed_at": None,
            "success": None,
            "brands_synced": 0,
            "error_message": "Connection refused",
            "sync_details": None,
            "timed_out": True,
        }
    )

    assert response.status == "failed"
    # Existing error_message should be preserved, not overwritten
    assert response.error_message == "Connection refused"
