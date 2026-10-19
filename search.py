"""Pencarian dan penyaringan data pada SheetData.

Memungkinkan pencarian kata kunci di semua kolom atau kolom tertentu.
"""

from __future__ import annotations

from models import SheetData


def search_rows(
    data: SheetData, keyword: str, column_name: str | None = None
) -> SheetData:
    """Saring baris data yang mengandung keyword.

    - If column_name diberikan: cari hanya di kolom tersebut.
    - If column_name None: cari di semua kolom.
    - Pencarian case-insensitive (tidak membedakan huruf besar/kecil).

    Mengembalikan SheetData baru (pencarian tidak mengubah data asli di memori).
    """
    keyword_lower = keyword.lower()
    matched_rows: list[list[str]] = []

    if column_name and column_name in data.headers:
        col_idx = data.headers.index(column_name)
        for row in data.rows:
            if col_idx < len(row) and keyword_lower in str(row[col_idx]).lower():
                matched_rows.append(row)
    else:
        # Cari di semua kolom
        for row in data.rows:
            if any(keyword_lower in str(cell).lower() for cell in row):
                matched_rows.append(row)

    # Buat SheetData hasil filter (bersifat read-only / tidak dirty)
    result = SheetData(
        headers=list(data.headers),
        rows=matched_rows,
        path=data.path,
        sheet=data.sheet,
        source=data.source,
    )
    result.dirty = False
    return result


def get_column_names(data: SheetData) -> list[str]:
    """Ambil daftar nama kolom untuk bantuan autocompletion/pilihan."""
    return list(data.headers)
