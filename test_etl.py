import pandas as pd
import sqlite3
from Fastighet import extract, transform, divide_by_type, load_to_db

# Testar extract
def test_extract_missing_file(tmp_path):
    # Om filen inte finns ska extract returnera en tom DataFrame
    df = extract("fil_som_inte_finns.csv")
    assert df.empty

def test_extract_valid_csv(tmp_path):
    # Skapa en liten test-CSV
    csv_file = tmp_path / "data.csv"
    csv_file.write_text("nyckel,Vån,tomt,Boarea,Biarea,Datum,pris,Adress,Typ,Område,Ort\n"
                        "1,2,500,100,20,2024-01-01,500000,Testgatan,Villa,Centrum,Teststad", encoding="utf-8")
    df = pd.read_csv(csv_file, sep=",")
    df = extract(csv_file)
    assert not df.empty
    assert "nyckel" in df.columns


# Testar transform
def test_transform_basic():
    # Testar att transform fixar datatyper och lägger till Totalarea
    raw = pd.DataFrame({
        "nyckel": [1],
        "våning": [1],
        "tomt": ["500"],
        "rum": [4],
        "boarea": ["100"],
        "biarea": ["20"],
        "datum": ["2024-01-01"],
        "pris": ["1 000 000"],
        "adress": ["Testgatan"],
        "typ": ["Villa"],
        "område": ["Centrum"],
        "ort": ["Teststad"]})
    df = transform(raw)
    assert "Totalarea" in df.columns
    assert df["Totalarea"].iloc[0] == 120
    assert pd.api.types.is_numeric_dtype(df["Boarea"])


# Testar uppdelning
def test_divide_by_type():
    df = pd.DataFrame({
        "Bostadstyp": ["Villa", "Lägenhet", "Villa"],
        "Boarea": [100, 50, 120]})
    result = divide_by_type(df)
    assert "Villa" in result
    assert "Lägenhet" in result
    assert len(result["Villa"]) == 2
    assert len(result["Lägenhet"]) == 1


# Testar load
def test_load_to_db(tmp_path):
    db_path = tmp_path / "test.db"
    df = pd.DataFrame({
        "Nyckel": [1, 2],
        "Boarea": [100, 120]})
    load_to_db(df, db_path, "fastighet_test")
    # Verifiera att tabellen skapats i SQLite
    conn = sqlite3.connect(db_path)
    rows = conn.execute("SELECT * FROM fastighet_test").fetchall()
    conn.close()
    assert len(rows) == 2
