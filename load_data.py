from pathlib import Path
import pandas as pd
from db import DatabaseManager

DATA_DIR = Path("DATA")

def load_csv_to_table(db: DatabaseManager, csv_path: Path, table_name: str):
    df = pd.read_csv(csv_path)
    df.to_sql(table_name, db.conn, if_exists="append", index=False)
    print(f"Loaded {len(df)} rows into {table_name}")

def load_all_csv_data(db: DatabaseManager):
    mapping = {
        "cyber_incidents.csv": "cyber_incidents",
        "datasets_metadata.csv": "datasets_metadata",
        "it_tickets.csv": "it_tickets",
    }
    for filename, table in mapping.items():
        path = DATA_DIR / filename
        if path.exists():
            load_csv_to_table(db, path, table)
        else:
            print(f"Skipping {filename}, file not found")
