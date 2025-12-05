# main.py
from pathlib import Path
from db import DatabaseManager
from schema import create_tables
from crud import (
    insert_user, get_user_by_username,
    create_incident, get_all_incidents, update_incident_status, delete_incident,
    create_dataset, get_all_datasets,
    create_ticket, get_all_tickets
)
from load_data import load_all_csv_data

DATA_DIR = Path("c:\MDX CSSE\Mustafa\My_Work\DATA")

def migrate_users_from_file(db: DatabaseManager, users_file: Path):
    if not users_file.exists():
        print("users.txt not found, skipping migration")
        return

    with users_file.open("r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            username, password_hash = line.split(",")
            role = "general"
            if get_user_by_username(db, username) is None:
                insert_user(db, username, password_hash, role)

def setup_database():
    with DatabaseManager() as db:
        create_tables(db)
        migrate_users_from_file(db, DATA_DIR / "users.txt")
        load_all_csv_data(db)

def demo_crud():
    with DatabaseManager() as db:
        print("\n=== Cyber Incidents BEFORE ===")
        print(len(get_all_incidents(db)))

        # Create
        create_incident(
            db,
            "TEST123", "Phishing", "Medium", "Open",
            "2025-01-01", None, "Alice", "Test incident"
        )

        print("\n=== After Create ===")
        print(len(get_all_incidents(db)))

        # Update
        update_incident_status(db, "TEST123", "Resolved")

        # Delete
        delete_incident(db, "TEST123")

        print("\n=== After Delete ===")
        print(len(get_all_incidents(db)))


if __name__ == "__main__":
    setup_database()
    demo_crud()
