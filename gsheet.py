# Integrasi Google Sheets menggunakan gspread OAuth (user credentials).
#
# Cara pakai:
# 1. Buat proyek Google Cloud Console → aktifkan Google Sheets API & Drive API
# 2. Buat OAuth 2.0 Client ID (Desktop app) → unduh file JSON → simpan di credentials/credentials.json
# 3. Jalankan program, browser akan buka untuk autentikasi pertama kali
# 4. Token disimpan otomatis di credentials/authorized_user.json (sudah di .gitignore)

from __future__ import annotations

from config import CREDENTIALS_DIR
from models import SheetData


def _get_client():
    import gspread

    creds_file = CREDENTIALS_DIR / "credentials.json"
    token_file = CREDENTIALS_DIR / "authorized_user.json"

    if not creds_file.exists():
        raise FileNotFoundError(
            f"File OAuth credentials tidak ditemukan: {creds_file}\n"
            "Pastikan file JSON dari Google Cloud Console (OAuth Client ID) "
            "sudah disalin ke folder credentials/ dengan nama credentials.json"
        )

    return gspread.oauth(
        credentials_filename=str(creds_file),
        authorized_user_filename=str(token_file),
    )


def list_worksheets(spreadsheet_key: str) -> list[str]:

    client = _get_client()
    spreadsheet = client.open_by_key(spreadsheet_key)
    return [ws.title for ws in spreadsheet.worksheets()]


def load_gsheet(spreadsheet_key: str, worksheet_name: str | None = None) -> SheetData:

    client = _get_client()
    spreadsheet = client.open_by_key(spreadsheet_key)

    if worksheet_name:
        ws = spreadsheet.worksheet(worksheet_name)
    else:
        ws = spreadsheet.sheet1

    # Ambil semua nilai (termasuk header)
    all_values = ws.get_all_values()

    if not all_values:
        return SheetData(headers=[], rows=[], source="gsheet")

    headers = all_values[0]
    rows = all_values[1:]

    return SheetData(
        headers=headers,
        rows=rows,
        path=spreadsheet_key,
        sheet=ws.title,
        source="gsheet",
    )


def write_gsheet(data: SheetData, spreadsheet_key: str | None = None) -> None:
    key = spreadsheet_key or data.path
    if not key:
        raise ValueError("Tidak ada spreadsheet key. Berikan key atau pastikan data berasal dari Google Sheets.")

    client = _get_client()
    spreadsheet = client.open_by_key(key)

    sheet_name = data.sheet if data.sheet else "Sheet1"

    # Cari atau buat worksheet
    try:
        ws = spreadsheet.worksheet(sheet_name)
    except Exception:
        ws = spreadsheet.add_worksheet(title=sheet_name, rows=100, cols=20)

    # Bersihkan isi lama
    ws.clear()

    # Tulis data baru
    data.ensure_width()
    all_values = [data.headers] + data.rows
    ws.update(all_values)

    data.mark_saved()
