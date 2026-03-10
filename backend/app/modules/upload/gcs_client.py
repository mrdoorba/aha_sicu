"""GCS storage client with local dev fallback."""

import logging
import tempfile
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

    @abstractmethod
    def generate_signed_download_url(
        self,
        object_name: str,
        expiry_minutes: int = 15,
    ) -> str:
        """Generate a signed URL for downloading a file."""


class GCSClient(StorageClient):
    """Google Cloud Storage client for production."""

    def __init__(self, bucket_name: str) -> None:
        import google.auth
        from google.cloud import storage

        self._credentials, self._project = google.auth.default()
        self._client = storage.Client(credentials=self._credentials, project=self._project)
        self._bucket = self._client.bucket(bucket_name)

    def generate_signed_upload_url(
        self,
        object_name: str,
        content_type: str,
        expiry_minutes: int = 15,
    ) -> str:
        import google.auth.compute_engine.credentials

        blob = self._bucket.blob(object_name)
        kwargs: dict = {
            "version": "v4",
            "expiration": timedelta(minutes=expiry_minutes),
            "method": "PUT",
            "content_type": content_type,
        }
        # On Cloud Run, default credentials can't sign directly.
        # Pass service_account_email + access_token to use IAM signBlob API.
        if isinstance(self._credentials, google.auth.compute_engine.credentials.Credentials):
            from google.auth.transport import requests
            if not self._credentials.token or self._credentials.expired:
                self._credentials.refresh(requests.Request())
            kwargs["service_account_email"] = self._credentials.service_account_email
            kwargs["access_token"] = self._credentials.token
        url = blob.generate_signed_url(**kwargs)
        return url

    def download_file(self, object_name: str) -> bytes:
        blob = self._bucket.blob(object_name)
        return blob.download_as_bytes()

    def delete_file(self, object_name: str) -> None:
        blob = self._bucket.blob(object_name)
        blob.delete()
        logger.info("Deleted GCS object: %s", object_name)

    def generate_signed_download_url(
        self,
        object_name: str,
        expiry_minutes: int = 15,
    ) -> str:
        import google.auth.compute_engine.credentials

        blob = self._bucket.blob(object_name)
        kwargs: dict = {
            "version": "v4",
            "expiration": timedelta(minutes=expiry_minutes),
            "method": "GET",
        }
        if isinstance(self._credentials, google.auth.compute_engine.credentials.Credentials):
            from google.auth.transport import requests
            if not self._credentials.token or self._credentials.expired:
                self._credentials.refresh(requests.Request())
            kwargs["service_account_email"] = self._credentials.service_account_email
            kwargs["access_token"] = self._credentials.token
        return blob.generate_signed_url(**kwargs)


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

    def generate_signed_download_url(
        self,
        object_name: str,
        expiry_minutes: int = 15,
    ) -> str:
        parts = object_name.split("/", 2)
        upload_id = parts[1] if len(parts) > 1 else "unknown"
        filename = parts[2] if len(parts) > 2 else "unknown"
        return f"http://localhost:8000/api/v1/upload/local/{upload_id}/{filename}"


def get_storage_client() -> StorageClient:
    """Return GCS client if configured, else local fallback."""
    if settings.gcs_upload_bucket:
        return GCSClient(settings.gcs_upload_bucket)
    return LocalStorageClient()


def make_object_name(upload_id: str, filename: str) -> str:
    """Build the GCS object path: uploads/{upload_id}/{filename}."""
    return f"uploads/{upload_id}/{filename}"
