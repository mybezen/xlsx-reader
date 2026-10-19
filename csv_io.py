# Modul baca dan tulis CSV.

# Fitur:
# - Deteksi otomatis pemisah (delimiter) via csv.Sniffer
# - Coba beberapa encoding berurutan (UTF-8, UTF-8-SIG, Latin-1)
# - Menangani baris kosong dan baris dengan panjang tidak seragam

from __future__ import annotations

import csv
import os
from pathlib import Path
from typing import Any

from config import BASE_DIR, DELIMITERS, ENCODINGS
from models import SheetData


def read_text_with_fallback(file_path: str) -> str:
    # Baca isi file teks dengan fallback encoding.

    # Mencoba encoding dari ENCODINGS berurutan.
    # Mengembalikan string teks dari encoding yang berhasil.
    for enc in ENCODINGS:
        try:
            with open(file_path, "r", encoding=enc, newline="") as f:
                return f.read()
        except UnicodeDecodeError:
            continue
    # Latin-1 selalu berhasil (baca byte demi byte)
    with open(file_path, "r", encoding="latin-1", newline="") as f:
        return f.read()


def detect_delimiter(text: str) -> str:
    # Deteksi pemisah CSV menggunakan csv.Sniffer.

    # Jika gagal, fallback ke koma.
    if not text.strip():
        return ","
    try:
        sniffer = csv.Sniffer()
        dialect = sniffer.sniff(text[:2048], delimiters=DELIMITERS)
        return dialect.delimiter
    except Exception:
        return ","


def load_csv(file_path: str, delimiter: str | None = None) -> SheetData:
    # Membaca file CSV menjadi SheetData.

    # - Jika delimiter None, deteksi otomatis.
    # - Encoding dicoba berurutan (UTF-8 → UTF-8-SIG → Latin-1).
    # - Header diambil dari baris pertama, baris selanjutnya jadi data.
    # - Baris kosong diabaikan.
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"File CSV tidak ditemukan: {file_path}")

    # Baca teks mentah dengan fallback encoding
    raw_text = read_text_with_fallback(file_path)

    # Deteksi delimiter
    if delimiter is None:
        delimiter = detect_delimiter(raw_text)

    # Parse dengan csv.reader
    reader = csv.reader(raw_text.splitlines(), delimiter=delimiter)

    # Ambil header
    headers: list[str] = []
    rows: list[list[str]] = []
    try:
        first_row = next(reader)
        headers = [str(cell) for cell in first_row]
    except StopIteration:
        headers = []
        rows = []
        return SheetData(headers=[], rows=[], path=file_path, source="csv")

    # Ambil data
    for row in reader:
        if not any(cell.strip() for cell in row):
            continue  # lewati baris sepenuhnya kosong
        rows.append([str(cell) for cell in row])

    return SheetData(headers=headers, rows=rows, path=file_path, source="csv")


def write_csv(data: SheetData, file_path: str, delimiter: str = ",") -> None:
    # Menulis SheetData ke file CSV.

    # Jika file sudah ada, ditimpa. Encoding UTF-8-SIG agar Excel Windows
    # membaca karakter non-ASCII dengan benar.
    data.ensure_width()
    with open(file_path, "w", encoding="utf-8-sig", newline="") as f:
        writer = csv.writer(f, delimiter=delimiter)
        writer.writerow(data.headers)
        for row in data.rows:
            writer.writerow(row)
    data.mark_saved()


def validate_csv_path(path: str) -> str:
    # Cek apakah path valid untuk file CSV.
    p = Path(path)
    if not p.exists():
        raise FileNotFoundError(f"File tidak ditemukan: {path}")
    if p.suffix.lower() != ".csv":
        raise ValueError(f"Hanya file CSV yang didukung. Ekstensi: {p.suffix}")
    return str(p)