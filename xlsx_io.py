"""Modul baca dan tulis file XLSX menggunakan openpyxl.

Konsep kunci:
- workbook → seluruh file XLSX
- sheet → satu halaman kerja (misalnya Sheet1)
- baris → antara 0 dan 99,999
- sel → kosong atau berisi nilai teks/angka
"""

from __future__ import annotations

import os
from pathlib import Path

from openpyxl import load_workbook
from openpyxl.utils import get_column_letter

from config import BASE_DIR
from models import SheetData


def list_xlsx_sheets(file_path: str) -> list[str]:
    """Ambil daftar nama sheet dalam file XLSX.

    Akan melempar FileNotFoundError jika file tidak ada.
    """
    workbook = load_workbook(file_path, read_only=True, data_only=True)
    sheet_names = workbook.sheetnames
    workbook.close()
    return sheet_names


def load_xlsx(file_path: str, sheet_name: str | None = None) -> SheetData:
    """Membaca file XLSX menjadi SheetData di memori.

    Jika sheet_name diberikan, akses langsung ke sheet tersebut.
    Jika None, gunakan sheet pertama.
    Mengembalikan SheetData dengan informasi path dan source "xlsx".
    """
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"File XLSX tidak ditemukan: {file_path}")

    wb = load_workbook(file_path, read_only=True, data_only=True)

    try:
        if sheet_name in wb.sheetnames:
            ws = wb[sheet_name]
        else:
            ws = wb.active

        # Header (baris pertama)
        header_row = next(ws.iter_rows(values_only=True))
        headers = [str(cell if cell is not None else "") for cell in header_row]

        # Baris data (mulai dari baris kedua)
        rows: list[list[str]] = []
        for row_cells in ws.iter_rows(min_row=2, values_only=True):
            row = [str(cell if cell is not None else "") for cell in row_cells]
            rows.append(row)

        sheet_data = SheetData(
            headers=headers,
            rows=rows,
            path=file_path,
            sheet=ws.title,
            source="xlsx",
        )
        return sheet_data

    finally:
        wb.close()


def write_xlsx(data: SheetData, file_path: str) -> None:
    """Menyimpan SheetData menjadi file XLSX.

    Jika file sudah ada, ditimpa (overwrite). Pastikan file tidak
    dibuka di Excel sebelum menyimpan.
    """
    data.ensure_width()

    wb = load_workbook()
    if os.path.exists(file_path):
        wb = load_workbook(file_path, read_only=False)

    sheet_name = data.sheet if data.sheet else "Sheet"
    if sheet_name in wb.sheetnames:
        ws = wb[sheet_name]
    else:
        ws = wb.create_sheet(title=sheet_name)

    # Tulis header
    for i, header in enumerate(data.headers, start=1):
        ws.cell(row=1, column=i, value=header)

    # Tulis baris data
    for row_idx, row_data in enumerate(data.rows, start=2):
        for col_idx, value in enumerate(row_data, start=1):
            ws.cell(row=row_idx, column=col_idx, value=value)

    wb.save(file_path)
    data.mark_saved()


def validate_xlsx_path(path: str) -> str:
    """Cek apakah path valid untuk file XLSX."""
    p = Path(path)
    if not p.exists():
        raise FileNotFoundError(f"File tidak ditemukan: {path}")
    if p.suffix.lower() != ".xlsx":
        raise ValueError(f"Hanya file XLSX yang didukung. Ekstensi: {p.suffix}")
    return str(p)