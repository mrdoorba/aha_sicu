"""GCS storage client with local dev fallback."""

import logging
import os
import shutil
import tempfile
import uuid
from abc import ABC, abstractmethod
from datetime import timedelta
from pathlib import Path

from app.config import settings

logger = logging.getLogger(__name__)


class StorageClient(ABC):
    """Abstract interface for file storage operations."""

    @abstractmethod
    def generate_signed_upload_url(
        self,
        object_name: str,
        content_type: str,
        expiry_minutes: int = 15,
    ) -> str:
        """Generate a signed URL for uploading a file."""

    @abstractmethod
    def download_file(self, object_name: str) -> bytes:
        """Download a file and return its bytes."""

    @abstractmethod
    def delete_file(self, object_name: str) -> None:
        """Delete a file from storage."""


class GCSClient(StorageClient):
    """Google Cloud Storage client for production."""

    def __init__(self, bucket_name: str) -> None:
        from google.cloud import storage

        self._client = storage.Client()
        self._bucket = self._client.bucket(bucket_name)

    def generate_signed_upload_url(
        self,
        object_name: str,
        content_type: str,
        expiry_minutes: int = 15,
    ) -> str:
        blob = self._bucket.blob(object_name)
        url = blob.generate_signed_url(
            version="v4",
            expiration=timedelta(minutes=expiry_minutes),
            method="PUT",
            content_type=content_type,
        )
        return url

    def download_file(self, object_name: str) -> bytes:
        blob = self._bucket.blob(object_name)
        return blob.download_as_bytes()

    def delete_file(self, object_name: str) -> None:
        blob = self._bucket.blob(object_name)
        blob.delete()
        logger.info("Deleted GCS object: %s", object_name)


class LocalStorageClient(StorageClient):
    """Local filesystem fallback for development without GCS."""

    def __init__(self) -> None:
        self._base_dir = Path(tempfile.gettempdir()) / "aha_sicu_uploads"
        self._base_dir.mkdir(parents=True, exist_ok=True)
        logger.info("LocalStorageClient using: %s", self._base_dir)

    def generate_signed_upload_url(
        self,
        object_name: str,
        content_type: str,
        expiry_minutes: int = 15,
    ) -> str:
        # In local mode, return a URL pointing to the local upload endpoint.
        # The frontend PUTs the file to this URL just like it would with GCS.
        # Extract upload_id and filename from object_name (uploads/{id}/{filename})
        parts = object_name.split("/", 2)
        upload_id = parts[1] if len(parts) > 1 else "unknown"
        filename = parts[2] if len(parts) > 2 else "unknown"
        return f"http://localhost:8000/api/v1/upload/local/{upload_id}/{filename}"

    def download_file(self, object_name: str) -> bytes:
        file_path = self._base_dir / object_name
        return file_path.read_bytes()

    def delete_file(self, object_name: str) -> None:
        file_path = self._base_dir / object_name
        if file_path.exists():
            file_path.unlink()
            logger.info("Deleted local file: %s", file_path)


def get_storage_client() -> StorageClient:
    """Return GCS client if configured, else local fallback."""
    if settings.gcs_upload_bucket:
        return GCSClient(settings.gcs_upload_bucket)
    return LocalStorageClient()


def make_object_name(upload_id: str, filename: str) -> str:
    """Build the GCS object path: uploads/{upload_id}/{filename}."""
    return f"uploads/{upload_id}/{filename}"
