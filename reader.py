"""Router pembuka file berdasarkan ekstensi.

Fungsi open_file menentukan apakah file adalah XLSX atau CSV
dan meneruskan ke loader yang tepat.
"""

from __future__ import annotations

from pathlib import Path

from config import SUPPORTED_EXT
from models import SheetData
from xlsx_io import list_xlsx_sheets, load_xlsx
from csv_io import load_csv
import ui


def open_file(file_path: str, sheet_name: str | None = None) -> SheetData:
    """Buka file sesuai ekstensinya dan kembalikan SheetData.

    Melempar ValueError jika ekstensi tidak didukung.
    """
    ext = Path(file_path).suffix.lower()
    if ext not in SUPPORTED_EXT:
        raise ValueError(
            f"Ekstensi '{ext}' tidak didukung. Gunakan: {', '.join(SUPPORTED_EXT)}"
        )

    if ext == ".xlsx":
        return load_xlsx(file_path, sheet_name)
    else:  # .csv
        return load_csv(file_path)


def choose_sheet(file_path: str) -> str | None:
    """Minta pengguna memilih sheet dari file XLSX.

    Menampilkan daftar sheet, lalu meminta pilihan nomor.
    Mengembalikan nama sheet yang dipilih, atau None jika hanya satu sheet.
    """
    from xlsx_io import list_xlsx_sheets

    sheets = list_xlsx_sheets(file_path)
    if not sheets:
        return None
    if len(sheets) == 1:
        return sheets[0]

    ui.console.print("[bold cyan]Sheet yang tersedia:[/]")
    for i, name in enumerate(sheets, start=1):
        ui.console.print(f"  {i}. {name}")

    pilihan = ui.ask_int("Pilih nomor sheet:", min_val=1, max_val=len(sheets))
    return sheets[pilihan - 1]
