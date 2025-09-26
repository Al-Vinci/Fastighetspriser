"""
Importera, transformera och spara data från en CSV-fil, till en SQLite-databas.
CSV-filen (data.csv) förväntas ligga i samma mapp som detta skript
och innehålla rubrikerna: nyckel, vån, tomt, boarea, biarea, datum, pris,
adress, typ, område, ort
"""

import os
import logging
import sqlite3
import pandas as pd
import datetime as dt

date_now = dt.datetime.now()
date_now = date_now.strftime("%y%m%d")

# Konfiguration av loggning
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    filename=f"fastighet_log_{date_now}.log", # Loggfil
    filemode="a") # Append-läge



def extract(file_path: str) -> pd.DataFrame:
    """Extraherar data från en CSV-fil."""
    logging.info("Startar dataextraktion från CSV.")
    try:
        # Prova med olika avgränsare och hantera citattecken
        data = pd.read_csv(
            file_path,
            encoding="utf-8",
            sep=None,              # Låter pandas gissa avgränsare
            engine="python",       # Mer flexibel tolkare än standard
            quotechar='"',         # Hanterar text med kommatecken i
            skip_blank_lines=True) # Hoppa över helt tomma rader
        logging.info("Dataextraktion lyckades. Antal rader: %d", len(data))
        return data
    except FileNotFoundError:
        logging.error("Filen %s hittades inte.", file_path)
        return pd.DataFrame()
    except Exception as error:
        logging.exception("Fel vid inläsning av CSV: %s", error)
        return pd.DataFrame()



def transform(data: pd.DataFrame) -> pd.DataFrame:
    """Transformerar data för analys och vidare bearbetning."""
    if data.empty:
        logging.warning("Ingen data att transformera.")
        return data
    logging.info("Startar transformation av data.")
    # Tar bort helt tomma kolumner (t.ex. spökkolumner från extra avgränsare)
    before_cols = data.shape[1]
    data = data.dropna(axis=1, how="all")
    data = data.loc[:, ~data.columns.str.contains("^Unnamed")]
    after_cols = data.shape[1]
    if after_cols < before_cols:
        logging.info("Tog bort %d tomma kolumner.", before_cols - after_cols)
    # Byter namn på kolumner
    new_names = {data.columns[0]: "Nyckel",
                data.columns[1]: "Våning",
                data.columns[2]: "Tomtarea",
                data.columns[3]: "Rum",
                data.columns[4]: "Boarea",
                data.columns[5]: "Biarea",
                data.columns[6]: "Datum",
                data.columns[7]: "Pris",
                data.columns[8]: "Adress",
                data.columns[9]: "Bostadstyp",
                data.columns[10]: "Område",
                data.columns[11]: "Ort"}
    data = data.rename(columns=new_names)
    # Konvertera datumkolumn till datetime-format
    if "Datum" in data.columns:
        data["Datum"] = pd.to_datetime(
            data["Datum"], errors="coerce", format="%Y-%m-%d")
    # Konvertera numeriska kolumner till rätt typ
    numeric_cols = ["Tomtarea", "Boarea", "Biarea", "Rum", "Pris"]
    for col in numeric_cols:
        if col in data.columns:
            # Gör om till sträng för att kunna rensa
            data[col] = data[col].astype(str)
            # Ta bort mellanslag (tusental)
            data[col] = data[col].str.replace(" ", "", regex=False)
            # Ta bort punkter som tusental
            data[col] = data[col].str.replace(".", "", regex=False)
            # Byt komma till punkt för decimal
            data[col] = data[col].str.replace(",", ".", regex=False)
            # Konvertera till numeriskt värde
            data[col] = pd.to_numeric(data[col], errors="coerce")
    if "Boarea" in data.columns and "Biarea" in data.columns:
        data["Totalarea"] = data["Boarea"].fillna(0) + data["Biarea"].fillna(0)
    else:
        data["Totalarea"] = pd.NA
    # Ta bort rader utan nyckel
    if "Nyckel" in data.columns:
        before = len(data)
        data = data.dropna(subset=["Nyckel"])
        after = len(data)
        logging.info("Tog bort %d rader utan nyckel.", before - after)
    logging.info("Transformation slutförd. Antal rader: %d, kolumner: %d", len(data), data.shape[1])
    # print(data.head(10))
    # logging.info(data.head(10))
    return data



def divide_by_type(data: pd.DataFrame):
    """Delar upp Dataframe i olika bostadstyper"""
    types = data["Bostadstyp"].unique()
    df_dict = {}
    for type in types:
        df_dict[type] = data[data["Bostadstyp"] == type].copy()
    return df_dict



def load_to_db(data: pd.DataFrame, db_path: str, table_name: str) -> None:
    """Laddar transformerad data till en SQLite-databas."""
    if data.empty:
        logging.warning("Ingen data att ladda till databas. Avbryter.")
        return
    try:
        conn = sqlite3.connect(db_path)
        data.to_sql(table_name, conn, if_exists="replace", index=False)
        conn.close()
        logging.info("Data laddades till SQLite-databas (%s), tabell: %s", db_path, table_name)
    except Exception as error:
        logging.exception("Fel vid laddning av data till databas: %s", error)

def main():
    """Huvudfunktion"""
    logging.info("Startar.")
    # Hitta sökväg till data.csv i samma mapp som skriptet
    script_dir = os.path.dirname(os.path.abspath(__file__))
    input_file = os.path.join(script_dir, "data.csv")
    # logging.info(script_dir) för felsökning
    # logging.info(input_file) för felsökning

    database_file = os.path.join(script_dir, "fastigheter.db")

    # ETL-process
    raw_data = extract(input_file)
    transformed_data = transform(raw_data)
    divided_data = divide_by_type(transformed_data)
    for bostadstyp, df_typ in divided_data.items():
        type = bostadstyp.replace(" ", "_").replace("/", "_").lower()
        # type = bostadstyp.replace(" ", "_").lower()
        load_to_db(df_typ, database_file,f"fastighetstyp_{type}")
    # load_to_db(transformed_data, database_file, table_name)

    logging.info("Skriptet är klart.")


if __name__ == "__main__":
    main()
