"""ZIP archive processing — extract, sort, merge Excel parts."""

import re
import zipfile
from io import BytesIO

import polars as pl

from app.config import settings
from app.core.exceptions import UploadException
from app.modules.upload.parser import parse_excel

# Regex to extract part number from filenames like "data_part_1_of_3.xlsx"
_PART_PATTERN = re.compile(r"part[_\s]?(\d+)[_\s]?of[_\s]?(\d+)", re.IGNORECASE)


def _extract_part_number(filename: str) -> int:
    """Extract part number from filename, defaulting to 0 if no match."""
    match = _PART_PATTERN.search(filename)
    return int(match.group(1)) if match else 0


def _is_valid_excel(name: str) -> bool:
    """Check if a ZIP entry is a real Excel file (not __MACOSX or temp)."""
    if name.startswith("__MACOSX"):
        return False
    if name.startswith("~$") or name.startswith("."):
        return False
    return name.lower().endswith((".xlsx", ".xls"))


def process_zip(zip_bytes: bytes, file_type: str) -> pl.DataFrame:
    """Extract Excel files from ZIP, sort by part, merge into single DataFrame.

    Args:
        zip_bytes: Raw ZIP file content.
        file_type: The upload file type (determines header_row for mass_update).

    Returns:
        Merged Polars DataFrame from all Excel parts.

    Raises:
        UploadException: UPLOAD_ZIP_NO_EXCEL if no Excel files found,
            UPLOAD_ZIP_STRUCTURE_MISMATCH if parts have different columns,
            UPLOAD_PARSE_FAILED if ZIP is corrupted.
    """
    try:
        zf = zipfile.ZipFile(BytesIO(zip_bytes))
    except zipfile.BadZipFile as e:
        raise UploadException(
            code="UPLOAD_PARSE_FAILED",
            detail="Uploaded ZIP file is corrupted or invalid",
        ) from e

    with zf:
        # Filter to valid Excel entries
        excel_entries = [name for name in zf.namelist() if _is_valid_excel(name)]

        if not excel_entries:
            raise UploadException(
                code="UPLOAD_ZIP_NO_EXCEL",
                detail="ZIP archive contains no Excel files",
            )

        # Zip-bomb guard: reject on entry count / total uncompressed size read from
        # the central directory (ZipInfo.file_size) BEFORE decompressing anything.
        if len(excel_entries) > settings.upload_max_zip_entries:
            raise UploadException(
                code="UPLOAD_TOO_LARGE",
                detail=f"ZIP has too many files (max {settings.upload_max_zip_entries})",
            )
        total_uncompressed = sum(zf.getinfo(name).file_size for name in excel_entries)
        max_uncompressed = settings.upload_max_zip_uncompressed_mb * 1024 * 1024
        if total_uncompressed > max_uncompressed:
            raise UploadException(
                code="UPLOAD_TOO_LARGE",
                detail=f"ZIP contents exceed the {settings.upload_max_zip_uncompressed_mb} MB uncompressed limit",
            )

        # Sort by part number
        excel_entries.sort(key=_extract_part_number)

        header_row = 2 if file_type == "mass_update" else 0
        result_df: pl.DataFrame | None = None
        reference_columns: list[str] | None = None

        for entry_name in excel_entries:
            entry_bytes = zf.read(entry_name)
            df = parse_excel(entry_bytes, header_row=header_row)

            if reference_columns is None:
                reference_columns = df.columns
            elif df.columns != reference_columns:
                raise UploadException(
                    code="UPLOAD_ZIP_STRUCTURE_MISMATCH",
                    detail=(
                        f"Excel parts have different column structures. "
                        f"Expected columns from first part: {reference_columns}, "
                        f"but '{entry_name}' has: {df.columns}"
                    ),
                )

            result_df = df if result_df is None else pl.concat([result_df, df])

        return result_df
