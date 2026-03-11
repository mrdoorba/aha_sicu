# File Download Feature Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers-extended-cc:executing-plans to implement this plan task-by-task.

**Goal:** Allow users to download previously uploaded files via signed URLs, with download buttons in upload cards and a collapsible download table.

**Architecture:** Add `storage_path` column to `brand_uploads`, stop deleting files after processing, add `generate_signed_download_url` to storage clients, new download endpoint, and frontend download UI (in-card buttons + collapsible Step 4b section).

**Tech Stack:** FastAPI, asyncpg, GCS signed URLs, React, TanStack Query, Tailwind CSS, lucide-react icons

---

### Task 0: Add `storage_path` column to `brand_uploads`

**Files:**
- Create: `backend/app/db/migrations/versions/024_add_storage_path_to_brand_uploads.py`
- Modify: `backend/app/db/queries/uploads.py`

**Step 1: Write the migration**

```python
"""Add storage_path column to brand_uploads

Stores the GCS/local object path so files can be downloaded later.

Revision ID: 024
Revises: 023
Create Date: 2026-03-10
"""

import sqlalchemy as sa
from alembic import op

revision = "024"
down_revision = "023"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        "brand_uploads",
        sa.Column("storage_path", sa.Text(), nullable=True),
    )


def downgrade() -> None:
    op.drop_column("brand_uploads", "storage_path")
```

**Step 2: Add `storage_path` to `UploadRow` TypedDict and queries**

In `backend/app/db/queries/uploads.py`:

- Add `storage_path: str | None` to `UploadRow` TypedDict (after `uploaded_at`)
- Add `storage_path` to SELECT in `get_uploads_by_brand()` query
- Add `storage_path` to SELECT in `get_upload_by_type()` query
- Add `storage_path` parameter to `upsert_upload()` — include in INSERT columns, VALUES, and ON CONFLICT UPDATE SET
- Add `storage_path` to RETURNING clause in `upsert_upload()`

**Step 3: Run migration**

```bash
cd backend && uv run alembic upgrade head
```

**Step 4: Commit**

```bash
git add backend/app/db/migrations/versions/024_add_storage_path_to_brand_uploads.py backend/app/db/queries/uploads.py
git commit -m "Add storage_path column to brand_uploads table"
```

---

### Task 1: Add `generate_signed_download_url` to storage clients

**Files:**
- Modify: `backend/app/modules/upload/gcs_client.py`
- Create: `backend/tests/unit/test_gcs_client.py`

**Step 1: Write failing test**

```python
"""Tests for storage client download URL generation."""

import tempfile
from pathlib import Path

from app.modules.upload.gcs_client import LocalStorageClient


def test_generate_signed_download_url_returns_local_url():
    """Local client returns a URL pointing to the local download endpoint."""
    storage = LocalStorageClient()
    url = storage.generate_signed_download_url("uploads/abc-123/report.csv")
    assert url == "http://localhost:8000/api/v1/upload/local/abc-123/report.csv"


def test_generate_signed_download_url_handles_nested_path():
    """Object names with nested paths are preserved."""
    storage = LocalStorageClient()
    url = storage.generate_signed_download_url("uploads/def-456/my file.xlsx")
    assert "/def-456/my file.xlsx" in url
```

**Step 2: Run test to verify it fails**

```bash
cd backend && uv run pytest tests/unit/test_gcs_client.py -v
```

Expected: FAIL — `generate_signed_download_url` does not exist.

**Step 3: Implement `generate_signed_download_url`**

In `backend/app/modules/upload/gcs_client.py`:

Add to `StorageClient` ABC (after `delete_file`):

```python
@abstractmethod
def generate_signed_download_url(
    self,
    object_name: str,
    expiry_minutes: int = 15,
) -> str:
    """Generate a signed URL for downloading a file."""
```

Add to `GCSClient`:

```python
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
```

Add to `LocalStorageClient`:

```python
def generate_signed_download_url(
    self,
    object_name: str,
    expiry_minutes: int = 15,
) -> str:
    # Reuse the local upload endpoint URL for downloads in dev.
    # The local download endpoint will serve the file bytes.
    parts = object_name.split("/", 2)
    upload_id = parts[1] if len(parts) > 1 else "unknown"
    filename = parts[2] if len(parts) > 2 else "unknown"
    return f"http://localhost:8000/api/v1/upload/local/{upload_id}/{filename}"
```

**Step 4: Run tests**

```bash
cd backend && uv run pytest tests/unit/test_gcs_client.py -v
```

Expected: PASS

**Step 5: Commit**

```bash
git add backend/app/modules/upload/gcs_client.py backend/tests/unit/test_gcs_client.py
git commit -m "Add generate_signed_download_url to storage clients"
```

---

### Task 2: Stop deleting files after processing + store storage_path

**Files:**
- Modify: `backend/app/modules/upload/service.py`
- Modify: `backend/tests/integration/api/test_upload.py`

**Step 1: Update the test to verify file is NOT deleted**

In `backend/tests/integration/api/test_upload.py`, find the test that verifies `process_upload` and update the mock assertion:

- Change `storage.delete_file.assert_called_once()` (or similar) to `storage.delete_file.assert_not_called()`
- Add assertion that the upserted row includes `storage_path`

**Step 2: Run test to verify it fails**

```bash
cd backend && uv run pytest tests/integration/api/test_upload.py -v -k "process"
```

Expected: FAIL — `delete_file` is still called.

**Step 3: Modify `process_upload` in service.py**

In `backend/app/modules/upload/service.py`:

1. **Remove the deletion block** (lines 297-302): Delete these lines:
   ```python
   # Delete from storage (best-effort cleanup)
   storage = get_storage_client()
   try:
       await asyncio.to_thread(storage.delete_file, pending.object_name)
   except Exception as e:
       logger.warning("Failed to delete file from storage: %s", e)
   ```

2. **Pass `storage_path` to `_store_and_auto_execute`**: The `pending.object_name` contains the storage path. Pass it through to `upsert_upload()`. Find where `upsert_upload` is called inside `_store_and_auto_execute` and add `storage_path=pending.object_name` as a parameter.

3. **Delete old file on re-upload**: Before upserting, check if an existing upload exists for this `(brand_id, file_type)`. If it has a `storage_path`, delete that old file from storage:
   ```python
   # Delete old file from storage if replacing
   async with db.connection() as conn:
       existing = await upload_queries.get_upload_by_type(conn, brand_id, file_type)
   if existing and existing.get("storage_path"):
       storage = get_storage_client()
       try:
           await asyncio.to_thread(storage.delete_file, existing["storage_path"])
       except Exception as e:
           logger.warning("Failed to delete old file from storage: %s", e)
   ```
   Place this before the `_store_and_auto_execute` call.

**Step 4: Run tests**

```bash
cd backend && uv run pytest tests/integration/api/test_upload.py -v
```

Expected: PASS

**Step 5: Commit**

```bash
git add backend/app/modules/upload/service.py backend/tests/integration/api/test_upload.py
git commit -m "Keep uploaded files in storage, delete old file on re-upload"
```

---

### Task 3: Add download endpoint

**Files:**
- Modify: `backend/app/modules/upload/schemas.py`
- Modify: `backend/app/modules/upload/service.py`
- Modify: `backend/app/modules/upload/router.py`
- Create: `backend/tests/integration/api/test_download.py`

**Step 1: Write failing test**

Create `backend/tests/integration/api/test_download.py`:

```python
"""Tests for file download endpoint."""

import pytest
from unittest.mock import AsyncMock, patch

from httpx import AsyncClient


@pytest.mark.anyio
async def test_download_returns_signed_url(
    auth_client: AsyncClient,
    seed_brand: dict,
):
    """Download endpoint returns a signed URL for an existing upload."""
    brand_id = seed_brand["id"]
    file_type = "cpc_ad_report"

    # Seed an upload with storage_path
    # (Use the existing upload flow or direct DB insert)
    with patch("app.modules.upload.service.get_storage_client") as mock_storage:
        mock_storage.return_value.generate_signed_download_url.return_value = (
            "https://storage.example.com/signed-download-url"
        )
        # Insert a brand_upload row with storage_path via direct DB
        from app.db import db
        from app.db.queries import uploads as upload_queries
        async with db.connection() as conn:
            await upload_queries.upsert_upload(
                conn,
                brand_id=brand_id,
                file_type=file_type,
                calculator_target="ads_keyword",
                filename="Brand_report.csv",
                file_size=1024,
                row_count=25,
                parsed_data={"rows": []},
                uploaded_by=1,
                storage_path="uploads/abc-123/report.csv",
            )

        resp = await auth_client.get(
            f"/api/v1/upload/brands/{brand_id}/download/{file_type}"
        )

    assert resp.status_code == 200
    body = resp.json()
    assert "download_url" in body
    assert "filename" in body


@pytest.mark.anyio
async def test_download_returns_404_when_no_upload(
    auth_client: AsyncClient,
    seed_brand: dict,
):
    """Download endpoint returns 404 if no file uploaded for this slot."""
    resp = await auth_client.get(
        f"/api/v1/upload/brands/{seed_brand['id']}/download/cpc_ad_report"
    )
    assert resp.status_code == 404


@pytest.mark.anyio
async def test_download_returns_404_when_no_storage_path(
    auth_client: AsyncClient,
    seed_brand: dict,
):
    """Download endpoint returns 404 if upload exists but has no storage_path (legacy)."""
    brand_id = seed_brand["id"]
    from app.db import db
    from app.db.queries import uploads as upload_queries
    async with db.connection() as conn:
        await upload_queries.upsert_upload(
            conn,
            brand_id=brand_id,
            file_type="cpc_ad_report",
            calculator_target="ads_keyword",
            filename="Brand_report.csv",
            file_size=1024,
            row_count=25,
            parsed_data={"rows": []},
            uploaded_by=1,
            storage_path=None,
        )

    resp = await auth_client.get(
        f"/api/v1/upload/brands/{brand_id}/download/cpc_ad_report"
    )
    assert resp.status_code == 404
```

**Step 2: Run test to verify it fails**

```bash
cd backend && uv run pytest tests/integration/api/test_download.py -v
```

Expected: FAIL — endpoint does not exist.

**Step 3: Implement the download endpoint**

Add to `backend/app/modules/upload/schemas.py`:

```python
class DownloadResponse(BaseModel):
    download_url: str
    filename: str
```

Add to `backend/app/modules/upload/service.py`:

```python
async def get_download_url(brand_id: int, file_type: str) -> DownloadResponse:
    """Generate a signed download URL for a previously uploaded file."""
    _validate_file_type(file_type)

    async with db.connection() as conn:
        upload = await upload_queries.get_upload_by_type(conn, brand_id, file_type)

    if not upload or not upload.get("storage_path"):
        raise AppException(
            code="UPLOAD_NOT_FOUND",
            detail=f"No downloadable file for brand {brand_id}, type {file_type}",
            status_code=404,
        )

    storage = get_storage_client()
    download_url = await asyncio.to_thread(
        storage.generate_signed_download_url, upload["storage_path"]
    )

    return DownloadResponse(
        download_url=download_url,
        filename=upload["filename"],
    )
```

Add to `backend/app/modules/upload/router.py`:

```python
from app.modules.upload.schemas import DownloadResponse
from app.modules.upload.service import get_download_url

@router.get("/brands/{brand_id}/download/{file_type}", response_model=DownloadResponse)
async def download_file(
    brand_id: int,
    file_type: str,
    current_user: dict = Depends(get_current_user),
) -> DownloadResponse:
    """Generate a signed download URL for a previously uploaded file."""
    return await get_download_url(brand_id=brand_id, file_type=file_type)
```

**Step 4: Run tests**

```bash
cd backend && uv run pytest tests/integration/api/test_download.py -v
```

Expected: PASS

**Step 5: Run all upload tests to ensure no regressions**

```bash
cd backend && uv run pytest tests/integration/api/test_upload.py tests/integration/api/test_download.py -v
```

Expected: All PASS

**Step 6: Commit**

```bash
git add backend/app/modules/upload/schemas.py backend/app/modules/upload/service.py backend/app/modules/upload/router.py backend/tests/integration/api/test_download.py
git commit -m "Add GET download endpoint with signed URL generation"
```

---

### Task 4: Add local download endpoint for dev

**Files:**
- Modify: `backend/app/modules/upload/router.py`

**Step 1: Write failing test**

Add to `backend/tests/integration/api/test_download.py`:

```python
@pytest.mark.anyio
async def test_local_download_serves_file(
    auth_client: AsyncClient,
):
    """Local download endpoint serves file bytes in dev mode."""
    from app.modules.upload.gcs_client import LocalStorageClient, make_object_name

    storage = LocalStorageClient()
    object_name = make_object_name("test-dl-id", "report.csv")
    file_path = storage._base_dir / object_name
    file_path.parent.mkdir(parents=True, exist_ok=True)
    file_path.write_bytes(b"col1,col2\nval1,val2\n")

    resp = await auth_client.get(
        "/api/v1/upload/local/test-dl-id/report.csv"
    )
    assert resp.status_code == 200
    assert resp.content == b"col1,col2\nval1,val2\n"

    # Cleanup
    file_path.unlink(missing_ok=True)
```

**Step 2: Run test to verify it fails**

```bash
cd backend && uv run pytest tests/integration/api/test_download.py::test_local_download_serves_file -v
```

Expected: FAIL — only PUT exists for local endpoint, no GET.

**Step 3: Add GET handler to the local endpoint**

In `backend/app/modules/upload/router.py`, add a new GET route:

```python
from fastapi.responses import Response

@router.get("/local/{upload_id}/{filename:path}")
async def local_download(
    upload_id: str,
    filename: str,
    current_user: dict = Depends(get_current_user),
) -> Response:
    """Local dev endpoint: serve file bytes for download.

    Only available when gcs_upload_bucket is not configured.
    """
    if settings.gcs_upload_bucket:
        return JSONResponse(
            status_code=404, content={"detail": "Local download not available in production"}
        )

    import mimetypes
    import os

    safe_filename = os.path.basename(filename)
    if not safe_filename or safe_filename in (".", ".."):
        return JSONResponse(status_code=400, content={"detail": "Invalid filename"})

    from app.modules.upload.gcs_client import LocalStorageClient, make_object_name

    storage = LocalStorageClient()
    object_name = make_object_name(upload_id, safe_filename)
    file_path = storage._base_dir / object_name

    if not file_path.exists():
        return JSONResponse(status_code=404, content={"detail": "File not found"})

    content_type = mimetypes.guess_type(safe_filename)[0] or "application/octet-stream"
    return Response(
        content=file_path.read_bytes(),
        media_type=content_type,
        headers={"Content-Disposition": f'attachment; filename="{safe_filename}"'},
    )
```

**Step 4: Run tests**

```bash
cd backend && uv run pytest tests/integration/api/test_download.py -v
```

Expected: PASS

**Step 5: Commit**

```bash
git add backend/app/modules/upload/router.py backend/tests/integration/api/test_download.py
git commit -m "Add local GET endpoint for file download in dev mode"
```

---

### Task 5: Add "Unduh File" download button to FileUploadSlot

**Files:**
- Modify: `frontend/src/hooks/useUpload.ts`
- Modify: `frontend/src/components/evaluation/FileUploadSlot.tsx`
- Modify: `frontend/src/components/evaluation/FileUploadSection.tsx`

**Step 1: Add `useDownloadFile` hook**

In `frontend/src/hooks/useUpload.ts`, add at the end:

```typescript
export function useDownloadFile() {
  return useMutation({
    mutationFn: async ({
      brandId,
      fileType,
    }: {
      brandId: number;
      fileType: string;
    }) => {
      const { data, error } = await client.GET(
        '/api/v1/upload/brands/{brand_id}/download/{file_type}',
        { params: { path: { brand_id: brandId, file_type: fileType } } },
      );
      if (error) throw new Error('Failed to get download URL');
      return data as { download_url: string; filename: string };
    },
  });
}
```

**Step 2: Add download button to FileUploadSlot**

In `frontend/src/components/evaluation/FileUploadSlot.tsx`:

- Add `Download` to lucide-react imports
- Add `onDownload?: () => void` and `isDownloading?: boolean` props to `FileUploadSlotProps`
- After the "Unggah Ulang" `<Button>` (line 174), add:

```tsx
{onDownload && (
  <Button
    variant="ghost"
    size="sm"
    className="mt-1 h-7 px-2 text-xs text-green-600 hover:text-green-700"
    onClick={onDownload}
    disabled={isDownloading}
  >
    <Download className="mr-1 size-3" aria-hidden="true" />
    {t('fileUpload.button.download')}
  </Button>
)}
```

**Step 3: Wire up download in FileUploadSection's SlotWrapper**

In `frontend/src/components/evaluation/FileUploadSection.tsx`:

- Import `useDownloadFile` from `../../hooks/useUpload`
- Inside `SlotWrapper`, call `const downloadMutation = useDownloadFile()`
- Add download handler:

```typescript
const handleDownload = useCallback(async () => {
  try {
    const result = await downloadMutation.mutateAsync({
      brandId,
      fileType: config.fileType,
    });
    // Open signed URL in new tab to trigger download
    window.open(result.download_url, '_blank');
  } catch {
    toast.error(t('fileUpload.downloadError'));
  }
}, [brandId, config.fileType, downloadMutation, t]);
```

- Pass `onDownload={existingUpload ? handleDownload : undefined}` and `isDownloading={downloadMutation.isPending}` to `<FileUploadSlot>`

**Step 4: Add translation keys**

Find the i18n translation file and add:
- `fileUpload.button.download`: `"Unduh File"`
- `fileUpload.downloadError`: `"Gagal mengunduh file"`

**Step 5: Manually verify in browser**

- Navigate to evaluation page for a brand with uploaded files
- Verify "Unduh File" button appears next to "Unggah Ulang"
- Click it — should open download URL in new tab

**Step 6: Commit**

```bash
git add frontend/src/hooks/useUpload.ts frontend/src/components/evaluation/FileUploadSlot.tsx frontend/src/components/evaluation/FileUploadSection.tsx
git commit -m "Add Unduh File download button to upload cards"
```

---

### Task 6: Create collapsible FileDownloadSection component (Step 4b)

**Files:**
- Create: `frontend/src/components/evaluation/FileDownloadSection.tsx`
- Create: `frontend/src/components/evaluation/FileDownloadSection.test.tsx`
- Modify: `frontend/src/components/evaluation/EvaluationSections.tsx`

**Step 1: Write test for FileDownloadSection**

Create `frontend/src/components/evaluation/FileDownloadSection.test.tsx`:

```tsx
import { render, screen, fireEvent } from '@testing-library/react';
import { describe, it, expect, vi } from 'vitest';
import { FileDownloadSection } from './FileDownloadSection';
import type { UploadInfo } from '../../hooks/useUpload';

// Mock useTranslation
vi.mock('react-i18next', () => ({
  useTranslation: () => ({
    t: (key: string) => key,
  }),
}));

// Mock useDownloadFile
vi.mock('../../hooks/useUpload', () => ({
  useDownloadFile: () => ({
    mutateAsync: vi.fn().mockResolvedValue({
      download_url: 'https://example.com/download',
      filename: 'test.csv',
    }),
    isPending: false,
  }),
}));

const mockUploads: UploadInfo[] = [
  {
    id: 1,
    brand_id: 1,
    file_type: 'cpc_ad_report',
    filename: 'Brand_report.csv',
    file_size: 1024,
    row_count: 25,
    uploaded_at: '2026-03-10T13:00:00Z',
  },
];

describe('FileDownloadSection', () => {
  it('should render collapsed by default', () => {
    render(<FileDownloadSection brandId={1} uploads={mockUploads} />);
    // Header visible
    expect(screen.getByText(/fileDownload.title/)).toBeInTheDocument();
    // Table not visible
    expect(screen.queryByText('Brand_report.csv')).not.toBeInTheDocument();
  });

  it('should expand when header is clicked', () => {
    render(<FileDownloadSection brandId={1} uploads={mockUploads} />);
    fireEvent.click(screen.getByText(/fileDownload.title/));
    expect(screen.getByText('Brand_report.csv')).toBeInTheDocument();
  });

  it('should not render when no uploads exist', () => {
    const { container } = render(
      <FileDownloadSection brandId={1} uploads={[]} />,
    );
    expect(container.firstChild).toBeNull();
  });
});
```

**Step 2: Run test to verify it fails**

```bash
cd frontend && npx vitest run src/components/evaluation/FileDownloadSection.test.tsx
```

Expected: FAIL — module not found.

**Step 3: Create FileDownloadSection component**

Create `frontend/src/components/evaluation/FileDownloadSection.tsx`:

```tsx
import { useState, useCallback } from 'react';
import { useTranslation } from 'react-i18next';
import { ChevronDown, ChevronUp, Download } from 'lucide-react';
import { Button } from '../ui/button';
import { useDownloadFile, type UploadInfo } from '../../hooks/useUpload';
import { toast } from 'sonner';

interface FileDownloadSectionProps {
  brandId: number;
  uploads: UploadInfo[];
}

export function FileDownloadSection({
  brandId,
  uploads,
}: FileDownloadSectionProps) {
  const { t } = useTranslation();
  const [isExpanded, setIsExpanded] = useState(false);
  const downloadMutation = useDownloadFile();

  const handleDownload = useCallback(
    async (fileType: string) => {
      try {
        const result = await downloadMutation.mutateAsync({
          brandId,
          fileType,
        });
        window.open(result.download_url, '_blank');
      } catch {
        toast.error(t('fileUpload.downloadError'));
      }
    },
    [brandId, downloadMutation, t],
  );

  if (uploads.length === 0) return null;

  return (
    <div className="mt-6">
      <button
        type="button"
        className="flex w-full items-center justify-between rounded-lg bg-muted px-4 py-3"
        onClick={() => setIsExpanded(!isExpanded)}
      >
        <div className="flex items-center gap-2">
          <h4 className="text-base font-semibold text-primary">
            {t('fileDownload.title')}
          </h4>
          <span className="rounded-full bg-primary px-2 py-0.5 text-xs font-medium text-primary-foreground">
            {uploads.length} {t('fileDownload.files')}
          </span>
        </div>
        {isExpanded ? (
          <ChevronUp className="size-5 text-primary" />
        ) : (
          <ChevronDown className="size-5 text-primary" />
        )}
      </button>

      {isExpanded && (
        <div className="mt-2 overflow-hidden rounded-lg border">
          <table className="w-full text-sm">
            <thead className="bg-muted">
              <tr>
                <th className="px-4 py-3 text-left text-xs font-semibold uppercase tracking-wider text-muted-foreground">
                  {t('fileDownload.column.fileType')}
                </th>
                <th className="px-4 py-3 text-left text-xs font-semibold uppercase tracking-wider text-muted-foreground">
                  {t('fileDownload.column.filename')}
                </th>
                <th className="px-4 py-3 text-left text-xs font-semibold uppercase tracking-wider text-muted-foreground">
                  {t('fileDownload.column.size')}
                </th>
                <th className="px-4 py-3 text-left text-xs font-semibold uppercase tracking-wider text-muted-foreground">
                  {t('fileDownload.column.date')}
                </th>
                <th className="px-4 py-3 text-center text-xs font-semibold uppercase tracking-wider text-muted-foreground">
                  {t('fileDownload.column.action')}
                </th>
              </tr>
            </thead>
            <tbody className="divide-y">
              {uploads.map((upload) => (
                <tr key={upload.id}>
                  <td className="px-4 py-3 font-medium">{upload.file_type}</td>
                  <td className="px-4 py-3 text-muted-foreground">
                    {upload.filename}
                  </td>
                  <td className="px-4 py-3 text-muted-foreground">
                    {formatFileSize(upload.file_size)}
                  </td>
                  <td className="px-4 py-3 text-muted-foreground">
                    {new Date(upload.uploaded_at).toLocaleDateString()}
                  </td>
                  <td className="px-4 py-3 text-center">
                    <Button
                      variant="ghost"
                      size="sm"
                      className="text-green-600 hover:text-green-700"
                      onClick={() => handleDownload(upload.file_type)}
                      disabled={downloadMutation.isPending}
                    >
                      <Download className="size-4" />
                    </Button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
}

function formatFileSize(bytes: number): string {
  if (bytes < 1024) return `${bytes} B`;
  if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(0)} KB`;
  return `${(bytes / (1024 * 1024)).toFixed(1)} MB`;
}
```

**Step 4: Run test**

```bash
cd frontend && npx vitest run src/components/evaluation/FileDownloadSection.test.tsx
```

Expected: PASS

**Step 5: Wire into EvaluationSections**

In `frontend/src/components/evaluation/EvaluationSections.tsx`:

- Import `FileDownloadSection` and `useBrandUploads`
- After the `<FileUploadSection>` closing `</section>` (line 211), add:

```tsx
{/* Section 4b: File Downloads */}
<FileDownloadSection
  brandId={brandId}
  uploads={brandUploadsData?.uploads ?? []}
/>
```

- At the top of the component, add the query:
```typescript
const { data: brandUploadsData } = useBrandUploads(brandId);
```

**Step 6: Add translation keys**

Add to the i18n files:
- `fileDownload.title`: `"Step 4b. Download File"`
- `fileDownload.files`: `"files"`
- `fileDownload.column.fileType`: `"Tipe File"`
- `fileDownload.column.filename`: `"Nama File"`
- `fileDownload.column.size`: `"Ukuran"`
- `fileDownload.column.date`: `"Tanggal"`
- `fileDownload.column.action`: `"Aksi"`

**Step 7: Manually verify in browser**

- Evaluation page shows collapsible "Step 4b. Download File" section
- Collapsed by default with file count badge
- Expands to show download table
- Download buttons work

**Step 8: Commit**

```bash
git add frontend/src/components/evaluation/FileDownloadSection.tsx frontend/src/components/evaluation/FileDownloadSection.test.tsx frontend/src/components/evaluation/EvaluationSections.tsx
git commit -m "Add collapsible FileDownloadSection (Step 4b) to evaluation page"
```

---

### Task 7: Update OpenAPI schema types

**Files:**
- Modify: `frontend/src/services/apiClient.ts` (or regenerate types)

**Step 1: Add the download endpoint types**

Ensure the OpenAPI-generated types include the new `GET /api/v1/upload/brands/{brand_id}/download/{file_type}` endpoint. If types are auto-generated:

```bash
cd frontend && npm run generate-api  # or equivalent command
```

If manually maintained, add the path and response type for the download endpoint.

**Step 2: Verify TypeScript compiles**

```bash
cd frontend && npx tsc --noEmit
```

Expected: No errors.

**Step 3: Commit**

```bash
git add frontend/src/services/apiClient.ts
git commit -m "Update OpenAPI types with download endpoint"
```

---

### Task 8: End-to-end verification

**Step 1: Run all backend tests**

```bash
cd backend && uv run pytest -v
```

Expected: All PASS

**Step 2: Run all frontend tests**

```bash
cd frontend && npx vitest run
```

Expected: All PASS

**Step 3: Manual smoke test**

1. Upload a file to any slot → verify file is NOT deleted from storage
2. Click "Unduh File" on the card → browser downloads the file
3. Expand Step 4b → see consolidated table → click download icon → file downloads
4. Re-upload same slot → old file deleted, new file downloadable
5. Verify legacy uploads (without storage_path) show no download button

**Step 4: Final commit (if any fixes needed)**

```bash
git add -A && git commit -m "Fix issues found during e2e verification"
```
