from __future__ import annotations

import os

import ui
import editor
import search
import writer
from editor import add_row, edit_cell, delete_rows, add_column
from models import SheetData
from reader import open_file, choose_sheet
from search import search_rows
from writer import save, save_as
from xlsx_io import list_xlsx_sheets, load_xlsx


# State global program: data yang sedang dibuka
current: SheetData | None = None


# Tampilan menu

MENU_ITEMS = [
    ("1", "Buka file (XLSX / CSV)"),
    ("2", "Buka Google Sheets"),
    ("3", "Tampilkan data"),
    ("4", "Pilih sheet"),
    ("5", "Tambah baris"),
    ("6", "Edit sel"),
    ("7", "Hapus baris"),
    ("8", "Tambah kolom"),
    ("9", "Cari / filter"),
    ("10", "Simpan"),
    ("11", "Simpan sebagai (konversi)"),
    ("12", "Simpan ke Google Sheets"),
    ("0", "Keluar"),
]


def show_menu() -> None:
    ui.console.print("[bold cyan]=== Spreadsheet CLI ===[/]")
    ui.show_status(current)
    ui.console.print()
    for key, label in MENU_ITEMS:
        ui.console.print(f" [bold]{key:>2}.[/] {label}")
    ui.console.print()


# ---------------------------------------------------------------------------
# Loop utama
# ---------------------------------------------------------------------------

def run_loop() -> None:
    global current
    while True:
        show_menu()
        pilihan = ui.console.input("[bold]Pilih menu:[/] ").strip()

        if pilihan == "0":
            if _exit_with_unsaved_check():
                ui.show_message("Keluar. Sampai jumpa!", "info")
                break
            continue

        # Validasi angka menu
        if not pilihan.isdigit():
            ui.show_message(f"'{pilihan}' bukan menu yang valid. Coba lagi.", "error")
            continue
        nomor = int(pilihan)
        if nomor < 0 or nomor > 12:
            ui.show_message(f"Menu {nomor} tidak ada. Pilih 0-12.", "error")
            continue

        try:
            handle_choice(pilihan)
        except KeyboardInterrupt:
            ui.show_message("Dibatalkan.", "warning")
        except Exception as exc:  # Tangkap error agar program tidak crash
            ui.show_message(f"Terjadi kesalahan: {exc}", "error")

        ui.console.print()


def _exit_with_unsaved_check() -> bool:
    if current is None or not current.dirty:
        return True

    ui.show_message("Ada perubahan yang belum disimpan!", "warning")
    if ui.confirm("Simpan sebelum keluar?"):
        try:
            save(current)
            ui.show_message("Berhasil disimpan.", "success")
            return True
        except Exception as exc:
            ui.show_message(f"Gagal menyimpan: {exc}", "error")
            return False
    if ui.confirm("Keluar tanpa menyimpan?"):
        return True
    return False

# Penanganan pilihan menu

def handle_choice(choice: str) -> None:
    global current

    if choice == "1":
        _menu_open_file()
    elif choice == "2":
        _menu_open_gsheet()
    elif choice == "3":
        _menu_show()
    elif choice == "4":
        _menu_choose_sheet()
    elif choice == "5":
        _menu_add_row()
    elif choice == "6":
        _menu_edit_cell()
    elif choice == "7":
        _menu_delete_rows()
    elif choice == "8":
        _menu_add_column()
    elif choice == "9":
        _menu_search()
    elif choice == "10":
        _menu_save()
    elif choice == "11":
        _menu_save_as()
    elif choice == "12":
        _menu_save_gsheet()


# ---------------------------------------------------------------------------
# Aksi menu satu per satu
# ---------------------------------------------------------------------------

def _menu_open_file() -> None:
    global current

    if current is not None and current.dirty:
        if not ui.confirm("Ada perubahan belum disimpan. Buka file baru anyway?"):
            return

    path = ui.ask_text("Masukkan path file (.xlsx / .csv):", allow_empty=False)
    path = path.strip('"').strip("'")  # hilangkan tanda kutip dari drag-and-drop

    ext = os.path.splitext(path)[1].lower()
    if ext not in (".xlsx", ".csv"):
        ui.show_message(f"Ekstensi '{ext}' tidak didukung. Gunakan .xlsx atau .csv", "error")
        return

    if not os.path.exists(path):
        ui.show_message(f"File tidak ditemukan: {path}", "error")
        return

    sheet_name = None
    if ext == ".xlsx":
        sheets = list_xlsx_sheets(path)
        if len(sheets) > 1:
            ui.console.print(f"[bold cyan]File memiliki {len(sheets)} sheet:[/]")
            for i, name in enumerate(sheets, start=1):
                ui.console.print(f"  {i}. {name}")
            pilihan = ui.ask_int("Pilih nomor sheet:", min_val=1, max_val=len(sheets))
            sheet_name = sheets[pilihan - 1]
        elif sheets:
            sheet_name = sheets[0]

    current = open_file(path, sheet_name)
    ui.show_message(f"Berhasil membuka: {path}", "success")
    ui.show_table(current)


def _menu_open_gsheet() -> None:
    global current

    try:
        from gsheet import load_gsheet, list_worksheets
    except ImportError:
        ui.show_message("Library gspread tidak terpasang. Jalankan: pip install gspread", "error")
        return

    key = ui.ask_text("Masukkan Spreadsheet ID / URL:", allow_empty=False)

    # Jika pengguna menempel URL, ambil ID-nya
    if "/" in key:
        from urllib.parse import urlparse
        parts = [p for p in urlparse(key).path.split("/") if p]
        if "d" in parts:
            key = parts[parts.index("d") + 1]

    try:
        worksheets = list_worksheets(key)
    except FileNotFoundError as exc:
        ui.show_message(str(exc), "error")
        return
    except Exception as exc:
        ui.show_message(f"Gagal membuka spreadsheet: {exc}", "error")
        return

    sheet_name = None
    if len(worksheets) > 1:
        ui.console.print("[bold cyan]Worksheet tersedia:[/]")
        for i, name in enumerate(worksheets, start=1):
            ui.console.print(f"  {i}. {name}")
        pilihan = ui.ask_int("Pilih nomor worksheet:", min_val=1, max_val=len(worksheets))
        sheet_name = worksheets[pilihan - 1]
    elif worksheets:
        sheet_name = worksheets[0]

    current = load_gsheet(key, sheet_name)
    ui.show_message("Berhasil membuka Google Sheets.", "success")
    ui.show_table(current)


def _menu_show() -> None:
    if current is None:
        ui.show_message("Belum ada file yang dibuka.", "warning")
        return
    ui.show_table(current)


def _menu_choose_sheet() -> None:
    global current

    if current is None:
        ui.show_message("Belum ada file yang dibuka.", "warning")
        return
    if current.source != "xlsx":
        ui.show_message("Pilih sheet hanya berlaku untuk file XLSX.", "warning")
        return

    try:
        sheets = list_xlsx_sheets(current.path)
    except Exception as exc:
        ui.show_message(f"Gagal membaca daftar sheet: {exc}", "error")
        return

    if len(sheets) <= 1:
        ui.show_message("File ini hanya punya satu sheet.", "info")
        return

    ui.console.print("[bold cyan]Sheet tersedia:[/]")
    for i, name in enumerate(sheets, start=1):
        penanda = " [green](aktif)[/]" if name == current.sheet else ""
        ui.console.print(f"  {i}. {name}{penanda}")

    pilihan = ui.ask_int("Pilih nomor sheet:", min_val=1, max_val=len(sheets))
    nama = sheets[pilihan - 1]
    current = load_xlsx(current.path, nama)
    ui.show_message(f"Pindah ke sheet: {nama}", "success")
    ui.show_table(current)


def _menu_add_row() -> None:
    if current is None:
        ui.show_message("Belum ada file yang dibuka.", "warning")
        return

    ui.console.print(f"[bold cyan]Masukkan {current.n_cols} nilai kolom:[/]")
    nilai: list[str] = []
    for header in current.headers:
        nilai.append(ui.ask_text(f"  {header}:"))

    add_row(current, nilai)
    ui.show_message("Baris baru ditambahkan (belum disimpan).", "success")
    ui.show_table(current)


def _menu_edit_cell() -> None:
    if current is None:
        ui.show_message("Belum ada file yang dibuka.", "warning")
        return
    if current.n_rows == 0:
        ui.show_message("Tidak ada baris data untuk diedit.", "warning")
        return

    ui.show_table(current)
    baris = ui.ask_int("Nomor baris (1-%d):" % current.n_rows, min_val=1, max_val=current.n_rows)

    ui.console.print("[bold cyan]Kolom tersedia:[/]")
    for i, header in enumerate(current.headers, start=1):
        ui.console.print(f"  {i}. {header}")
    kolom = ui.ask_int("Nomor kolom (1-%d):" % current.n_cols, min_val=1, max_val=current.n_cols)

    lama = editor.get_cell_reference(current, baris, kolom)
    ui.console.print(f"Nilai lama: [yellow]{lama}[/]")
    baru = ui.ask_text("Nilai baru:")

    if edit_cell(current, baris - 1, kolom - 1, baru):
        ui.show_message(f"Sel [{baris},{kolom}] berhasil diubah (belum disimpan).", "success")
    else:
        ui.show_message("Gagal mengubah sel. Cek nomor baris/kolom.", "error")


def _menu_delete_rows() -> None:
    if current is None:
        ui.show_message("Belum ada file yang dibuka.", "warning")
        return
    if current.n_rows == 0:
        ui.show_message("Tidak ada baris data untuk dihapus.", "warning")
        return

    ui.show_table(current)
    nomor = ui.ask_row_numbers(
        "Nomor baris yang dihapus (pisahkan koma, mis. 2,4,7):", current.n_rows
    )
    if not nomor:
        ui.show_message("Tidak ada nomor valid yang dimasukkan.", "warning")
        return

    info = ", ".join(str(n + 1) for n in sorted(nomor))
    if not ui.confirm(f"Yakin hapus baris {info}?"):
        ui.show_message("Dibatalkan.", "info")
        return

    jumlah = delete_rows(current, [n + 1 for n in nomor])
    ui.show_message(f"{jumlah} baris dihapus (belum disimpan).", "success")
    ui.show_table(current)


def _menu_add_column() -> None:
    if current is None:
        ui.show_message("Belum ada file yang dibuka.", "warning")
        return

    nama = ui.ask_text("Nama kolom baru:", allow_empty=False)
    nilai_default = ui.ask_text("Nilai default untuk semua baris (boleh kosong):")
    add_column(current, nama, nilai_default)
    ui.show_message(f"Kolom '{nama}' ditambahkan (belum disimpan).", "success")
    ui.show_table(current)


def _menu_search() -> None:
    if current is None:
        ui.show_message("Belum ada file yang dibuka.", "warning")
        return
    if current.n_rows == 0:
        ui.show_message("Tidak ada data untuk dicari.", "warning")
        return

    ui.console.print("[bold cyan]Pilih cara pencarian:[/]")
    ui.console.print("  1. Semua kolom")
    for i, header in enumerate(current.headers, start=2):
        ui.console.print(f"  {i}. Kolom '{header}'")
    pilihan = ui.ask_int("Pilih:", min_val=1, max_val=len(current.headers) + 1)

    kolom = None if pilihan == 1 else current.headers[pilihan - 2]
    keyword = ui.ask_text("Kata kunci:", allow_empty=False)

    hasil = search_rows(current, keyword, kolom)
    if hasil.n_rows == 0:
        ui.show_message(f"Tidak ada baris yang cocok dengan '{keyword}'.", "warning")
        return

    ui.show_message(f"Ditemukan {hasil.n_rows} baris.", "success")
    judul = f"Hasil pencarian '{keyword}'"
    if kolom:
        judul += f" di kolom '{kolom}'"
    ui.show_table(hasil, title=judul)


def _menu_save() -> None:
    if current is None:
        ui.show_message("Belum ada file yang dibuka.", "warning")
        return

    try:
        save(current)
        ui.show_message(f"Berhasil disimpan: {current.path}", "success")
    except PermissionError:
        ui.show_message(
            "Gagal menyimpan: file mungkin sedang dibuka di Excel. "
            "Tutup Excel dulu lalu coba lagi.",
            "error",
        )
    except Exception as exc:
        ui.show_message(f"Gagal menyimpan: {exc}", "error")


def _menu_save_as() -> None:
    if current is None:
        ui.show_message("Belum ada file yang dibuka.", "warning")
        return

    ui.console.print("[bold cyan]Konversi / simpan sebagai:[/]")
    ui.console.print("  Format didukung: .xlsx, .csv")
    target = ui.ask_text("Path tujuan (mis. data/baru.xlsx):", allow_empty=False)

    ext = os.path.splitext(target)[1].lower()
    if ext not in (".xlsx", ".csv"):
        ui.show_message("Ekstensi harus .xlsx atau .csv", "error")
        return

    if os.path.exists(target) and not ui.confirm(f"File '{target}' sudah ada. Timpa?"):
        ui.show_message("Dibatalkan.", "info")
        return

    try:
        save_as(current, target)
        ui.show_message(f"Berhasil disimpan sebagai: {target}", "success")
    except PermissionError:
        ui.show_message(
            "Gagal menyimpan: file mungkin sedang dibuka di Excel. Tutup dulu.",
            "error",
        )
    except Exception as exc:
        ui.show_message(f"Gagal menyimpan: {exc}", "error")


def _menu_save_gsheet() -> None:
    if current is None:
        ui.show_message("Belum ada file yang dibuka.", "warning")
        return

    try:
        from gsheet import write_gsheet
    except ImportError:
        ui.show_message("Library gspread tidak terpasang. Jalankan: pip install gspread", "error")
        return

    if current.source == "gsheet":
        key = current.path
        ui.console.print(f"[dim]Menyimpan ke spreadsheet yang sama: {key}[/]")
    else:
        key = ui.ask_text("Spreadsheet ID / URL tujuan:", allow_empty=False)
        if "/" in key:
            from urllib.parse import urlparse
            parts = [p for p in urlparse(key).path.split("/") if p]
            if "d" in parts:
                key = parts[parts.index("d") + 1]

    try:
        write_gsheet(current, key)
        current.path = key
        current.source = "gsheet"
        current.mark_saved()
        ui.show_message("Berhasil disimpan ke Google Sheets.", "success")
    except FileNotFoundError as exc:
        ui.show_message(str(exc), "error")
    except Exception as exc:
        ui.show_message(f"Gagal menyimpan ke Google Sheets: {exc}", "error")
