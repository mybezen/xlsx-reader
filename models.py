from __future__ import annotations

from typing import Any


class SheetData:
    """Wadah data satu sheet / tabel di memori."""

    def __init__(
        self,
        headers: list[str] | None = None,
        rows: list[list[Any]] | None = None,
        path: str | None = None,
        sheet: str | None = None,
        source: str | None = None,
    ) -> None:
        self.headers: list[str] = headers if headers else []
        self.rows: list[list[Any]] = rows if rows else []
        self.path: str | None = path
        self.sheet: str | None = sheet
        self.source: str | None = source
        self.dirty: bool = False

    # Properti bantu
    @property
    def n_rows(self) -> int:
        """Jumlah baris data."""
        return len(self.rows)

    @property
    def n_cols(self) -> int:
        """Jumlah kolom (berdasarkan header, fallback ke baris terpanjang)."""
        if self.headers:
            return len(self.headers)
        return max((len(r) for r in self.rows), default=0)

    def is_loaded(self) -> bool:
        """True jika ada data (atau setidaknya header) yang bisa diproses."""
        return bool(self.headers) or bool(self.rows)

    # Manipulasi baris
    def get_row(self, index: int) -> list[Any] | None:
        """Ambil baris berdasarkan indeks 0-based, None jika di luar jangkauan."""
        if 0 <= index < len(self.rows):
            return self.rows[index]
        return None

    def set_row(self, index: int, row: list[Any]) -> bool:
        """Ganti baris berdasarkan indeks 0-based."""
        if 0 <= index < len(self.rows):
            self.rows[index] = row
            self.dirty = True
            return True
        return False

    def append_row(self, row: list[Any]) -> None:
        """Tambah baris di paling bawah."""
        self.rows.append(row)
        self.dirty = True

    def delete_row_indices(self, indices: list[int]) -> int:
        """Hapus beberapa baris berdasarkan indeks 0-based.

        Mengembalikan jumlah baris yang benar-benar terhapus.
        Indeks duplikat diabaikan; penghapusan dilakukan dari indeks besar
        ke kecil agar posisi indeks lain tidak bergeser.
        """
        unik = sorted({i for i in indices if 0 <= i < len(self.rows)}, reverse=True)
        for i in unik:
            del self.rows[i]
        if unik:
            self.dirty = True
        return len(unik)

    # ------------------------------------------------------------------
    # Manipulasi kolom
    # ------------------------------------------------------------------
    def add_column(self, name: str, default: Any = "") -> None:
        """Tambah kolom baru di sisi kanan dengan nilai default."""
        self.headers.append(name)
        for row in self.rows:
            # Pastikan panjang baris sesuai jumlah kolom sebelum menambah
            while len(row) < len(self.headers) - 1:
                row.append("")
            row.append(default)
        self.dirty = True

    def ensure_width(self) -> None:
        """Pastikan setiap baris sama panjang dengan jumlah kolom.

        Dipakai sebelum menyimpan agar tabel rapi (tidak ada baris
        yang lebih pendek / panjang).
        """
        width = self.n_cols
        for row in self.rows:
            while len(row) < width:
                row.append("")
            if len(row) > width:
                del row[width:]

    # ------------------------------------------------------------------
    # Status perubahan
    # ------------------------------------------------------------------
    def mark_dirty(self) -> None:
        """Tandai ada perubahan belum disimpan."""
        self.dirty = True

    def mark_saved(self) -> None:
        """Tandai semua perubahan sudah disimpan."""
        self.dirty = False

    def __repr__(self) -> str:  # pragma: no cover - hanya untuk debugging
        return (
            f"SheetData(headers={len(self.headers)}, rows={len(self.rows)}, "
            f"source={self.source!r}, sheet={self.sheet!r}, dirty={self.dirty})"
        )
