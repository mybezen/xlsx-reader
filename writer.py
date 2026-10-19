"""Penyimpanan dan konversi format file.

Fungsi save_as memungkinkan konversi antara XLSX dan CSV.
"""

from __future__ import annotations

from pathlib import Path

from config import SUPPORTED_EXT
from models import SheetData
from xlsx_io import write_xlsx
from csv_io import write_csv


def save(data: SheetData) -> None:
    """Simpan perubahan ke file sumber asal.

    Jika data berasal dari Google Sheets, panggil write_gsheet.
    Jika tidak ada path sumber, melempar ValueError.
    """
    if data.source == "gsheet":
        from gsheet import write_gsheet
        write_gsheet(data)
        return

    if not data.path:
        raise ValueError("Tidak ada path file sumber. Gunakan 'Simpan sebagai'.")

    ext = Path(data.path).suffix.lower()
    if ext == ".xlsx":
        write_xlsx(data, data.path)
    elif ext == ".csv":
        write_csv(data, data.path)
    else:
        raise ValueError(f"Ekstensi '{ext}' tidak didukung untuk penyimpanan.")


def save_as(data: SheetData, target_path: str) -> None:
    """Simpan data ke path baru (bisa sekaligus konversi format XLSX ↔ CSV).

    Path dan source pada object SheetData akan diperbarui.
    """
    ext = Path(target_path).suffix.lower()
    if ext not in SUPPORTED_EXT:
        raise ValueError(
            f"Ekstensi target '{ext}' tidak didukung. Gunakan: {', '.join(SUPPORTED_EXT)}"
        )

    if ext == ".xlsx":
        write_xlsx(data, target_path)
        data.source = "xlsx"
    else:  # .csv
        write_csv(data, target_path)
        data.source = "csv"

    data.path = target_path
    data.mark_saved()
