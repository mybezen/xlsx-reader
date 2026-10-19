# Konstanta global untuk aplikasi Spreadsheet CLI.

# File ini menyimpan konfigurasi yang dipakai bersama oleh modul lain:
# ekstensi file yang didukung, daftar encoding yang dicoba saat membaca CSV,
# dan lokasi file kunci service account Google.


from pathlib import Path

# Direktori proyek ini (folder tempat config.py berada)
BASE_DIR = Path(__file__).resolve().parent

# Folder default untuk data contoh dan kunci Google
DATA_DIR = BASE_DIR / "data"
CREDENTIALS_DIR = BASE_DIR / "credentials"

# Ekstensi file yang didukung program
SUPPORTED_EXT = {".xlsx", ".csv"}

# Daftar encoding yang dicoba berurutan saat membaca CSV.
# UTF-8 dicoba dulu, lalu Latin-1 (selalu berhasil) sebagai cadangan.
ENCODINGS = ["utf-8", "utf-8-sig", "latin-1"]

# Kandidat pemisah (delimiter) CSV saat deteksi otomatis
DELIMITERS = [",", ";", "\t", "|"]

# Lokasi file kunci service account Google (JSON)
CREDENTIALS_PATH = CREDENTIALS_DIR / "service_account.json"

# Batas jumlah baris yang ditampilkan sekaligus di terminal.
# Baris lebih dari ini akan dipotong (agar tabel tidak terpotong).
MAX_DISPLAY_ROWS = 50
