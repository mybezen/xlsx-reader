"""Test suite sederhana untuk memverifikasi logika aplikasi."""

from pathlib import Path
from models import SheetData
from reader import open_file
from editor import add_row, edit_cell, delete_rows, add_column
from search import search_rows
from writer import save_as

def test_all():
    print("Run tests...")
    
    # 1. Test load XLSX
    data = open_file(r"data/nilai.xlsx")
    assert data.n_rows == 10
    assert data.n_cols == 4
    print("[OK] Load XLSX")
    
    # 2. Test edit cell
    edit_cell(data, 0, 0, "Andi Wijaya")
    assert data.get_row(0)[0] == "Andi Wijaya"
    assert data.dirty
    print("[OK] Edit cell")
    
    # 3. Test add row
    add_row(data, ["Kiki", "X-A", "82", "Lulus"])
    assert data.n_rows == 11
    print("[OK] Add row")
    
    # 4. Test add column
    add_column(data, "Keterangan", "OK")
    assert data.n_cols == 5
    assert data.headers[-1] == "Keterangan"
    print("[OK] Add column")
    
    # 5. Test search
    res = search_rows(data, "Remedial")
    assert res.n_rows == 2
    print("[OK] Search rows")
    
    # 6. Test delete rows
    delete_rows(data, [1]) # delete row 1
    assert data.n_rows == 10
    print("[OK] Delete rows")
    
    # 7. Test convert / save as CSV
    save_as(data, r"data/test_out.csv")
    assert Path(r"data/test_out.csv").exists()
    print("[OK] Save as CSV")
    
    # 8. Load the exported CSV
    data_csv = open_file(r"data/test_out.csv")
    assert data_csv.n_rows == 10
    assert data_csv.n_cols == 5
    print("[OK] Load CSV export")

    print("\nSemua test BERHASIL!")

if __name__ == "__main__":
    test_all()
