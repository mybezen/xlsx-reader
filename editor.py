# Manipulasi data di memori: add/edit/delete rows & columns.

# Semua fungsi mengubah SheetData dan menandainya dirty=True
# agar pengguna ingat harus menyimpan setelah mengedit.

from __future__ import annotations

from models import SheetData


def add_row(data: SheetData, row: list[str]) -> None:
    data.ensure_width()
    data.rows.append(row[: data.n_cols])
    data.mark_dirty()


def edit_cell(data: SheetData, row_idx: int, col_idx: int, value: str) -> bool:

    row = data.get_row(row_idx)
    if row is None:
        return False

    if col_idx < 0 or col_idx >= data.n_cols:
        return False

    row[col_idx] = value
    data.mark_dirty()
    return True


def delete_rows(data: SheetData, row_numbers: list[int]) -> int:
    idx_0based = [r - 1 for r in row_numbers]
    return data.delete_row_indices(idx_0based)

def add_column(data: SheetData, name: str, default: str = "") -> None:
    data.add_column(name, default)

def edit_row(data: SheetData, row_idx: int, new_row: list[str]) -> bool:
    if data.set_row(row_idx, new_row):
        return True
    return False

def get_cell_reference(data: SheetData, row_number: int, col_number: int) -> str | None:
    idx_0r = row_number - 1
    idx_0c = col_number - 1
    row = data.get_row(idx_0r)
    if row is None:
        return None
    if idx_0c >= len(row):
        return None
    return row[idx_0c]


def find_row_index(data: SheetData, keyword: str, col_start: int = 0) -> int | None:
    for i, row in enumerate(data.rows):
        for j in range(col_start, min(len(row), data.n_cols)):
            if keyword.lower() in str(row[j]).lower():
                return i
    return None