# File Download Feature Design

## Overview

Keep original uploaded files in storage (instead of deleting after processing) and allow users to download them via signed URLs. Download access in two places: per-card in Step 4 and a consolidated table in Step 4b.

## Design Decisions

| Decision | Choice | Rationale |
|----------|--------|-----------|
| Download method | Signed URL from GCS | Reuses existing upload infrastructure, no backend load |
| File retention | Keep until replaced | Mirrors existing upsert behavior, no unbounded growth |
| Filename format | Standardized (`{brand}_{file_type}.{ext}`) | Consistent naming for users managing multiple brands |
| UI placement | In-card button + consolidated table | Quick access per slot + full overview below |
| Step 4b visibility | Collapsible accordion, hidden by default | Keeps page clean; expand on demand |

## Backend Changes

### 1. Stop deleting files after processing

In `upload/service.py`, remove the file cleanup step after successful processing. When a new file is uploaded for the same slot (upsert), delete the **old** file from storage before storing the new one.

### 2. Add `storage_path` column to `brand_uploads`

New migration adding `storage_path TEXT` column to `brand_uploads` table. Populated during upload processing with the GCS/local path (e.g. `uploads/{upload_id}/{filename}`). Required so the download endpoint knows where to find the file.

### 3. New endpoint: `GET /api/v1/upload/brands/{brand_id}/download/{file_type}`

- Looks up `brand_uploads` by `brand_id` + `file_type`
- Generates a signed download URL from GCS (or local equivalent)
- Returns `{ download_url, filename }` where filename is standardized: `{brand_name}_{file_type}.{ext}`
- 404 if no upload exists for that slot

## Frontend Changes

### 4. Download button in each upload card (Step 4)

- When a file is uploaded (card shows "File berhasil diunggah"), show a green "Unduh File" link with download icon
- Placed next to the existing "Unggah Ulang" button
- Clicking calls the download endpoint, then opens the signed URL to trigger browser download

### 5. New `FileDownloadSection` component (Step 4b)

- Rendered below `FileUploadSection` in `EvaluationSections.tsx`
- **Collapsible accordion, hidden (collapsed) by default**
- Header shows "Step 4b. Download File" with file count badge and chevron icon
- Clicking the header toggles the table visibility (React `useState`)
- Table with columns: Tipe File, Nama File (standardized), Ukuran, Tanggal, Aksi
- For each uploaded file: shows data and green download icon button
- For files not yet uploaded: row is omitted or shows disabled state

## Storage Behavior

- Files persist until replaced by a new upload for the same slot
- On re-upload: old file deleted from storage -> new file stored -> old DB record upserted
- Local dev: files in `/tmp/aha_sicu_uploads` follow same behavior

## No changes to

- Upload flow (signed URL -> direct upload -> process)
- Parsing logic
- Calculator execution
- Evaluation scoring

## Visual Reference

See `pencil-new.pen` for the mockup showing both Step 4 (with download buttons) and Step 4b (consolidated download table).
