"""Shared test helpers for unit tests."""

from io import BytesIO

import polars as pl


def make_excel_bytes(df: pl.DataFrame, *, header_row: int = 0) -> bytes:
    """Write a DataFrame to in-memory Excel bytes.

    For header_row > 0 we prepend blank rows so the real headers land
    at the expected row index using xlsxwriter directly.
    """
    import xlsxwriter

    buf = BytesIO()
    if header_row > 0:
        workbook = xlsxwriter.Workbook(buf)
        worksheet = workbook.add_worksheet()
        for col_idx, col_name in enumerate(df.columns):
            worksheet.write(header_row, col_idx, col_name)
        for row_idx, row_data in enumerate(df.to_dicts()):
            for col_idx, col_name in enumerate(df.columns):
                worksheet.write(header_row + 1 + row_idx, col_idx, row_data[col_name])
        workbook.close()
        return buf.getvalue()

    df.write_excel(buf)
    return buf.getvalue()
