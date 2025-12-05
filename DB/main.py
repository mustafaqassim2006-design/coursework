# DB/main.py

from pathlib import Path

from DB.db import DatabaseManager
from DB.schema import create_tables
from DB.crud import (
    insert_user,
    get_user_by_username,
    create_incident,
    get_all_incidents,
    update_incident_status,
    delete_incident,
    create_dataset,
    get_all_datasets,
    create_ticket,
    get_all_tickets,
)
from DB.load_data import load_all_csv_data

# Path to DATA folder (works anywhere on your machine)
DATA_DIR = Path(__file__).resolve().parent.parent / "DATA"


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
            role = "general"  # default role for Week 8/9

            if get_user_by_username(db, username) is None:
                insert_user(db, username, password_hash, role)


def setup_database():
    with DatabaseManager() as db:
        # 1) create all tables
        create_tables(db)

        # 2) migrate Week 7 users into the users table
        migrate_users_from_file(db, DATA_DIR / "users.txt")

        # 3) load CSV data into the three domain tables
        load_all_csv_data(db)


if __name__ == "__main__":
    setup_database()
    print("Database initialized.")
