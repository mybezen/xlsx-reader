"""Antarmuka terminal berbasis rich.

Menyediakan fungsi tampilan (tabel berwarna, status, pesan) dan
pembacaan input pengguna yang sudah divalidasi.
"""

from __future__ import annotations

from rich.console import Console
from rich.table import Table

from config import MAX_DISPLAY_ROWS

# Console utama dipakai di seluruh program
console = Console()


# ---------------------------------------------------------------------------
# Tampilan
# ---------------------------------------------------------------------------

def show_message(text: str, kind: str = "info") -> None:
    """Tampilkan pesan berwarna.

    kind : "success" (hijau), "error" (merah), "info" (biru), "warning" (kuning)
    """
    colors = {
        "success": "bold green",
        "error": "bold red",
        "info": "bold blue",
        "warning": "bold yellow",
    }
    console.print(f"[{colors.get(kind, 'white')}]{text}[/]")


def show_status(data) -> None:
    """Tampilkan baris status singkat di bawah judul menu.

    Contoh: File : nilai.xlsx *  | Sheet : Sheet1 | 10 baris | 4 kolom
    """
    if data is None or not data.is_loaded():
        console.print("[dim]File : (belum ada) | 0 baris | 0 kolom[/]")
        return

    nama_file = data.path if data.path else "(Google Sheets)"
    bintang = " *" if data.dirty else ""
    sheet_info = f"  |  Sheet : {data.sheet}" if data.sheet else ""
    console.print(
        f"[bold cyan]File[/] : {nama_file}{bintang}{sheet_info}"
        f"  |  [bold cyan]{data.n_rows}[/] baris"
        f"  |  [bold cyan]{data.n_cols}[/] kolom"
    )


def show_table(data, title: str = "", max_rows: int = MAX_DISPLAY_ROWS) -> None:
    """Tampilkan data sebagai tabel berwarna dengan kolom nomor baris (#).

    Jika baris lebih banyak dari max_rows, hanya bagian awal yang ditampilkan
    beserta catatan jumlah baris yang tersembunyi.
    """
    if data is None or not data.is_loaded():
        show_message("Belum ada data. Buka file terlebih dahulu.", "warning")
        return

    tabel = Table(title=title or None, show_lines=False)
    tabel.add_column("#", style="bold yellow", justify="right", width=4)

    for header in data.headers:
        tabel.add_column(str(header), style="white", overflow="fold")

    # Pastikan lebar baris seragam dengan jumlah kolom
    data.ensure_width()
    tampil = data.rows[:max_rows]

    for i, row in enumerate(tampil):
        tabel.add_row(str(i + 1), *[str(v) for v in row])

    console.print(tabel)

    if data.n_rows > max_rows:
        console.print(
            f"[dim]{max_rows} dari {data.n_rows} baris ditampilkan "
            f"(terpotong untuk kepasstasan terminal)[/]"
        )
    elif data.n_rows == 0:
        console.print("[dim](tidak ada baris data)[/]")


# ---------------------------------------------------------------------------
# Input tervalidasi
# ---------------------------------------------------------------------------

def ask_text(prompt: str, allow_empty: bool = True) -> str:
    """Minta input teks dari pengguna.

    allow_empty=False → pengguna harus mengetik sesuatu (tidak boleh kosong).
    """
    while True:
        value = console.input(f"[bold]{prompt}[/] ").strip()
        if value or allow_empty:
            return value
        show_message("Input tidak boleh kosong.", "warning")


def ask_int(prompt: str, min_val: int | None = None, max_val: int | None = None) -> int:
    """Minta input bilangan bulat, diulang sampai valid."""
    while True:
        raw = console.input(f"[bold]{prompt}[/] ").strip()
        try:
            num = int(raw)
        except ValueError:
            show_message(f"'{raw}' bukan angka. Coba lagi.", "error")
            continue
        if min_val is not None and num < min_val:
            show_message(f"Angka minimal {min_val}.", "error")
            continue
        if max_val is not None and num > max_val:
            show_message(f"Angka maksimal {max_val}.", "error")
            continue
        return num


def ask_row_numbers(prompt: str, max_val: int) -> list[int]:
    """Minta daftar nomor baris, dipisah koma, misalnya '2,4,7'.

    Mengembalikan list indeks 0-based yang sudah tervalidasi.
    Baris kosong / non-angka diabaikan.
    """
    raw = console.input(f"[bold]{prompt}[/] ").strip()
    if not raw:
        return []

    result: list[int] = []
    for bagian in raw.split(","):
        bagian = bagian.strip()
        if not bagian:
            continue
        try:
            num = int(bagian)
        except ValueError:
            show_message(f"'{bagian}' diabaikan (bukan angka).", "warning")
            continue
        if 1 <= num <= max_val:
            result.append(num - 1)  # konversi ke indeks 0-based
        else:
            show_message(f"Nomor {num} di luar jangkauan (1-{max_val}), diabaikan.", "warning")
    return result


def confirm(prompt: str) -> bool:
    """Minta konfirmasi y/n, mengembalikan True jika pengguna menjawab y/Y."""
    jawaban = console.input(f"[bold]{prompt}[/] (y/n): ").strip().lower()
    return jawaban in ("y", "ya", "yes")
